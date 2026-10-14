import time

import py_trees
from py_trees.common import Status
from std_msgs.msg import String

from georg_task_manager.tasks.priority import TaskPriority, MAX_RETRIES

SERVER_WAIT_S = 2.0


class ActionLeaf(py_trees.behaviour.Behaviour):
    """Entspricht wait_for_action_result(): Goal senden, Result abwarten,
    Timeout/Abort -> Goal stornieren und FAILURE."""

    def __init__(self, name, client, robot, state, timeout):
        super().__init__(name)
        self.client = client
        self.robot = robot
        self.state = state
        self.timeout = timeout
        self._reset()

    def _reset(self):
        self._t_wait = time.monotonic()
        self._t_goal = None
        self._goal_future = None
        self._goal_handle = None
        self._result_future = None

    # --- Hooks fuer Unterklassen ---
    def make_goal(self):
        raise NotImplementedError

    def on_result(self, status, result):
        raise NotImplementedError

    def on_start(self):
        pass

    def on_end(self):
        pass

    # --- py_trees ---
    def initialise(self):
        self._reset()
        self.on_start()

    def _cancel(self):
        if (self._goal_handle is not None and self._result_future is not None
                and not self._result_future.done()):
            self._goal_handle.cancel_goal_async()

    def update(self):
        if getattr(self.state, "abort_requested", False):
            self._cancel()
            return Status.FAILURE

        if self._goal_future is None:
            if self.client.server_is_ready():
                goal = self.make_goal()
                if goal is None:
                    return Status.FAILURE
                self._goal_future = self.client.send_goal_async(goal)
            elif time.monotonic() - self._t_wait > SERVER_WAIT_S:
                self.feedback_message = "Server nicht erreichbar"
                return Status.FAILURE
            return Status.RUNNING

        if self._goal_handle is None:
            if not self._goal_future.done():
                return Status.RUNNING
            handle = self._goal_future.result()
            if not handle.accepted:
                self.feedback_message = "Goal abgelehnt"
                return Status.FAILURE
            self._goal_handle = handle
            self._result_future = handle.get_result_async()
            self._t_goal = time.monotonic()

        if not self._result_future.done():
            if time.monotonic() - self._t_goal > self.timeout:
                self.feedback_message = "Timeout"
                self._cancel()
                return Status.FAILURE
            return Status.RUNNING

        res = self._result_future.result()
        return self.on_result(res.status, res.result)

    def terminate(self, new_status):
        if new_status == Status.INVALID:
            self._cancel()
        self.on_end()


class TaskLabel(py_trees.behaviour.Behaviour):
    """Wie TaskManager._run_single_task: current_task setzen und publizieren."""

    def __init__(self, task_name, robot, state):
        super().__init__(f"Label {task_name}")
        self.task_name = task_name
        self.robot = robot
        self.state = state

    def update(self):
        self.state.current_task = self.task_name
        msg = String()
        msg.data = self.task_name
        self.robot.taskmanager_current_task_pub.publish(msg)
        print(f"[TASK MANAGER BT] Running {self.task_name}")
        return Status.SUCCESS


class StateFlags(py_trees.decorators.Decorator):
    """Setzt state-Flags beim Start und setzt sie beim Ende zurueck (wie try/finally)."""

    def __init__(self, name, child, state, on_start, on_end):
        super().__init__(name=name, child=child)
        self.state = state
        self._on_start = on_start
        self._on_end = on_end

    def initialise(self):
        for k, v in self._on_start.items():
            setattr(self.state, k, v)

    def update(self):
        return self.decorated.status

    def terminate(self, new_status):
        for k, v in self._on_end.items():
            setattr(self.state, k, v)


def with_priority(subtree, priority):
    """Retry/Verwerfen/Abbruch wie TaskManager._handle_failure."""
    child = subtree
    if priority == TaskPriority.MID:
        delay = py_trees.composites.Sequence(
            name="RetryDelay", memory=True,
            children=[py_trees.timers.Timer("Wait", duration=1.0),
                      py_trees.behaviours.Failure("Retry")])
        child = py_trees.composites.Selector(
            name="TryOrWait", memory=True, children=[subtree, delay])

    node = py_trees.decorators.Retry(
        name=f"{subtree.name} [{priority.name}]",
        child=child,
        num_failures=MAX_RETRIES.get(priority, 0) + 1)

    if priority != TaskPriority.CRITICAL:
        node = py_trees.decorators.FailureIsSuccess(
            name=f"Discard {subtree.name}", child=node)
    return node