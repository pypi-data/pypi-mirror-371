#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务退避管理工具包
"""

import logging
from .utils.logging_utils import init_logging

# 全局初始化日志配置
import os
from pathlib import Path
# 获取当前文件所在目录
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
# 构建配置文件路径
config_path = current_dir / 'conf' / 'logging.config.yaml'
# 初始化日志，指定配置文件路径
init_logging(config_path)
logger = logging.getLogger()

# 导出公共模块和类，便于外部使用
from .common import TaskBackoffConfig, BackoffType, ExecutorType, TaskEntity
from .scheduler import TaskBackoffScheduler
