from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole

""" Repositories 数据访问层——CRUD
SessionLocal（会话工厂）→ 
get_db()（生成会话）→
api里的业务代码（接收会话）→ 
UserRepository（使用会话）-> 对数据增删改查
"""
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        通过用户名获得用户对象
        """
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        通过邮箱获得用户对象
        """
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_addition_order(self, prefix: str) -> int:
        """
        获取当前的添加顺序

        :param prefix: 账号前缀
        """
        user = await self.session.execute(select(func.count(User.id)).where(User.username.startswith(prefix)))
        total_users = user.scalar() or 0
        return total_users + 1

    async def create_user(
        self,
        username: str,
        password: str,
        realname: str,
        email: str,
        role: UserRole = UserRole.student,
        status: bool = True,
    ) -> Optional[User]:
        """
        创建一个用户

        :param username: 用户名
        :param password: 用户哈希密钥
        :param realname: 姓名
        :param email: 学校邮箱
        :param role: 用户角色(student/admin)
        :param status: 用户状态(正常/禁用)

        :raise IntegrityError: 用户名或邮箱已存在

        :return: 用户对象。失败则返回 None
        """

        user = User(
            username=username,
            password=password,
            realname=realname,
            email=email,
            role=role,
            status=status,
        )

        self.session.add(user)
        await self.session.commit()

        return user

    async def edit_info(
        self,
        user: User,
        realname: Optional[str] = None,
        status: Optional[bool] = None,
        role: Optional[UserRole] = None,
        email: Optional[str] = None,
    ) -> bool:
        """
        编辑用户信息

        :param user: 用户对象
        :param name: 姓名
        :param role: 用户角色(student/teacher/admin)
        :param status: 用户状态(正常/禁用)
        :param session: 届号
        :param dept_no: 院系ID
        :param major_no: 专业ID
        :param class_number: 班级ID
        """
        user.realname = realname or user.realname
        user.role = role or user.role
        user.status = status or user.status
        user.email = email or user.email

        try:
            await self.session.commit()
        except IntegrityError:
            return False

        return True

    async def change_password(self, user: User, new_password: str):
        """
        修改用户密码

        :param user: 用户对象
        :param new_password: 新密码（已哈希）
        """
        user.password = new_password
        await self.session.commit()

    def _term_filter(self, course_date_column, term: str):
        """
        term json 对象过滤器
        """
        bind = self.session.get_bind()
        if bind.dialect.name == "mysql":
            return course_date_column.op("->>")("$.term") == term
        elif bind.dialect.name == "sqlite":
            return func.json_extract(course_date_column, "$.term") == term
        else:  # pragma: no cover
            return course_date_column["term"] == term

    async def delete_user(self, user: User):
        """
        删除用户

        :param user: 用户对象
        """
        await self.session.delete(user)
        await self.session.commit()
