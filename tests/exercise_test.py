import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
from routers import exercises  # noqa: E402
from main import app  # noqa: E402

# from database import get_db  # noqa: E402
app.include_router(exercises.router)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def test_get_all_exercises(client: TestClient):
    response = client.get("/exercise/")
    assert response.status_code == 200


def test_get_exercise_by_id(client: TestClient):
    response = client.get("/exercise/1")
    assert response.status_code == 200
