#!/usr/bin/env python
# -*-coding:utf-8 -*-

import logging
import threading
from backoff.common.task_entity import ExecutorType
from pebble import ProcessPool, ThreadPool

logger = logging.getLogger()


class BackoffThreadPool:
    """线程池/进程池管理器"""

    def __init__(self, max_workers: int, executor_type, timeout):
        """
        初始化执行器管理器

        Args:
            max_workers: 最大工作线程/进程数
            executor_type: 执行器类型 (THREAD 或 PROCESS)
        """
        self.executor_type = executor_type
        self.max_workers = max_workers
        self.timeout = timeout
        
        # 添加任务计数器
        self._submitted_tasks = 0
        self._completed_tasks = 0
        self._failed_tasks = 0
        self._running_tasks = 0  # 正在执行的任务数
        self._lock = threading.Lock()

        # 根据类型创建对应的执行器
        if executor_type == ExecutorType.THREAD.value:
            # I/O密集型任务用线程池
            self.executor = ThreadPool(max_workers=max_workers)
        else:
            # CPU密集型任务用进程池
            self.executor = ProcessPool(max_workers=max_workers)
        logger.info(
            f"backoff_threadpool 初始化完成: executor_type: {self.executor_type}, max_workers: {self.max_workers}"
        )

    def submit_task(self, func, *args, **kwargs):
        """
        提交任务到执行器
        
        Args:
            func: 要执行的函数
            *args: 函数的位置参数
            **kwargs: 函数的关键字参数
            
        Returns:
            Future: Pebble Future 对象，可用于获取结果或添加回调
            
        注意:
            - 任务会在 self.timeout 秒后超时
            - 可以通过返回的 Future 对象添加回调或获取结果
        """
        with self._lock:
            self._submitted_tasks += 1
        
        # 使用初始化时设置的超时时间
        if self.executor_type == ExecutorType.THREAD.value:
            future = self.executor.schedule(func, args=args, kwargs=kwargs)
        else:
            future = self.executor.schedule(func, args=args, kwargs=kwargs, timeout=self.timeout)
        
        # 添加回调来统计任务完成情况
        future.add_done_callback(self._task_callback)
        
        # 立即增加正在执行的任务数（因为任务已经开始执行）
        with self._lock:
            self._running_tasks += 1
            
        return future
    
    def _task_callback(self, future):
        """任务完成回调，用于统计任务状态"""
        with self._lock:
            self._running_tasks -= 1  # 任务执行完成
            if future.exception():
                self._failed_tasks += 1
            else:
                self._completed_tasks += 1

    def get_pool_info(self) -> dict:
        """
        获取线程池信息
        
        Returns:
            dict: 包含线程池状态信息的字典
        """
        # 基础信息
        info = {
            "executor_type": self.executor_type,
            "max_workers": self.max_workers,
            "timeout": self.timeout,
            "active": self.executor.active,
            "submitted_tasks": self._submitted_tasks,
            "completed_tasks": self._completed_tasks,
            "failed_tasks": self._failed_tasks,
            "running_tasks": self._running_tasks,  # 正在执行的任务数
            "available_workers": max(0, self.max_workers - self._running_tasks),  # 可用线程数
            "utilization_rate": round((self._running_tasks / self.max_workers) * 100, 2) if self.max_workers > 0 else 0,  # 线程利用率
            "pending_tasks": self._submitted_tasks - self._completed_tasks - self._failed_tasks,
        }
        
        # 尝试获取pebble内部信息
        try:
            if hasattr(self.executor, '_context'):
                context = self.executor._context
                info["total_workers"] = getattr(context, 'workers', self.max_workers)
                info["queue_size"] = getattr(context.task_queue, 'qsize', lambda: 0)()
                info["task_counter"] = getattr(context, 'task_counter', None)
                
                # 使用pebble内部信息计算可用线程数（如果可能）
                if hasattr(context, 'workers'):
                    # 尝试从队列大小推断正在执行的任务数
                    # 注意：这是一个估算，可能不是100%准确
                    estimated_running = max(0, self._submitted_tasks - self._completed_tasks - self._failed_tasks - info["queue_size"])
                    info["pebble_estimated_available"] = max(0, info["total_workers"] - estimated_running)
                    
        except Exception as e:
            logger.debug(f"获取pebble内部信息失败: {e}")
        
        # 尝试获取更多信息
        try:
            # 获取当前活跃的线程数（通过threading模块）
            if self.executor_type == ExecutorType.THREAD.value:
                active_threads = threading.active_count()
                info["active_threads"] = active_threads
                info["main_thread"] = threading.main_thread().ident
        except Exception as e:
            logger.debug(f"获取线程信息失败: {e}")
        
        return info
    
    def get_pool_status(self) -> str:
        """
        获取线程池状态摘要
        
        Returns:
            str: 状态摘要字符串
        """
        info = self.get_pool_info()
        return (f"线程池状态: {info['executor_type']}, "
                f"最大工作线程: {info['max_workers']}, "
                f"可用线程: {info['available_workers']}, "
                f"正在执行: {info['running_tasks']}, "
                f"利用率: {info['utilization_rate']}%, "
                f"活跃: {info['active']}, "
                f"已提交任务: {info['submitted_tasks']}, "
                f"已完成任务: {info['completed_tasks']}, "
                f"失败任务: {info['failed_tasks']}, "
                f"待处理任务: {info['pending_tasks']}")
    
    def get_core_metrics(self) -> dict:
        """
        获取核心指标
        
        Returns:
            dict: 核心指标字典
        """
        info = self.get_pool_info()
        return {
            "available_workers": info["available_workers"],      # 可用线程数
            "running_tasks": info["running_tasks"],              # 正在执行的任务数
            "max_workers": info["max_workers"],                  # 最大线程数
            "utilization_rate": info["utilization_rate"],        # 线程利用率
            "pending_tasks": info["pending_tasks"],              # 待处理任务数
        }
        
    def shutdown(self):
        """关闭执行器"""
        self.executor.close()
        self.executor.join()
        logger.debug(f"{self.executor_type}池关闭...")