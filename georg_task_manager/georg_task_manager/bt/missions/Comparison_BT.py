import py_trees
from py_trees.common import ParallelPolicy

from georg_task_manager.tasks_bt import Listening_BT, Gesture_BT, Navigate_BT, ReturnToIdle_BT
from georg_task_manager.tasks.priority import LOW, MID, HIGH, CRITICAL

MAP_PATH = "/home/giu/georg_maps/Nav_Test_V3.yaml"
NAV_ATTEMPTS = 2
TABLE_TARGETS = ("Seat", "Water")
EXIT_TARGETS = ("Exit", "Entrance")


def ComparisonBT(robot, state):

    def nav_fallback(name, targets):
        # FALLBACK ueber die Ziele, je Ziel NAV_ATTEMPTS Versuche (Retry)
        selector = py_trees.composites.Selector(name=name, memory=True)
        selector.add_children([
            py_trees.decorators.Retry(
                name=f"{target} ({NAV_ATTEMPTS}x)",
                child=Navigate_BT.build(robot, state, target, MAP_PATH, priority=HIGH),
                num_failures=NAV_ATTEMPTS,
            )
            for target in targets
        ])
        return selector

    # 1) PARALLEL: Klingel abwarten und gleichzeitig zur Tuer schauen
    wait_for_guest = py_trees.composites.Parallel(
        name="Warten auf Gast",
        policy=ParallelPolicy.SuccessOnAll(synchronise=True),
    )
    wait_for_guest.add_children([
        Listening_BT.build(robot, state, "DOORBELL", timeout_sec=60.0, priority=MID),
        Gesture_BT.build(robot, state, "look_at", -1000.0, 0.0, 100.0),
    ])

    mission = py_trees.composites.Sequence(name="Gast empfangen", memory=True)
    mission.add_children([
        wait_for_guest,
        Gesture_BT.build(robot, state, "point_to", -2000.0, 0.0, 100.0),          # 2)
        nav_fallback("Zum Tisch (Fallback)", TABLE_TARGETS),                      # 3)
        Listening_BT.build(robot, state, "SPEECH"),                               # 4)
        Gesture_BT.build(robot, state, "look_at", -1000.0, 0.0, 100.0),
        Gesture_BT.build(robot, state, "greet_person", -1000.0, 0.0, 100.0),
        nav_fallback("Ausgang (Fallback)", EXIT_TARGETS),                         # 5)
    ])

    # 6) Egal ob die Mission klappt: danach immer ReturnToIdle
    root = py_trees.composites.Sequence(name="Test Mapping", memory=True)
    root.add_children([
        py_trees.decorators.FailureIsSuccess(name="Mission (Fehler egal)", child=mission),
        ReturnToIdle_BT.build(robot, state),
    ])
    return root