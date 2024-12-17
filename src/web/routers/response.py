from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.containers import RepositoriesContainer
from storage.sqlalchemy.tables import Response
from web.schemas.response import ResponseSchema

router = APIRouter(prefix="/responses", tags=["responses"])

@router.get("/{user_id}")
@inject
async def get_by_user_id(
    user_id: int,
    limit: int = 100,
    skip: int = 0,
    db: AsyncSession = Depends(Provide[RepositoriesContainer.db]),
) -> list[ResponseSchema]:

    async with db.Session() as session:
        query = select(Response).where(Response.user_id == user_id).limit(limit)
        res = await session.execute(query)
        result = res.scalars().all()

    return result

