from dataclasses import asdict, dataclass, field
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


"""数据模型定义模块，该 schemas/auth.py文件定义了三个核心数据模型"""

class Token(BaseModel):
    """
    jwt 密钥（或者说令牌）实体
    """
    access_token: str
    token_type: str

# 导入定义内部业务层的数据模型，简化类的定义
@dataclass
class Payload:
    """
    jwt 的载荷结构，以下 sub，exp，jti都是 jwt标准字段
    """

    sub: str
    """令牌所属用户名"""

    exp: Optional[int] = None
    """令牌过期时间"""

    jti: str = field(default_factory=lambda: uuid4().hex)# 通过 uuid4().hex生成唯一 UUID
    """JWT ID 令牌"""

    def to_json(self):
        return asdict(self)


class RegisterRequest(BaseModel):
    """
    注册请求体，前端传入的注册数据必须符合此模型定义，否则直接返回错误
    """

    #                  ... 表示非空
    username: str = Field(..., description="用户名", examples=["Muika", "Moemu"])
    """用户名"""

    realname: str = Field(..., description="真实姓名", examples=["沐妮卡", "萌沐"])
    """真实姓名"""

    email: str = Field(
        ...,
        description="广金邮箱",
        pattern=r"^[a-zA-Z0-9._%+-]+@m\.gduf\.edu\.cn$",
        examples=["240000000@m.gduf.edu.cn"],
    )
    """广金邮箱"""

    password: str = Field(..., min_length=6, description="密码，至少六位(明文)")
    """密码"""

    role: str = Field(default="student", description="用户角色，默认为 student", examples=["student", "admin"])
    """用户角色"""
