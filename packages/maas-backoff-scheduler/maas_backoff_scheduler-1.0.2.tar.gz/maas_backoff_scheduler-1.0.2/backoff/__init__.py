#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务退避管理工具包
"""

import logging
from backoff.utils.logging_utils import init_logging

# 全局初始化日志配置
init_logging()
logger = logging.getLogger()