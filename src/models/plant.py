from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from statistics import mean

@dataclass
class Plant:
    name: str
    family: str
    birthdate: Optional[datetime] = None
    id: Optional[int] = None
    image_data: Optional[bytes] = None
    image_mime_type: Optional[str] = None
    created_at: Optional[datetime] = None
    last_leaf_date: Optional[datetime] = None
    leaf_records: List[datetime] = field(default_factory=list)
    last_watered: Optional[datetime] = None

    def __post_init__(self):
        # Convert string dates to datetime if needed
        if isinstance(self.birthdate, str):
            self.birthdate = datetime.strptime(self.birthdate, '%Y-%m-%d')
        if isinstance(self.last_watered, str):
            self.last_watered = datetime.strptime(self.last_watered, '%Y-%m-%d')

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Plant':
        """Create a Plant instance from a database row"""
        try:
            return cls(
                id=row[0],
                name=row[1],
                family=row[2],
                image_data=row[3],
                image_mime_type=row[4],
                birthdate=cls._parse_date(row[5]),
                created_at=cls._parse_date(row[6]),
                last_leaf_date=cls._parse_date(row[7]),
                last_watered=cls._parse_date(row[8])
            )
        except IndexError as e:
            raise ValueError(f"Invalid database row format: {e}")

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            return None

    def calculate_leaf_statistics(self) -> Dict:
        """Calculate statistics about leaf growth"""
        if not self.leaf_records:
            return {
                'total_leaves': 0,
                'avg_days_between_leaves': None,
                'days_since_last_leaf': None
            }

        total_leaves = len(self.leaf_records)
        sorted_dates = sorted(self.leaf_records)

        # Calculate average days between leaves
        if total_leaves > 1:
            intervals = [(sorted_dates[i + 1] - sorted_dates[i]).days
                        for i in range(total_leaves - 1)]
            avg_days = mean(intervals)
        else:
            avg_days = None

        # Calculate days since last leaf
        days_since_last = (datetime.now() - sorted_dates[-1]).days

        return {
            'total_leaves': total_leaves,
            'avg_days_between_leaves': avg_days,
            'days_since_last_leaf': days_since_last
        }

    def __str__(self) -> str:
        return f"{self.name} ({self.family})"
