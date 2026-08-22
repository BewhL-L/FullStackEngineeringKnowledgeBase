---
title: Python 中间件与异步任务知识点系统梳理
tags: [Python全栈, Python, 中间件, Celery, 消息队列, 异步任务, 面试]
created: 2026-08-13
updated: 2026-08-13
---

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


# Python 中间件与异步任务知识点系统梳理（优化版）

> **文档说明**：系统梳理 Python 生态的中间件与异步任务处理，涵盖 Celery、消息队列、定时任务、事件驱动架构等。

---

## 1. 概述

Python Web 应用中，耗时操作（发送邮件、生成报表、调用第三方 API）不应阻塞请求响应，需要异步任务队列。Celery 是 Python 生态最成熟的分布式任务队列，配合 Redis/RabbitMQ 作为 Broker 实现异步处理。

**核心概念**：
- **Broker（中间人）**：消息队列，存储任务（Redis/RabbitMQ）
- **Worker（工人）**：执行任务的进程
- **Backend（结果存储）**：存储任务结果（Redis/数据库）
- **Task（任务）**：被异步执行的函数

---


---
## 2. Celery

### 2.1 基本配置

> 🔍 **知识点深度解析**
>
> **作用**：Celery 的基本配置是连接 Broker 与 Result Backend、定义序列化与并发参数的起点。
>
> **原理**：Celery 通过 Celery(app) 或独立实例创建应用，配置以 broker_url、result_backend 指定消息代理与结果存储；配置可写在代码、配置文件或 Django settings 中。
>
> **用法要点**：① broker_url 指定消息中间件（Redis/RabbitMQ） ② result_backend 指定结果存储 ③ task_serializer 控制序列化格式 ④ 配置可集中管理便于环境切换 ⑤ Django 项目常用 celery.py + settings 集成


```python
# celery_app.py
from celery import Celery

app = Celery(
    "myapp",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=["tasks"]
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_acks_late=True,       # 任务执行完再确认（防丢失）
    worker_prefetch_multiplier=1,  # 每次只预取1个任务
)
```

### 2.2 定义与调用任务

> 🔍 **知识点深度解析**
>
> **作用**：任务是 Celery 的调度单元，掌握定义与异步调用是使用该框架的基础。
>
> **原理**：用 @app.task 装饰函数即定义为任务；.delay()/.apply_async() 将任务推入 Broker 异步执行，调用方立即返回 AsyncResult 而非等待结果。
>
> **用法要点**：① @app.task 装饰器定义任务 ② delay()/apply_async() 异步触发 ③ 调用方立即返回不阻塞 ④ AsyncResult 可查询任务状态与结果 ⑤ 耗时操作应剥离为异步任务


```python
# tasks.py
from celery_app import app
from celery import shared_task

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email(self, to, subject, body):
    try:
        # 发送邮件逻辑
        return f"Email sent to {to}"
    except Exception as e:
        raise self.retry(exc=e)

@shared_task
def generate_report(user_id):
    # 生成报表
    return report_path

# 调用（异步）
result = send_email.delay("user@example.com", "Hello", "Body")
print(result.id)  # 任务ID

# 延迟执行
send_email.apply_async(args=[...], countdown=60)  # 60秒后执行
send_email.apply_async(args=[...], eta=datetime(2026,1,1,10,0,0))  # 指定时间

# 获取结果
result = send_email.AsyncResult(task_id)
result.ready()    # 是否完成
result.result     # 结果
result.state      # PENDING/STARTED/SUCCESS/FAILURE
```

### 2.3 定时任务（Celery Beat）

> 🔍 **知识点深度解析**
>
> **作用**：Celery Beat 提供类 cron 的周期性任务调度，适合报表、清理、同步等定时作业。
>
> **原理**：Beat 是独立调度进程，按 schedule 配置周期性将任务发往 Broker；支持 interval（间隔）与 crontab（类 cron 表达式）两种触发方式。
>
> **用法要点**：① Beat 是独立调度进程 ② interval 表示固定间隔 ③ crontab 支持类 cron 表达式 ④ 调度配置与任务定义分离 ⑤ 需同时运行 beat 与 worker


```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    "daily-report": {
        "task": "tasks.generate_daily_report",
        "schedule": crontab(hour=8, minute=0),  # 每天8点
    },
    "every-5-min": {
        "task": "tasks.sync_data",
        "schedule": 300.0,  # 每300秒
    },
}
```

### 2.4 Worker 启动

```bash

> 🔍 **知识点深度解析**
>
> **作用**：Celery Worker 是执行任务的进程，启动参数控制并发数、队列、日志和自动重载。
>
> **原理**：celery -A proj worker --loglevel=info 启动 Worker。-c/--concurrency 并发数（默认 CPU 核数，prefork 模式）；-Q 指定监听的队列；--autoscale=max,min 自动伸缩；-n 设置节点名；--logfile 指定日志文件。生产环境用 systemd/supervisor 管理 Worker 进程，多队列时启动多个 Worker 分别消费不同队列实现任务隔离。
>
> **用法要点**：① celery -A proj worker -l info 启动，-A 指定 Celery 实例  ② -c 4 设置 prefork 并发数，-P gevent 用协程池  ③ -Q queue1,queue2 指定监听队列  ④ --autoscale=10,3 自动伸缩 3-10 进程  ⑤ 面试常考：Worker 启动参数、并发模式、多队列隔离

# 启动 worker
celery -A celery_app worker --loglevel=info -c 4  # 4个进程

# 启动定时任务调度器
celery -A celery_app beat --loglevel=info

# 生产环境用 supervisor/systemd 管理
```

> 🔍 **知识点深度解析**
>
> **作用**：Celery 是 Python 异步任务的标准方案，理解其架构和可靠性配置很重要。
>
> **原理**：Celery 采用生产者-消费者模式：应用调用 `task.delay()` 将任务消息发送到 Broker（Redis/RabbitMQ），Worker 进程从 Broker 消费任务并执行，结果写入 Backend。`task_acks_late=True` 让 Worker 在任务执行完后才确认消息，Worker 崩溃时任务会重新入队（防丢失）。`worker_prefetch_multiplier=1` 防止长任务阻塞短任务（公平调度）。任务重试用 `self.retry()`，设置 `max_retries` 避免无限重试。Celery Beat 是定时任务调度器，将定时任务作为消息发送到 Broker。
>
> **用法要点**：① 任务参数要可 JSON 序列化（不要传 ORM 对象，传 ID）；② 长任务设置超时 `soft_time_limit`/`time_limit`；③ 生产用 RabbitMQ（更可靠），Redis 适合简单场景；④ 面试常考：Celery 架构、任务可靠性、ack 机制、定时任务、与消息队列关系。

---

## 2.5 Celery 高级原语（任务编排）

```python
from celery import chain, group, chord, chunk


> 🔍 **知识点深度解析**
>
> **作用**：Celery 原语（chain/group/chord/chain）实现任务编排，支持串行、并行、分组和回调。
>
> **原理**：chain：任务串行执行，前一个结果作为后一个参数（chain(task1.s(), task2.s())()）。group：任务并行执行，返回 GroupResult（group(task.s(i) for i in range(10))()）。chord：group 执行完后执行回调（chord(header)(callback)），类似 MapReduce。chunks：大批量任务分块。这些原语可组合成复杂工作流，结果通过 ResultBackend 持久化。
>
> **用法要点**：① chain 串行：A→B→C，前一个返回值传给后一个  ② group 并行：多个任务同时执行，收集所有结果  ③ chord = group + callback，并行完成后执行汇总  ④ 原语可嵌套组合成复杂 DAG 工作流  ⑤ 面试常考：chain/group/chord 区别、工作流编排、结果获取

# chain：顺序执行，前一个结果传给后一个
result = chain(add.s(1, 2), multiply.s(10), subtract.s(5))()
# 等价于 subtract(multiply(add(1,2), 10), 5)

# group：并行执行，返回结果列表
result = group([add.s(i, i) for i in range(10)])()
result.get()  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# chord：group 并行执行完后，执行回调
header = group([process.s(item) for item in items])
callback = summarize.s()
result = chord(header)(callback)  # 所有process完成后调用summarize

# chunk：将大数据分批处理
result = add.chunks(zip(range(100), range(100)), 10)()
```

### 2.6 任务优先级与路由

```python

> 🔍 **知识点深度解析**
>
> **作用**：Celery 任务路由将不同任务分发到不同队列，配合 Worker 实现优先级和资源隔离。
>
> **原理**：task_routes 配置任务到队列的映射（如 task.add → queue:high-priority）。任务优先级：RabbitMQ/Redis 支持队列优先级（x-max-priority），apply_async(priority=0-9) 设置任务优先级。多队列架构：high/default/low 三级队列，分别启动 Worker，high 队列分配更多并发。定时任务和实时任务分到不同队列避免互相影响。
>
> **用法要点**：① task_routes 将任务路由到指定队列  ② RabbitMQ 支持 priority，Redis 优先级支持有限  ③ 多队列+多 Worker 实现资源隔离和优先级  ④ apply_async(queue='high', priority=9) 指定队列和优先级  ⑤ 面试常考：任务路由配置、优先级实现、多队列架构

# 任务优先级（RabbitMQ 支持）
@app.task(queue="high_priority")
def urgent_task():
    pass

# 任务路由：不同任务到不同队列
app.conf.task_routes = {
    "tasks.send_email": {"queue": "email"},
    "tasks.process_image": {"queue": "image"},
}

# 启动指定队列的 worker
celery -A app worker -Q email -c 2
celery -A app worker -Q image -c 4
```

> 🔍 **知识点深度解析**
>
> **作用**：Celery 原语实现复杂任务工作流，是构建异步处理管道的核心。
>
> **原理**：`chain` 通过回调链接实现顺序执行，每个任务的返回值作为下一个任务的第一个参数。`group` 将多个任务并行提交到 Broker，用 ResultSet 收集结果。`chord` 是 group + 回调，所有 header 任务完成后触发 callback（Redis 作为 Broker 时需要额外配置，RabbitMQ 原生支持）。任务路由通过 `task_routes` 将不同任务发送到不同队列，配合不同 Worker 实现资源隔离和优先级。优先级队列需要 Broker 支持（RabbitMQ 优先级队列，Redis 用多个队列模拟）。
>
> **用法要点**：① chain 中任务参数要兼容（前一个返回值是后一个输入）；② chord 在 Redis Broker 下注意结果后端配置；③ 大任务拆分用 group 并行，注意下游限流；④ 面试常考：chain/group/chord 区别、任务路由、优先级队列、工作流设计。

---


---
## 3. 消息队列

### 3.1 Redis 作为 Broker

> 🔍 **知识点深度解析**
>
> **作用**：Redis 是最常用的轻量级 Broker，部署简单、性能高，适合多数中小规模场景。
>
> **原理**：任务以列表/流结构存入 Redis，Worker 用 BRPOP 等方式阻塞取任务；Redis 内存存储，重启可能丢失未消费任务（可开启 AOF/RDB 持久化缓解）。
>
> **用法要点**：① 部署简单、性能优秀 ② 基于内存，需注意持久化 ③ 支持阻塞弹出高效消费 ④ 不适合超大规模消息堆积 ⑤ 常配合 Redis 同时做缓存与 Broker


- 简单易用，适合中小规模
- 支持优先级队列
- 不支持消息持久化确认（相对 RabbitMQ 可靠性低）

### 3.2 RabbitMQ 作为 Broker

> 🔍 **知识点深度解析**
>
> **作用**：RabbitMQ 是功能完备的消息中间件，适合对可靠性、路由和吞吐要求高的场景。
>
> **原理**：基于 AMQP 协议，支持交换机（Exchange）灵活路由、消息确认（ack）、持久化与优先级队列；相比 Redis 更擅长复杂的消息可靠投递。
>
> **用法要点**：① 基于 AMQP，路由能力强 ② 支持消息确认与持久化 ③ 支持优先级队列 ④ 可靠性高于 Redis ⑤ 运维复杂度也更高


- 专业消息队列，支持 AMQP 协议
- 消息持久化、确认机制、死信队列
- 支持复杂路由（Exchange/Binding/Queue）
- 适合大规模、高可靠场景

### 3.3 Kafka

> 🔍 **知识点深度解析**
>
> **作用**：Kafka 是高吞吐分布式日志系统，适合海量事件流与削峰填谷。
>
> **原理**：以分区（partition）日志方式存储消息，支持多消费者组、持久化与水平扩展；Celery 对 Kafka 支持有限，通常直接用 kafka-python 消费。
>
> **用法要点**：① 高吞吐、可水平扩展 ② 分区日志持久化 ③ 适合事件流与大数据管道 ④ Celery 原生支持弱 ⑤ 常用于日志/埋点/流处理


- 高吞吐量分布式消息系统
- 适合日志收集、事件流、大数据场景
- Python 客户端：`confluent-kafka`、`kafka-python`

```python
# Kafka 生产者
from confluent_kafka import Producer
p = Producer({"bootstrap.servers": "localhost:9092"})
p.produce("topic", key="key", value="message")
p.flush()

# Kafka 消费者
from confluent_kafka import Consumer
c = Consumer({"bootstrap.servers": "localhost:9092", "group.id": "mygroup", "auto.offset.reset": "earliest"})
c.subscribe(["topic"])
while True:
    msg = c.poll(1.0)
    if msg:
        print(msg.value())
```

---


---
## 4. 其他异步任务方案

### 4.1 Django Q / django-celery

> 🔍 **知识点深度解析**
>
> **作用**：Django Q 是轻量异步任务方案，原生集成 Django 且无需独立 Broker 即可用。
>
> **原理**：基于 Django ORM 作 Broker，配套 Django Admin 管理任务与调度；相比 Celery 更轻，适合已用 Django、任务量不大的项目。
>
> **用法要点**：① 轻量、与 Django 深度集成 ② 可用 ORM 作 Broker ③ 自带 Admin 任务管理 ④ 适合中小项目 ⑤ 生态与扩展性弱于 Celery


- Django 生态的任务队列
- Django Q 更轻量，支持 ORM/Redis 作为 Broker

### 4.2 RQ（Redis Queue）

> 🔍 **知识点深度解析**
>
> **作用**：RQ 是基于 Redis 的极简任务队列，API 直观、学习成本低。
>
> **原理**：用 Queue 将函数入队，独立 worker 进程消费；仅依赖 Redis，无复杂配置，适合简单后台任务。
>
> **用法要点**：① 仅依赖 Redis，极简 ② API 直观易上手 ③ 适合简单后台任务 ④ 功能比 Celery 少 ⑤ 无内置复杂定时调度


- 比 Celery 更简单，只支持 Redis
- API 简洁，适合小型项目

```python
from redis import Redis
from rq import Queue

q = Queue(connection=Redis())
job = q.enqueue(send_email, "user@example.com")
```

### 4.3 Dramatiq

> 🔍 **知识点深度解析**
>
> **作用**：Dramatiq 是现代化的可靠任务处理库，强调简洁 API 与中间件机制。
>
> **原理**：任务用 @dramatiq.actor 声明，配套 broker（RabbitMQ/Redis）与 worker；通过中间件实现重试、限流、监控，支持任务结果存储。
>
> **用法要点**：① API 简洁、中间件化 ② 支持 RabbitMQ/Redis ③ 内置重试与限流 ④ 比 Celery 年轻、生态较小 ⑤ 适合追求简洁的异步任务


- 现代任务队列，支持 Redis/RabbitMQ
- 比 Celery 更简单，类型提示友好

### 4.4 asyncio 原生异步

> 🔍 **知识点深度解析**
>
> **作用**：asyncio 是 Python 原生并发模型，适合 IO 密集型协程任务而无需外部 Broker。
>
> **原理**：基于事件循环与协程（async/await），单线程内通过挂起/恢复实现高并发；适合爬虫、并发请求等场景，但不适合 CPU 密集任务。
>
> **用法要点**：① 基于事件循环与协程 ② 适合 IO 密集型并发 ③ 单线程避免线程开销 ④ 不适合 CPU 密集 ⑤ 可与任务队列互补


```python
import asyncio
async def handle_request():
    # 不阻塞的异步任务
    task = asyncio.create_task(send_email_async())
    return "Processing"  # 立即响应
```

---

## 4.5 APScheduler（独立定时任务）

APScheduler 是轻量级定时任务库，不需要 Broker，适合单机定时任务。

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()


> 🔍 **知识点深度解析**
>
> **作用**：APScheduler 是 Python 独立定时任务库，支持 cron/间隔/日期触发器，可嵌入应用或独立运行。
>
> **原理**：四大组件：Scheduler（调度器：BackgroundScheduler/BlockingScheduler）、Trigger（触发器：CronTrigger/IntervalTrigger/DateTrigger）、JobStore（任务存储：内存/SQLAlchemy/MongoDB）、Executor（执行器：线程池/进程池）。@scheduler.scheduled_job('cron', hour=2) 添加任务。支持任务持久化（重启不丢失）、错过任务补偿（misfire_grace_time）和最大并发实例控制。
>
> **用法要点**：① BackgroundScheduler 后台运行，BlockingScheduler 阻塞主线程  ② CronTrigger 类似 Linux cron，IntervalTrigger 固定间隔  ③ JobStore 持久化到数据库，重启后任务不丢失  ④ misfire_grace_time 处理错过的任务，coalesce 合并错过的执行  ⑤ 面试常考：APScheduler 组件、触发器类型、与 Celery Beat 区别

# 间隔执行
scheduler.add_job(
    sync_data,
    trigger=IntervalTrigger(minutes=30),
    id="sync_data"
)

# Cron 表达式
scheduler.add_job(
    daily_report,
    trigger=CronTrigger(hour=8, minute=0, day_of_week="mon-fri"),
    id="daily_report"
)

# 一次性执行
scheduler.add_job(cleanup, "date", run_date="2026-12-31 23:59:59")

scheduler.start()
```

**定时任务方案对比**：

| 方案 | 特点 | 适用场景 |
|------|------|----------|
| **Celery Beat** | 分布式，需 Broker，配合 Celery | Celery 项目、分布式定时 |
| **APScheduler** | 轻量，单机，支持多种触发器 | 单机定时、简单场景 |
| **crontab** | 系统级，独立进程 | 系统脚本、简单命令 |
| **systemd timer** | 现代 Linux 定时 | 系统服务定时 |
| **Kubernetes CronJob** | 容器化定时 | K8s 集群、容器化任务 |

---

## 4.6 asyncio 事件循环原理

```
┌─────────────────────────────────────┐
│           Event Loop                │
│  ┌─────────┐    ┌───────────────┐   │
│  │  任务队列 │ ←→ │  就绪协程调度  │   │
│  └─────────┘    └───────┬───────┘   │
│                         │           │
│  ┌──────────────────────▼────────┐  │
│  │      IO 多路复用（select）     │  │
│  │   socket 可读/可写/超时事件     │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

- 事件循环是单线程的，通过 IO 多路复用实现并发
- `await` 挂起当前协程，交出控制权，事件循环调度其他就绪协程
- IO 完成后，事件循环唤醒等待的协程继续执行
- 不要在协程中调用阻塞 IO（会阻塞整个事件循环）

---


> 🔍 **知识点深度解析**
>
> **作用**：asyncio 事件循环是单线程协作式并发核心，通过 IO 多路复用和回调调度实现高并发。
>
> **原理**：事件循环（Event Loop）不断从就绪队列取出任务执行，遇到 await（协程挂起点）时将控制权交还循环，去执行其他就绪任务。底层用 selector（epoll/kqueue/IOCP）监听 IO 事件，IO 就绪后唤醒对应协程。协程在单线程内切换，无锁但不能有阻塞调用（time.sleep 会阻塞整个循环）。async/await 是语法糖，协程对象由事件循环驱动。
>
> **用法要点**：① 单线程+IO多路复用（epoll），协作式调度  ② await 是挂起点，遇到 await 交还控制权给事件循环  ③ 阻塞调用（requests/time.sleep）会卡住整个循环，用 aiohttp/asyncio.sleep  ④ asyncio.gather 并发执行多个协程  ⑤ 面试常考：事件循环原理、协程 vs 线程、await 机制、selector


---
## 5. 事件驱动架构

### 5.1 发布订阅模式

> 🔍 **知识点深度解析**
>
> **作用**：发布订阅解耦消息生产者与消费者，支持一对多广播与动态扩展订阅者。
>
> **原理**：发布者将消息发到主题（topic/channel），所有订阅者各自收到副本；Redis 的 pub/sub、Kafka 的消费者组都是典型实现。
>
> **用法要点**：① 生产者与消费者解耦 ② 支持一对多广播 ③ 订阅者可动态增减 ④ 消息通常不持久（视实现） ⑤ 适合事件通知/实时推送


```python
# Redis Pub/Sub
import redis
r = redis.Redis()

# 发布者
r.publish("notifications", json.dumps({"type": "order_created", "id": 123}))

# 订阅者
pubsub = r.pubsub()
pubsub.subscribe("notifications")
for message in pubsub.listen():
    if message["type"] == "message":
        handle_event(json.loads(message["data"]))
```

### 5.2 Webhook

> 🔍 **知识点深度解析**
>
> **作用**：Webhook 是反向 API，由事件触发主动向预设 URL 推送通知，实现系统间实时集成。
>
> **原理**：当源系统发生事件时主动 POST 数据到目标 URL；相比轮询更实时、省资源，但需目标方提供可公网访问的稳定接口并处理重试与签名校验。
>
> **用法要点**：① 事件驱动，主动回调 ② 比轮询更实时省资源 ③ 需接收方提供稳定 URL ④ 需校验签名防伪造 ⑤ 要做好重试与幂等


- 第三方服务通过 HTTP 回调通知
- 需要签名验证防伪造

---


---
## 6. 任务队列最佳实践

1. **任务幂等**：同一任务执行多次结果相同（用唯一 ID 去重）
2. **任务粒度**：不要太大（超时风险），也不要太小（开销大）
3. **错误处理**：重试 + 死信队列 + 告警
4. **监控**：任务执行时间、成功率、队列长度
5. **限流**：控制任务并发数，避免压垮下游
6. **序列化**：用 JSON，不要用 pickle（安全风险）

---


---
## 7. 面试高频考点

1. **Celery 架构**：Broker/Worker/Backend 角色
2. **任务可靠性**：acks_late、重试机制、消息确认
3. **Celery Beat**：定时任务实现
4. **Redis vs RabbitMQ**：作为 Broker 的区别
5. **异步任务 vs 协程**：适用场景
6. **任务幂等性**：如何保证
7. **死信队列**：处理失败任务
8. **消息队列选型**：Redis/RabbitMQ/Kafka
9. **任务监控**：Flower、Prometheus
10. **分布式任务**：多 Worker 并发、任务路由
11. **Celery 原语**：chain/group/chord 任务编排
12. **任务优先级**：队列路由、优先级队列
13. **定时任务对比**：Celery Beat/APScheduler/crontab/K8s CronJob
14. **事件循环**：asyncio 原理、IO 多路复用、阻塞问题
15. **任务队列设计模式**：生产者-消费者、竞争消费者

---


---
## 📝 精简总结

- Celery 是 Python 分布式任务队列标准，Broker(消息) + Worker(执行) + Backend(结果)
- 可靠性配置：acks_late（执行完确认）、重试、超时限制
- 定时任务用 Celery Beat，支持 crontab 表达式
- Celery 原语：chain（顺序）、group（并行）、chord（并行+回调）
- 任务路由：不同任务到不同队列，实现优先级和资源隔离
- Broker 选型：Redis（简单）、RabbitMQ（可靠/优先级/死信）、Kafka（高吞吐）
- 轻量方案：RQ（仅Redis）、Dramatiq（现代）、asyncio（原生异步）
- APScheduler：轻量单机定时任务，支持 Interval/Cron/Date 触发器
- 定时任务对比：Celery Beat（分布式）、APScheduler（单机）、crontab（系统）、K8s CronJob（容器）
- asyncio 事件循环：单线程 + IO 多路复用，await 挂起协程，禁止阻塞 IO
- 最佳实践：任务幂等、参数可序列化、错误重试+死信、监控告警
- 事件驱动：Redis Pub/Sub、Webhook、Kafka 事件流

---

[[08-Python全栈/MOC-Python全栈|← 返回 Python 全栈 MOC]] | [[Home|🏠 返回首页]]
