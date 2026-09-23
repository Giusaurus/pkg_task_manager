from georg_task_manager.missions.DigitalFestival import get_mission as DigitalFestival
from georg_task_manager.missions.Test_Mapping import get_mission as TestMapping


def select_mission():

    while True:

        print("\n==================================")
        print("         TASK MANAGER")
        print("==================================")
        print("1 - Digital Festival")
        print("2 - Mapping Test")
        print("0 - Exit")

        choice = input("\nSelect Mission: ")

        if choice == "1":
            return DigitalFestival()
        
        if choice == "2":
            return TestMapping()


        elif choice == "0":
            return None

        print("\nInvalid selection.\n")