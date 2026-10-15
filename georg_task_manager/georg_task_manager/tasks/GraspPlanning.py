# GraspPlanning.py

from .base import BaseTask
from .timeout_watcher import wait_for_action_result
from .priority import TaskPriority
from geometry_msgs.msg import Point
from grasp_planning.action import GraspPlanning as GraspPlanningAction


class GraspPlanning(BaseTask):


    GOAL_CONTENT = "goal_content"   
    DEFAULT_SCRIPT_PATH = "/home/athome/DRO-Gym/validate.py"
    MAX_REACH_M = 0.6
    SUPPORTED_HANDS = ("pib_r",)   
    DEFAULT_TIMEOUT_S = 600.0

    def __init__(self, object_name: str, object_coordinates, object_distance: float,
                 which_hand: str = None,
                 script_path: str = DEFAULT_SCRIPT_PATH,
                 timeout_sec: float = DEFAULT_TIMEOUT_S,
                 priority: TaskPriority = TaskPriority.LOW):
        super().__init__("GraspPlanning", priority)
        self.object_name = object_name
        self.object_coordinates = object_coordinates  
        self.object_distance = object_distance
        self.which_hand = which_hand                  
        self.script_path = script_path
        self.timeout_sec = timeout_sec

    async def run(self, robot, state):
        print(f"[TASK] GraspPlanning started -> '{self.object_name}'")

        hand = self.which_hand or self.choose_hand(self.object_coordinates[1])
        error = self.validate(hand, self.object_distance)
        if error:
            print(f"[TASK] GraspPlanning FAILED: {error}")
            return False

        goal_msg = self.make_goal(self.object_name, self.object_coordinates,
                                  self.object_distance, hand, self.script_path)

        result = await wait_for_action_result(
            robot.grasp_planning_action_client,
            goal_msg,
            timeout=self.timeout_sec,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )

        if result is None:
            print("[TASK] GraspPlanning REJECTED/TIMEOUT/ABORTED")
            return False

        print(f"[TASK] GraspPlanning result: {result.result_content}")
        if not self.is_success(result):
            print("[TASK] GraspPlanning FAILED")
            return False

        state.grasp_result = result.result_content
        print(f"[TASK] GraspPlanning finished successfully -> '{self.object_name}'")
        return True


    @staticmethod
    def choose_hand(y):
        return "pib_l" if y < 0 else "pib_r"

    @classmethod
    def validate(cls, hand, distance):
        if distance < 0 or distance > cls.MAX_REACH_M:
            return f"Objekt ausser Reichweite ({distance:.2f} m)"
        if hand not in cls.SUPPORTED_HANDS:
            return f"Hand '{hand}' wird vom Greifmodell noch nicht unterstuetzt"
        return None

    @classmethod
    def make_goal(cls, object_name, coords, distance, hand, script_path):
        goal = GraspPlanningAction.Goal()
        goal.goal_content = cls.GOAL_CONTENT
        goal.script_path = script_path
        goal.object_name = object_name
        goal.object_coordinates = Point(x=float(coords[0]), y=float(coords[1]), z=float(coords[2]))
        goal.object_distance = float(distance)
        goal.which_hand = hand
        return goal

    @staticmethod
    def is_success(result):
        return result.result_content.startswith("success")