import os
from typing import Literal

from dotenv import load_dotenv # 用于加载项目根目录下的 .env 文件（环境变量文件）如果 .env 中定义了与配置类中同名的变量（如 DB_URL），会自动覆盖代码中的默认值，方便在不同环境（开发/生产）中切换配置，而无需修改代码。
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    env: Literal["dev", "prod"] = "dev" # 只能是 "dev" 或 "prod"，默认是开发环境 "dev"
    """当前环境：dev"""
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG" if env == "dev" else "INFO"
    """日志等级：开发环境用 DEBUG 详细日志，生产环境用 INFO 精简日志"""

    # FastAPI 配置，
    title: str = "FinancialCareerCommunity API"
    """API文档标题"""
    version: str = "0.1.0"
    """API 服务版本"""
    host: str = "127.0.0.1"
    """API 本地回环地址(IP地址)"""
    port: int = 8080
    """API 服务端口"""

    # jwt 配置
    secret_key: str = "82ec285b5f0670c852c2e16d9776c5d17bd89a5f1dc09cdab5374a8a9ec7aa11"
    """jwt 签名密钥，32 位 hex 密钥，可以通过类似于 openssl rand -hex 32 的命令获得"""
    algorithm: str = "HS256"
    """jwt 签名算法"""
    expire_minutes: int = 60
    """jwt Token的过期时间（60分钟）"""

    # JWXT 配置
    jwxt_encryption_key: str = "EWE1wl__6LIkWY1zNl5RS_ipky_bbYOf_8r5Tf4-e6E="
    """JWXT密码加密密钥，建议使用32字节的随机字符串"""
    jwxt_sync_interval_days: int = 90
    """JWXT自动同步间隔天数，默认90天（一学期）"""
    jwxt_api_timeout: int = 30
    """JWXT外部API请求超时时间（秒）"""

    # 数据库配置
    # db_url: str = "sqlite+aiosqlite:///./database.db"
    db_url: str = "mysql+aiomysql://root:123456@localhost/test?charset=utf8mb4"\


    # Redis 缓存配置
    redis_host: str = "localhost"
    """Redis 主机地址"""
    redis_port: int = 6379
    """Redis 端口号"""


    # CORS配置（跨域资源共享配置）
    cors_allow_origins: list = ["*"]  # 允许的源，生产环境应指定具体域名
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]


app_config = Config()



    # # 爬虫相关配置

config = Config()
# 创建 Config 实例后，整个项目可以通过 config.xxx 的方式统一访问配置
# 例如： config.port，config.db_url，config.secret_key
