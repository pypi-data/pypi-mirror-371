#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试日志配置
"""
import logging
from app.utils.logging_utils import init_logging

init_logging()

logger = logging.getLogger()


def test_logging():
    """测试日志配置"""
    logger.info("开始测试日志配置...")
    # 测试不同级别的日志
    logger.debug("这是一条DEBUG日志")
    logger.info("这是一条INFO日志")
    logger.warning("这是一条WARNING日志")
    logger.error("这是一条ERROR日志")

    # 测试其他模块的日志
    other_logger = logging.getLogger("task_backoff_framework.core.task_entity")
    other_logger.info("这是任务实体模块的日志")

    logger.info("日志配置测试完成！")


if __name__ == "__main__":
    test_logging()
