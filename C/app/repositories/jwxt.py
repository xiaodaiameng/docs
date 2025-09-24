import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.jwxt import JWXTBinding, JWXTUserInfo
from app.schemas.jwxt import JWXTUserInfoAPIResponse
from app.services.password_encryption import encrypt_jwxt_password


class JWXTRepository:
    """JWXT数据访问层"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_binding_by_user_id(self, user_id: int) -> Optional[JWXTBinding]:
        """根据用户ID获取绑定信息"""
        result = await self.db.execute(select(JWXTBinding).where(JWXTBinding.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_binding_by_student_id(self, student_id: str) -> Optional[JWXTBinding]:
        """根据学号获取绑定信息"""
        result = await self.db.execute(select(JWXTBinding).where(JWXTBinding.student_id == student_id))
        return result.scalar_one_or_none()

    async def create_binding(self, user_id: int, student_id: str, password: str) -> JWXTBinding:
        """创建新的绑定"""
        # 加密密码
        encrypted_password = encrypt_jwxt_password(password)

        binding = JWXTBinding(
            user_id=user_id,
            student_id=student_id,
            jwxt_password=encrypted_password,
        )

        self.db.add(binding)
        await self.db.flush()
        return binding

    async def update_binding(
        self, binding: JWXTBinding, password: Optional[str] = None, last_sync_time: Optional[datetime] = None
    ) -> JWXTBinding:
        """更新绑定信息"""
        if password:
            binding.jwxt_password = encrypt_jwxt_password(password)

        if last_sync_time:
            binding.last_sync_time = last_sync_time
            binding.sync_count += 1

        await self.db.flush()
        return binding

    async def delete_binding(self, binding: JWXTBinding):
        """删除绑定"""
        await self.db.delete(binding)
        await self.db.flush()

    async def get_user_info_by_user_id(self, user_id: int, limit: int = 1) -> List[JWXTUserInfo]:
        """根据用户ID获取用户信息（按同步时间倒序）"""
        result = await self.db.execute(
            select(JWXTUserInfo)
            .where(JWXTUserInfo.user_id == user_id)
            .order_by(JWXTUserInfo.sync_time.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_latest_user_info(self, user_id: int) -> Optional[JWXTUserInfo]:
        """获取最新的用户信息"""
        user_info_list = await self.get_user_info_by_user_id(user_id, 1)
        return user_info_list[0] if user_info_list else None

    async def create_user_info(self, user_id: int, student_id: str, user_data: JWXTUserInfoAPIResponse) -> JWXTUserInfo:
        """创建用户信息记录"""
        user_info = JWXTUserInfo(
            user_id=user_id,
            student_id=student_id,
            realname=user_data.get("xm"),
            college=user_data.get("college"),
            major=user_data.get("major"),
            class_name=user_data.get("class_name"),
            grade=user_data.get("grade"),
            enrollment_date=user_data.get("enrollment_date"),
            raw_data=json.dumps(user_data, ensure_ascii=False),
        )

        self.db.add(user_info)
        await self.db.flush()
        return user_info

    async def is_student_id_bound(self, student_id: str, exclude_user_id: Optional[int] = None) -> bool:
        """检查学号是否已被其他用户绑定"""
        query = select(JWXTBinding).where(JWXTBinding.student_id == student_id)

        if exclude_user_id:
            query = query.where(JWXTBinding.user_id != exclude_user_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def commit(self):
        """提交事务"""
        await self.db.commit()

    async def rollback(self):
        """回滚事务"""
        await self.db.rollback()
