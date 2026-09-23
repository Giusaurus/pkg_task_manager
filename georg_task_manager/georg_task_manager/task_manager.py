from collections import deque
from std_msgs.msg import String
import rclpy

from georg_task_manager.tasks.priority import TaskPriority, MAX_RETRIES


class TaskManager:

    def __init__(self, robot, state, current_task_pub):

        self.robot = robot
        self.state = state
        self.current_task_pub = current_task_pub

    def request_abort(self):
        self.state.abort_requested = True

    async def run(self, tasks):

        print("\n=== Mission Started ===\n")

        self.state.mission_running = True
        self.state.abort_requested = False

        queue = deque(tasks)

        while queue:

            if self.state.abort_requested:
                print("\n[MISSION ABORTED] Stopping before next task\n")
                self.state.mission_running = False
                self._go_idle()
                return False

            task = queue.popleft()

            self.state.current_task = task.name
            self._publish_task_state(task.name)

            print(f"[TASK MANAGER] Running {task.name}")

            result = await task.run(
                self.robot,
                self.state
            )

            print(
                f"[TASK RESULT] {result}\n"
            )

            if not result:

                if not self._handle_failure(task, queue):

                    print(
                        "[MISSION FAILED]"
                    )

                    self.state.mission_running = False
                    self._go_idle()

                    return False

        self._go_idle()

        self.state.mission_running = False
        self.state.mission_finished = True

        print(
            "=== Mission Complete ==="
        )

        return True

    def _handle_failure(self, task, queue):

        task.attempts += 1
        max_retries = MAX_RETRIES.get(task.priority, 0)

        if task.attempts > max_retries:

            if task.priority == TaskPriority.CRITICAL:
                print(f"[MISSION ABORTED] {task.name} critical, out of retries")
                return False

            print(f"[TASK DISCARDED] {task.name} ({task.priority.name})")
            return True

        if task.priority in (TaskPriority.HIGH, TaskPriority.CRITICAL):
            print(f"[TASK RETRY] {task.name} retries immediately "
                  f"(attempt {task.attempts}/{max_retries})")
            queue.appendleft(task)
            return True

        if task.priority == TaskPriority.MID:
            print(f"[TASK REQUEUED] {task.name} retries after next task "
                  f"(attempt {task.attempts}/{max_retries})")
            queue.insert(1, task)
            return True

        return True

    def _go_idle(self):

        self.state.current_task = "Idle"
        self._publish_task_state("Idle")

    def _publish_task_state(self, name: str) -> None:

        if not rclpy.ok():
            return

        msg = String()
        msg.data = name

        try:
            self.current_task_pub.publish(msg)
        except rclpy._rclpy_pybind11.RCLError:
            pass