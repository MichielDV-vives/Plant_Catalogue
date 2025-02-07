import argparse
from datetime import datetime
from typing import Optional

def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(description='Plant Catalogue CLI')
    subparsers = parser.add_subparsers(dest='command', help='commands')

    # List plants
    list_parser = subparsers.add_parser('list', help='List all plants')

    # Add plant
    add_parser = subparsers.add_parser('add-plant', help='Add a new plant')
    add_parser.add_argument('--name', required=True, help='Plant name')
    add_parser.add_argument('--family', required=True, help='Plant family')
    add_parser.add_argument('--image', help='Path to plant image')
    add_parser.add_argument('--age-months', type=int, help='Plant age in months')
    add_parser.add_argument('--birthdate', help='Plant birthdate (YYYY-MM-DD)')

    # Edit plant
    edit_parser = subparsers.add_parser('edit-plant', help='Edit an existing plant')
    edit_parser.add_argument('--id', type=int, required=True, help='Plant ID')
    edit_parser.add_argument('--name', help='New plant name')
    edit_parser.add_argument('--family', help='New plant family')
    edit_parser.add_argument('--image', help='New plant image path')

    # Generate report
    subparsers.add_parser('report', help='Generate plant report')

    # Add leaf record
    leaf_parser = subparsers.add_parser('add-leaf', help='Add a leaf record')
    leaf_parser.add_argument('--id', type=int, required=True, help='Plant ID')
    leaf_parser.add_argument('--date', help='Record date (YYYY-MM-DD)')

    # Leaf statistics
    stats_parser = subparsers.add_parser('leaf-stats', help='Show leaf statistics')
    stats_parser.add_argument('--id', type=int, help='Plant ID (optional, for specific plant)')

    # Show image
    image_parser = subparsers.add_parser('show-image', help='Display plant image')
    image_parser.add_argument('--id', type=int, required=True, help='Plant ID')

    # Search plants
    search_parser = subparsers.add_parser('search-plant', help='Search plants by name or family')
    search_parser.add_argument('--query', required=True, help='Search term')

    # QR code scanning
    subparsers.add_parser('scan', help='Scan QR code and interact with plant')
    subparsers.add_parser('list-qr', help='List all available QR codes')

    # Database migrations
    subparsers.add_parser('migrate', help='Perform database migrations')

    # Watering management
    water_parser = subparsers.add_parser('water', help='Record watering for a plant')
    water_parser.add_argument('--id', type=int, required=True, help='Plant ID')

    water_info_parser = subparsers.add_parser('water-info', help='Show watering information')
    water_info_parser.add_argument('--id', type=int, required=True, help='Plant ID')

    return parser

def validate_args(args) -> bool:
    """Validate command line arguments"""
    if not args.command:
        print("Please specify a command. Use -h for help.")
        return False

    if args.command == 'add-plant' and args.birthdate:
        try:
            datetime.strptime(args.birthdate, '%Y-%m-%d')
        except ValueError:
            print("Invalid birthdate format. Use YYYY-MM-DD")
            return False

    if args.command == 'add-leaf' and args.date:
        try:
            datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            return False

    return True
