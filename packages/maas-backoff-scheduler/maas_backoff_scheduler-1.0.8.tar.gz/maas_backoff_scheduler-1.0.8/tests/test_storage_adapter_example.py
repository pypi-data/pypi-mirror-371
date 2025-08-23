#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存储适配器使用示例
"""

import logging
import time
from backoff.common.backoff_config import StorageConfig
from backoff.models.repository.storage_adapter import StorageType, StorageAdapterFactory
from backoff.models.repository.redis_adapter import RedisStorageAdapter

# 初始化日志
from backoff.utils.logging_utils import init_logging

init_logging()
logger = logging.getLogger()


def test_memory_storage():
    """测试内存存储适配器"""
    logger.info("=== 测试内存存储适配器 ===")
    
    # 创建配置
    config = StorageConfig(host="localhost", port=6379, db=0,type="memory")
    
    # 创建适配器
    adapter = StorageAdapterFactory.create_adapter(config)
    
    # 基本键值操作
    adapter.set("test_key", "test_value")
    value = adapter.get("test_key")
    logger.info(f"获取键值: {value}")
    
    # 哈希表操作
    adapter.set_hash("hash_key", "field1", "value1")
    adapter.set_hash("hash_key", "field2", "value2")
    hash_value = adapter.get_hash("hash_key", "field1")
    logger.info(f"获取哈希字段: {hash_value}")
    
    all_fields = adapter.get_hash_all("hash_key")
    logger.info(f"获取所有哈希字段: {all_fields}")
    
    # 有序集合操作
    adapter.add_to_sorted_set("zset_key", "member1", 1.0)
    adapter.add_to_sorted_set("zset_key", "member2", 2.0)
    adapter.add_to_sorted_set("zset_key", "member3", 3.0)
    
    members = adapter.get_sorted_set_range("zset_key", 0, -1)
    logger.info(f"获取有序集合成员: {members}")
    
    # 分布式锁操作
    lock_acquired = adapter.acquire_lock("lock_key", "lock_value", 10)
    logger.info(f"获取锁: {lock_acquired}")
    
    lock_released = adapter.release_lock("lock_key", "lock_value")
    logger.info(f"释放锁: {lock_released}")
    
    # 关闭适配器
    adapter.close()


def test_sqlite_storage():
    """测试SQLite存储适配器"""
    logger.info("=== 测试SQLite存储适配器 ===")
    
    # 创建配置
    config = StorageConfig(path=":memory:",type="sqlite")  # 使用内存数据库
    
    # 创建适配器
    adapter = StorageAdapterFactory.create_adapter(config)
    
    # 基本键值操作
    adapter.set("test_key", "test_value")
    value = adapter.get("test_key")
    logger.info(f"获取键值: {value}")
    
    # 哈希表操作
    adapter.set_hash_multiple("hash_key", {
        "field1": "value1",
        "field2": "value2",
        "field3": "value3"
    })
    
    all_fields = adapter.get_hash_all("hash_key")
    logger.info(f"获取所有哈希字段: {all_fields}")
    
    # 有序集合操作
    adapter.add_to_sorted_set("zset_key", "member1", 1.0)
    adapter.add_to_sorted_set("zset_key", "member2", 2.0)
    adapter.add_to_sorted_set("zset_key", "member3", 3.0)
    
    members = adapter.get_sorted_set_range("zset_key", 0, -1, with_scores=True)
    logger.info(f"获取有序集合成员及分数: {members}")
    
    # 关闭适配器
    adapter.close()


def test_redis_storage():
    """测试Redis存储适配器"""
    logger.info("=== 测试Redis存储适配器 ===")
    
    try:
        # 创建配置
        config = StorageConfig(
            host="localhost",
            port=6379,
            db=0,
            password="",
            type="redis"
        )
        
        # 创建适配器
        adapter = StorageAdapterFactory.create_adapter(config)
        
        # 基本键值操作
        adapter.set("test_key", "test_value")
        value = adapter.get("test_key")
        logger.info(f"获取键值: {value}")
        
        # 哈希表操作
        adapter.set_hash_multiple("hash_key", {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        })
        
        all_fields = adapter.get_hash_all("hash_key")
        logger.info(f"获取所有哈希字段: {all_fields}")
        
        # 有序集合操作
        adapter.add_to_sorted_set("zset_key", "member1", 1.0)
        adapter.add_to_sorted_set("zset_key", "member2", 2.0)
        adapter.add_to_sorted_set("zset_key", "member3", 3.0)
        
        members = adapter.get_sorted_set_range("zset_key", 0, -1, with_scores=True)
        logger.info(f"获取有序集合成员及分数: {members}")
        
        # 关闭适配器
        adapter.close()
    except Exception as e:
        logger.error(f"Redis测试失败: {str(e)}")


def main():
    """主函数"""
    # 测试内存存储
    test_memory_storage()
    
    # 测试SQLite存储
    test_sqlite_storage()
    
    # 测试Redis存储（如果可用）
    try:
        test_redis_storage()
    except Exception as e:
        logger.error(f"Redis测试跳过: {str(e)}")


if __name__ == "__main__":
    main()