from pathlib import Path
import csv
from typing import List, Tuple, Dict
from configparser import ConfigParser
from datetime import datetime
from statistics import mean, median
from collections import Counter

class ReportGenerator:
    def __init__(self) -> None:
        self.output_dir = self._get_output_dir()
        self.output_dir.mkdir(exist_ok=True)

    def _get_output_dir(self) -> Path:
        """Get output directory from config"""
        config = ConfigParser()
        config.read('config.ini')
        return Path(config['reports']['output_dir'])

    def generate_plant_report(self, plants: List[Tuple]) -> str:
        """Generate a comprehensive plant report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.output_dir / f'plant_collection_{timestamp}.csv'
        
        stats = self._generate_statistics(plants)
        self._write_report(filepath, plants, stats)
        
        return str(filepath)

    def _generate_statistics(self, plants: List[Tuple]) -> Dict:
        """Generate statistics from plant data"""
        if not plants:
            return self._empty_statistics()

        ages = self._extract_ages(plants)
        families = [plant[2] for plant in plants]
        
        return {
            "Total Plants": len(plants),
            "Number of Families": len(set(families)),
            "Most Common Family": Counter(families).most_common(1)[0] if families else None,
            "Plants with Images": sum(1 for plant in plants if plant[3]),
            "Age Statistics": self._calculate_age_statistics(ages),
            "Family Distribution": dict(Counter(families)),
            "Report Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _write_report(self, filepath: Path, plants: List[Tuple], stats: Dict) -> None:
        """Write report to CSV file"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            self._write_header_section(writer, stats)
            self._write_statistics_section(writer, stats)
            self._write_plants_section(writer, plants)

    def _write_header_section(self, writer: csv.writer, stats: Dict) -> None:
        """Write report header"""
        writer.writerow(['Plant Collection Report'])
        writer.writerow([f'Generated on: {stats["Report Generated"]}'])
        writer.writerow([])

    def _write_statistics_section(self, writer: csv.writer, stats: Dict) -> None:
        """Write statistics section"""
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
        for key, value in stats['Age Statistics'].items():
            writer.writerow([key, value])
        writer.writerow([])

        # Write family distribution
        writer.writerow(['Family Distribution'])
        for family, count in stats['Family Distribution'].items():
            writer.writerow([family, count])
        writer.writerow([])

    def _write_plants_section(self, writer: csv.writer, plants: List[Tuple]) -> None:
        """Write individual plant details"""
        writer.writerow(['Individual Plant Details'])
        writer.writerow(['ID', 'Name', 'Family', 'Image', 'Birthdate', 'Added Date'])
        
        for plant in plants:
            row = list(plant)
            row[3] = "Yes" if isinstance(row[3], bytes) else "No"  # Replace binary data
            writer.writerow(row)

    @staticmethod
    def _empty_statistics() -> Dict:
        """Return empty statistics structure"""
        return {
            "Total Plants": 0,
            "Number of Families": 0,
            "Most Common Family": None,
            "Plants with Images": 0,
            "Age Statistics": {
                "Average Age": 0,
                "Median Age": 0,
                "Youngest": 0,
                "Oldest": 0
            },
            "Family Distribution": {},
            "Report Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def _extract_ages(plants: List[Tuple]) -> List[float]:
        """Extract valid ages from plant data"""
        ages = []
        for plant in plants:
            age = plant[4]
            if age is not None:
                try:
                    ages.append(float(age))
                except ValueError:
                    continue
        return ages

    @staticmethod
    def _calculate_age_statistics(ages: List[float]) -> Dict:
        """Calculate statistics for plant ages"""
        if not ages:
            return {
                "Average Age": 0,
                "Median Age": 0,
                "Youngest": 0,
                "Oldest": 0
            }
        
        return {
            "Average Age": round(mean(ages), 1),
            "Median Age": round(median(ages), 1),
            "Youngest": min(ages),
            "Oldest": max(ages)
        }
