import pytest
from pydantic import EmailStr

import json
from web.schemas import UserCreateSchema, LoginSchema


def test_example(client_app):
    email = "user5@example.com"
    password = "12345678"

    user, token = _register_new_user_and_login(client_app, email, password, name="User 11", is_company=False)

    #response = client_app.get(url="/users/" + str(1), headers={"Authorization": f"Bearer {token.access_token}"})
    #print(response.json)
    #assert response.status_code == 200


def _register_new_user_and_login(client_app, email, password, **kwargs):
    user_create_schema = UserCreateSchema(email=email, password=password, password2=password, **kwargs)
    response_user = client_app.post(url="/users", data=user_create_schema.model_dump_json())
    response_token_schema = client_app.post("/auth", data=LoginSchema(email=email, password=password).model_dump_json())
    return response_user, response_token_schema

# @pytest.fixture
# def auth_token(client_app):
#     data = {"email": EmailStr(), "password": }
