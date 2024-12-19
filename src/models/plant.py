from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Plant:
    name: str
    family: str
    age: int
    id: Optional[int] = None
    image_path: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Plant':
        return cls(
            id=row[0],
            name=row[1],
            family=row[2],
            image_path=row[3],
            age=row[4],
            created_at=datetime.fromisoformat(row[5]) if row[5] else None
        )