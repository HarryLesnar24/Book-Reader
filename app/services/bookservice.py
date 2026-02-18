from pathlib import Path
from typing import List, Sequence
from fastapi import UploadFile
from app.models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.book import Book
from app.schemas.book import BookCreateModel, BookUpdateModel
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError
import aiofiles



class BookService:
    async def getUserBooks(self, userUID: str, session: AsyncSession) -> Sequence[Book]:
        statement = select(Book).where((Book.user_uid == userUID))
        books = await session.exec(statement)
        return books.all()

    async def findByName(self, bookName: str, user_id: str, session: AsyncSession) -> bool:
        statement = select(Book).where((Book.filename == bookName) & (Book.user_uid == user_id))
        book = await session.exec(statement)
        return True if book.first() else False


    async def createBooks(
        self, files: List[UploadFile], user: User, session: AsyncSession
    ) -> List[Book]:
        uploadedPaths: List[Path] = []
        books: List[Book] = []

        uploadDir = Path("storage/books") / f"{user.username}-{user.uid}"
        uploadDir.mkdir(exist_ok=True, parents=True)

        try:
            for file in files:
                assert file.filename is not None
                duplicate = False
                filename = file.filename
                originalStem = Path(filename).stem
                suffix = Path(filename).suffix
                i = 0

                # Ensure unique filename
                while await self.findByName(filename, str(user.uid), session):
                    i += 1
                    if not duplicate:
                        duplicate = True
                    filename = f"{originalStem}({i}){suffix}"

                book = BookCreateModel(
                    filename=filename, user_uid=str(user.uid), filepath=""
                )
                newBook = Book(**book.model_dump())

                filePath = (
                    uploadDir / f"{Path(filename).stem}-{newBook.uid}{suffix}"
                )

                # Write file safely
                try:
                    await file.seek(0)
                    async with aiofiles.open(filePath, "wb") as buffer:
                        while chunk := await file.read(8 * 1024 * 1024):
                            await buffer.write(chunk)
                except Exception as io_err:
                    raise IOError(f"Failed to save file {filename}: {io_err}")
                
                if duplicate:
                    newBook.duplicate = duplicate
                uploadedPaths.append(filePath)
                newBook.filepath = str(filePath.absolute())
                books.append(newBook)

            # Commit DB transaction
            session.add_all(books)
            await session.commit()
            return books

        except (SQLAlchemyError, IOError, ValueError) as e:
            # Rollback DB changes
            await session.rollback()

            # Cleanup uploaded files
            for path in uploadedPaths:
                if path.exists():
                    path.unlink()

            # Raise clear error
            raise RuntimeError(f"Book upload failed: {str(e)}") from e

        except Exception as e:
            # Catch-all fallback
            await session.rollback()
            for path in uploadedPaths:
                if path.exists():
                    path.unlink()
            raise RuntimeError(f"Unexpected error during book upload: {str(e)}") from e


    async def getBookByUid(
        self, bookUid: str, userUid: str, session: AsyncSession
    ) -> Book | None:
        statement = select(Book).where(
            (Book.uid == bookUid) & (Book.user_uid == userUid)
        )
        book = await session.exec(statement)
        return book.first()

    async def updateBookByUid(
        self, bookUpdate: BookUpdateModel, book: Book, session: AsyncSession
    ):
        bookUpdateDict = bookUpdate.model_dump(exclude_none=True)
        for k, v in bookUpdateDict.items():
            setattr(book, k, v)
        await session.commit()
        return book
    
    async def getBookLocation(self, book_uid: str, session: AsyncSession):
        statement = select(Book.filepath).where(Book.uid == book_uid)
        response = await session.exec(statement)
        filepath = response.first()
        return filepath

    async def deleteBookByUid(self, bookUid: str, session: AsyncSession):
        pass
