from georg_task_manager.missions.DigitalFestival import get_mission as DigitalFestival
from georg_task_manager.missions.Test_Mapping import get_mission as TestMapping
import os

def select_mission():
    mission_id = os.environ.get("MISSION_ID")

    # Start mit Docker über Mission ID (festgelegt in Dockerfile)
    if mission_id is not None:

        if mission_id == "1":
            return DigitalFestival

        elif mission_id == "2":
            return TestMapping

        print(f"\nInvalid MISSION_ID: {mission_id}\n")
        return None

    # Start über Terminal
    print("\n==================================")
    print("         TASK MANAGER")
    print("==================================")
    print("1 - Digital Festival")
    print("2 - Mapping Test")
    print("0 - Exit")

    choice = input("\nSelect Mission: ")

    if choice == "1":
        return DigitalFestival

    elif choice == "2":
        return TestMapping

    elif choice == "0":
        return None

    print("\nInvalid selection.\n")
    return None