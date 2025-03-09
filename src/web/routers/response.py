from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_current_user
from dependencies.containers import RepositoriesContainer
from storage.sqlalchemy.tables import User
from web.schemas.response import ResponseCreateSchema, ResponseSchema, ResponseUpdateSchema

router = APIRouter(prefix="/responses", tags=["responses"])


@router.get("")
@inject
async def get_all(
    limit: int = 100,
    skip: int = 0,
    job_repository: RepositoriesContainer = Depends(Provide[RepositoriesContainer.job_repository]),
    response_repository: RepositoriesContainer = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
    current_user: User = Depends(get_current_user),
) -> list[ResponseSchema]:
    responses_from_db = await response_repository.retrieve_many(limit=limit, skip=skip)

    user_jobs = await job_repository.retrieve_many(limit=limit, skip=skip, user_id=current_user.id)
    current_user_jobs_ids = [job.id for job in user_jobs]

    result = []
    for response in responses_from_db:
        if response.user_id == current_user.id or response.job_id in current_user_jobs_ids:
            result.append(
                ResponseSchema(
                    id=response.id,
                    user_id=response.user_id,
                    job_id=response.job_id,
                    message=response.message,
                )
            )
    return result


@router.get("/{id}")
@inject
async def get_by_id(
    id: int,
    response_repository: RepositoriesContainer = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    result = await response_repository.retrieve(id=id)
    if result.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недостаточно прав")
    return result


@router.get("/users/{user_id}")
@inject
async def get_by_user_id(
    user_id: int,
    limit: int = 100,
    skip: int = 0,
    response_repository: RepositoriesContainer = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
    current_user: User = Depends(get_current_user),
) -> list[ResponseSchema]:
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недостаточно прав")

    responses_from_db = await response_repository.retrieve_many(limit=limit, skip=skip)

    result = []
    for response in responses_from_db:
        if response.user_id == user_id:
            result.append(response)

    return result


@router.get("/jobs/{job_id}")
@inject
async def get_by_job_id(
    job_id: int,
    limit: int = 100,
    skip: int = 0,
    job_repository: RepositoriesContainer = Depends(Provide[RepositoriesContainer.job_repository]),
    response_repository: RepositoriesContainer = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
    current_user: User = Depends(get_current_user),
) -> list[ResponseSchema]:
    existing_job = await job_repository.retrieve(id=job_id)
    if existing_job.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недостаточно прав")
    responses_from_db = await response_repository.retrieve_many(limit=limit, skip=skip)
    result = []
    for response in responses_from_db:
        if response.job_id == job_id:
            result.append(response)

    return result


@router.post("")
@inject
async def create(
    response_create_schema: ResponseCreateSchema,
    job_repository: RepositoriesContainer = Depends(Provide[RepositoriesContainer.job_repository]),
    response_repository: RepositoriesContainer = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:

    existing_job = await job_repository.retrieve(id=response_create_schema.job_id)
    if existing_job is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Указана несуществующая вакансия"
        )
    return await response_repository.create(
        ResponseSchema(
            user_id=current_user.id,
            job_id=response_create_schema.job_id,
            message=response_create_schema.message,
        )
    )


@router.put("")
@inject
async def update(
    response_update_schema: ResponseUpdateSchema,
    user_repository: RepositoriesContainer = Depends(
        Provide[RepositoriesContainer.user_repository]
    ),
    response_repository: RepositoriesContainer = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:

    existing_response = await response_repository.retrieve(id=response_update_schema.id)
    if existing_response is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Несуществующий отклик")
    existing_user = await user_repository.retrieve(id=existing_response.user_id)
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недостаточно прав")

    # try:
    response_dto = ResponseSchema(
        id=existing_response.id,
        job_id=existing_response.job_id,
        user_id=existing_response.user_id,
        message=response_update_schema.message,
    )
    updated_repository = await response_repository.update(response_update_schema.id, response_dto)
    return updated_repository

    # except ValueError:
    #    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")


@router.delete("/{id}")
@inject
async def delete(
    id: int,
    user_repository: RepositoriesContainer = Depends(
        Provide[RepositoriesContainer.user_repository]
    ),
    response_repository: RepositoriesContainer = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:

    existing_response = await response_repository.retrieve(id=id)
    if existing_response is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Несуществующий отклик")
    existing_user = await user_repository.retrieve(id=existing_response.user_id)
    if existing_user and existing_response.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недостаточно прав")
    return await response_repository.delete(id=id)
