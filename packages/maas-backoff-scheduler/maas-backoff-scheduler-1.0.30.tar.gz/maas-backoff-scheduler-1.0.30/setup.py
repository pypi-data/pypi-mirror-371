#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
from setuptools import setup, find_packages

with io.open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="maas-backoff-scheduler",
    version="1.0.30",
    author="xinzhifu",
    author_email="515361725@qq.com",
    description="一个基于Redis的任务退避重试框架，支持多种退避策略和自定义配置",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://192.168.3.118:8082/maas/maas-backoff_scheduler/",
    packages=find_packages(where="."),  # 从项目根目录查找包
    package_dir={"": "."},              # 告诉setuptools包在当前目录中
    include_package_data=True,
    package_data={
        # 确保包内 YAML 被安装
        "backoff": ["conf/*.yaml"],
        "backoff.conf": ["*.yaml"]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "redis>=4.0.0",
        "PyYAML>=6.0",
        "dataclasses>=0.6;python_version<'3.7'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
    },
    keywords="task retry backoff redis queue",
    license="MIT",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/task-backoff-scheduler/issues",
        "Source": "https://github.com/yourusername/task-backoff-scheduler",
        "Documentation": "https://github.com/yourusername/task-backoff-scheduler#readme",
    },
)