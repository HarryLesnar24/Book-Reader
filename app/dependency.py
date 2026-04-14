from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status, Request, Query
from app.utilis.security import decodeToken
from typing import Optional


oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def accessTokenValidation(headerToken: Optional[str] = Depends(oauth2), queryToken: Optional[str] = Query(default=None, alias='token')) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    credential = headerToken or queryToken
    
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing from header and query parameters"
        )
    
    payload = await decodeToken(credential)
    if not payload:
        raise credentials_exception
    if payload["refresh"] == True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token get access token",
        )
    uid = str(payload["sub"])
    return uid
