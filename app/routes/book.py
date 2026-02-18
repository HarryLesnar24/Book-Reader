from pathlib import Path
from fastapi import APIRouter, Depends, status, File, UploadFile, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession
from app.utilis.document import DocumentValidator, DocumentStream
from app.models.book import Book
from app.services.bookservice import BookService
from app.services.userservice import UserService
from app.schemas.book import BookResponseModel, BookUpdateModel
from app.services.authservice import AuthService
from app.database import getSession
from app.dependency import accessTokenValidation
from typing import Annotated, List
from app.config import Config
from app.utilis.jobs import JobCreator




bookRouter = APIRouter()
bookService = BookService()
authService = AuthService()
userService = UserService()
initialValidator = DocumentValidator()

templates = Jinja2Templates(directory=f'{Path('app/templates').absolute()}')


@bookRouter.post("/uploadfiles")
async def uploadBooks(
    backgroundTask: BackgroundTasks,
    files: Annotated[list[UploadFile], File(...)],
    session: AsyncSession = Depends(getSession),
    userid: str = Depends(accessTokenValidation),
) -> List[Book]:
    creator = JobCreator()
    if len(files) > Config.MAX_FILE_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many files. Maximum {Config.MAX_FILE_UPLOAD} files allowed",
        )
    for file in files:
        validation = await initialValidator.validatefile(file)
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "File validation failed",
                    "errors": validation["errors"],
                },
            )

    user = await userService.getUserByUid(uid=userid, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Invalid User ID"},
        )
    books = await bookService.createBooks(files=files, user=user, session=session)
    if not books:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"message": "Upload Fails"}
        )
    backgroundTask.add_task(creator.createJob, books, session)
    return books


@bookRouter.get("/{bookuid}")
async def getBookById(
    bookuid: str,
    session: AsyncSession = Depends(getSession),
    userid: str = Depends(accessTokenValidation),
):
    book = await bookService.getBookByUid(bookuid, userid, session)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="No Book Found"
        )
    return book


@bookRouter.get("/", response_class=HTMLResponse)
async def getAllBooks(
    request: Request,
    session: AsyncSession = Depends(getSession),
    userid: str = '019b91ed-5ca4-7c7b-a31a-8534494d622b',
    
):
    books = await bookService.getUserBooks(userid, session)
    if not books:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="No books. upload book first"
        )
    return templates.TemplateResponse(name='catalog.html', context={'request': request, 'books': books, 'url': f'{Config.DOMAIN}api/{Config.API_VERSION}/reader'})


@bookRouter.post("/update/{bookid}")
async def updateBookName(
    updateData: BookUpdateModel,
    bookid: str,
    session: AsyncSession = Depends(getSession),
    userid: str = Depends(accessTokenValidation),
) -> Book:
    book = await bookService.getBookByUid(
        bookUid=bookid, userUid=userid, session=session
    )
    if not book:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="No book found"
        )
    updatedBook = await bookService.updateBookByUid(
        bookUpdate=updateData, book=book, session=session
    )
    return updatedBook


@bookRouter.get("/{bookid}/{filename}")
async def streamBookData(
    request: Request,
    bookid: str,
    filename: str,
    userid: str = '019b91ed-5ca4-7c7b-a31a-8534494d622b',
    session: AsyncSession = Depends(getSession),
) -> StreamingResponse:
    book = await bookService.getBookByUid(
        bookUid=bookid, userUid=userid, session=session
    )
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Invalid Book ID"}
        )
    if book.filename != filename:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Invalid Book Filename Request"},
        )

    docStreamer = DocumentStream()
    filePath = Path(book.filepath)
    if not filePath.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "File not present in storage system"},
        )
    
    fileSize = filePath.stat().st_size
    rangeHeader = request.headers.get('range')
    contents = {".pdf": "application/pdf"}
    contentType = contents.get(filePath.suffix, "application/octet-stream")
    header = {"Content-Disposition": f'inline; filename="{filename}"'}

    if rangeHeader:
        start, end = rangeHeader.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else fileSize - 1

        if start < 0 or end < start:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
                "message": "Invalid Range Request"
            })
        
        if start >= fileSize:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
                "message": "Invalid Range Request"
            })
        
        end = min(end, fileSize - 1)

        header.update({"Content-Range": f"bytes {start}-{end}/{fileSize}",
                       "Accept-Range": "bytes",
                       "Content-Length": str(end - start + 1)})
        print(f"From Range Streamer: {end - start + 1} chunk")
        return StreamingResponse(docStreamer.rangeStreamer(filePath, start, end), media_type=contentType, headers=header, status_code=status.HTTP_206_PARTIAL_CONTENT)
    
    print(f"From Streamer")
    return StreamingResponse(
        content=docStreamer.fileStreamer(filePath),
        media_type=contentType,
        headers=header,
    )















