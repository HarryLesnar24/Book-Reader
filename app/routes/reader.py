from fastapi import Depends, status, APIRouter, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.templating import Jinja2Templates
from app.database import getSession
from app.dependency import accessTokenValidation
from app.schemas.reader import ListBookModel
from app.services import indexservice

# from app.services.indexservice import IndexService
from typing import List
from pathlib import Path
from app.services.bookservice import BookService
from app.config import Config


readRouter = APIRouter()
bookService = BookService()
# indexService = IndexService()

template = Jinja2Templates(directory=f"{Path('app/templates/').absolute()}")


@readRouter.get("/{bookuid}")
async def viewBook(
    request: Request, bookuid: str, session: AsyncSession = Depends(getSession)
):
    book = await bookService.getBookByUid(
        bookUid=bookuid, userUid="019b91ed-5ca4-7c7b-a31a-8534494d622b", session=session
    )
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Book Not Found"}
        )
    pdfURL = f"{Config.DOMAIN}api/v1/books/{bookuid}/{book.filename}"

    return template.TemplateResponse(
        name="viewer.html",
        context={"request": request, "url": pdfURL, "filename": book.filename},
    )


# @readRouter.get('/index')
# async def createIndexRequest(book_uid: str, user_id: str = Depends(accessTokenValidation), session: AsyncSession = Depends(getSession)):
#     book = await bookService.getBookByUid(bookUid=book_uid, userUid=user_id, session=session)
#     if not book:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
#             'message': 'Invalid Book UID'
#         })

#     index = {'book_uid': book.uid,
#              'user_uid': book.user_uid,
#              'filelocation': book.filepath}

#     response = await indexService.createIndex(index, session)
#     if not response:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
#             "message": "Something went wrong"
#         })
#     return response


# @readRouter.get('/status')
# async def getStatus(book_uid: str, user_id: str = Depends(accessTokenValidation), session: AsyncSession = Depends(getSession)):
#     progression = await indexService.getProgress(book_uid, user_id, session)
#     if progression is None:
#         raise HTTPException(status_code=status.HTTP_410_GONE, detail={
#             'message': 'Requested Content Not Found'
#         })
#     return progression
