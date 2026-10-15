import py_trees
from py_trees.common import Status

from georg_task_manager.bt.bt_common import ActionLeaf, TaskLabel, with_priority
from georg_task_manager.tasks.GraspPlanning import GraspPlanning as GraspTask
from georg_task_manager.tasks.priority import LOW


class CheckGraspable(py_trees.behaviour.Behaviour):

    def __init__(self, state, object_name, coords, distance, which_hand):
        super().__init__(f"Check '{object_name}'")
        self.state = state
        self.coords = coords
        self.distance = distance
        self.which_hand = which_hand

    def update(self):
        hand = self.which_hand or GraspTask.choose_hand(self.coords[1])
        error = GraspTask.validate(hand, self.distance)
        if error:
            print(f"[TASK] GraspPlanning FAILED: {error}")
            return Status.FAILURE
        self.state.grasp_hand = hand
        return Status.SUCCESS


class GraspLeaf(ActionLeaf):

    def __init__(self, robot, state, object_name, coords, distance, script_path, timeout):
        super().__init__("GraspPlanning", robot.grasp_planning_action_client,
                         robot, state, timeout=timeout)
        self.object_name = object_name
        self.coords = coords
        self.distance = distance
        self.script_path = script_path

    def make_goal(self):
        return GraspTask.make_goal(self.object_name, self.coords, self.distance,
                                   self.state.grasp_hand, self.script_path)

    def on_result(self, status, result):
        print(f"[TASK] GraspPlanning result: {result.result_content}")
        if not GraspTask.is_success(result):
            print("[TASK] GraspPlanning FAILED")
            return Status.FAILURE
        self.state.grasp_result = result.result_content
        print("[TASK] GraspPlanning finished successfully")
        return Status.SUCCESS


def build(robot, state, object_name, object_coordinates, object_distance,
          which_hand=None,
          script_path=GraspTask.DEFAULT_SCRIPT_PATH,
          timeout_sec=GraspTask.DEFAULT_TIMEOUT_S,
          priority=LOW):

    body = py_trees.composites.Sequence(
        name=f"GraspPlanning({object_name})", memory=True, children=[
            TaskLabel("GraspPlanning", robot, state),
            CheckGraspable(state, object_name, object_coordinates, object_distance, which_hand),
            GraspLeaf(robot, state, object_name, object_coordinates, object_distance,
                      script_path, timeout_sec),
        ])
    return with_priority(body, priority)