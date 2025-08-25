#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务工作器模块
"""
import json
import logging
from typing import Optional, Dict, Any, Callable
from backoff.common.task_entity import TaskEntity
from .task_repository import TaskRepository
from backoff.models.backoff_threadpool import BackoffThreadPool
from backoff.common.result_entity import ResultEntity
from backoff.common.error_code import ErrorCode

logger = logging.getLogger()


class BackoffWorker:
    """任务工作器，负责执行具体的任务"""

    def __init__(
        self,
        task_repository: TaskRepository,
        backoff_threadpool: Optional[BackoffThreadPool] = None,
        task_handler: Optional[Callable] = None,
        task_exception_handler: Optional[Callable] = None,
        task_timeout: int = 300,
    ):
        """
        初始化任务工作器

        Args:
            task_repository: 任务管理器
            backoff_threadpool: 线程池管理器
            task_handler: 任务处理函数
            task_timeout: 任务超时时间(秒)
        """
        self.task_repository = task_repository
        self.backoff_threadpool = backoff_threadpool
        self.task_handler = task_handler
        self.task_exception_handler = task_exception_handler
        self.task_timeout = task_timeout
        
    
    def execute_batch_tasks(self, pending_taskIds: list[str]) -> list[Dict[str, Any]]:
        """
        批量执行任务

        Args:
            tasks: 任务列表

        Returns:
            list[Dict[str, Any]]: 执行结果列表
        """
        results = []

        if self.backoff_threadpool:
            # 使用线程池并发执行
            futures = []
            for taskId in pending_taskIds:
                future = self.backoff_threadpool.submit_task(self.execute_task, str(taskId))
                futures.append((taskId, future))
            # 收集结果
            for task_id, future in futures:
                try:
                    result = future.result(timeout=self.task_timeout)
                    results.append(result)

                except TimeoutError as e:
                    logger.error(f"任务 {task_id} 执行超时: {str(e)}")
                    error_result = {
                        "success": False,
                        "error": f"任务执行超时: {task_id}",
                        "task_id": task_id,
                    }
                    results.append(error_result)
                except Exception as e:
                    logger.error(f"任务 {task_id} 执行异常: {e}")
                    error_result = {
                        "success": False,
                        "error": str(e),
                        "task_id": task_id,
                    }
                    results.append(error_result)

        return results

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """
        执行单个任务

        Args:
            task_entity: 任务实体

        Returns:
            Dict[str, Any]: 执行结果
        """
        logger.info(f"任务 {task_id} 正在执行")

        task_entity = self.task_repository.get_task(task_id)
        
        self.task_repository.mark_task_processing(task_id)
        task_params = json.loads(task_entity.param) if task_entity.param else {}

        try:
            # 执行任务
            result = self.execute_task_handler(task_entity, task_params)

            status = result["status"]
            logger.info(f"任务 {task_id} 执行成功, 结果: {status}")

            # 标记任务为已完成
            result_str = (json.dumps(result) if isinstance(result, (dict, list)) else str(result))
            self.task_repository.mark_task_completed(task_id, result_str)
    
            return ResultEntity.ok(result, task_id)
        
        except Exception as e:
            error_msg = f"任务执行失败: {str(e)}"
            logger.error(f"{error_msg}, task_id: {task_id}")
            self.task_repository.mark_task_failed(task_id, error_msg)
            
            # 如果有自定义异常处理器，则调用它
            self.execute_exception_handler(task_entity, task_params)
            
            return ResultEntity.fail(ErrorCode.TASK_EXECUTE_FAILURE, error_msg, task_id)
        

    def execute_task_handler(
        self, task_entity: TaskEntity, task_params: Dict[str, Any]
    ) -> Any:
        """使用自定义处理器执行任务"""
        try:
            return self.task_handler(task_entity, task_params)
        except Exception as e:
            raise e
        
        
    def execute_exception_handler(
        self, task_entity: TaskEntity, task_params: Dict[str, Any]
    ) -> Any:
        """使用自定义异常处理器执行任务"""
        try:
            return self.task_exception_handler(task_entity, task_params)
        except Exception as e:
            raise e


    def set_custom_task_handler(self, handler: Callable):
        """
        设置任务处理器

        Args:
            handler: 任务处理函数
        """
        self.task_handler = handler
        logger.info(f"custom_task_handler: [{handler.__name__}] 任务处理器已设置")

    def set_custom_task_exception_handler(self, handler: Callable):
        """
        设置任务异常处理器

        Args:
            handler: 任务异常处理函数
        """
        self.task_exception_handler = handler
        logger.info(f"custom_task_exception_handler: [{handler.__name__}] 任务异常处理器已设置")


    def get_queue_stats(self) -> Dict[str, int]:
        return self.task_repository.get_queue_stats()
