from fastapi import background
from pydantic import BaseModel
from enum import Enum

class JobTypeEnum(str, Enum):
    bootstrap = "bootstrap"
    background = "background"
    focus = "focus"

class JobPriorityEnum(int, Enum):
    low = 2
    high = 1
    urgent = 0


