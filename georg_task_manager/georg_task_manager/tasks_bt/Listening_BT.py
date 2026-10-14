import py_trees
from py_trees.common import Status
from datatypes.action import Listen

from georg_task_manager.bt.bt_common import ActionLeaf, TaskLabel, with_priority
from georg_task_manager.tasks.priority import LOW


class ListeningLeaf(ActionLeaf):

    def __init__(self, robot, state, sound, timeout_sec):
        super().__init__(f"Listen {sound}", robot.listen_action_client, robot, state,
                         timeout=timeout_sec + 2.0)
        self.sound = sound
        self.timeout_sec = timeout_sec

    def make_goal(self):
        goal = Listen.Goal()
        if self.sound == "SPEECH":
            goal.mode = Listen.Goal.MODE_SPEECH
        elif self.sound == "DOORBELL":
            goal.mode = Listen.Goal.MODE_DOORBELL
        else:
            goal.mode = Listen.Goal.MODE_DOORBELL
            print("(Wrong Mode: Using MODE_DOORBELL!)")
        goal.timeout_sec = self.timeout_sec
        return goal

    def on_start(self):
        print(f"[TASK] Listening started - target: {self.sound}")
        self.state.is_listening = True
        self.state.listening_for = self.sound

    def on_end(self):
        self.state.is_listening = False

    def on_result(self, status, result):
        if not result.detected:
            print(f"[TASK] Listening to {self.sound}: FAILED (confidence={result.confidence:.2f})")
            return Status.FAILURE
        print(f"[TASK] Listening to {self.sound}: Finished successfully "
              f"(confidence={result.confidence:.2f})(Transcript={result.transcript})")
        return Status.SUCCESS


def build(robot, state, sound, timeout_sec=60.0, priority=LOW):
    name = f"Listening({sound})"
    seq = py_trees.composites.Sequence(name=name, memory=True, children=[
        TaskLabel(name, robot, state),
        ListeningLeaf(robot, state, sound, timeout_sec),
    ])
    return with_priority(seq, priority)