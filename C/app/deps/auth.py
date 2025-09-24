from datetime import datetime
from typing import Annotated, Callable, Coroutine

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.logger import logger
from app.core.redis import get_redis_client
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.auth import Payload
from app.services.auth.token_blacklist import is_token_blacklisted

from .sql import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

"""认证函数 get_current_user()
这是一个依赖项函数（核心作用是解耦代码、复用逻辑、简化路由实现）
流程： 解码令牌 -> 解码结果转为 payload实例对象 -> 验证信息 -> 返回验证结果"""
async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
    redis: Annotated[Redis, Depends(get_redis_client)],) -> User:

    logger.debug("尝试鉴权已登录用户...")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload_dict = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        payload = Payload(**payload_dict)
        if (
            (payload.sub is None or payload.exp is None)
            or payload.exp < datetime.timestamp(datetime.now())
            or await is_token_blacklisted(redis, payload.jti)
        ):
            logger.warning("用户鉴权失败，用户可能没有设置密钥体或密钥过期")
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        logger.warning("用户鉴权失败，用户使用的 jwt 已过期")
        raise credentials_exception

    except InvalidTokenError:
        logger.warning("用户鉴权失败，用户使用了无效的 jwt")
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get_by_username(payload.sub)

    if not user or not user.status:
        logger.warning("用户鉴权失败，尝试登录的用户不存在或已被禁用")
        raise credentials_exception

    logger.debug(f"鉴权成功: 登录用户 {user.username}")
    return user


# 角色权限检查函数
def check_and_get_current_role(
    role: UserRole,
) -> Callable[..., Coroutine[None, None, User]]:

    async def wrapper(
        db: Annotated[AsyncSession, Depends(get_db)],
        token: Annotated[str, Depends(oauth2_scheme)],
        redis: Annotated[Redis, Depends(get_redis_client)],
    ) -> User:

        user = await get_current_user(db, token, redis)
        if user.role != role:
            logger.warning("用户鉴权失败，所登录的用户没有响应的权限")
            raise HTTPException(status_code=403, detail="Permission denied")
        return user

    return wrapper
