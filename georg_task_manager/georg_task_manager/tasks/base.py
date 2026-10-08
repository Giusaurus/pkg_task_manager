import asyncio
from .priority import TaskPriority


class BaseTask:

    def __init__(self, name, priority: TaskPriority = TaskPriority.LOW):
        self.name = name
        self.priority = priority
        self.attempts = 0

    async def run(self, interface):
        raise NotImplementedError