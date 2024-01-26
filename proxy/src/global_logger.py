"""
logger
"""
import logging
import sys


def setup_logger():
    logger = logging.getLogger("proxy_logger")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    sh = logging.StreamHandler(sys.stdout)  # 输出到stdout
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


# 调用配置函数，返回全局logger实例
logger = setup_logger()
