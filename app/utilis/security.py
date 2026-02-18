from datetime import timedelta, datetime
from typing import Any, TypedDict, cast
from app.config import Config
from pwdlib import PasswordHash
from pydantic import SecretStr
import uuid
import jwt


class JWTPayload(TypedDict):
    sub: str
    exp: datetime
    jti: str
    iat: int
    refresh: bool


pwd = PasswordHash.recommended()


def generateHash(password: SecretStr) -> str:
    return pwd.hash(password.get_secret_value())


def verifyHash(password: str, pwdHash: str) -> tuple[bool, str | None]:
    valid, update = pwd.verify_and_update(password, pwdHash)
    return (valid, update)


def createToken(
    userUID: uuid.UUID, expiry: timedelta | None = None, refresh: bool = False
) -> tuple[str, JWTPayload] | str:
    payload: JWTPayload = {
        "sub": str(userUID),
        "exp": datetime.now()
        + (expiry if expiry else timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE)),
        "jti": str(uuid.uuid4()),
        "iat": int(datetime.now().timestamp()),
        "refresh": refresh,
    }

    token = jwt.encode(
        cast(dict[str, Any], payload), Config.JWT_KEY, Config.JWT_ALGORITHM
    )
    return (token, payload) if refresh else token


def decodeToken(token: str) -> dict | None:
    try:
        tokenData = jwt.decode(
            jwt=token, key=Config.JWT_KEY, algorithms=[Config.JWT_ALGORITHM]
        )
        return tokenData
    except jwt.PyJWTError as e:
        return None
