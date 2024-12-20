from pathlib import Path
import csv
from typing import List, Tuple, Dict
from configparser import ConfigParser
from datetime import datetime
from statistics import mean, median
from collections import Counter


class ReportGenerator:
    def __init__(self) -> None:
        config = ConfigParser()
        config.read('config.ini')
        self.output_dir = Path(config['reports']['output_dir'])
        self.output_dir.mkdir(exist_ok=True)

    def _generate_statistics(self, plants: List[Tuple]) -> Dict:
        if not plants:
            return {}

        # Extract data from tuples (assuming order: ID, Name, Family, Image, Age, Added Date)
        ages = [plant[4] for plant in plants if plant[4] is not None]
        families = [plant[2] for plant in plants]

        stats = {
            "Total Plants": len(plants),
            "Number of Families": len(set(families)),
            "Most Common Family": Counter(families).most_common(1)[0] if families else None,
            "Plants with Images": sum(1 for plant in plants if plant[3]),
            "Age Statistics": {
                "Average Age": round(mean(ages), 1) if ages else 0,
                "Median Age": round(median(ages), 1) if ages else 0,
                "Youngest": min(ages) if ages else 0,
                "Oldest": max(ages) if ages else 0
            },
            "Family Distribution": dict(Counter(families)),
            "Report Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return stats

    def generate_plant_report(self, plants: List[Tuple]) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f'plant_collection_{timestamp}.csv'
        stats = self._generate_statistics(plants)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write report header
            writer.writerow(['Plant Collection Report'])
            writer.writerow([f'Generated on: {stats["Report Generated"]}'])
            writer.writerow([])

            # Write collection statistics
            writer.writerow(['Collection Statistics'])
            writer.writerow(['Total Plants', stats['Total Plants']])
            writer.writerow(['Number of Families', stats['Number of Families']])
            if stats['Most Common Family']:
                writer.writerow(['Most Common Family',
                                 f"{stats['Most Common Family'][0]} ({stats['Most Common Family'][1]} plants)"])
            writer.writerow(['Plants with Images', stats['Plants with Images']])
            writer.writerow([])

            # Write age statistics
            writer.writerow(['Age Statistics'])
            writer.writerow(['Average Age', stats['Age Statistics']['Average Age']])
            writer.writerow(['Median Age', stats['Age Statistics']['Median Age']])
            writer.writerow(['Youngest Plant', stats['Age Statistics']['Youngest']])
            writer.writerow(['Oldest Plant', stats['Age Statistics']['Oldest']])
            writer.writerow([])

            # Write family distribution
            writer.writerow(['Family Distribution'])
            for family, count in stats['Family Distribution'].items():
                writer.writerow([family, count])
            writer.writerow([])

            # Write individual plant data
            writer.writerow(['Individual Plant Details'])
            writer.writerow(['ID', 'Name', 'Family', 'Image Path', 'Age (Years)', 'Added Date'])
            writer.writerows(plants)

        return str(filepath)