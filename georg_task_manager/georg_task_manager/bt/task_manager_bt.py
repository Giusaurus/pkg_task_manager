import time

import rclpy
from rclpy.node import Node
from py_trees.common import Status
import py_trees_ros
from std_msgs.msg import String

from georg_task_manager.Georg import Georg
from .mission_selector_bt import select_mission


class TaskManagerBT(Node):

    def __init__(self):
        super().__init__("task_manager_bt")
        self.started = False
        self.shutdown_requested = False
        self.tree = None
        self.robot = Georg(self)
        self.create_timer(0.5, self.start_once)

    def start_once(self):
        if self.started:
            return
        self.started = True

        mission = select_mission()
        if mission is None:
            self.get_logger().info("Exiting...")
            rclpy.shutdown()
            return

        self.get_logger().info("Starting mission (BT)...")
        self.robot.state.mission_running = True
        self.robot.state.abort_requested = False

        root = mission(self.robot, self.robot.state)
        self.tree = py_trees_ros.trees.BehaviourTree(root, unicode_tree_debug=False)
        self.tree.setup(node=self, timeout=15.0)
        self.tree.add_post_tick_handler(self._on_tick)
        self.tree.tick_tock(period_ms=100)

        self.create_timer(0.1, self.check_shutdown)

    def _on_tick(self, tree):
        status = tree.root.status
        if status not in (Status.SUCCESS, Status.FAILURE) or self.shutdown_requested:
            return
        state = self.robot.state
        if status == Status.SUCCESS:
            print("=== Mission Complete ===")
            state.mission_finished = True
        else:
            print("\n[MISSION ABORTED]\n")
        state.mission_running = False
        state.current_task = "Idle"
        msg = String()
        msg.data = "Idle"
        self.robot.taskmanager_current_task_pub.publish(msg)
        self.shutdown_requested = True

    def check_shutdown(self):
        if self.shutdown_requested:
            self.destroy_node()
            if rclpy.ok():
                rclpy.shutdown()

    def request_abort(self):
        self.robot.state.abort_requested = True


def main():
    rclpy.init(signal_handler_options=rclpy.SignalHandlerOptions.NO)
    node = TaskManagerBT()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\n[CTRL+C] Abort requested - waiting for mission to stop...")
        node.request_abort()
        deadline = time.monotonic() + 5.0
        try:
            while not node.shutdown_requested and time.monotonic() < deadline:
                rclpy.spin_once(node, timeout_sec=0.1)
        except KeyboardInterrupt:
            print("\n[CTRL+C] Second interrupt - forcing shutdown.")
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()