import py_trees
from py_trees.common import Status
from geometry_msgs.msg import Vector3
from pib_gestures_action.action import PibGesturesInterface

from georg_task_manager.bt.bt_common import ActionLeaf, TaskLabel, with_priority
from georg_task_manager.tasks.priority import LOW


class GestureLeaf(ActionLeaf):

    def __init__(self, robot, state, mode, vx, vy, vz):
        super().__init__(f"Gesture {mode}", robot.greet_action_client, robot, state, timeout=15.0)
        self.mode, self.vx, self.vy, self.vz = mode, vx, vy, vz

    def make_goal(self):
        goal = PibGesturesInterface.Goal()
        goal.gesture = self.mode
        goal.camera_vector = Vector3(x=self.vx, y=self.vy, z=self.vz)
        goal.pib_side = "right"
        goal.pib_gesture = "wave"
        goal.pib_hand = "open_hand"
        return goal

    def on_start(self):
        print(f"[TASK] Gesture {self.mode}: Started")
        self.state.is_greeting_guest = True

    def on_end(self):
        self.state.is_greeting_guest = False

    def on_result(self, status, result):
        if result.success != 0:
            print(f"[TASK] Gesture {self.mode}: FAILED")
            return Status.FAILURE
        print(f"[TASK] Gesture {self.mode}: Finished successfully")
        return Status.SUCCESS


def build(robot, state, mode, vx, vy, vz, priority=LOW):
    name = f"Gesture {mode}"
    seq = py_trees.composites.Sequence(name=name, memory=True, children=[
        TaskLabel("Gesture", robot, state),
        GestureLeaf(robot, state, mode, vx, vy, vz),
    ])
    return with_priority(seq, priority)