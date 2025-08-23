import json
import os
import datetime
from typing import Dict, List, Optional

class SaveSlotManager:
    def __init__(self, max_slots: int = 5):
        self.max_slots = max_slots
        self.save_directory = "saves"
        self.ensure_save_directory()
    
    def ensure_save_directory(self):
        """Create saves directory if it doesn't exist"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def get_save_filename(self, slot_number: int) -> str:
        """Generate filename for a specific save slot"""
        return os.path.join(self.save_directory, f"savegame_slot_{slot_number}.json")
    
    def get_all_save_info(self) -> List[Dict]:
        """Get information about all save slots"""
        save_info = []
        
        for slot in range(1, self.max_slots + 1):
            filename = self.get_save_filename(slot)
            
            if os.path.exists(filename) and self.is_valid_save_file(filename):
                try:
                    with open(filename, 'r') as file:
                        data = json.load(file)
                        
                    save_info.append({
                        'slot': slot,
                        'exists': True,
                        'player_name': data.get('player_name', 'Unknown'),
                        'days_passed': data.get('days_passed', 0),
                        'gold': data.get('gold', 0),
                        'save_date': data.get('save_date', 'Unknown'),
                        'playtime': data.get('playtime', 'Unknown')
                    })
                except Exception:
                    save_info.append({
                        'slot': slot,
                        'exists': False,
                        'corrupted': True
                    })
            else:
                save_info.append({
                    'slot': slot,
                    'exists': False
                })
        
        return save_info
    
    def is_valid_save_file(self, filepath: str) -> bool:
        """Check if save file exists and contains valid save game data"""
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                
            if not isinstance(data, dict) or len(data) == 0:
                return False
            
            expected_keys = ['player_name', 'gold', 'cart', 'completed_quests', 
                           'days_passed', 'time_of_day', 'weather', 'german_arrival_day']
            
            return any(key in data for key in expected_keys)
            
        except (json.JSONDecodeError, FileNotFoundError, IOError):
            return False
    
    def display_save_slots(self):
        """Display all save slots in a formatted way"""
        print("\n" + "="*60)
        print("                    SAVE SLOTS")
        print("="*60)
        
        save_info = self.get_all_save_info()
        
        for info in save_info:
            slot_num = info['slot']
            
            if info['exists']:
                if info.get('corrupted'):
                    print(f"[{slot_num}] CORRUPTED SAVE FILE")
                else:
                    print(f"[{slot_num}] {info['player_name']} - Day {info['days_passed']} - {info['gold']} gold")
                    print(f"    Saved: {info['save_date']}")
            else:
                print(f"[{slot_num}] Empty Slot")
            
            print("-" * 60)
        
        print("[0] Back to main menu")
        print("="*60)
    
    def save_game_to_slot(self, slot_number: int, player_name: str, gold: int, 
                         cart: List, completed_quests: List, days_passed: int,
                         time_of_day: str, weather: str, german_arrival_day: int,
                         start_time: datetime.datetime = None) -> bool:
        """Save game data to specific slot"""
        if slot_number < 1 or slot_number > self.max_slots:
            print(f"Invalid slot number! Must be between 1 and {self.max_slots}")
            return False
        
        filename = self.get_save_filename(slot_number)
        
        # Calculate playtime if start_time is provided
        playtime = "Unknown"
        if start_time:
            current_time = datetime.datetime.now()
            time_diff = current_time - start_time
            hours, remainder = divmod(time_diff.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            playtime = f"{int(hours):02d}:{int(minutes):02d}"
        
        save_data = {
            'player_name': player_name,
            'gold': gold,
            'cart': cart,
            'completed_quests': completed_quests,
            'days_passed': days_passed,
            'time_of_day': time_of_day,
            'weather': weather,
            'german_arrival_day': german_arrival_day,
            'save_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'playtime': playtime
        }
        
        try:
            with open(filename, 'w') as file:
                json.dump(save_data, file, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False
    
    def load_game_from_slot(self, slot_number: int) -> Optional[Dict]:
        """Load game data from specific slot"""
        if slot_number < 1 or slot_number > self.max_slots:
            return None
        
        filename = self.get_save_filename(slot_number)
        
        if not self.is_valid_save_file(filename):
            return None
        
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Failed to load game: {e}")
            return None
    
    def delete_save_slot(self, slot_number: int) -> bool:
        """Delete a save slot"""
        if slot_number < 1 or slot_number > self.max_slots:
            return False
        
        filename = self.get_save_filename(slot_number)
        
        if os.path.exists(filename):
            try:
                os.remove(filename)
                return True
            except Exception as e:
                print(f"Failed to delete save: {e}")
                return False
        return True

def handle_save_menu(save_manager: SaveSlotManager, player_name: str, gold: int,
                    cart: List, completed_quests: List, days_passed: int,
                    time_of_day: str, weather: str, german_arrival_day: int,
                    start_time: datetime.datetime = None):
    """Handle the save game menu"""
    while True:
        save_manager.display_save_slots()
        
        try:
            choice = input("\nSelect slot to save (1-5) or 0 to cancel: ").strip()
            
            if choice == '0':
                break
            
            slot_num = int(choice)
            if slot_num < 1 or slot_num > save_manager.max_slots:
                print("Invalid slot number!")
                input("Press Enter to continue...")
                continue
            
            # Check if slot has existing save
            save_info = save_manager.get_all_save_info()
            slot_info = next((info for info in save_info if info['slot'] == slot_num), None)
            
            if slot_info and slot_info['exists']:
                confirm = input(f"Slot {slot_num} already contains a save. Overwrite? (y/n): ").lower()
                if confirm != 'y':
                    continue
            
            if save_manager.save_game_to_slot(slot_num, player_name, gold, cart,
                                            completed_quests, days_passed, time_of_day,
                                            weather, german_arrival_day, start_time):
                print(f"Game saved to slot {slot_num} successfully!")
                input("Press Enter to continue...")
                break
            else:
                print("Failed to save game!")
                input("Press Enter to continue...")
                
        except ValueError:
            print("Please enter a valid number!")
            input("Press Enter to continue...")

def handle_load_menu(save_manager: SaveSlotManager) -> Optional[Dict]:
    """Handle the load game menu"""
    while True:
        save_manager.display_save_slots()
        
        try:
            choice = input("\nSelect slot to load (1-5), 'd' to delete, or 0 to cancel: ").strip().lower()
            
            if choice == '0':
                return None
            
            if choice == 'd':
                delete_slot = input("Which slot to delete (1-5)? ").strip()
                try:
                    delete_num = int(delete_slot)
                    if 1 <= delete_num <= save_manager.max_slots:
                        confirm = input(f"Really delete slot {delete_num}? (y/n): ").lower()
                        if confirm == 'y':
                            if save_manager.delete_save_slot(delete_num):
                                print(f"Slot {delete_num} deleted!")
                            else:
                                print("Failed to delete slot!")
                    else:
                        print("Invalid slot number!")
                except ValueError:
                    print("Invalid input!")
                input("Press Enter to continue...")
                continue
            
            slot_num = int(choice)
            if slot_num < 1 or slot_num > save_manager.max_slots:
                print("Invalid slot number!")
                input("Press Enter to continue...")
                continue
            
            save_data = save_manager.load_game_from_slot(slot_num)
            if save_data:
                return save_data
            else:
                print("No valid save data in this slot!")
                input("Press Enter to continue...")
                
        except ValueError:
            print("Please enter a valid number!")
            input("Press Enter to continue...")