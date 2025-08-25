#!/usr/bin/env python
# -*-coding:utf-8-*-

import time
from backoff.common.error_code import ErrorCode


class ResultEntity:
    """
    接口返回结果vo类
    """

    code: int
    # 成功或失败的消息
    message: str
    # True成功,False失败
    success: bool
    # 返回结果对象
    result: object
    # 时间戳
    timestamp: int
    # task_id
    task_id: str

    def __init__(self):
        self.code = 200
        self.message = "成功"
        self.success = True
        self.result = None
        self.timestamp = int(time.time())

    @staticmethod
    def ok(result: object = None, task_id: str = "") -> "ResultEntity":
        """
        创建API返回结果

        Args:
            error_code: 错误码枚举
            detail: 详细信息
            result: 返回结果

        Returns:
            ApiResult: API返回结果对象
        """
        result_entity = ResultEntity()
        result_entity.result = result
        result_entity.timestamp = int(time.time())
        result_entity.task_id = task_id
        result_entity.success = True
        return result_entity

    @staticmethod
    def fail(error_code: ErrorCode, message: str, task_id: str = "") -> "ResultEntity":
        """
        创建API返回结果

        Args:
            error_code: 错误码枚举
            detail: 详细信息
            result: 返回结果

        Returns:
            ApiResult: API返回结果对象
        """
        result_entity = ResultEntity()
        result_entity.message = message
        result_entity.code = error_code.code
        result_entity.task_id = task_id
        if not message:
            result_entity.message = error_code.message
        result_entity.success = False
        result_entity.timestamp = int(time.time())
        return result_entity
