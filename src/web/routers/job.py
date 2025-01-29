from dataclasses import asdict

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_user
from dependencies.containers import RepositoriesContainer
from storage.sqlalchemy.tables import Job
from web.schemas.job import JobSchema, JobCreateSchema, JobUpdateSchema
from models.user import User

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("")
@inject
async def read_jobs(
    limit: int = 100,
    skip: int = 0,
    job_repository: RepositoriesContainer = Depends(Provide[RepositoriesContainer.job_repository]),
) -> list[JobSchema]:

    jobs_model = await job_repository.retrieve_many(limit=limit, skip=skip)

    jobs_schema = []
    for job in jobs_model:
        jobs_schema.append(JobSchema(
            id=job.id,
            user_id=job.user_id,
            title=job.title,
            description=job.description,
            salary_to=job.salary_to,
            salary_from=job.salary_from,
            is_active=job.is_active,
        ))

    return jobs_schema


@router.get("/{job_id}")
@inject
async def read_job(
    job_id: int,
    limit: int = 100,
    skip: int = 0,
    job_repository: RepositoriesContainer = Depends(Provide[RepositoriesContainer.job_repository]),
) -> list[JobSchema]:

    jobs_model = await job_repository.retrieve(id=job_id, limit=limit, skip=skip)

    jobs_schema = []
    for job in jobs_model:
        jobs_schema.append(JobSchema(
            id=job.id,
            user_id=job.user_id,
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
    job_repository: RepositoriesContainer = Depends(Provide[RepositoriesContainer.job_repository]),
    current_user: User = Depends(get_current_user),
) -> JobSchema:

    #if job_create_schema.user_id != current_user.id:
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    job_model = await job_repository.create(JobSchema(
        user_id=current_user.id,
        title=job_create_schema.title,
        description=job_create_schema.description,
        salary_to=job_create_schema.salary_to,
        salary_from=job_create_schema.salary_from,
        is_active=job_create_schema.is_active,
    ))
    return JobSchema(**asdict(job_model))


@router.put("")
@inject
async def update_job(
    job_update_schema: JobUpdateSchema,
    job_repository: RepositoriesContainer = Depends(Provide[RepositoriesContainer.job_repository]),
    current_user: User = Depends(get_current_user),
) -> JobSchema:

    existing_job = job_repository.retrieve(id=job_update_schema.id)
    if existing_job is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Несуществующая вакансия")
    #existing_user = user_repository.retrieve(id=current_user.id)
    if existing_job.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
    job_model = await job_repository.update(JobSchema(
        id=job_update_schema.id,
        user_id=current_user.id,
        title=job_update_schema.title,
        description=job_update_schema.description,
        salary_to=job_update_schema.salary_to,
        salary_from=job_update_schema.salary_from,
        is_active=job_update_schema.is_active,
    ))
    return JobSchema(**asdict(job_model))


@router.delete("/{id}")
@inject
async def delete(
    id: int,
    user_repository: RepositoriesContainer = Depends(Provide[RepositoriesContainer.user_repository]),
    job_repository: RepositoriesContainer = Depends(Provide[RepositoriesContainer.job_repository]),
    current_user: User = Depends(get_current_user),
) -> JobSchema:

    existing_job = await job_repository.retrieve(id=id)
    if existing_job is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Несуществующая вакансия")
    if existing_job.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недостаточно прав")
    return await job_repository.delete(id=id)
