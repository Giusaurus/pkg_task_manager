import os
import py_trees
from py_trees.common import Status

from georg_task_manager.tasks_bt import Navigate_BT, ReturnToIdle_BT
from georg_task_manager.tasks.priority import LOW, MID, HIGH, CRITICAL

MAP_DIR = os.environ.get("GEORG_MAP_DIR", os.path.expanduser("~/georg_maps"))
MAP_PATH = os.path.join(MAP_DIR, "Nav_Test_V3.yaml")

NAV_ATTEMPTS = 2

# Route: Start -> Seat -> Lemonade (Fallback: Water) -> Seat -> Exit (Fallback: Start) -> Start
ROUTE = [
    ("Zum Sitzplatz",       ("Seat",)),
    ("Zum Getraenk",        ("Water",)),
    ("Zum Sitzplatz",       ("Seat",)),
    ("Zum Ausgang",         ("Exit", "Start")),
    ("Zur Startposition",   ("Start",)),
]


class Log(py_trees.behaviour.Behaviour):

    def __init__(self, message):
        super().__init__(name="Log")
        self.message = message

    def update(self):
        print(self.message)
        return Status.SUCCESS


class LogAttempt(py_trees.behaviour.Behaviour):

    def __init__(self, target):
        super().__init__(name=f"Versuch {target}")
        self.target = target
        self.attempt = 0

    def update(self):
        self.attempt += 1
        print(f"[MISSION] Navigate {self.target}, Versuch {self.attempt}/{NAV_ATTEMPTS}")
        return Status.SUCCESS


class LogResult(py_trees.decorators.Decorator):


    def update(self):
        status = self.decorated.status
        if status == Status.SUCCESS:
            print("[TASK RESULT] True\n")
        elif status == Status.FAILURE:
            print("[TASK RESULT] False\n")
        return status


def ComparisonNavBT(robot, state):

    def nav_attempt(target):

        attempt = py_trees.composites.Sequence(name=f"Navigate {target}", memory=True)
        attempt.add_children([
            LogAttempt(target),
            LogResult(
                name=f"Result {target}",
                child=Navigate_BT.build(robot, state, target, MAP_PATH, priority=HIGH),
            ),
        ])
        return attempt

    def nav_fallback(name, targets):

        selector = py_trees.composites.Selector(name=name, memory=True)
        selector.add_children([
            py_trees.decorators.Retry(
                name=f"{target} ({NAV_ATTEMPTS}x)",
                child=nav_attempt(target),
                num_failures=NAV_ATTEMPTS,
            )
            for target in targets
        ])
        return selector

    def leg(step, name, targets):

        seq = py_trees.composites.Sequence(name=f"{step}) {name}", memory=True)
        seq.add_children([
            Log(f"[MISSION] Teilstrecke {step}: {name}"),
            nav_fallback(f"{name} (Fallback)", targets),
        ])
        return seq

    mission = py_trees.composites.Sequence(name="Navigationstest", memory=True)
    mission.add_children(
        [Log("[MISSION] Navigationstest (BT) gestartet")]
        + [leg(step, name, targets) for step, (name, targets) in enumerate(ROUTE, start=1)]
        + [Log("[MISSION] Navigationstest erfolgreich")]
    )

    root = py_trees.composites.Sequence(name="Navigationstest (BT)", memory=True)
    root.add_children([
        py_trees.decorators.FailureIsSuccess(name="Mission (Fehler egal)", child=mission),
        ReturnToIdle_BT.build(robot, state),
    ])
    return root