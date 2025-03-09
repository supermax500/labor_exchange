import pytest
from sqlalchemy.orm.persistence import delete_obj

import storage.sqlalchemy.tables.jobs
from tools.fixtures.jobs import JobFactory
from web.routers.job import delete


def _job_orm_to_dict(job_orm: storage.sqlalchemy.tables.jobs.Job) -> dict:
    return {
        "id": job_orm.id,
        "user_id": job_orm.user.id,
        "title": job_orm.title,
        "description": job_orm.description,
        "salary_from": job_orm.salary_from,
        "salary_to": job_orm.salary_to,
        "is_active": job_orm.is_active,
    }


@pytest.mark.asyncio
async def test_get_all_jobs(client_with_fake_db, sa_session):
    async with sa_session() as session:
        job = JobFactory.build()
        session.add(job)
        session.flush()

        jobs_response = await client_with_fake_db.get("/jobs")
        assert jobs_response.status_code == 200


@pytest.mark.asyncio
async def test_get_one_job(client_with_fake_db, sa_session):
    async with sa_session() as session:
        job = JobFactory.build()
        session.add(job)
        session.flush()

        job_response = await client_with_fake_db.get(f"/jobs/{job.id}")
        assert job_response.status_code == 200


@pytest.mark.asyncio
async def test_post_good_job(client_with_fake_db, sa_session):
    job = JobFactory.build(salary_from=100, salary_to=200)
    post_response = await client_with_fake_db.post("/jobs", json=_job_orm_to_dict(job))
    assert post_response.status_code == 200


@pytest.mark.asyncio
async def test_post_bad_job(client_with_fake_db, sa_session):
    job = JobFactory.build(salary_from=300, salary_to=200)
    post_response = await client_with_fake_db.post("/jobs", json=_job_orm_to_dict(job))
    assert post_response.status_code == 422


@pytest.mark.asyncio
async def test_put_job(client_with_fake_db, sa_session, current_user, access_token):
    async with sa_session() as session:
        job = JobFactory.build(user=current_user, salary_from=100, salary_to=200)
        session.add(job)
        session.flush()

        updated_job = JobFactory.build(id=job.id, salary_from=300, salary_to=500)
        job_update_response = await client_with_fake_db.put("/jobs", json=_job_orm_to_dict(updated_job), headers={"Authorization": f"{access_token.token_type} {access_token.access_token}"})
        assert job_update_response.status_code == 200


@pytest.mark.asyncio
async def test_put_job_no_exist(client_with_fake_db, sa_session, current_user, access_token):
    job = JobFactory.build()
    nonexistent_id = job.id
    job = JobFactory.build(id=nonexistent_id, user=current_user, salary_from=100, salary_to=200)
    job_update_response = await client_with_fake_db.put("/jobs", json=_job_orm_to_dict(job), headers={"Authorization": f"{access_token.token_type} {access_token.access_token}"})
    assert job_update_response.status_code == 403


@pytest.mark.asyncio
async def test_put_job_no_priv(client_with_fake_db, sa_session, current_user, access_token):
    async with sa_session() as session:
        job = JobFactory.build(salary_from=100, salary_to=200)
        session.add(job)
        session.flush()

        updated_job = JobFactory.build(id=job.id, salary_from=300, salary_to=500)
        job_update_response = await client_with_fake_db.put("/jobs", json=_job_orm_to_dict(updated_job), headers={"Authorization": f"{access_token.token_type} {access_token.access_token}"})
        assert job_update_response.status_code == 403


@pytest.mark.asyncio
async def test_delete_job(client_with_fake_db, sa_session, current_user, access_token):
    async with sa_session() as session:
        job = JobFactory.build(user=current_user, salary_from=100, salary_to=200)
        session.add(job)
        session.flush()

        delete_response = await client_with_fake_db.delete(f"/jobs/{job.id}", headers={"Authorization": f"{access_token.token_type} {access_token.access_token}"})
        assert delete_response.status_code == 200


@pytest.mark.asyncio
async def test_delete_job_no_exist(client_with_fake_db, sa_session, current_user, access_token):
    job = JobFactory.build(user=current_user, salary_from=100, salary_to=200)

    delete_response = await client_with_fake_db.delete(f"/jobs/{job.id}", headers={"Authorization": f"{access_token.token_type} {access_token.access_token}"})
    assert delete_response.status_code == 403


@pytest.mark.asyncio
async def test_delete_job_no_priv(client_with_fake_db, sa_session, current_user, access_token):
    async with sa_session() as session:
        job = JobFactory.build(salary_from=100, salary_to=200)
        session.add(job)
        session.flush()

        delete_response = await client_with_fake_db.delete(f"/jobs/{job.id}", headers={"Authorization": f"{access_token.token_type} {access_token.access_token}"})
        assert delete_response.status_code == 401

