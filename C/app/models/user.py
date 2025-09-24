import enum
from datetime import datetime

import sqlalchemy
from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.sql import Base



class UserRole(str, enum.Enum):
    student = "student"
    admin = "admin"


class User(Base):
    __tablename__ = "users"  # 表名

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    username: Mapped[str] = mapped_column(String(12), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(100), nullable=False, comment="密码(密文)")
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, comment="角色(ADMIN/TEACHER/STUDENT)", default=UserRole.student
    )
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="状态(正常/禁用)")

    realname: Mapped[str] = mapped_column(String(10), nullable=False, comment="真实姓名")
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="邮箱")

    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        comment="创建时间",
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
        comment="更新时间",
    )
