from dataclasses import asdict

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_current_user
from dependencies.containers import RepositoriesContainer
from models import User
from repositories import UserRepository
from tools.security import hash_password
from web.schemas import UserCreateSchema, UserSchema, UserUpdateSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
@inject
async def read_users(
    limit: int = 100,
    skip: int = 0,
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
    current_user: User = Depends(get_current_user),
) -> list[UserSchema]:
    users_model = await user_repository.retrieve_many(limit, skip)

    users_schema = []
    for model in users_model:
        if model.id != current_user.id and model.is_company == False:
            continue
        users_schema.append(
            UserSchema(
                id=model.id,
                name=model.name,
                email=model.email,
                is_company=model.is_company,
            )
        )
    return users_schema


@router.get("/{user_id}")
@inject
async def read_user(
    user_id: int,
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недостаточно прав")
    user_model = await user_repository.retrieve(id=user_id)

    return UserSchema(
        id=user_model.id,
        name=user_model.name,
        email=user_model.email,
        is_company=user_model.is_company,
    )


@router.post("")
@inject
async def create_user(
    user_create_dto: UserCreateSchema,
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
) -> UserSchema:
    print(user_repository.session)
    user = await user_repository.create(
        user_create_dto, hashed_password=hash_password(user_create_dto.password)
    )
    return UserSchema(**asdict(user))


@router.put("")
@inject
async def update_user(
    user_update_schema: UserUpdateSchema,
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
    current_user: User = Depends(get_current_user),
) -> UserSchema:

    existing_user = await user_repository.retrieve(email=user_update_schema.email)
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недостаточно прав")

    try:
        updated_user = await user_repository.update(current_user.id, user_update_schema)
        return UserSchema(**asdict(updated_user))

    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

