import qrcode
from pathlib import Path
from typing import Optional
import cv2
import numpy as np
import time

class QRHandlerError(Exception):
    """Custom exception for QR handler errors"""
    pass

class QRHandler:
    def __init__(self):
        self.qr_dir = Path('data/qr_codes')
        self.qr_dir.mkdir(exist_ok=True)
        self.last_scanned = None

    def get_qr_path(self, plant_id: int) -> Path:
        """Get the path to a QR code file"""
        return self.qr_dir / f"plant_{plant_id}_qr.png"

    def save_qr_code(self, plant_id: int) -> Path:
        """Generate and save QR code for a plant ID"""
        try:
            qr_path = self.get_qr_path(plant_id)
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(str(plant_id))
            qr.make(fit=True)
            
            # Create QR image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Save to file
            qr_image.save(qr_path)
            return qr_path
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None

    def scan_qr(self, show_image: bool = True) -> Optional[int]:
        """Scan QR code using webcam"""
        try:
            import tkinter as tk
            from PIL import Image, ImageTk
            import cv2
            
            # Initialize camera
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Could not open camera")
                return None

            # Create Tkinter window
            root = tk.Tk()
            root.title("QR Scanner")
            
            # Create label for video feed
            label = tk.Label(root)
            label.pack()

            def update_frame():
                ret, frame = cap.read()
                if ret:
                    # Convert frame to RGB for PIL
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Detect QR code
                    detector = cv2.QRCodeDetector()
                    data, bbox, _ = detector.detectAndDecode(frame)
                    
                    if data:
                        try:
                            plant_id = int(data)
                            self.last_scanned = plant_id
                            cap.release()
                            root.quit()
                            root.destroy()
                            return plant_id
                        except ValueError:
                            pass

                    # Convert frame to PhotoImage
                    img = Image.fromarray(frame_rgb)
                    img.thumbnail((640, 480))
                    imgtk = ImageTk.PhotoImage(image=img)
                    label.imgtk = imgtk
                    label.configure(image=imgtk)
                    
                    # Schedule next update
                    root.after(10, update_frame)
                else:
                    cap.release()
                    root.quit()
                    root.destroy()

            # Add quit button
            quit_button = tk.Button(root, text="Cancel", command=root.destroy)
            quit_button.pack(pady=10)

            # Start update loop
            root.after(0, update_frame)
            root.mainloop()

            return self.last_scanned

        except Exception as e:
            print(f"Error scanning QR code: {e}")
            if 'cap' in locals():
                cap.release()
            return None

    def display_qr(self, plant_id: Optional[int] = None) -> Optional[Path]:
        """Get QR code path for display"""
        try:
            if plant_id is None:
                if self.last_scanned is None:
                    print("No QR code has been scanned")
                    return None
                plant_id = self.last_scanned

            qr_path = self.get_qr_path(plant_id)
            
            # Generate QR code if it doesn't exist
            if not qr_path.exists():
                qr_path = self.save_qr_code(plant_id)
            
            if not qr_path or not qr_path.exists():
                print(f"Could not find or generate QR code for plant {plant_id}")
                return None
                
            return qr_path

        except Exception as e:
            print(f"Error accessing QR code: {e}")
            return None 
