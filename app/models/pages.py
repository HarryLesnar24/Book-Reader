from sqlmodel import SQLModel, Field, Column
import uuid
import edwh_uuid7
import sqlalchemy.dialects.postgresql as pg


class Page(SQLModel, table=True):
    uid: uuid.UUID = Field()
