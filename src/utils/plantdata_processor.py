from datetime import datetime
from typing import Any, Dict
from dateutil.relativedelta import relativedelta


class PlantDataProcessor:
    def __init__(self, image_handler):
        self.image_handler = image_handler

    def __call__(self, args: Any) -> Dict[str, Any]:
        image_data = image_mime_type = None
        if args.image:
            image_result = self.image_handler.read_image(args.image)
            if image_result:
                image_data, image_mime_type = image_result

        birthdate = None
        if args.age_months:
            birthdate = datetime.now() - relativedelta(months=args.age_months)

        return {
            'name': args.name,
            'family': args.family,
            'image_data': image_data,
            'image_mime_type': image_mime_type,
            'birthdate': birthdate
        }