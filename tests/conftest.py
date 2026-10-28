import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()
PASSWORD = "StrongPass123!"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="john@example.com",
        password=PASSWORD,
        first_name="John",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email="jane@example.com",
        password=PASSWORD,
        first_name="Jane",
    )


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        email="admin@example.com",
        password=PASSWORD,
        is_staff=True,
        first_name="Admin",
    )
