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
    db: AsyncSession = Depends(Provide[RepositoriesContainer.db]),
) -> list[JobSchema]:

    async with db.Session() as session:
        query = select(Job).limit(limit)
        res = await session.execute(query)
        jobs = res.scalars().all()

    return jobs

