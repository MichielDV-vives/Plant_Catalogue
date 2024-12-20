#!/usr/bin/env python3
import configparser
import os
from datetime import datetime

from models.plant import Plant
from database.db_manager import DatabaseManager
from utils.report_generator import ReportGenerator
from utils.image_handler import ImageHandler
from cli.argument_parser import create_parser, validate_args
from tabulate import tabulate


def create_data_folders():
    folders = ['data', 'data/reports', 'data/images']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)


def main() -> None:
    create_data_folders()
    db = DatabaseManager()
    report_gen = ReportGenerator()
    image_handler = ImageHandler()

    parser = create_parser()
    args = parser.parse_args()

    if not validate_args(args):
        return

    if args.command == 'list':
        results = db.get_all_plants()
        if results:
            print(tabulate(results, headers=['ID', 'Name', 'Family', 'Image', 'Age', 'Added Date']))
        else:
            print("No plants found")
        return

    if args.command == 'add-plant':
        image_path = None
        if args.image:
            image_path = image_handler.save_image(args.image, args.name)
        plant = Plant(
            name=args.name,
            family=args.family,
            image_path=image_path,
            age=args.age or 0
        )
        plant_id = db.add_plant(plant)
        print(f"Plant added successfully with ID: {plant_id}")

    elif args.command == 'search-plant':
        results = db.search_plants(args.query)
        if results:
            print(tabulate(results, headers=['ID', 'Name', 'Family', 'Image', 'Age', 'Added Date']))
        else:
            print("No plants found")

    elif args.command == 'edit-plant':
        # Handle image if provided
        image_path = None
        if args.image:
            image_path = image_handler.save_image(args.image, args.name or f"plant_{args.id}")

        # Get current plant details
        current_plant = db.get_plant_by_id(args.id)
        if not current_plant:
            print(f"No plant found with ID {args.id}")
            return

        # Update plant with new values, keeping existing values if not provided
        updated = db.edit_plant(
            plant_id=args.id,
            name=args.name,
            family=args.family,
            image_path=image_path,
            age=args.age
        )

        if updated:
            print(f"Plant with ID {args.id} updated successfully")
            # Show updated plant details
            plant = db.get_plant_by_id(args.id)
            if plant:
                print("\nUpdated plant details:")
                print(tabulate([plant], headers=['ID', 'Name', 'Family', 'Image', 'Age', 'Added Date']))
        else:
            print("Failed to update plant")

    elif args.command == 'report':
        plants = db.get_all_plants()
        report_path = report_gen.generate_plant_report(plants)
        print(f"Report generated: {report_path}")

    elif args.command == 'add-leaf':
        if not args.id:
            print("Please provide a plant ID")
            return

        date = None
        if args.date:
            try:
                date = datetime.strptime(args.date, '%Y-%m-%d')
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")
                return

        if db.add_leaf_record(args.id, date):
            print(f"Leaf record added for plant {args.id}")
        else:
            print("Failed to add leaf record")

    elif args.command == 'leaf-stats':
        if args.id:
            # Single plant statistics
            stats = db.get_leaf_statistics(args.id)
            if stats:
                plant = db.get_plant_by_id(args.id)
                print(f"\nLeaf Statistics for {plant[1]}:")
                print(f"Total leaves: {stats['total_leaves']}")
                if stats['avg_days_between_leaves']:
                    print(f"Average days between leaves: {stats['avg_days_between_leaves']:.1f}")
                if stats['days_since_last_leaf'] is not None:
                    print(f"Days since last leaf: {stats['days_since_last_leaf']}")
            else:
                print("No statistics available")
        else:
            # Export all plant statistics to a file
            config = configparser.ConfigParser()
            config.read("config.ini")
            reports_dir = config.get('reports', 'output_dir', fallback='data/reports')
            os.makedirs(reports_dir, exist_ok=True)
            default_filename = os.path.join(reports_dir, f"leaf_statistics_{datetime.now().strftime('%Y%m%d')}.csv")
            db.export_leaf_data(default_filename)
            print(f"Leaf statistics successfully exported to: {default_filename}")


if __name__ == "__main__":
    main()

