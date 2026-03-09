from sqlmodel import Field, Column, func, SQLModel, ForeignKeyConstraint, Relationship, TEXT, DateTime
from datetime import datetime
from typing import Optional
import uuid
from edwh_uuid7 import uuid7
import sqlalchemy.dialects.postgresql as pg


class Chunk(SQLModel, table=True):
    __tablename__ = "chunks" # type: ignore

    chunk_id: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True), default_factory=uuid7)
    page_uid: uuid.UUID = Field(foreign_key='pages.uid', nullable=False, index=True)
    book_uid: uuid.UUID = Field(foreign_key='books.uid', nullable=False, index=True)
    user_uid: uuid.UUID = Field(foreign_key='users.uid', nullable=False, index=True)
    chunk_index: int = Field(nullable=False)
    chunk_data: str = Field(sa_column=Column(TEXT, nullable=False))
    page: Optional["Page"] = Relationship(back_populates='chunks') # type: ignore
    book: Optional["Book"] = Relationship() # type: ignore
    user: Optional["User"] = Relationship() # type: ignore
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        )
    )