#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Redis 连接集成测试
- 从环境变量或默认配置创建 StorageConfig
- 尝试连接并 PING
- 执行一次 set/get 验证基本读写
- 如果本机未启动 Redis（连接失败），测试将被跳过
"""

import uuid
import logging
import pytest
from app.utils.logging_utils import init_logging
from app.common.backoff_config import TaskBackoffConfig
from app.models.redis_client import (
    get_redis_client,
    init_redis_client,
    close_redis_client,
)

init_logging()
logger = logging.getLogger()

class TestRedisConnection:
    """Redis 连接测试类（集成测试）"""

    @classmethod
    def setup_class(cls):
        logger.info("初始化 Redis 连接测试...")

    @classmethod
    def teardown_class(cls):
        close_redis_client()
        logger.info("已关闭 Redis 客户端")

    def _get_config(self) -> TaskBackoffConfig:

        return TaskBackoffConfig.from_dict(
            {
                "storage": {
                    "host": "192.168.3.52",
                    "port": 6379,
                    "db": 1,
                    "password": "ucap2020",
                }
            }
        )

    def test_redis_ping(self):
        """测试 Redis PING"""
        config = self._get_config()
        logger.info(
            "使用配置测试 Redis 连接: %s:%s db=%s",
            config.storage.host,
            config.storage.port,
            config.storage.db,
        )

        if not init_redis_client(config.storage):
            pytest.skip(
                "Redis 未就绪或无法连接（请启动本地或指定的 Redis 服务后再运行此测试）"
            )

        client = get_redis_client(config.storage)
        assert client.ping() is True
        logger.info(
            "Redis PING 成功: %s:%s db=%s",
            config.storage.host,
            config.storage.port,
            config.storage.db,
        )

    def test_redis_set_get(self):
        """测试 Redis 基本读写"""
        config = self._get_config()

        if not init_redis_client(config.storage):
            pytest.skip(
                "Redis 未就绪或无法连接（请启动本地或指定的 Redis 服务后再运行此测试）"
            )

        client = get_redis_client(config.storage)

        test_key = f"test:task_backoff:{uuid.uuid4()}"
        test_value = "hello_redis"
        logger.info("测试 Redis set/get: key=%s, value=%s", test_key, test_value)

        client.set(test_key, test_value)
        got = client.get(test_key)
        client.delete(test_key)

        logger.info(f"获取 Redis 值: {got}, 类型={type(got)}")
        # Redis get 返回的是字节字符串，需要解码为普通字符串再比较
        if isinstance(got, bytes):
            got = got.decode("utf-8")
        assert got == test_value
        logger.info("Redis set/get 成功: key=%s, value=%s", test_key, got)


if __name__ == "__main__":
    pytest.main()
