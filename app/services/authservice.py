from sqlalchemy import FallbackAsyncAdaptedQueuePool
from core_db.models.user import User # type: ignore
from pydantic import SecretStr
from app.utilis.security import verifyHash
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from core_db.models.auth import RefreshToken # type: ignore
from core_db.schemas.auth import RefreshCreateModel # type: ignore


class AuthService:
    async def verifypassword(
        self, user: User, secret: SecretStr, session: AsyncSession
    ):
        crct, update = verifyHash(
            password=secret.get_secret_value(), pwdHash=user.passwordhash
        )
        if update:
            user.passwordhash = update
            await session.commit()
            return crct
        else:
            return crct

    async def createRefreshObject(
        self, refreshData: RefreshCreateModel, session: AsyncSession
    ) -> RefreshToken:
        refreshDict = refreshData.model_dump()
        newRefresh = RefreshToken(**refreshDict)
        session.add(newRefresh)
        await session.commit()
        return newRefresh

    async def getRefreshObject(
        self, jti: str, session: AsyncSession
    ) -> RefreshToken | None:
        statement = select(RefreshToken).where(RefreshToken.jti == jti)
        result = await session.exec(statement)
        return result.first()

    async def revokeRefreshToken(
        self, refreshObj: RefreshToken | None, session: AsyncSession
    ) -> bool:
        if refreshObj:
            setattr(refreshObj, "revoked", True)
            await session.flush()
            await session.commit()
            return True
        else:
            return False

    async def isvalidRefreshToken(self, jti: str, session: AsyncSession) -> bool:
        statement = select(RefreshToken.revoked).where(RefreshToken.jti == jti)
        result = await session.exec(statement)
        if not result:
            return False
        return True if result.first() == False else False
