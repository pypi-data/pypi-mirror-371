# 任务退避重试框架

一个基于Redis的任务退避重试框架，支持多种退避策略和自定义配置。

## 功能特点
- 基于Redis的分布式任务队列
- 支持多种退避策略（固定间隔、指数退避、线性退避等）
- 支持任务优先级
- 支持任务超时和失败处理
- 支持并发执行任务（线程池/进程池）
- 支持任务状态管理和监控

## 打包上传

```bash
python  setup.py sdist bdist_wheel

twine upload dist/*

pip3.10 install maas-backoff-scheduler==1.0.23

更新包
pip3 install --upgrade .
```
## 安装说明

### 使用pip安装
```bash
pip install backoff_scheduler
```

### 从源码安装
```bash
# 克隆项目
git clone https://github.com/yourusername/backoff_scheduler.git
cd backoff_scheduler

# 安装依赖
pip install -r requirements.txt

# 安装包
python setup.py install
```

## 快速开始

```python
from backoff_scheduler import TaskBackoffFramework, TaskEntity, BackoffConfig
from backoff_scheduler.common.task_entity import BackoffStrategy

# 初始化配置
config = BackoffConfig(
    redis_host='localhost',
    redis_port=6379,
    redis_db=0,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    max_retries=5,
    initial_delay=1000,
    max_delay=30000
)

# 初始化框架
framework = TaskBackoffFramework(config)

# 定义任务处理函数
def task_handler(task_entity, params):
    # 任务处理逻辑
    print(f"处理任务: {task_entity.task_id}, 参数: {params}")
    # 模拟任务成功
    return {"status": "success", "result": "任务处理完成"}

# 设置任务处理器
framework.set_task_handler(task_handler)

# 创建任务
params = {"data": "需要处理的数据"}
 task_id = framework.create_task(params)

# 启动框架
framework.start()

# 等待任务完成
import time
time.sleep(10)

# 获取任务结果
result = framework.get_task_result(task_id)
print(f"任务结果: {result}")

# 停止框架
framework.stop()
```

## 配置说明

### BackoffConfig 参数
- `redis_host`: Redis主机地址
- `redis_port`: Redis端口
- `redis_db`: Redis数据库索引
- `backoff_strategy`: 退避策略（FIXED, EXPONENTIAL, LINEAR）
- `max_retries`: 最大重试次数
- `initial_delay`: 初始延迟时间（毫秒）
- `max_delay`: 最大延迟时间（毫秒）
- `executor_type`: 执行器类型（THREAD, PROCESS）
- `max_workers`: 最大工作线程/进程数

## 高级使用

### 自定义退避策略
```python
from backoff_scheduler.common.task_entity import BackoffStrategy
from backoff_scheduler.core.backoff_strategy import BaseBackoffStrategy

class CustomBackoffStrategy(BaseBackoffStrategy):
    def calculate_delay(self, retry_count):
        # 自定义退避算法
        return min(1000 * (retry_count ** 2), 30000)

# 注册自定义策略
BackoffStrategy.register('CUSTOM', CustomBackoffStrategy)

# 使用自定义策略
config = BackoffConfig(
    backoff_strategy=BackoffStrategy.CUSTOM,
    # 其他配置...
)
```

### 任务异常处理
```python
def exception_handler(task_entity, params):
    # 异常处理逻辑
    print(f"任务 {task_entity.task_id} 执行失败: {params}")

# 设置异常处理器
framework.set_exception_handler(exception_handler)
```

## 项目结构
```
app/
├── common/       # 公共模块
├── conf/         # 配置文件
├── core/         # 核心功能
├── models/       # 数据模型
├── scheduler/    # 调度器
└── utils/        # 工具函数
```

## 贡献指南
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/fooBar`)
3. 提交更改 (`git commit -am 'Add some fooBar'`)
4. 推送到分支 (`git push origin feature/fooBar`)
5. 创建新的 Pull Request

## 许可证
本项目采用 MIT 许可证 - 详情请见 LICENSE 文件

## 联系方式
如有问题或建议，请联系: xinzf@ucap.com.cn