#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试日志配置
"""
import logging
from app.common.backoff_config import TaskBackoffConfig

from app.utils.logging_utils import init_logging

init_logging()

logger = logging.getLogger()


def test_config():
    """测试日志配置"""
    logger.info("开始测试日志配置...")

    # 创建配置
    config = TaskBackoffConfig.from_dict(
        {
            "storage": {
                "type": "redis",
                "host": "127.0.0.1",
                "port": 6379,
                "db": 1,
                "password": "123",
            },
            "task": {
                "biz_key_prefix": "ceshikeu",
                "batch_size": 50,
                "max_retry_count": 32,
                "backoff_type": "fixed",
                "backoff_interval": 222,
                "backoff_multiplier": 23.0,
                "task_exec_timeout": 1000,
                "min_gpu_memory_mb": 1024,
                "min_gpu_utilization": 70,
            },
            "threadpool": {"concurrency": 20, "executor_type": "process"},
            "scheduler": {"cron": "* * * * *", "interval": 10},
        }
    )
    logger.info(config)


if __name__ == "__main__":
    test_config()
