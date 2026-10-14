import os

from georg_task_manager.bt.missions.Test_Mapping_BT import get_mission_bt as TestMapping
# from georg_task_manager.bt.missions.DigitalFestival_BT import get_mission_bt as DigitalFestival


def select_mission():
    mission_id = os.environ.get("MISSION_ID")

    if mission_id is not None:
        if mission_id == "2":
            return TestMapping
        print(f"\nInvalid MISSION_ID: {mission_id}\n")
        return None

    print("\n==================================")
    print("       TASK MANAGER (BT)")
    print("==================================")
    print("2 - Mapping Test")
    print("0 - Exit")

    choice = input("\nSelect Mission: ")
    if choice == "2":
        return TestMapping
    return None