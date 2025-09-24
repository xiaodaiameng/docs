from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.models.user import User
from app.repositories.user import UserRepository

client = TestClient(app)
access_token: str = ""


async def test_login(async_client, test_user: User):
    response = await async_client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    global access_token
    access_token = response.json()["access_token"]


async def test_register(async_client: AsyncClient, user_repo: UserRepository):
    response = await async_client.post(
        "/api/auth/register",
        json={
            "username": "test_register",
            "password": "test_register",
            "realname": "test_register",
            "email": "test_register@m.gduf.edu.cn",
            "role": "student",
        },
    )
    assert response.status_code == 200
    user = await user_repo.get_by_username("test_register")
    assert user is not None


async def test_logout(async_client: AsyncClient):
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    response = await async_client.post("/api/auth/logout")
    assert response.status_code == 200
    response = await async_client.post("/api/student/info")
    assert response.status_code != 200
