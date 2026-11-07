import os

from georg_task_manager.tasks.ReturnToIdle import ReturnToIdle
from georg_task_manager.tasks.Navigate import Navigate
from georg_task_manager.tasks.priority import LOW, MID, HIGH, CRITICAL


MAP_DIR = os.environ.get("GEORG_MAP_DIR", os.path.expanduser("~/georg_maps"))
MAP_PATH = os.path.join(MAP_DIR, "Nav_Test_V3.yaml")

NAV_ATTEMPTS = 2

# Route: Start -> Seat -> Lemonade (Fallback: Water)  -> Seat -> Exit (Fallback: Entrance)
ROUTE = [
    ("Zum Sitzplatz",       ("Seat",)),
    ("Zum Getraenk",        ("Water",)),
    ("Zum Sitzplatz",       ("Seat",)),
    ("Zum Ausgang",         ("Exit", "Start")),
    ("Zur Startposition",   ("Start",)),
]

def succeeded(result):
    return bool(result)


async def navigate_any(run_task, targets):
    # Fallback ueber die Ziele (FOR), je Ziel mehrere Versuche (WHILE)
    for target in targets:
        attempt = 0
        while attempt < NAV_ATTEMPTS:
            attempt += 1
            print(f"[MISSION] Navigate {target}, Versuch {attempt}/{NAV_ATTEMPTS}")
            if succeeded(await run_task(Navigate(target, MAP_PATH, priority=HIGH))):
                return True
        print(f"[MISSION] {target} fehlgeschlagen, naechstes Ziel")
    return False


async def get_mission(robot, state, run_task):
    print("[MISSION] Navigationstest (async) gestartet")

    try:
        for step, (name, targets) in enumerate(ROUTE, start=1):
            print(f"[MISSION] Teilstrecke {step}: {name}")
            if not await navigate_any(run_task, targets):
                print(f"[MISSION] Teilstrecke {step} fehlgeschlagen")
                return
        print("[MISSION] Navigationstest erfolgreich")

    finally:
        await run_task(ReturnToIdle())