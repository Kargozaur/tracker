import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def test_create_user(client: TestClient):
    response = client.post(
        "/users/signin",
        json={
            "email": "newuser1234@example.com",
            "password": "12345678",
        },
    )
    assert response.status_code == 201


def test_unexisting_user_login(client: TestClient):
    response = client.post(
        "/users/login",
        json={"email": "someemail", "password": "somepassword"},
    )
    assert response.status_code == 422


def test_create_wrong_user(client: TestClient):
    response = client.post(
        "/users/signin", json={"email": "newuser", "pass": "1234"}
    )
    assert response.status_code == 422


@pytest.fixture
def user_token(client: TestClient):
    response = client.post(
        "/users/login",
        json={"email": "user@example.com", "password": "12345678"},
    )
    return response.json()["access_token"]


def test_user_token_fixture(user_token):
    assert isinstance(user_token, str)
    assert len(user_token) > 10
