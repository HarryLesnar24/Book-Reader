from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status, Request
from app.utilis.security import decodeToken


oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def accessTokenValidation(credential: str = Depends(oauth2)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decodeToken(credential)
    if not payload:
        raise credentials_exception
    if payload["refresh"] == True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token get access token",
        )
    uid = str(payload["sub"])
    return uid
