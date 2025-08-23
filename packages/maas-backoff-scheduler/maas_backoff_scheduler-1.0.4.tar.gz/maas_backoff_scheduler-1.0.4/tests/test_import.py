#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""测试导入包"""

# 添加项目根目录到Python路径
import sys
import os

sys.path.insert(0, os.path.abspath('.'))

# 测试从backoff.common.task_entity导入
from backoff.common.task_entity import BackoffType, ExecutorType, TaskEntity
print("从backoff.common.task_entity导入成功!")
print(f"BackoffType: {BackoffType}")
print(f"ExecutorType: {ExecutorType}")
print(f"TaskEntity: {TaskEntity}")

# 测试从backoff.scheduler.backoff_scheduler导入
from backoff.scheduler.backoff_scheduler import TaskBackoffScheduler
print("从backoff.scheduler.backoff_scheduler导入成功!")
print(f"TaskBackoffScheduler: {TaskBackoffScheduler}")

# 测试从backoff.scheduler导入(通过__init__.py提供的便捷导入)
from backoff.scheduler import TaskBackoffScheduler, TaskBackoffConfig, TaskEntity
print("从backoff.scheduler导入成功!")
print(f"TaskBackoffScheduler: {TaskBackoffScheduler}")
print(f"TaskBackoffConfig: {TaskBackoffConfig}")
print(f"TaskEntity: {TaskEntity}")