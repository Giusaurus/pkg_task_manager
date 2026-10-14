import math

import py_trees
from py_trees.common import Status
from geometry_msgs.msg import Point
from georg_nav_msgs.action import Navigate as NavigateAction, DriveRoute
from navigate_server import grid_rasterizer

from georg_task_manager.bt.bt_common import ActionLeaf, TaskLabel, StateFlags, with_priority
from georg_task_manager.tasks.Navigate import Navigate as NavigateTask
from georg_task_manager.tasks.priority import LOW


class ResolveTarget(py_trees.behaviour.Behaviour):

    def __init__(self, state, object_name, map_path):
        super().__init__(f"Resolve '{object_name}'")
        self.state = state
        self.object_name = object_name
        self.map_path = map_path

    def update(self):
        target = grid_rasterizer.load_named_object_position(self.map_path, self.object_name)
        if target is None:
            print(f"[TASK] NavigateObject FAILED: '{self.object_name}' not found in map")
            return Status.FAILURE
        self.state.nav_target = target
        if not hasattr(self.state, "extra_obstacles"):
            self.state.extra_obstacles = []
        self.state.nav_obstacle_hit = False
        return Status.SUCCESS


class PlanLeaf(ActionLeaf):

    def __init__(self, robot, state, map_path, standoff_m, obstacle_radius_m):
        super().__init__("PlanPath", robot.navigate_action_client, robot, state, timeout=120.0)
        self.map_path = map_path
        self.standoff_m = standoff_m
        self.obstacle_radius_m = obstacle_radius_m

    def make_goal(self):

        odom = getattr(self.state, "current_position", None)
        if odom is None:
            print("[TASK] NavigateObject FAILED: no current position available")
            return None
        map_start = grid_rasterizer.load_map_start(self.map_path) or (0.0, 0.0)
        start = (odom[0] + map_start[0], odom[1] + map_start[1])
        
        goal_point = NavigateTask._apply_standoff(start, self.state.nav_target, self.standoff_m)
        goal = NavigateAction.Goal()
        goal.start = Point(x=start[0], y=start[1], z=0.0)
        goal.goal = Point(x=goal_point[0], y=goal_point[1], z=0.0)
        goal.map_name = self.map_path
        goal.simplify_path = True
        goal.extra_obstacles = list(self.state.extra_obstacles)
        goal.obstacle_radius_m = self.obstacle_radius_m
        return goal

    def on_result(self, status, result):
        if result.result_code != NavigateAction.Result.RESULT_OK:
            print(f"[TASK] NavigateObject FAILED (result_code={result.result_code})")
            return Status.FAILURE
        print(f"[TASK] NavigateObject planned successfully: "
              f"{len(result.waypoints)} waypoints, {result.path_length_m:.2f} m")
        self.state.nav_waypoints = list(result.waypoints)
        return Status.SUCCESS


class DriveLeaf(ActionLeaf):

    def __init__(self, robot, state, map_path):
        super().__init__("DriveRoute", robot.drive_route_action_client, robot, state, timeout=120.0)
        self.map_path = map_path

    def make_goal(self):
        wps = self.state.nav_waypoints
        target = self.state.nav_target
        last = wps[-1]
        goal = DriveRoute.Goal()
        goal.waypoints = wps
        goal.map_name = self.map_path
        goal.use_final_yaw = True
        goal.final_yaw = math.atan2(target[1] - last.y, target[0] - last.x)
        return goal

    def on_result(self, status, result):
        if result.result_code == DriveRoute.Result.RESULT_OK:
            print("[TASK] Navigate finished successfully")
            self.state.extra_obstacles = []
            return Status.SUCCESS

        if result.result_code == DriveRoute.Result.RESULT_OBSTACLE_DETECTED:
            bp = result.blocked_position
            print(f"[TASK] Navigate obstacle at ({bp.x:.2f}, {bp.y:.2f})")
            pts = list(result.blocked_points)
            self.state.extra_obstacles.extend(pts if pts else [bp])
            self.state.nav_obstacle_hit = True
            return Status.FAILURE

        print(f"[TASK] Navigate FAILED during drive (result_code={result.result_code})")
        return Status.FAILURE


class ReplanOnObstacle(py_trees.decorators.Decorator):
    """Wiederholt Plan+Fahrt nur nach RESULT_OBSTACLE_DETECTED (max. max_attempts mal)."""

    def __init__(self, name, child, state, max_attempts):
        super().__init__(name=name, child=child)
        self.state = state
        self.max_attempts = max_attempts
        self.obstacles = 0

    def initialise(self):
        self.obstacles = 0
        self.state.nav_obstacle_hit = False

    def update(self):
        if self.decorated.status == Status.FAILURE and self.state.nav_obstacle_hit:
            self.state.nav_obstacle_hit = False
            self.obstacles += 1
            if self.obstacles <= self.max_attempts:
                print(f"[TASK] Navigate replanning (attempt {self.obstacles}/{self.max_attempts})")
                return Status.RUNNING
            print("[TASK] Navigate FAILED: replan attempts exhausted")
            return Status.FAILURE
        return self.decorated.status


def build(robot, state, object_name, map_path,
          standoff_m=NavigateTask.DEFAULT_STANDOFF_M,
          priority=LOW,
          max_replan_attempts=NavigateTask.DEFAULT_MAX_REPLAN_ATTEMPTS,
          obstacle_radius_m=NavigateTask.DEFAULT_OBSTACLE_RADIUS_M):

    attempt = py_trees.composites.Sequence(name="PlanAndDrive", memory=True, children=[
        PlanLeaf(robot, state, map_path, standoff_m, obstacle_radius_m),
        DriveLeaf(robot, state, map_path),
    ])
    replan = ReplanOnObstacle("ReplanOnObstacle", attempt, state, max_replan_attempts)

    body = py_trees.composites.Sequence(
        name=f"NavigateObject({object_name})", memory=True, children=[
            TaskLabel("NavigateObject", robot, state),
            ResolveTarget(state, object_name, map_path),
            replan,
        ])
    scoped = StateFlags(body.name, body, state,
                        on_start={"is_navigating": True},
                        on_end={"is_navigating": False})
    return with_priority(scoped, priority)