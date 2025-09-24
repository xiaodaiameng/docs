from datetime import datetime
from typing import Any, Optional, TypedDict

from pydantic import BaseModel, Field


class JWXTUserInfoAPIResponse(TypedDict):
    fxzy: str
    xh: str
    xm: str
    dqszj: str
    usertype: str
    yxmc: str
    xz: int
    bj: str
    dh: Optional[Any]
    email: Optional[str]
    rxnf: str
    xb: str
    ksh: str
    nj: str
    qq: Optional[str]
    zymc: str


class JWXTBindRequest(BaseModel):
    """JWXT绑定请求"""

    student_id: str = Field(..., min_length=1, max_length=20, description="学号", examples=["241500000"])
    password: str = Field(..., min_length=1, description="教务系统密码")


class JWXTBindResponse(BaseModel):
    """JWXT绑定响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[JWXTUserInfoAPIResponse] = Field(default=None, description="返回数据")


class JWXTSyncResponse(BaseModel):
    """JWXT同步响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[JWXTUserInfoAPIResponse] = Field(default=None, description="用户信息数据")
    updated_fields: Optional[list] = Field(default=None, description="更新的字段列表")


class JWXTUserInfoResponse(BaseModel):
    """JWXT用户信息响应"""

    student_id: str = Field(..., description="学号")
    student_name: Optional[str] = Field(None, description="学生姓名")
    college: Optional[str] = Field(None, description="学院")
    major: Optional[str] = Field(None, description="专业")
    class_name: Optional[str] = Field(None, description="班级")
    grade: Optional[str] = Field(None, description="年级")
    sync_time: datetime = Field(..., description="同步时间")


class JWXTBindingInfoResponse(BaseModel):
    """JWXT绑定信息响应"""

    is_bound: bool = Field(..., description="是否已绑定")
    student_id: Optional[str] = Field(None, description="学号")
    sync_count: int = Field(0, description="同步次数")
    bind_time: Optional[datetime] = Field(None, description="绑定时间")
    should_sync: bool = Field(False, description="是否建议同步")


class JWXTExternalLoginResponse(BaseModel):
    """外部教务系统登录响应"""

    token: Optional[str] = Field(None, description="登录token")
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")


class JWXTExternalUserInfoResponse(BaseModel):
    """外部教务系统用户信息响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[JWXTUserInfoAPIResponse] = Field(None, description="用户信息原始数据")
