from enum import Enum


class TaskPriority(Enum):
    LOW = "low"
    MID = "mid"
    HIGH = "high"
    CRITICAL = "critical"


LOW = TaskPriority.LOW
MID = TaskPriority.MID
HIGH = TaskPriority.HIGH
CRITICAL = TaskPriority.CRITICAL


MAX_RETRIES = {
    TaskPriority.LOW: 0,
    TaskPriority.MID: 1,
    TaskPriority.HIGH: 3,
    TaskPriority.CRITICAL: 3,
}