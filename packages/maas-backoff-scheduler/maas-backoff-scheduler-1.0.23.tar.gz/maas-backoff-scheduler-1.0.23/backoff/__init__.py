#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务退避管理工具包
"""

# 在导入其他模块之前，先初始化日志
from backoff.utils.logging_utils import auto_init_logging
auto_init_logging()

# 导出公共模块和类，便于外部使用
from backoff.common import TaskBackoffConfig, BackoffType, ExecutorType, TaskEntity
from backoff.scheduler import TaskBackoffScheduler

# 导出日志初始化函数，让用户也可以手动调用
from backoff.utils.logging_utils import init_logging
