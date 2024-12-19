CREATE_PLANTS_TABLE = '''
    CREATE TABLE IF NOT EXISTS plants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        family TEXT NOT NULL,
        image_path TEXT,
        age INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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