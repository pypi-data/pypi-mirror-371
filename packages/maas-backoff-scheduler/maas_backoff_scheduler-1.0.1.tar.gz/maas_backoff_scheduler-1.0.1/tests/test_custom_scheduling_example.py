#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自定义调度示例

此示例展示如何在没有内置调度器的情况下使用任务退避框架：
1. 使用Python自带的threading.Timer实现定时任务
2. 简单定时执行任务处理函数
"""
import time
import logging
from app.common.task_entity import BackoffType, ExecutorType
from app.scheduler.backoff_scheduler import (
    TaskBackoffScheduler,
    TaskBackoffConfig,
    TaskEntity
)

# 初始化日志
from app.utils.logging_utils import init_logging

init_logging()

logger = logging.getLogger()

# 创建配置
config = TaskBackoffConfig.from_dict(
    {
        "storage": {
            "host": "192.168.3.52",
            "port": 6379,
            "db": 1,
            "password": "ucap2020",
        },
        "task": {
            "biz_prefix": "custom_scheduling_example",
            "max_retry_count": 5,
            "backoff_type": BackoffType.EXPONENTIAL,
            "backoff_interval": 30,
            "backoff_multiplier": 3.0,
            "batch_size": 2,
            "task_exec_timeout": 2,
        },
        "threadpool": {"concurrency": 10, "executor_type": "process"},
        "scheduler": {"interval": 5},
    }
)


def my_task_handler(task_entity: TaskEntity, task_params: dict):
    """自定义任务处理函数"""

    # time.sleep(4)
    logger.info(f"INFO: 处理任务: {task_entity.task_id}, 参数: {task_params}")
    return {"status": "success", "message": f"任务 {task_entity.task_id} 处理完成"}

def my_exception_task_handler(task_entity: TaskEntity, task_params: dict):
    """自定义任务异常处理函数"""

    logger.info(f"ERROR: 我的任务异常了: {task_entity.task_id}, 参数: {task_params}")
    return {"status": "success", "message": f"任务 {task_entity.task_id} 处理完成"}



def main():

    # 初始化框架
    taskBackoffScheduler = TaskBackoffScheduler(config)

    # 设置任务处理器
    taskBackoffScheduler.set_custom_task_handler(my_task_handler)

    taskBackoffScheduler.set_custom_task_exception_handler(my_exception_task_handler)

    for i in range(4):
        task_id = taskBackoffScheduler.create_task(
            task_params={"index": i, "data": f"test_data_{i}"},
            task_id=f"task_{i}",
        )
        
    try:
        while True:
            time.sleep(20)
    except KeyboardInterrupt:
        logger.debug("程序停止")
    finally:
        taskBackoffScheduler.shutdown()


if __name__ == "__main__":
    main()
