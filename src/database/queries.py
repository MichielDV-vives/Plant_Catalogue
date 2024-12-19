CREATE_PLANTS_TABLE = '''
    CREATE TABLE IF NOT EXISTS plants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        family TEXT NOT NULL,
        image_path TEXT,
        age INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_leaf_date TIMESTAMP
    )
'''

CREATE_LEAF_RECORDS_TABLE = '''
    CREATE TABLE IF NOT EXISTS leaf_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plant_id INTEGER NOT NULL,
        appearance_date TIMESTAMP NOT NULL,
        FOREIGN KEY (plant_id) REFERENCES plants (id)
    )
'''

INSERT_PLANT = '''
    INSERT INTO plants (name, family, image_path, age)
    VALUES (?, ?, ?, ?)
'''

SEARCH_PLANTS = '''
    SELECT * FROM plants
    WHERE name LIKE ? OR family LIKE ?
'''

UPDATE_PLANT = '''
    UPDATE plants
    SET name = COALESCE(?, name),
        family = COALESCE(?, family),
        image_path = COALESCE(?, image_path),
        age = COALESCE(?, age)
    WHERE id = ?
'''

GET_PLANT_BY_ID = '''
    SELECT * FROM plants
    WHERE id = ?
'''

GET_ALL_PLANTS = '''
    SELECT * FROM plants
    ORDER BY name
'''

ADD_LEAF_RECORD = '''
    INSERT INTO leaf_records (plant_id, appearance_date)
    VALUES (?, ?)
'''

GET_LEAF_RECORDS = '''
    SELECT appearance_date FROM leaf_records
    WHERE plant_id = ?
    ORDER BY appearance_date
'''

UPDATE_LAST_LEAF_DATE = '''
    UPDATE plants
    SET last_leaf_date = ?
    WHERE id = ?
'''