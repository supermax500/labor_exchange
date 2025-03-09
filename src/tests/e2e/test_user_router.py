import pytest
from faker.proxy import Faker

import storage.sqlalchemy.tables.users
from tools.fixtures.users import UserFactory


def _user_orm_to_dict(user_orm: storage.sqlalchemy.tables.users.User) -> dict:
    return {
        "id": user_orm.id,
        "name": user_orm.name,
        "email": user_orm.email,
        "is_company": user_orm.is_company,
    }


@pytest.mark.asyncio
async def test_get_all_users(client_with_fake_db, sa_session):
    async with sa_session() as session:
        user1 = UserFactory.build(is_company=False)
        user2 = UserFactory.build(is_company=False)
        company1 = UserFactory.build(is_company=True)
        company2 = UserFactory.build(is_company=True)
        company3 = UserFactory.build(is_company=True)
        session.add(user1)
        session.add(user2)
        session.add(company1)
        session.add(company2)
        session.add(company3)
        session.flush()

        users_response = await client_with_fake_db.get("/users")
        assert users_response.status_code == 200
        assert len(users_response.json()) == 3


@pytest.mark.asyncio
async def test_get_one_user(client_with_fake_db, sa_session):
    async with sa_session() as session:
        user = UserFactory.build(is_company=True)
        session.add(user)
        session.flush()

        user_response = await client_with_fake_db.get(f"/users/{user.id}")
        assert user_response.status_code == 200


@pytest.mark.asyncio
async def test_get_one_user_no_perm(client_with_fake_db, sa_session):
    async with sa_session() as session:
        user = UserFactory.build(is_company=False)
        session.add(user)
        session.flush()

        user_response = await client_with_fake_db.get(f"/users/{user.id}")
        assert user_response.status_code == 401


@pytest.mark.asyncio
async def test_register_user(client_with_fake_db, sa_session):
    user = UserFactory.build()
    password = Faker().password()
    data = _user_orm_to_dict(user)
    data.update({"password": password, "password2": password})
    post_response = await client_with_fake_db.post("/users", json=data)
    assert post_response.status_code == 200


@pytest.mark.asyncio
async def test_put_user(client_with_fake_db, sa_session, current_user, access_token):
    updated_user = UserFactory.build(id=current_user.id)
    user_update_response = await client_with_fake_db.put(
        "/users",
        json=_user_orm_to_dict(updated_user),
        headers={"Authorization": f"{access_token.token_type} {access_token.access_token}"},
    )
    assert user_update_response.status_code == 200


@pytest.mark.asyncio
async def test_put_user_no_priv(client_with_fake_db, sa_session, current_user, access_token):
    async with sa_session() as session:
        user = UserFactory.build()
        session.add(user)
        session.flush()
        updated_user = UserFactory.build(email=user.email)
        user_update_response = await client_with_fake_db.put(
            "/users",
            json=_user_orm_to_dict(updated_user),
            headers={"Authorization": f"{access_token.token_type} {access_token.access_token}"},
        )
        assert user_update_response.status_code == 401
