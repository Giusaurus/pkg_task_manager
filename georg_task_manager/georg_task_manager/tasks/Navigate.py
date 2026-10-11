# Navigate.py
from .base import BaseTask
from .timeout_watcher import wait_for_action_result
from .priority import TaskPriority
from geometry_msgs.msg import Point
from georg_nav_msgs.action import Navigate as NavigateAction, DriveRoute

from navigate_server import grid_rasterizer


class Navigate(BaseTask):
    # Navigates to a named object's position in the map YAML (e.g. a
    # charging station or a specific seat)
    

    # How far (meters) to stop short of the object's exact point, so the
    # robot doesnt plan a path that ends centered on/inside

    DEFAULT_STANDOFF_M = 0.3
    DEFAULT_MAX_REPLAN_ATTEMPTS = 4
    DEFAULT_OBSTACLE_RADIUS_M = 0.30

    def __init__(self, object_name: str, map_path: str, standoff_m: float = DEFAULT_STANDOFF_M,
                 priority: TaskPriority = TaskPriority.LOW,
                 max_replan_attempts: int = DEFAULT_MAX_REPLAN_ATTEMPTS,
                 obstacle_radius_m: float = DEFAULT_OBSTACLE_RADIUS_M):
        super().__init__("NavigateObject", priority)
        self.object_name = object_name
        self.map_path = map_path
        self.standoff_m = standoff_m
        self.max_replan_attempts = max_replan_attempts
        self.obstacle_radius_m = obstacle_radius_m

    async def run(self, robot, state):

        print(f"[TASK] NavigateObject started -> '{self.object_name}'")

        target = grid_rasterizer.load_named_object_position(self.map_path, self.object_name)
        if target is None:
            print(f"[TASK] NavigateObject FAILED: '{self.object_name}' not found in map")
            return False

        if not hasattr(state, "extra_obstacles"):
            state.extra_obstacles = []
        extra_obstacles = state.extra_obstacles
        
        state.is_navigating = True

        try:
            for attempt in range(self.max_replan_attempts + 1):

                start = getattr(state, "current_position", None)
                if start is None:
                    print("[TASK] NavigateObject FAILED: no current position available")
                    return False

                goal_point = self._apply_standoff(start, target, self.standoff_m)

                goal_msg = NavigateAction.Goal()
                goal_msg.start = Point(x=start[0], y=start[1], z=0.0)
                goal_msg.goal = Point(x=goal_point[0], y=goal_point[1], z=0.0)
                goal_msg.map_name = self.map_path
                goal_msg.simplify_path = True
                goal_msg.extra_obstacles = extra_obstacles
                goal_msg.obstacle_radius_m = self.obstacle_radius_m

                result = await wait_for_action_result(
                    robot.navigate_action_client,
                    goal_msg,
                    timeout=120.0,
                    abort_check=lambda: getattr(state, "abort_requested", False),
                )

                if result is None:
                    print("[TASK] NavigateObject REJECTED/TIMEOUT/ABORTED")
                    return False

                if result.result_code != NavigateAction.Result.RESULT_OK:
                    print(f"[TASK] NavigateObject FAILED (result_code={result.result_code})")
                    return False

                print(
                    f"[TASK] NavigateObject planned successfully: "
                    f"{len(result.waypoints)} waypoints, {result.path_length_m:.2f} m"
                )

                print("[TASK] waypoints:", [(round(w.x, 2), round(w.y, 2)) for w in result.waypoints])



                drive_goal = DriveRoute.Goal()
                drive_goal.waypoints = result.waypoints
                drive_goal.map_name = self.map_path

                drive_result = await wait_for_action_result(
                    robot.drive_route_action_client,
                    drive_goal,
                    timeout=120.0,
                    abort_check=lambda: getattr(state, "abort_requested", False),
                )

                if drive_result is None:
                    print("[TASK] Navigate REJECTED/TIMEOUT/ABORTED during drive")
                    return False

                if drive_result.result_code == DriveRoute.Result.RESULT_OK:
                    print(f"[TASK] Navigate finished successfully -> '{self.object_name}'")
                    state.extra_obstacles = []
                    return True

                if drive_result.result_code == DriveRoute.Result.RESULT_OBSTACLE_DETECTED:
                    bp = drive_result.blocked_position
                    print(f"[TASK] Navigate obstacle at ({bp.x:.2f}, {bp.y:.2f})")

                    if attempt >= self.max_replan_attempts:
                        print("[TASK] Navigate FAILED: replan attempts exhausted")
                        return False

                    pts = list(drive_result.blocked_points)
                    extra_obstacles.extend(pts if pts else [bp])
                    print(f"[TASK] Navigate replanning "
                          f"(attempt {attempt + 1}/{self.max_replan_attempts})")
                    continue

                print(f"[TASK] Navigate FAILED during drive (result_code={drive_result.result_code})")
                return False

            return False

        finally:
            state.is_navigating = False

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