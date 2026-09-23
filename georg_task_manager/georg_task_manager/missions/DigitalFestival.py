from georg_task_manager.tasks.Listening import Listening
from georg_task_manager.tasks.Gesture import Gesture
from georg_task_manager.tasks.ReturnToIdle import ReturnToIdle
from georg_task_manager.tasks.NavigateObject import NavigateObject
from georg_task_manager.tasks.NavigateObject import DriveRoute
from georg_task_manager.tasks.priority import LOW, MID, HIGH, CRITICAL



# Parameters:

# Listening: ("SPEECH") = Speech detection
#            ("DOORBELL") = Doorbell detection

# Gesture:   ("Movement", camera_vector_x, camera_vector_y, camera_vector_z)
#            Movements: greet_person, point_to, look_at 

def get_mission():

    print("[MISSION] Bar started")

    return [

        Listening("DOORBELL", HIGH),
        Gesture("look_at", -1000.0, 0.0, 100.0),
        Gesture("point_to", -2000.0, 0.0, 100.0),
        #NavigateObject("front_door", "/home/giuseppe/georg_maps/arena.yaml"),
        Listening("SPEECH"),
        Gesture("look_at", -1000.0, 0.0, 100.0),
        Gesture("greet_person", -1000.0, 0.0, 100.0),
        #NavigateObject("charging_station", "/home/giuseppe/georg_maps/arena.yaml"),
        ReturnToIdle()

    ]