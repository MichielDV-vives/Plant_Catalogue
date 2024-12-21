from typing import Optional, Tuple
from utils.image_processor import process_image
from utils.image_viewer import ImageViewer

class ImageHandler:
    def __init__(self):
        self.viewer = ImageViewer()

    def read_image(self, image_path: str) -> Optional[Tuple[bytes, str]]:

        try:
            with open(image_path, 'rb') as f:
                original_image_data = f.read()
            # Process the image using image_processor
            return process_image(original_image_data)
        except Exception as e:
            print(f"Error reading image file: {e}")
            return None

    def display_image(self, image_data: bytes, title: str = "Plant Image") -> None:
        self.viewer.show_image(image_data, title)