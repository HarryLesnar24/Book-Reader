from datetime import datetime
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from sqlmodel import default


class RefreshCreateModel(BaseModel):
    jti: str
    expire_at: datetime
    userid: str
    revoked: bool = Field(default=False)


class RefreshResponseModel(BaseModel):
    jti: uuid.UUID
    expire_at: datetime
    userid: uuid.UUID
    revoked: bool
