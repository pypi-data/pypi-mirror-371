#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志初始化工具
"""

import logging
import logging.config
import os

try:
    import importlib.resources as pkg_res  # Python 3.9+
except Exception:  # pragma: no cover
    pkg_res = None

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


DEFAULT_PACKAGE = "backoff.conf"
DEFAULT_FILENAME = "logging.config.yaml"

# 全局标志，用于防止重复初始化
_LOGGING_INITIALIZED = False


def init_logging(config_path=None, fallback_level=logging.INFO, force=False):
    """初始化日志配置。

    优先级：
    1) 指定的 config_path
    2) 包内默认 `backoff/conf/logging.config.yaml`
    3) 回退到 basicConfig
    
    Args:
        config_path: 日志配置文件路径，可选
        fallback_level: 回退日志级别，默认为 INFO
        force: 是否强制重新初始化，默认为 False
    """
    global _LOGGING_INITIALIZED
    
    # 如果已经初始化过且不强制重新初始化，则直接返回
    if _LOGGING_INITIALIZED and not force:
        # logging.getLogger().debug("Logging already initialized, skipping.")
        return
    
    # 如果强制重新初始化，清除现有的日志配置
    if force:
        # 清除根日志器的处理器
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 清除所有已命名日志器的处理器
        for name in logging.root.manager.loggerDict:
            logger = logging.getLogger(name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
        
        # 重置标志
        _LOGGING_INITIALIZED = False
        
    # 标记为已初始化
    _LOGGING_INITIALIZED = True
        
    # 优先使用外部传入路径
    if config_path:
        _load_from_path(config_path, fallback_level)
        return

    # 其次尝试包内资源
    if pkg_res is not None and yaml is not None:
        try:
            # 兼容Python 2.7的资源加载方式
            config_file = pkg_res.resource_filename(DEFAULT_PACKAGE, DEFAULT_FILENAME)
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
            logging.config.dictConfig(config)
            return
        except Exception as e:  # pragma: no cover
            # 回退至basicConfig
            logging.basicConfig(level=fallback_level)
            return

    # 最后回退到basicConfig
    logging.basicConfig(level=fallback_level)
    # logging.getLogger().debug("Logging basicConfig initialized at level %s", fallback_level)


def _load_from_path(path, fallback_level):
    if yaml is None:
        logging.basicConfig(level=fallback_level)
        # logging.getLogger().warning("PyYAML not installed. Fallback to basicConfig.")
        return
    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
        # logging.getLogger().debug("Logging configured from file: %s", path)
    except Exception as e:  # pragma: no cover
        logging.basicConfig(level=fallback_level)
        # logging.getLogger().warning("Failed to load logging from file: %s. Fallback to basicConfig. err=%s", path, e)


def auto_init_logging():
    """自动初始化日志配置，使用包内默认配置文件"""
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取包根目录 (从 utils 目录向上两级到 backoff 目录)
    package_root = os.path.dirname(os.path.dirname(current_dir))
    # 构建配置文件路径
    config_path = os.path.join(package_root, 'backoff', 'conf', 'logging.config.yaml')
    
    # 如果配置文件存在，使用它；否则使用默认配置
    if os.path.exists(config_path):
        init_logging(config_path)
    else:
        # 尝试其他可能的路径
        alt_path = os.path.join(package_root, 'conf', 'logging.config.yaml')
        if os.path.exists(alt_path):
            init_logging(alt_path)
        else:
            init_logging()  # 使用默认配置