#!/usr/bin/env python
# -*-coding:utf-8-*-

import logging
from backoff.common.task_entity import ExecutorType
from pebble import ProcessPool, ThreadPool

logger = logging.getLogger()


class BackoffThreadPool:
    """线程池/进程池管理器"""

    def __init__(self, max_workers: int, thread_name_prefix: str, executor_type,timeout):
        """
        初始化执行器管理器

        Args:
            max_workers: 最大工作线程/进程数
            thread_name_prefix: 线程/进程名称前缀
            executor_type: 执行器类型 (THREAD 或 PROCESS)
        """
        self.executor_type = executor_type
        self.max_workers = max_workers
        self.thread_name_prefix = thread_name_prefix
        self.timeout = timeout

        # 根据类型创建对应的执行器
        if executor_type == ExecutorType.THREAD.value:
            # I/O密集型任务用线程池
            self.executor = ThreadPool(max_workers=max_workers)
        else:
            # CPU密集型任务用进程池
            self.executor = ProcessPool(max_workers=max_workers)
        logger.info(
            f"线程池初始化 executor_type: {self.executor_type}, max_workers: {self.max_workers}, thread_name_prefix: {self.thread_name_prefix}"
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
        # 使用初始化时设置的超时时间
        if self.executor_type == ExecutorType.THREAD.value:
            return self.executor.schedule(func, args=args, kwargs=kwargs)
        else:
            return self.executor.schedule(func, args=args, kwargs=kwargs, timeout=self.timeout)
        
    def shutdown(self):
        """关闭执行器"""
        self.executor.close()
        self.executor.join()
        logger.debug(f"{self.executor_type}池关闭...")

    def get_executor_info(self):
        """获取执行器综合信息"""
        try:
            if self.executor_type == ExecutorType.THREAD:
                return self._get_thread_pool_info()
            else:
                return self._get_process_pool_info()
        except Exception as e:
            logger.error(f"获取执行器信息失败: {str(e)}")
            return self._get_default_info()

    def _get_thread_pool_info(self):
        """获取线程池信息"""
        try:
            max_workers = getattr(self.executor, "_max_workers", 0)
            threads = getattr(self.executor, "_threads", set())
            active_threads = len([thread for thread in threads if thread.is_alive()])
            total_threads = len(threads)
            idle_threads = max(0, max_workers - active_threads)
            utilization_rate = (
                (active_threads / max_workers) * 100 if max_workers > 0 else 0
            )

            # 获取队列信息
            queue_size = 0
            try:
                queue_size = self.executor._work_queue.qsize()
            except Exception:
                pass

            thread_name_prefix = getattr(
                self.executor, "_thread_name_prefix", "unknown"
            )

            info = {
                "executor_type": "thread",
                "max_workers": max_workers,
                "total_threads": total_threads,
                "active_threads": active_threads,
                "idle_threads": idle_threads,
                "utilization_rate": utilization_rate,
                "queue_size": queue_size,
                "thread_name_prefix": thread_name_prefix,
            }

            logger.info("线程池状态详情:")
            logger.info(f"  - 执行器类型: 线程池")
            logger.info(f"  - 最大工作线程数: {max_workers}")
            logger.info(f"  - 总线程数: {total_threads}")
            logger.info(f"  - 当前活跃线程数: {active_threads}")
            logger.info(f"  - 空闲线程数: {idle_threads}")
            logger.info(f"  - 线程池利用率: {utilization_rate:.2f}%")
            logger.info(f"  - 任务队列大小: {queue_size}")
            logger.info(f"  - 线程名称前缀: {thread_name_prefix}")

            return info
        except Exception as e:
            logger.error(f"获取线程池信息失败: {str(e)}")
            return self._get_default_info()

    def _get_process_pool_info(self):
        """获取进程池信息"""
        try:
            max_workers = getattr(self.executor, "_max_workers", 0)

            # 进程池的信息获取相对简单
            info = {
                "executor_type": "process",
                "max_workers": max_workers,
                "total_processes": max_workers,  # 进程池通常保持固定数量
                "active_processes": max_workers,  # 进程池通常所有进程都在工作
                "idle_processes": 0,
                "utilization_rate": 100.0,  # 进程池通常100%利用
                "queue_size": 0,  # 进程池通常没有队列
                "process_name_prefix": "ProcessPool",
            }

            logger.info("进程池状态详情:")
            logger.info(f"  - 执行器类型: 进程池")
            logger.info(f"  - 最大工作进程数: {max_workers}")
            logger.info(f"  - 总进程数: {max_workers}")
            logger.info(f"  - 当前活跃进程数: {max_workers}")
            logger.info(f"  - 空闲进程数: 0")
            logger.info(f"  - 进程池利用率: 100.0%")
            logger.info(f"  - 任务队列大小: 0")

            return info
        except Exception as e:
            logger.error(f"获取进程池信息失败: {str(e)}")
            return self._get_default_info()

    def _get_default_info(self):
        """获取默认信息"""
        return {
            "executor_type": self.executor_type,
            "max_workers": self.max_workers,
            "total_threads": 0,
            "active_threads": 0,
            "idle_threads": 0,
            "utilization_rate": 0,
            "queue_size": 0,
            "thread_name_prefix": self.thread_name_prefix,
        }

    # 保持向后兼容的方法名
    def get_thread_pool_info(self):
        """保持向后兼容的方法"""
        return self.get_executor_info()
    