import sqlalchemy.dialects.postgresql as pg
import uuid
from sqlalchemy import false
from sqlmodel import SQLModel, Field, Column
from datetime import datetime


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refreshtokens"  # type: ignore
    jti: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False, primary_key=True))
    expire_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, nullable=False))
    userid: uuid.UUID = Field(nullable=False, foreign_key="users.uid", index=True)
    revoked: bool = Field(
        sa_column=Column(pg.BOOLEAN, nullable=False, server_default=false())
    )
