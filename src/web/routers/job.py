from dataclasses import asdict

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_user
from dependencies.containers import RepositoriesContainer
from storage.sqlalchemy.tables import Job
from web.schemas.job import JobSchema, JobCreateSchema
from models.user import User

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


@router.post("")
@inject
async def create_job(
        job_create_schema: JobCreateSchema,
        job_repository: RepositoriesContainer = Depends(RepositoriesContainer.job_repository),
        current_user: User = Depends(get_current_user),
) -> JobSchema:

    if job_create_schema.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    job_model = job_repository.create(job_create_schema)
    return JobSchema(**asdict(job_model))
