import pytest
from starlette.exceptions import HTTPException

from tests.e2e.test_user_router import _register_new_user_and_login
from web.schemas import JobCreateSchema, ResponseCreateSchema, ResponseUpdateSchema


def test_get_all_responses(client_app):
    email = "response_checker4@example.com"
    password = "12345678"
    user_json, token_json = _register_new_user_and_login(client_app, email, password, name="Response Bot", is_company=False)

    responses_response = client_app.get("/responses", headers={"Authorization": f"Bearer {token_json["access_token"]}"})
    assert responses_response.status_code == 200
    print(responses_response.json())


def test_create_get_update_and_delete_response(client_app):
    email = "response_bot10@example.com"
    password = "12345678"
    job_create_schema = JobCreateSchema(title="Example Job", description="Example Job Description")
    response_message = "Test message"
    response_updated_message = "Updated message"

    user_json, token_json = _register_new_user_and_login(client_app, email, password, name="Job Giving Man", is_company=True)
    sample_job = _create_job(client_app, job_create_schema, token_json["access_token"])

    post_result = client_app.post("/responses", data=ResponseCreateSchema(job_id=sample_job["id"], message=response_message).model_dump_json(), headers={"Authorization": f"Bearer {token_json["access_token"]}"})
    new_response_json = post_result.json()
    print("new response")
    print(new_response_json)
    assert post_result.status_code == 200
    get_result = client_app.get(f"/responses/{new_response_json["id"]}", headers={"Authorization": f"Bearer {token_json["access_token"]}"})
    response_json_after_creation = get_result.json()
    assert get_result.status_code == 200
    assert response_json_after_creation["user_id"] == user_json["id"]
    assert response_json_after_creation["job_id"] == sample_job["id"]

    update_result = client_app.put("/responses/", data=ResponseUpdateSchema(id=new_response_json["id"], message=response_updated_message).model_dump_json(), headers={"Authorization": f"Bearer {token_json["access_token"]}"})
    updated_response_json = update_result.json()
    assert update_result.status_code == 200
    assert updated_response_json["message"] == response_updated_message

    delete_result = client_app.delete(f"/responses/{new_response_json["id"]}", headers={"Authorization": f"Bearer {token_json["access_token"]}"})
    assert delete_result.status_code == 200
    #with pytest.raises(Exception):
    get_result_2 = client_app.get(f"/responses/{new_response_json["id"]}")
        # assert get_result_2.status_code == 404


def _create_job(client_app, job_create_dto, token):
    created_job_response = client_app.post("/jobs", data=job_create_dto.model_dump_json(), headers={"Authorization": f"Bearer {token}"})
    return created_job_response.json()