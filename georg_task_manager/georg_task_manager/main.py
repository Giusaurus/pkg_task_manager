import threading
import asyncio

import rclpy
from rclpy.node import Node

from .Georg import Georg
from .task_manager import TaskManager
from .mission_selector import select_mission
from std_msgs.msg import String


class TaskManagerNode(Node):

    def __init__(self):

        super().__init__("task_manager")

        self.started = False
        self.shutdown_requested = False
        self.mission_thread = None

        self.robot = Georg(self)

        self.manager = TaskManager(
            self.robot,
            self.robot.state,
            self.robot.taskmanager_current_task_pub
        )

        self.create_timer(
            0.5,
            self.start_once
        )


    def start_once(self):

        if self.started:
            return

        self.started = True

        mission = select_mission()

        if mission is None:

            self.get_logger().info(
                "Exiting..."
            )

            rclpy.shutdown()
            return

        self.get_logger().info(
            "Starting mission..."
        )

        self.start_mission_thread(
            mission
        )

    def start_mission_thread(
        self,
        mission
    ):

        def runner():

            try:
                asyncio.run(
                    self.manager.run(
                        mission
                    )
                )
            except asyncio.CancelledError:
                pass

            self.shutdown_requested = True

        self.mission_thread = threading.Thread(
            target=runner,
            daemon=True
        )
        self.mission_thread.start()

        self.create_timer(
            0.1,
            self.check_shutdown
        )

    def check_shutdown(self):

        if self.shutdown_requested:

            self.destroy_node()

            if rclpy.ok():
                rclpy.shutdown()

    def request_abort(self):

        self.manager.request_abort()


def main():

    rclpy.init()

    node = TaskManagerNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:

        print(
            "\n[CTRL+C] Abort requested - waiting for mission to stop..."
        )

        node.request_abort()

        if node.mission_thread is not None:

            try:
                node.mission_thread.join(timeout=5.0)
            except KeyboardInterrupt:
                print(
                    "\n[CTRL+C] Second interrupt received - forcing shutdown "
                    "without waiting further."
                )

            if node.mission_thread.is_alive():
                print(
                    "[WARNING] Mission thread did not stop in time - "
                    "forcing shutdown anyway"
                )

    finally:

        if rclpy.ok():

            node.destroy_node()

            rclpy.shutdown()