#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务退避管理工具API接口
"""
import logging
import uuid
from typing import Optional, Dict, Any, Callable
from backoff.common.backoff_config import TaskBackoffConfig
from backoff.common.task_entity import TaskEntity
from backoff.core.task_repository import TaskRepository
from backoff.core.backoff_worker import BackoffWorker
from backoff.models.backoff_threadpool import BackoffThreadPool
from backoff.models.redis_client import init_redis_client, close_redis_client
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from .biz_task_scheduler import task_scheduler

logger = logging.getLogger()


class TaskBackoffScheduler:
    """任务退避管理工具主类"""

    def __init__(self, config: Optional[TaskBackoffConfig] = None):
        """
        初始化任务退避管理工具

        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or TaskBackoffConfig()
        self.task_repository: Optional[TaskRepository] = None
        self.backoff_worker: Optional[BackoffWorker] = None
        self.backoff_threadpool: Optional[BackoffThreadPool] = None
        self._initialized = False

        # 初始化调度器
        scheduler_name = f"{self.config.task.biz_prefix}_scheduler"
        task_scheduler.add_scheduler(scheduler_name, self.default_biz_scheduler)
        task_scheduler.start(scheduler_name)

        self.initialize()

        logger.info("任务退避管理工具初始化完成")

    def initialize(self) -> bool:
        """
        初始化框架

        Returns:
            bool: 是否初始化成功
        """
        try:
            # 初始化Redis连接
            if not init_redis_client(self.config.storage):
                logger.error(f"Redis连接初始化失败:{self.config.storage}")
                return False

            # 创建任务管理器
            global task_repository
            self.task_repository = TaskRepository(
                biz_prefix=self.config.task.biz_prefix,
                storage_config=self.config.storage,
            )
            task_repository = self.task_repository

            # 创建线程池管理器
            global backoff_threadpool
            self.backoff_threadpool = BackoffThreadPool(
                max_workers=self.config.threadpool.concurrency,
                thread_name_prefix=f"{self.config.task.biz_prefix}_worker",
                executor_type=self.config.threadpool.executor_type,
                timeout=self.config.task.task_exec_timeout,
            )
            backoff_threadpool = self.backoff_threadpool

            # 创建任务工作器
            global backoff_worker
            self.backoff_worker = BackoffWorker(
                task_repository=self.task_repository,
                backoff_threadpool=self.backoff_threadpool,
                task_timeout=self.config.task.task_exec_timeout,
            )
            backoff_worker = self.backoff_worker
            logger.info(
                f"backoff_worker工作器初始化: task_exec_timeout={self.config.task.task_exec_timeout}"
            )

            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"任务退避管理工具初始化失败: {str(e)}")
            return False

    def default_biz_scheduler(self):
        """
        创建自定义的业务调度器

        Returns:
            BackgroundScheduler: 配置好的调度器实例
        """

        # 配置Redis作为jobstore
        job_stores = {
            "default": RedisJobStore(
                host=self.config.storage.host,
                port=self.config.storage.port,
                db=self.config.storage.db,
                password=self.config.storage.password,
            )
        }

        # 配置线程池执行器
        executors = {"default": ThreadPoolExecutor(max_workers=10)}

        # 创建调度器
        scheduler = BackgroundScheduler(
            jobstores=job_stores,
            executors=executors,
        )
        # 添加定时任务job是业务的核心方法
        scheduler.add_job(
            self.default_job_function,
            "interval",
            seconds=self.config.scheduler.interval,
            id=f"{self.config.task.biz_prefix}_job",
            name="退避工具内置调度任务",
            max_instances=1,
            replace_existing=True,
        )

        return scheduler

    def default_job_function(self):
        """默认的定时任务执行job"""

        if not backoff_worker or not task_repository:
            logger.error("任务工作器或任务管理器未初始化")
            return

        try:
            # 获取待处理任务
            pending_taskIds = task_repository.get_pending_taskIds(
                batch_size=self.config.task.batch_size
            )
            if not pending_taskIds:
                logger.info(f"{self.config.task.biz_prefix},没有待处理任务")
                return

            backoff_worker.execute_batch_tasks(pending_taskIds)
        except Exception as e:
            logger.error(f"执行定时任务失败: {e}")

    def set_custom_task_handler(self, handler: Callable):
        """
        设置业务任务处理器

        Args:
            handler: 任务处理函数，接收(task_entity, task_params)参数
        """
        if self.backoff_worker:
            self.backoff_worker.set_custom_task_handler(handler)
        else:
            logger.error("任务工作器未初始化")

    def set_custom_task_exception_handler(self, handler: Callable):
        """
        设置任务异常处理器

        Args:
            handler: 任务处理函数，接收(task_entity, task_params)参数
        """
        if self.backoff_worker:
            self.backoff_worker.set_custom_task_exception_handler(handler)
        else:
            logger.error("任务工作器未初始化")

    def create_task(
        self, task_params: Dict[str, Any], task_id: Optional[str] = None
    ) -> Optional[str]:
        """
        创建任务

        Args:
            task_params: 任务参数
            task_id: 任务ID，如果为None则自动生成
            max_retry_count: 最大重试次数
            backoff_type: 退避类型
            backoff_interval: 退避间隔(秒)
            backoff_multiplier: 退避倍数

        Returns:
            str: 任务ID，如果创建失败返回None
        """
        if not self._initialized:
            logger.error("框架未初始化，请先调用initialize()")
            return None

        try:
            # 生成任务ID
            if task_id is None:
                task_id = str(uuid.uuid4())

            # 创建任务实体
            task_entity = TaskEntity.create(
                task_id=task_id,
                param=task_params,
                max_retry_count=self.config.task.max_retry_count,
                backoff_type=self.config.task.backoff_type,
                backoff_interval=self.config.task.backoff_interval,
                backoff_multiplier=self.config.task.backoff_multiplier,
            )

            if self.task_repository.create_task(task_entity):
                return task_id
            else:
                return None

        except Exception as e:
            logger.error(f"创建任务异常: {str(e)}")
            return None

    def get_task(self, task_id: str) -> Optional[TaskEntity]:
        """
        获取任务详情

        Args:
            task_id: 任务ID

        Returns:
            TaskEntity: 任务实体
        """
        if self.task_repository:
            return self.task_repository.get_task(task_id)
        return None

    def delete_task(self, task_id: str) -> bool:
        """
        删除任务

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否删除成功
        """
        if self.task_repository:
            return self.task_repository.delete_task(task_id)
        return False

    def get_queue_stats(self) -> Dict[str, int]:
        """
        获取队列统计信息

        Returns:
            Dict[str, int]: 队列统计
        """
        if self.task_repository:
            return self.task_repository.get_queue_stats()
        return {}

    def shutdown(self):
        """关闭框架"""
        try:
            # 停止调度器
            if task_scheduler:
                task_scheduler.stop()

            # 关闭线程池
            if self.backoff_threadpool:
                self.backoff_threadpool.shutdown()

            # 关闭Redis连接
            close_redis_client()

            self._initialized = False
            logger.info("任务退避管理工具已关闭")

        except Exception as e:
            logger.error(f"关闭框架失败: {str(e)}")

    def __enter__(self):
        """上下文管理器入口"""
        if not self.initialize():
            raise RuntimeError("框架初始化失败")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.shutdown()
