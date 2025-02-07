from typing import Optional
from utils.qr_handler import QRHandler
from database import db_operations as db
import os

class PlantInteraction:
    def __init__(self):
        self.qr_handler = QRHandler()
        
    def show_plant_menu(self, plant_id: int) -> None:
        """Show interactive menu for plant"""
        plant = db.get_plant_by_id(plant_id)
        
        while True:
            print("\n" * 5)
            print(f"Plant Menu: {plant[1]} - {plant[2]}")
            print("Choose an option:")
            print("1. Add new leaf")
            print("2. View leaf statistics")
            print("3. Show image")
            print("4. Water plant")
            print("5. View watering info")
            print("6. Exit")

            choice = input("\nEnter choice (1-6): ")
            print("\n" * 3)
            
            if choice == "1":
                db.add_leaf_record(plant_id)
                print("Leaf record added successfully")
            elif choice == "2":
                self.show_plant_stats(plant_id)
            elif choice == "3":
                db.show_plant_image(plant_id)
            elif choice == "4":
                if db.update_last_watered(plant_id):
                    print("Watering recorded successfully")
                else:
                    print("Failed to record watering")
            elif choice == "5":
                self.show_watering_info(plant_id)
            elif choice == "6":
                print("Exiting plant menu")
                break
            else:
                print("Invalid option. Please choose 1-6")
            
            input("\nPress Enter to continue...")

    def show_plant_stats(self, plant_id: int) -> None:
        """Show statistics for a plant"""
        stats = db.get_leaf_statistics(plant_id)
        if not stats:
            print("No statistics available")
            return

        plant = db.get_plant_by_id(plant_id)
        print(f"\nLeaf Statistics for {plant[1]}:")
        print(f"Total leaves: {stats['total_leaves']}")
        if stats['avg_days_between_leaves']:
            print(f"Average days between leaves: {stats['avg_days_between_leaves']:.1f}")
        if stats['days_since_last_leaf'] is not None:
            print(f"Days since last leaf: {stats['days_since_last_leaf']}")

    def show_watering_info(self, plant_id: int) -> None:
        """Show watering information"""
        info = db.get_watering_info(plant_id)
        if info:
            print("\nWatering Information:")
            if info['last_watered']:
                print(f"Last watered: {info['last_watered'].strftime('%Y-%m-%d')}")
                print(f"Days since last watering: {info['days_since_watered']}")
            else:
                print("Plant has never been watered") 
