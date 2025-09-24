import asyncio
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.core.sql import Base
from app.core.config import app_config

# 配置目标元数据
target_metadata = Base.metadata

# 这是Alembic的配置对象
config = context.config

# 设置日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 将异步URL转换为同步URL
def get_sync_db_url(async_url):
    # 从异步URL中提取必要的部分，创建同步URL
    if async_url.startswith('mysql+aiomysql://'):
        return async_url.replace('mysql+aiomysql://', 'mysql+pymysql://')
    return async_url

# 使用同步连接进行迁移
def run_migrations_online():
    # 获取同步数据库URL
    sync_db_url = get_sync_db_url(app_config.db_url)
    
    # 创建同步引擎
    connectable = engine_from_config(
        {
            'sqlalchemy.url': sync_db_url
        },
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# 离线模式
def run_migrations_offline():
    url = get_sync_db_url(app_config.db_url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# 执行迁移
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
