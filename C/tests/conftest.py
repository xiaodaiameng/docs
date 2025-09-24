from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest_asyncio
from database import close_db, get_db, init_test_db
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.sql import get_db as get_sql_db
from app.main import app
from app.models.user import User, UserRole
from app.repositories.profile import UserProfileRepository
from app.repositories.test_record import UserTestRecordRepository
from app.repositories.user import UserRepository
from app.services.authenticate_service import get_password_hash


@pytest_asyncio.fixture(scope="session")
async def database() -> AsyncGenerator[AsyncSession, None]:
    await init_test_db()
    try:
        async for db in get_db():
            yield db
    finally:
        await close_db()  # type:ignore


@pytest_asyncio.fixture
async def async_client(database: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield database

    app.dependency_overrides[get_sql_db] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_repo(database: AsyncSession) -> UserRepository:
    repo = UserRepository(database)
    return repo


@pytest_asyncio.fixture
async def profile_repo(database: AsyncSession) -> UserProfileRepository:
    return UserProfileRepository(database)


@pytest_asyncio.fixture
async def test_record_repo(database: AsyncSession) -> UserTestRecordRepository:
    return UserTestRecordRepository(database)


@pytest_asyncio.fixture
async def test_user(user_repo: UserRepository) -> User:
    uuid = str(uuid4())
    hashed_password = get_password_hash("123456")
    user = await user_repo.create_user(
        username=f"test_{uuid}",
        password=hashed_password,
        realname="Test User",
        email=f"test_{uuid}@m.gduf.edu.cn",
        role=UserRole.student,
    )
    assert user
    return user


@pytest_asyncio.fixture
async def test_admin(user_repo: UserRepository) -> User:
    hashed_password = get_password_hash("123456")
    admin = await user_repo.create_user(
        username="test_admin",
        password=hashed_password,
        realname="Test User",
        email="test_admin@m.gduf.edu.cn",
        role=UserRole.admin,
    )
    assert admin
    return admin


@pytest_asyncio.fixture
async def admin_client(async_client: AsyncClient, test_admin: User) -> AsyncClient:
    response = await async_client.post(
        "/api/auth/login",
        data={"username": test_admin.username, "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client


@pytest_asyncio.fixture
async def student_client(async_client: AsyncClient, test_user: User) -> AsyncClient:
    response = await async_client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client


@pytest_asyncio.fixture
async def teacher_client(async_client: AsyncClient, test_teacher: User) -> AsyncClient:
    response = await async_client.post(
        "/api/auth/login",
        data={"username": test_teacher.username, "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client
