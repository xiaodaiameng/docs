from redis.asyncio import Redis

BLACKLIST_PREFIX = "token_blacklist:"

# 用户 “主动登出” 场景

async def add_token_to_blacklist(redis_client: Redis, jti: str, expires_in: int):
    """
    添加登出 token 到黑名单

    :param jti: jwt secret
    :param expires_in: 过期时间（秒）
    """
    key = BLACKLIST_PREFIX + jti
    await redis_client.set(key, "true", ex=expires_in)


async def is_token_blacklisted(redis_client: Redis, jti: str) -> bool:
    """
    检查 jwt secret 是否在黑名单中

    :param jti: jwt secret
    """
    key = BLACKLIST_PREFIX + jti
    return await redis_client.exists(key) == 1
