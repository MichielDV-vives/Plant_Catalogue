from datetime import datetime
from typing import Any, Dict, Optional
from dataclasses import dataclass
from dateutil.relativedelta import relativedelta
from argparse import Namespace
from .image_handler import ImageHandler, ProcessedImage

@dataclass
class PlantData:
    name: Optional[str] = None
    family: Optional[str] = None
    image_data: Optional[bytes] = None
    image_mime_type: Optional[str] = None
    birthdate: Optional[datetime] = None
    created_at: Optional[datetime] = None

class PlantDataProcessor:
    def __init__(self, image_handler: ImageHandler):
        self.image_handler = image_handler

    def __call__(self, args: Namespace) -> Dict[str, Any]:
        """Process command line arguments into plant data"""
        plant_data = PlantData()
        
        # Process basic data
        plant_data.name = args.name
        plant_data.family = args.family
        plant_data.created_at = datetime.now()

        # Process image if provided
        if args.image:
            processed_image = self.image_handler.read_image(args.image)
            if processed_image:
                plant_data.image_data = processed_image.data
                plant_data.image_mime_type = processed_image.mime_type

        # Calculate birthdate from age if provided
        if args.age_months:
            plant_data.birthdate = datetime.now() - relativedelta(months=args.age_months)

        return self._to_dict(plant_data)

    @staticmethod
    def _to_dict(data: PlantData) -> Dict[str, Any]:
        """Convert PlantData to dictionary, excluding None values"""
        return {k: v for k, v in data.__dict__.items() if v is not None}
