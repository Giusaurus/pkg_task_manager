import asyncio
from std_msgs.msg import Bool

from .base import BaseTask


class ReturnToIdle(BaseTask):

    def __init__(self):

        super().__init__("ReturnToIdle")

    async def run(self, robot, state):

        print("[TASK] ReturnToIdle started")

        
        # Reset Flanken


        state.is_listening = False
        state.listening_for = ""

        state.is_greeting_guest = False

        state.is_navigating = False
        state.navigating_to = ""


        state.current_task = "Idle"

        print("[TASK] ReturnToIdle finished")

        return True