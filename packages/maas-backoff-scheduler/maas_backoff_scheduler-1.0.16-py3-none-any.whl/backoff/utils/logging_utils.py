#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志初始化工具
"""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path
from typing import Optional, Union

try:
    import importlib.resources as pkg_res  # Python 3.9+
except Exception:  # pragma: no cover
    pkg_res = None

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


DEFAULT_PACKAGE = "app.conf"
DEFAULT_FILENAME = "logging.config.yaml"

# 全局标志，用于防止重复初始化
_LOGGING_INITIALIZED = False


def init_logging(config_path: Optional[Union[str, Path]] = None, *, fallback_level: int = logging.INFO, force: bool = False) -> None:
    """初始化日志配置。

    优先级：
    1) 指定的 config_path
    2) 包内默认 `task_backoff_framework/app/conf/logging.config.yaml`
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
        
    # 标记为已初始化
    _LOGGING_INITIALIZED = True
    # 优先使用外部传入路径
    if config_path:
        _load_from_path(Path(config_path), fallback_level)
        return

    # 其次尝试包内资源
    if pkg_res is not None and yaml is not None:
        try:
            with pkg_res.files(DEFAULT_PACKAGE).joinpath(DEFAULT_FILENAME).open("r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            logging.config.dictConfig(config)
            # logging.getLogger().debug("Logging configured from package resource: %s/%s", DEFAULT_PACKAGE, DEFAULT_FILENAME)
            return
        except Exception as e:  # pragma: no cover
            # 回退至basicConfig
            logging.basicConfig(level=fallback_level)
            # logging.getLogger().warning("Failed to load logging from package resource: %s. Fallback to basicConfig. err=%s", DEFAULT_FILENAME, e)
            return

    # 最后回退到basicConfig
    logging.basicConfig(level=fallback_level)
    # logging.getLogger().debug("Logging basicConfig initialized at level %s", fallback_level)


def _load_from_path(path: Path, fallback_level: int) -> None:
    if yaml is None:
        logging.basicConfig(level=fallback_level)
        # logging.getLogger().warning("PyYAML not installed. Fallback to basicConfig.")
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
        # logging.getLogger().debug("Logging configured from file: %s", path)
    except Exception as e:  # pragma: no cover
        logging.basicConfig(level=fallback_level)
        # logging.getLogger().warning("Failed to load logging from file: %s. Fallback to basicConfig. err=%s", path, e)