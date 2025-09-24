from datetime import datetime
from typing import Optional

import sqlalchemy
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.sql import Base


class JWXTBinding(Base):
    """教务系统绑定信息表"""

    __tablename__ = "jwxt_binding"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True, comment="用户ID"
    )
    student_id: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, comment="学号")
    jwxt_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="教务系统密码(加密)")

    last_sync_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="最后同步时间")
    sync_count: Mapped[int] = mapped_column(Integer, default=0, comment="同步次数")

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


class JWXTUserInfo(Base):
    """从教务系统同步的用户信息表"""

    __tablename__ = "jwxt_user_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="用户ID"
    )
    student_id: Mapped[str] = mapped_column(String(20), nullable=False, comment="学号")
    realname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="学生姓名")
    college: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="学院")
    major: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="专业")
    class_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="班级")
    grade: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, comment="年级")

    # 存储原始JSON数据
    raw_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="原始JSON数据")

    sync_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        comment="同步时间",
    )
