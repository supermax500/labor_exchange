import pytest

import storage.sqlalchemy.tables.responses
from tools.fixtures.jobs import JobFactory
from tools.fixtures.responses import ResponseFactory


def _response_orm_to_dict(response_orm: storage.sqlalchemy.tables.responses.Response) -> dict:
    return {
        "id": response_orm.id,
        "job_id": response_orm.job.id,
        "user_id": response_orm.user.id,
        "message": response_orm.message,
    }


@pytest.mark.asyncio
async def test_get_all_responses(client_with_fake_db, sa_session, current_user):
    async with sa_session() as session:
        job = JobFactory.build(user=current_user)
        response1 = ResponseFactory.build()
        response2 = ResponseFactory.build(user=current_user)
        response3 = ResponseFactory.build(job=job)
        session.add(job)
        session.add(response1)
        session.add(response2)
        session.add(response3)
        session.flush()

        responses_response = await client_with_fake_db.get("/responses")
        assert responses_response.status_code == 200
        assert len(responses_response.json()) == 2


@pytest.mark.asyncio
async def test_get_one_response(client_with_fake_db, sa_session, current_user):
    async with sa_session() as session:
        response = ResponseFactory.build(user=current_user)
        session.add(response)
        session.flush()

        user_response = await client_with_fake_db.get(f"/responses/{response.id}")
        assert user_response.status_code == 200


@pytest.mark.asyncio
async def test_get_one_response_no_perm(client_with_fake_db, sa_session):
    async with sa_session() as session:
        response = ResponseFactory.build()
        session.add(response)
        session.flush()

        user_response = await client_with_fake_db.get(f"/responses/{response.id}")
        assert user_response.status_code == 401


@pytest.mark.asyncio
async def test_get_responses_by_user_id(client_with_fake_db, sa_session, current_user):
    async with sa_session() as session:
        response = ResponseFactory.build(user=current_user)
        session.add(response)
        session.flush()

        response_response = await client_with_fake_db.get(f"/responses/users/{response.user.id}")
        assert response_response.status_code == 200


@pytest.mark.asyncio
async def test_get_responses_by_user_id_no_perm(client_with_fake_db, sa_session):
    async with sa_session() as session:
        response = ResponseFactory.build()
        session.add(response)
        session.flush()

        response_response = await client_with_fake_db.get(f"/responses/users/{response.user.id}")
        assert response_response.status_code == 401


@pytest.mark.asyncio
async def test_get_responses_by_job_id(client_with_fake_db, sa_session, current_user):
    async with sa_session() as session:
        job = JobFactory.build(user=current_user)
        response = ResponseFactory.build(job=job, user=current_user)
        session.add(job)
        session.add(response)
        session.flush()

        response_response = await client_with_fake_db.get(f"/responses/jobs/{response.job.id}")
        assert response_response.status_code == 200


@pytest.mark.asyncio
async def test_get_responses_by_job_id_no_perm(client_with_fake_db, sa_session):
    async with sa_session() as session:
        response = ResponseFactory.build()
        session.add(response)
        session.flush()

        response_response = await client_with_fake_db.get(f"/responses/jobs/{response.job.id}")
        assert response_response.status_code == 401


@pytest.mark.asyncio
async def test_post_response(client_with_fake_db, sa_session, current_user):
    async with sa_session() as session:
        job = JobFactory.build()
        session.add(job)
        session.flush()
        response = ResponseFactory.build(job=job)
        data = _response_orm_to_dict(response)
        post_response = await client_with_fake_db.post("/responses", json=data)
        assert post_response.status_code == 200


@pytest.mark.asyncio
async def test_post_response_non_existent_job(client_with_fake_db, sa_session, current_user):
    response = ResponseFactory.build()
    data = _response_orm_to_dict(response)
    post_response = await client_with_fake_db.post("/responses", json=data)
    assert post_response.status_code == 403


@pytest.mark.asyncio
async def test_put_response(client_with_fake_db, sa_session, current_user):
    async with sa_session() as session:
        response = ResponseFactory.build(user=current_user)
        session.add(response)
        session.flush()
        updated_response = ResponseFactory.build(id=response.id)
        data = _response_orm_to_dict(updated_response)
        response_update_response = await client_with_fake_db.put("/responses", json=data)
        assert response_update_response.status_code == 200


@pytest.mark.asyncio
async def test_put_response_non_existent(client_with_fake_db, sa_session, current_user):
    updated_response = ResponseFactory.build()
    data = _response_orm_to_dict(updated_response)
    response_update_response = await client_with_fake_db.put("/responses", json=data)
    assert response_update_response.status_code == 403


@pytest.mark.asyncio
async def test_put_response_no_priv(client_with_fake_db, sa_session, current_user):
    async with sa_session() as session:
        response = ResponseFactory.build()
        session.add(response)
        session.flush()
        updated_response = ResponseFactory.build(id=response.id)
        data = _response_orm_to_dict(updated_response)
        response_update_response = await client_with_fake_db.put("/responses", json=data)
        assert response_update_response.status_code == 401


@pytest.mark.asyncio
async def test_delete_response(client_with_fake_db, sa_session, current_user):
    async with sa_session() as session:
        response = ResponseFactory.build(user=current_user)
        session.add(response)
        session.flush()
        delete_response = await client_with_fake_db.delete(f"/responses/{response.id}")
        assert delete_response.status_code == 200


@pytest.mark.asyncio
async def test_delete_response_non_existent(client_with_fake_db, sa_session, current_user):
    response = ResponseFactory.build()
    delete_response = await client_with_fake_db.delete(f"/responses/{response.id}")
    assert delete_response.status_code == 403


@pytest.mark.asyncio
async def test_delete_response_no_priv(client_with_fake_db, sa_session, current_user):
    async with sa_session() as session:
        response = ResponseFactory.build()
        session.add(response)
        session.flush()
        delete_response = await client_with_fake_db.delete(f"/responses/{response.id}")
        assert delete_response.status_code == 401
