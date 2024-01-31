"""
To setup and config the global logger module
"""
import logging
import sys


def setup_logger():
    # 创建日志对象
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # 创建Docker日志处理器
    docker_handler = logging.StreamHandler(sys.stdout)  # 输出到stdout
    docker_handler.setLevel(logging.INFO)  # 设置日志级别

    # 创建格式化器并将其添加到处理器
    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    docker_handler.setFormatter(formatter)

    # 将处理器添加到日志对象
    logger.addHandler(docker_handler)

    return logger


# 调用配置函数，返回全局logger实例
logger = setup_logger()
