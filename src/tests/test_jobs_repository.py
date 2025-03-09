from decimal import Decimal

import pytest

from storage.sqlalchemy.tables import Response
from tools.fixtures.jobs import JobFactory
from web.schemas import JobCreateSchema, JobUpdateSchema


@pytest.mark.asyncio
async def test_get_all(job_repository, sa_session):
    async with sa_session() as session:
        job = JobFactory.build()
        session.add(job)
        session.flush()

    all_jobs = await job_repository.retrieve_many()
    assert all_jobs

    job_from_repo = all_jobs[0]
    assert job_from_repo.title == job.title
    assert job_from_repo.description == job.description
    assert job_from_repo.salary_from == job.salary_from
    assert job_from_repo.salary_to == job.salary_to
    assert job_from_repo.is_active == job.is_active


@pytest.mark.asyncio
async def test_get_all_with_relations(job_repository, sa_session):
    async with sa_session() as session:
        job = JobFactory.build(is_active=True)
        response = Response(job_id=job.id)
        session.add(job)
        session.add(response)
        session.flush()

    all_jobs = await job_repository.retrieve_many(include_relations=True)
    assert all_jobs
    # assert len(all_jobs) > 1

    job_from_repo = all_jobs[0]
    # assert len(job_from_repo.jobs) == 1
    assert job_from_repo.responses[0].id == response.id
    assert job_from_repo.id == job.id
    assert job_from_repo.user_id == job.user_id
    assert job_from_repo.title == job.title
    assert job_from_repo.salary_from == job.salary_from


@pytest.mark.asyncio
async def test_get_by_id(job_repository, sa_session):
    async with sa_session() as session:
        job = JobFactory.build()
        session.add(job)
        session.flush()

    current_job = await job_repository.retrieve(id=job.id)
    assert current_job is not None
    assert current_job.id == job.id


@pytest.mark.asyncio
async def test_create(job_repository, sa_session, user_repository):
    all_users = await user_repository.retrieve_many(include_relations=True)
    user_id = all_users[0].id
    job = JobCreateSchema(
        user_id=user_id,
        title="VakBelyash",
        salary_from=100000,
        salary_to=120000,
        is_active=False,
    )

    created_job = await job_repository.create(job_create_dto=job)
    assert created_job is not None
    assert created_job.user_id == user_id
    assert created_job.title == "VakBelyash"


@pytest.mark.asyncio
async def test_create_bad_salary(job_repository, sa_session, user_repository):
    all_users = await user_repository.retrieve_many(include_relations=True)
    user_id = all_users[0].id

    with pytest.raises(ValueError):
        JobCreateSchema(
            user_id=user_id,
            title="VakBelyash",
            salary_from=100000,
            salary_to=10000,
            is_active=False,
        )
    # created_job = await job_repository.create(job_create_dto=job)
    # assert created_job is not None
    # assert created_job.user_id == user_id
    # assert created_job.title == "VakBelyash"


@pytest.mark.asyncio
async def test_update(job_repository, sa_session):
    async with sa_session() as session:
        job = JobFactory.build()
        session.add(job)
        session.flush()

    job_update_dto = JobUpdateSchema(title="New Title")
    updated_job = await job_repository.update(id=job.id, job_update_dto=job_update_dto)
    assert job.id == updated_job.id
    assert updated_job.title == "New Title"


@pytest.mark.asyncio
async def test_update_bad_salary(job_repository, sa_session):
    async with sa_session() as session:
        job = JobFactory.build(salary_from=Decimal(10000))
        session.add(job)
        session.flush()

    job_update_dto = JobUpdateSchema(title="New Title 2", salary_to=Decimal(8000))
    updated_job = await job_repository.update(id=job.id, job_update_dto=job_update_dto)
    assert job.id == updated_job.id
    assert updated_job.title == "New Title 2"


@pytest.mark.asyncio
async def test_delete(job_repository, sa_session):
    async with sa_session() as session:
        job = JobFactory.build()
        session.add(job)
        session.flush()

    await job_repository.delete(id=job.id)
    res = await job_repository.retrieve(id=job.id)
    assert res is not None
