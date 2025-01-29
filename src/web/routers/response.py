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
    #db: AsyncSession = Depends(Provide[RepositoriesContainer.db]),
    response_repository: RepositoriesContainer = Depends(RepositoriesContainer.response_repository),
) -> list[ResponseSchema]:

    # async with db.Session() as session:
    #     query = select(Response).where(Response.user_id == user_id).limit(limit)
    #     res = await session.execute(query)
    #     result = res.scalars().all()
    responses_from_db = await response_repository.retrieve_many(limit=limit, skip=skip)

    result = []
    for response in responses_from_db:
        if response.user_id == user_id:
            result.append(response)

    return result
