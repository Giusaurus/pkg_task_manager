import os

import asyncio
from georg_task_manager.tasks.Listening import Listening
from georg_task_manager.tasks.Gesture import Gesture
from georg_task_manager.tasks.ReturnToIdle import ReturnToIdle
from georg_task_manager.tasks.Navigate import Navigate
from georg_task_manager.tasks.Navigate import DriveRoute
from georg_task_manager.tasks.priority import LOW, MID, HIGH, CRITICAL


MAP_DIR = os.environ.get("GEORG_MAP_DIR", os.path.expanduser("~/georg_maps"))
MAP_PATH = os.path.join(MAP_DIR, "Nav_Test_V3.yaml")

NAV_ATTEMPTS = 2
TABLE_TARGETS = ("Seat", "Water")
EXIT_TARGETS = ("Exit", "Entrance")


def succeeded(result):

    return bool(result)


async def navigate_any(run_task, targets):

    for target in targets:
        attempt = 0
        while attempt < NAV_ATTEMPTS:
            attempt += 1
            print(f"[MISSION] Navigate {target}, Try {attempt}/{NAV_ATTEMPTS}")
            if succeeded(await run_task(Navigate(target, MAP_PATH, priority=HIGH))):
                return True
        print(f"[MISSION] {target} failed, next target")
    return False


async def get_mission(robot, state, run_task):
    print("[MISSION] Guest welcomed (async) started")

    try:

        results = await asyncio.gather(
            run_task(Listening("DOORBELL", timeout_sec=60.0, priority=MID)),
            run_task(Gesture("look_at", -1000.0, 0.0, 100.0)),
        )
        if not all(succeeded(r) for r in results):
            print("[MISSION] Waiting for guest: Error")
            return


        if not succeeded(await run_task(Gesture("point_to", -2000.0, 0.0, 100.0))):
            return


        if not await navigate_any(run_task, TABLE_TARGETS):
            return


        if not succeeded(await run_task(Listening("SPEECH"))):
            return
        if not succeeded(await run_task(Gesture("look_at", -1000.0, 0.0, 100.0))):
            return
        if not succeeded(await run_task(Gesture("greet_person", -1000.0, 0.0, 100.0))):
            return


        if not await navigate_any(run_task, EXIT_TARGETS):
            return

    finally:

        await run_task(ReturnToIdle())