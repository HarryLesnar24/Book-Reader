from pickle import FALSE
from sqlmodel import SQLModel, Field, Column, func, Enum
from datetime import datetime
from sqlalchemy import DateTime, UniqueConstraint
import sqlalchemy.dialects.postgresql as pg
from edwh_uuid7 import uuid7
from app.schemas.task import TaskStatusEnum
from app.schemas.job import JobPriorityEnum, JobTypeEnum
import uuid


class Job(SQLModel, table=True):
    __tablename__ = "jobs"  # type: ignore
    __table_args__ = (
        UniqueConstraint(
            "user_uid", "book_uid", "dedupekey", name="uq_jobs_user_book_dedupe"
        ),
    )
    job_uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True), default_factory=uuid7
    )
    book_uid: uuid.UUID = Field(foreign_key="books.uid", nullable=False, index=True)
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
            nullable=False,
            onupdate=func.now(),
        )
    )
    page_total: int = Field(nullable=True)
    job_type: JobTypeEnum = Field(
        sa_column=Column(Enum(JobTypeEnum), nullable=False),
        default=JobTypeEnum.bootstrap,
    )
    priority: JobPriorityEnum = Field(
        sa_column=Column(Enum(JobPriorityEnum), nullable=False)
    )
    page_done: int = Field(default=0)
    task_status: TaskStatusEnum = Field(
        sa_column=Column(Enum(TaskStatusEnum)), default=TaskStatusEnum.queued
    )
    page_start: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    page_end: int = Field(sa_column=Column(pg.INTEGER, nullable=False))
    attempts: int = Field(sa_column=Column(pg.INTEGER), default=0)
    error: str = Field(sa_column=Column(pg.VARCHAR, nullable=True), default=None)
    next_run_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    locked_by: str = Field(sa_column=Column(pg.VARCHAR, nullable=True))
    locked_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    heartbeat_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    dedupekey: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    completed: bool = Field(sa_column=Column(pg.BOOLEAN), default=False)
