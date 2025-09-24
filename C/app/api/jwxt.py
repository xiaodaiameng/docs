from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.deps.auth import get_current_user, get_db
from app.models.user import User
from app.repositories.jwxt import JWXTRepository
from app.schemas.jwxt import (
    JWXTBindRequest,
    JWXTBindResponse,
    JWXTSyncResponse,
    JWXTUserInfoResponse,
)
from app.services.jwxt_service import jwxt_external_service
from app.services.password_encryption import decrypt_jwxt_password

router = APIRouter()


@router.post("/bind", response_model=JWXTBindResponse)
async def bind_jwxt_account(
    request: JWXTBindRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    绑定教务系统账号

    此接口用于将用户的教务系统账号与当前账号绑定。
    绑定过程会验证教务系统账号密码的正确性。
    """
    try:
        jwxt_repo = JWXTRepository(db)

        # 检查当前用户是否已绑定
        existing_binding = await jwxt_repo.get_binding_by_user_id(current_user.id)
        if existing_binding:
            return JWXTBindResponse(success=False, message="您已绑定教务系统账号，请先解绑后重新绑定")

        # 检查学号是否已被其他用户绑定
        is_bound = await jwxt_repo.is_student_id_bound(request.student_id)
        if is_bound:
            return JWXTBindResponse(success=False, message="该学号已被其他用户绑定")

        # 验证教务系统账号密码
        is_valid, user_data, error_msg = await jwxt_external_service.validate_and_get_user_info(
            request.student_id, request.password
        )

        if not is_valid:
            return JWXTBindResponse(success=False, message=f"教务系统验证失败: {error_msg}")

        # 创建绑定记录
        binding = await jwxt_repo.create_binding(current_user.id, request.student_id, request.password)

        # 创建用户信息记录
        if user_data:
            await jwxt_repo.create_user_info(current_user.id, request.student_id, user_data)

        # 更新绑定的同步时间
        await jwxt_repo.update_binding(binding, last_sync_time=datetime.now())

        # 提交事务
        await jwxt_repo.commit()

        logger.info(f"User {current_user.id} successfully bound JWXT account {request.student_id}")

        return JWXTBindResponse(success=True, message="绑定成功", data=user_data)

    except Exception as e:
        await jwxt_repo.rollback()
        logger.error(f"Error binding JWXT account for user {current_user.id}: {e}")

        return JWXTBindResponse(success=False, message="绑定失败，请稍后重试")


@router.post("/sync", response_model=JWXTSyncResponse)
async def sync_jwxt_info(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    从教务系统同步用户信息

    此接口用于从教务系统同步最新的用户信息。
    需要用户已绑定教务系统账号。
    """
    try:
        jwxt_repo = JWXTRepository(db)

        logger.info(f"用户 {current_user.username} 请求从教务系统同步用户信息")

        logger.debug("[1/4] 获取绑定信息")
        binding = await jwxt_repo.get_binding_by_user_id(current_user.id)
        if not binding:
            return JWXTSyncResponse(success=False, message="您尚未绑定教务系统账号，请先绑定")
        student_id = binding.student_id

        logger.debug("[2/4] 尝试登录到教务系统")
        password = decrypt_jwxt_password(binding.jwxt_password)
        if password is None:
            return JWXTSyncResponse(success=False, message="密码解密失败，请重新绑定账号")
        login_response = await jwxt_external_service.authenticate_user(student_id, password)
        if not login_response.success or not login_response.token:
            return JWXTSyncResponse(
                success=False, message=f"教务系统登录失败: {login_response.message}。请重新绑定账号"
            )
        token = login_response.token

        logger.debug("[3/4] 获取用户信息")
        response = await jwxt_external_service.get_user_info(binding.student_id, token)
        if not response.success or not response.data:
            return JWXTSyncResponse(success=False, message=f"获取用户信息失败: {response.message}")
        user_data = response.data

        logger.debug("[4/4] 更新本地数据")
        await jwxt_repo.create_user_info(current_user.id, binding.student_id, user_data)
        await jwxt_repo.update_binding(binding, last_sync_time=datetime.now())
        await jwxt_repo.commit()

        logger.info(f"User {current_user.id} successfully synced JWXT info for account {binding.student_id}")
        return JWXTSyncResponse(
            success=True,
            message="同步成功",
            data=user_data,
        )

    except Exception as e:
        logger.error(f"Error syncing JWXT info for user {current_user.id}: {e}")

        return JWXTSyncResponse(success=False, message="同步失败，请稍后重试")


@router.get("/info", response_model=JWXTUserInfoResponse)
async def get_jwxt_binding_info(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    获取教务系统绑定信息

    此接口用于获取用户的教务系统绑定状态和基本信息。
    """
    try:
        jwxt_repo = JWXTRepository(db)

        # 获取绑定信息
        binding = await jwxt_repo.get_binding_by_user_id(current_user.id)

        if not binding:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="您尚未绑定教务系统账号")

        jwxt_profiles = await jwxt_repo.get_user_info_by_user_id(current_user.id)

        if not jwxt_profiles:
            logger.warning(f"No JWXT user info found for user {current_user.id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到同步的教务系统用户信息，请先同步")

        jwxt_profile = jwxt_profiles[0]

        return JWXTUserInfoResponse(
            student_id=binding.student_id,
            student_name=jwxt_profile.realname,
            college=jwxt_profile.college,
            major=jwxt_profile.major,
            class_name=jwxt_profile.class_name,
            grade=jwxt_profile.grade,
            sync_time=binding.last_sync_time or datetime.min,
        )

    except Exception as e:
        logger.error(f"Error getting JWXT binding info for user {current_user.id}: {e}")

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取绑定信息失败")


@router.delete("/unbind", response_model=JWXTBindResponse)
async def unbind_jwxt_account(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    解绑教务系统账号

    此接口用于解绑用户的教务系统账号。
    解绑后将删除所有相关的绑定信息和同步数据。
    """
    try:
        jwxt_repo = JWXTRepository(db)

        # 检查绑定是否存在
        binding = await jwxt_repo.get_binding_by_user_id(current_user.id)
        if not binding:
            return JWXTBindResponse(success=False, message="您尚未绑定教务系统账号")

        # 删除绑定（级联删除相关数据）
        await jwxt_repo.delete_binding(binding)
        await jwxt_repo.commit()

        logger.info(f"User {current_user.id} successfully unbound JWXT account {binding.student_id}")

        return JWXTBindResponse(success=True, message="解绑成功")

    except Exception as e:
        await jwxt_repo.rollback()
        logger.error(f"Error unbinding JWXT account for user {current_user.id}: {e}")

        return JWXTBindResponse(success=False, message="解绑失败，请稍后重试")
