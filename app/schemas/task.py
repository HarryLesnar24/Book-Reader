from pydantic import BaseModel
from enum import Enum


class TaskStatusEnum(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"
    cancelled = "cancelled"
