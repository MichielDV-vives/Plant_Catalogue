from pathlib import Path
from typing import Optional
from configparser import ConfigParser
from PIL import Image

class ImageHandler:
    def __init__(self) -> None:
        config = ConfigParser()
        config.read('config.ini')
        self.storage_path = Path(config['images']['storage_path'])
        self.storage_path.mkdir(exist_ok=True)

    def save_image(self, image_path: str, plant_name: str) -> Optional[str]:
        if not image_path or not Path(image_path).exists():
            return None
        safe_name = "".join(c for c in plant_name if c.isalnum() or c in "._- ")
        new_path = self.storage_path / f"{safe_name}.jpg"
        with Image.open(image_path) as img:
            if max(img.size) > 1200:
                img.thumbnail((1200, 1200))
            img.save(new_path, 'JPEG', quality=85, optimize=True)
        return str(new_path)