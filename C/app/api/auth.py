import asyncio
import os
import time
import uuid
from datetime import datetime, timedelta
import redis
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

# 前端目录路径定义
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")

from app.core.config import config
from app.core.logger import logger
from app.core.redis import get_redis_client
from app.deps.auth import oauth2_scheme, get_current_user  # 确保该依赖已实现用户认证
from app.deps.sql import get_db
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.auth import Payload, RegisterRequest
from app.services.auth.auth_service import authenticate_user, create_access_token, get_password_hash
from app.services.auth.token_blacklist import add_token_to_blacklist

router = APIRouter()


@router.post("/logout")
async def logout(
        token: str = Depends(oauth2_scheme),
        redis: Redis = Depends(get_redis_client),
        current_user: User = Depends(get_current_user)
):
    try:
        payload_dict = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        payload = Payload(**payload_dict)
        current_timestamp = datetime.timestamp(datetime.now())
        expires_in = int(payload.exp - current_timestamp)
        if expires_in > 0:
            await add_token_to_blacklist(redis, payload.jti, expires_in)
            logger.info(f"用户 {current_user.username} 登出，令牌 {payload.jti} 已加入黑名单")
        else:
            logger.info(f"用户 {current_user.username} 登出，令牌已过期")
        return {"msg": "登出成功"}
    except Exception as e:
        logger.error(f"登出失败：{str(e)}")
        raise HTTPException(status_code=500, detail="登出失败")

@router.post("/login", tags=["auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    logger.info(f"收到登录请求: {form_data.username}")

    repo = UserRepository(db)
    user = await authenticate_user(repo, form_data.username, form_data.password)

    if not user:
        logger.warning(f"用户 {form_data.username} 不存在或密码错误，抛出 401")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"为用户 {form_data.username} 创建 access_token ...")
    access_token_expires = timedelta(minutes=config.expire_minutes)
    access_token = create_access_token(payload=Payload(sub=user.username), expires_delta=access_token_expires)

    logger.info(f"用户 {form_data.username} 登录成功, 密钥后五位 {access_token[-5:]}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", tags=["auth"])
async def register(register_request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    logger.info(f"收到注册请求: {register_request.username}")

    repo = UserRepository(db)

    existing_user = await repo.get_by_username(register_request.username)
    if existing_user:
        logger.warning(f"用户名 {register_request.username} 已存在，抛出 400")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    existing_email = await repo.get_by_email(register_request.email)
    if existing_email:
        logger.warning(f"邮箱 {register_request.email} 已存在，抛出 400")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(register_request.password)

    try:
        await repo.create_user(
            username=register_request.username,
            realname=register_request.realname,
            email=register_request.email,
            password=hashed_password,
            role=UserRole(register_request.role or "student"),
        )
    except IntegrityError as e:
        logger.error(f"注册用户 {register_request.username} 失败: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或邮箱已存在")

    logger.info(f"用户 {register_request.username} 注册成功")
    return {"msg": "User registered successfully"}


@router.get("/register")
async def register_page():
    # 先检查是否存在Vue构建后的应用
    vue_dist_dir = os.path.join(FRONTEND_DIR, "金融就业服务系统", "finance-employment", "dist")
    index_file = os.path.join(vue_dist_dir, "index.html")
    
    if os.path.exists(index_file):
        # 如果存在Vue构建后的应用，返回index.html，由Vue Router处理/register路由
        return FileResponse(index_file)
    else:
        # 否则尝试返回原有的register.html
        register_file = os.path.join(FRONTEND_DIR, "register.html")
        if os.path.exists(register_file):
            return FileResponse(register_file)
        else:
            return JSONResponse({
                "message": "注册文件未找到",
                "hint": "请确保已构建Vue应用或register.html文件在frontend目录中"
            })

# 用户仪表盘数据接口

