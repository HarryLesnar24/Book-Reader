from typing import List
import uuid
from sqlalchemy.dialects.postgresql import insert
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.job import Job



class JobService:

    async def createJobsBatch(self, jobs: List[dict], session: AsyncSession):
        createdJobs = []
        try:
            for job in jobs:
                job['book_uid'] = uuid.UUID(job['book_uid'])
                job['user_uid'] = uuid.UUID(job['user_uid'])
                stmt = insert(Job).values(**job).on_conflict_do_nothing(constraint='uq_jobs_user_book_dedupe').returning(Job)
                result = await session.exec(stmt)
                inserted_job = result.scalar_one_or_none()
                if inserted_job:
                    createdJobs.append((inserted_job, True, None))
                else:
                    createdJobs.append((Job(**job), False, 'Duplicate Dedupekey'))
                    
            await session.commit()
            return createdJobs
        except Exception as e:
            await session.rollback()
            return [(job, False, str(e)) for job in createdJobs]

    
    async def getJob(self, job_uid: str, session: AsyncSession):
        statement = select(Job).where(Job.job_uid == job_uid)
        result = await session.exec(statement)
        job = result.first()
        return job
        

    async def updateJob(self, job_id: str, jobUpdate: dict, session: AsyncSession):
        job = await self.getJob(job_id, session)
        if job:
            for k, v in jobUpdate.items():
                setattr(job, k, v)
                await session.commit()
                return True
        return False
        
        


    

    