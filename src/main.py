#!/usr/bin/env python3
import configparser
import os
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path
from tabulate import tabulate
import cv2
import time

from models.plant import Plant
from database import db_operations as db
from utils.image_handler import ImageHandler
from utils.plantdata_processor import PlantDataProcessor
from utils.report_generator import ReportGenerator
from cli.argument_parser import create_parser, validate_args
from utils.qr_handler import QRHandler
from utils.image_viewer import ImageViewer
from utils.plant_interaction import PlantInteraction

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    filename='errors.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlantCatalogueApp:
    def __init__(self):
        self.report_gen = ReportGenerator()
        self.plantdata_processor = PlantDataProcessor(ImageHandler())
        self.qr_handler = QRHandler()
        self.plant_interaction = PlantInteraction()

    def setup(self) -> None:
        """Initialize application setup"""
        self._create_data_folders()
        db.init_db()

    def _create_data_folders(self) -> None:
        """Create necessary data directories"""
        folders = ['data', 'data/reports', 'data/images']
        for folder in folders:
            Path(folder).mkdir(exist_ok=True)

    def list_plants(self) -> None:
        """Display all plants in tabulated format"""
        results = db.get_all_plants()
        if not results:
            print("No plants found")
            return

        formatted_results = self._format_plant_results(results)
        headers = ['ID', 'Name', 'Family', 'Image', 'MIME Type', 'Birthdate', 'Created At', 'Last Leaf Date']
        print(tabulate(formatted_results, headers=headers, tablefmt='simple'))

    def add_plant(self, args) -> None:
        """Add a new plant to the database"""
        plant_data = self.plantdata_processor(args)
        plant = Plant(**plant_data)
        plant_id = db.add_plant(plant)
        print(f"Plant added successfully with ID: {plant_id}")

    def edit_plant(self, args) -> None:
        """Edit an existing plant"""
        plant_data = self.plantdata_processor(args)
        if db.edit_plant(plant_id=args.id, **plant_data):
            print(f"Plant with ID {args.id} updated successfully")
            self._show_updated_plant(args.id)
        else:
            print("Failed to update plant")

    def generate_report(self) -> None:
        """Generate a plant report"""
        plants = db.get_all_plants()
        report_path = self.report_gen.generate_plant_report(plants)
        print(f"Report generated: {report_path}")

    def add_leaf_record(self, args) -> None:
        """Add a new leaf record"""
        if not args.id:
            print("Please provide a plant ID")
            return

        date = self._parse_date(args.date) if args.date else None
        if db.add_leaf_record(args.id, date):
            print(f"Leaf record added for plant {args.id}")
        else:
            print("Failed to add leaf record")

    def show_leaf_stats(self, args) -> None:
        """Display leaf statistics"""
        if args.id:
            self._show_single_plant_stats(args.id)
        else:
            self._export_all_plant_stats()

    def search_plants(self, args) -> None:
        """Search for plants"""
        results = db.search_plants(args.query)
        if results:
            formatted_results = self._format_plant_results(results)
            headers = ['ID', 'Name', 'Family', 'Image', 'MIME Type', 'Birthdate', 'Created At', 'Last Leaf Date']
            print(tabulate(formatted_results, headers=headers))
        else:
            print("No plants found")

    def show_plant_image(self, args) -> None:
        """Display plant image"""
        if not args.id:
            print("Please provide a plant ID")
            return
        db.show_plant_image(args.id)

    def scan_and_interact(self) -> None:
        """Scan QR code and interact with plant"""
        print("Scanning plant QR code...")
        plant_id = self.qr_handler.scan_qr(show_image=True)
        
        if not plant_id:
            print("No QR code detected")
            return

        plant = db.get_plant_by_id(plant_id)
        if not plant:
            print("Plant not found")
            return

        self.plant_interaction.show_plant_menu(plant_id)

    def _show_updated_plant(self, plant_id: int) -> None:
        """Show updated plant details"""
        plant = db.get_plant_by_id(plant_id)
        if plant:
            print("\nUpdated plant details:")
            headers = ['ID', 'Name', 'Family', 'Image', 'MIME Type', 'Birthdate', 'Created At', 'Last Leaf Date']
            formatted_plant = list(plant[:8])  # ID, Name, Family, Image, MIME Type, Birthdate, Created At, Last Leaf Date
            formatted_plant[3] = "Yes" if formatted_plant[3] else "No"
            print(tabulate([formatted_plant], headers=headers))

    def _show_single_plant_stats(self, plant_id: int) -> None:
        """Show statistics for a single plant"""
        stats = db.get_leaf_statistics(plant_id)
        if not stats:
            print("No statistics available")
            return

        plant = db.get_plant_by_id(plant_id)
        print(f"\nLeaf Statistics for {plant[1]}:")
        print(f"Total leaves: {stats['total_leaves']}")
        if stats['avg_days_between_leaves']:
            print(f"Average days between leaves: {stats['avg_days_between_leaves']:.1f}")
        if stats['days_since_last_leaf'] is not None:
            print(f"Days since last leaf: {stats['days_since_last_leaf']}")

    def _export_all_plant_stats(self) -> None:
        """Export statistics for all plants"""
        config = configparser.ConfigParser()
        config.read("config.ini")
        reports_dir = Path(config.get('reports', 'output_dir', fallback='data/reports'))
        reports_dir.mkdir(exist_ok=True)
        
        filename = reports_dir / f"leaf_statistics_{datetime.now().strftime('%Y%m%d')}.csv"
        db.export_leaf_data(str(filename))
        print(f"Leaf statistics successfully exported to: {filename}")

    def list_qr_codes(self) -> None:
        """List all available QR codes"""
        qr_dir = Path('data/qr_codes')
        if not qr_dir.exists():
            print("No QR codes directory found")
            return
        
        qr_files = list(qr_dir.glob('plant_*_qr.png'))
        if not qr_files:
            print("No QR codes found")
            return

        print("\nAvailable QR codes:")
        for qr_file in qr_files:
            plant_id = int(qr_file.stem.split('_')[1])
            plant = db.get_plant_by_id(plant_id)
            if plant:
                print(f"Plant {plant_id}: {plant[1]} - {qr_file}")

    def migrate(self) -> None:
        """Perform database migrations"""
        db.migrate_database()

    def water_plant(self, args) -> None:
        """Record watering for a plant"""
        if not args.id:
            print("Please provide a plant ID")
            return

        if db.update_last_watered(args.id):
            print(f"Watering recorded for plant {args.id}")
            self._show_watering_info(args.id)
        else:
            print("Failed to record watering")

    def show_water_info(self, args) -> None:
        """Show watering information for a plant"""
        if not args.id:
            print("Please provide a plant ID")
            return

        self._show_watering_info(args.id)

    def _show_watering_info(self, plant_id: int) -> None:
        """Show watering information for a plant"""
        info = db.get_watering_info(plant_id)
        if not info:
            print("No watering information available")
            return

        print("\nWatering Information:")
        if info['last_watered']:
            print(f"Last watered: {info['last_watered'].strftime('%Y-%m-%d')}")
            print(f"Days since last watering: {info['days_since_watered']}")
        else:
            print("Plant has never been watered")

    def _format_plant_results(self, results: List[Tuple]) -> List[List]:
        """Format plant results for display"""
        formatted_results = []
        for plant in results:
            # Take only the first 8 columns and convert to list
            formatted_plant = list(plant[:8])  # ID, Name, Family, Image, MIME Type, Birthdate, Created At, Last Leaf Date
            
            # Convert image data to Yes/No
            formatted_plant[3] = "Yes" if formatted_plant[3] else "No"
            
            # Format dates if they exist
            for i in [5, 6, 7]:  # birthdate, created_at, last_leaf_date
                if formatted_plant[i]:
                    try:
                        date = datetime.fromisoformat(formatted_plant[i])
                        formatted_plant[i] = date.strftime('%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass
            formatted_results.append(formatted_plant[:8])  # Ensure we only take first 8 columns
        return formatted_results

def main() -> None:
    try:
        app = PlantCatalogueApp()
        app.setup()

        parser = create_parser()
        args = parser.parse_args()

        if not validate_args(args):
            return

        # Command dispatch dictionary
        commands = {
            'list': app.list_plants,
            'add-plant': lambda: app.add_plant(args),
            'edit-plant': lambda: app.edit_plant(args),
            'report': app.generate_report,
            'add-leaf': lambda: app.add_leaf_record(args),
            'leaf-stats': lambda: app.show_leaf_stats(args),
            'show-image': lambda: app.show_plant_image(args),
            'search-plant': lambda: app.search_plants(args),
            'scan': app.scan_and_interact,
            'list-qr': app.list_qr_codes,
            'migrate': app.migrate,
            'water': lambda: app.water_plant(args),
            'water-info': lambda: app.show_water_info(args),
        }

        # Execute the command
        commands[args.command]()

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"An unexpected error occurred. Check errors.log for details.")

if __name__ == "__main__":
    main()
