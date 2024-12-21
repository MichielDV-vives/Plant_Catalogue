from PIL import Image, ExifTags
from io import BytesIO
from typing import Optional, Tuple


def process_image(image_data: bytes) -> Optional[Tuple[bytes, str]]:
    try:
        # Read image from binary data
        with BytesIO(image_data) as input_buffer:
            with Image.open(input_buffer) as img:
                # Handle EXIF orientation
                img = _fix_orientation(img)

                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Resize if too large while maintaining aspect ratio
                if max(img.size) > 1200:
                    img.thumbnail((1200, 1200))

                # Save optimized image to bytes
                output_buffer = BytesIO()
                img.save(output_buffer, format='JPEG', quality=85, optimize=True)
                return output_buffer.getvalue(), 'image/jpeg'
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def _fix_orientation(img: Image.Image) -> Image.Image:
    try:
        exif = img._getexif()
        if exif is not None:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            orientation = exif.get(orientation)
            if orientation == 3:
                return img.rotate(180, expand=True)
            elif orientation == 6:
                return img.rotate(270, expand=True)
            elif orientation == 8:
                return img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass
    return img