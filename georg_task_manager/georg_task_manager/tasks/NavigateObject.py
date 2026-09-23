# NavigateObject.py
from .base import BaseTask
from .timeout_watcher import wait_for_action_result
from .priority import TaskPriority
from geometry_msgs.msg import Point
from georg_nav_msgs.action import Navigate, DriveRoute

from navigate_server import grid_rasterizer


class NavigateObject(BaseTask):
    # Navigates to a named object's position in the map YAML (e.g. a
    # charging station or a specific seat), as distinct from NavigateRoom.
    

    # How far (meters) to stop short of the object's exact point, so the
    # robot doesnt plan a path that ends centered on/inside

    DEFAULT_STANDOFF_M = 0.3

    def __init__(self,  object_name: str, map_path: str, standoff_m: float = DEFAULT_STANDOFF_M, priority: TaskPriority = TaskPriority.LOW):
        super().__init__("NavigateObject", priority)
        self.object_name = object_name
        self.map_path = map_path
        self.standoff_m = standoff_m

    async def run(self, robot, state):

        print(f"[TASK] NavigateObject started -> '{self.object_name}'")

        target = grid_rasterizer.load_named_object_position(self.map_path, self.object_name)
        if target is None:
            print(f"[TASK] NavigateObject FAILED: '{self.object_name}' not found in map")
            return False

        start = getattr(state, "current_position", None)
        if start is None:
            print("[TASK] NavigateObject FAILED: no current position available")
            return False

        goal_point = self._apply_standoff(start, target, self.standoff_m)

        goal_msg = Navigate.Goal()
        goal_msg.start = Point(x=start[0], y=start[1], z=0.0)
        goal_msg.goal = Point(x=goal_point[0], y=goal_point[1], z=0.0)
        goal_msg.map_name = self.map_path
        goal_msg.simplify_path = True

        state.is_navigating = True

        result = await wait_for_action_result(
            robot.navigate_object_action_client,
            goal_msg,
            timeout=120.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )

        if result is None:
            state.is_navigating = False
            print("[TASK] NavigateObject REJECTED/TIMEOUT/ABORTED")
            return False

        if result.result_code != Navigate.Result.RESULT_OK:
            state.is_navigating = False
            print(f"[TASK] NavigateObject FAILED (result_code={result.result_code})")
            return False

        print(
            f"[TASK] NavigateObject planned successfully: "
            f"{len(result.waypoints)} waypoints, {result.path_length_m:.2f} m"
        )

        drive_goal = DriveRoute.Goal()
        drive_goal.waypoints = result.waypoints

        drive_result = await wait_for_action_result(
            robot.drive_route_action_client,
            drive_goal,
            timeout=120.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )

        state.is_navigating = False

        if drive_result is None:
            print("[TASK] NavigateObject REJECTED/TIMEOUT/ABORTED during drive")
            return False

        if drive_result.result_code != DriveRoute.Result.RESULT_OK:
            print(f"[TASK] NavigateObject FAILED during drive (result_code={drive_result.result_code})")
            return False

        print(f"[TASK] NavigateObject finished successfully -> '{self.object_name}'")
        return True

    @staticmethod
    def _apply_standoff(start, target, standoff_m):
        # moves goal point, so that the robot doesnt move into it
        
        if standoff_m <= 0:
            return target

        dx = target[0] - start[0]
        dy = target[1] - start[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist <= standoff_m:
            return start  # if already within standoff distance, dont move

        ratio = (dist - standoff_m) / dist
        return (start[0] + dx * ratio, start[1] + dy * ratio)