
# 会话（Session）关闭（await session.close()）

# 会话是应用程序与数据库之间的一次交互会话，用于暂存和跟踪数据库操作（如查询、新增、修改等）
# 会话关闭仅表示当前这次交互结束，释放会话占用的内存资源和临时状态
# 不会关闭底层的数据库连接，连接可能会被连接池回收复用
# 作用：避免会话对象长期占用内存，确保事务正确提交或回滚


# 数据库连接关闭（await _engine.dispose()）

# 这里关闭的是数据库引擎（Engine）管理的所有连接
# 会真正断开与数据库服务器的网络连接，释放所有连接资源
# 通常在应用程序退出时调用，彻底清理数据库资源
# 作用：完全释放数据库连接资源，避免应用退出后仍有残留连接


from collections.abc import AsyncGenerator
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker  # 新增导入async_sessionmaker
from sqlalchemy.orm import declarative_base, declared_attr  # 移除同步sessionmaker
from app.core.config import config
from app.core.logger import logger

# 保持基类定义不变
Base = declarative_base()


class BaseModel:
    """自定义的 “功能基类”，不具备 ORM 核心能力，需要与 Base 组合使用 """
    @declared_attr
    def __tablename__(cls): # User → 表名 users
        return cls.__name__.lower() + 's'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    create_time = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")


# 异步引擎配置
_engine: AsyncEngine = create_async_engine(
    config.db_url,
    pool_pre_ping=True,
    echo=False,  # 生产环境关闭SQL日志
)

# 创建异步会话工厂：使用async_sessionmaker替代sessionmaker
AsyncSessionLocal = async_sessionmaker(  # 这里从sessionmaker改为async_sessionmaker
    _engine, 
    class_=AsyncSession,
    autocommit=False, 
    autoflush=False,
    expire_on_commit=False  # 异步模式建议设置
)

# 异步依赖注入函数（保持不变）
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """异步获取数据库会话，自动关闭连接"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def load_db():
    """异步初始化数据库表"""
    logger.info("初始化数据库表...")
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库引擎，释放连接资源"""
    await _engine.dispose()
    