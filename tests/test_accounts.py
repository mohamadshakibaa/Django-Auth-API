from django.contrib.auth import get_user_model

from .conftest import PASSWORD

User = get_user_model()
REGISTER_URL = "/accounts/api/v1/registration/"


def test_register_rejects_weak_password(client, db):
    response = client.post(
        REGISTER_URL,
        {
            "email": "weak@example.com",
            "password": "m@123456",
            "password2": "m@123456",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "password" in response.data


def test_register_rejects_duplicate_email_case_insensitively(client, user):
    response = client.post(
        REGISTER_URL,
        {
            "email": user.email.swapcase(),
            "password": PASSWORD,
            "password2": PASSWORD,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "email" in response.data


def test_register_normalizes_email_to_lowercase(client, db):
    response = client.post(
        REGISTER_URL,
        {
            "email": "Carol@Example.com",
            "password": PASSWORD,
            "password2": PASSWORD,
        },
        format="json",
    )

    assert response.status_code == 201
    assert User.objects.filter(email="carol@example.com").exists()


def test_me_requires_authentication(client, db):
    assert client.get("/accounts/api/v1/profile/").status_code == 401


def test_me_returns_profile_and_email_is_read_only(client, user):
    client.force_authenticate(user=user)
    assert client.get("/accounts/api/v1/profile/").data["email"] == "john@example.com"

    response = client.patch(
        "/accounts/api/v1/profile/",
        {"first_name": "Johnny", "email": "hacker@example.com"},
        format="json",
    )
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == "Johnny"
    assert user.email == "john@example.com"


def test_logout_blacklists_refresh_token(client, user):
    tokens = client.post(
        "/token/create/", {"email": user.email, "password": PASSWORD}, format="json"
    ).data

    client.force_authenticate(user=user)
    response = client.post(
        "/token/logout/", {"refresh": tokens["refresh"]}, format="json"
    )
    assert response.status_code == 204

    client.force_authenticate(user=None)
    response = client.post(
        "/token/refresh/", {"refresh": tokens["refresh"]}, format="json"
    )
    assert response.status_code == 401


def test_logout_rejects_garbage_token(client, user):
    client.force_authenticate(user=user)
    response = client.post("/token/logout/", {"refresh": "not-a-token"}, format="json")
    assert response.status_code == 400
