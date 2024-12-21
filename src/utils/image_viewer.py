import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO


class ImageViewer:
    def __init__(self):
        self.window = None

    def show_image(self, image_data: bytes, title: str = "Plant Image"):
        # Create window if it doesn't exist
        if not self.window:
            self.window = tk.Tk()
        self.window.title(title)

        # Create image from binary data
        image = Image.open(BytesIO(image_data))

        # Scale image if too large (max 800x800)
        if max(image.size) > 800:
            ratio = 800 / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        # Convert to Tkinter PhotoImage
        photo = ImageTk.PhotoImage(image)

        # Create and pack label with image
        label = ttk.Label(self.window, image=photo)
        label.image = photo  # Keep reference to prevent garbage collection
        label.pack(padx=10, pady=10)

        # Add close button
        close_btn = ttk.Button(self.window, text="Close", command=self.window.destroy)
        close_btn.pack(pady=5)

        self.window.mainloop()