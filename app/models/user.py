from sqlalchemy import VARCHAR, DateTime, table
from sqlmodel import SQLModel, Field, Column, Relationship, String, func
from pydantic import EmailStr
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, timezone, tzinfo
from typing import List, Optional
from edwh_uuid7 import uuid7
import uuid


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True), default_factory=uuid7
    )
    username: str = Field(sa_column=Column(String(64), unique=True, nullable=False))
    firstname: str | None = Field(
        sa_column=Column(pg.VARCHAR, nullable=True), default=None
    )
    lastname: str | None = Field(
        sa_column=Column(pg.VARCHAR, nullable=True), default=None
    )
    email: EmailStr = Field(sa_column=Column(String(255), unique=True, nullable=False))
    passwordhash: str = Field(
        exclude=True, sa_column=Column(pg.VARCHAR, nullable=False)
    )
    verified: bool = Field(default=False, sa_column=Column(pg.BOOLEAN, nullable=False))
    role: str = Field(default="User", sa_column=Column(String(50), nullable=False))
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

    books: List["Book"] = Relationship(back_populates='user', sa_relationship_kwargs={'lazy': 'raise_on_sql'}) # type: ignore
