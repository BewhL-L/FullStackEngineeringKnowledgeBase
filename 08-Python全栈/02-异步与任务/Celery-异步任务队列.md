---
title: Celery-异步任务队列
category: Python全栈
tags: [Python, Redis, RabbitMQ, 分布式, 异步, 异步任务, 消息队列, 定时任务, Flower]
priority: P1
status: completed
created: 2026-09-10
updated: 2026-09-10
version: 2.0
author: BewhY_L
pre: ["[[Python-异步编程asyncio]]", "[[Redis-Python客户端与缓存策略]]"]
description: Celery分布式任务队列完整知识体系，涵盖架构原理、Broker选型、任务定义调用、编排工作流、定时任务、Worker管理、监控部署与性能优化
---

# Celery 异步任务队列深度指南

> **文档定位**：本文是 Python 生态最流行分布式任务队列 Celery 的系统化深度教程，从架构原理到生产部署全覆盖。无论你是刚接触 Celery 的初学者，还是需要在生产环境中优化任务系统的资深工程师，都能从中找到所需内容。
>
> **学习目标**：掌握 Celery 四阶段架构（Producer→Broker→Worker→Backend）、任务定义与调用、任务编排（chain/group/chord）、定时任务调度、Worker 并发模型、Flower 监控、FastAPI/Django 集成、生产部署与性能优化。
>
> **前置知识**：Python 基础语法、异步编程概念、Redis 基本操作、消息队列原理

---

## 一、概述与学习路径

### 1.1 什么是 Celery

**概念解释**：Celery 是一个简单、灵活且可靠的分布式任务队列系统，专注于实时处理和任务调度。它是 Python 生态中使用最广泛的异步任务框架，被 Instagram、Pinterest、Udemy 等公司大规模用于生产环境。

**生活化比喻**：把 Celery 想象成一家外卖餐厅——顾客（Producer）下单后不需要站在厨房等菜，而是拿着取餐号（task_id）去做别的事；服务员（Broker）把订单放到出餐队列；厨师（Worker）按队列顺序做菜；做完后把菜和小票（Result Backend）放在取餐台，顾客随时可以凭取餐号取餐。

**核心价值**：将耗时操作从主业务流程中剥离，实现异步执行、系统解耦、流量削峰和定时调度。

```python
# 最简 Celery 应用示例（app.py）
from celery import Celery

# 创建 Celery 实例，指定 Broker 地址
app = Celery(
    'hello',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1',
)

# 定义一个任务
@app.task
def add(x, y):
    return x + y

# 预期结果：启动 Worker 后，在 Python REPL 中执行
# >>> from app import add
# >>> result = add.delay(4, 6)
# >>> result.get()
# 10
```

```bash
# 启动 Worker（另一个终端）
celery -A app worker --loglevel=info
# 预期输出：
# celery@hostname v5.x.x ready.
# [tasks]
#   . app.add
```

> 🎯 **面试高频**：Celery 的核心架构组件有哪些？各自职责是什么？
>
> 答案：Producer（生产者，发布任务）、Broker（消息中间件，存储和路由任务）、Worker（消费者，执行任务）、Result Backend（结果存储）、Celery Beat（定时调度器）。

### 1.2 为什么需要异步任务队列

**概念解释**：异步任务队列是一种设计模式，将耗时操作放入队列后台执行，主流程立即返回，从而提升系统响应速度和吞吐量。

**痛点对比**：

| 场景 | 同步执行的问题 | 异步队列的解决方案 |
|------|--------------|-------------------|
| 发送邮件/短信 | 用户等待 2-5 秒 | 立即返回，后台异步发送 |
| 生成报表/PDF | 请求超时 | 提交后轮询或通知完成 |
| 图片/视频处理 | 占用 Web 服务器线程 | Worker 独立处理，水平扩展 |
| 批量数据导入 | 接口超时 | 分批异步处理，进度可查 |
| 第三方 API 调用 | 对方慢导致连锁超时 | 异步调用，失败自动重试 |
| 定时任务 | cron 脚本难管理 | Beat 统一调度，状态可监控 |

**不适用场景**：
- 操作极快（<10ms）且无需异步——直接同步调用更简单
- 需要立即获取结果的操作——同步调用更直接
- 简单脚本任务——无需引入额外复杂度

### 1.3 核心应用场景总览

```mermaid
flowchart TD
    A[异步任务队列应用场景] --> B[异步处理]
    A --> C[系统解耦]
    A --> D[流量削峰]
    A --> E[定时任务]
    A --> F[分布式计算]
    A --> G[延迟任务]

    B --> B1[发送邮件/短信]
    B --> B2[生成PDF/报表]
    B --> B3[图片处理/视频转码]

    C --> C1[订单创建→通知/积分/统计]
    C --> C2[用户注册→欢迎流程]

    D --> D1[秒杀下单缓冲]
    D --> D2[批量数据导入]

    E --> E1[每日报表生成]
    E --> E2[数据同步/日志清理]

    F --> F1[大规模数据处理]
    F --> F2[分布式爬虫]

    G --> G1[订单超时取消]
    G --> G2[预约提醒]

    style A fill:#667eea,color:#fff
    style B fill:#f093fb,color:#fff
    style C fill:#4facfe,color:#fff
    style D fill:#43e97b,color:#333
```

### 1.4 学习路线图

```text
Celery 学习路线：

第一阶段：基础入门
  ├── 安装与配置（Redis/RabbitMQ Broker）
  ├── 定义第一个任务（@app.task）
  ├── 调用任务（delay / apply_async）
  └── 查询任务结果（AsyncResult）

第二阶段：核心进阶
  ├── 任务路由与队列
  ├── 任务重试与超时
  ├── 任务编排（chain / group / chord）
  ├── 定时任务（Celery Beat / crontab）
  └── 任务优先级

第三阶段：生产实战
  ├── Worker 并发模型（prefork / gevent）
  ├── Flower 监控
  ├── FastAPI / Django 集成
  ├── 生产部署（Systemd / Docker）
  └── 性能优化与故障排查

第四阶段：深入理解
  ├── ACK 机制与消息可靠性
  ├── 任务幂等性设计
  ├── 任务序列化协议
  └── 信号系统与钩子
```

```python
# 完整的幂等任务实现（Redis SETNX + 状态机）
import redis
from celery_app import app

redis_client = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

@app.task(bind=True, max_retries=3, autoretry_for=(ConnectionError,))
def process_payment(self, payment_id: str, amount: float, user_id: int) -> dict:
    """
    幂等支付处理任务
    确保同一 payment_id 只被处理一次
    """
    lock_key = f"lock:payment:{payment_id}"
    result_key = f"result:payment:{payment_id}"

    # 1. 检查是否已有结果（完全幂等）
    cached = redis_client.get(result_key)
    if cached:
        return {"status": "cached", "payment_id": payment_id, "result": cached}

    # 2. 获取处理锁（NX = 不存在才设置）
    acquired = redis_client.set(lock_key, "processing", nx=True, ex=300)
    if not acquired:
        # 已有其他 Worker 在处理，等待后重试
        raise self.retry(countdown=10)

    try:
        # 3. 执行支付逻辑
        result = payment_gateway.charge(
            payment_id=payment_id,
            amount=amount,
            user_id=user_id,
        )

        # 4. 存储结果（保留24小时）
        redis_client.setex(result_key, 86400, str(result.transaction_id))

        return {
            "status": "success",
            "payment_id": payment_id,
            "transaction_id": result.transaction_id,
        }

    except InsufficientFundsError:
        # 业务错误：不重试，记录后返回
        redis_client.setex(result_key, 86400, "insufficient_funds")
        return {"status": "failed", "reason": "insufficient_funds"}

    except Exception as exc:
        # 系统错误：清除锁，允许重试
        redis_client.delete(lock_key)
        raise self.retry(exc=exc, countdown=30)
```

```python
# 幂等性设计的另一种方案：数据库唯一约束
# 适合不需要 Redis 的简单场景
from sqlalchemy import Column, String, DateTime, UniqueConstraint
from datetime import datetime

class TaskResult(db.Model):
    """任务结果表：用唯一约束保证幂等"""
    __tablename__ = 'task_results'
    __table_args__ = (
        UniqueConstraint('task_type', 'business_id', name='uq_task_biz'),
    )

    id = Column(db.Integer, primary_key=True)
    task_type = Column(String(50), nullable=False)
    business_id = Column(String(100), nullable=False)
    status = Column(String(20), default='pending')  # pending/done/failed
    result = Column(db.Text)
    created_at = Column(DateTime, default=datetime.utcnow)


@app.task(bind=True)
def process_order_idempotent(self, order_id: str):
    """使用数据库唯一约束实现幂等"""
    # 尝试插入记录（如果已存在则说明已处理过）
    existing = TaskResult.query.filter_by(
        task_type='process_order',
        business_id=order_id
    ).first()

    if existing and existing.status == 'done':
        return {"status": "already_processed", "result": existing.result}

    if existing and existing.status == 'pending':
        # 正在处理中，稍后重试
        raise self.retry(countdown=5)

    # 创建新记录
    record = TaskResult(
        task_type='process_order',
        business_id=order_id,
        status='pending',
    )
    db.session.add(record)
    db.session.commit()

    try:
        result = do_process_order(order_id)
        record.status = 'done'
        record.result = str(result)
        db.session.commit()
        return {"status": "success", "result": result}
    except Exception as exc:
        record.status = 'failed'
        db.session.commit()
        raise
```

> ✅ **最佳实践**：幂等性是异步任务的硬性要求。两种主流方案：(1) Redis SETNX 去重锁——高性能、适合高并发场景；(2) 数据库唯一约束——强一致性、不需要额外组件。选择原则：读多写少用数据库方案，高并发写多用 Redis 方案。

> 💡 **深度讲解**：Celery 架构的本质是分布式消息传递系统。理解它的关键在于理解"解耦"——生产者不需要知道谁来执行任务、在哪里执行、执行多久，只需要把消息扔到 Broker；消费者不需要知道任务从哪来、为什么执行，只需要从队列里取任务执行。这种解耦带来了系统的灵活性、可扩展性和容错能力。

> 📝 **本章精简总结**：
> - 核心概念：Celery = 分布式任务队列，四阶段架构（Producer→Broker→Worker→Backend）
> - 关键原理：生产者消费者解耦、任务持久化、水平扩展
> - 常用操作：`@app.task` 定义任务、`delay()` 调用、`get()` 获取结果
> - 最佳实践：生产环境开启 `task_acks_late`、任务幂等设计
> - 常见坑点：Worker 不消费先查 Broker 连接、Beat 只能单实例
> - 面试高频：Celery 架构组件、Broker 选型、Worker 并发模型

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：Celery 的四大核心组件是什么？各自的职责？
>   - 答案：Producer（发布任务）、Broker（消息中间件）、Worker（执行任务）、Result Backend（存储结果）
> - **基础题（⭐）**：`task.delay()` 和 `task.apply_async()` 有什么区别？
>   - 答案：delay 是简化版，apply_async 支持 countdown、eta、queue、priority 等高级参数
> - **进阶题（⭐⭐）**：为什么生产环境必须开启 `task_acks_late=True`？如果不开启会怎样？
>   - 思考方向：从 ACK 时机、Worker 崩溃场景、消息丢失风险角度分析
> - **实战题（⭐⭐⭐）**：设计一个用户注册后的异步流程：发送欢迎邮件→7天后发送回访问卷→30天后发送满意度调查。要求任务可重试、可追踪。
>   - 提示：使用 chain 编排三个任务，用 countdown 控制延迟，配置 max_retries 和 autoretry_for

---

## 二、核心架构与工作原理

### 2.1 四阶段架构详解

**概念解释**：Celery 采用经典的生产者-消费者架构，分为四个阶段：任务生产、消息存储、任务消费、结果存储。每个阶段独立部署、水平扩展，通过消息中间件解耦。

**原理说明**：当 Producer 调用 `task.delay()` 时，Celery 将任务名、参数、ETA 等信息序列化为消息体，通过 AMQP 或 Redis 协议发送到 Broker。Broker 将消息持久化到队列中。Worker 进程从队列中 BLPOP（Redis）或 Basic.Consume（RabbitMQ）获取消息，反序列化后执行任务函数，最后将返回值序列化存储到 Result Backend。

```mermaid
flowchart LR
    subgraph 生产者端
        P[Web应用/脚本<br/>Producer]
    end

    subgraph Broker
        Q1[Queue: default]
        Q2[Queue: email]
        Q3[Queue: report]
    end

    subgraph Worker集群
        W1[Worker-1<br/>prefork]
        W2[Worker-2<br/>prefork]
        W3[Worker-3<br/>gevent]
    end

    subgraph 结果存储
        R[(Result Backend<br/>Redis/DB)]
    end

    P -->|发布任务消息| Q1
    P -->|路由到email队列| Q2
    P -->|路由到report队列| Q3
    Q1 --> W1
    Q2 --> W2
    Q3 --> W3
    W1 -->|存储结果| R
    W2 -->|存储结果| R
    W3 -->|存储结果| R

    Beat[Celery Beat<br/>定时调度器] -->|定时发布| Q1

    style P fill:#667eea,color:#fff
    style Q1 fill:#f093fb,color:#fff
    style Q2 fill:#f093fb,color:#fff
    style Q3 fill:#f093fb,color:#fff
    style W1 fill:#4facfe,color:#fff
    style W2 fill:#4facfe,color:#fff
    style W3 fill:#4facfe,color:#fff
    style R fill:#43e97b,color:#333
    style Beat fill:#fa709a,color:#fff
```

**组件职责对照表**：

| 组件 | 职责 | 可选技术 | 部署方式 |
|------|------|---------|---------|
| Producer | 发布任务 | Web应用/脚本/Beat | 应用进程内 |
| Broker | 存储和路由任务消息 | Redis / RabbitMQ / SQS | 独立服务 |
| Worker | 执行任务 | Celery Worker 进程 | 独立机器/容器 |
| Result Backend | 存储任务结果和状态 | Redis / Database / MongoDB | 独立服务 |
| Celery Beat | 定时发布任务 | Celery Beat 进程 | 单实例独立部署 |

### 2.2 Broker 消息中间件深度对比

**概念解释**：Broker 是 Celery 的消息中枢，负责接收、存储、路由和分发任务消息。它是生产者和消费者之间的缓冲区，解耦两端并提供持久化保证。

**原理说明**：不同 Broker 实现机制不同。Redis 使用 List 数据结构存储任务（LPUSH 推入、BRPOP 弹出），支持 ZSet 实现延迟任务；RabbitMQ 实现 AMQP 协议，通过 Exchange→Binding→Queue 模型实现灵活路由，支持消息确认、持久化、死信队列。

```python
# Redis Broker 配置示例
broker_url = 'redis://:password@localhost:6379/0'

# Redis Sentinel 高可用配置
broker_url = 'sentinel://:password@localhost:26379/0;sentinel-master=mymaster'
broker_transport_options = {
    'master_name': 'mymaster',
    'sentinel_kwargs': {'password': 'password'},
}

# RabbitMQ Broker 配置
broker_url = 'amqp://user:password@localhost:5672//'

# RabbitMQ 带虚拟主机
broker_url = 'amqp://user:password@localhost:5672/myvhost'
```

| 对比维度 | Redis | RabbitMQ |
|---------|-------|----------|
| 部署复杂度 | 极低（单二进制） | 中等（Erlang 运行时） |
| 性能 | 极高（内存操作） | 高（但略低于 Redis） |
| 消息持久化 | RDB/AOF（最终一致） | 可靠（写盘后才确认） |
| 路由能力 | 简单（队列名匹配） | 丰富（Exchange 类型） |
| 优先级支持 | 支持（0-9） | 支持（需队列声明） |
| 延迟任务 | ZSet 实现 | 原生支持（TTL+DLX） |
| 死信队列 | 不支持 | 原生支持 |
| 高可用 | Sentinel/Cluster | 镜像队列/Quorum Queue |
| 内存占用 | 高（数据全在内存） | 中等 |
| 适用规模 | 中小规模 | 大规模生产环境 |

> ✅ **最佳实践**：中小项目和初创团队选 Redis（运维简单、性能足够）；大规模、高可靠要求选 RabbitMQ（消息可靠性、路由能力更强）。已有 Redis 基础设施的团队优先复用。

```python
# Broker 连接参数配置（生产环境）
app.conf.update(
    # Broker 连接重试
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,

    # Broker 心跳（防止空闲连接断开）
    broker_heartbeat=30,

    # 传输选项
    broker_transport_options={
        # Redis：可见性超时（Worker 崩溃后消息多久重新投递）
        'visibility_timeout': 3600,  # 1小时

        # RabbitMQ：预取计数
        # 'confirm_publish': True,  # 发布确认
    },
)
```

```python
# RabbitMQ 高级配置：死信队列（Dead Letter Exchange）
# 用于处理失败任务的重试和死信
app.conf.update(
    # RabbitMQ 传输选项
    broker_transport_options={
        # 队列声明参数
        'queue_args': {
            'x-dead-letter-exchange': 'dlx',  # 死信交换机
            'x-dead-letter-routing-key': 'dead',
            'x-max-priority': 10,  # 最大优先级
        },
    },
)

# 死信队列消费：处理多次重试仍失败的任务
# 生产环境推荐使用 RabbitMQ 的 DLX 机制
# 任务被拒绝（reject/requeue=false）后自动进入死信队列
```

```python
# Redis Broker 的 visibility_timeout 详解
# visibility_timeout 是 Redis Broker 特有的概念
# Worker 取出任务后，Redis 将消息放入一个 "unacked" 集合
# 在 visibility_timeout 内，Worker 需要 ACK
# 如果超时未 ACK，消息重新放回队列

app.conf.update(
    broker_transport_options={
        # 默认 3600 秒（1小时）
        # 如果任务执行时间可能超过1小时，必须调大
        'visibility_timeout': 7200,  # 2小时
    },
)

# 计算建议：visibility_timeout > 任务最大执行时间 × 2
# 例如：任务最大执行时间 30 分钟 → visibility_timeout = 3600
```

```python
# 任务序列化协议对比
# Celery 支持的序列化格式：
# json（默认推荐）：跨语言、安全、人类可读
# pickle：Python 专属、安全风险（可执行任意代码）
# msgpack：二进制、紧凑、高性能
# yaml：可读性好但安全性较低

# 使用 msgpack 提升性能
app.conf.update(
    task_serializer='msgpack',
    accept_content=['msgpack', 'json'],  # 兼容旧格式
    result_serializer='msgpack',
)

# ⚠️ 安全警告：永远不要在公网传输中使用 pickle
# pickle 反序列化可以执行任意代码，存在远程代码执行风险
```

> ❌ **常见坑点**：Redis Broker 的 `visibility_timeout` 设置不当会导致任务重复执行。如果任务执行时间超过 `visibility_timeout`（默认1小时），消息会被重新投递到另一个 Worker，导致同一任务被执行两次。**正确做法**：将 `visibility_timeout` 设为任务最大执行时间的 2 倍以上。

### 2.3 任务生命周期与状态机

**概念解释**：Celery 任务从发布到终结经历多个状态，形成一个状态机。理解状态流转对于调试任务问题至关重要。

```mermaid
stateDiagram-v2
    [*] --> PENDING: 任务发布(delay/apply_async)
    PENDING --> RECEIVED: Worker拉取消息
    RECEIVED --> STARTED: Worker开始执行
    STARTED --> SUCCESS: 执行成功
    STARTED --> FAILURE: 执行异常
    STARTED --> RETRY: 触发重试条件
    RETRY --> PENDING: 重新入队等待
    STARTED --> REVOKED: 被revoke撤销
    SUCCESS --> [*]: 结果存储到Backend
    FAILURE --> [*]: 异常信息存储到Backend
    REVOKED --> [*]: 标记撤销

    note right of PENDING
        PENDING 也可能表示
        任务不存在（task_id无效）
        这是一个设计陷阱
    end note
```

```python
# 任务状态查询代码示例
from celery.result import AsyncResult
from your_celery_app import app

def inspect_task(task_id: str) -> dict:
    """
    完整的任务状态查询
    """
    result = AsyncResult(task_id, app=app)

    # 状态中文映射
    status_map = {
        'PENDING': '等待中（任务未被Worker接收）',
        'RECEIVED': '已接收（Worker已获取）',
        'STARTED': '执行中（Worker正在运行）',
        'SUCCESS': '执行成功',
        'FAILURE': '执行失败',
        'RETRY': '重试中（等待下次执行）',
        'REVOKED': '已撤销',
    }

    info = {
        'task_id': task_id,
        'status': result.status,
        'status_cn': status_map.get(result.status, '未知状态'),
        'ready': result.ready(),        # 是否已结束（成功/失败/撤销）
        'successful': result.successful(),  # 是否成功
        'failed': result.failed(),      # 是否失败
    }

    # 根据状态获取详情
    if result.successful():
        info['result'] = result.result       # 任务返回值
        info['date_done'] = result.date_done  # 完成时间
    elif result.failed():
        info['traceback'] = result.traceback  # 完整错误堆栈
        info['result'] = result.result        # 异常对象
    elif result.status == 'RETRY':
        info['result'] = result.result        # 触发重试的异常
        # 下次重试时间需要通过调度器查询

    return info

# 预期使用方式：
# info = inspect_task('abc-123-def')
# print(f"状态: {info['status_cn']}")
```

> ❌ **常见坑点**：PENDING 状态有歧义——它既表示"任务等待执行"，也表示"task_id 不存在"。当你查询一个不存在的 task_id 时，Celery 不会报错，而是返回 PENDING。**正确做法**：不要仅靠 PENDING 判断任务是否存在，应在发布任务时就记录 task_id 到数据库，或使用 Flower 确认任务已注册。

### 2.4 ACK 机制与消息可靠性

**概念解释**：ACK（Acknowledgment）机制是 Celery 保证任务不丢失的核心机制。Worker 从 Broker 取到任务后，Broker 不会立即删除消息，而是等待 Worker 的 ACK 确认后才删除。

**原理说明**：
- **早 ACK（默认行为）**：Worker 收到消息就 ACK，然后执行任务。如果 Worker 在执行过程中崩溃，消息已被 ACK，任务丢失。
- **晚 ACK（`task_acks_late=True`）**：Worker 执行完任务才 ACK。如果 Worker 崩溃，消息未被 ACK，Broker 会将消息重新投递给其他 Worker。

```python
# 生产环境推荐的 ACK 配置
app.conf.update(
    task_acks_late=True,                    # 执行完成后才 ACK
    task_reject_on_worker_lost=True,        # Worker 异常退出时 reject 消息
    task_acks_on_failure_or_timeout=True,   # 任务失败也 ACK（不再重试）
)
```

```python
# 任务失败但不重试的场景
@app.task(acks_late=True, reject_on_worker_lost=True)
def critical_task(task_id):
    """关键任务：Worker 崩溃后任务不会丢失"""
    try:
        do_critical_work(task_id)
    except SpecificRecoverableError:
        # 可恢复错误：不 ACK，让其他 Worker 重新执行
        raise  # 重新抛出，Celery 会根据 max_retries 处理
    except SpecificFatalError:
        # 致命错误：ACK 确认，不再重试
        # 这种情况下任务会标记为 FAILURE
        logger.error(f"任务 {task_id} 致命失败")
        raise
```

> ✅ **最佳实践**：
> 1. 所有生产环境任务必须开启 `task_acks_late=True`
> 2. 配合 `task_reject_on_worker_lost=True` 确保 Worker 被 kill 时任务重新入队
> 3. 任务必须设计为幂等的（幂等性详见后续章节）
> 4. Redis Broker 注意 `visibility_timeout` 要大于任务最大执行时间

### 2.5 Worker 并发模型

**概念解释**：Celery Worker 支持多种并发模型，决定了 Worker 如何同时处理多个任务。选择合适的并发模型对性能至关重要。

```python
# Worker 启动时指定并发模型
# prefork（默认，多进程）
# celery -A app worker --pool=prefork --concurrency=8

# gevent（协程，IO密集型）
# celery -A app worker --pool=gevent --concurrency=1000

# eventlet（协程，另一个选择）
# celery -A app worker --pool=eventlet --concurrency=1000

# solo（单线程，调试用）
# celery -A app worker --pool=solo --loglevel=debug
```

| 并发模型 | 底层机制 | 适用场景 | 内存开销 | 并发上限 |
|---------|---------|---------|---------|---------|
| **prefork** | multiprocessing 多进程 | CPU 密集型任务 | 高（每进程独立内存） | CPU 核心数 × 2~4 |
| **gevent** | 协程 + monkey patch | IO 密集型任务 | 极低 | 数千~数万 |
| **eventlet** | 协程（eventlet 库） | IO 密集型任务 | 极低 | 数千~数万 |
| **solo** | 单进程单线程 | 调试 / 简单任务 | 最低 | 1 |

```python
# gevent 模式下的猴子补丁（必须在最顶部）
# 文件：celery_gevent.py
from gevent import monkey
monkey.patch_all()  # ⚠️ 必须在 import celery/requests/psycopg2 之前

from celery import Celery

app = Celery('gevent_demo', broker='redis://localhost:6379/0')

@app.task
def fetch_url(url):
    """IO 密集型任务：HTTP 请求，适合 gevent"""
    import requests
    resp = requests.get(url, timeout=10)
    return resp.status_code

# 启动：celery -A celery_gevent worker --pool=gevent --concurrency=1000
# 预期效果：1000 个并发 HTTP 请求不阻塞，内存仅占用几十 MB
```

> ❌ **常见坑点**：gevent 模式下忘记打猴子补丁（`monkey.patch_all()`）。后果：requests、socket 等库仍是同步阻塞的，协程退化为串行执行，性能反而比 prefork 更差。**正确做法**：在所有 import 之前打补丁，或使用 `celery -P gevent` 自动打补丁。

> 💡 **深度讲解**：理解 Celery 架构的关键在于理解"消息传递"这一核心抽象。Broker 是整个系统的枢纽，它的选型直接影响系统的可靠性、性能和运维复杂度。ACK 机制保证了至少一次投递（at-least-once），这意味着任务可能被重复执行——这就是为什么幂等性如此重要。Worker 并发模型的选择本质上是在 CPU 密集和 IO 密集之间做权衡：多进程利用多核但内存开销大，协程轻量但需要避免阻塞调用。

> 📝 **本章精简总结**：
> - 核心概念：四阶段架构、Broker/Backend、任务状态机、ACK 机制
> - 关键原理：生产者解耦、晚 ACK 保证不丢消息、可见性超时防重复
> - 常用操作：Broker 配置、Worker 并发模型选择、任务状态查询
> - 最佳实践：`task_acks_late=True`、Redis `visibility_timeout` 调大
> - 常见坑点：PENDING 歧义、gevent 忘打猴子补丁
> - 面试高频：Broker 选型对比、ACK 机制、prefork vs gevent

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：Redis 和 RabbitMQ 作为 Broker 各有什么优缺点？
>   - 答案：Redis 部署简单性能好但持久化弱；RabbitMQ 功能完善但部署复杂
> - **基础题（⭐）**：任务有哪些状态？PENDING 有什么陷阱？
>   - 答案：PENDING/RECEIVED/STARTED/SUCCESS/FAILURE/RETRY/REVOKE；PENDING 也表示任务不存在
> - **进阶题（⭐⭐）**：为什么 `task_acks_late=True` 可能导致任务重复执行？如何解决？
>   - 思考方向：Worker 执行完但 ACK 前网络中断→消息重新投递→任务执行两次
> - **实战题（⭐⭐⭐）**：为一个图片处理任务选择合适的并发模型。任务需要下载图片（IO）、调用 CPU 做滤镜处理（CPU）、上传到 CDN（IO）。如何设计？
>   - 提示：考虑拆分队列——下载和上传用 gevent，滤镜处理用 prefork

---

## 三、安装与基础配置

### 3.1 安装与依赖管理

**概念解释**：Celery 的安装非常简单，但不同的 Broker 和 Backend 需要额外的依赖包。正确安装所有可选依赖是避免运行时错误的第一步。

```bash
# 基础安装（仅核心功能）
pip install celery

# 安装 Redis Broker 支持
pip install celery[redis]

# 安装 RabbitMQ Broker 支持
pip install celery[rabbitmq]

# 同时安装所有常用依赖
pip install celery[redis,rabbitmq,msgpack,yaml]

# 使用 pip-tools / poetry 管理依赖
# pyproject.toml 示例
# [tool.poetry.dependencies]
# celery = { version = "^5.3", extras = ["redis"] }
# flower = "^2.0"
```

```bash
# 验证安装
python -c "import celery; print(celery.__version__)"
# 预期输出：5.3.x 或更高版本

# 验证 Redis 可用
python -c "from celery.backends.redis import RedisBackend; print('Redis backend OK')"
# 预期输出：Redis backend OK
```

### 3.2 创建 Celery 应用实例

**概念解释**：Celery 应用（Application）是 Celery 的核心对象，它代表一个 Celery 项目，包含配置、任务注册、Broker 连接等。每个项目应该有一个唯一的 Celery 实例。

```python
# celery_app.py —— 生产推荐的应用初始化方式
import os
from celery import Celery
from celery.signals import task_prerun, task_postrun
import logging

logger = logging.getLogger(__name__)

# 从环境变量读取配置（12-Factor App 最佳实践）
def create_celery_app() -> Celery:
    """工厂模式创建 Celery 应用"""
    app = Celery(
        'myapp',
        broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
        include=['tasks.email', 'tasks.report', 'tasks.data'],
    )

    # 加载配置模块
    app.config_from_object('celery_config')

    # 注册信号处理器
    register_signals(app)

    return app


def register_signals(app: Celery):
    """注册任务信号"""

    @task_prerun.connect
    def log_task_start(sender=None, task_id=None, args=None, kwargs=None, **kw):
        logger.info(f"任务开始: {sender.name}[{task_id}] args={args}")

    @task_postrun.connect
    def log_task_end(sender=None, task_id=None, state=None, **kw):
        logger.info(f"任务结束: {sender.name}[{task_id}] state={state}")


# 全局应用实例（Worker 启动时使用）
app = create_celery_app()
```

```python
# celery_config.py —— 配置文件
"""
Celery 配置文件
所有配置项参考：https://docs.celeryq.dev/en/stable/userguide/configuration.html
"""

# ============ Broker 配置 ============
broker_url = 'redis://localhost:6379/0'
broker_connection_retry_on_startup = True

# ============ 结果 Backend ============
result_backend = 'redis://localhost:6379/1'
result_expires = 3600  # 结果 1 小时后自动删除
result_serializer = 'json'
result_compression = 'gzip'  # 大结果自动压缩

# ============ 序列化 ============
task_serializer = 'json'
accept_content = ['json']
# ⚠️ 不要使用 pickle（安全风险 + 跨语言不兼容）

# ============ 时区 ============
timezone = 'Asia/Shanghai'
enable_utc = True

# ============ 任务可靠性 ============
task_acks_late = True
task_reject_on_worker_lost = True

# ============ Worker 配置 ============
worker_max_tasks_per_child = 1000       # 子进程执行1000任务后重启（防内存泄漏）
worker_max_memory_per_child = 200000    # 子进程内存上限 200MB（单位 KB）
worker_prefetch_multiplier = 4           # 预取任务数
worker_concurrency = 8                   # 默认并发数

# ============ 任务默认值 ============
task_default_retry_delay = 30
task_default_max_retries = 3
task_soft_time_limit = 300   # 5 分钟软超时
task_time_limit = 600        # 10 分钟硬超时
```

### 3.3 配置加载方式

```python
# 方式一：直接在代码中 update（简单场景）
app.conf.update(
    task_serializer='json',
    timezone='Asia/Shanghai',
)

# 方式二：从配置对象加载（推荐）
app.config_from_object('celery_config')

# 方式三：从 Python 模块加载
from celery.config import Config
app.config_from_object(Config)

# 方式四：从环境变量加载（容器化部署推荐）
broker_url = os.getenv('CELERY_BROKER_URL')
result_backend = os.getenv('CELERY_RESULT_BACKEND')

# 方式五：从 Django settings 加载（Django 项目）
# app.config_from_object('django.conf:settings', namespace='CELERY')
```

> ❌ **常见坑点**：`timezone` 配置不一致导致定时任务在错误时间执行。如果 Broker 是 UTC 时间，而你设置了 `timezone='Asia/Shanghai'`，但没有设置 `enable_utc=True`，crontab 会按本地时间解释，可能导致时差问题。**正确做法**：始终设置 `enable_utc=True`，然后通过 `timezone` 指定业务时区。

> 💡 **深度讲解**：Celery 应用实例是整个系统的核心枢纽。它不仅是一个配置容器，还管理任务注册、连接池、事件系统等。生产环境推荐使用工厂模式创建应用，便于测试时创建不同配置的实例。配置管理推荐使用环境变量（12-Factor App），这样同一份代码可以在不同环境（dev/staging/prod）下运行，只需改变环境变量。

> 📝 **本章精简总结**：
> - 核心概念：Celery 应用实例、配置体系
> - 关键原理：工厂模式创建应用、环境变量配置
> - 常用操作：安装依赖、创建 app、加载配置
> - 最佳实践：用环境变量管理配置、避免 pickle 序列化
> - 常见坑点：时区配置不一致、忘记安装 Broker 额外依赖

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：为什么推荐使用 JSON 而不是 pickle 作为序列化格式？
>   - 答案：pickle 有安全风险（可执行任意代码）、不跨语言、调试困难
> - **进阶题（⭐⭐）**：`worker_max_tasks_per_child` 和 `worker_max_memory_per_child` 的作用是什么？为什么需要它们？
>   - 思考方向：从内存泄漏、第三方库资源释放角度分析

---

## 四、任务定义与调用

### 4.1 @app.task 装饰器详解

**概念解释**：`@app.task` 装饰器将普通 Python 函数包装为 Celery 任务，使其可以异步执行。装饰器接受多个参数控制任务行为。

```python
# tasks/email.py —— 完整的任务定义示例
from celery_app import app
from celery.exceptions import SoftTimeLimitExceeded
import logging

logger = logging.getLogger(__name__)


@app.task(
    # ===== 基本属性 =====
    name='email.send_welcome',      # 显式任务名（推荐，避免模块路径变化）
    bind=True,                       # 绑定 self（任务实例），可访问 self.retry 等

    # ===== 重试配置 =====
    max_retries=3,                   # 最大重试次数
    default_retry_delay=60,          # 默认重试延迟（秒）
    autoretry_for=(ConnectionError, TimeoutError),  # 自动重试的异常类型
    retry_backoff=True,              # 指数退避
    retry_backoff_max=600,           # 最大退避时间（秒）
    retry_jitter=True,               # 随机抖动，防止惊群效应

    # ===== 超时配置 =====
    time_limit=30,                   # 硬超时（秒）：到时间直接杀死进程
    soft_time_limit=20,              # 软超时（秒）：抛出 SoftTimeLimitExceeded

    # ===== 速率限制 =====
    rate_limit='100/m',              # 每分钟最多执行 100 次

    # ===== 结果配置 =====
    ignore_result=False,             # 是否忽略结果（不需要结果时设 True 节省空间）

    # ===== 队列配置 =====
    queue='email',                   # 指定默认队列
)
def send_welcome_email(self, user_id: int, email: str, username: str):
    """
    发送欢迎邮件任务

    bind=True 时第一个参数是 self（Task 实例）
    self.request 包含请求信息：id, retries, args, kwargs 等
    """
    logger.info(f"发送欢迎邮件: user_id={user_id}, email={email}")

    try:
        # 模拟邮件发送逻辑
        result = email_service.send(
            to=email,
            subject=f"欢迎 {username}！",
            template="welcome.html",
            context={"username": username, "user_id": user_id}
        )
        logger.info(f"邮件发送成功: {result.message_id}")
        return {
            "status": "success",
            "message_id": result.message_id,
            "user_id": user_id,
        }

    except SoftTimeLimitExceeded:
        logger.error(f"邮件发送超时: user_id={user_id}")
        raise  # 软超时不重试，标记为失败

    except (ConnectionError, TimeoutError) as exc:
        # 手动重试（autoretry_for 已配置，但这里展示手动用法）
        logger.warning(
            f"邮件发送失败(第{self.request.retries}次): {exc}"
        )
        raise self.retry(exc=exc, countdown=30 * (self.request.retries + 1))

    except Exception as exc:
        logger.error(f"邮件发送异常: {exc}", exc_info=True)
        raise
```

```python
# 任务自调用模式（递归任务）
@app.task(bind=True, max_reties=5)
def process_batch(self, batch_id: int, offset: int = 0, batch_size: int = 1000):
    """
    分批处理数据：每次处理一批，然后自调用处理下一批
    适用于大数据量处理，避免单次任务超时
    """
    items = fetch_batch(batch_id, offset, batch_size)

    if not items:
        # 所有批次处理完毕
        logger.info(f"批次 {batch_id} 全部处理完成")
        return {"batch_id": batch_id, "total_processed": offset}

    for item in items:
        process_item(item)

    logger.info(f"批次 {batch_id} 已处理 {offset + len(items)} 条")

    # 自调用：处理下一批
    raise self.retry(
        kwargs={"batch_id": batch_id, "offset": offset + batch_size},
        countdown=10,  # 10秒后处理下一批
    )
```

### 4.2 任务调用方式

**概念解释**：Celery 提供多种方式调用任务，从简单的 `delay()` 到支持高级参数的 `apply_async()`。

```python
# 方式一：delay() —— 最简单的调用方式
# 适用于不需要高级参数的场景
send_welcome_email.delay(user_id=1, email="user@example.com", username="张三")

# 等价于：
send_welcome_email.apply_async(
    kwargs={"user_id": 1, "email": "user@example.com", "username": "张三"}
)
```

```python
# 方式二：apply_async() —— 完整控制调用参数
result = send_welcome_email.apply_async(
    # 位置参数
    args=[1, "user@example.com", "张三"],

    # 关键字参数（优先使用）
    kwargs={"user_id": 1, "email": "user@example.com", "username": "张三"},

    # ===== 调度控制 =====
    countdown=60,           # 60 秒后执行（延迟任务）
    # eta=datetime(2026, 9, 10, 12, 0, 0),  # 指定时间执行（UTC）

    # ===== 路由控制 =====
    queue='email',           # 指定队列
    exchange='default',      # 指定交换机
    routing_key='email.high', # 路由键
    priority=9,              # 优先级（0-9，9最高）

    # ===== 结果控制 =====
    soft_time_limit=15,      # 覆盖默认软超时
    time_limit=30,           # 覆盖默认硬超时
    serializer='json',       # 覆盖序列化格式

    # ===== 其他 =====
    expiration=600,          # 任务10分钟内未被消费则丢弃
    retry=True,              # Broker 重连时重试发布
)

print(f"任务ID: {result.id}")
# 预期输出：任务ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

```python
# 方式三：delay() 的语法糖变体
# .s() 创建签名（Signature），用于任务编排
from celery import chain

# 创建任务签名
welcome_sig = send_welcome_email.s(user_id=1, email="user@example.com")

# 签名也可以直接调用
result = welcome_sig.delay()

# 部分参数签名（.s() 不传参数，等待链式传递）
process_sig = process_data.s()  # 等待前一个任务的结果传入
```

```python
# 方式四：同步执行（调试用）
# task_always_eager = True 时，任务同步执行，不经过 Broker
# 适用于单元测试和调试
result = send_welcome_email.apply(args=[1, "user@example.com", "张三"])
print(result.get())
# 预期输出：{'status': 'success', 'message_id': 'xxx', 'user_id': 1}
```

```python
# 自定义任务基类：统一错误处理和日志
from celery import Task
import logging
import traceback

logger = logging.getLogger(__name__)

class BaseTask(Task):
    """所有任务的基类：统一错误处理、日志、告警"""

    # 通用默认配置
    autoretry_for = (ConnectionError, TimeoutError)
    max_retries = 3
    default_retry_delay = 60
    retry_backoff = True
    retry_jitter = True

    def __call__(self, *args, **kwargs):
        """任务执行入口：添加前后日志"""
        logger.info(f"任务开始: {self.name}[{self.request.id}]")
        try:
            result = self.run(*args, **kwargs)
            logger.info(f"任务成功: {self.name}[{self.request.id}]")
            return result
        except Exception as exc:
            logger.error(
                f"任务失败: {self.name}[{self.request.id}] "
                f"重试次数={self.request.retries} 错误={exc}",
                exc_info=True
            )
            # 失败告警
            if self.request.retries >= self.max_retries:
                self.send_alert(exc)
            raise

    def send_alert(self, exception):
        """发送失败告警到钉钉/飞书"""
        alert_msg = (
            f"🚨 Celery 任务最终失败\n"
            f"任务: {self.name}\n"
            f"任务ID: {self.request.id}\n"
            f"错误: {exception}\n"
            f"堆栈: {traceback.format_exc()}"
        )
        try:
            webhook.send(alert_msg)
        except Exception:
            logger.error("发送告警失败", exc_info=True)


# 使用自定义基类
@app.task(base=BaseTask, bind=True)
def my_custom_task(self, data):
    """使用自定义基类的任务"""
    return process_data(data)
```

```python
# 任务速率限制（rate_limit）详解
# rate_limit 控制单位时间内任务的最大执行次数
# 格式：'N/s'（每秒）、'N/m'（每分钟）、'N/h'（每小时）

@app.task(rate_limit='100/m')  # 每分钟最多执行100次
def call_third_party_api(user_id):
    """调用有速率限制的第三方API"""
    return api_client.fetch(user_id)

# 动态调整速率限制（运行时）
from celery.app.control import Control
def set_rate_limit(task_name: str, rate_limit: str, worker=None):
    """动态调整任务速率限制"""
    app.control.rate_limit(
        task_name,
        rate_limit,
        destination=[worker] if worker else None,
    )
# 使用：set_rate_limit('tasks.call_api', '50/m')
```

```python
# 任务结果压缩（大结果优化）
app.conf.result_compression = 'gzip'  # 大结果自动 gzip 压缩
app.conf.result_compression = 'bzip2'  # 更高压缩率但更慢

# 结果序列化压缩示例
# 当结果大于 100KB 时自动压缩，节省 Backend 存储空间
@app.task
def generate_large_dataset(query: dict) -> list:
    """生成大数据集：自动压缩存储"""
    data = db.query_complex(query)
    # 结果可能很大（几MB），开启压缩后实际存储体积减少 80%+
    return data
```

> ❌ **常见坑点**：`delay()` 和 `apply_async()` 不能混用位置参数和关键字参数。`delay(x, y)` 传位置参数，`apply_async(args=[x, y])` 也是位置参数；但 `delay(x=1, y=2)` 传关键字参数，`apply_async(kwargs={x:1, y:2})` 也是关键字参数。混用会导致参数错误。**正确做法**：统一使用关键字参数，提高代码可读性。

### 4.3 任务参数序列化

**概念解释**：Celery 任务参数需要从 Producer 序列化传输到 Broker，再从 Broker 反序列化到 Worker。这意味着参数必须是可序列化的。

```python
# ✅ 正确：使用可序列化的基本类型
@app.task
def create_order(order_data: dict):
    """参数使用 dict/list/str/int/float/bool/None"""
    order = Order(**order_data)
    db.session.add(order)
    db.session.commit()
    return order.id

# 调用
create_order.delay({
    "user_id": 123,
    "items": [{"sku": "A001", "qty": 2}],
    "total": 99.9,
})
```

```python
# ❌ 错误：传递不可序列化对象
class OrderService:
    def process(self, order):
        # 错误：把数据库 session 或模型实例传给任务
        # create_order_task.delay(db_session, order)
        # TypeError: Object of type Session is not JSON serializable
        pass

# ✅ 正确：传递 ID，任务内重新查询
@app.task
def process_order(order_id: int):
    """传递 ID，任务内从数据库重新加载"""
    order = Order.query.get(order_id)
    # 处理订单...
    return order.status
```

> ✅ **最佳实践**：任务参数只使用 JSON 可序列化的基本类型（str/int/float/bool/None/list/dict）。复杂对象（ORM 实例、数据库连接、文件句柄）传 ID，在任务内部重新获取。这样不仅解决序列化问题，还保证了任务的独立性和可重试性。

> 💡 **深度讲解**：任务定义是 Celery 使用中最核心的部分。`@app.task` 装饰器的参数几乎覆盖了任务的所有行为控制：重试策略、超时限制、速率限制、队列路由、结果存储。理解这些参数的含义和默认值，能够在不修改任务代码的情况下调整任务行为。任务调用的 `delay()` vs `apply_async()` 选择原则很简单——不需要高级参数就用 `delay()`，需要 countdown/eta/priority/queue 等参数就用 `apply_async()`。

> 📝 **本章精简总结**：
> - 核心概念：@app.task 装饰器、任务签名、参数序列化
> - 关键原理：bind=True 绑定 self、任务参数必须可 JSON 序列化
> - 常用操作：delay() 简单调用、apply_async() 高级调用
> - 最佳实践：显式指定任务名、参数只用基本类型、传 ID 不传对象
> - 常见坑点：delay/apply_async 参数混用、传递不可序列化对象
> - 面试高频：bind=True 的作用、autoretry_for 和 retry_backoff

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：`@app.task(bind=True)` 中 bind=True 的作用是什么？
>   - 答案：将任务实例作为第一个参数 self 传入，可访问 self.retry、self.request 等
> - **进阶题（⭐⭐）**：为什么任务参数不应该传递 ORM 模型实例？
>   - 思考方向：序列化问题、跨进程状态不一致、连接池问题
> - **实战题（⭐⭐⭐）**：编写一个图片处理任务：下载图片→添加水印→压缩→上传到 OSS。要求：单步失败可重试、整体超时5分钟、支持优先级。
>   - 提示：拆分 4 个子任务用 chain 编排，每个子任务配置 autoretry_for

---

## 五、任务状态与结果管理

### 5.1 Result Backend 选择

**概念解释**：Result Backend 负责存储任务执行结果和状态。Worker 执行完任务后将返回值序列化存入 Backend，Producer 通过 task_id 查询结果。

```python
# Redis Backend 配置
app.conf.result_backend = 'redis://localhost:6379/1'

# 数据库 Backend（适合需要持久化结果的场景）
# pip install sqlalchemy
app.conf.result_backend = 'db+postgresql://user:pass@localhost/celery_results'

# MongoDB Backend
# pip install pymongo
app.conf.result_backend = 'mongodb://localhost:27017/celery_results'

# RPC Backend（不存储，通过消息队列返回结果——不推荐用于跨进程查询）
app.conf.result_backend = 'rpc://'

# 不使用 Backend（不需要查询结果时）
app.conf.result_backend = None
# 同时在任务上设置 ignore_result=True
```

| Backend | 优点 | 缺点 | 适用场景 |
|---------|------|------|---------|
| **Redis** | 快、支持过期、已有 Redis 可复用 | 数据量大时内存压力大 | 中小规模、结果短期查询 |
| **Database** | 持久化、可 SQL 查询 | 性能较低、需要建表 | 需要长期保存结果 |
| **MongoDB** | 灵活、适合大文档 | 额外维护一个数据库 | 半结构化结果存储 |
| **RPC** | 无存储开销 | 仅同进程可用 | 不推荐生产使用 |

### 5.2 结果查询模式

```python
# tasks/order.py
from celery import Celery
from celery.result import AsyncResult, GroupResult
import time

app = Celery('order', broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/1')

@app.task
def process_order(order_id: int) -> dict:
    """处理订单任务"""
    time.sleep(2)  # 模拟耗时操作
    return {"order_id": order_id, "status": "processed", "amount": 99.9}
```

```python
# 查询模式一：非阻塞查询（推荐）
# 立即返回任务 ID，前端轮询状态
def submit_order(order_id: int) -> str:
    """提交订单处理任务，返回 task_id"""
    result = process_order.delay(order_id)
    return result.id  # 立即返回，不等待


def query_order_status(task_id: str) -> dict:
    """查询订单处理状态（前端轮询调用）"""
    result = AsyncResult(task_id, app=app)

    if result.ready():
        if result.successful():
            return {"status": "completed", "data": result.result}
        else:
            return {"status": "failed", "error": str(result.result)}
    else:
        return {"status": "processing"}

# 预期使用：
# task_id = submit_order(123)
# # 前端轮询 /api/order/status?task_id=xxx
```

```python
# 查询模式二：阻塞等待（慎用）
# 适合脚本/测试场景，Web 环境不要用
result = process_order.delay(123)

try:
    # 阻塞等待结果，超时10秒
    data = result.get(timeout=10, propagate=True)
    print(f"结果: {data}")
    # 预期输出：结果: {'order_id': 123, 'status': 'processed', 'amount': 99.9}
except TimeoutError:
    print("任务超时未完成")
    result.forget()  # 清除结果
except Exception as e:
    print(f"任务失败: {e}")
```

```python
# 查询模式三：批量查询任务组
from celery import group

# 并行处理多个订单
tasks = group(process_order.s(oid) for oid in [101, 102, 103, 104])
group_result = tasks.apply_async()

# 等待全部完成（阻塞）
results = group_result.get(timeout=30)
print(results)
# 预期输出：
# [
#     {'order_id': 101, 'status': 'processed', 'amount': 99.9},
#     {'order_id': 102, 'status': 'processed', 'amount': 50.0},
#     {'order_id': 103, 'status': 'processed', 'amount': 200.0},
#     {'order_id': 104, 'status': 'processed', 'amount': 150.0},
# ]

# 恢复 GroupResult（如果只有 group_id）
# restored = GroupResult.restore(group_id, app=app)
```

### 5.3 任务撤销与清理

```python
# 撤销任务
result = process_order.delay(123)

# 方式一：只撤销未开始的任务
result.revoke()
# 如果任务正在执行，不会被终止

# 方式二：强制终止正在执行的任务
result.revoke(terminate=True)
# ⚠️ terminate=True 会直接 kill Worker 子进程
# 可能导致资源泄漏（数据库连接未释放等）
# 建议谨慎使用

# 方式三：终止并删除结果
result.revoke(terminate=True, signal='SIGKILL')
# 使用不同信号终止：SIGTERM（优雅）、SIGKILL（强制）
```

```python
# 清除已完成任务的结果
result.forget()  # 从 Backend 删除结果

# 批量清理 Backend 中的过期结果
# result_expires 配置自动过期
app.conf.result_expires = 3600  # 1小时后自动删除

# 手动清理 Redis Backend
import redis
r = redis.Redis(host='localhost', port=6379, db=1)
# 清理所有 celery 结果 key
r.delete(*r.keys('celery-task-meta-*'))
```

> ❌ **常见坑点**：`result.get()` 在 Web 环境中是反模式。它会阻塞 Web 服务器的工作线程等待任务完成，高并发时耗尽连接池。**正确做法**：Web 接口立即返回 task_id，前端通过轮询或 WebSocket 推送获取结果。只有在脚本、测试等非 Web 场景才使用 `get()`。

### 5.4 任务结果存储最佳实践

```python
# 不需要结果的任务：设置 ignore_result=True
@app.task(ignore_result=True)
def send_notification(user_id: int, message: str):
    """发送通知：不需要查询结果，节省 Backend 空间"""
    notification_service.send(user_id, message)

# 大结果不要存 Backend：存数据库，返回 ID
@app.task
def generate_large_report(user_id: int, date_range: str) -> str:
    """生成大报表：结果存数据库，只返回文件路径"""
    report_data = build_report(user_id, date_range)

    # 存到文件系统/对象存储
    report_path = save_to_storage(report_data, f"report_{user_id}.pdf")

    # 只返回路径，不返回全部数据
    return report_path
```

> 💡 **深度讲解**：结果管理是 Celery 中容易被忽视但非常重要的环节。很多团队的 Redis 内存爆满就是因为任务结果没有正确过期和清理。核心原则是：不需要结果的任务设置 `ignore_result=True`；大结果存外部存储只返回引用；设置合理的 `result_expires` 自动清理。`result.get()` 阻塞调用在 Web 环境中是反模式，应该改为异步轮询模式。

> 📝 **本章精简总结**：
> - 核心概念：Result Backend、AsyncResult、GroupResult
> - 关键原理：任务结果序列化存储、非阻塞查询模式
> - 常用操作：delay() 后存 task_id、AsyncResult 查询状态、revoke 撤销
> - 最佳实践：Web 环境不用 get()、ignore_result 节省空间、大结果存外部
> - 常见坑点：result.get() 阻塞 Web 线程、PENDING 状态歧义
> - 面试高频：Result Backend 选型、revoke terminate 的副作用

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：`result.ready()`、`result.successful()`、`result.failed()` 有什么区别？
>   - 答案：ready 表示是否结束（含失败）；successful 表示是否成功；failed 表示是否失败
> - **进阶题（⭐⭐）**：为什么不推荐在 Web 请求中使用 `result.get()`？
>   - 思考方向：线程阻塞、连接池耗尽、超时风险
> - **实战题（⭐⭐⭐）**：设计一个异步报表系统：提交报表任务→返回 task_id→前端轮询进度→完成后通知下载。需要支持进度查询。
>   - 提示：任务内用 Backend 更新进度（update_state），前端查询进度百分比

---

## 六、任务路由与队列管理

### 6.1 为什么需要多队列

**概念解释**：默认所有任务都进入同一个 default 队列。当存在快慢不同、优先级不同的任务时，慢任务会阻塞快任务。通过多队列路由，不同类型的任务进入不同队列，由独立的 Worker 消费。

**生活化比喻**：就像银行柜台——普通业务和VIP业务分开窗口办理，VIP不用排队等普通人办完。如果只有一个窗口，办复杂业务的人会堵住后面所有人。

```mermaid
flowchart TD
    subgraph 生产者
        P1[Web应用]
    end

    subgraph 队列层
        Q1[default队列<br/>快任务]
        Q2[email队列<br/>邮件发送]
        Q3[report队列<br/>报表生成<br/>慢任务]
        Q4[priority队列<br/>高优先级]
    end

    subgraph Worker集群
        W1[Worker-1<br/>-Q default -c 8]
        W2[Worker-2<br/>-Q email -c 4]
        W3[Worker-3<br/>-Q report -c 2]
        W4[Worker-4<br/>-Q priority -c 4]
    end

    P1 -->|普通任务| Q1
    P1 -->|邮件任务| Q2
    P1 -->|报表任务| Q3
    P1 -->|紧急任务| Q4

    Q1 --> W1
    Q2 --> W2
    Q3 --> W3
    Q4 --> W4

    style Q1 fill:#43e97b,color:#333
    style Q2 fill:#4facfe,color:#fff
    style Q3 fill:#fa709a,color:#fff
    style Q4 fill:#fee140,color:#333
```

### 6.2 配置任务路由

```python
# celery_app.py —— 路由配置
app.conf.update(
    # 默认队列
    task_default_queue = 'default',
    task_default_exchange = 'default',
    task_default_routing_key = 'default',

    # 路由规则：按任务名模式匹配
    task_routes = {
        # 邮件相关任务 → email 队列
        'tasks.email.*': {
            'queue': 'email',
            'routing_key': 'email.send',
        },

        # 报表相关任务 → report 队列（慢任务独立队列）
        'tasks.report.*': {
            'queue': 'report',
            'routing_key': 'report.generate',
        },

        # 高优先级任务 → priority 队列
        'tasks.priority.*': {
            'queue': 'priority',
            'routing_key': 'priority.high',
        },

        # 数据处理任务 → data 队列
        'tasks.data.*': {'queue': 'data'},

        # 精确匹配优先于模式匹配
        'tasks.email.send_urgent': {'queue': 'priority'},
    },
)
```

```python
# 也可以在任务定义时直接指定队列
@app.task(queue='email', routing_key='email.send')
def send_email(to, subject, body):
    """显式指定队列，优先于 task_routes 配置"""
    pass

@app.task(queue='report')
def generate_daily_report():
    pass
```

```python
# 调用时动态指定队列
def handle_email_send(email: str, urgent: bool = False):
    if urgent:
        # 紧急邮件走 priority 队列
        send_email.apply_async(
            args=[email, "紧急通知", "内容"],
            queue='priority',
            priority=9,
        )
    else:
        # 普通邮件走 email 队列
        send_email.delay(email, "通知", "内容")
```

### 6.3 启动不同队列的 Worker

```bash
# 启动 default 队列的 Worker（8个进程）
celery -A celery_app worker -Q default -c 8 --loglevel=info

# 启动 email 队列的 Worker（4个进程）
celery -A celery_app worker -Q email -c 4 --loglevel=info

# 启动 report 队列的 Worker（2个进程，慢任务不需要太多并发）
celery -A celery_app worker -Q report -c 2 --loglevel=info

# 一个 Worker 消费多个队列
celery -A celery_app worker -Q default,email -c 6 --loglevel=info

# 查看所有队列和任务
celery -A celery_app inspect active_queues
# 预期输出：显示各 Worker 当前消费的队列
```

```bash
# Docker Compose 多 Worker 配置示例
# docker-compose.yml
# version: '3.8'
# services:
#   worker-default:
#     build: .
#     command: celery -A celery_app worker -Q default -c 4
#     depends_on: [redis]
#
#   worker-email:
#     build: .
#     command: celery -A celery_app worker -Q email -c 2
#     depends_on: [redis]
#
#   worker-report:
#     build: .
#     command: celery -A celery_app worker -Q report -c 1
#     depends_on: [redis]
```

### 6.4 任务优先级

```python
# Redis Broker 优先级配置
# Redis 使用 List 的 LPUSH/BRPOP 实现简单优先级
# priority 0-9，9 最高

app.conf.update(
    # Redis 优先级队列数量
    broker_transport_options={
        'priority_steps': [0, 3, 6, 9],  # 使用 4 个优先级级别
    },
)

# 发送高优先级任务
send_email.apply_async(
    args=[...],
    queue='email',
    priority=9,  # 最高优先级，Worker 优先消费
)

# 发送低优先级任务
send_daily_digest.apply_async(
    args=[...],
    queue='email',
    priority=0,  # 最低优先级，排队等待
)
```

```python
# RabbitMQ 优先级队列（更完善）
# 需要在队列声明时设置 x-max-priority
app.conf.update(
    task_queue_max_priority=10,  # 0-9 共10个优先级
)

# RabbitMQ 的优先级实现更完善，支持严格的优先级排序
# Redis 的优先级是基于多个 List 实现的，粒度较粗
```

> ❌ **常见坑点**：Redis Broker 的优先级不是严格优先级。Redis 使用多个 List（按优先级分级），Worker 从高优先级 List 开始消费。如果高优先级任务持续不断，低优先级任务可能永远得不到执行（饥饿）。**正确做法**：设置合理的优先级级别，避免低优先级任务堆积；监控队列长度，防止饥饿。

> 💡 **深度讲解**：多队列路由是 Celery 生产环境最常用的架构优化手段。核心原则是"快慢分离"——将执行时间差异大的任务放到不同队列，用不同的 Worker 池处理。这样慢任务（报表生成）不会阻塞快任务（发邮件）。队列划分通常按任务类型、优先级、资源需求三个维度。Worker 数量根据任务的 IO/CPU 特性调整：IO 密集型用协程+高并发，CPU 密集型用多进程+核心数并发。

> 📝 **本章精简总结**：
> - 核心概念：多队列路由、task_routes、-Q 参数、优先级
> - 关键原理：快慢分离、独立 Worker 池、按队列隔离
> - 常用操作：配置 task_routes、启动 -Q 指定队列、apply_async 指定 queue
> - 最佳实践：按任务类型分队列、慢任务独立低并发 Worker
> - 常见坑点：Redis 优先级饥饿、Worker 队列名不匹配
> - 面试高频：为什么需要多队列？如何设计队列划分策略？

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：`celery -A app worker -Q default,email` 是什么意思？
>   - 答案：这个 Worker 同时消费 default 和 email 两个队列
> - **进阶题（⭐⭐）**：如何设计一个混合了 CPU 密集和 IO 密集任务的 Celery 系统？
>   - 思考方向：拆分队列+拆分 Worker，CPU 任务用 prefork，IO 任务用 gevent
> - **实战题（⭐⭐⭐）**：一个电商系统有以下任务：下单（快）、发邮件（中）、生成报表（慢）、推荐计算（CPU密集）。设计队列和 Worker 方案。
>   - 提示：4个队列×4种 Worker 配置，按任务特性分配并发模型

---

## 七、定时任务与 Celery Beat

### 7.1 Celery Beat 基础

**概念解释**：Celery Beat 是 Celery 的定时任务调度器，它按照配置的时间表定时将任务发布到 Broker。它替代了传统的 crontab，提供了更好的可管理性和监控能力。

**原理说明**：Beat 是一个独立的进程，它读取配置的调度表（beat_schedule），在每个调度时间点到来时，调用 `task.apply_async()` 将任务发布到 Broker。Beat 不执行任务，只负责"定时发布"——真正的执行由 Worker 完成。

```python
# celery_app.py —— Beat 定时任务配置
from celery.schedules import crontab, schedule
from datetime import timedelta

app.conf.beat_schedule = {
    # ===== 方式一：固定间隔（秒）=====
    'health-check': {
        'task': 'tasks.system.health_check',
        'schedule': 300,  # 每 300 秒（5分钟）执行一次
        'args': (),       # 传递给任务的参数
    },

    # ===== 方式二：crontab 表达式 =====
    'daily-report': {
        'task': 'tasks.report.generate_daily',
        'schedule': crontab(
            minute=0,           # 第0分钟
            hour=8,             # 第8小时
            day_of_week='mon-fri',  # 周一到周五
            # day_of_month='1-7',  # 每月1-7号
            # month_of_year='1,4,7,10',  # 季度
        ),
        'args': ('yesterday',),
    },

    # ===== 方式三：timedelta =====
    'cleanup-cache': {
        'task': 'tasks.cache.cleanup_expired',
        'schedule': timedelta(hours=1),  # 每1小时
    },

    # ===== 方式四：带参数的定时任务 =====
    'hourly-data-sync': {
        'task': 'tasks.sync.sync_from_external_api',
        'schedule': crontab(minute=0),  # 每小时整点
        'kwargs': {'source': 'crm', 'batch_size': 500},  # 关键字参数
        'options': {
            'queue': 'data_sync',  # 路由到指定队列
            'expires': 3600,       # 1小时内未执行则丢弃
        },
    },
}
```

```bash
# 启动 Beat（必须单独启动一个进程）
celery -A celery_app beat --loglevel=info

# Beat + Worker 一起启动（开发环境用，生产不推荐）
celery -A celery_app worker --beat --loglevel=info

# 指定调度文件（持久化调度状态）
celery -A celery_app beat --schedule=/var/run/celery/celerybeat-schedule
```

### 7.2 crontab 表达式详解

```python
from celery.schedules import crontab

# crontab 参数说明
# crontab(minute, hour, day_of_month, month_of_year, day_of_month, day_of_week)

# 每天早上8点
crontab(hour=8, minute=0)

# 每周一早上9点
crontab(hour=9, minute=0, day_of_week=1)  # 0=周日, 1=周一, ..., 6=周六

# 每月1号凌晨0点
crontab(day_of_month=1, hour=0, minute=0)

# 每15分钟
crontab(minute='*/15')  # 0,15,30,45 分

# 工作日的每小时整点
crontab(minute=0, hour='9-18', day_of_week='mon-fri')

# 复杂表达式
crontab(minute='0,30', hour='6-22')  # 每天6:00-22:30，每半小时
crontab(minute='*/10', day_of_week='sat,sun')  # 周末每10分钟
```

| 表达式 | 含义 | 示例 |
|--------|------|------|
| `*` | 每单位 | `minute='*'` = 每分钟 |
| `*/N` | 每N单位 | `hour='*/2'` = 每2小时 |
| `A,B,C` | 指定值 | `hour='1,6,12'` = 1/6/12点 |
| `A-B` | 范围 | `hour='9-18'` = 9到18点 |
| `A-B/N` | 范围间隔 | `minute='0-30/5'` = 0-30分内每5分钟 |
| `mon-fri` | 星期名 | `day_of_week='mon-fri'` = 工作日 |

### 7.3 数据库存储定时任务（django-celery-beat）

**概念解释**：默认的 Beat 定时任务配置在代码中，修改需要重启 Beat。`django-celery-beat` 提供数据库存储定时任务的能力，可以通过 Admin 界面动态增删改查定时任务。

```python
# Django 项目集成 django-celery-beat
# 安装：pip install django-celery-beat

# settings.py
INSTALLED_APPS = [
    # ...
    'django_celery_beat',
]

# 运行迁移
# python manage.py migrate

# 使用 DatabaseScheduler
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
```

```python
# 通过代码动态创建定时任务
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

# 创建 crontab 计划
schedule, created = CrontabSchedule.objects.get_or_create(
    minute=0, hour=8,
    day_of_week='mon-fri',
    timezone='Asia/Shanghai',
)

# 创建定时任务
PeriodicTask.objects.get_or_create(
    name='工作日日报',
    defaults={
        'crontab': schedule,
        'task': 'tasks.report.generate_daily',
        'args': json.dumps(['yesterday']),
        'enabled': True,
    }
)
```

> ❌ **常见坑点**：Beat 启动多个实例会导致定时任务重复执行。Beat 是单例调度器——如果启动了多个 Beat 进程，每个进程都会独立发布任务，导致同一任务被执行多次。**正确做法**：生产环境只运行一个 Beat 实例，通过 Systemd/Docker 确保单实例。需要高可用时使用 `django-celery-beat` 的数据库锁机制。

### 7.4 延迟任务（countdown / ETA）

```python
# 延迟任务：订单超时自动取消
from datetime import datetime, timedelta

@app.task
def cancel_order_if_unpaid(order_id: int):
    """检查订单是否已支付，未支付则取消"""
    order = Order.query.get(order_id)
    if order.status == 'pending':
        order.status = 'cancelled'
        db.session.commit()
        send_notification.delay(order.user_id, "订单已超时取消")
        logger.info(f"订单 {order_id} 超时取消")


def create_order(user_id: int, items: list):
    """创建订单后，设置30分钟后自动取消"""
    order = Order(user_id=user_id, items=items, status='pending')
    db.session.add(order)
    db.session.commit()

    # 方式一：countdown（相对延迟，30分钟后执行）
    cancel_order_if_unpaid.apply_async(
        args=[order.id],
        countdown=1800,  # 1800秒 = 30分钟
    )

    # 方式二：eta（绝对时间，到指定时间执行）
    # eta_time = datetime.utcnow() + timedelta(minutes=30)
    # cancel_order_if_unpaid.apply_async(
    #     args=[order.id],
    #     eta=eta_time,
    # )

    return order.id
```

```python
# 延迟任务的取消：用户提前支付后取消自动取消任务
def pay_order(order_id: int):
    """用户支付订单后，撤销超时取消任务"""
    order = Order.query.get(order_id)
    order.status = 'paid'
    db.session.commit()

    # 查找之前注册的取消任务
    # 需要在创建订单时保存 task_id
    task_id = get_cancel_task_id(order_id)
    if task_id:
        AsyncResult(task_id).revoke()
        clear_cancel_task_id(order_id)
```

> ❌ **常见坑点**：Redis Broker 实现延迟任务（ETA）使用 ZSet，当大量延迟任务同时到期时（如整点），会出现"惊群效应"——瞬间大量任务同时被取出执行，Worker 瞬间过载。**正确做法**：使用 `retry_jitter=True` 给重试加随机抖动；对延迟任务的到期时间加随机偏移（如 30分钟±60秒）。

> 💡 **深度讲解**：Celery Beat 是替代 crontab 的现代方案。它的核心优势是：任务定义和调度统一在代码中、可以通过 Flower 监控、失败任务可以在 Worker 端重试。但 Beat 也有局限——它只负责"定时发布"，不保证任务一定执行（Worker 可能宕机）；多实例会导致重复执行。对于需要严格高可用的定时任务场景，推荐使用 `django-celery-beat` + 数据库锁，或考虑使用专业调度系统如 Airflow。

> 📝 **本章精简总结**：
> - 核心概念：Celery Beat、crontab、countdown/eta、延迟任务
> - 关键原理：Beat 只负责定时发布、Worker 负责执行、单实例部署
> - 常用操作：beat_schedule 配置、crontab 表达式、countdown 延迟
> - 最佳实践：Beat 单实例、django-celery-beat 动态管理
> - 常见坑点：多 Beat 重复执行、延迟任务惊群效应
> - 面试高频：Beat 原理、crontab 表达式、countdown vs eta

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：countdown 和 eta 有什么区别？
>   - 答案：countdown 是相对延迟（N秒后），eta 是绝对时间点（到某个时刻）
> - **进阶题（⭐⭐）**：为什么 Beat 只能启动一个实例？多实例会怎样？
>   - 思考方向：Beat 独立读取配置并发布任务，无分布式锁
> - **实战题（⭐⭐⭐）**：设计一个订阅到期提醒系统：用户订阅30天到期，到期前7天、3天、1天分别发送提醒。要求可取消。
>   - 提示：创建订阅时注册3个延迟任务，记录 task_id；取消订阅时 revoke 对应任务

---

## 八、任务编排：Chain/Group/Chord

### 8.1 Chain（任务链）

**概念解释**：Chain 将多个任务按顺序串联执行，前一个任务的返回值自动作为下一个任务的输入。适合有明确依赖关系的流水线场景。

```python
# tasks/pipeline.py
from celery import chain
from celery_app import app

@app.task
def fetch_user_data(user_id: int) -> dict:
    """第一步：获取用户数据"""
    user = User.query.get(user_id)
    return {"id": user.id, "name": user.name, "email": user.email}

@app.task
def process_user_data(user_data: dict) -> dict:
    """第二步：处理用户数据（接收上一步的结果）"""
    user_data["name_upper"] = user_data["name"].upper()
    user_data["email_domain"] = user_data["email"].split("@")[1]
    return user_data

@app.task
def save_to_database(processed_data: dict) -> int:
    """第三步：保存处理后的数据"""
    record = ProcessedRecord(**processed_data)
    db.session.add(record)
    db.session.commit()
    return record.id
```

```python
# 使用 Chain 编排：fetch → process → save
def process_user_pipeline(user_id: int):
    """
    链式执行：
    fetch_user_data(user_id) → process_user_data(result) → save_to_database(result)
    """
    workflow = chain(
        fetch_user_data.s(user_id),      # .s() 创建任务签名，传入参数
        process_user_data.s(),            # .s() 不传参数，自动接收上一步结果
        save_to_database.s(),             # 同上
    )

    result = workflow()
    return result.id  # 返回最终任务的 ID

# 预期行为：三个任务顺序执行，前一个的返回值自动传入下一个
# 步骤1返回 dict → 步骤2接收 dict → 步骤2返回 dict → 步骤3接收 dict
```

```python
# 带额外参数的 Chain
@app.task
def enrich_user_data(user_data: dict, extra_info: str) -> dict:
    """需要额外参数的步骤"""
    user_data["extra"] = extra_info
    return user_data

def pipeline_with_extra(user_id: int, extra: str):
    workflow = chain(
        fetch_user_data.s(user_id),
        enrich_user_data.s(extra),  # 额外参数 + 自动接收上一步结果
    )
    return workflow()
```

### 8.2 Group（任务组）

**概念解释**：Group 并行执行多个任务，等待所有任务完成后返回结果列表。适合需要同时处理多个独立任务的场景。

```python
from celery import group

@app.task
def send_notification(user_id: int, message: str) -> dict:
    """发送单个用户的通知"""
    notification_service.send(user_id, message)
    return {"user_id": user_id, "status": "sent"}

# Group：并行给多个用户发通知
def broadcast_notification(user_ids: list[int], message: str):
    """
    并行执行：同时给100个用户发通知
    比串行快100倍（取决于 Worker 并发数）
    """
    # 创建任务签名列表
    signatures = [
        send_notification.s(uid, message)
        for uid in user_ids
    ]

    # 创建 Group 并执行
    result = group(signatures)()

    # 等待所有完成（阻塞，慎用）
    results = result.get()
    # results 是按顺序的结果列表：
    # [{"user_id": 1, "status": "sent"}, {"user_id": 2, ...}, ...]

    success_count = sum(1 for r in results if r["status"] == "sent")
    return {"total": len(user_ids), "success": success_count}
```

```python
# Group 结果的非阻塞查询
def submit_broadcast(user_ids: list[int], message: str) -> str:
    """提交广播任务，返回 group_id"""
    result = group(
        send_notification.s(uid, message)
        for uid in user_ids
    ).apply_async()

    # result.id 是 group_id，可用于后续查询
    return result.id

def check_broadcast_status(group_id: str) -> dict:
    """查询广播进度"""
    from celery.result import GroupResult
    group_result = GroupResult.restore(group_id, app=app)

    total = len(group_result.results)
    done = sum(1 for r in group_result.results if r.ready())

    return {
        "total": total,
        "done": done,
        "percent": f"{done/total*100:.1f}%",
    }
```

### 8.3 Chord（和弦）

**概念解释**：Chord = Group + 回调。先并行执行一组任务（header），全部完成后执行一个回调任务（body）。适合"先并行处理，再汇总结果"的场景。

```python
from celery import chord

@app.task
def generate_report_by_dept(dept: str, month: str) -> dict:
    """生成单个部门的报表"""
    data = query_dept_data(dept, month)
    return {"dept": dept, "data": data, "total": len(data)}

@app.task
def generate_summary_report(reports: list, month: str) -> str:
    """汇总所有部门的报表（接收 header 所有结果的列表）"""
    total_all = sum(r["total"] for r in reports)
    summary = f"{month}月总数据：{total_all}条记录\n"
    for r in reports:
        summary += f"  - {r['dept']}: {r['total']}条\n"

    # 发送汇总报表
    send_summary_email.delay(summary)
    return summary
```

```python
# Chord：并行生成3个部门报表 → 全部完成后汇总
def monthly_report(month: str):
    """
    header: 并行执行 generate_report_by_dept
    body: 所有 header 任务完成后执行 generate_summary_report
    """
    departments = ['sales', 'finance', 'operations']

    # 方式一：chord 函数
    result = chord(
        header=[
            generate_report_by_dept.s(dept, month)
            for dept in departments
        ],
        body=generate_summary_report.s(month),  # 接收 header 结果列表
    )()

    return result.id

# 方式二：chord 链式写法
# result = (
#     chord(
#         generate_report_by_dept.s(dept, month)
#         for dept in departments
#     )
#     | generate_summary_report.s(month)
# )()
```

```python
# 复杂编排：Chain + Group + Chord 混合
def complex_workflow(user_id: int):
    """
    流程：
    1. 获取用户数据（单任务）
    2. 并行处理3个维度（Group）
    3. 汇总结果（Chord body）
    4. 保存并通知（Chain）
    """
    workflow = (
        fetch_user_data.s(user_id)
        | group(
            process_dimension_a.s(),
            process_dimension_b.s(),
            process_dimension_c.s(),
        )
        | summarize_results.s()
        | save_and_notify.s(user_id)
    )

    return workflow()
```

> ❌ **常见坑点**：Chord 在 Redis Broker 上性能较差。Chord 的回调需要等待所有 header 任务完成，Redis Broker 实现 Chord 的方式是不断轮询检查每个任务状态，当 header 任务数很多（>100）时性能严重下降。**正确做法**：header 任务数控制在几十个以内；大规模并行使用 RabbitMQ Broker；或改用 Group + 手动检查完成后发布回调任务。

> ✅ **最佳实践**：
> 1. Chain 适合线性流水线（A→B→C）
> 2. Group 适合并行独立任务（A、B、C同时跑）
> 3. Chord 适合并行+汇总（A/B/C并行→汇总D）
> 4. 复杂工作流组合使用，但不要超过3层嵌套
> 5. 监控编排工作流的中间状态

> 💡 **深度讲解**：任务编排是 Celery 区别于简单消息队列的核心能力。Chain 实现顺序依赖，Group 实现并行执行，Chord 实现"并行+汇总"模式。这三种原语可以组合出复杂的工作流。需要注意的是，Celery 的编排是"消息驱动"的——每个步骤都是独立的任务消息，中间状态存储在 Broker/Backend 中。这种设计保证了每个步骤都可以独立重试，但也意味着编排工作流的调试比普通函数调用更困难。生产环境建议为编排工作流添加详细日志和状态监控。

> 📝 **本章精简总结**：
> - 核心概念：chain（顺序）、group（并行）、chord（并行+回调）、Signature
> - 关键原理：.s() 创建签名、自动传递结果、消息驱动编排
> - 常用操作：chain(a.s(), b.s())、group([a.s(), b.s()])、chord(header, body)
> - 最佳实践：控制 chord header 大小、复杂工作流加日志
> - 常见坑点：Chord Redis 性能差、group.get() 阻塞
> - 面试高频：chain/group/chord 区别、Chord 实现原理

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：chain 和 group 的执行模式有什么本质区别？
>   - 答案：chain 顺序执行（前一个输出→后一个输入）；group 并行执行（同时启动，等待全部完成）
> - **进阶题（⭐⭐）**：Chord 为什么在 Redis Broker 上性能差？
>   - 思考方向：Chord 需要轮询检查所有 header 任务状态
> - **实战题（⭐⭐⭐）**：设计一个数据ETL工作流：并行从3个数据源抽取数据→清洗转换→加载到数仓→发送完成通知。用 chain/group/chord 组合实现。
>   - 提示：Group(抽取A/B/C) → Chord(清洗汇总) → Chain(加载→通知)

---

## 九、任务重试与错误处理

### 9.1 重试机制详解

**概念解释**：任务重试是指任务执行失败后自动重新执行。这是处理临时性错误（网络抖动、服务暂时不可用）的关键机制。

```python
# 方式一：autoretry_for 自动重试（推荐）
@app.task(
    autoretry_for=(ConnectionError, TimeoutError,),  # 这些异常自动重试
    max_retries=5,                  # 最多重试5次
    default_retry_delay=60,         # 默认重试间隔60秒
    retry_backoff=True,             # 指数退避
    retry_backoff_max=600,          # 最大退避间隔600秒
    retry_jitter=True,              # 加随机抖动
)
def call_external_api(user_id: int):
    """调用外部API，网络错误自动重试"""
    response = requests.get(f"https://api.example.com/users/{user_id}", timeout=10)
    response.raise_for_status()
    return response.json()
```

```python
# 方式二：手动重试（更灵活的控制）
@app.task(bind=True, max_retries=5)
def send_email(self, to: str, subject: str, body: str):
    try:
        result = email_service.send(to, subject, body)
        return result.message_id

    except ConnectionError as exc:
        # 第1次重试：60秒后
        # 第2次重试：120秒后
        # 第3次重试：240秒后
        delay = 60 * (2 ** self.request.retries)
        logger.warning(
            f"邮件发送失败(第{self.request.retries}次), "
            f"{delay}秒后重试: {exc}"
        )
        raise self.retry(exc=exc, countdown=delay)

    except Exception as exc:
        # 不可恢复的错误：不重试，直接失败
        logger.error(f"邮件发送致命错误: {exc}", exc_info=True)
        # 不调用 self.retry，任务标记为 FAILURE
        raise
```

```python
# 指数退避 + 抖动 详解
# retry_backoff=True 时的重试间隔（retry_backoff_max=600）：
# 第1次重试：1 * 2 = 2秒（加抖动±50%）
# 第2次重试：2 * 2 = 4秒
# 第3次重试：4 * 2 = 8秒
# 第4次重试：8 * 2 = 16秒
# 第5次重试：16 * 2 = 32秒（封顶 retry_backoff_max=600）

# retry_jitter=True 的作用：
# 不加抖动：所有任务在第 N 次重试时同时醒来 → 惊群效应
# 加抖动：实际间隔 = 计算值 * (0.5 ~ 1.5) → 分散重试时间
```

### 9.2 超时控制

```python
@app.task(
    # 硬超时：到时间直接 SIGKILL 杀掉进程
    time_limit=300,

    # 软超时：抛出 SoftTimeLimitExceeded，可被捕获处理
    soft_time_limit=240,
)
def long_running_task(task_id: str):
    """长时间运行的任务"""
    from celery.exceptions import SoftTimeLimitExceeded

    try:
        for i in range(10000):
            process_item(i)
            # 定期检查是否超时
            if i % 100 == 0:
                logger.info(f"进度: {i}/10000")
    except SoftTimeLimitExceeded:
        # 软超时：做清理工作后退出
        logger.warning(f"任务 {task_id} 软超时，保存中间状态")
        save_partial_progress(task_id, i)
        raise  # 重新抛出，Celery 标记任务为失败
```

| 超时类型 | 机制 | 捕获方式 | 用途 |
|---------|------|---------|------|
| **soft_time_limit** | 抛出异常 | `try/except SoftTimeLimitExceeded` | 优雅清理后退出 |
| **time_limit** | 直接杀进程 | 无法捕获 | 防止任务完全卡死 |

### 9.3 错误分类处理

```python
from celery.exceptions import (
    SoftTimeLimitExceeded,
    Retry,
    Ignore,
    Reject,
)

@app.task(bind=True, autoretry_for=(ConnectionError,), max_retries=3)
def robust_task(self, data: dict):
    """分类处理不同类型的错误"""
    try:
        result = risky_operation(data)

    except RecoverableError as exc:
        # 可恢复错误：重试
        logger.warning(f"可恢复错误，准备重试: {exc}")
        raise self.retry(exc=exc, countdown=30)

    except PermanentError as exc:
        # 永久性错误：不重试，记录后放弃
        logger.error(f"永久性错误，不重试: {exc}")
        # 使用 Ignore 让任务不被标记为失败
        raise Ignore()

    except ValidationError as exc:
        # 参数错误：拒绝（消息重新入队但不重试）
        logger.error(f"参数验证错误: {exc}")
        raise Reject(exc, requeue=False)

    except SoftTimeLimitExceeded:
        # 超时：保存进度后退出
        save_progress(data)
        raise

    except Exception as exc:
        # 未预期错误：记录完整堆栈
        logger.critical(f"未预期错误: {exc}", exc_info=True)
        raise  # 标记为 FAILURE，不自动重试

    return result
```

> ❌ **常见坑点**：`self.retry()` 忘记 `raise`。Celery 的重试机制要求 `raise self.retry(...)`，如果只调用不 raise，函数会继续执行后面的代码，重试不会生效。**正确做法**：始终 `raise self.retry(exc=exc)`。或者使用 `autoretry_for` 参数自动处理。

> ✅ **最佳实践**：
> 1. 区分可恢复错误（重试）和永久性错误（不重试）
> 2. 使用指数退避+抖动避免惊群
> 3. 设置合理的 max_retries（3-5次），避免无限重试
> 4. 软超时做清理，硬超时做兜底
> 5. 失败任务记录完整上下文，便于排查

> 💡 **深度讲解**：重试是分布式系统中处理临时性故障的标准手段。Celery 的重试设计有几个关键点：(1) `autoretry_for` 声明哪些异常自动重试，减少样板代码；(2) `retry_backoff` 指数退避避免重试风暴；(3) `retry_jitter` 随机打散防止惊群；(4) 软超时允许优雅清理，硬超时兜底防卡死。理解这些机制后，可以根据业务需求精细控制重试行为。

> 📝 **本章精简总结**：
> - 核心概念：autoretry_for、指数退避、jitter、软/硬超时
> - 关键原理：retry 必须 raise、可恢复vs永久性错误分类
> - 常用操作：配置 max_retries、self.retry(exc=exc, countdown=N)
> - 最佳实践：指数退避+抖动、分类处理错误、软超时清理
> - 常见坑点：self.retry 忘记 raise、无限重试
> - 面试高频：retry_backoff 原理、SoftTimeLimit vs TimeLimit

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：soft_time_limit 和 time_limit 的区别？
>   - 答案：soft 抛异常可捕获清理；time 直接杀进程无法捕获
> - **进阶题（⭐⭐）**：为什么 retry_jitter=True 能防止惊群效应？
>   - 思考方向：不加抖动时大量任务同时重试→同时访问同一资源→过载
> - **实战题（⭐⭐⭐）**：设计一个调用不稳定第三方 API 的任务。要求：最多重试5次、间隔指数增长、最后一次失败后发送告警通知。
>   - 提示：autoretry_for + retry_backoff + on_failure 信号发告警

---

## 十、Worker 管理与调优

### 10.1 Worker 启动与参数

```bash
# 基础启动
celery -A celery_app worker --loglevel=info

# 指定并发数（默认=CPU核心数）
celery -A celery_app worker --concurrency=8

# 指定队列
celery -A celery_app worker --queues=default,email

# 指定主机名
celery -A celery_app worker --hostname=worker1@%h

# 预取倍数
celery -A celery_app worker --prefetch-multiplier=4

# 最大任务数（每个子进程执行N个任务后重启）
celery -A celery_app worker --max-tasks-per-child=1000

# 最大内存（KB）
celery -A celery_app worker --max-memory-per-child=200000
```

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|---------|
| `--concurrency` | CPU核心数 | Worker 子进程/协程数 | CPU密集=核心数；IO密集=100-1000 |
| `--prefetch-multiplier` | 4 | 每个 Worker 预取任务数 | CPU密集=1；IO密集=4-16 |
| `--max-tasks-per-child` | 无限制 | 子进程执行N任务后重启 | 1000-5000（防内存泄漏） |
| `--max-memory-per-child` | 无限制 | 子进程内存上限(KB) | 200000=200MB |
| `--pool` | prefork | 并发模型 | prefork/gevent/eventlet/solo |
| `--loglevel` | warning | 日志级别 | info/debug 用于调试 |

### 10.2 Worker 自动扩展

```bash
# 安装 autoscale 支持
pip install celery

# 启动时配置自动扩展
celery -A celery_app worker --autoscale=10,2
# 格式：--autoscale=MAX,MIN
# 平时保持2个进程，任务多时自动扩到10个，空闲后缩回2个
```

```python
# 代码中动态控制自动扩展
from celery.app.control import Control

def scale_worker(hostname: str, max: int, min: int = 1):
    """动态调整 Worker 并发数"""
    app.control.autoscale(max, min, destination=[hostname])

# 查看当前 Worker 状态
def get_worker_stats():
    """获取所有 Worker 的统计信息"""
    stats = app.control.inspect().stats()
    for worker_name, stat in stats.items():
        print(f"{worker_name}:")
        print(f"  并发数: {stat['pool']['max-concurrency']}")
        print(f"  已处理任务: {stat['total']}")
```

### 10.3 Worker 信号系统

```python
from celery.signals import (
    worker_process_init,    # Worker 子进程初始化
    worker_process_shutdown, # Worker 子进程关闭
    task_prerun,           # 任务开始前
    task_postrun,          # 任务结束后
    task_failure,          # 任务失败
    task_retry,            # 任务重试
    task_success,          # 任务成功
    task_revoked,          # 任务被撤销
)

@worker_process_init.connect
def init_worker_process(**kwargs):
    """
    每个 Worker 子进程启动时执行
    适用于：初始化数据库连接、加载模型、初始化客户端
    """
    logger.info("Worker 子进程初始化")
    # 在子进程中初始化数据库连接池
    # 避免 fork 后连接失效的问题
    init_db_pool()
    # 加载机器学习模型到内存
    load_ml_model()

@worker_process_shutdown.connect
def cleanup_worker_process(**kwargs):
    """每个 Worker 子进程关闭时清理"""
    logger.info("Worker 子进程清理")
    close_db_pool()
```

```python
# 任务级信号
@task_failure.connect
def on_task_failure(sender=None, task_id=None, exception=None, traceback=None, **kwargs):
    """任务失败时触发：发送告警"""
    error_msg = (
        f"任务失败告警\n"
        f"任务: {sender.name}\n"
        f"任务ID: {task_id}\n"
        f"错误: {exception}\n"
        f"堆栈: {traceback}"
    )
    # 发送到钉钉/飞书/Sentry
    send_alert_to_dingtalk(error_msg)

@task_retry.connect
def on_task_retry(sender=None, task_id=None, reason=None, einfo=None, **kwargs):
    """任务重试时触发"""
    logger.warning(f"任务重试: {sender.name}[{task_id}] 原因: {reason}")
```

> ❌ **常见坑点**：prefork 模式下数据库连接在 fork 后失效。主进程创建数据库连接池后 fork 出子进程，子进程继承了父进程的连接，但这些连接在子进程中已经失效（PostgreSQL 每个连接对应一个后端进程，fork 后连接状态不一致）。**正确做法**：在 `worker_process_init` 信号中为每个子进程创建独立的连接池，而不是在主进程创建后继承。

### 10.4 优雅停止 Worker

```bash
# SIGTERM：优雅停止（推荐）
# 等待当前任务执行完成，然后退出
kill -TERM <pid>

# SIGINT：Ctrl+C，同 SIGTERM
kill -INT <pid>

# SIGQUIT：立即停止（不等待任务完成）
# ⚠️ 未完成的任务会重新入队（如果开启了 task_acks_late）
kill -QUIT <pid>

# SIGUSR1：立即停止但保留任务（用于调试）
kill -USR1 <pid>
```

```python
# Celery 任务去重（防止重复提交同一任务）
# 使用 celery-singleton 或自定义实现
import hashlib
import json

@app.task(bind=True)
def deduplicated_task(self, params: dict):
    """带去重功能的任务：相同参数5分钟内只执行一次"""
    # 根据参数生成唯一键
    param_hash = hashlib.md5(
        json.dumps(params, sort_keys=True).encode()
    ).hexdigest()
    dedup_key = f"dedup:task:{self.name}:{param_hash}"

    # 检查是否已存在
    if redis_client.get(dedup_key):
        logger.info(f"任务已存在，跳过: {dedup_key}")
        return {"status": "duplicate_skipped"}

    # 设置去重标记（5分钟过期）
    redis_client.setex(dedup_key, 300, "1")

    try:
        result = do_work(params)
        return result
    except Exception:
        # 失败时清除去重标记，允许重试
        redis_client.delete(dedup_key)
        raise
```

```python
# 优雅的 Worker 关闭流程（SIGTERM）
# 1. 停止从 Broker 拉取新任务
# 2. 等待当前正在执行的任务完成
# 3. 对正在执行的任务发送 ACK
# 4. 关闭数据库连接等资源
# 5. 退出进程

# 对应的信号处理时序：
# SIGTERM → warm shutdown → waiting tasks → all acknowledged → exit(0)

# 如果需要强制退出（不推荐）：
# SIGQUIT → 立即停止 → 未完成任务重新入队（acks_late=True时）
```

> ✅ **最佳实践**：生产环境停止 Worker 时使用 SIGTERM（Systemd 的默认行为），让 Worker 完成当前任务后优雅退出。强制 kill（SIGKILL）会导致任务中断，如果开启了 `task_acks_late` 任务会重新入队，但可能造成数据不一致。

> 💡 **深度讲解**：Worker 管理是 Celery 生产运维的核心。关键调优点包括：(1) `worker_max_tasks_per_child` 防止内存泄漏累积；(2) `prefetch_multiplier` 根据任务类型调整——CPU密集设为1避免任务分配不均，IO密集设大提高吞吐量；(3) `worker_process_init` 信号中初始化子进程资源，解决 fork 连接问题；(4) 自动扩展应对流量波动。优雅停止（SIGTERM）确保任务不中断，是生产部署的基本要求。

> 📝 **本章精简总结**：
> - 核心概念：Worker 子进程、并发模型、预取、信号系统
> - 关键原理：fork 后连接失效、子进程重启防泄漏、优雅停止
> - 常用操作：-c 并发数、-Q 队列、--max-tasks-per-child、信号注册
> - 最佳实践：子进程中初始化连接池、设置内存上限、优雅停止
> - 常见坑点：fork 后数据库连接失效、SIGKILL 中断任务
> - 面试高频：prefork vs gevent、worker_process_init 作用

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：`--max-tasks-per-child=1000` 的作用是什么？
>   - 答案：每个子进程执行1000个任务后重启，释放内存，防止泄漏累积
> - **进阶题（⭐⭐）**：为什么 prefork 模式下不能在主进程创建数据库连接？
>   - 思考方向：fork 后文件描述符复制、PostgreSQL 后端进程状态
> - **实战题（⭐⭐⭐）**：一个 Worker 运行几天后内存持续增长，最终 OOM。如何排查和解决？
>   - 提示：设置 worker_max_memory_per_child + tracemalloc 定位泄漏点

---

## 十一、监控与管理（Flower）

### 11.1 Flower 安装与启动

**概念解释**：Flower 是 Celery 的实时监控和管理 Web 工具，提供任务状态查看、Worker 监控、任务撤销、速率调整等功能。

```bash
# 安装 Flower
pip install flower

# 启动 Flower（连接到 Broker）
celery -A celery_app flower --port=5555

# 带认证启动
celery -A celery_app flower \
    --port=5555 \
    --basic_auth=admin:yourpassword \
    --url_prefix=flower  # 反向代理时的 URL 前缀

# 指定 Broker
celery -A celery_app flower \
    --broker=redis://localhost:6379/0 \
    --port=5555
```

### 11.2 Flower 功能与 API

```python
# Flower REST API 示例
import requests

FLOWER_URL = "http://localhost:5555/api"
AUTH = ("admin", "yourpassword")

# 获取所有 Worker
def get_workers():
    resp = requests.get(f"{FLOWER_URL}/workers", auth=AUTH)
    workers = resp.json()
    for name, info in workers.items():
        print(f"Worker: {name}")
        print(f"  状态: {'在线' if info['status'] else '离线'}")
        print(f"  活跃任务: {len(info.get('active', []))}")
        print(f"  队列: {info.get('active_queues', [])}")

# 获取任务列表
def get_tasks(state: str = None):
    url = f"{FLOWER_URL}/tasks"
    if state:
        url += f"?state={state}"
    resp = requests.get(url, auth=AUTH)
    return resp.json()

# 撤销任务
def revoke_task(task_id: str, terminate: bool = False):
    requests.post(
        f"{FLOWER_URL}/task/revoke",
        auth=AUTH,
        json={"task_id": task_id, "terminate": terminate}
    )

# 重新执行任务
def rerun_task(task_id: str):
    requests.post(
        f"{FLOWER_URL}/task/retry",
        auth=AUTH,
        json={"task_id": task_id}
    )

# 控制 Worker（关闭/重启/扩容）
def shutdown_worker(worker_name: str):
    requests.post(
        f"{FLOWER_URL}/worker/shutdown/{worker_name}",
        auth=AUTH
    )
```

### 11.3 Prometheus 监控集成

```python
# 安装 celery-prometheus-exporter
# pip install celery-prometheus-exporter

# 启动 exporter
# celery -A celery_app flower --prom-port=9808

# 或使用独立 exporter
# celery-prometheus-exporter --broker=redis://localhost:6379/0
```

```python
# 自定义 Prometheus 指标
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from celery.signals import task_prerun, task_postrun, task_failure

# 任务计数器
task_total = Counter(
    'celery_tasks_total',
    'Total number of tasks',
    ['task_name', 'state']
)

# 任务耗时直方图
task_duration = Histogram(
    'celery_task_duration_seconds',
    'Task duration in seconds',
    ['task_name']
)

# 活跃任务数
active_tasks = Gauge(
    'celery_active_tasks',
    'Number of active tasks',
    ['queue']
)

@task_prerun.connect
def before_task(sender=None, task_id=None, **kwargs):
    active_tasks.labels(queue='default').inc()

@task_postrun.connect
def after_task(sender=None, task_id=None, state=None, **kwargs):
    active_tasks.labels(queue='default').dec()
    task_total.labels(task_name=sender.name, state=state).inc()

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    task_total.labels(task_name=sender.name, state='FAILURE').inc()
    # 发送告警
    send_alert(f"任务失败: {sender.name} - {exception}")
```

> ❌ **常见坑点**：Flower 版本与 Celery 版本不兼容导致连不上。Flower 版本必须与 Celery 大版本匹配。**正确做法**：安装时指定兼容版本，如 `pip install flower==2.0.*` 对应 Celery 5.x。

```python
# 单元测试中使用 Celery（task_always_eager）
# tests/test_tasks.py
import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def celery_eager_mode(app):
    """测试环境：Celery 同步执行"""
    app.conf.task_always_eager = True
    app.conf.task_eager_propagates = True
    yield

def test_send_email_task():
    """测试邮件任务：同步执行，Mock 外部服务"""
    with patch('tasks.email.email_service.send') as mock_send:
        mock_send.return_value.message_id = "msg_123"

        result = send_email.delay("test@example.com", "主题", "内容")

        # 同步执行后立即可获取结果
        assert result.get()["status"] == "success"
        mock_send.assert_called_once()

def test_task_retry_on_failure():
    """测试任务重试逻辑"""
    with patch('tasks.email.email_service.send') as mock_send:
        # 前两次失败，第三次成功
        mock_send.side_effect = [
            ConnectionError("网络错误"),
            ConnectionError("网络错误"),
            MagicMock(message_id="msg_456"),
        ]

        result = send_email.delay("test@example.com", "主题", "内容")

        # eager 模式下 max_retries 内会自动重试
        assert mock_send.call_count == 3
```

```python
# Celery 健康检查任务
@app.task
def health_check():
    """系统健康检查：检查 Broker、Backend、数据库连接"""
    checks = {}

    # 检查 Broker 连接
    try:
        app.connection().ensure_connection(timeout=5)
        checks['broker'] = 'ok'
    except Exception as e:
        checks['broker'] = f'error: {e}'

    # 检查 Backend 连接
    try:
        from celery.result import AsyncResult
        AsyncResult('test', app=app).status
        checks['backend'] = 'ok'
    except Exception as e:
        checks['backend'] = f'error: {e}'

    # 检查数据库连接
    try:
        db.session.execute('SELECT 1')
        checks['database'] = 'ok'
    except Exception as e:
        checks['database'] = f'error: {e}'

    all_ok = all(v == 'ok' for v in checks.values())
    return {'status': 'healthy' if all_ok else 'unhealthy', 'checks': checks}

# 定时健康检查
app.conf.beat_schedule['health-check-every-5min'] = {
    'task': 'tasks.health_check',
    'schedule': 300,
}
```

```python
# 任务结果分页查询（大量历史任务）
# 使用 Flower API 查询历史任务
import requests

def query_task_history(state: str = 'SUCCESS', limit: int = 100, offset: int = 0):
    """分页查询历史任务"""
    resp = requests.get(
        "http://localhost:5555/api/tasks",
        auth=("admin", "pass"),
        params={
            'state': state,
            'limit': limit,
            'offset': offset,
        }
    )
    tasks = resp.json()
    return [
        {
            'id': tid,
            'name': info.get('name'),
            'state': info.get('state'),
            'timestamp': info.get('timestamp'),
            'result': info.get('result'),
        }
        for tid, info in tasks.items()
    ]
```

> 💡 **深度讲解**：监控是生产环境不可缺少的环节。Flower 提供了直观的 Web 界面查看任务状态、Worker 状态和队列长度。对于大规模系统，推荐结合 Prometheus + Grafana 实现指标采集和可视化告警。关键监控指标包括：任务吞吐量（tasks/s）、任务延迟（从发布到开始执行的时间）、队列长度（积压程度）、失败率、Worker 内存/CPU 使用。

> 📝 **本章精简总结**：
> - 核心概念：Flower 监控、REST API、Prometheus 指标
> - 关键原理：Celery 事件系统、信号采集指标
> - 常用操作：启动 Flower、查询 Worker/任务、撤销任务
> - 最佳实践：Flower 加认证、Prometheus+Grafana 告警
> - 常见坑点：版本不兼容、Flower 暴露公网风险
> - 面试高频：如何监控 Celery 任务状态？

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：Flower 默认端口是多少？如何加认证？
>   - 答案：5555端口，--basic_auth=user:pass
> - **进阶题（⭐⭐）**：除了 Flower，还有哪些方式监控 Celery？
>   - 思考方向：Prometheus exporter、日志监控、自定义指标
> - **实战题（⭐⭐⭐）**：为 Celery 系统设计告警规则：任务失败率>5%、队列积压>1000、Worker 离线。用 PromQL 实现。
>   - 提示：rate(celery_tasks_total{state="FAILURE"}[5m]) / rate(celery_tasks_total[5m]) > 0.05

---

## 十二、与 Web 框架集成

### 12.1 FastAPI 集成

```python
# main.py —— FastAPI + Celery 完整示例
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from celery.result import AsyncResult
from celery_app import app as celery_app
from tasks import send_email, generate_report, process_order

app = FastAPI(title="Celery + FastAPI 示例")


# 请求模型
class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

class ReportRequest(BaseModel):
    report_type: str
    month: str


@app.post("/api/email/send", status_code=202)
async def api_send_email(req: EmailRequest):
    """
    异步发送邮件：立即返回 task_id
    202 Accepted = 已接受请求，正在处理
    """
    task = send_email.delay(req.to, req.subject, req.body)
    return {
        "task_id": task.id,
        "status": "accepted",
        "message": "邮件发送任务已提交",
    }


@app.get("/api/tasks/{task_id}")
async def api_get_task_status(task_id: str):
    """查询任务状态（前端轮询）"""
    result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": result.status,
        "ready": result.ready(),
    }

    if result.ready():
        if result.successful():
            response["result"] = result.result
        elif result.failed():
            response["error"] = str(result.result)

    return response


@app.post("/api/reports/generate", status_code=202)
async def api_generate_report(req: ReportRequest):
    """生成报表：慢任务异步处理"""
    task = generate_report.apply_async(
        args=[req.report_type, req.month],
        queue='report',  # 路由到报表队列
    )
    return {
        "task_id": task.id,
        "status": "processing",
        "estimated_time": "60秒",
    }


@app.post("/api/orders/{order_id}/cancel")
async def api_cancel_order(order_id: int):
    """撤销订单处理任务"""
    task_id = get_order_task_id(order_id)  # 从数据库获取关联的 task_id
    if task_id:
        AsyncResult(task_id, app=celery_app).revoke(terminate=True)
        return {"status": "cancelled", "order_id": order_id}
    raise HTTPException(status_code=404, detail="任务不存在或已完成")
```

```python
# tasks/progress.py —— 任务进度更新（FastAPI 轮询进度）
@app.task(bind=True)
def long_process_task(self, file_path: str):
    """长时间任务：实时更新进度"""
    total_lines = count_lines(file_path)

    for i, line in enumerate(read_lines(file_path)):
        process_line(line)

        # 每处理100行更新一次进度
        if i % 100 == 0:
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i,
                    'total': total_lines,
                    'percent': f"{i/total_lines*100:.1f}%",
                }
            )

    return {'status': 'complete', 'processed': total_lines}
```

```python
# FastAPI 端查询进度
@app.get("/api/progress/{task_id}")
async def get_progress(task_id: str):
    result = AsyncResult(task_id, app=celery_app)

    if result.state == 'PROGRESS':
        return {
            "status": "processing",
            "progress": result.result,  # update_state 中的 meta
        }
    elif result.ready():
        return {"status": "done", "result": result.result}
    else:
        return {"status": "pending"}
```

### 12.2 Django 集成

```python
# Django settings.py 配置
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'

# Django + Celery 应用初始化（myapp/celery.py）
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')

app = Celery('myapp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()  # 自动发现各 app 的 tasks.py
```

```python
# Django app 中的任务（myapp/users/tasks.py）
from celery import shared_task
from django.core.mail import send_mail
from .models import User

@shared_task
def send_welcome_email(user_id: int):
    """Django 共享任务（不需要绑定具体 app）"""
    user = User.objects.get(id=user_id)
    send_mail(
        subject="欢迎注册",
        message=f"欢迎 {user.username}！",
        from_email="noreply@example.com",
        recipient_list=[user.email],
        fail_silently=False,
    )
    return f"欢迎邮件已发送至 {user.email}"

# 在 Django View 中调用
# from .tasks import send_welcome_email
# send_welcome_email.delay(user.id)
```

> ❌ **常见坑点**：FastAPI 的 `BackgroundTasks` 和 Celery 混淆。`BackgroundTasks` 在 Web 进程内执行，Web 进程重启或崩溃时任务丢失；Celery 在独立 Worker 进程执行，持久化可靠。**正确做法**：短任务（<1秒）用 BackgroundTasks；长任务、需要重试、需要持久化的用 Celery。

> 💡 **深度讲解**：Web 框架集成 Celery 的核心模式是"提交-轮询"——API 立即返回 task_id，前端轮询任务状态。这比同步等待更好：避免 Web 连接超时、提高并发能力、支持任务重试。FastAPI 中要注意 async/await——Celery 的 delay() 是同步调用，在 async 视图中不会阻塞事件循环太多（只是发一条消息到 Broker），但要避免在 async 视图中调用 `result.get()`（会阻塞事件循环）。

> 📝 **本章精简总结**：
> - 核心概念：FastAPI 集成模式、Django shared_task、进度更新
> - 关键原理：提交-轮询模式、202 Accepted 状态码
> - 常用操作：delay() 提交、AsyncResult 查询、update_state 更新进度
> - 最佳实践：API 返回 202、前端轮询进度、长任务路由到慢队列
> - 常见坑点：async 视图中 result.get() 阻塞事件循环
> - 面试高频：Celery vs BackgroundTasks、如何实现任务进度查询

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：FastAPI 中 Celery 任务提交后应该返回什么状态码？
>   - 答案：202 Accepted（已接受，正在处理）
> - **进阶题（⭐⭐）**：如何实现任务的实时进度查询？
>   - 思考方向：self.update_state(state='PROGRESS', meta={...})
> - **实战题（⭐⭐⭐）**：为一个文件上传处理 API 设计：上传文件→异步处理→轮询进度→下载结果。用 FastAPI + Celery 实现。
>   - 提示：POST 上传返回 task_id → GET /progress 查进度 → 完成后 GET /download 下载

---

## 十三、生产部署与性能优化

### 13.1 Systemd 部署

```ini
# /etc/systemd/system/celery-worker.service
[Unit]
Description=Celery Worker
After=network.target redis.service rabbitmq.service
Wants=redis.service

[Service]
Type=simple
User=celery
Group=celery
WorkingDirectory=/opt/myapp
Environment="PATH=/opt/myapp/venv/bin"
Environment="CELERY_BROKER_URL=redis://localhost:6379/0"
Environment="CELERY_RESULT_BACKEND=redis://localhost:6379/1"

ExecStart=/opt/myapp/venv/bin/celery -A celery_app worker \
    --loglevel=info \
    --concurrency=8 \
    --queues=default,email \
    --max-tasks-per-child=1000 \
    --max-memory-per-child=200000 \
    --hostname=worker1@%h

ExecReload=/bin/kill -HUP $MAINPID
ExecStop=/bin/kill -TERM $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/celery-beat.service
[Unit]
Description=Celery Beat Scheduler
After=network.target redis.service

[Service]
Type=simple
User=celery
WorkingDirectory=/opt/myapp
Environment="PATH=/opt/myapp/venv/bin"
ExecStart=/opt/myapp/venv/bin/celery -A celery_app beat \
    --loglevel=info \
    --schedule=/var/lib/celery/celerybeat-schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启动管理
sudo systemctl daemon-reload
sudo systemctl enable celery-worker celery-beat
sudo systemctl start celery-worker celery-beat
sudo systemctl status celery-worker
sudo journalctl -u celery-worker -f  # 查看日志
```

### 13.2 Docker 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 默认命令（可被 docker-compose 覆盖）
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: always

  worker-default:
    build: .
    command: celery -A celery_app worker -Q default -c 4 --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      - redis
    restart: always
    deploy:
      replicas: 2  # Docker Swarm 下扩展

  worker-email:
    build: .
    command: celery -A celery_app worker -Q email -c 2 --loglevel=info
    depends_on:
      - redis
    restart: always

  beat:
    build: .
    command: celery -A celery_app beat --loglevel=info
    depends_on:
      - redis
    restart: always

  flower:
    build: .
    command: celery -A celery_app flower --port=5555 --basic_auth=admin:secret
    ports:
      - "5555:5555"
    depends_on:
      - redis
    restart: always

volumes:
  redis_data:
```

### 13.3 性能优化 Checklist

| 优化项 | 配置 | 预期收益 |
|--------|------|---------|
| **连接池** | Broker 连接复用 | 减少 TCP 握手开销 |
| **Prefetch** | `worker_prefetch_multiplier=4` | 提高吞吐 |
| **结果过期** | `result_expires=3600` | 节省 Backend 内存 |
| **忽略结果** | `ignore_result=True` | 不存结果，零开销 |
| **序列化** | JSON + gzip 压缩 | 减少网络传输 |
| **子进程回收** | `max_tasks_per_child=1000` | 防内存泄漏 |
| **多队列** | 快慢分离 | 慢任务不阻塞快任务 |
| **Gevent** | IO密集任务用协程 | 单机并发 ×10 |
| **批量任务** | group + execute_values | 批量处理快10倍 |
| **Broker 优化** | Redis pipelining | 减少网络往返 |

> ✅ **最佳实践 Checklist**：
> - [ ] `task_acks_late=True` + `task_reject_on_worker_lost=True`
> - [ ] `worker_max_tasks_per_child=1000`
> - [ ] `worker_max_memory_per_child=200000`
> - [ ] 显式指定任务 `name`
> - [ ] `time_limit` + `soft_time_limit` 防卡死
> - [ ] 任务幂等设计
> - [ ] 按任务类型分队列
> - [ ] Beat 单实例
> - [ ] Flower 加认证
> - [ ] 失败任务告警

> 💡 **深度讲解**：生产部署 Celery 需要考虑的核心问题是可靠性和可运维性。可靠性方面：Broker 持久化、晚 ACK、任务幂等、Worker 崩溃恢复。可运维性方面：Systemd/Docker 进程管理、Flower 监控、日志收集、告警机制。性能优化从三个层面入手：任务层面（批处理、避免大结果）、Worker 层面（并发模型选择、预取调整）、Broker 层面（多队列分离、连接优化）。

> 📝 **本章精简总结**：
> - 核心概念：Systemd/Docker 部署、性能优化、可靠性
> - 关键原理：优雅停止、子进程回收、多队列隔离
> - 常用操作：systemctl 管理、docker-compose 编排
> - 最佳实践：晚ACK+幂等、多队列、Beat单实例、监控告警
> - 常见坑点：多Beat重复任务、OOM内存泄漏
> - 面试高频：生产部署架构、性能优化手段

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：为什么 Beat 不能水平扩展？
>   - 答案：Beat 是单实例调度器，多实例会重复发布定时任务
> - **进阶题（⭐⭐）**：如何设计一个高可用的 Celery 集群？
>   - 思考方向：Broker 高可用（Redis Sentinel）+ Worker 多实例 + Beat 主备
> - **实战题（⭐⭐⭐）**：公司从 Redis Broker 迁移到 RabbitMQ，需要注意哪些问题？
>   - 提示：消息格式兼容性、队列声明差异、优先级支持、运维监控变化

---

## 十四、常见坑点与故障排查

### 14.1 故障排查速查表

| 问题现象 | 可能原因 | 排查步骤 | 解决方案 |
|---------|---------|---------|---------|
| **Worker 不消费任务** | Broker 连接失败 | `redis-cli ping` 检查 | 检查 Broker URL、网络、密码 |
| | 队列名不匹配 | `celery inspect active_queues` | 确认 -Q 参数和 task_routes |
| | 任务未注册 | `celery inspect registered` | 检查 include 配置、任务 import |
| | Worker 没启动 | `ps aux grep celery` | 启动 Worker |
| **任务丢失** | 未开启 acks_late | 检查配置 | `task_acks_late=True` |
| | Worker 被 SIGKILL | 检查 OOM killer | 调小并发、增加内存 |
| | Broker 数据丢失 | Redis RDB/AOF 配置 | 开启 AOF 持久化 |
| **任务重复执行** | 网络超时 ACK 丢失 | 查看 Worker 日志 | 任务幂等设计 |
| | visibility_timeout 太短 | 检查 Redis 配置 | 调大 visibility_timeout |
| **任务执行慢** | Worker 并发不够 | 查看 Flower | 增加并发/Worker |
| | 任务本身慢 | profiler 分析 | 优化任务逻辑 |
| | 数据库慢查询 | 查看慢查询日志 | 优化 SQL/加索引 |
| **内存泄漏** | 大对象未释放 | tracemalloc 分析 | max_tasks_per_child |
| | 第三方库泄漏 | 更新依赖版本 | 定期重启子进程 |
| **定时任务不执行** | Beat 未启动 | `ps aux grep beat` | 启动 Beat |
| | 时区不对 | 检查时区配置 | `timezone='Asia/Shanghai'` |
| | 多 Beat 实例 | `ps aux grep beat` | 只保留一个 Beat |
| **结果查不到** | Backend 配置错误 | 检查 result_backend | 确认 Backend 连接 |
| | 结果已过期 | 检查 result_expires | 调大过期时间 |

### 14.2 调试技巧

```python
# 开发环境：同步执行任务（不经过 Broker）
app.conf.task_always_eager = True
app.conf.task_eager_propagates = True  # 异常直接抛出

# 这样 delay() 就变成同步执行，方便调试
result = send_email.delay("test@example.com", "主题", "内容")
# 直接在当前进程执行，立即看到结果和错误
```

```bash
# 查看已注册的任务
celery -A celery_app inspect registered

# 查看活跃任务
celery -A celery_app inspect active

# 查看保留任务（预取但未执行）
celery -A celery_app inspect reserved

# 查看统计信息
celery -A celery_app inspect stats

# 查看所有 Worker
celery -A celery_app inspect ping

# 查看日志（详细模式）
celery -A celery_app worker --loglevel=debug
```

```python
# 在任务中添加调试日志
@app.task(bind=True)
def debuggable_task(self, param):
    """带详细日志的任务，便于排查"""
    logger.info(f"任务ID: {self.request.id}")
    logger.info(f"重试次数: {self.request.retries}")
    logger.info(f"参数: {param}")
    logger.info(f"当前节点: {self.request.hostname}")

    try:
        result = do_work(param)
        logger.info(f"任务成功: {result}")
        return result
    except Exception as e:
        logger.error(f"任务失败: {e}", exc_info=True)
        raise
```

### 14.3 面试高频考点汇总

```text
Celery 面试高频考点清单：

1. Celery 的架构组成？
   → Producer, Broker, Worker, Result Backend, Beat

2. Broker 选型？Redis vs RabbitMQ？
   → Redis 简单性能好；RabbitMQ 功能完善可靠

3. delay() vs apply_async()？
   → delay 简单调用；apply_async 支持 countdown/eta/queue/priority

4. task_acks_late 的作用？
   → 执行完才ACK，Worker崩溃不丢任务

5. prefork vs gevent？
   → prefork多进程CPU密集；gevent协程IO密集

6. chain/group/chord 区别？
   → chain顺序；group并行；chord并行+回调

7. 如何实现任务幂等？
   → Redis SETNX去重 + 状态机

8. Beat 为什么单实例？
   → 多实例重复发布定时任务

9. result.get() 为什么不能在Web用？
   → 阻塞Web线程，耗尽连接池

10. 任务重复执行的原因和解决？
    → ACK丢失/超时重投；幂等设计+去重

11. Worker 内存泄漏怎么处理？
    → max_tasks_per_child + tracemalloc

12. 如何监控 Celery？
    → Flower + Prometheus + 日志告警

13. countdown 和 eta 区别？
    → countdown相对延迟；eta绝对时间

14. 任务序列化为什么不用pickle？
    → 安全风险 + 跨语言不兼容

15. 多队列的作用？
    → 快慢分离，慢任务不阻塞快任务
```

> 💡 **深度讲解**：故障排查的核心方法论是"分层定位"——先确认 Broker 是否正常（消息是否到达），再确认 Worker 是否正常消费（是否拿到消息），最后确认任务逻辑是否正确（执行是否报错）。使用 `celery inspect` 命令可以快速定位问题所在层。开发环境开启 `task_always_eager=True` 可以直接在 Python 中调试任务逻辑，排除 Broker/Worker 层问题。

> 📝 **本章精简总结**：
> - 核心概念：故障分层定位、调试技巧、面试考点
> - 关键原理：Broker层→Worker层→任务逻辑层排查
> - 常用操作：inspect 命令、eager 模式、日志调试
> - 最佳实践：生产前对照 Checklist 检查
> - 常见坑点：Worker 不消费先查队列名和 include
> - 面试高频：15个核心考点已汇总

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：`task_always_eager=True` 的作用是什么？
>   - 答案：任务同步执行，不经过 Broker，用于调试和单元测试
> - **进阶题（⭐⭐）**：任务提交后 Worker 不消费，排查思路是什么？
>   - 思考方向：Broker连通性→队列名匹配→任务注册→Worker启动状态
> - **实战题（⭐⭐⭐）**：线上环境突然大量任务失败，错误是数据库连接超时。给出排查和解决步骤。
>   - 提示：检查数据库连接池→Worker子进程数→慢查询→数据库负载

---

## 十五、进阶拓展与学习资源

### 15.1 Celery 生态工具

| 工具 | 用途 | 说明 |
|------|------|------|
| **Flower** | 监控 Web UI | 实时查看任务和 Worker |
| **django-celery-beat** | 数据库定时任务 | Django Admin 管理定时任务 |
| **django-celery-results** | Django 结果存储 | 任务结果存 Django ORM |
| **celery-progress** | 任务进度条 | 前端显示任务进度 |
| **flower** + **prometheus** | 指标监控 | Grafana 可视化 |
| **sentry** | 错误追踪 | 自动上报任务异常 |
| **celery-singleton** | 单例任务 | 防止同一任务重复执行 |

### 15.2 学习路径推荐

```text
Celery 进阶学习路径：

初级（1-2周）
  ├── 完成本文所有代码示例
  ├── 搭建本地 Redis + Celery 环境
  └── 实现一个完整的异步任务项目

中级（2-4周）
  ├── 多队列路由 + Flower 监控
  ├── chain/group/chord 编排复杂工作流
  ├── 生产环境部署（Systemd + Docker）
  └── 性能调优（并发模型、预取、连接池）

高级（1-3月）
  ├── 源码阅读：任务调度器、Mingle、Gossip 协议
  ├── 自定义任务基类、自定义序列化器
  ├── 大规模集群架构（Broker 高可用、Worker 自动扩展）
  └── 与 Airflow/Dagster 等工作流系统对比
```

### 15.3 推荐资源

```text
官方资源：
  - Celery 官方文档：https://docs.celeryq.dev/
  - Celery GitHub：https://github.com/celery/celery
  - Flower 文档：https://flower.readthedocs.io/

实践资源：
  - Celery 最佳实践：https://docs.celeryq.dev/en/stable/userguide/configuration.html
  - Production Checklist：https://docs.celeryq.dev/en/stable/userguide/faq.html
  - Instagram 工程博客（Celery 大规模实践）

进阶阅读：
  - RabbitMQ 可靠模式：Publisher Confirms + Consumer Acknowledgements
  - Redis 持久化：RDB vs AOF
  - 分布式系统：至少一次投递、幂等性设计
```

> 💡 **深度讲解**：Celery 虽然功能完善，但它不是万能的。对于需要复杂 DAG 依赖、数据血缘追踪、定时重跑的场景，应该考虑 Airflow、Dagster 等专业工作流调度系统。Celery 更适合"即时异步任务"和"简单定时任务"场景。理解工具的适用边界，比精通工具本身更重要。

> 📝 **本章精简总结**：
> - 核心概念：Celery 生态、学习路径、工具选型
> - 关键原理：Celery vs Airflow 适用场景
> - 常用工具：Flower、django-celery-beat、sentry
> - 最佳实践：根据场景选择合适工具
> - 常见坑点：Celery 不适合复杂 DAG 工作流

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：Celery 和 Airflow 的适用场景有什么区别？
>   - 答案：Celery 适合即时异步任务；Airflow 适合复杂 DAG 数据管道
> - **进阶题（⭐⭐）**：什么场景下应该用 Celery Beat，什么场景应该用系统 crontab？
>   - 思考方向：任务需要监控/重试/分布式→Celery；简单单节点脚本→crontab
> - **实战题（⭐⭐⭐）**：团队要引入 Celery，需要做技术选型报告。请列出选型评估维度和推荐方案。
>   - 提示：从功能需求、运维成本、团队技能、扩展性、社区活跃度评估

---

**🔗 关联笔记**

- [[Python-异步编程asyncio]] — Python 异步编程基础
- [[Redis-Python客户端与缓存策略]] — Redis 详细用法
- [[FastAPI-路由与依赖注入]] — FastAPI Web 框架
- [[SQLAlchemy-ORM核心原理]] — 数据库 ORM
- [[Python-集成测试与E2E测试]] — 测试策略

**📖 前置知识**

- [[Python-语法基础与数据结构]]
- [[Python-异步编程asyncio]]
- [[Redis-Python客户端与缓存策略]]

**🏷️ 相关标签**

#Python #Celery #Redis #RabbitMQ #分布式 #异步任务 #消息队列 #定时任务 #Flower #任务队列

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]
