import pytest
from tools.fixtures.jobs import JobFactory


@pytest.mark.asyncio
async def test_get_all_jobs(client_with_fake_db, sa_session):

    async with sa_session() as session:
        job = JobFactory.build()
        session.add(job)
        session.flush()

        jobs_response = await client_with_fake_db.get("/jobs")
        assert jobs_response.status_code == 200
