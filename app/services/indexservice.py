# from sqlmodel import select
# from sqlmodel.ext.asyncio.session import AsyncSession
# from app.models.index import Index


# class IndexService:
#     async def createIndex(self, indexData: dict, session: AsyncSession):
#         newIndex = Index(**indexData)
#         session.add(newIndex)
#         await session.commit()
#         return newIndex
    
#     async def getProgress(self, book_id: str, user_id: str, session: AsyncSession):
#         statement = select(Index.progression).where((Index.book_uid == book_id) & (Index.user_uid == user_id))
#         result = await session.exec(statement)
#         return result.first()
    
#     async def getIndexDetail(self, book_id: str, session: AsyncSession):
#         statement = select(Index).where(Index.book_uid == book_id)
#         result = await session.exec(statement=statement)
#         return result.first()
    
#     async def updateProgression(self, book_id: str, user_id: str, session: AsyncSession, progressData: int):
#         statement = select(Index).where((Index.book_uid == book_id) & (Index.user_uid == user_id))
#         result = await session.exec(statement)
#         index = result.first()
#         if index:
#             index.progression = progressData
#             await session.commit()
        
    
    