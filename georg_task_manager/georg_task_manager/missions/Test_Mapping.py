import os

from georg_task_manager.tasks.Listening import Listening
from georg_task_manager.tasks.Gesture import Gesture
from georg_task_manager.tasks.ReturnToIdle import ReturnToIdle
from georg_task_manager.tasks.Navigate import Navigate
from georg_task_manager.tasks.Navigate import DriveRoute
from georg_task_manager.tasks.priority import LOW, MID, HIGH, CRITICAL


MAP_DIR = os.environ.get("GEORG_MAP_DIR", os.path.expanduser("~/georg_maps"))
MAP_PATH = os.path.join(MAP_DIR, "Nav_Test_V3.yaml")


async def get_mission(robot, state, run_task):
    print("[MISSION] Test Mapping started")

    #await run_task(Listening("DOORBELL", timeout_sec=60.0, priority=HIGH))
    #await run_task(Gesture("look_at", -1000.0, 0.0, 100.0))
    #await run_task(Gesture("point_to", -2000.0, 0.0, 100.0))
    await run_task(Navigate("Seat", MAP_PATH, priority= HIGH))
    #await run_task(Navigate("Sink", MAP_PATH))
    #await run_task(Listening("SPEECH"))
    #await run_task(Gesture("look_at", -1000.0, 0.0, 100.0))
    #await run_task(Gesture("greet_person", -1000.0, 0.0, 100.0))
    #await run_task(Navigate("Water", MAP_PATH,priority= HIGH))
    #await run_task(Navigate("Exit", MAP_PATH,priority= HIGH))
    #await run_task(Navigate("Entrance", MAP_PATH,priority= HIGH))
    await run_task(ReturnToIdle())