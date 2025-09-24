from typing import Optional

from pydantic import BaseModel, Field


class UserResetPasswordRequest(BaseModel):
    """
    用户重置密码请求体
    """

    old_password: str = Field(..., min_length=6, description="旧密码，至少六位(明文)")
    """旧密码"""
    new_password: str = Field(..., min_length=6, description="新密码，至少六位(明文)")
    """新密码"""


class UserSetProfileRequest(BaseModel):
    """
    用户设置个人资料请求体
    """

    realname: Optional[str] = Field(None, description="真实姓名", examples=["沐妮卡", "萌沐"])
    """真实姓名"""
    email: Optional[str] = Field(
        None,
        description="广金邮箱",
        pattern=r"^[a-zA-Z0-9._%+-]+@m\.gduf\.edu\.cn$",
        examples=["240000000@m.gduf.edu.cn", "240000001@m.gduf.edu.cn"],
    )
    """广金邮箱"""
    college: Optional[str] = Field(None, description="学院", examples=["计算机与信息工程学院", "经济与贸易学院"])
    """学院"""
    major: Optional[str] = Field(None, description="专业", examples=["计算机科学与技术", "国际经济与贸易"])
    """专业"""
    grade: Optional[int] = Field(None, description="年级", examples=[2023, 2024])
    """年级"""


class UserAddTestRecordRequest(BaseModel):
    """
    用户添加测试记录请求体
    """

    test_name: str = Field(
        ..., min_length=1, max_length=50, description="测试名称", examples=["性格测试", "职业倾向测试"]
    )
    """测试名称"""
    result: str = Field(
        ..., min_length=1, max_length=250, description="测试结果", examples=["外向型", "适合从事金融行业"]
    )
    """测试结果"""
    details: Optional[str] = Field(
        None,
        max_length=500,
        description="测试详情",
        examples=["你是一个外向、乐观的人，喜欢与人交往。", "你适合从事金融分析、投资等工作。"],
    )
    """测试详情"""
