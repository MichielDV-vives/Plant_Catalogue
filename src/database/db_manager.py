import csv
import sqlite3
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from configparser import ConfigParser
# from src.models.plant import Plant
# from src.database.queries import CREATE_PLANTS_TABLE, INSERT_PLANT, SEARCH_PLANTS, GET_ALL_PLANTS, UPDATE_PLANT, GET_PLANT_BY_ID
from models.plant import Plant
from database.queries import CREATE_PLANTS_TABLE, INSERT_PLANT, SEARCH_PLANTS, GET_ALL_PLANTS, UPDATE_PLANT, \
    GET_PLANT_BY_ID, ADD_LEAF_RECORD, UPDATE_LAST_LEAF_DATE, GET_LEAF_RECORDS, CREATE_LEAF_RECORDS_TABLE


class DatabaseManager:
    def __init__(self) -> None:
        config = ConfigParser()
        config.read('config.ini')
        self.db_path = Path(config['database']['path'])
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_PLANTS_TABLE)
            cursor.execute(CREATE_LEAF_RECORDS_TABLE)
            conn.commit()

    def add_plant(self, plant: Plant) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(INSERT_PLANT, (
                plant.name,
                plant.family,
                plant.image_path,
                plant.birthdate.isoformat() if plant.birthdate else None
            ))
            conn.commit()
            return cursor.lastrowid

    def search_plants(self, query: str) -> List[tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(SEARCH_PLANTS, (f'%{query}%', f'%{query}%'))
            return cursor.fetchall()

    def get_all_plants(self) -> List[tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(GET_ALL_PLANTS)
            return cursor.fetchall()

    def get_plant_by_id(self, plant_id: int) -> Optional[tuple]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(GET_PLANT_BY_ID, (plant_id,))
            return cursor.fetchone()

    def edit_plant(self, plant_id: int, name: Optional[str] = None,
                   family: Optional[str] = None, image_path: Optional[str] = None,
                   birthdate: Optional[datetime] = None) -> bool:
        # Check if plant exists
        if not self.get_plant_by_id(plant_id):
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(UPDATE_PLANT, (
                name,
                family,
                image_path,
                birthdate.isoformat() if birthdate else None,
                plant_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def add_leaf_record(self, plant_id: int, date: Optional[datetime] = None) -> bool:
        # First check if plant exists
        plant = self.get_plant_by_id(plant_id)
        if not plant:
            print(f"No plant found with ID {plant_id}")
            return False

        date = date or datetime.now()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(ADD_LEAF_RECORD, (plant_id, date.isoformat()))
                conn.commit()
                print(f"Successfully added leaf record for plant {plant_id}")
                return True
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                return False

    def get_leaf_statistics(self, plant_id: int) -> Optional[dict]:
        plant = self.get_plant_by_id(plant_id)
        if not plant:
            return None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(GET_LEAF_RECORDS, (plant_id,))
            records = cursor.fetchall()

        leaf_dates = [datetime.fromisoformat(row[0]) for row in records]
        plant_obj = Plant.from_db_row(plant)
        plant_obj.leaf_records = leaf_dates
        return plant_obj.calculate_leaf_statistics()

    def export_leaf_data(self, filename: str):
        plants = self.get_all_plants()
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Plant ID', 'Name', 'Total Leaves', 'Avg Days Between Leaves',
                'Days Since Last Leaf'
            ])

            for plant in plants:
                plant_id = plant[0]
                stats = self.get_leaf_statistics(plant_id)
                if stats:
                    writer.writerow([
                        plant_id, plant[1], stats['total_leaves'],
                        round(stats['avg_days_between_leaves'], 1) if stats['avg_days_between_leaves'] else None,
                        stats['days_since_last_leaf']
                    ])
