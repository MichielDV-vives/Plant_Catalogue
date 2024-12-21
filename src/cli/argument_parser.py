from argparse import ArgumentParser
from argparse import Namespace

def create_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Plant Catalogue System')
    parser.add_argument('command', nargs='?', default='list', choices=[
        'list',
        'add-plant',
        'search-plant',
        'report',
        'edit-plant',
        'add-leaf',
        'leaf-stats',
        'show-image'
    ])
    parser.add_argument('--name', help='Plant name')
    parser.add_argument('--family', help='Plant family')
    parser.add_argument('--image', help='Path to plant image')
    parser.add_argument('--age-months', type=int, help='Plant age in months')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--id', type=int, help='Plant ID for editing')
    parser.add_argument('--date', help='Date of leaf appearance (YYYY-MM-DD)')
    return parser

def validate_args(args: Namespace) -> bool:
    if args.command == 'add-plant':
        if not all([args.name, args.family]):
            print("Plant name and family are required")
            return False
    elif args.command == 'search-plant':
        if not args.query:
            print("Please provide a search query")
            return False
    elif args.command == 'edit-plant':
        if not args.id:
            print("Please provide a plant ID to edit")
            return False
        if not any([args.name, args.family, args.image, args.age_months]):
            print("Please provide at least one field to update")
            return False
    return True