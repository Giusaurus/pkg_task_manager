import os


from georg_task_manager.bt.missions.Test_Mapping_BT import TestMapping as TestMapping
from georg_task_manager.bt.missions.Comparison_BT import ComparisonBT as ComparisonBT
from georg_task_manager.bt.missions.ComparisonNav_BT import ComparisonNavBT as ComparisonNavBT


def select_mission():

    # starts mission with docker over MISSION_ID (specified in Dockerfile)
    mission_id = os.environ.get("MISSION_ID")

    if mission_id is not None:

        if mission_id == "1":
            return TestMapping


        if mission_id == "2":
            return ComparisonBT


        if mission_id == "3":
            return ComparisonNavBT

        
        print(f"\nInvalid MISSION_ID: {mission_id}\n")
        return None


    # starts mission with input in terminal

    print("\n==================================")
    print("       TASK MANAGER (BT)")
    print("==================================")

    print("1 - Mapping Test")
    print("2 - ComparisonBT")
    print("3 - ComparisonNavBT")        
    print("0 - Exit")

    choice = input("\nSelect Mission: ")


    if choice == "1":
        return TestMapping
    
    if choice == "2":
        return ComparisonBT

    if choice == "3":
        return ComparisonNavBT    

    elif choice == "0":
        return None    
    
    return None