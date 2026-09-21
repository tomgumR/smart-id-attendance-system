import os

os.environ["DATABASE_URL"] = "sqlite:///./test_smart_attendance.db"
os.environ["JWT_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Role, User


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        db.add(User(username="admin", password_hash=hash_password("admin123"), role=Role.ADMIN))
        db.commit()
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_headers(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123", "role": "ADMIN"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
