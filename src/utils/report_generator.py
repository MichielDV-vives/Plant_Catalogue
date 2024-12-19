from pathlib import Path
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
