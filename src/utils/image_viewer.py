import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import io
import platform
import sys
from typing import Optional, Tuple

class ImageViewer:
    """Handles image display in a Tkinter window"""
    
    def __init__(self):
        self.root = None
        # Check specifically for macOS on ARM
        self.is_apple_silicon = sys.platform == 'darwin' and platform.processor() == 'arm'

    def show_image(self, image_data: bytes, title: str = "Plant Image", 
                  window_size: Optional[Tuple[int, int]] = None) -> None:
        """Display an image in a Tkinter window"""
        try:
            # Create a new root window
            self.root = tk.Tk()
            self.root.title(title)

            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))

            # Handle window size
            if window_size:
                image = image.resize(window_size, Image.Resampling.LANCZOS)
            else:
                # Default max size while maintaining aspect ratio
                image.thumbnail((800, 800), Image.Resampling.LANCZOS)

            # Handle color mode for Apple Silicon
            if self.is_apple_silicon and image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)

            # Create and configure frame
            frame = ttk.Frame(self.root, padding="10")
            frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

            # Display image
            label = ttk.Label(frame, image=photo)
            label.image = photo  # Keep a reference
            label.grid(row=0, column=0, padx=5, pady=5)

            # Center window
            self.center_window()

            # Start event loop
            self.root.mainloop()

        except Exception as e:
            print(f"Error displaying image: {e}")
            if self.root:
                self.root.destroy()

    def center_window(self) -> None:
        """Center the window on screen"""
        if not self.root:
            return

        # Update window size
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - self.root.winfo_width()) // 2
        y = (screen_height - self.root.winfo_height()) // 2
        
        # Set window position
        self.root.geometry(f"+{x}+{y}")
