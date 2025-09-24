from datetime import datetime

import sqlalchemy
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.sql import Base


class UserTestRecord(Base):
    __tablename__ = "user_test_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(Integer, sqlalchemy.ForeignKey("user.id"), nullable=False, comment="用户ID")

    test_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="测试名称")
    result: Mapped[str] = mapped_column(String(250), nullable=False, comment="测试结果")
    details: Mapped[str] = mapped_column(String(500), nullable=True, comment="测试详情")

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
