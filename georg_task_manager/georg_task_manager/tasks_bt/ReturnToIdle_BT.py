import py_trees
from py_trees.common import Status

from georg_task_manager.bt.bt_common import TaskLabel


class ReturnToIdleLeaf(py_trees.behaviour.Behaviour):

    def __init__(self, state):
        super().__init__("ReturnToIdle")
        self.state = state

    def update(self):
        s = self.state
        s.is_listening = False
        s.listening_for = ""
        s.is_greeting_guest = False
        s.is_navigating = False
        s.navigating_to = ""
        s.current_task = "Idle"
        print("[TASK] ReturnToIdle finished")
        return Status.SUCCESS


def build(robot, state):
    return py_trees.composites.Sequence(name="ReturnToIdle", memory=True, children=[
        TaskLabel("ReturnToIdle", robot, state),
        ReturnToIdleLeaf(state),
    ])