from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import Field
import uuid
from enum import Enum


class BookCreateModel(BaseModel):
    filename: str = Field(max_length=512)
    filepath: str = Field(max_length=2048)
    user_uid: str


# class BookUploadModel(BookCreateModel):
#     filepath: str = Field(pattern=r'^.+\.pdf$', max_length=2048)


class BookResponseModel(BaseModel):
    uid: uuid.UUID
    filename: str
    filepath: str
    user_uid: uuid.UUID
    created_at: datetime
    updated_at: datetime


class BookUpdateModel(BaseModel):
    filename: str = Field(pattern=r"^.+\.pdf$", max_length=512)


class BookStatusModel(str, Enum):
    pending = "pending"
    processing = "processing"
    ready_partial = "bootstrap complete"
    ready_full = "background complete"
    failed = "failed"
