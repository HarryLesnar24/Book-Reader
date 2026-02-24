from pydantic import BaseModel
from datetime import datetime


class ListBookModel(BaseModel):
    filename: str
    updatedDate: datetime
