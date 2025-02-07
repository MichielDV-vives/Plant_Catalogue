import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from pathlib import Path
from configparser import ConfigParser
import csv

# Use absolute imports
from models.plant import Plant
from utils.image_viewer import ImageViewer
from database.queries import *
from utils.qr_handler import QRHandler

class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

def get_db_path() -> Path:
    """Get database path from config file"""
    config = ConfigParser()
    config.read('config.ini')
    return Path(config['database']['path'])

def _execute_query(query: str, params: Tuple = (), fetch: bool = False) -> Optional[List[tuple]]:
    """Execute a database query with error handling"""
    try:
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid else None
    except sqlite3.Error as e:
        raise DatabaseError(f"Database error: {e}")

# Database initialization
def init_db() -> None:
    """Initialize the database with required tables"""
    _execute_query(CREATE_PLANTS_TABLE)
    _execute_query(CREATE_LEAF_RECORDS_TABLE)
    migrate_database()

# Plant operations
def add_plant(plant: Plant) -> int:
    """Add a new plant to the database"""
    plant_id = _execute_query(INSERT_PLANT, (
        plant.name,
        plant.family,
        plant.image_data,
        plant.image_mime_type,
        plant.birthdate.isoformat() if plant.birthdate else None
    ))
    
    if plant_id:
        # Generate QR code for new plant
        qr_handler = QRHandler()
        qr_path = qr_handler.generate_qr(plant_id)
        print(f"QR code generated: {qr_path}")
    
    return plant_id

def get_all_plants() -> List[tuple]:
    """Get all plants from the database"""
    return _execute_query(GET_ALL_PLANTS, fetch=True) or []

def get_plant_by_id(plant_id: int) -> Optional[tuple]:
    """Get a plant by its ID"""
    result = _execute_query(GET_PLANT_BY_ID, (plant_id,), fetch=True)
    return result[0] if result else None

def search_plants(query: str) -> List[tuple]:
    """Search plants by name or family"""
    search_params = (f'%{query}%', f'%{query}%')
    return _execute_query(SEARCH_PLANTS, search_params, fetch=True) or []

def edit_plant(plant_id: int, **kwargs) -> bool:
    """Edit an existing plant's details"""
    if not get_plant_by_id(plant_id):
        return False
        
    params = (
        kwargs.get('name'),
        kwargs.get('family'),
        kwargs.get('image_data'),
        kwargs.get('image_mime_type'),
        kwargs.get('birthdate').isoformat() if kwargs.get('birthdate') else None,
        plant_id
    )
    return bool(_execute_query(UPDATE_PLANT, params))

def update_last_watered(plant_id: int, date: Optional[datetime] = None) -> bool:
    """Update the last watered date for a plant"""
    date = date or datetime.now()
    try:
        _execute_query(UPDATE_LAST_WATERED, (date.isoformat(), plant_id))
        return True
    except DatabaseError:
        return False

def get_watering_info(plant_id: int) -> Optional[Dict]:
    """Get watering information for a plant"""
    result = _execute_query(GET_WATERING_INFO, (plant_id,), fetch=True)
    if not result:
        return None

    last_watered = result[0][0]  # Now only returns last_watered
    
    info = {
        'last_watered': datetime.fromisoformat(last_watered) if last_watered else None,
        'days_since_watered': None
    }
    
    if info['last_watered']:
        info['days_since_watered'] = (datetime.now() - info['last_watered']).days
        
    return info

# Leaf record operations
def add_leaf_record(plant_id: int, date: Optional[datetime] = None) -> bool:
    """Add a new leaf record for a plant"""
    if not get_plant_by_id(plant_id):
        return False

    date = date or datetime.now()
    try:
        _execute_query(ADD_LEAF_RECORD, (plant_id, date.isoformat()))
        _execute_query(UPDATE_LAST_LEAF_DATE)
        return True
    except DatabaseError:
        return False

def get_leaf_statistics(plant_id: int) -> Optional[dict]:
    """Get leaf statistics for a specific plant"""
    plant = get_plant_by_id(plant_id)
    if not plant:
        return None

    records = _execute_query(GET_LEAF_RECORDS, (plant_id,), fetch=True)
    leaf_dates = [datetime.fromisoformat(row[0]) for row in records]
    plant_obj = Plant.from_db_row(plant)
    plant_obj.leaf_records = leaf_dates
    return plant_obj.calculate_leaf_statistics()

def export_leaf_data(filename: str) -> None:
    """Export leaf statistics for all plants to a CSV file"""
    plants = get_all_plants()
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Plant ID', 'Name', 'Total Leaves', 'Avg Days Between Leaves',
            'Days Since Last Leaf'
        ])

        for plant in plants:
            plant_id = plant[0]
            stats = get_leaf_statistics(plant_id)
            if stats:
                writer.writerow([
                    plant_id, plant[1], stats['total_leaves'],
                    round(stats['avg_days_between_leaves'], 1) if stats['avg_days_between_leaves'] else None,
                    stats['days_since_last_leaf']
                ])

# Image operations
def show_plant_image(plant_id: int) -> None:
    """Display the image for a specific plant"""
    plant = get_plant_by_id(plant_id)
    if not plant or not plant[3] or not plant[4]:
        print("No image available for this plant")
        return

    viewer = ImageViewer()
    viewer.show_image(plant[3], f"Plant: {plant[1]} {plant[2]}")

# Add this function to db_operations.py
def migrate_database() -> None:
    """Perform database migrations"""
    try:
        # Add watering-related columns if they don't exist
        _execute_query("""
            ALTER TABLE plants 
            ADD COLUMN last_watered DATE DEFAULT NULL
        """, fetch=False)
    except DatabaseError:
        pass  # Column might already exist

    try:
        _execute_query("""
            ALTER TABLE plants 
            ADD COLUMN watering_interval INTEGER DEFAULT 7
        """, fetch=False)
    except DatabaseError:
        pass  # Column might already exist

    # Generate QR codes for existing plants
    plants = get_all_plants()
    qr_handler = QRHandler()
    for plant in plants:
        plant_id = plant[0]
        qr_handler.save_qr_code(plant_id)  # Use save_qr_code instead of generate_qr

def update_watering_interval(plant_id: int, interval: int) -> bool:
    """Update the watering interval for a plant"""
    try:
        _execute_query(UPDATE_WATERING_INTERVAL, (interval, plant_id))
        return True
    except DatabaseError:
        return False 
