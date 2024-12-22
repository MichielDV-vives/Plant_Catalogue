#!/usr/bin/env python3
import configparser
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
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
            headers = ['ID', 'Name', 'Family', 'Image', 'MIME Type', 'Birthdate', 'Created At', 'Last Leaf Date']
            formatted_results = []
            for row in results:
                formatted_row = []
                for i, cell in enumerate(row):
                    # Skip processing binary data (e.g., Image column)
                    if i == 3:  # Assuming the binary image data is in column index 3
                        cell = '[Binary Data]'  # Or set to an appropriate placeholder
                    # Format date columns
                    elif i in [5, 6, 7]:  # Indices of date columns
                        if cell:
                            try:
                                cell = datetime.fromisoformat(cell).strftime('%Y-%m-%d')
                            except (ValueError, TypeError):
                                cell = ''  # Use an empty string for invalid or missing dates
                    # Handle None values
                    if cell is None:
                        cell = ''  # Replace None with an empty string
                    formatted_row.append(str(cell))  # Ensure all cells are strings
                formatted_results.append(formatted_row)

            print(tabulate(formatted_results, headers=headers, tablefmt='simple'))
        else:
            print("No plants found")
        return

    if args.command == 'add-plant':
        image_data = None
        image_mime_type = None
        if args.image:
            image_result = image_handler.read_image(args.image)
            if image_result:
                image_data, image_mime_type = image_result

        birthdate = None
        if args.age_months:
            birthdate = datetime.now() - relativedelta(months=args.age_months)

        plant = Plant(
            name=args.name,
            family=args.family,
            image_data=image_data,
            image_mime_type=image_mime_type,
            birthdate=birthdate,
            created_at=datetime.now()
        )
        plant_id = db.add_plant(plant)
        print(f"Plant added successfully with ID: {plant_id}")

    elif args.command == 'edit-plant':
        image_data = None
        image_mime_type = None
        if args.image:
            image_result = image_handler.read_image(args.image)
            if image_result:
                image_data, image_mime_type = image_result

        birthdate = None
        if args.age_months:
            birthdate = datetime.now() - relativedelta(months=args.age_months)

        updated = db.edit_plant(
            plant_id=args.id,
            name=args.name,
            family=args.family,
            image_data=image_data,
            image_mime_type=image_mime_type,
            birthdate=birthdate,
        )

        if updated:
            print(f"Plant with ID {args.id} updated successfully")
            plant = db.get_plant_by_id(args.id)
            if plant:
                print("\nUpdated plant details:")
                headers = ['ID', 'Name', 'Family', 'Image', 'MIME Type', 'Birthdate', 'Created At', 'Last Leaf Date']
                # Format the row to show image presence instead of binary data
                formatted_plant = list(plant)
                formatted_plant[3] = "Yes" if formatted_plant[3] else "No"  # Replace binary data with Yes/No
                print(tabulate([formatted_plant], headers=headers))
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

    elif args.command == 'show-image':
        if not args.id:
            print("Please provide a plant ID")
            return
        db.show_plant_image(args.id)

if __name__ == "__main__":
    main()