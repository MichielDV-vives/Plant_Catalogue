from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class Plant:
    name: str
    family: str
    age: int
    id: Optional[int] = None
    image_path: Optional[str] = None
    created_at: Optional[datetime] = None
    last_leaf_date: Optional[datetime] = None
    leaf_records: List[datetime] = field(default_factory=list)

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Plant':
        return cls(
            id=row[0],
            name=row[1],
            family=row[2],
            image_path=row[3],
            age=row[4],
            created_at=datetime.fromisoformat(row[5]) if row[5] else None,
            last_leaf_date=datetime.fromisoformat(row[6]) if row[6] else None
        )

    def calculate_leaf_statistics(self) -> dict:
        if not self.leaf_records:
            return {
                'total_leaves': 0,
                'avg_days_between_leaves': None,
                'days_since_last_leaf': None
            }

        total_leaves = len(self.leaf_records)

        # Calculate average days between leaves
        if total_leaves > 1:
            intervals = [(self.leaf_records[i + 1] - self.leaf_records[i]).days
                         for i in range(total_leaves - 1)]
            avg_days = sum(intervals) / len(intervals)
        else:
            avg_days = None

        # Calculate days since last leaf
        days_since_last = (datetime.now() - self.leaf_records[-1]).days if self.leaf_records else None

        return {
            'total_leaves': total_leaves,
            'avg_days_between_leaves': avg_days,
            'days_since_last_leaf': days_since_last
        }
