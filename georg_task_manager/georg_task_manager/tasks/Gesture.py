# greet_guest.py
from .base import BaseTask
from .timeout_watcher import wait_for_action_result
from .priority import TaskPriority
from geometry_msgs.msg import Vector3
from pib_gestures_action.action import PibGesturesInterface


class Gesture(BaseTask):

    def __init__(self, mode: str, vx:float, vy:float, vz:float, priority: TaskPriority = TaskPriority.LOW):
        super().__init__("Gesture", priority)
        self.mode = mode
        self.vx = vx
        self.vy = vy
        self.vz = vz
        

    async def run(self, robot, state):

        print(f"[TASK] Gesture {self.mode}: Started")

        goal_msg = PibGesturesInterface.Goal()
        goal_msg.gesture = self.mode
        goal_msg.camera_vector = Vector3(x=self.vx, y=self.vy, z=self.vz)
        goal_msg.pib_side = "right"
        goal_msg.pib_gesture = "wave"
        goal_msg.pib_hand = "open_hand"  

        state.is_greeting_guest = True

        result = await wait_for_action_result(
            robot.greet_action_client,
            goal_msg,
            timeout=15.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )

        state.is_greeting_guest = False

        if result is None:
            print(f"[TASK] Gesture {self.mode}: REJECTED/TIMEOUT/ABORTED")
            return False

        if result.success != 0:
            print(f"[TASK] Gesture {self.mode}: FAILED")
            return False

        print(f"[TASK] Gesture {self.mode}: Finished successfully")
        return True