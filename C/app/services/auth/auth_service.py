from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from app.core.config import config
from app.models.user import User
from app.repositories.user import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(payload: dict | object, expires_delta: Optional[timedelta] = None) -> str:
    # 检查payload是否有to_json方法，如果有则调用它获取字典
    if hasattr(payload, 'to_json'):
        to_encode = payload.to_json().copy()
    else:
        # 假设payload是字典
        to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)

async def authenticate_user(userdb: UserRepository, username: str, password: str) -> Optional[User]:
    user = await userdb.get_by_username(username)
    if user and verify_password(password, user.password):
        return user
    return None


def generate_random_password(length: int = 8) -> str:
    """
    随机生成一个密码
    """
    import secrets
    import string
    letters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(letters) for i in range(length))
