from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import UserProfile
from app.models.user import User


class UserProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> Optional[UserProfile]:
        """
        通过用户名获得用户资料对象
        """
        result = await self.session.execute(select(UserProfile).join(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create_profile(
        self,
        user_id: int,
        college: Optional[str] = None,
        major: Optional[str] = None,
        grade: Optional[int] = None,
    ) -> Optional[UserProfile]:
        """
        创建一个用户资料

        :param user_id: 用户ID
        :param college: 学院
        :param major: 专业
        :param grade: 年级

        :return: 用户资料对象。失败则返回 None
        """

        profile = UserProfile(
            user_id=user_id,
            college=college,
            major=major,
            grade=grade,
        )
        self.session.add(profile)
        try:
            await self.session.commit()
            await self.session.refresh(profile)
            return profile
        except IntegrityError:
            await self.session.rollback()
            return None

    async def update_profile(
        self,
        profile: UserProfile,
        college: Optional[str] = None,
        major: Optional[str] = None,
        grade: Optional[int] = None,
    ) -> Optional[UserProfile]:
        """
        更新用户资料

        :param profile: 用户资料对象
        :param college: 学院
        :param major: 专业
        :param grade: 年级

        :return: 更新后的用户资料对象。失败则返回 None
        """

        if college is not None:
            profile.college = college
        if major is not None:
            profile.major = major
        if grade is not None:
            profile.grade = grade

        try:
            await self.session.commit()
            await self.session.refresh(profile)
            return profile
        except IntegrityError:
            await self.session.rollback()
            return None
