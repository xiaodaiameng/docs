from collections.abc import AsyncGenerator
from redis.asyncio import Redis
from .config import config
from .logger import logger


#                                异步生成器函数 接收值类型 返回值类型
async def get_redis_client() -> AsyncGenerator[Redis, None]:

    """这是一个异步生成器函数，生成异步的Redis客户端并管理其生命周期。"""

    logger.info("初始化 Redis 实例...")
    # 创建异步Redis客户端实例
    client = Redis(
                        host=config.redis_host,    # 从配置中获取Redis主机地址（localhost）
                        port=config.redis_port,    # 从配置中获取Redis端口（默认6379）
                        decode_responses=True      # 自动将Redis返回的字节数据解码为字符串（方便使用）
                    )
    try:
        yield client  # 提供客户端给调用方使用
    finally:
        await client.close()  # 关闭 redis连接