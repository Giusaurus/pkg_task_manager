# NavigateRoom.py
from .base import BaseTask
from .timeout_watcher import wait_for_action_result
from .priority import TaskPriority
from geometry_msgs.msg import Point
from georg_nav_msgs.action import Navigate, DriveRoute

from navigate_server import grid_rasterizer


def _get_current_position(robot, state):
    #Returns (x, y) world-space current position, or None if no
    #pose source is wired up yet."""

    return None


class NavigateRoom(BaseTask):


    def __init__(self, room_name: str, map_path: str, priority: TaskPriority = TaskPriority.LOW):
        super().__init__("NavigateRoom", priority)
        self.room_name = room_name
        self.map_path = map_path

    async def run(self, robot, state):

        print(f"[TASK] NavigateRoom started -> '{self.room_name}'")

        target = grid_rasterizer.load_named_object_position(self.map_path, self.room_name)
        if target is None:
            print(f"[TASK] NavigateRoom FAILED: '{self.room_name}' not found in map")
            return False

        start = _get_current_position(robot, state)
        if start is None:
            print(
                "[TASK] NavigateRoom FAILED: no current-position source "
                "wired up yet (see TODO(localization) in this file)"
            )
            return False

        goal_msg = Navigate.Goal()
        goal_msg.start = Point(x=start[0], y=start[1], z=0.0)
        goal_msg.goal = Point(x=target[0], y=target[1], z=0.0)
        goal_msg.map_name = self.map_path
        goal_msg.simplify_path = True

        state.moving_to_door = True

        result = await wait_for_action_result(
            robot.navigate_room_action_client,
            goal_msg,
            timeout=120.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )

        if result is None:
            state.moving_to_door = False
            print("[TASK] NavigateRoom REJECTED/TIMEOUT/ABORTED")
            return False

        if result.result_code != Navigate.Result.RESULT_OK:
            state.moving_to_door = False
            print(f"[TASK] NavigateRoom FAILED (result_code={result.result_code})")
            return False

        print(
            f"[TASK] NavigateRoom planned successfully: "
            f"{len(result.waypoints)} waypoints, {result.path_length_m:.2f} m"
        )

        # Hand the plan off to DriveRoute for execution.
        drive_goal = DriveRoute.Goal()
        drive_goal.waypoints = result.waypoints

        drive_result = await wait_for_action_result(
            robot.drive_route_action_client,
            drive_goal,
            timeout=120.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )

        state.moving_to_door = False

        if drive_result is None:
            print("[TASK] NavigateRoom REJECTED/TIMEOUT/ABORTED during drive")
            return False

        if drive_result.result_code != DriveRoute.Result.RESULT_OK:
            print(f"[TASK] NavigateRoom FAILED during drive (result_code={drive_result.result_code})")
            return False

        state.reached_door = True
        print(f"[TASK] NavigateRoom finished successfully -> '{self.room_name}'")
        return True