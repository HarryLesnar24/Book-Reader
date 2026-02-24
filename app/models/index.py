# from datetime import datetime
# from sqlmodel import SQLModel, Field, Column, DateTime, func
# import sqlalchemy.dialects.postgresql as pg
# from edwh_uuid7 import uuid7
# import uuid


# class Index(SQLModel, table=True):
#     uid: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, unique=True), default_factory=uuid7)
#     book_uid: uuid.UUID = Field(foreign_key='books.uid', nullable=False, unique=True)
#     user_uid: uuid.UUID = Field(foreign_key='users.uid', nullable=False)
#     filelocation: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
#     progression: int = Field(sa_column=Column(pg.INTEGER), default=0)
#     created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
#     updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()))
