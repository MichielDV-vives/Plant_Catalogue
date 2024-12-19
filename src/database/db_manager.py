import sqlite3
from pathlib import Path
from configparser import ConfigParser
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

