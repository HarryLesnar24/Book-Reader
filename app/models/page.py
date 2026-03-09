from datetime import datetime
from sqlmodel import SQLModel, Field, Column, Enum, func, Relationship
import uuid
from edwh_uuid7 import uuid7
from sqlalchemy import DateTime
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import UniqueConstraint
from typing import List, Optional
from app.schemas.page import PageIndexEnum, PageStatusEnum


class Page(SQLModel, table=True):
    __tablename__ = "pages"  # type: ignore
    __table_args__ = (UniqueConstraint("book_uid", "page_no", name="uq_book_page"),)
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True), default_factory=uuid7
    )
    page_no: int = Field(index=True, sa_type=pg.INTEGER)
    book_uid: uuid.UUID = Field(foreign_key="books.uid", nullable=False, index=True)
    user_uid: uuid.UUID = Field(foreign_key="users.uid", nullable=False)
    index: PageIndexEnum = Field(
        sa_column=Column(Enum(PageIndexEnum), nullable=False),
        default=PageIndexEnum.pending,
    )
    required_deep: bool = Field(default=False, sa_type=pg.BOOLEAN)
    has_image: bool = Field(default=False, sa_type=pg.BOOLEAN)
    has_table: bool = Field(default=False, sa_type=pg.BOOLEAN)
    has_code: bool = Field(default=False, sa_type=pg.BOOLEAN)
    has_formula: bool = Field(default=False, sa_type=pg.BOOLEAN)
    status: PageStatusEnum = Field(sa_column=Column(Enum(PageStatusEnum)))
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

    book: Optional["Book"] = Relationship(back_populates='pages') # type: ignore

    chunks: List['Chunk'] = Relationship(back_populates='page', sa_relationship_kwargs={'lazy': 'raise_on_sql'}) # type: ignore
