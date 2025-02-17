import pytest

from web.schemas import UserCreateSchema, LoginSchema, UserUpdateSchema


def test_example(client_app):
    email = "user22@example.com"
    password = "12345678"

    user_response, token_response = _register_new_user_and_login(client_app, email, password, name="User 11", is_company=False)

    #response = client_app.get(url="/users/" + str(1), headers={"Authorization": f"Bearer {token.access_token}"})
    #print(response.json)
    #assert response.status_code == 200


def _register_new_user_and_login(client_app, email, password, **kwargs):
    user_create_schema = UserCreateSchema(email=email, password=password, password2=password, **kwargs)
    response_user = client_app.post(url="/users", data=user_create_schema.model_dump_json())
    response_token_schema = client_app.post("/auth", data=LoginSchema(email=email, password=password).model_dump_json())
    user_json = response_user.json()
    token_json = response_token_schema.json()
    return user_json, token_json


def test_get_and_update_user(client_app):
    email = "user21@example.com"
    password = "12345678"
    user_json, token_json = _register_new_user_and_login(client_app, email, password, name="User 121", is_company=False)
    #print(user_json)
    get_result = client_app.get("/users/" + str(user_json["id"]), headers={"Authorization": f"Bearer {token_json["access_token"]}"})
    #print(get_result)
    assert get_result.status_code == 200
    update_result = client_app.put("/users/",
                                   data=UserUpdateSchema(name="New Updated Name").model_dump_json(),
                                   headers={"Authorization": f"Bearer {token_json["access_token"]}"})
    #print(update_result)
    assert update_result.status_code == 200


# def test_delete_other_and_self(client_app):
#     email = "shouldnotexist_2@example.com"
#     password = "<PASSWORD>"
#     user_json, token_json = _register_new_user_and_login(client_app, email, password, name="Mr. Deletable", is_company=False)
#     #with pytest.raises(Exception) as e:
#     #    client_app.delete("/users/0")
#     print("self id =", user_json["id"])
#
#     client_app.delete("/users/0")
#
#     client_app.delete("/users/" + str(user_json["id"]))
#     # интересно, а что случится с сессией? пользователь-то удален, что случится с токеном?






# @pytest.fixture
# def auth_token(client_app):
#     data = {"email": EmailStr(), "password": }
