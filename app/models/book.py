from sqlalchemy import VARCHAR, DateTime, false, table
from sqlmodel import SQLModel, Field, Column, Relationship, String, func, Enum, text
from pydantic import EmailStr
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, timezone, tzinfo
from typing import List, Optional
from edwh_uuid7 import uuid7
import uuid
from app.schemas.book import BookStatusModel

# book_status_enum = pg.ENUM(
#     BookStatusModel,
#     name='bookstatus',
#     create_type=True,

# )


class Book(SQLModel, table=True):
    __tablename__ = "books"  # type: ignore
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True), default_factory=uuid7
    )
    filename: str = Field(index=True)
    filepath: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    user_uid: uuid.UUID = Field(foreign_key="users.uid", nullable=False, index=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    )
    status: BookStatusModel = Field(
        default=BookStatusModel.pending,
        sa_column=Column(
            Enum(BookStatusModel),
            server_default=BookStatusModel.pending,
            nullable=False,
        ),
    )
    total_pages: int = Field(sa_column=Column(pg.INTEGER, nullable=True), default=None)
    duplicate: bool = Field(
        default=False, sa_column=Column(pg.BOOLEAN, server_default=text("false"))
    )
