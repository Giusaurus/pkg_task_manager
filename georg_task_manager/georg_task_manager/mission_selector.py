from georg_task_manager.missions.DigitalFestival import get_mission as DigitalFestival
from georg_task_manager.missions.Test_Mapping import get_mission as TestMapping
from georg_task_manager.missions.Comparison import get_mission as Comparison
from georg_task_manager.missions.ComparisonNav import get_mission as ComparisonNav
import os

def select_mission():
    mission_id = os.environ.get("MISSION_ID")

    # starts mission with docker over MISSION_ID (specified in Dockerfile)
    if mission_id is not None:

        if mission_id == "1":
            return DigitalFestival


        elif mission_id == "2":
            return TestMapping


        elif mission_id == "3":
            return Comparison


        elif mission_id == "4":
            return ComparisonNav

        print(f"\nInvalid MISSION_ID: {mission_id}\n")
        return None

    # starts mission with input in terminal
    
    print("\n==================================")
    print("         TASK MANAGER")
    print("==================================")
    print("1 - Digital Festival")
    print("2 - Mapping Test")
    print("3 - Comparison")
    print("4 - ComparisonNav")
    print("0 - Exit")

    choice = input("\nSelect Mission: ")

    if choice == "1":
        return DigitalFestival
    

    elif choice == "2":
        return TestMapping
    

    elif choice == "3":
        return Comparison
    

    elif choice == "4":
        return ComparisonNav
    

    elif choice == "0":
        return None

    print("\nInvalid selection.\n")
    return None