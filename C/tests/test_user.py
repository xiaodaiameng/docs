from httpx import AsyncClient

from app.models.user import User
from app.repositories.profile import UserProfileRepository
from app.repositories.test_record import UserTestRecordRepository
from app.repositories.user import UserRepository


async def test_reset_password(student_client: AsyncClient, test_user: User):
    # Test with correct old password
    response = await student_client.post(
        "/api/user/resetpw",
        json={"old_password": "123456", "new_password": "newpassword"},
    )

    assert response.status_code == 200

    response = await student_client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": "newpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200


async def test_update_profile(
    student_client: AsyncClient, test_user: User, user_repo: UserRepository, profile_repo: UserProfileRepository
):
    response = await student_client.post(
        "/api/user/setprofile",
        json={
            "college": "计算机与信息工程学院",
            "major": "计算机科学与技术",
            "grade": 2024,
            "realname": "测试用户",
            "email": "test@m.gduf.edu.cn",
        },
    )
    assert response.status_code == 200

    user = await user_repo.get_by_username(test_user.username)
    assert user is not None
    assert user.email == "test@m.gduf.edu.cn"
    assert user.realname == "测试用户"

    profile = await profile_repo.get_by_username(test_user.username)
    assert profile is not None
    assert profile.college == "计算机与信息工程学院"
    assert profile.major == "计算机科学与技术"
    assert profile.grade == 2024


async def test_get_profile(student_client: AsyncClient, test_user: User, profile_repo: UserProfileRepository):
    response = await student_client.get("/api/user/profile")
    assert response.status_code == 200
    data = response.json()

    assert data["username"] == test_user.username
    assert data["realname"] == test_user.realname
    assert data["email"] == test_user.email

    profile = await profile_repo.get_by_username(test_user.username)
    if profile:
        assert data["college"] == profile.college
        assert data["major"] == profile.major
        assert data["grade"] == profile.grade
    else:
        assert data["college"] is None
        assert data["major"] is None
        assert data["grade"] is None


async def test_add_test_record(
    student_client: AsyncClient, test_user: User, test_record_repo: UserTestRecordRepository
):
    response = await student_client.post(
        "/api/user/addtestrecord",
        json={"test_name": "性格测试", "result": "外向型", "details": "你是一个外向、乐观的人，喜欢与人交往。"},
    )
    assert response.status_code == 200

    records = await test_record_repo.get_by_username(test_user.username, "性格测试")
    assert records is not None
    assert len(records) > 0
    record = records[0]
    assert record.test_name == "性格测试"
    assert record.result == "外向型"
    assert record.details == "你是一个外向、乐观的人，喜欢与人交往。"


async def test_get_test_records(
    student_client: AsyncClient, test_user: User, test_record_repo: UserTestRecordRepository
):
    # First, add a test record
    await test_record_repo.create_test_record(
        user_id=test_user.id,
        test_name="职业倾向测试",
        result="适合从事金融行业",
        details="你适合从事金融分析、投资等工作。",
    )

    response = await student_client.get("/api/user/testrecords", params={"test_name": "职业倾向测试"})
    assert response.status_code == 200
    data = response.json()
    assert "test_records" in data
    assert len(data["test_records"]) > 0
    record = data["test_records"][0]
    assert record["test_name"] == "职业倾向测试"
    assert record["result"] == "适合从事金融行业"
    assert record["details"] == "你适合从事金融分析、投资等工作。"
