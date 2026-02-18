from app.schemas.user import UserCreateModel, UserUpdateModel
from app.models.user import User
from app.utilis.security import generateHash
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from pydantic import EmailStr


class UserService:
    async def getUserByEmail(self, email: str, session: AsyncSession) -> User | None:
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def getUserByName(self, username: str, session: AsyncSession) -> User | None:
        statement = select(User).where(User.username == username)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def getUserByUid(self, uid: str, session: AsyncSession) -> User | None:
        statement = select(User).where(User.uid == uid)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def checkUserExists(
        self,
        session: AsyncSession,
        email: str | None = None,
        username: str | None = None,
    ) -> User | None:
        return (
            await self.getUserByEmail(email, session)
            if email
            else await self.getUserByName(username, session)
            if username
            else None
        )

    async def createUser(
        self, userData: UserCreateModel, session: AsyncSession
    ) -> User:
        userDict = userData.model_dump()
        newUser = User(**userDict)
        newUser.passwordhash = generateHash(userDict["password"])
        session.add(newUser)
        await session.commit()
        return newUser

    async def updateUser(
        self, user: User, updateData: UserUpdateModel, session: AsyncSession
    ):
        updateDict = updateData.model_dump(exclude_none=True)
        for k, v in updateDict.items():
            setattr(user, k, v)
        await session.commit()
        return user

    async def deleteUser(self, username: str, session: AsyncSession):
        pass
