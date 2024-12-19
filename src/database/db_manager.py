import sqlite3
from typing import List, Optional
from pathlib import Path
from configparser import ConfigParser
from src.models.plant import Plant
from src.database.queries import CREATE_PLANTS_TABLE, INSERT_PLANT, SEARCH_PLANTS, GET_ALL_PLANTS, UPDATE_PLANT, GET_PLANT_BY_ID


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
            conn.commit()

    def add_plant(self, plant: Plant) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(INSERT_PLANT, (
                plant.name,
                plant.family,
                plant.image_path,
                plant.age
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
                   age: Optional[int] = None) -> bool:
        # Check if plant exists
        if not self.get_plant_by_id(plant_id):
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(UPDATE_PLANT, (
                name,
                family,
                image_path,
                age,
                plant_id
            ))
            conn.commit()
            return cursor.rowcount > 0
