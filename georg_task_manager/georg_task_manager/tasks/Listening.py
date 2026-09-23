# listening.py
from .base import BaseTask
from .timeout_watcher import wait_for_action_result
from .priority import TaskPriority

from datatypes.action import Listen


class Listening(BaseTask):

    def __init__(self, sound: str, timeout_sec: float = 60.0, priority: TaskPriority = TaskPriority.LOW):

        super().__init__(f"Listening({sound})", priority)
        self.sound = sound
        self.timeout_sec = timeout_sec

    async def run(self, robot, state):

        print(f"[TASK] Listening started - target: {self.sound}")

        goal_msg = Listen.Goal()

        if self.sound == "SPEECH":
            goal_msg.mode = Listen.Goal.MODE_SPEECH

        elif self.sound == "DOORBELL":    
            goal_msg.mode = Listen.Goal.MODE_DOORBELL

        else:
            goal_msg.mode = Listen.Goal.MODE_DOORBELL
            print (f"(Wrong Mode: Using MODE_DOORBELL!)")

        goal_msg.timeout_sec = self.timeout_sec

        state.is_listening = True
        state.listening_for = self.sound

        result = await wait_for_action_result(
            robot.listen_action_client,
            goal_msg,
            timeout=self.timeout_sec + 2.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )

        state.is_listening = False



        if result is None:
            print(f"[TASK] Listening to {self.sound}: REJECTED/TIMEOUT/ABORTED")
            return False

        if not result.detected:
            print(f"[TASK] Listening to {self.sound}: FAILED "
                  f"(confidence={result.confidence:.2f})")
            return False


        print(f"[TASK] Listening to {self.sound}: Finished successfully "
            f"(confidence={result.confidence:.2f})"
            f"(Transcript={result.transcript})")
        return True

