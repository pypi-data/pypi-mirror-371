#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""models模块初始化文件"""

# 从backoff_threadpool.py导入
from .backoff_threadpool import BackoffThreadPool

# 从redis_client.py导入
from .redis_client import RedisClient, get_redis_client, init_redis_client

# 从repository子模块导入
from .repository.storage_adapter import StorageAdapter, StorageType
from .repository.redis_adapter import RedisStorageAdapter
from .repository.storage_adapter import StorageAdapterFactory

# 导出所有类和函数
__all__ = [
    'BackoffThreadPool',
    'RedisClient',
    'get_redis_client',
    'init_redis_client',
    'StorageAdapter',
    'StorageType',
    'RedisStorageAdapter'
]


