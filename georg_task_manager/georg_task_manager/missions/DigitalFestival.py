from georg_task_manager.tasks.Listening import Listening
from georg_task_manager.tasks.Gesture import Gesture
from georg_task_manager.tasks.ReturnToIdle import ReturnToIdle
from georg_task_manager.tasks.Navigate import Navigate
from georg_task_manager.tasks.Navigate import DriveRoute
from georg_task_manager.tasks.GraspPlanning import GraspPlanning
from georg_task_manager.tasks.priority import LOW, MID, HIGH, CRITICAL


MAP_PATH = "/home/giu/georg_maps/Nav_Test.yaml"

# Parameters:
# Listening: ("SPEECH") = Speech detection
#            ("DOORBELL") = Doorbell detection
# Gesture:   ("Movement", camera_vector_x, camera_vector_y, camera_vector_z)
#            Movements: greet_person, point_to, look_at


async def get_mission(robot, state, run_task):
    print("[MISSION] Bar started")

    await run_task(Listening("DOORBELL", timeout_sec=60.0, priority=MID))
    await run_task(Gesture("look_at", -1000.0, 0.0, 100.0))
    await run_task(Gesture("point_to", -2000.0, 0.0, 100.0))
    await run_task(Navigate("Seat", MAP_PATH, priority= HIGH))
    await run_task(GraspPlanning("cup", (0.4, -0.1, 0.8), 0.45, priority=HIGH))
    await run_task(Listening("SPEECH"))
    await run_task(Gesture("look_at", -1000.0, 0.0, 100.0))
    await run_task(Gesture("greet_person", -1000.0, 0.0, 100.0))
    await run_task(Navigate("Door", MAP_PATH))
    await run_task(ReturnToIdle())
