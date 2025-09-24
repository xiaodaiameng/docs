from datetime import datetime

import sqlalchemy
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.sql import Base


class UserProfile(Base):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, unique=True, comment="用户ID")

    college: Mapped[str] = mapped_column(String(100), nullable=True, comment="学院")
    major: Mapped[str] = mapped_column(String(100), nullable=True, comment="专业")
    grade: Mapped[int] = mapped_column(Integer, nullable=True, comment="年级")

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
