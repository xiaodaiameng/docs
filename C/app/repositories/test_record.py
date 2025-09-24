from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_record import UserTestRecord
from app.models.user import User


class UserTestRecordRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str, test_name: Optional[str] = None) -> Optional[list[UserTestRecord]]:
        """
        通过用户名获得用户测试记录对象
        """
        query = select(UserTestRecord).join(User).where(User.username == username)
        if test_name:
            query = query.where(UserTestRecord.test_name == test_name)
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore

    async def create_test_record(
        self,
        user_id: int,
        test_name: str,
        result: str,
        details: Optional[str] = None,
    ) -> Optional[UserTestRecord]:
        """
        创建一个用户测试记录

        :param user_id: 用户ID
        :param test_name: 测试名称
        :param result: 测试结果
        :param details: 测试详情

        :return: 用户测试记录对象。失败则返回 None
        """

        test_record = UserTestRecord(
            user_id=user_id,
            test_name=test_name,
            result=result,
            details=details,
        )
        self.session.add(test_record)
        try:
            await self.session.commit()
            await self.session.refresh(test_record)
            return test_record
        except IntegrityError:
            await self.session.rollback()
            return None
