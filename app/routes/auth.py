from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, status, Depends, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from app.database import getSession
from app.config import Config
from app.dependency import OAuth2PasswordRequestForm
from app.services.userservice import UserService
from app.services.authservice import AuthService
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.user import UserCreateModel, UserReturnModel
from app.schemas.auth import RefreshCreateModel
from typing import cast
from app.models.user import User
from pydantic import SecretStr
from app.utilis.security import JWTPayload, createToken, decodeToken
from email.utils import format_datetime
from app.dependency import accessTokenValidation
from app.schemas.token import AccessToken


authRouter = APIRouter()
userService = UserService()
authService = AuthService()


async def revokeAccess(jti: str, session: AsyncSession) -> bool:
    obj = await authService.getRefreshObject(jti, session)
    return await authService.revokeRefreshToken(obj, session)


@authRouter.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserReturnModel
)
async def createUserAcc(
    userData: UserCreateModel, session: AsyncSession = Depends(getSession)
) -> User:
    email, username = userData.email, userData.username
    userExists = (
        await userService.checkUserExists(session=session, email=email)
        if email
        else await userService.checkUserExists(session=session, username=username)
    )
    if userExists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User already exists login with credentials",
        )
    newUser = await userService.createUser(userData, session)
    return newUser


@authRouter.post("/login", status_code=status.HTTP_200_OK, response_model=AccessToken)
async def login(
    response: Response,
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(getSession),
):
    userid = form.username
    pwd = SecretStr(form.password)

    rtoken = request.cookies.get("identity")
    if rtoken:
        tokenData = decodeToken(rtoken)
        if tokenData and await authService.isvalidRefreshToken(
            tokenData["jti"], session
        ):
            await revokeAccess(tokenData["jti"], session)
            response.delete_cookie(
                "identity", samesite="lax", path="/", domain="127.0.0.1", httponly=True
            )

    user = (
        await userService.checkUserExists(session, email=userid)
        if userid.find("@") != -1
        else await userService.checkUserExists(session, username=userid)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not exist sign up!"
        )

    if not await authService.verifypassword(user, pwd, session):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid Email/Username or Password",
        )

    refreshToken, payloadData = cast(
        tuple[str, dict[str, JWTPayload]],
        createToken(
            user.uid, expiry=timedelta(days=Config.REFRESH_TOKEN_EXPIRE), refresh=True
        ),
    )
    refreshDict = {
        "jti": str(payloadData["jti"]),
        "expire_at": payloadData["exp"],
        "userid": str(payloadData["sub"]),
    }

    refreshData = RefreshCreateModel(**refreshDict)
    await authService.createRefreshObject(refreshData, session)

    response.set_cookie(
        key="identity",
        value=refreshToken,
        expires=format_datetime(
            (datetime.now(timezone.utc) + timedelta(days=Config.REFRESH_TOKEN_EXPIRE)),
            usegmt=True,
        ),
        secure=False,
        httponly=True,
        samesite="lax",
    )

    accessToken = cast(str, createToken(user.uid))
    return AccessToken(access_token=accessToken, token_type="bearer")


@authRouter.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    response: Response,
    _: str = Depends(accessTokenValidation),
    session: AsyncSession = Depends(getSession),
):
    refreshToken = request.cookies.get("identity")
    if refreshToken:
        tokenData = decodeToken(refreshToken)
        if (
            tokenData
            and await authService.isvalidRefreshToken(tokenData["jti"], session)
            and await revokeAccess(tokenData["jti"], session)
        ):
            response.delete_cookie(
                "identity", httponly=True, domain="127.0.0.1", samesite="lax", path="/"
            )
            return {"message": "logged out successfully"}

        response.delete_cookie(
            "identity", samesite="lax", path="/", domain="127.0.0.1", httponly=True
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token"
        )
    return JSONResponse(
        content={"message": "Oops something went wrong! try again..."}, status_code=400
    )


@authRouter.get("/refresh")
async def getAccessToken(
    request: Request, session: AsyncSession = Depends(getSession)
) -> AccessToken:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    identity = request.cookies.get("identity")
    if not identity:
        raise credentials_exception
    tokenData = decodeToken(identity)
    if not tokenData:
        raise credentials_exception
    if not await authService.isvalidRefreshToken(tokenData["jti"], session):
        raise credentials_exception
    userExist = await userService.getUserByUid(tokenData["sub"], session)
    if not userExist:
        raise credentials_exception
    accessToken = createToken(userExist.uid)
    return AccessToken(access_token=cast(str, accessToken), token_type="bearer")
