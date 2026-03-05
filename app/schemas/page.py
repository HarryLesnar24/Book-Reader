from enum import Enum
from pydantic import BaseModel


class PageIndexEnum(str, Enum):
    pending = "PENDING"
    text = "TEXT"
    quick = "QUICK"
    deep = "DEEP"


class PageStatusEnum(str, Enum):
    complete = "COMPLETED"
    fail = "FAILED"
