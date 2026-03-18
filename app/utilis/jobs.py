from core_db.models.book import Book # type: ignore
import asyncio
from typing import List, Literal, Tuple
from app.config import Config
import pymupdf
from app.services.jobservice import JobService
from sqlmodel.ext.asyncio.session import AsyncSession
from pymupdf import Document
import uuid
import hashlib
from core_db.schemas.job import JobTypeEnum, JobPriorityEnum # type: ignore

failedJobs = []


jobService = JobService()


class JobCreator:
    # async def isduplicate(self, book: Book):
    #     return book.duplicate

    async def open_document(self, path: str) -> Document:
        return await asyncio.to_thread(pymupdf.open, path)

    async def pageRangeSelection(
        self, total: int
    ) -> Tuple[Literal[0], int] | List[Tuple[int, int]]:
        if total < Config.RANGE:
            return (0, total - 1)
        ranges: List[Tuple[int, int]] = [
            (i, min(i + Config.RANGE - 1, total - 1))
            for i in range(0, total, Config.RANGE)
        ]
        return ranges

    async def createDupeKey(
        self, start: int, end: int, book_id: str, user_id: str, jobtype: str
    ):
        key = f"{user_id}-{book_id}-{jobtype}-{start}-{end}"
        hashObj = hashlib.sha256(key.encode())
        return hashObj.hexdigest()

    async def createJob(self, books: List[Book], session: AsyncSession):
        jobsData = []
        for book in books:
            if not book.duplicate:
                document = await self.open_document(book.filepath)
                totalPages = document.page_count
                rangePages = await self.pageRangeSelection(totalPages)

                if isinstance(rangePages, list):
                    for i, (start, end) in enumerate(rangePages):
                        jobtype = (
                            JobTypeEnum.bootstrap if i == 0 else JobTypeEnum.background
                        )
                        dupeKey = await self.createDupeKey(
                            start, end, str(book.uid), str(book.user_uid), jobtype
                        )
                        jobsData.append(
                            {
                                "book_uid": str(book.uid),
                                "user_uid": str(book.user_uid),
                                "page_total": end - start + 1,
                                "job_type": jobtype,
                                "priority": JobPriorityEnum.high
                                if jobtype == JobTypeEnum.bootstrap
                                else JobPriorityEnum.low,
                                "page_start": start,
                                "page_end": end,
                                "dedupekey": dupeKey,
                            }
                        )
                else:
                    start, end = rangePages
                    dupeKey = await self.createDupeKey(
                        start,
                        end,
                        str(book.uid),
                        str(book.user_uid),
                        JobTypeEnum.bootstrap,
                    )
                    jobsData.append(
                        {
                            "book_uid": str(book.uid),
                            "user_uid": str(book.user_uid),
                            "page_total": end - start + 1,
                            "job_type": JobTypeEnum.bootstrap,
                            "priority": JobPriorityEnum.high,
                            "page_start": start,
                            "page_end": end,
                            "dedupekey": dupeKey,
                        }
                    )

        response = await jobService.createJobsBatch(jobsData, session)
