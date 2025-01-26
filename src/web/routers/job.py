from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.containers import RepositoriesContainer
from storage.sqlalchemy.tables import Job
from web.schemas.job import JobSchema

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("")
@inject
async def read_jobs(
    limit: int = 100,
    skip: int = 0,
    #db: AsyncSession = Depends(Provide[RepositoriesContainer.db]),
    job_repository: RepositoriesContainer = Depends(RepositoriesContainer.job_repository),
) -> list[JobSchema]:

    jobs_model = await job_repository.read_all(limit=limit, skip=skip)

    jobs_schema = []
    for job in jobs_model:
        jobs_schema.append(JobSchema(
            id=job.id,
            user_id=job.user.id,
            title=job.title,
            description=job.description,
            salary_to=job.salary_to,
            salary_from=job.salary_from,
            is_active=job.is_active,
        ))

    return jobs_schema

