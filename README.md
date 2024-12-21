## Plant Catalogue System

A command-line application to manage your plant collection.

### Features
- Add and manage plants (name, family, image path, birthdate)
- Search plants by name or family
- Generate plant collection reports in CSV format
- Keep track of plant growth in CSV format

### Setup
1. Copy `config.example.ini` to `config.ini` and update settings
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python src/main.py`

### Commands
- `python src/main.py add-plant`: Add a new plant
- `python src/main.py search-plant`: Search plants by name or family
- `python src/main.py list`: Show the whole database of plants
- `python src/main.py edit-plant`: Change attributes of plants
- `python src/main.py add-leaf`: Add a leaf to the plant
- `python src/main.py leaf-stats`: Generate CSV of your collection leaf status
- `python src/main.py show-image`: Show image of a plant

### Usage Example

In terminal at /plant_catalogue

- Help
`python src/main.py -h`

- Show List of plants
`python src/main.py`

- Add a new plant
`python src/main.py add-plant --name Venus_Flytrap --family Droseraceae --age 1 `

- Edit a specific plant
`python src/main.py edit-plant --id 3 --name Changed --family Changed_Family`

- Search for plants
`python src/main.py search-plant --query Venus`

- Add leave function to keep track of growth
`python src/main.py add-leaf --id 3`

- Generate report
`python src/main.py report`

- Generate csv of leaf statistics
`python src/main.py leaf-stats`  

- Show leaf statistics of a specific plant
`python src/main.py leaf-stats --id 2`  

- Show image of a specific plant
`python src/main.py show-iamge --id 2`  






### Project Structure
```
plant_catalogue/
├── src/
│   ├── main.py
│   ├── models/
│   │   └── plant.py
│   ├── database/
│   │   ├── db_manager.py
│   │   └── queries.py
│   ├── utils/
│   │   ├── image_handler.py
│   │   ├── image_processor.py
│   │   ├── image_viewer.py
│   │   └── report_generator.py
│   └── cli/
│       └── argument_parser.py
├── data/
│   ├── images/
│   ├── reports/
│   └── plants.db
├── config.example.ini
├── README.md
└── requirements.txt
```