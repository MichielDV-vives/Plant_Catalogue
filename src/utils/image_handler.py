from pathlib import Path
from typing import Optional
from configparser import ConfigParser
from PIL import Image, ExifTags
import time


class ImageHandler:
    def __init__(self) -> None:
        config = ConfigParser()
        config.read('config.ini')
        self.storage_path = Path(config['images']['storage_path'])
        self.storage_path.mkdir(exist_ok=True)

    def save_image(self, image_path: str, plant_name: str, plant_family: str) -> Optional[str]:
        """Save and optimize plant image"""
        if not image_path or not Path(image_path).exists():
            return None

        # Create a safe filename from plant name and family
        safe_name = "".join(c for c in plant_name if c.isalnum() or c in "._- ")
        safe_family = "".join(c for c in plant_family if c.isalnum() or c in "._- ")
        if not safe_name:
            safe_name = "plant"
        if not safe_family:
            safe_family = "family"

        # Add a Unix timestamp to ensure uniqueness
        timestamp = int(time.time())
        new_path = self.storage_path / f"{safe_name}_{safe_family}_{timestamp}.jpg"

        # Optimize and save image
        try:
            with Image.open(image_path) as img:
                # Handle EXIF orientation
                exif = img._getexif()
                if exif is not None:
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                    orientation = exif.get(orientation)
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)

                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                # Resize if too large while maintaining aspect ratio
                if max(img.size) > 1200:
                    img.thumbnail((1200, 1200))
                # Save with optimization
                img.save(new_path, 'JPEG', quality=85, optimize=True)
            print(f"Image saved to {new_path}")
        except Exception as e:
            print(f"Error saving image: {e}")
            return None

        return str(new_path)