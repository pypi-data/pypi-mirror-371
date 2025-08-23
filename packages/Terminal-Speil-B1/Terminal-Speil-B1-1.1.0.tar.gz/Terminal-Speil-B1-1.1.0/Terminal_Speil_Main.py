# PLEASE ENTER 
# 'cls'
# 'python -W ignore Terminal_Speil_Main.py'

# TO RUN THE FILE,
# THANKS, BASANTA

import json
import random
import datetime
import os
import sys
from utils import *
from game_data import *
from save_system import *

def main():
    clear_terminal()
    print("Starting Terminal Speil...")
    
    # GLOBAL VARIABLES/DEFINES
    start_time = datetime.datetime.now()
    completed_quests = []
    time_of_day = "morning"
    weather = "clear"
    gold = 10000
    cart = ["healing potion"]
    game_ended = False
    days_passed = 0
    german_arrival_day = 7
    player_name = ""
    
    # MAIN CODE
    print("""
    '########:'########:'########::'##::::'##:'####:'##::: ##::::'###::::'##:::::::::::'######::'########::'########:'####:'##:::::::
    ... ##..:: ##.....:: ##.... ##: ###::'###:. ##:: ###:: ##:::'## ##::: ##::::::::::'##... ##: ##.... ##: ##.....::. ##:: ##:::::::
    ::: ##:::: ##::::::: ##:::: ##: ####'####:: ##:: ####: ##::'##:. ##:: ##:::::::::: ##:::..:: ##:::: ##: ##:::::::: ##:: ##:::::::
    ::: ##:::: ######::: ########:: ## ### ##:: ##:: ## ## ##:'##:::. ##: ##::::::::::. ######:: ########:: ######:::: ##:: ##:::::::
    ::: ##:::: ##...:::: ##.. ##::: ##. #: ##:: ##:: ##. ####: #########: ##:::::::::::..... ##: ##.....::: ##...::::: ##:: ##:::::::
    ::: ##:::: ##::::::: ##::. ##:: ##:.:: ##:: ##:: ##:. ###: ##.... ##: ##::::::::::'##::: ##: ##:::::::: ##:::::::: ##:: ##:::::::
    ::: ##:::: ########: ##:::. ##: ##:::: ##:'####: ##::. ##: ##:::: ##: ########::::. ######:: ##:::::::: ########:'####: ########:
    :::..:::::........::..:::::..::..:::::..::....::..::::..::..:::::..::........::::::......:::..:::::::::........::....::........:: """)
    
    # Check if any save files exist
    save_manager = SaveSlotManager(max_slots=5)   
    save_info = save_manager.get_all_save_info()

    has_saves = any(info['exists'] for info in save_info)
    if has_saves:
        load_choice = get_valid_input("Found saved games! Load one? (y/n): ", ['y', 'n'])
        if load_choice == 'y':
            save_data = handle_load_menu(save_manager)
            if save_data:
                player_name = save_data.get('player_name', '')
                gold = save_data.get('gold', 10000)
                cart = save_data.get('cart', ["healing potion"])
                completed_quests = save_data.get('completed_quests', [])
                days_passed = save_data.get('days_passed', 0)
                time_of_day = save_data.get('time_of_day', 'morning')
                weather = save_data.get('weather', 'clear')
                german_arrival_day = save_data.get('german_arrival_day', 7)
                print(f"Welcome back, Sir {player_name}!")
    
    if not player_name: 
        # Get start game input
        start_choice = get_valid_input("Shall we begin our adventure? (y/n): ", ['y', 'n'])
        if start_choice == 'n':
            print("Game cancelled!")
            sys.exit()

        # Get player name
        player_name = input("Enter character name: ").strip()
        if not player_name:
            player_name = "Hero"

    # Show opening intro
    show_opening_intro(player_name)
    
    # Show current time
    current_hour = datetime.datetime.now().hour
    current_time = datetime.datetime.now()
    print(f"Adventure starts at: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Set time_of_day based on real time if starting new game
    if days_passed == 0:
        if current_hour < 6:
            time_of_day = "night"
        elif current_hour < 12:
            time_of_day = "morning" 
        elif current_hour < 18:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"

    # Main game loop
    while not game_ended:
        # Show daily interlude at the start of each day
        if time_of_day == "morning":
            show_daily_interlude(days_passed + 1, player_name)
        
        # Check if Germans have arrived
        if days_passed >= german_arrival_day:
            show_final_battle_intro(player_name)
            
            battle_choice = get_valid_input("Face the Germans in battle? (yes/flee): ", ['yes', 'flee'])
            if battle_choice == 'flee':
                print("You flee the village in shame...")
                print("COWARD'S ENDING: The villagers are left to their fate.")
                print("Thanks for playing!")
                game_ended = True
                break
            else:
                game_ended = handle_final_battle(cart, player_name, completed_quests, days_passed)
                break

        # Weather changes
        if random.random() < 0.2:
            old_weather = weather
            weather = random.choice(["clear", "cloudy", "rainy", "foggy"])
            if weather != old_weather:
                print(f"\nThe weather changes to {weather}...")

        # Show atmosphere
        show_atmosphere(time_of_day, weather)
        
        # Show main menu
        show_main_menu(gold, len(cart), days_passed, german_arrival_day, len(completed_quests))
        
        # Random events
        if random.random() < 0.1:
            event = random.choice(RANDOM_EVENTS)
            print(f"\n--- RANDOM EVENT ---")
            print(f"{event['event']}")
            gold += event['gold']
            print(f"You gained {event['gold']} gold!")
            input("Press Enter to continue...")
            
        # Get main menu choice
        main_choice = get_valid_input("Choose an option: ", ['i', 's', 'b', 'r', 'save', 'q'])
        
        if main_choice == 'q':
            save_choice = get_valid_input(f"Save before quitting? (y/n): ", ['y', 'n'])
            if save_choice == 'y':
                handle_save_menu(save_manager, player_name, gold, cart, completed_quests, 
                        days_passed, time_of_day, weather, german_arrival_day, start_time)
                print(f"Thanks for playing, Sir {player_name}!")
            game_ended = True
            
        elif main_choice == 'save':
            handle_save_menu(save_manager, player_name, gold, cart, completed_quests, 
                            days_passed, time_of_day, weather, german_arrival_day, start_time)

            
        elif main_choice == 'i':
            show_inventory(gold, cart, completed_quests)
            
        elif main_choice == 'r':
            if days_passed >= 3:
                raid_result = handle_german_raid(cart, player_name)
                if raid_result == 'victory':
                    german_arrival_day += 2
                    print("Your successful raid has delayed the German attack by 2 days!")
                elif raid_result == 'death':
                    death_handled = handle_death_alternatives(cart, player_name)
                    if not death_handled:
                        game_ended = True
                        break
                days_passed += 1
            else:
                print("You need more preparation before attempting a raid! (Available after day 3)")
                input("Press Enter to continue...")
                
        elif main_choice == 'b':
            # Check battle ready
            battle_items = ['brian', 'black knight', 'grim reaper', 'god', 'mage', 'nordic', 'biccus diccus', 'raddragonore']
            battle_ready = any(item in cart for item in battle_items)
            
            if battle_ready:
                print("You decide to face the Germanic threat head-on!")
                game_ended = handle_final_battle(cart, player_name, completed_quests, days_passed)
            else:
                print("You need allies or powerful weapons before you can battle the Germans!")
                print("Visit the Freelancers Guild or Antique Shop to prepare.")
                input("Press Enter to continue...")
                
        elif main_choice == 's':
            # Shop selection
            shop_result = handle_shop_selection(gold, cart, completed_quests, player_name)
            gold = shop_result['gold']
            cart = shop_result['cart'] 
            completed_quests = shop_result['completed_quests']
            if shop_result['game_ended']:
                game_ended = True
                break
            
            # Advance time after shopping
            time_of_day = advance_time(time_of_day)
            if time_of_day == "morning":
                days_passed += 1

if __name__ == "__main__":
    main()