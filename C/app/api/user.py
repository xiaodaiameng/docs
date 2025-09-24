import time
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.logger import logger
from app.core.redis import get_redis_client
from app.deps.auth import get_current_user, get_db, oauth2_scheme
from app.models.user import User
from app.repositories.profile import UserProfileRepository
from app.repositories.test_record import UserTestRecordRepository
from app.repositories.user import UserRepository
from app.schemas.user import (
    UserAddTestRecordRequest,
    UserResetPasswordRequest,
    UserSetProfileRequest,
)
from app.services.auth_service import (
    authenticate_user,
    get_password_hash,
)
from app.services.token_blacklist import add_token_to_blacklist

router = APIRouter()


def get_user_profile_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> UserProfileRepository:
    return UserProfileRepository(db)


@router.post("/resetpw", tags=["user"])
async def reset_password(
    form_data: UserResetPasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    redis: Annotated[Redis, Depends(get_redis_client)],
    db: Annotated[AsyncSession, Depends(get_db)],
    token: str = Depends(oauth2_scheme),
):
    logger.info(f"用户 {current_user.username} 请求重置密码")

    # 获取用户
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # 验证旧密码
    user = await authenticate_user(user_repo, current_user.username, form_data.old_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # 修改密码
    hashed_password = get_password_hash(form_data.new_password)
    await user_repo.change_password(user, hashed_password)

    # 将当前 token 加入黑名单
    payload = jwt.decode(token, config.secret_key, algorithms=config.algorithm)
    jti = payload.get("jti")
    exp = payload.get("exp")
    now = int(time.time())
    ttl = exp - now

    logger.debug(f"将 jti {jti[-5:]} 加入到 redis 黑名单中...")
    await add_token_to_blacklist(redis, jti, ttl)

    logger.info(f"用户 {current_user.username} 登出成功，jti 已禁用")
    return {"msg": "密码重置成功，请使用新密码登录"}


@router.get("/profile", tags=["user"])
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repo)],
):
    logger.info(f"用户 {current_user.username} 请求获取个人资料")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    profile = await profile_repo.get_by_username(user.username)
    profile_data = {
        "username": user.username,
        "realname": user.realname,
        "email": user.email,
        "college": profile.college if profile else None,
        "major": profile.major if profile else None,
        "grade": profile.grade if profile else None,
    }

    logger.info(f"用户 {current_user.username} 个人资料获取成功")
    return profile_data


@router.post("/setprofile", tags=["user"])
async def set_profile(
    profile_data: UserSetProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repo)],
):
    logger.info(f"用户 {current_user.username} 请求设置个人资料")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if profile_data.email or profile_data.realname:
        await user_repo.edit_info(
            user,
            realname=profile_data.realname,
            email=profile_data.email,
        )

    if not (profile_data.college or profile_data.major or profile_data.grade):
        return {"msg": "Profile updated successfully"}

    profile = await profile_repo.get_by_username(user.username)

    # 如果已有资料则更新，否则创建新资料
    if profile:
        updated_profile = await profile_repo.update_profile(
            profile,
            college=profile_data.college,
            major=profile_data.major,
            grade=profile_data.grade,
        )
        if not updated_profile:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update profile")
    else:
        new_profile = await profile_repo.create_profile(
            user_id=user.id,
            college=profile_data.college,
            major=profile_data.major,
            grade=profile_data.grade,
        )
        if not new_profile:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create profile")

    logger.info(f"用户 {current_user.username} 个人资料设置成功")
    return {"msg": "Profile updated successfully"}


@router.get("/testrecords", tags=["user"])
async def get_test_records(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    test_name: str | None = None,
):
    logger.info(f"用户 {current_user.username} 请求获取测试记录")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    test_record_repo = UserTestRecordRepository(db)
    test_records = await test_record_repo.get_by_username(user.username, test_name=test_name)

    if not test_records:
        return {"test_records": []}

    records_data = [
        {
            "test_name": record.test_name,
            "result": record.result,
            "details": record.details,
            "created_at": record.create_time,
        }
        for record in test_records
    ]

    logger.info(f"用户 {current_user.username} 测试记录获取成功")
    return {"test_records": records_data}


@router.post("/addtestrecord", tags=["user"])
async def add_test_record(
    test_record_data: UserAddTestRecordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    logger.info(f"用户 {current_user.username} 请求添加测试记录")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    test_record_repo = UserTestRecordRepository(db)
    test_record = await test_record_repo.create_test_record(
        user_id=user.id,
        test_name=test_record_data.test_name,
        result=test_record_data.result,
        details=test_record_data.details,
    )
    if not test_record:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add test record")

    logger.info(f"用户 {current_user.username} 测试记录添加成功")
    return {"msg": "Test record added successfully"}
