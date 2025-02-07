from typing import Optional
from pathlib import Path
from PIL import Image, ExifTags
from io import BytesIO
from dataclasses import dataclass
from utils.image_viewer import ImageViewer

@dataclass
class ProcessedImage:
    data: bytes
    mime_type: str

class ImageProcessingError(Exception):
    """Custom exception for image processing errors"""
    pass

class ImageHandler:
    def __init__(self):
        self.viewer = ImageViewer()

    def display_image(self, image_data: bytes, title: str = "Plant Image") -> None:
        """Display an image using the viewer"""
        try:
            if not image_data:
                raise ImageProcessingError("No image data provided")
            self.viewer.show_image(image_data, title)
        except Exception as e:
            print(f"Error displaying image: {e}")

    def read_image(self, image_path: str) -> Optional[ProcessedImage]:
        """Read and process an image file"""
        try:
            path = Path(image_path)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            with Image.open(path) as img:
                # Fix orientation and convert to RGB if needed
                img = self._fix_orientation(img)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                
                # Save to bytes
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True)
                return ProcessedImage(
                    data=buffer.getvalue(),
                    mime_type='image/jpeg'
                )
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def _fix_orientation(self, img: Image.Image) -> Image.Image:
        """Fix image orientation based on EXIF data"""
        try:
            exif = img._getexif()
            if not exif:
                return img

            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            
            orientation_value = exif.get(orientation)
            if orientation_value == 3:
                return img.rotate(180, expand=True)
            elif orientation_value == 6:
                return img.rotate(270, expand=True)
            elif orientation_value == 8:
                return img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass
        return img
