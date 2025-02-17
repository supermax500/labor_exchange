import asyncio
from decimal import Decimal

import pytest

from tests.e2e.test_user_router import _register_new_user_and_login
from web.schemas import JobCreateSchema, JobUpdateSchema

# @pytest.fixture
# def client_app(test_app, sa_session):
#     return TestClient(test_app)


def test_get_all_jobs(client_app):
    print(f"test_job_router 15: event loop id {id(asyncio.get_event_loop())}")
    jobs_response = client_app.get("/jobs")
    assert jobs_response.status_code == 200
    print(jobs_response.json())


def test_create_get_update_and_delete_job(client_app):
    print(f"test_job_router 22: event loop id {id(asyncio.get_event_loop())}")
    email = "job18@example.com"
    password = "12345678"
    job_title = "Python jr."
    job_description = "Hiring a dev, needed skills: Postgres, Docker etc"
    job_is_active = True

    job_salary_from = 120000
    job_salary_to = 150000

    user_json, token_json = _register_new_user_and_login(client_app, email, password, name="Job Giving Man", is_company=True)
    post_result = client_app.post("/jobs", data=JobCreateSchema(title=job_title, description=job_description, is_active=job_is_active).model_dump_json(), headers={"Authorization": f"Bearer {token_json["access_token"]}"})
    new_job_json = post_result.json()
    print("new job")
    print(new_job_json)
    assert post_result.status_code == 200
    get_result = client_app.get(f"/jobs/{new_job_json["id"]}")
    job_json1 = get_result.json()
    assert get_result.status_code == 200
    assert job_json1["title"] == job_title
    assert job_json1["description"] == job_description
    with pytest.raises(Exception):
        client_app.put("/jobs/",
                       data=JobUpdateSchema(id=new_job_json["id"], salary_from=Decimal(100), salary_to=Decimal(50)).model_dump_json(),
                       headers={"Authorization": f"Bearer {token_json["access_token"]}"})

    job_update_schema = JobUpdateSchema(id=new_job_json["id"], salary_from=Decimal(job_salary_from), salary_to=Decimal(job_salary_to))
    update_result = client_app.put("/jobs/", data=job_update_schema.model_dump_json(), headers={"Authorization": f"Bearer {token_json["access_token"]}"})
    job_json2 = update_result.json()
    assert update_result.status_code == 200
    assert int(Decimal(job_json2["salary_from"])) == job_salary_from
    assert int(Decimal(job_json2["salary_to"])) == job_salary_to

    delete_result = client_app.delete(f"/jobs/{new_job_json["id"]}", headers={"Authorization": f"Bearer {token_json["access_token"]}"})
    assert delete_result.status_code == 200
    with pytest.raises(Exception):
        get_result_2 = client_app.get(f"/jobs/{new_job_json["id"]}")


