import logging
import time
from pathlib import Path
import colorlog
from .config import config

LOG_PATH = Path("./logs")
LOG_PATH.mkdir(exist_ok=True)


def init_logger():

    logger = logging.getLogger("app")# 创建名为 "app" 的 logger 对象
    logger.setLevel(logging.DEBUG)# 日志级别为 DEBUG（最低级别，意味着会记录所有级别的日志

    # 创建控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.log_level)

    # 创建文件日志处理器
    file_handler = logging.FileHandler(f'logs/{time.strftime("%Y-%m-%d", time.localtime())}.log', encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(funcName)s: %(message)s"))

    # 定义颜色输出格式
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(levelname)s] %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )

    # 将颜色输出格式添加到控制台日志处理器
    console_handler.setFormatter(color_formatter)

    # 移除默认的handler
    for handler in logger.handlers:
        logger.removeHandler(handler)
    # 禁用日志传播，防止日志被父 logger 重复处理
    logger.propagate = False

    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger # 将配置好的 logger 对象导出，
    # 其他模块只需通过 from .logger import logger 导入，
    # 即可使用 logger.debug()、logger.info()、logger.error() 等方法记录不同级别的日志，实现统一的日志管理。


logger = init_logger()
