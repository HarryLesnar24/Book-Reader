from datetime import datetime
import re
from pydantic import BaseModel, SecretStr, Field, EmailStr, field_validator
from email_validator import validate_email, EmailNotValidError
import uuid


class UserCreateModel(BaseModel):
    username: str = Field(max_length=32, pattern=r"^[A-Za-z][A-Za-z0-9_]{3,31}$")
    firstname: str | None = Field(default=None, max_length=64)
    lastname: str | None = Field(default=None, max_length=64)
    email: EmailStr = Field(max_length=255)
    password: SecretStr = Field(max_length=32)

    @field_validator("email", mode="before")
    @classmethod
    def validateEmail(cls, value: str):
        try:
            validate_email(value, check_deliverability=True)
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {str(e)}")
        return value

    @field_validator("password", mode="after")
    @classmethod
    def validatePassword(cls, value: SecretStr):
        secret = value.get_secret_value()
        pattern = re.compile(
            r"^(?=.*[A-Z])(?=.*[a-z])(?=(?:.*\d){2,})(?=.*[@#$%^&*()!_\-+=\[\]{}:;\"'<>,.?\\/|~`])[A-Za-z\d@#$%^&*()!_\-+=\[\]{}:;\"'<>,.?\\/|~`]{8,32}$"
        )
        if not bool(pattern.match(secret)):
            raise ValueError("Password must follow the following rules")
        return SecretStr(secret)


class UserReturnModel(BaseModel):
    uid: uuid.UUID
    username: str
    firstname: str | None = Field(default=None)
    lastname: str | None = Field(default=None)
    email: str
    passwordhash: SecretStr = Field(exclude=True)
    verified: bool
    role: str
    created_at: datetime
    updated_at: datetime


class UserUpdateModel(BaseModel):
    username: str | None = Field(
        default=None, max_length=32, pattern=r"^[A-Za-z][A-Za-z0-9_]{3,31}$"
    )
    firstname: str | None = Field(default=None, max_length=64)
    lastname: str | None = Field(default=None, max_length=64)
    passwordhash: SecretStr | None

    @field_validator("passwordhash", mode="after")
    @classmethod
    def validatePassword(cls, value: SecretStr):
        if not value:
            return
        secret = value.get_secret_value()
        pattern = re.compile(
            r"^(?=.*[A-Z])(?=.*[a-z])(?=(?:.*\d){2,})(?=.*[@#$%^&*()!_\-+=\[\]{}:;\"'<>,.?\\/|~`])[A-Za-z\d@#$%^&*()!_\-+=\[\]{}:;\"'<>,.?\\/|~`]{8,32}$"
        )
        if not bool(pattern.match(secret)):
            raise ValueError("Password must follow the following rules")
        return SecretStr(secret)
