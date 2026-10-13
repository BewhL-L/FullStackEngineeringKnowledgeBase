---
title: Python 异步编程 asyncio
category: 异步与任务
tags: [Python, asyncio, 协程, 事件循环, async, await, 并发编程, aiohttp, asyncpg]
priority: P0
status: completed
created: 2026-09-10
updated: 2026-09-10
version: 2.0
author: BewhY_L
pre: ["[[Python-语法基础与数据结构]]", "[[Python-装饰器与上下文管理器]]", "[[Python-类型注解与mypy]]"]
description: 深度掌握Python asyncio异步编程全体系：事件循环、协程、Task/Future、gather/wait/as_completed、异步IO、同步原语、线程/进程混合、aiohttp/asyncpg、TaskGroup结构化并发与全部坑点
---

# Python 异步编程 asyncio

> **文档定位**：本文是 Python asyncio 异步编程的 P0 级深度教材。从"同步为什么慢"出发，系统讲解协程、事件循环、Task/Future、并发原语、异步 IO、与线程/进程混合、生产架构、调试与性能优化，覆盖 Python 3.7~3.13 全部关键特性。
>
> **适用人群**：使用 FastAPI/aiohttp/异步数据库的后端开发者；想从同步编程转型异步的工程师；准备高并发面试的 Python 程序员。
>
> **前置知识**：[[Python-语法基础与数据结构]] · [[Python-装饰器与上下文管理器]] · [[Python-类型注解与mypy]]

---

## 一、概述与学习路径

### 1.1 为什么需要异步

互联网后端服务 80% 以上时间在等待 IO：数据库查询、HTTP 调用、磁盘读写、消息队列。同步阻塞模式下，每个连接占一个线程，线程切换开销大、内存占用高，千级并发就到极限。异步编程用单线程协程 + 事件循环，在等待 IO 时切换到其他任务，CPU 不浪费在等待上，单线程可支撑万级并发。

```mermaid
graph LR
    subgraph 同步阻塞
        A1[请求1] --> B1[等待IO]
        B1 --> C1[处理]
        A2[请求2] -.->|排队| B1
    end
    subgraph 异步非阻塞
        A3[请求1] --> C3[挂起]
        A4[请求2] --> C4[挂起]
        C3 --> D3[请求1就绪恢复]
        C4 --> D4[请求2就绪恢复]
    end
    style B1 fill:#ff6b6b,color:#fff
    style C3 fill:#43e97b,color:#333
    style C4 fill:#43e97b,color:#333
```

### 1.2 核心概念对比

| 概念 | 说明 | Python 实现 |
|---|---|---|
| 并发 Concurrency | 任务交替执行，宏观同时 | 协程 asyncio |
| 并行 Parallelism | 任务真正同时执行 | 多进程 multiprocessing |
| 阻塞 Blocking | 调用后等待 | time.sleep, requests.get |
| 非阻塞 Non-blocking | 调用后立即返回 | asyncio.sleep, await |
| 同步 Synchronous | 按顺序执行 | 普通函数调用 |
| 异步 Asynchronous | 不等待继续做别的 | async/await |

### 1.3 协程 vs 线程 vs 进程

| 维度 | 协程 asyncio | 线程 threading | 进程 multiprocessing |
|---|---|---|---|
| 调度 | 用户态协作式 | 内核态抢占式 | 内核态抢占式 |
| 切换开销 | 纳秒级 | 微秒级 | 毫秒级 |
| 内存 | KB级 | MB级 | GB级 |
| 并发量 | 万级+ | 千级 | 百级 |
| CPU利用 | 单线程 | GIL限制 | 多核 |
| 数据共享 | 同线程无需锁 | 共享内存需锁 | 独立内存需IPC |

### 1.4 适用与不适用场景

| 适合异步 | 不适合异步 |
|---|---|
| 网络爬虫（大量HTTP） | CPU密集计算（加密/压缩） |
| Web服务器（高并发） | 纯数值计算 |
| API网关（聚合后端） | 必须严格顺序 |
| 数据库操作 | 阻塞库无法改造 |
| 消息队列消费 | 简单一次性脚本 |
| WebSocket/SSE | 对延迟不敏感的批处理 |

### 1.5 学习路线

1. **第一阶段**：async/await 语法 → 第一个协程 → asyncio.run。
2. **第二阶段**：事件循环原理 → Task → gather/wait。
3. **第三阶段**：异步IO（TCP/HTTP/文件/数据库）。
4. **第四阶段**：同步原语（Lock/Semaphore/Queue/Event）。
5. **第五阶段**：与线程/进程混合 → 生产架构。
6. **第六阶段**：TaskGroup 结构化并发 → 调试与性能优化。

---

### 💡 本章深度讲解

异步编程解决的核心问题是"IO 密集型场景下 CPU 等待浪费"。模型本质是单线程 + IO 多路复用（epoll/kqueue）+ 协作式调度。代价是所有 IO 必须用异步版本库，不能调用阻塞函数。选择异步的关键判断：程序 80% 以上时间在等待 IO 才值得用。

### 📝 本章精简总结

- 异步 = 单线程协程 + 事件循环 + IO多路复用。
- 适合 IO 密集，不适合 CPU 密集。
- 协程切换纳秒级，万级并发。

### 🎯 梯度练习题

**基础题（⭐）**
1. 并发和并行的区别？
2. 协程和线程的切换开销差异？
3. 什么场景适合异步？

**进阶题（⭐⭐）**
1. 为什么异步不能利用多核？
2. 为什么协程不需要锁？

**实战题（⭐⭐⭐）**
- 写一个脚本：用同步 requests 顺序请求 10 个 URL，再用 aiohttp 并发请求，对比耗时。

---

## 二、协程基础：async/await

### 2.1 async def 定义协程

```python
# 示例 2.1.1：最简协程
async def hello():
    print("Hello")

# 调用协程函数返回协程对象，不执行
coro = hello()
print(type(coro))  # <class 'coroutine'>
# 必须 await 或用 asyncio.run 运行

import asyncio
asyncio.run(hello())
# 预期输出：Hello
```

```python
# 示例 2.1.2：协程返回值
async def add(a, b):
    return a + b

async def main():
    result = await add(1, 2)
    print(result)  # 3

asyncio.run(main())
```

```python
# 示例 2.1.3：协程内部 await
async def greet(name):
    await asyncio.sleep(0.1)
    return f"Hello, {name}"

async def main():
    msg = await greet("World")
    print(msg)

asyncio.run(main())
```

### 2.2 await 表达式规则

await 只能等待可等待对象（awaitable）：协程、Task、Future、实现了 `__await__` 的对象。

```python
# 示例 2.2.1：可等待对象
async def foo():
    return 42

async def main():
    # 协程对象
    r1 = await foo()
    # Task
    task = asyncio.create_task(foo())
    r2 = await task
    # Future
    future = asyncio.Future()
    future.set_result(99)
    r3 = await future
    print(r1, r2, r3)  # 42 42 99

asyncio.run(main())
```

```python
# 示例 2.2.2：错误用法
# await 42  # TypeError: object int can't be used in await
# await "hello"  # TypeError
# def sync_func(): await foo()  # SyntaxError
```

```python
# 示例 2.2.3：协程未 await 警告
async def buggy():
    print("我不会执行")

async def main():
    buggy()  # RuntimeWarning: coroutine was never awaited

asyncio.run(main())
```

### 2.3 asyncio.run 入口

```python
# 示例 2.3.1：asyncio.run 创建事件循环
import asyncio

async def main():
    print("在事件循环中")

asyncio.run(main())
# asyncio.run 自动：创建loop → 运行main → 关闭loop
```

```python
# 示例 2.3.2：asyncio.run 不能嵌套
async def outer():
    async def inner():
        pass
    # asyncio.run(inner())  # RuntimeError: 在已运行的loop中不能再run
    await inner()  # 正确

asyncio.run(outer())
```

### 2.4 顺序执行 vs 并发执行

```python
# 示例 2.4.1：顺序执行（await 会等待）
async def say(name, delay):
    print(f"开始 {name}")
    await asyncio.sleep(delay)
    print(f"完成 {name}")

async def main():
    await say("A", 2)  # 等2秒
    await say("B", 1)  # 再等1秒
    # 总耗时3秒

asyncio.run(main())
```

```python
# 示例 2.4.2：并发执行（create_task）
async def main():
    t1 = asyncio.create_task(say("A", 2))
    t2 = asyncio.create_task(say("B", 1))
    await t1
    await t2
    # 总耗时2秒（并发）
```

```python
# 示例 2.4.3：gather 并发
async def main():
    results = await asyncio.gather(
        say("A", 2),
        say("B", 1),
        say("C", 1.5),
    )
    # 总耗时2秒（最长的那个）
```

---

### 💡 本章深度讲解

协程的本质是"可挂起可恢复的函数"。`async def` 定义协程函数，调用后返回协程对象不执行。`await` 挂起当前协程，把控制权还给事件循环，等待的操作完成后从挂起点恢复。`asyncio.run` 是标准入口，创建/运行/关闭事件循环。直接 await 协程是顺序执行，create_task/gather 才是并发。

### 📝 本章精简总结

- `async def` 定义协程，调用返回协程对象。
- `await` 挂起等待，只能在 async 函数内。
- `asyncio.run(main())` 入口。
- create_task/gather 实现并发。

### 🎯 梯度练习题

**基础题（⭐）**
1. `async def f()` 调用后做了什么？
2. await 后面能跟什么？
3. asyncio.run 的作用？

**进阶题（⭐⭐）**
1. 为什么直接 await 协程是顺序执行？
2. 如何让两个协程并发？

**实战题（⭐⭐⭐）**
- 写一个协程：并发请求 3 个模拟 IO 操作（用 asyncio.sleep 模拟），总耗时应等于最长的那个。

---

## 三、事件循环原理

### 3.1 事件循环是什么

事件循环是 asyncio 的核心引擎，一个无限循环：检查就绪任务 → 执行 → 等待 IO → 重复。

```mermaid
graph TB
    A[事件循环启动] --> B[检查就绪Task/Future]
    B --> C{有就绪?}
    C -->|是| D[执行Task直到await]
    D --> E[Task挂起注册回调]
    E --> B
    C -->|否| F[epoll等待IO事件]
    F --> G[IO就绪/定时器触发]
    G --> B
    B --> H{所有任务完成?}
    H -->|否| B
    H -->|是| I[循环结束]
```

### 3.2 获取事件循环

```python
# 示例 3.2.1：获取当前运行的事件循环
async def main():
    loop = asyncio.get_running_loop()  # 协程内推荐
    print(loop)

asyncio.run(main())
```

```python
# 示例 3.2.2：旧版 API（不推荐）
# loop = asyncio.get_event_loop()  # Python 3.10+ 已废弃
```

### 3.3 调度回调

```python
# 示例 3.3.1：call_soon 立即调度
async def main():
    loop = asyncio.get_running_loop()
    def cb(arg):
        print(f"回调: {arg}")
    loop.call_soon(cb, "马上")
    print("先打印我")
    await asyncio.sleep(0.1)

asyncio.run(main())
# 输出：先打印我 / 回调: 马上
```

```python
# 示例 3.3.2：call_later 延迟调度
async def main():
    loop = asyncio.get_running_loop()
    def cb():
        print("2秒后")
    loop.call_later(2, cb)
    await asyncio.sleep(3)
```

```python
# 示例 3.3.3：call_at 绝对时间调度
async def main():
    loop = asyncio.get_running_loop()
    now = loop.time()
    loop.call_at(now + 1, lambda: print("1秒后"))
    await asyncio.sleep(2)
```

### 3.4 IO 多路复用

```python
# 示例 3.4.1：Linux 上事件循环用 epoll
# import selectors
# selector = selectors.DefaultSelector()
# Linux: EpollSelector
# macOS: KqueueSelector
# Windows: SelectSelector 或 Proactor
```

### 3.5 uvloop 加速

```python
# 示例 3.5.1：使用 uvloop
# pip install uvloop
import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# uvloop 基于 libuv，比默认 loop 快 2-4 倍
# 仅 Linux/macOS 支持
```

---

### 💡 本章深度讲解

事件循环是 asyncio 的心脏。它通过 IO 多路复用（epoll/kqueue/IOCP）同时监听成千上万的连接，单线程调度所有协程。协程在 await 时挂起让出控制权，事件循环去执行其他就绪协程。这种模型是 Node.js/Nginx/Redis 高并发的共同基础。uvloop 用 libuv 重写了事件循环，性能提升 2-4 倍，生产环境推荐。

### 📝 本章精简总结

- 事件循环：无限循环 + IO多路复用 + 任务调度。
- get_running_loop 获取当前循环。
- call_soon/call_later/call_at 调度回调。
- uvloop 提升性能。

### 🎯 梯度练习题

**基础题（⭐）**
1. 事件循环的作用？
2. call_soon 和 call_later 的区别？
3. Linux 用什么 IO 多路复用？

**进阶题（⭐⭐）**
1. 事件循环为什么能单线程支撑万级并发？
2. uvloop 为什么快？

**实战题（⭐⭐⭐）**
- 用 call_later 实现一个每秒打印一次心跳、10 次后自动退出的程序。

---

## 四、Task 与 Future

### 4.1 Future：异步结果占位符

Future 代表一个尚未完成的异步操作结果，有 `set_result`/`result`/`done` 方法。

```python
# 示例 4.1.1：手动创建 Future
async def main():
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    # 模拟后台设置结果
    async def setter():
        await asyncio.sleep(1)
        future.set_result(42)
    asyncio.create_task(setter())
    # await future 会挂起，直到 set_result
    result = await future
    print(result)  # 42

asyncio.run(main())
```

```python
# 示例 4.1.2：Future 的状态
async def main():
    f = asyncio.Future()
    print(f.done())  # False
    f.set_result("ok")
    print(f.done())    # True
    print(f.result())  # ok

asyncio.run(main())
```

### 4.2 Task：协程的调度封装

Task 是 Future 的子类，把协程包装成可调度任务。

```python
# 示例 4.2.1：create_task 创建任务
async def work(name, delay):
    await asyncio.sleep(delay)
    return f"{name} 完成"

async def main():
    task = asyncio.create_task(work("A", 1))
    print("任务已创建，立即返回")
    result = await task
    print(result)

asyncio.run(main())
```

```python
# 示例 4.2.2：并发创建多个 Task
async def main():
    tasks = [
        asyncio.create_task(work(f"T{i}", i*0.5))
        for i in range(5)
    ]
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
```

### 4.3 Task 取消

```python
# 示例 4.3.1：取消任务
async def long_task():
    try:
        for i in range(10):
            print(f"执行 {i}")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("被取消")
        raise  # 必须重新抛出

async def main():
    task = asyncio.create_task(long_task())
    await asyncio.sleep(3)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("主程序捕获取消")

asyncio.run(main())
```

### 4.4 Task 引用保持

```python
# 示例 4.4.1：Task 被 GC 回收的坑
background_tasks = set()

def fire_and_forget(coro):
    task = asyncio.create_task(coro)
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

# ❌ 错误：不保存引用，任务可能被GC
# asyncio.create_task(bg_work())

# ✅ 正确：保存引用，完成后移除
```

---

### 💡 本章深度讲解

Future 是"未来结果"的占位符，Task 是"协程 + Future"的封装。create_task 把协程提交到事件循环后台执行，当前协程继续做别的事。取消任务时要捕获 CancelledError 做清理，然后重新抛出。后台任务必须保持引用，否则可能被垃圾回收。

### 📝 本章精简总结

- Future：异步结果占位符。
- Task：协程的并发封装。
- create_task 后台执行。
- cancel 取消任务，捕获 CancelledError 清理。
- 后台任务保持引用。

### 🎯 梯度练习题

**基础题（⭐）**
1. Future 和 Task 的关系？
2. create_task 做了什么？
3. 为什么后台任务要保持引用？

**进阶题（⭐⭐）**
1. 取消任务时为什么要重新抛出 CancelledError？
2. 如何实现 fire-and-forget？

**实战题（⭐⭐⭐）**
- 写一个任务：运行 10 秒，每 1 秒打印一次，3 秒后取消，验证清理逻辑。

---

## 五、asyncio 并发 API 大全

### 5.1 gather：并发组合

```python
# 示例 5.1.1：gather 基本用法
async def fetch(name, delay):
    await asyncio.sleep(delay)
    return f"{name} 数据"

async def main():
    results = await asyncio.gather(
        fetch("A", 2),
        fetch("B", 1),
        fetch("C", 1.5),
    )
    print(results)  # 按输入顺序返回
    # 总耗时2秒（最长的）

asyncio.run(main())
```

```python
# 示例 5.1.2：return_exceptions
async def may_fail(should_fail):
    if should_fail:
        raise ValueError("出错")
    return "成功"

async def main():
    results = await asyncio.gather(
        may_fail(False),
        may_fail(True),
        may_fail(False),
        return_exceptions=True,
    )
    print(results)  # ['成功', ValueError('出错'), '成功']

asyncio.run(main())
```

### 5.2 wait：灵活等待

```python
# 示例 5.2.1：FIRST_COMPLETED
async def main():
    tasks = [
        asyncio.create_task(fetch("A", 2)),
        asyncio.create_task(fetch("B", 1)),
        asyncio.create_task(fetch("C", 1.5)),
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    print("先完成:", [t.result() for t in done])
    print("等待中:", len(pending))
    for t in pending:
        t.cancel()

asyncio.run(main())
```

```python
# 示例 5.2.2：FIRST_EXCEPTION
async def main():
    tasks = [asyncio.create_task(fetch("A", 1))]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
```

### 5.3 as_completed：按完成顺序

```python
# 示例 5.3.1：按完成顺序获取结果
async def main():
    coros = [fetch("慢", 2), fetch("快", 0.5), fetch("中", 1)]
    for coro in asyncio.as_completed(coros):
        result = await coro
        print(result)
    # 输出顺序：快 → 中 → 慢

asyncio.run(main())
```

### 5.4 wait_for：超时

```python
# 示例 5.4.1：wait_for 超时
async def long_task():
    await asyncio.sleep(10)
    return "完成"

async def main():
    try:
        result = await asyncio.wait_for(long_task(), timeout=2)
    except asyncio.TimeoutError:
        print("超时")

asyncio.run(main())
```

```python
# 示例 5.4.2：wait_for 嵌套超时
async def main():
    try:
        await asyncio.wait_for(
            asyncio.wait_for(long_task(), timeout=5),
            timeout=2,
        )
    except asyncio.TimeoutError:
        print("外层超时")
```

### 5.5 shield：保护不被取消

```python
# 示例 5.5.1：shield 保护后台任务
async def important():
    await asyncio.sleep(5)
    return "重要结果"

async def main():
    task = asyncio.create_task(asyncio.shield(important()))
    await asyncio.sleep(1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("外部取消，但 important 仍在跑")

asyncio.run(main())
```

---

### 💡 本章深度讲解

四个并发 API 覆盖不同场景：gather 最简单（全部并发按序返回）、wait 最灵活（可设等待条件）、as_completed 按完成顺序流式处理、wait_for 超时控制、shield 保护任务不被取消。生产中最常用 gather + wait_for 组合。

### 📝 本章精简总结

- gather：并发+按序返回+return_exceptions。
- wait：FIRST_COMPLETED/ALL_COMPLETED/FIRST_EXCEPTION。
- as_completed：按完成顺序。
- wait_for：超时。
- shield：保护不被取消。

### 🎯 梯度练习题

**基础题（⭐）**
1. gather 和 wait 的区别？
2. as_completed 返回顺序？
3. wait_for 超时抛什么？

**进阶题（⭐⭐）**
1. return_exceptions=False 时 gather 遇到异常会怎样？
2. shield 真正保护了什么？

**实战题（⭐⭐⭐）**
- 并发请求 10 个 URL，任何一个 5 秒超时，先完成的先处理。

---

## 六、同步原语

### 6.1 Lock 异步锁

```python
# 示例 6.1.1：异步锁保护共享状态
counter = 0
lock = asyncio.Lock()

async def increment():
    global counter
    for _ in range(1000):
        async with lock:
            current = counter
            await asyncio.sleep(0)  # 让出控制权
            counter = current + 1

async def main():
    await asyncio.gather(increment(), increment(), increment())
    print(counter)  # 3000

asyncio.run(main())
```

### 6.2 Semaphore 信号量

```python
# 示例 6.2.1：限制并发数
sem = asyncio.Semaphore(5)

async def fetch(url):
    async with sem:
        print(f"请求 {url}")
        await asyncio.sleep(1)
        return f"{url} 完成"

async def main():
    urls = [f"url{i}" for i in range(20)]
    await asyncio.gather(*[fetch(u) for u in urls])
    # 最多同时5个

asyncio.run(main())
```

### 6.3 Event 事件

```python
# 示例 6.3.1：协程间事件通知
event = asyncio.Event()

async def waiter(name):
    print(f"{name} 等待")
    await event.wait()
    print(f"{name} 收到信号")

async def setter():
    await asyncio.sleep(2)
    event.set()

async def main():
    await asyncio.gather(
        waiter("A"), waiter("B"), setter()
    )

asyncio.run(main())
```

### 6.4 Queue 队列

```python
# 示例 6.4.1：生产者-消费者
queue = asyncio.Queue(maxsize=10)

async def producer(name):
    for i in range(5):
        await queue.put(i)
        print(f"{name} 生产 {i}")
        await asyncio.sleep(0.1)

async def consumer(name):
    while True:
        item = await queue.get()
        print(f"{name} 消费 {item}")
        queue.task_done()

async def main():
    producers = [asyncio.create_task(producer(f"P{i}")) for i in range(2)]
    consumers = [asyncio.create_task(consumer(f"C{i}")) for i in range(3)]
    await asyncio.gather(*producers)
    await queue.join()
    for c in consumers:
        c.cancel()

asyncio.run(main())
```

### 6.5 Condition 条件变量

```python
# 示例 6.5.1：条件变量
cond = asyncio.Condition()
ready = False

async def waiter():
    async with cond:
        while not ready:
            await cond.wait()
        print("收到通知")

async def setter():
    global ready
    await asyncio.sleep(1)
    async with cond:
        ready = True
        cond.notify_all()
```

---

### 💡 本章深度讲解

异步同步原语和线程版一一对应，但都是 await/async with 不阻塞事件循环。单线程协程大多数情况不需要锁，但在 await 点之间可能有其他协程修改共享状态时仍需要。Semaphore 是限流利器，Queue 是生产者消费者核心，Event 是协程间通知。

### 📝 本章精简总结

- Lock：保护临界区。
- Semaphore：限制并发数。
- Event：事件通知。
- Queue：生产者消费者。
- Condition：条件等待。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步 Lock 和 threading.Lock 的区别？
2. Semaphore 怎么限制并发？
3. Queue.task_done 的作用？

**进阶题（⭐⭐）**
1. 为什么单线程协程还需要锁？
2. Event 和 Condition 的区别？

**实战题（⭐⭐⭐）**
- 用 Semaphore 实现：20 个并发请求，最多同时 5 个访问 API。

---

## 七、异步 IO 操作

### 7.1 异步 TCP 客户端/服务器

```python
# 示例 7.1.1：异步 TCP 客户端
async def tcp_client(host, port, message):
    reader, writer = await asyncio.open_connection(host, port)
    writer.write(message.encode())
    await writer.drain()
    data = await reader.read(100)
    writer.close()
    await writer.wait_closed()
    return data.decode()
```

```python
# 示例 7.1.2：异步 TCP 服务器
async def handle(reader, writer):
    data = await reader.read(100)
    writer.write(b"echo: " + data)
    await writer.drain()
    writer.close()

async def run_server():
    server = await asyncio.start_server(handle, "127.0.0.1", 8888)
    async with server:
        await server.serve_forever()
```

### 7.2 异步子进程

```python
# 示例 7.2.1：执行外部命令
async def run_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode(), stderr.decode(), proc.returncode

async def main():
    out, err, code = await run_cmd("echo hello")
    print(out, code)

asyncio.run(main())
```

### 7.3 异步文件 IO

```python
# 示例 7.3.1：aiofiles
# pip install aiofiles
import aiofiles

async def read_file(path):
    async with aiofiles.open(path) as f:
        return await f.read()

async def write_file(path, content):
    async with aiofiles.open(path, "w") as f:
        await f.write(content)
```

```python
# 示例 7.3.2：用 to_thread 包装同步文件
async def read_file_sync(path):
    def _read():
        with open(path) as f:
            return f.read()
    return await asyncio.to_thread(_read)
```

### 7.4 异步上下文管理器/迭代器/生成器

```python
# 示例 7.4.1：异步上下文管理器
class AsyncResource:
    async def __aenter__(self):
        print("获取")
        return self
    async def __aexit__(self, *a):
        print("释放")

async def main():
    async with AsyncResource():
        print("使用")
```

```python
# 示例 7.4.2：异步迭代器
class AsyncCounter:
    def __init__(self, stop):
        self.stop = stop
        self.count = 0
    def __aiter__(self):
        return self
    async def __anext__(self):
        if self.count >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)
        self.count += 1
        return self.count

async def main():
    async for n in AsyncCounter(5):
        print(n)
```

```python
# 示例 7.4.3：异步生成器
async def async_gen(start, stop):
    for i in range(start, stop):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for n in async_gen(1, 6):
        print(n)
```

---

### 💡 本章深度讲解

异步 IO 覆盖 TCP、子进程、文件、自定义资源。标准库没有内置异步文件 IO（aiofiles 基于线程池），但 TCP/子进程是原生的。异步上下文管理器/迭代器/生成器让异步代码和同步代码结构一致。

### 📝 本章精简总结

- TCP：open_connection/start_server。
- 子进程：create_subprocess_shell。
- 文件：aiofiles 或 to_thread。
- async with/async for/yield。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步文件 IO 为什么用 aiofiles？
2. async for 用什么协议？

**进阶题（⭐⭐）**
1. 为什么标准库没有原生异步文件 IO？
2. 异步生成器和同步生成器的区别？

**实战题（⭐⭐⭐）**
- 用 aiofiles 并发读取 10 个文件并合并内容。

---

## 八、异步与线程/进程混合

### 8.1 asyncio.to_thread

```python
# 示例 8.1.1：在线程池运行阻塞函数
def blocking(seconds):
    time.sleep(seconds)
    return "完成"

async def main():
    result = await asyncio.to_thread(blocking, 2)
    print(result)
    # 并发多个
    results = await asyncio.gather(
        asyncio.to_thread(blocking, 2),
        asyncio.to_thread(blocking, 1),
    )

asyncio.run(main())
```

### 8.2 run_in_executor

```python
# 示例 8.2.1：自定义线程池
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

async def main():
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=10) as pool:
        result = await loop.run_in_executor(pool, blocking, 2)
```

```python
# 示例 8.2.2：进程池（CPU密集）
async def main():
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=4) as pool:
        result = await loop.run_in_executor(pool, cpu_task, 1000000)
```

### 8.3 从同步代码调用异步

```python
# 示例 8.3.1：同步函数中运行异步
def sync_main():
    result = asyncio.run(async_function())
    return result
```

### 8.4 阻塞调用对照表

| 阻塞调用 | 异步替代 |
|---|---|
| time.sleep | asyncio.sleep |
| requests.get | aiohttp/httpx.AsyncClient |
| open().read | aiofiles |
| sqlite3 | aiosqlite |
| psycopg2 | asyncpg |
| CPU 计算 | to_thread/ProcessPool |

---

### 💡 本章深度讲解

异步生态不是所有库都有异步版本。混合编程是现实：主流程异步，阻塞操作丢到线程池（IO 阻塞）或进程池（CPU 密集）。asyncio.to_thread 是 3.9+ 的便捷 API。

### 📝 本章精简总结

- to_thread：线程池运行阻塞函数。
- run_in_executor：自定义线程池/进程池。
- CPU 密集用进程池绕过 GIL。
- 阻塞调用对照表。

### 🎯 梯度练习题

**基础题（⭐）**
1. asyncio.to_thread 的作用？
2. CPU 密集为什么用进程池？

**进阶题（⭐⭐）**
1. 为什么不能在协程里直接调用 time.sleep？
2. to_thread 和 run_in_executor 的关系？

**实战题（⭐⭐⭐）**
- 在异步函数中调用同步 requests 库，用 to_thread 包装，不阻塞事件循环。

---

## 九、主流异步库生态

### 9.1 aiohttp 异步 HTTP

```python
# 示例 9.1.1：GET 请求
import aiohttp

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()
```

```python
# 示例 9.1.2：并发请求
async def main():
    urls = ["https://api.example.com/users/1", ...]
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(u) for u in urls]
        responses = await asyncio.gather(*tasks)
```

```python
# 示例 9.1.3：带超时
timeout = aiohttp.ClientTimeout(total=10)
async with aiohttp.ClientSession(timeout=timeout) as session:
    ...
```

### 9.2 httpx 异步客户端

```python
# 示例 9.2.1：httpx.AsyncClient
import httpx

async def fetch(url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.json()
```

### 9.3 asyncpg 异步 PostgreSQL

```python
# 示例 9.3.1：asyncpg 查询
import asyncpg

async def query():
    conn = await asyncpg.connect("postgresql://user:pass@localhost/db")
    rows = await conn.fetch("SELECT * FROM users WHERE id = $1", 1)
    await conn.close()
    return rows
```

### 9.4 aiosqlite 异步 SQLite

```python
# 示例 9.4.1：aiosqlite
import aiosqlite

async def query():
    async with aiosqlite.connect("test.db") as db:
        async with db.execute("SELECT * FROM users") as cur:
            rows = await cur.fetchall()
    return rows
```

### 9.5 FastAPI 异步 Web

```python
# 示例 9.5.1：FastAPI 异步路由
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{uid}")
async def get_user(uid: int):
    user = await fetch_user(uid)
    return user
```

---

### 💡 本章深度讲解

异步库生态已成熟：HTTP（aiohttp/httpx）、数据库（asyncpg/aiosqlite/aiomysql）、Web（FastAPI/aiohttp/Uvicorn）。选择标准：有异步版本用异步版本，没有就用 to_thread 包装。

### 📝 本章精简总结

- HTTP：aiohttp/httpx。
- 数据库：asyncpg/aiosqlite。
- Web：FastAPI + Uvicorn。
- 连接池复用。

### 🎯 梯度练习题

**基础题（⭐）**
1. aiohttp.ClientSession 的作用？
2. asyncpg 比 psycopg2 快在哪？

**进阶题（⭐⭐）**
1. 为什么 ClientSession 要复用而不是每次新建？
2. httpx 和 aiohttp 的区别？

**实战题（⭐⭐⭐）**
- 用 aiohttp 写一个并发爬虫：信号量限制 20 并发，超时 10 秒。

---

## 十、实战案例

### 10.1 异步爬虫

```python
# 示例 10.1.1：完整爬虫
async def crawl(urls, concurrency=20):
    sem = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as session:
        async def fetch(url):
            async with sem:
                async with session.get(url, timeout=10) as r:
                    return await r.text()
        return await asyncio.gather(*[fetch(u) for u in urls])
```

### 10.2 API 聚合

```python
# 示例 10.2.1：并发调用多个后端
async def get_profile(uid):
    async with aiohttp.ClientSession() as s:
        user, orders, favs = await asyncio.gather(
            s.get(f"http://user/{uid}"),
            s.get(f"http://order/{uid}"),
            s.get(f"http://fav/{uid}"),
            return_exceptions=True,
        )
```

### 10.3 消息消费

```python
# 示例 10.3.1：异步队列消费
async def consume(queue, handler):
    while True:
        msg = await queue.get()
        try:
            await handler(msg)
        finally:
            queue.task_done()
```

---

### 💡 本章深度讲解

实战案例展示了异步的典型用法：IO 密集、并发聚合、消息消费。核心模式是 Semaphore 限并发 + gather 并发 + return_exceptions 容错。

### 📝 本章精简总结

- 爬虫：Semaphore + gather。
- 聚合：gather 并发多后端。
- 消费：Queue 异步。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步爬虫为什么快？
2. Semaphore 在爬虫中的作用？

**进阶题（⭐⭐）**
1. 为什么用 return_exceptions？
2. 如何处理部分失败？

**实战题（⭐⭐⭐）**
- 写一个异步 API 聚合服务：并发调用 3 个后端，任何一个失败不影响其他。

---

## 十一、异常处理与调试

### 11.1 异常传播

```python
# 示例 11.1.1：try/except 包裹 await
async def may_fail():
    raise ValueError

async def main():
    try:
        await may_fail()
    except ValueError as e:
        print(f"捕获: {e}")
```

```python
# 示例 11.1.2：gather + return_exceptions
results = await asyncio.gather(coro1, coro2, return_exceptions=True)
for r in results:
    if isinstance(r, Exception):
        handle(r)
```

### 11.2 全局异常处理

```python
# 示例 11.2.1：loop.set_exception_handler
def handler(loop, context):
    exc = context.get("exception")
    print(f"未捕获异常: {exc}")

async def main():
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(handler)
```

### 11.3 调试模式

```python
# 示例 11.3.1：开启调试
asyncio.run(main(), debug=True)
# 检测未 await 协程、慢回调 >100ms、资源泄漏
```

```python
# 示例 11.3.2：慢回调阈值
loop.slow_callback_duration = 0.05  # 50ms
```

### 11.4 常见错误表

| 错误 | 原因 | 解决 |
|---|---|---|
| coroutine was never awaited | 没 await | await 或 create_task |
| run() cannot be called from running loop | 嵌套 run | 直接 await |
| dict can't be used in await | await 非可等待 | 确认类型 |
| TimeoutError | 超时 | wait_for |
| CancelledError | 任务取消 | 捕获后 re-raise |
| 事件循环卡死 | 调用阻塞函数 | to_thread |
| 任务泄漏 | 不保存引用 | 保持引用 |

---

### 💡 本章深度讲解

异步异常处理的关键是：try/except 包裹 await、gather 用 return_exceptions、全局 handler 兜底。调试模式能检测未 await 协程和慢回调。最大坑是协程中调用阻塞函数卡死事件循环。

### 📝 本章精简总结

- try/except 包裹 await。
- gather return_exceptions。
- 全局 set_exception_handler。
- debug=True 检测问题。
- 阻塞函数用 to_thread。

### 🎯 梯度练习题

**基础题（⭐）**
1. 协程未 await 警告怎么修？
2. 事件循环卡死怎么排查？

**进阶题（⭐⭐）**
1. gather 不加 return_exceptions 会怎样？
2. 全局异常 handler 的作用？

**实战题（⭐⭐⭐）**
- 写一个异步函数：内部调用 3 个协程，任何一个失败都捕获并记录，不影响其他。

---

## 十二、Python 3.11+ 新特性

### 12.1 TaskGroup 结构化并发

```python
# 示例 12.1.1：TaskGroup
async def main():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(work("A", 2))
        t2 = tg.create_task(work("B", 1))
    # 退出时所有任务已完成
    print(t1.result(), t2.result())
```

```python
# 示例 12.1.2：异常自动取消
async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(task1())
            tg.create_task(failing_task())
    except* ValueError as eg:
        print(f"ValueError 组: {eg.exceptions}")
```

### 12.2 ExceptionGroup 与 except*

```python
# 示例 12.2.1：except* 语法
try:
    raise ExceptionGroup("多错误", [ValueError("a"), TypeError("b"), ValueError("c")])
except* ValueError as eg:
    print(f"ValueError: {eg.exceptions}")
except* TypeError as eg:
    print(f"TypeError: {eg.exceptions}")
```

### 12.3 性能提升

Python 3.11 对 asyncio 做了 2-4 倍性能提升，包括：
- 更快的协程调度
- 更高效的 Task 创建
- 优化的 Future

---

### 💡 本章深度讲解

TaskGroup 是结构化并发：退出 with 时自动等待所有任务，任何任务异常自动取消其他并抛 ExceptionGroup。这比手动管理 Task 更安全、更清晰。except* 按类型捕获异常组。

### 📝 本章精简总结

- TaskGroup：async with 管理任务组。
- 自动等待 + 异常传播 + 取消。
- ExceptionGroup + except*。

### 🎯 梯度练习题

**基础题（⭐）**
1. TaskGroup 比 gather 好在哪？
2. except* 的作用？

**进阶题（⭐⭐）**
1. TaskGroup 遇到异常时的行为？
2. 为什么叫"结构化并发"？

**实战题（⭐⭐⭐）**
- 用 TaskGroup 重写你的异步爬虫，替代手动 gather。

---

## 十三、最佳实践与性能优化

### 13.1 代码规范

```python
# ✅ 好
async def main():
    await do_work()

if __name__ == "__main__":
    asyncio.run(main())

# ❌ 坏
async def bad():
    time.sleep(1)  # 阻塞
    fetch(url)     # 没 await
    asyncio.create_task(work())  # 不保存引用
```

### 13.2 性能优化

```python
# 1. 连接池复用
session = aiohttp.ClientSession()  # 全局一次

# 2. 合理并发数
sem = asyncio.Semaphore(20)

# 3. uvloop
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# 4. 批量操作
# 5. 减少 await 点
```

### 13.3 测试异步代码

```python
# pytest-asyncio
import pytest

@pytest.mark.asyncio
async def test_async():
    result = await async_func()
    assert result == "ok"
```

---

### 💡 本章深度讲解

最佳实践核心：永远不要在协程中调用阻塞函数、保持任务引用、用 Semaphore 限并发、连接池复用、uvloop 加速、TaskGroup 结构化并发。

### 📝 本章精简总结

- 不阻塞事件循环。
- 连接池复用。
- uvloop 加速。
- TaskGroup 结构化。
- pytest-asyncio 测试。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么不要每次新建 ClientSession？
2. 如何测试异步代码？

**进阶题（⭐⭐）**
1. 并发数越大越好吗？
2. uvloop 为什么快？

**实战题（⭐⭐⭐）**
- 优化你的异步爬虫：uvloop + 连接池 + 合理并发数，测量性能提升。

---

## 十四、常见坑点汇总

### 14.1 坑点对照表

| # | 坑点 | 解决 |
|---|---|---|
| 1 | 协程未 await | await 或 create_task |
| 2 | 阻塞调用卡死 loop | to_thread |
| 3 | 任务泄漏 | 保持引用 |
| 4 | run 嵌套 | 直接 await |
| 5 | await 非可等待 | 确认类型 |
| 6 | 取消后不 re-raise | 捕获后 raise |
| 7 | Semaphore 用错 | async with |
| 8 | 共享状态无锁 | asyncio.Lock |
| 9 | 每次新建连接 | 连接池复用 |
| 10 | 超时不设置 | wait_for |
| 11 | 异常被吞 | return_exceptions |
| 12 | while True 无 await | 加 await asyncio.sleep(0) |
| 13 | threading.local 失效 | 用 contextvars |
| 14 | 事件循环策略错 | Windows Proactor |
| 15 | 任务异常未查 | task.exception() |
| 16 | gather 一个全挂 | return_exceptions |
| 17 | as_completed 顺序误解 | 按完成顺序 |
| 18 | shield 误解 | 只保护 await 点 |
| 19 | Queue 不 task_done | join 永远等 |
| 20 | 异步中用同步 with | async with |
| 21 | CPU 密集用异步 | 进程池 |
| 22 | 事件循环关太早 | run 等所有任务 |
| 23 | 信号量不释放 | async with |
| 24 | 子进程 Windows 问题 | ProactorEventLoop |
| 25 | 大结果集内存 | stream/迭代 |
| 26 | 日志阻塞 loop | 异步日志或线程 |
| 27 | 重试在异步中用 time.sleep | asyncio.sleep |
| 28 | 上下文变量跨任务 | contextvars.copy_context |
| 29 | 任务名冲突 | create_task(name=...) |
| 30 | 测试等待时间 | asyncio.sleep 用真时间 |

---

### 💡 本章深度讲解

30 个坑点覆盖了 asyncio 的全部典型错误。最大的杀手是阻塞调用卡死事件循环。其次是任务泄漏和异常处理不当。排查时先看现象归类，再对照表。

### 📝 本章精简总结

- 不阻塞 loop。
- 保持任务引用。
- 异常显式处理。
- Semaphore async with。
- 连接池复用。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么 time.sleep 卡死 loop？
2. 任务泄漏是什么？

**进阶题（⭐⭐）**
1. 为什么 threading.local 在异步中失效？
2. 如何排查事件循环卡死？

**实战题（⭐⭐⭐）**
- 审查你的异步代码，对照 30 个坑点逐一检查。

---

## 十五、面试高频考点汇总

### 15.1 asyncio 基础题

1. **什么是协程？和线程的区别？**
   > 答：协程是用户态可挂起恢复的函数，线程是内核态抢占式调度。协程切换纳秒级、内存 KB 级、万级并发；线程切换微秒级、MB 级、千级并发。

2. **async/await 的底层原理？**
   > 答：async def 定义协程函数，调用返回协程对象。await 挂起当前协程，保存上下文，把控制权还给事件循环。等待操作完成后事件循环恢复协程。

3. **事件循环是什么？**
   > 答：asyncio 的核心引擎，无限循环检查就绪任务、通过 IO 多路复用等待事件、调度协程执行。

4. **Task 和 Future 的关系？**
   > 答：Future 是异步结果占位符，Task 是 Future 的子类，包装协程使其可调度。

5. **gather/wait/as_completed 区别？**
   > 答：gather 全部并发按序返回；wait 可设等待条件；as_completed 按完成顺序 yield。

6. **为什么不能在协程中调用阻塞函数？**
   > 答：单线程模型，阻塞调用会卡住整个事件循环，其他协程无法执行。

7. **如何运行阻塞函数？**
   > 答：asyncio.to_thread() 或 run_in_executor 丢到线程池。

8. **CPU 密集为什么不用异步？**
   > 答：异步单线程，CPU 密集会占满一个核心，无法利用多核。应该用多进程。

9. **什么是结构化并发？**
   > 答：TaskGroup 用 async with 管理任务组，退出时自动等待所有任务，异常自动取消其他。

10. **CancelledError 怎么处理？**
    > 答：捕获做清理，然后必须 re-raise，否则掩盖取消。

### 15.2 异步 IO 题

11. **aiohttp.ClientSession 为什么要复用？**
    > 答：内部维护连接池，复用避免 TCP 握手开销。每次新建会慢且耗资源。

12. **asyncpg 为什么快？**
    > 答：纯异步实现，无阻塞，和事件循环集成，协议级优化。

13. **异步文件 IO 怎么实现？**
    > 答：aiofiles 底层用线程池包装同步 open，因为操作系统没有真正的异步文件 API（Linux AIO 不成熟）。

14. **WebSocket 在 asyncio 中怎么做？**
    > 答：aiohttp.WebSocketResponse 或 websockets 库。

15. **如何优雅关闭异步服务器？**
    > 答：监听信号，停止接受新连接，等待现有连接处理完，关闭事件循环。

### 15.3 同步原语题

16. **异步 Lock 和 threading.Lock 的区别？**
    > 答：异步 Lock 是协程级，async with，不阻塞事件循环；threading.Lock 是线程级，会阻塞。

17. **Semaphore 怎么用？**
    > 答：async with sem: 块内最多 N 个协程同时执行。

18. **Queue 和 asyncio.Queue 的区别？**
    > 答：asyncio.Queue 是协程安全的，put/get 是 await 的，不阻塞事件循环。

19. **Event 和 Condition 的区别？**
    > 答：Event 是简单信号（set/wait），Condition 支持更复杂的等待条件和 notify。

20. **单线程为什么还需要锁？**
    > 答：在 await 点之间可能有其他协程修改共享状态，需要锁保护临界区。

---

### 💡 本章深度讲解

面试题覆盖基础概念、IO、同步原语、生产实践。核心考点：协程 vs 线程、事件循环原理、并发 API 区别、阻塞函数处理、TaskGroup、异常处理。

### 📝 本章精简总结

- 协程 vs 线程 vs 进程。
- 事件循环 + IO多路复用。
- 并发 API 四件套。
- 不阻塞 loop。
- TaskGroup 结构化并发。

### 🎯 梯度练习题

**基础题（⭐）**
1. 默写 async/await 语法。
2. 解释事件循环原理。

**进阶题（⭐⭐）**
1. 为什么协程不需要锁？
2. TaskGroup 解决了什么问题？

**实战题（⭐⭐⭐）**
- 白板手写：并发请求 10 个 URL，超时 5 秒，信号量限制 5 并发。

---

### 十六、异步架构模式

### 16.1 生产者-消费者

```python
# 示例 16.1.1：完整生产者消费者
async def producer(queue, name, n=10):
    for i in range(n):
        await queue.put(f"{name}-{i}")
        await asyncio.sleep(0.1)

async def consumer(queue, name):
    while True:
        item = await queue.get()
        try:
            print(f"{name} 处理 {item}")
            await asyncio.sleep(0.2)
        finally:
            queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=5)
    producers = [asyncio.create_task(producer(queue, f"P{i}")) for i in range(2)]
    consumers = [asyncio.create_task(consumer(queue, f"C{i}")) for i in range(3)]
    await asyncio.gather(*producers)
    await queue.join()
    for c in consumers:
        c.cancel()

asyncio.run(main())
```

### 16.2 Fan-out/Fan-in

```python
# 示例 16.2.1：扇出扇入
async def fan_out_fan_in(urls):
    async with aiohttp.ClientSession() as session:
        # Fan-out：分发到多个 worker
        tasks = [asyncio.create_task(worker(session, u)) for u in urls]
        # Fan-in：收集结果
        results = await asyncio.gather(*tasks)
    return results
```

### 16.3 Pipeline 管道

```python
# 示例 16.3.1：异步管道
async def stage1(input_q, output_q):
    while True:
        item = await input_q.get()
        result = item * 2
        await output_q.put(result)
        input_q.task_done()

async def stage2(input_q, output_q):
    while True:
        item = await input_q.get()
        result = item + 1
        await output_q.put(result)
        input_q.task_done()
```

### 16.4 延时任务

```python
# 示例 16.4.1：延迟执行
async def later(delay, func, *args):
    await asyncio.sleep(delay)
    return func(*args)
```

### 16.5 心跳/监控

```python
# 示例 16.5.1：心跳任务
async def heartbeat(interval=5):
    while True:
        print(f"心跳 {time.strftime('%H:%M:%S')}")
        await asyncio.sleep(interval)
```

---

### 💡 本章深度讲解

异步架构模式：生产者消费者（Queue）、扇出扇入（gather）、管道（多阶段 Queue）、延时任务（sleep）、心跳（while True + sleep）。这些模式组合起来可以构建复杂的异步系统。

### 📝 本章精简总结

- 生产者消费者：Queue。
- 扇出扇入：gather。
- 管道：多阶段 Queue。
- 心跳：while True + sleep。

### 🎯 梯度练习题

**基础题（⭐）**
1. 生产者消费者用什么？
2. Fan-out/Fan-in 是什么？

**进阶题（⭐⭐）**
1. 如何实现多阶段管道？
2. 心跳任务怎么优雅停止？

**实战题（⭐⭐⭐）**
- 实现一个异步管道：stage1 读取 → stage2 处理 → stage3 写入，用 Queue 连接。

---

### 十七、异步 Web 框架深度

### 17.1 FastAPI 异步依赖

```python
# 示例 17.1.1：异步依赖注入
from fastapi import Depends, FastAPI

app = FastAPI()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/users/{uid}")
async def get_user(uid: int, db=Depends(get_db)):
    return await db.get(User, uid)
```

### 17.2 WebSocket

```python
# 示例 17.2.1：aiohttp WebSocket
from aiohttp import web

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            await ws.send_str(f"echo: {msg.data}")
    return ws
```

### 17.3 SSE 流式响应

```python
# 示例 17.3.1：Server-Sent Events
async def stream(request):
    response = web.StreamResponse()
    await response.prepare(request)
    for i in range(10):
        await response.write(f"data: {i}\n\n".encode())
        await asyncio.sleep(1)
    return response
```

---

### 💡 本章深度讲解

异步 Web 框架是 asyncio 最大的应用场景。FastAPI 依赖注入、WebSocket、SSE 都是异步 IO 的典型应用。理解事件循环是理解 Web 框架的基础。

### 📝 本章精简总结

- FastAPI 异步依赖。
- WebSocket 双向通信。
- SSE 流式响应。

### 🎯 梯度练习题

**基础题（⭐）**
1. FastAPI 依赖注入的作用？
2. WebSocket 是什么？

**进阶题（⭐⭐）**
1. 为什么 Web 框架要用异步？
2. SSE 和 WebSocket 的区别？

**实战题（⭐⭐⭐）**
- 用 FastAPI 写一个 WebSocket 聊天端点。

---

### 十八、异步数据库深度

### 18.1 SQLAlchemy 异步

```python
# 示例 18.1.1：异步引擎和会话
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_user(uid):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == uid))
        return result.scalar_one_or_none()
```

### 18.2 连接池

```python
# 示例 18.2.1：连接池配置
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
```

### 18.3 异步 Redis

```python
# 示例 18.3.1：aioredis
import aioredis

async def cache():
    redis = await aioredis.from_url("redis://localhost")
    await redis.set("key", "value")
    val = await redis.get("key")
    await redis.close()
```

---

### 💡 本章深度讲解

异步数据库是 Web 后端的核心。SQLAlchemy 2.0 原生异步支持，连接池复用，asyncpg 高性能驱动。

### 📝 本章精简总结

- async_sessionmaker 创建会话工厂。
- 连接池 pool_size/max_overflow。
- await execute 查询。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步数据库和同步的区别？
2. 连接池的作用？

**进阶题（⭐⭐）**
1. expire_on_commit=False 的作用？
2. 为什么用 asyncpg？

**实战题（⭐⭐⭐）**
- 用 SQLAlchemy 异步写一个用户 CRUD 服务。

---

### 十九、异步测试

### 19.1 pytest-asyncio

```python
# 示例 19.1.1：测试异步函数
import pytest

@pytest.mark.asyncio
async def test_fetch():
    result = await async_fetch(1)
    assert result["id"] == 1
```

### 19.2 异步 fixture

```python
# 示例 19.2.1：异步 fixture
@pytest_asyncio.fixture
async def async_client():
    client = await create_client()
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_endpoint(async_client):
    r = await async_client.get("/")
    assert r.status == 200
```

### 19.3 测试超时

```python
# 示例 19.3.1：测试超时
@pytest.mark.asyncio
async def test_timeout():
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow(), timeout=0.1)
```

---

### 💡 本章深度讲解

测试异步代码用 pytest-asyncio，fixture 也支持异步。测试超时和异常。

### 📝 本章精简总结

- @pytest.mark.asyncio。
- 异步 fixture yield。
- 测试超时和异常。

### 🎯 梯度练习题

**基础题（⭐）**
1. 如何测试异步函数？
2. 异步 fixture 怎么写？

**进阶题（⭐⭐）**
1. 如何测试异步异常？
2. 如何 mock 异步依赖？

**实战题（⭐⭐⭐）**
- 为你的异步 API 写完整测试。

---

### 二十、异步性能剖析

### 20.1 测量耗时

```python
# 示例 20.1.1：测量协程耗时
async def measure(coro):
    t0 = time.perf_counter()
    result = await coro
    dt = time.perf_counter() - t0
    return result, dt
```

### 20.2 找慢回调

```python
# 示例 20.2.1：慢回调检测
loop.slow_callback_duration = 0.05  # 50ms
# debug 模式下打印超过阈值的回调
```

### 20.3 py-spy 性能分析

```bash
# pip install py-spy
# py-spy top --pid <pid>
# py-spy dump --pid <pid>
```

### 20.4 常见性能瓶颈

| 瓶颈 | 原因 | 解决 |
|---|---|---|
| 阻塞调用 | time.sleep/requests | to_thread |
| 连接不复用 | 每次新建 | 连接池 |
| 并发太高 | 目标服务器扛不住 | Semaphore 限制 |
| 大量小任务 | 创建开销 | 批量合并 |
| 同步日志 | print 阻塞 | 异步日志 |

---

### 💡 本章深度讲解

性能优化核心：消除阻塞调用、复用连接、合理限并发、批量操作。用 debug 模式和 py-spy 定位瓶颈。

### 📝 本章精简总结

- 不阻塞 loop。
- 连接池复用。
- Semaphore 限并发。
- py-spy 分析。

### 🎯 梯度练习题

**基础题（⭐）**
1. 如何找慢回调？
2. py-spy 的作用？

**进阶题（⭐⭐）**
1. 并发数为什么不是越大越好？
2. 如何消除阻塞？

**实战题（⭐⭐⭐）**
- 用 py-spy 分析你的异步应用，找到最慢的协程并优化。

---

### 二十一、异步错误恢复

### 21.1 重试 + 超时 + 熔断

```python
# 示例 21.1.1：完整错误恢复
async def robust_fetch(url, retries=3, timeout=5):
    for i in range(retries):
        try:
            return await asyncio.wait_of(session.get(url), timeout=timeout)
        except (asyncio.TimeoutError, aiohttp.ClientError):
            if i == retries - 1:
                raise
            await asyncio.sleep(0.5 * (2 ** i))
```

### 21.2 降级策略

```python
# 示例 21.2.1：降级返回缓存
async def get_user(uid):
    try:
        return await fetch_from_db(uid)
    except Exception:
        return await redis.get(f"user:{uid}")  # 降级到缓存
```

### 21.3 断路器

```python
# 示例 21.3.1：异步熔断器
class AsyncCircuitBreaker:
    def __init__(self, failures=5, reset_timeout=60):
        self.failures = failures
        self.reset_timeout = reset_timeout
        self.count = 0
        self.opened_until = 0
    async def call(self, func, *a, **kw):
        now = time.time()
        if now < self.opened_until:
            raise RuntimeError("熔断中")
        try:
            r = await func(*a, **kw)
            self.count = 0
            return r
        except Exception:
            self.count += 1
            if self.count >= self.failures:
                self.opened_until = now + self.reset_timeout
            raise
```

---

### 💡 本章深度讲解

生产异步系统必须有错误恢复：重试（指数退避）、超时（wait_for）、熔断（失败快速失败）、降级（返回缓存）。

### 📝 本章精简总结

- 重试 + 超时 + 熔断 + 降级。
- 指数退避。
- 失败快速失败。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么要重试？
2. 熔断的作用？

**进阶题（⭐⭐）**
1. 指数退避为什么加抖动？
2. 降级策略有哪些？

**实战题（⭐⭐⭐）**
- 为你的 HTTP 客户端实现完整错误恢复：重试+超时+熔断+降级。

---

### 二十二、异步与 contextvars

### 22.1 contextvars 基础

```python
# 示例 22.1.1：ContextVar
import contextvars

request_id = contextvars.ContextVar("request_id", default="-")

async def handle():
    request_id.set("abc-123")
    print(f"处理 {request_id.get()}")
```

### 22.2 Task 间 context 隔离

```python
# 示例 22.2.1：Task 自动复制 context
async def worker():
    request_id.set("task-value")
    print(request_id.get())

async def main():
    request_id.set("main-value")
    task = asyncio.create_task(worker())
    await task
    print(request_id.get())  # main-value（task 内的 set 不影响外层）
```

### 22.3 链路追踪

```python
# 示例 22.3.1：请求 ID 链路追踪
trace_id = contextvars.ContextVar("trace_id")

async def traced_call():
    print(f"[{trace_id.get()}] 调用")
    await downstream()
```

---

### 💡 本章深度讲解

contextvars 是异步版线程局部变量。每个 Task 自动复制 context，任务内的 set 不影响外层。用于请求 ID、用户身份、链路追踪。

### 📝 本章精简总结

- ContextVar 替代 threading.local。
- Task 自动复制 context。
- 请求 ID 链路追踪。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么异步不能用 threading.local？
2. ContextVar 的作用？

**进阶题（⭐⭐）**
1. create_task 如何处理 context？
2. 如何实现链路追踪？

**实战题（⭐⭐⭐）**
- 用 ContextVar 实现请求 ID 自动注入日志。

---

### 二十三、异步日志

### 23.1 异步日志问题

同步 logging 是线程安全的，但在异步中高频 logging 会阻塞事件循环。

```python
# 示例 23.1.1：异步日志方案
# 方案1：用 QueuedHandler 把日志丢到队列，后台线程写
# 方案2：用第三方异步日志库
# 方案3：减少日志量，DEBUG 级别生产关闭
```

### 23.2 结构化日志

```python
# 示例 23.2.1：JSON 结构化日志
import logging, json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "ts": record.created,
            "func": record.funcName,
            "msg": record.getMessage(),
        })
```

---

### 💡 本章深度讲解

异步日志要避免阻塞事件循环。用队列异步写或减少日志量。

### 📝 本章精简总结

- 同步日志阻塞 loop。
- 队列异步写。
- 结构化 JSON。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么 print 阻塞事件循环？
2. 结构化日志好处？

**进阶题（⭐⭐）**
1. 如何实现异步日志？
2. 生产环境日志级别？

**实战题（⭐⭐⭐）**
- 为异步应用配置异步日志：队列+后台写+JSON格式。

---

### 二十四、异步配置与部署

### 24.1 配置管理

```python
# 示例 24.1.1：pydantic-settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    MAX_CONCURRENCY: int = 20
```

### 24.2 Uvicorn 部署

```bash
# uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
# --workers 多进程，每个进程一个事件循环
```

### 24.3 Gunicorn + Uvicorn worker

```bash
# gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

### 💡 本章深度讲解

异步应用部署：多进程（Gunicorn/Uvicorn workers），每个进程一个事件循环。配置用 pydantic-settings。

### 📝 本章精简总结

- 多进程部署。
- Uvicorn/Gunicorn。
- 配置管理。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么异步应用要多进程？
2. Uvicorn 的作用？

**进阶题（⭐⭐）**
1. 多进程和单进程事件循环的关系？
2. 如何配置 workers？

**实战题（⭐⭐⭐）**
- 部署你的 FastAPI 应用到生产：Gunicorn + Uvicorn worker + 4 workers。

---

### 二十五、学习资源与延伸

### 25.1 官方文档

- docs.python.org/3/library/asyncio.html
- docs.python.org/3/whatsnew/3.11.html

### 25.2 推荐书籍

- **Using Asyncio in Python** (Caleb Hattingh)
- **Fluent Python** 异步章节

### 25.3 开源项目

- **aiohttp**：异步 HTTP
- **FastAPI**：异步 Web
- **uvloop**：高性能事件循环
- **httpx**：同步异步双 HTTP

### 25.4 进阶方向

- **asyncio + WebSocket**：实时应用
- **asyncio + 消息队列**：微服务
- **asyncio + 机器学习**：异步推理

---

> 💡 **本文总结**：asyncio 是 Python 异步编程的标准库，核心是事件循环 + 协程 + Task。掌握它需要理解：协作式调度、IO 多路复用、不阻塞原则、结构化并发。从协程语法到生产架构，本文 25 章覆盖了全部核心知识点。

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]] — 异步上下文管理器
- [[Python-语法基础与数据结构]] — 前置
- [[FastAPI-路由与依赖注入]] — 异步 Web 框架
- [[SQLAlchemy-ORM核心原理]] — 异步数据库
- [[aiohttp-异步HTTP]] — 异步 HTTP 客户端

### 📖 前置知识

- [[Python-语法基础与数据结构]]
- [[Python-类型注解与mypy]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #事件循环 #高并发

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 二十六、协程原理深入剖析

### 26.1 从生成器到协程

Python 协程经历了三个阶段：

```python
# 示例 26.1.1：Python 2.5 生成器协程雏形
def bare_generator_coroutine():
    while True:
        value = yield
        print(f"收到: {value}")

gen = bare_generator_coroutine()
next(gen)           # 启动到第一个 yield
gen.send("hello")    # 收到: hello
gen.send("world")    # 收到: world
```

```python
# 示例 26.1.2：Python 3.4 @asyncio.coroutine
# @asyncio.coroutine
# def old_style():
#     yield from asyncio.sleep(1)
# 已废弃，不推荐
```

```python
# 示例 26.1.3：Python 3.5+ async/await（现代标准）
async def modern_coroutine():
    await asyncio.sleep(1)
```

### 26.2 协程状态机

```mermaid
stateDiagram-v2
    [*] --> CREATED: 调用协程函数
    CREATED --> SUSPENDED: await 挂起
    SUSPENDED --> RUNNING: 事件循环恢复
    RUNNING --> SUSPENDED: 遇到下一个 await
    RUNNING --> CLOSED: return/异常
    SUSPENDED --> CLOSED: close()
```

```python
# 示例 26.2.1：查看协程状态
import asyncio, inspect

async def my_coro():
    await asyncio.sleep(0.1)
    return "done"

coro = my_coro()
print(inspect.getcoroutinestate(coro))  # 'CREATED'

async def main():
    result = await coro
    print(inspect.getcoroutinestate(coro))  # 'CLOSED'

asyncio.run(main())
```

### 26.3 await 挂起机制

```python
# 示例 26.3.1：await 点让出控制权
async def a():
    print("A1")
    await asyncio.sleep(0)  # 让出控制权
    print("A2")

async def b():
    print("B1")
    await asyncio.sleep(0)
    print("B2")

async def main():
    await asyncio.gather(a(), b())

asyncio.run(main())
# 输出：
# A1
# B1
# A2
# B2
```

> 🎯 **面试高频**：await 做了什么？
>
> **答**：await 后面的对象必须是 awaitable。await 挂起当前协程，保存执行上下文（栈帧、寄存器），把控制权还给事件循环。事件循环执行其他就绪协程，等待的操作完成后，事件循环恢复协程从挂起点继续执行。这个过程是用户态切换，没有内核参与，所以极快。

### 26.4 协程 vs 生成器

| 维度 | 生成器 | 协程 |
|---|---|---|
| 语法 | yield | async/await |
| 数据流向 | 产出数据 | 控制流挂起/恢复 |
| 复用 | 单迭代 | 可多次挂起恢复 |
| 错误处理 | throw | raise + 异常传播 |
| 状态 | GI/GS/GEN_CLOSED | CREATED/SUSPENDED/RUNNING/CLOSED |

---

### 💡 本章深度讲解

协程本质是"可挂起可恢复的函数"，从生成器演进而来。await 是挂起点，保存上下文，让出控制权。事件循环负责在挂起点之间调度其他协程。理解这个机制就理解了 asyncio 的核心。

### 📝 本章精简总结

- 协程三阶段：生成器 → @coroutine → async/await。
- 状态：CREATED/SUSPENDED/RUNNING/CLOSED。
- await 挂起让出控制权。
- 用户态切换纳秒级。

### 🎯 梯度练习题

**基础题（⭐）**
1. 协程和生成器的关系？
2. 协程有哪几种状态？
3. await 做了什么？

**进阶题（⭐⭐）**
1. 为什么 await 能让出控制权？
2. 协程切换为什么比线程快？

**实战题（⭐⭐⭐）**
- 用 inspect 观察协程从 CREATED 到 CLOSED 的状态变化。

---

### 二十七、事件循环深度剖析

### 27.1 事件循环内部结构

```mermaid
graph TB
    subgraph EventLoop
        R[Ready Queue<br/>就绪任务队列]
        S[Scheduled Callbacks<br/>定时器堆]
        I[Selector<br/>IO多路复用 epoll]
    end
    R -->|执行就绪任务| T[Task]
    T -->|await挂起| I
    I -->|IO就绪| R
    S -->|到期| R
```

### 27.2 事件循环生命周期

```python
# 示例 27.2.1：完整生命周期
async def main():
    loop = asyncio.get_running_loop()
    print(f"循环: {loop}")
    print(f"运行中: {loop.is_running()}")

asyncio.run(main())
```

### 27.3 自定义事件循环策略

```python
# 示例 27.3.1：Windows ProactorEventLoop（支持子进程）
import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

### 27.4 事件循环中的回调链

```python
# 示例 27.4.1：call_soon 回调顺序
async def main():
    loop = asyncio.get_running_loop()
    loop.call_soon(lambda: print("回调1"))
    loop.call_soon(lambda: print("回调2"))
    print("先打印")
    await asyncio.sleep(0.1)

asyncio.run(main())
# 先打印 → 回调1 → 回调2
```

---

### 💡 本章深度讲解

事件循环是 asyncio 的心脏，由就绪队列、定时器堆、IO 多路复用三部分组成。它不断从就绪队列取任务执行，任务 await 时注册到 selector，IO 就绪后重新入队。

### 📝 本章精简总结

- 就绪队列 + 定时器 + selector。
- call_soon/call_later/call_at。
- Windows Proactor。

### 🎯 梯度练习题

**基础题（⭐）**
1. 事件循环由哪几部分组成？
2. call_soon 和 call_later 区别？

**进阶题（⭐⭐）**
1. 事件循环如何知道 IO 就绪？
2. 为什么 Windows 需要 Proactor？

**实战题（⭐⭐⭐）**
- 用 call_later 实现一个简单的定时器任务。

---

### 二十八、Task 深度剖析

### 28.1 Task 创建与调度

```python
# 示例 28.1.1：create_task 立即调度
async def work():
    print("工作")

async def main():
    print("创建前")
    task = asyncio.create_task(work())
    print("创建后，task 已在事件循环队列中")
    await task
    print("完成")

asyncio.run(main())
# 输出：创建前 / 创建后 / 工作 / 完成
```

### 28.2 Task 取消传播

```python
# 示例 28.2.1：取消传播链
async def grandchild():
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("孙子被取消")
        raise

async def child():
    try:
        await grandchild()
    except asyncio.CancelledError:
        print("儿子被取消")
        raise

async def main():
    t = asyncio.create_task(child())
    await asyncio.sleep(1)
    t.cancel()
    try:
        await t
    except asyncio.CancelledError:
        print("主程序被取消")
```

### 28.3 TaskGroup 深度

```python
# 示例 28.3.1：TaskGroup 异常处理
async def ok_task():
    await asyncio.sleep(1)
    return "ok"

async def fail_task():
    await asyncio.sleep(0.5)
    raise ValueError("失败")

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(ok_task())
            t2 = tg.create_task(fail_task())
    except* ValueError as eg:
        print(f"捕获: {eg.exceptions}")
    print(f"t1 结果: {t1.result()}")
```

### 28.4 Task 命名

```python
# 示例 28.4.1：Task 命名（3.8+）
async def main():
    task = asyncio.create_task(work(), name="my-worker")
    print(task.get_name())  # my-worker
```

---

### 💡 本章深度讲解

Task 是协程的并发封装。create_task 立即提交到事件循环。取消会传播到子任务。TaskGroup 是结构化并发的现代方式，自动管理任务生命周期。

### 📝 本章精简总结

- create_task 立即调度。
- cancel 传播到子任务。
- TaskGroup 结构化并发。
- 3.8+ 支持 Task 命名。

### 🎯 梯度练习题

**基础题（⭐）**
1. create_task 做了什么？
2. cancel 如何工作？

**进阶题（⭐⭐）**
1. 取消为什么会传播？
2. TaskGroup 比 gather 好在哪？

**实战题（⭐⭐⭐）**
- 用 TaskGroup 重写一个并发爬虫，确保异常时所有任务正确取消。

---

### 二十九、异步 IO 深度

### 29.1 IO 多路复用原理

```python
# 示例 29.1.1：selectors 模块
import selectors
selector = selectors.DefaultSelector()
print(type(selector))
# Linux: <class 'selectors.EpollSelector'>
# macOS: <class 'selectors.KqueueSelector'>
# Windows: <class 'selectors.SelectSelector'>
```

### 29.2 aiohttp 连接池

```python
# 示例 29.2.1：配置 aiohttp 连接池
import aiohttp

timeout = aiohttp.ClientTimeout(total=10, connect=5)
connector = aiohttp.TCPConnector(
    limit=100,              # 总连接数
    limit_per_host=20,      # 每主机连接数
    ttl_dns_cache=300,      # DNS 缓存
)
session = aiohttp.ClientSession(connector=connector, timeout=timeout)
```

### 29.3 异步流式读取

```python
# 示例 29.3.1：流式 HTTP 响应
async def stream_download(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            async for chunk in response.content.iter_chunked(8192):
                process(chunk)
```

### 29.4 异步 WebSocket

```python
# 示例 29.4.1：aiohttp WebSocket 客户端
async def ws_client(url):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            await ws.send_str("hello")
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print(msg.data)
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    break
```

---

### 💡 本章深度讲解

异步 IO 的底层是 IO 多路复用。aiohttp 的连接池、流式读取、WebSocket 都是生产级必备。理解底层原理能帮助你调优。

### 📝 本章精简总结

- epoll/kqueue/IOCP。
- 连接池 limit/limit_per_host。
- 流式读取 iter_chunked。
- WebSocket 双向通信。

### 🎯 梯度练习题

**基础题（⭐）**
1. epoll 是什么？
2. aiohttp 连接池配置？

**进阶题（⭐⭐）**
1. 为什么 limit_per_host 重要？
2. 流式读取的好处？

**实战题（⭐⭐⭐）**
- 写一个异步大文件下载器：流式读取 + 进度显示。

---

### 三十、异步同步原语深度

### 30.1 Lock 内部原理

```python
# 示例 30.1.1：异步 Lock 状态
lock = asyncio.Lock()
print(lock.locked())  # False
await lock.acquire()
print(lock.locked())  # True
lock.release()
```

### 30.2 Semaphore 公平性

```python
# 示例 30.2.1：BoundedSemaphore
sem = asyncio.BoundedSemaphore(3)
# release 超过初始值会报错，防止误用
```

### 30.3 Queue 优先级

```python
# 示例 30.3.1：PriorityQueue
pq = asyncio.PriorityQueue()
await pq.put((1, "低优先级"))
await pq.put((0, "高优先级"))
print(await pq.get())  # (0, "高优先级")
```

### 30.4 Queue LIFO

```python
# 示例 30.4.1：LifoQueue
lq = asyncio.LifoQueue()
await lq.put(1)
await lq.put(2)
print(await lq.get())  # 2
```

---

### 💡 本章深度讲解

异步同步原语是协程级别的，不阻塞事件循环。Semaphore 限并发、Queue 解耦、Event 通知、Lock 保护临界区。

### 📝 本章精简总结

- Lock：临界区。
- Semaphore：限并发。
- PriorityQueue/LifoQueue。
- Event/Condition。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步 Lock 和线程 Lock 的区别？
2. PriorityQueue 怎么排序？

**进阶题（⭐⭐）**
1. 为什么用 BoundedSemaphore？
2. Queue 和 LifoQueue 的区别？

**实战题（⭐⭐⭐）**
- 用 PriorityQueue 实现任务调度：高优先级任务先执行。

---

### 三十一、异步生产架构

### 31.1 典型架构

```mermaid
graph TB
    C[客户端] --> U[Uvicorn/Gunicorn]
    U --> A[FastAPI 应用]
    A --> DB[(PostgreSQL asyncpg)]
    A --> R[(Redis aioredis)]
    A --> M[(消息队列)]
    A --> E[外部API aiohttp]
```

### 31.2 优雅关闭

```python
# 示例 31.2.1：信号处理
import signal

async def shutdown(signal, loop):
    print(f"收到信号 {signal.name}")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

loop = asyncio.get_event_loop()
for sig in (signal.SIGINT, signal.SIGTERM):
    loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s, loop)))
```

### 31.3 健康检查

```python
# 示例 31.3.1：健康检查端点
@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": time.time()}
```

### 31.4 指标监控

```python
# 示例 31.4.1：Prometheus 指标
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter("requests", "请求数")
REQUEST_LATENCY = Histogram("latency", "延迟")

@app.middleware("http")
async def metrics(request, call_next):
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        return await call_next(request)
```

---

### 💡 本章深度讲解

生产异步架构：Uvicorn/Gunicorn 多进程、优雅关闭、健康检查、指标监控。这些是从 demo 到生产的必要步骤。

### 📝 本章精简总结

- 多进程部署。
- 优雅关闭：信号处理 + cancel tasks。
- 健康检查 /health。
- Prometheus 指标。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么要优雅关闭？
2. /health 端点的作用？

**进阶题（⭐⭐）**
1. 如何实现优雅关闭？
2. 如何监控异步应用？

**实战题（⭐⭐⭐）**
- 为你的 FastAPI 应用添加：优雅关闭、健康检查、请求计数指标。

---

### 三十二、异步调试技巧

### 32.1 调试模式

```python
# 示例 32.1.1：debug=True
asyncio.run(main(), debug=True)
```

### 32.2 打印所有任务

```python
# 示例 32.2.1：列出所有任务
async def debug_tasks():
    tasks = asyncio.all_tasks()
    for t in tasks:
        print(f"{t.get_name()}: {t._state}")
```

### 32.3 栈追踪

```python
# 示例 32.3.1：查看协程栈
import traceback

async def show_stack():
    tasks = asyncio.all_tasks()
    for t in tasks:
        print(f"=== {t.get_name()} ===")
        traceback.print_stack(t._source_traceback)
```

### 32.4 faulthandler

```python
# 示例 32.4.1：faulthandler 转储
import faulthandler
faulthandler.dump_traceback()
# 或定时 dump
faulthandler.dump_traceback_later(10)  # 10秒后 dump
```

---

### 💡 本章深度讲解

异步调试比同步难，因为单线程多协程交错执行。调试模式、all_tasks、faulthandler 是三大工具。py-spy 是生产环境性能分析利器。

### 📝 本章精简总结

- debug=True。
- all_tasks()。
- faulthandler。
- py-spy。

### 🎯 梯度练习题

**基础题（⭐）**
1. debug=True 做了什么？
2. 如何列出所有任务？

**进阶题（⭐⭐）**
1. 异步为什么难调试？
2. faulthandler 的作用？

**实战题（⭐⭐⭐）**
- 用 debug 模式找一个"协程未 await"的 bug。

---

### 三十三、异步设计模式

### 33.1 异步策略模式

```python
# 示例 33.1.1：异步策略
class AsyncStrategy:
    async def execute(self, data): ...

class FastStrategy(AsyncStrategy):
    async def execute(self, data):
        return await fast_process(data)

class SlowStrategy(AsyncStrategy):
    async def execute(self, data):
        return await slow_process(data)
```

### 33.2 异步观察者

```python
# 示例 33.2.1：异步事件总线
class EventBus:
    def __init__(self):
        self.subscribers = []
    def subscribe(self, callback):
        self.subscribers.append(callback)
    async def emit(self, event):
        for cb in self.subscribers:
            await cb(event)
```

### 33.3 异步代理

```python
# 示例 33.3.1：异步代理
class AsyncProxy:
    def __init__(self, real):
        self.real = real
    async def request(self, data):
        # 前置：限流/缓存/日志
        result = await self.real.request(data)
        # 后置：统计
        return result
```

---

### 💡 本章深度讲解

设计模式在异步中依然适用，只是方法变成 async。事件总线、策略、代理都是常见异步模式。

### 📝 本章精简总结

- 策略/观察者/代理都可异步化。
- 事件总线解耦。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步事件总线怎么实现？
2. 异步策略模式？

**进阶题（⭐⭐）**
1. 异步观察者和同步的区别？
2. 异步代理的应用场景？

**实战题（⭐⭐⭐）**
- 实现一个异步事件总线：订阅者异步处理事件。

---

### 三十四、异步反模式

### 34.1 反模式清单

| 反模式 | 问题 | 正确做法 |
|---|---|---|
| 协程中 time.sleep | 阻塞 loop | asyncio.sleep |
| 协程中 requests.get | 阻塞 loop | aiohttp |
| 不保存 Task 引用 | 任务泄漏 | 集合保存 |
| 嵌套 asyncio.run | RuntimeError | 直接 await |
| while True 无 await | 卡死 loop | await asyncio.sleep(0) |
| 每次新建 Session | 连接不复用 | 全局复用 |
| 不设超时 | 永久挂起 | wait_for |
| 同步 with 包异步资源 | 不工作 | async with |
| 用 threading.local | 跨协程失效 | contextvars |
| 阻塞 CPU | 占满单线程 | 进程池 |

---

### 💡 本章深度讲解

反模式的核心是"在协程中做了同步阻塞的事"。原则是：任何可能阻塞的操作都要用异步版本或 to_thread。

### 📝 本章精简总结

- 不阻塞 loop。
- 保存任务引用。
- 不嵌套 run。
- 连接池复用。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么 while True 要加 await？
2. 为什么不能嵌套 run？

**进阶题（⭐⭐）**
1. 为什么 threading.local 失效？
2. 如何检测阻塞调用？

**实战题（⭐⭐⭐）**
- 审查你的异步代码，列出所有反模式并修复。

---

### 三十五、异步 vs 同步决策树

```mermaid
flowchart TD
    A[新任务] --> B{IO密集?}
    B -->|否| C[CPU密集]
    C --> D[多进程]
    B -->|是| E{有异步库?}
    E -->|是| F[asyncio]
    E -->|否| G{阻塞库可包装?}
    G -->|是| H[asyncio + to_thread]
    G -->|否| I[线程池]
    F --> J{需要多核?}
    J -->|是| K[asyncio + ProcessPool]
    J -->|否| L[纯 asyncio]
```

---

### 💡 本章深度讲解

选择异步还是同步/多线程/多进程，关键看任务类型：IO 密集用异步，CPU 密集用多进程，混合场景用 asyncio + 执行器。

### 📝 本章精简总结

- IO 密集 → 异步。
- CPU 密集 → 多进程。
- 混合 → asyncio + executor。

### 🎯 梯度练习题

**基础题（⭐）**
1. 什么时候用多进程？
2. 什么时候用线程池？

**进阶题（⭐⭐）**
1. 混合场景怎么选？
2. 如何判断 IO 密集 vs CPU 密集？

**实战题（⭐⭐⭐）**
- 评估你的项目：哪些部分应该异步化？哪些应该多进程？

---

### 三十六、附录速查表

### 36.1 asyncio API 速查

| API | 用途 |
|---|---|
| `asyncio.run(main())` | 入口 |
| `async def` | 定义协程 |
| `await coro` | 等待协程 |
| `asyncio.create_task(coro)` | 创建任务 |
| `asyncio.gather(*cs)` | 并发组合 |
| `asyncio.wait(ts)` | 灵活等待 |
| `asyncio.as_completed(cs)` | 按完成顺序 |
| `asyncio.wait_for(c, timeout)` | 超时 |
| `asyncio.shield(c)` | 保护 |
| `asyncio.sleep(s)` | 异步睡眠 |
| `asyncio.Lock()` | 异步锁 |
| `asyncio.Semaphore(n)` | 信号量 |
| `asyncio.Event()` | 事件 |
| `asyncio.Queue()` | 队列 |
| `asyncio.to_thread(f, *a)` | 线程池 |
| `asyncio.TaskGroup()` | 结构化并发 |

### 36.2 错误异常速查

| 异常 | 含义 |
|---|---|
| `asyncio.TimeoutError` | 超时 |
| `asyncio.CancelledError` | 任务取消 |
| `RuntimeError` | 嵌套 run / 无运行 loop |
| `TypeError` | await 非可等待 |

---

> 💡 **全文总结**：本文 36 章系统讲解了 Python asyncio：从协程语法到事件循环原理，从并发 API 到同步原语，从异步 IO 到生产架构。掌握 asyncio 的关键是理解"单线程协作式调度"模型，以及"永远不要阻塞事件循环"这第一原则。

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]
- [[aiohttp-异步HTTP客户端]]
- [[Redis-异步客户端aioredis]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]
- [[Python-类型注解与mypy]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #高并发 #事件循环

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 三十七、并发模式完整实现

### 37.1 信号量限流器

```python
# 示例 37.1.1：生产级限流器
import asyncio, time

class RateLimiter:
    """滑动窗口限流器"""
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            self.calls = [t for t in self.calls if now - t < self.period]
            while len(self.calls) >= self.max_calls:
                sleep_time = self.calls[0] + self.period - now
                await asyncio.sleep(sleep_time)
                now = time.time()
                self.calls = [t for t in self.calls if now - t < self.period]
            self.calls.append(now)

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, *args):
        pass

# 用法：
# limiter = RateLimiter(100, 60)  # 每分钟100次
# async with limiter:
#     await call_api()
```

```python
# 示例 37.1.2：令牌桶限流器
class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate          # 每秒生成多少令牌
        self.capacity = capacity
        self.tokens = capacity
        self.last = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last = now
            if self.tokens < 1:
                await asyncio.sleep((1 - self.tokens) / self.rate)
                self.tokens = 0
            else:
                self.tokens -= 1
```

### 37.2 并发批处理器

```python
# 示例 37.2.1：批量并发处理
async def batch_process(items: list, worker, concurrency: int = 10):
    sem = asyncio.Semaphore(concurrency)
    async def safe_worker(item):
        async with sem:
            try:
                return await worker(item)
            except Exception as e:
                return {"error": str(e), "item": item}
    return await asyncio.gather(*[safe_worker(i) for i in items])

# 用法：
# results = await batch_process(urls, fetch, concurrency=20)
```

### 37.3 异步 Map/Reduce

```python
# 示例 37.3.1：异步 Map
async def async_map(func, items, concurrency=10):
    sem = asyncio.Semaphore(concurrency)
    async def mapped(item):
        async with sem:
            return await func(item)
    return await asyncio.gather(*[mapped(i) for i in items])

# 示例 37.3.2：异步 Reduce
async def async_reduce(func, async_iter, initial=None):
    result = initial
    async for item in async_iter:
        result = func(result, item)
    return result
```

### 37.4 超时组

```python
# 示例 37.4.1：带整体超时的并发组
async def gather_with_timeout(coros, timeout):
    try:
        return await asyncio.wait_for(
            asyncio.gather(*coros, return_exceptions=True),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        return [asyncio.TimeoutError() for _ in coros]
```

### 37.5 延迟结果

```python
# 示例 37.5.1：Future 作为延迟结果
async def deferred_result():
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    async def background():
        await asyncio.sleep(1)
        future.set_result(42)
    asyncio.create_task(background())
    return future

async def main():
    f = await deferred_result()
    result = await f
    print(result)  # 42
```

---

### 💡 本章深度讲解

并发模式是生产级异步应用的核心：限流器保护下游、批处理器控制并发、Map/Reduce 处理数据、超时组避免永久挂起。这些模式组合起来就是完整的异步并发框架。

### 📝 本章精简总结

- 限流器：滑动窗口/令牌桶。
- 批处理：Semaphore + gather。
- Map/Reduce：异步版本。
- 超时组：wait_for + gather。

### 🎯 梯度练习题

**基础题（⭐）**
1. 滑动窗口限流原理？
2. 令牌桶和漏桶的区别？

**进阶题（⭐⭐）**
1. 为什么限流器要加锁？
2. 批处理器的并发数怎么定？

**实战题（⭐⭐⭐）**
- 实现一个令牌桶限流器，支持异步使用，测试 100 个并发请求。

---

### 三十八、异步 HTTP 客户端深度

### 38.1 aiohttp 完整用法

```python
# 示例 38.1.1：完整 GET 请求
async def fetch_json(url, params=None, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
```

```python
# 示例 38.1.2：POST JSON
async def post_json(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            return await resp.json()
```

```python
# 示例 38.1.3：自定义超时和重试
async def fetch_with_retry(url, retries=3, timeout=10):
    timeout_cfg = aiohttp.ClientTimeout(total=timeout)
    for i in range(retries):
        try:
            async with aiohttp.ClientSession(timeout=timeout_cfg) as session:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if i == retries - 1:
                raise
            await asyncio.sleep(0.5 * (2 ** i))
```

```python
# 示例 38.1.4：自定义请求头和 Cookie
async def fetch_auth(url, token):
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            return await resp.json()
```

```python
# 示例 38.1.5：大文件流式下载
async def download_file(url, path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            with open(path, "wb") as f:
                async for chunk in resp.content.iter_chunked(8192):
                    f.write(chunk)
```

### 38.2 httpx 异步用法

```python
# 示例 38.2.1：httpx 异步客户端
import httpx

async def fetch_httpx(url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.json()
```

```python
# 示例 38.2.2：httpx 同步异步统一
# httpx 同时支持同步和异步，API 一致
client = httpx.Client()        # 同步
aclient = httpx.AsyncClient()  # 异步
```

### 38.3 并发爬虫框架

```python
# 示例 38.3.1：完整异步爬虫框架
class AsyncCrawler:
    def __init__(self, concurrency=10, timeout=10):
        self.sem = asyncio.Semaphore(concurrency)
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def fetch(self, url):
        async with self.sem:
            try:
                async with self.session.get(url) as resp:
                    return await resp.text()
            except Exception as e:
                return f"error: {e}"

    async def crawl(self, urls):
        return await asyncio.gather(*[self.fetch(u) for u in urls])

# 用法：
# async with AsyncCrawler(concurrency=20) as crawler:
#     results = await crawler.crawl(urls)
```

---

### 💡 本章深度讲解

异步 HTTP 是 asyncio 最大的应用场景。aiohttp 和 httpx 是两大库。连接池复用、超时配置、重试、流式下载是生产必备。

### 📝 本章精简总结

- aiohttp.ClientSession 复用。
- 超时/重试/流式。
- httpx 同步异步统一 API。
- 爬虫框架：Semaphore + gather。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么 ClientSession 要复用？
2. 流式下载的好处？

**进阶题（⭐⭐）**
1. aiohttp 和 httpx 怎么选？
2. 爬虫框架如何设计？

**实战题（⭐⭐⭐）**
- 写一个完整异步爬虫：20 并发、超时 10 秒、失败重试、结果存文件。

---

### 三十九、异步数据库深度

### 39.1 asyncpg 深度

```python
# 示例 39.1.1：asyncpg 连接池
import asyncpg

async def get_pool():
    return await asyncpg.create_pool(
        "postgresql://user:pass@localhost/db",
        min_size=5,
        max_size=20,
    )

async def query(pool, sql, *args):
    async with pool.acquire() as conn:
        return await conn.fetch(sql, *args)
```

```python
# 示例 39.1.2：asyncpg 事务
async def transfer(pool, from_id, to_id, amount):
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
                amount, from_id
            )
            await conn.execute(
                "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
                amount, to_id
            )
```

```python
# 示例 39.1.3：asyncpg 批量插入
async def bulk_insert(pool, rows):
    async with pool.acquire() as conn:
        await conn.executemany(
            "INSERT INTO users (name, email) VALUES ($1, $2)",
            rows,
        )
```

### 39.2 aiosqlite

```python
# 示例 39.2.1：aiosqlite 完整用法
import aiosqlite

async def query_users():
    async with aiosqlite.connect("test.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]
```

### 39.3 SQLAlchemy 异步

```python
# 示例 39.3.1：异步 CRUD
async def create_user(session, email, name):
    user = User(email=email, name=name)
    session.add(user)
    await session.flush()
    return user

async def get_user(session, uid):
    result = await session.execute(select(User).where(User.id == uid))
    return result.scalar_one_or_none()

async def list_users(session, page=1, size=20):
    result = await session.execute(
        select(User).offset((page-1)*size).limit(size)
    )
    return result.scalars().all()
```

---

### 💡 本章深度讲解

异步数据库是 Web 后端核心。asyncpg 性能最好，aiosqlite 轻量，SQLAlchemy 2.0 统一 API。连接池复用是关键优化。

### 📝 本章精简总结

- asyncpg 连接池。
- 事务 async with conn.transaction()。
- SQLAlchemy 2.0 await execute。
- 批量插入 executemany。

### 🎯 梯度练习题

**基础题（⭐）**
1. asyncpg 连接池怎么配？
2. 异步事务怎么写？

**进阶题（⭐⭐）**
1. 为什么 asyncpg 比 psycopg2 快？
2. 批量插入为什么比单条快？

**实战题（⭐⭐⭐）**
- 用 asyncpg 写一个用户服务：CRUD + 连接池 + 事务。

---

### 四十、异步消息队列

### 40.1 asyncio.Queue 生产消费

```python
# 示例 40.1.1：完整生产者消费者系统
async def producer(queue, name, items):
    for item in items:
        await queue.put(item)
        print(f"{name} 生产 {item}")
        await asyncio.sleep(0.1)
    await queue.put(None)  # 结束信号

async def consumer(queue, name):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        print(f"{name} 消费 {item}")
        await asyncio.sleep(0.2)
        queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=10)
    producers = [asyncio.create_task(producer(queue, f"P{i}", range(5))) for i in range(2)]
    consumers = [asyncio.create_task(consumer(queue, f"C{i}")) for i in range(3)]
    await asyncio.gather(*producers)
    await queue.join()
    for c in consumers:
        c.cancel()
```

### 40.2 延迟队列

```python
# 示例 40.2.1：延迟任务队列
class DelayedQueue:
    def __init__(self):
        self.queue = asyncio.PriorityQueue()

    async def put(self, delay, item):
        await self.queue.put((time.time() + delay, item))

    async def get(self):
        while True:
            ts, item = await self.queue.get()
            now = time.time()
            if now >= ts:
                return item
            await asyncio.sleep(ts - now)
            await self.queue.put((ts, item))
```

### 40.3 死信队列

```python
# 示例 40.3.1：失败消息进入死信队列
async def safe_consumer(queue, dlq, handler):
    while True:
        msg = await queue.get()
        try:
            await handler(msg)
        except Exception as e:
            await dlq.put({"msg": msg, "error": str(e)})
        finally:
            queue.task_done()
```

---

### 💡 本章深度讲解

asyncio.Queue 是异步生产者消费者的核心组件。延迟队列、死信队列是生产消息系统的常见模式。

### 📝 本章精简总结

- Queue：maxsize/put/get/task_done/join。
- 延迟队列：PriorityQueue + sleep。
- 死信队列：失败消息转移。

### 🎯 梯度练习题

**基础题（⭐）**
1. queue.task_done() 的作用？
2. queue.join() 等什么？

**进阶题（⭐⭐）**
1. 如何实现延迟队列？
2. 死信队列的作用？

**实战题（⭐⭐⭐）**
- 实现一个完整消息系统：生产者 + 3个消费者 + 死信队列。

---

### 四十一、异步缓存

### 41.1 内存缓存

```python
# 示例 41.1.1：异步 LRU 缓存
from collections import OrderedDict

class AsyncLRUCache:
    def __init__(self, maxsize=100):
        self.store = OrderedDict()
        self.maxsize = maxsize
        self.lock = asyncio.Lock()

    async def get(self, key):
        async with self.lock:
            if key in self.store:
                self.store.move_to_end(key)
                return self.store[key]
            return None

    async def set(self, key, value):
        async with self.lock:
            self.store[key] = value
            self.store.move_to_end(key)
            if len(self.store) > self.maxsize:
                self.store.popitem(last=False)
```

### 41.2 aioredis

```python
# 示例 41.2.1：aioredis 基本用法
import aioredis

async def cache_example():
    redis = await aioredis.from_url("redis://localhost")
    await redis.set("key", "value")
    val = await redis.get("key")
    await redis.close()
```

```python
# 示例 41.2.2：缓存装饰器
def redis_cache(ttl=60):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args):
            key = f"{func.__name__}:{args}"
            cached = await redis.get(key)
            if cached:
                return json.loads(cached)
            result = await func(*args)
            await redis.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

---

### 💡 本章深度讲解

异步缓存分两层：内存缓存（LRU）和分布式缓存（Redis）。内存缓存快但不共享，Redis 跨进程共享。

### 📝 本章精简总结

- 内存 LRU。
- aioredis。
- 缓存装饰器。

### 🎯 梯度练习题

**基础题（⭐）**
1. LRU 原理？
2. aioredis 和 redis-py 的区别？

**进阶题（⭐⭐）**
1. 为什么缓存要加锁？
2. 缓存穿透怎么处理？

**实战题（⭐⭐⭐）**
- 实现一个异步 TTL 缓存：LRU + 过期时间 + 统计。

---

### 四十二、异步文件处理

### 42.1 aiofiles 深度

```python
# 示例 42.1.1：异步读大文件
async def read_large_file(path):
    async with aiofiles.open(path) as f:
        while True:
            chunk = await f.read(8192)
            if not chunk:
                break
            process(chunk)
```

```python
# 示例 42.1.2：异步写文件
async def write_lines(path, lines):
    async with aiofiles.open(path, "w") as f:
        for line in lines:
            await f.write(line + "\n")
```

```python
# 示例 42.1.3：并发处理多个文件
async def process_files(paths):
    async def process_one(path):
        async with aiofiles.open(path) as f:
            return await f.read()
    return await asyncio.gather(*[process_one(p) for p in paths])
```

### 42.2 异步压缩

```python
# 示例 42.2.1：用 to_thread 包装 zlib
async def async_decompress(data):
    import zlib
    return await asyncio.to_thread(zlib.decompress, data)
```

---

### 💡 本章深度讲解

异步文件 IO 底层用线程池（因为操作系统没有成熟的异步文件 API）。aiofiles 是标准选择。

### 📝 本章精简总结

- aiofiles 异步读写。
- 分块读取大文件。
- to_thread 包装 CPU 密集处理。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么异步文件用线程池？
2. aiofiles 怎么读大文件？

**进阶题（⭐⭐）**
1. 为什么不用真正的异步文件 IO？
2. 如何并发处理文件？

**实战题（⭐⭐⭐）**
- 写一个异步日志分析器：并发读多个日志文件，统计错误数。

---

### 四十三、异步微服务架构

### 43.1 API 网关模式

```python
# 示例 43.1.1：异步 API 网关聚合
async def gateway_handler(request):
    uid = request.path_params["uid"]
    async with aiohttp.ClientSession() as session:
        # 并发调用三个后端
        user_task = asyncio.create_task(fetch_user(session, uid))
        orders_task = asyncio.create_task(fetch_orders(session, uid))
        stats_task = asyncio.create_task(fetch_stats(session, uid))

        user, orders, stats = await asyncio.gather(
            user_task, orders_task, stats_task,
            return_exceptions=True,
        )

    return {
        "user": user if not isinstance(user, Exception) else None,
        "orders": orders if not isinstance(orders, Exception) else [],
        "stats": stats if not isinstance(stats, Exception) else {},
    }
```

### 43.2 服务发现与熔断

```python
# 示例 43.2.1：带熔断的服务调用
class ResilientClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.circuit_open = False
        self.failures = 0
        self.opened_until = 0

    async def call(self, path, retries=3):
        if self.circuit_open and time.time() < self.opened_until:
            raise RuntimeError("熔断中")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}{path}") as r:
                    r.raise_for_status()
                    self.failures = 0
                    return await r.json()
        except Exception as e:
            self.failures += 1
            if self.failures >= 5:
                self.circuit_open = True
                self.opened_until = time.time() + 60
            raise
```

### 43.3 异步 RPC

```python
# 示例 43.3.1：异步 JSON-RPC 客户端
class JsonRpcClient:
    def __init__(self, url):
        self.url = url
        self.id = 0

    async def call(self, method, **params):
        self.id += 1
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": self.id}
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload) as r:
                result = await r.json()
                return result.get("result")
```

---

### 💡 本章深度讲解

异步微服务架构：API 网关并发聚合多个后端、熔断器保护下游、异步 RPC。这些是现代微服务的标准模式。

### 📝 本章精简总结

- API 网关：gather 聚合多后端。
- 熔断器：失败快速失败。
- 异步 RPC：JSON-RPC over HTTP。

### 🎯 梯度练习题

**基础题（⭐）**
1. API 网关为什么要并发？
2. 熔断器的作用？

**进阶题（⭐⭐）**
1. 熔断和重试的关系？
2. 如何实现服务降级？

**实战题（⭐⭐⭐）**
- 实现一个异步 API 网关：并发聚合 3 个后端，带熔断和降级。

---

### 四十四、异步实时通信

### 44.1 WebSocket 服务器

```python
# 示例 44.1.1：aiohttp WebSocket 聊天
from aiohttp import web

class ChatServer:
    def __init__(self):
        self.clients = set()

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.clients.add(ws)
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    for client in self.clients:
                        await client.send_str(msg.data)
        finally:
            self.clients.remove(ws)
        return ws

chat = ChatServer()
app = web.Application()
app.add_routes([web.get("/ws", chat.websocket_handler)])
# web.run_app(app)
```

### 44.2 SSE 服务器

```python
# 示例 44.2.1：Server-Sent Events
async def sse_handler(request):
    response = web.StreamResponse()
    response.headers["Content-Type"] = "text/event-stream"
    await response.prepare(request)
    for i in range(100):
        await response.write(f"data: {i}\n\n".encode())
        await asyncio.sleep(1)
    return response
```

### 44.3 WebSocket 客户端

```python
# 示例 44.3.1：aiohttp WebSocket 客户端
async def ws_client(url):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            await ws.send_str("hello")
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    print(msg.data)
```

---

### 💡 本章深度讲解

WebSocket 和 SSE 是异步实时通信的两大协议。WebSocket 双向，SSE 服务端单向推送。aiohttp 都支持。

### 📝 本章精简总结

- WebSocket：双向实时。
- SSE：服务端推送。
- aiohttp 支持两者。

### 🎯 梯度练习题

**基础题（⭐）**
1. WebSocket 和 HTTP 的区别？
2. SSE 是什么？

**进阶题（⭐⭐）**
1. WebSocket 适合什么场景？
2. 如何管理多个 WebSocket 连接？

**实战题（⭐⭐⭐）**
- 写一个 WebSocket 聊天室：多客户端广播。

---

### 四十五、异步任务调度

### 45.1 定时任务

```python
# 示例 45.1.1：异步定时器
class AsyncScheduler:
    def __init__(self):
        self.tasks = []

    async def every(self, seconds, coro):
        while True:
            await coro()
            await asyncio.sleep(seconds)

    def start(self, seconds, coro):
        task = asyncio.create_task(self.every(seconds, coro))
        self.tasks.append(task)
        return task

    async def stop_all(self):
        for t in self.tasks:
            t.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
```

### 45.2 Cron 任务

```python
# 示例 45.2.1：异步 cron（用 aiocron 库）
# pip install aiocron
import aiocron

# @aiocron.crontab("*/5 * * * *")
# async def every_5_min():
#     print("每5分钟")
```

### 45.3 延迟任务

```python
# 示例 45.3.1：延迟执行
async def later(delay, func, *args):
    await asyncio.sleep(delay)
    return await func(*args)
```

---

### 💡 本章深度讲解

异步任务调度：定时任务、cron、延迟任务。用 while True + sleep 实现简单调度，生产用 Celery/RQ。

### 📝 本章精简总结

- 定时：while True + sleep。
- cron：aiocron。
- 延迟：sleep + await。

### 🎯 梯度练习题

**基础题（⭐）**
1. 如何实现定时任务？
2. 如何优雅停止定时任务？

**进阶题（⭐⭐）**
1. 异步定时任务和系统 cron 的区别？
2. 如何处理任务执行失败？

**实战题（⭐⭐⭐）**
- 实现一个异步调度器：支持每 N 秒执行、延迟执行、优雅停止。

---

### 四十六、异步监控与可观测性

### 46.1 请求追踪

```python
# 示例 46.1.1：请求 ID 追踪
import contextvars, uuid

request_id = contextvars.ContextVar("request_id", default="-")

@app.middleware("http")
async def add_request_id(request, call_next):
    request_id.set(str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id.get()
    return response
```

### 46.2 指标收集

```python
# 示例 46.2.1：异步指标
from collections import defaultdict
import time

metrics = defaultdict(list)

def track(name):
    def decorator(func):
        async def wrapper(*a, **kw):
            t0 = time.perf_counter()
            try:
                return await func(*a, **kw)
            finally:
                metrics[name].append(time.perf_counter() - t0)
        return wrapper
    return decorator
```

### 46.3 健康检查

```python
# 示例 46.3.1：健康检查端点
@app.get("/health")
async def health():
    checks = {}
    # 检查数据库
    try:
        await asyncio.wait_for(ping_db(), timeout=2)
        checks["db"] = "ok"
    except Exception:
        checks["db"] = "fail"
    # 检查 Redis
    try:
        await asyncio.wait_for(redis.ping(), timeout=2)
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "fail"
    status = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return {"status": status, "checks": checks}
```

---

### 💡 本章深度讲解

生产异步应用需要可观测性：请求追踪、指标、健康检查。这些是从 demo 到生产的必要步骤。

### 📝 本章精简总结

- 请求 ID 追踪。
- 指标收集。
- 健康检查。

### 🎯 梯度练习题

**基础题（⭐）**
1. 请求 ID 有什么用？
2. 健康检查检查什么？

**进阶题（⭐⭐）**
1. 如何用 contextvars 做链路追踪？
2. 如何暴露 Prometheus 指标？

**实战题（⭐⭐⭐）**
- 为你的异步应用添加：请求 ID 中间件、/health 端点、延迟指标。

---

### 四十七、异步安全

### 47.1 并发安全

```python
# 示例 47.1.1：共享状态加锁
counter = 0
lock = asyncio.Lock()

async def safe_increment():
    global counter
    async with lock:
        current = counter
        await asyncio.sleep(0)
        counter = current + 1
```

### 47.2 资源限制

```python
# 示例 47.2.1：限制并发防 DoS
@app.middleware("http")
async def limit_concurrency(request, call_next):
    sem = request.app.state.semaphore
    async with sem:
        return await call_next(request)
```

### 47.3 超时防护

```python
# 示例 47.3.1：全局超时
@app.middleware("http")
async def timeout_middleware(request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=30)
    except asyncio.TimeoutError:
        return JSONResponse({"error": "timeout"}, status_code=504)
```

---

### 💡 本章深度讲解

异步安全：并发安全用锁、资源限制用 Semaphore、超时防护用 wait_for。这些防止 DoS 和资源耗尽。

### 📝 本章精简总结

- 共享状态加锁。
- Semaphore 限并发。
- wait_for 全局超时。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步为什么还需要锁？
2. 如何防 DoS？

**进阶题（⭐⭐）**
1. 如何全局限制并发？
2. 超时中间件怎么写？

**实战题（⭐⭐⭐）**
- 为 FastAPI 应用添加：并发限制 + 全局超时 + 请求大小限制。

---

### 四十八、异步测试深度

### 48.1 pytest-asyncio 完整用法

```python
# 示例 48.1.1：测试异步函数
import pytest

@pytest.mark.asyncio
async def test_fetch_user():
    user = await get_user(1)
    assert user["id"] == 1
```

```python
# 示例 48.1.2：异步 fixture
@pytest_asyncio.fixture
async def db():
    db = await create_test_db()
    yield db
    await db.close()

@pytest.mark.asyncio
async def test_with_db(db):
    await db.execute("INSERT INTO users VALUES (1, 'test')")
```

```python
# 示例 48.1.3：测试异常
@pytest.mark.asyncio
async def test_raises():
    with pytest.raises(ValueError):
        await failing_func()
```

```python
# 示例 48.1.4：测试超时
@pytest.mark.asyncio
async def test_timeout():
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_func(), timeout=0.1)
```

### 48.2 mock 异步

```python
# 示例 48.2.1：mock 协程函数
from unittest.mock import patch, AsyncMock

async def test_api():
    with patch("module.external_api", new=AsyncMock(return_value={"ok": 1})):
        result = await business_logic()
        assert result == {"ok": 1}
```

```python
# 示例 48.2.2：AsyncMock
mock = AsyncMock(return_value=42)
result = await mock()
assert result == 42
mock.assert_called_once()
```

---

### 💡 本章深度讲解

测试异步代码：pytest-asyncio + AsyncMock。异步 fixture yield。测试超时和异常。

### 📝 本章精简总结

- @pytest.mark.asyncio。
- 异步 fixture yield。
- AsyncMock mock 协程。
- 测试超时。

### 🎯 梯度练习题

**基础题（⭐）**
1. 如何测试异步函数？
2. AsyncMock 的作用？

**进阶题（⭐⭐）**
1. 如何 mock 异步依赖？
2. 如何测试异步异常？

**实战题（⭐⭐⭐）**
- 为你的异步 API 写完整测试：正常/异常/超时/mock 外部依赖。

---

### 四十九、异步性能剖析深度

### 49.1 性能指标

```python
# 示例 49.1.1：性能计时器
import time, statistics

class PerfTimer:
    def __init__(self):
        self.samples = []
    async def time(self, coro):
        t0 = time.perf_counter()
        try:
            return await coro
        finally:
            self.samples.append(time.perf_counter() - t0)
    def report(self):
        if not self.samples:
            return
        print(f"n={len(self.samples)} avg={statistics.mean(self.samples)*1000:.1f}ms "
              f"p50={statistics.quantiles(self.samples, n=100)[49]*1000:.1f}ms")
```

### 49.2 找瓶颈

```python
# 示例 49.2.1：哪个协程最慢
async def profile(coros):
    results = await asyncio.gather(*[time_coro(c) for c in coros], return_exceptions=True)
    return sorted(zip(coros, results), key=lambda x: x[1], reverse=True)
```

### 49.3 优化清单

```python
# 优化清单：
# 1. 消除阻塞调用
# 2. 连接池复用
# 3. 合理并发数（Semaphore）
# 4. 批量操作
# 5. uvloop
# 6. 减少 await 点
# 7. 异步日志
# 8. 进程池 CPU 密集
```

---

### 💡 本章深度讲解

性能剖析：测量耗时、找瓶颈、优化。最大优化是消除阻塞调用和复用连接。

### 📝 本章精简总结

- 测量耗时。
- 找瓶颈。
- 优化清单。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步应用最大性能瓶颈？
2. 如何测量协程耗时？

**进阶题（⭐⭐）**
1. uvloop 为什么快？
2. 并发数怎么定？

**实战题（⭐⭐⭐）**
- 用 perf 工具分析你的异步应用，找到最慢的协程并优化。

---

### 五十、异步反模式深度剖析

### 50.1 反模式详解

```python
# 示例 50.1.1：反模式 1：阻塞调用
async def bad():
    time.sleep(1)  # ❌ 阻塞事件循环

async def good():
    await asyncio.sleep(1)  # ✅
```

```python
# 示例 50.1.2：反模式 2：不保存 Task 引用
async def bad():
    asyncio.create_task(background())  # ❌ 可能被GC

background_tasks = set()
async def good():
    t = asyncio.create_task(background())
    background_tasks.add(t)
    t.add_done_callback(background_tasks.discard)
```

```python
# 示例 50.1.3：反模式 3：嵌套 run
async def bad():
    asyncio.run(other())  # ❌ RuntimeError

async def good():
    await other()  # ✅
```

```python
# 示例 50.1.4：反模式 4：while True 无 await
async def bad():
    while True:
        do_work()  # ❌ 卡死 loop

async def good():
    while True:
        do_work()
        await asyncio.sleep(0)  # ✅ 让出控制权
```

```python
# 示例 50.1.5：反模式 5：每次新建 Session
async def bad(url):
    async with aiohttp.ClientSession() as s:  # ❌ 每次新建
        return await s.get(url)

# ✅ 全局复用
session = aiohttp.ClientSession()
```

```python
# 示例 50.1.6：反模式 6：不设超时
async def bad():
    await fetch(url)  # ❌ 可能永久挂起

async def good():
    await asyncio.wait_for(fetch(url), timeout=10)  # ✅
```

```python
# 示例 50.1.7：反模式 7：同步 with 包异步资源
async def bad():
    with AsyncResource():  # ❌ 应该 async with
        ...

async def good():
    async with AsyncResource():  # ✅
        ...
```

```python
# 示例 50.1.8：反模式 8：threading.local 失效
ctx = threading.local()
async def bad():
    ctx.user = "x"  # ❌ 所有协程共享

ctx_var = contextvars.ContextVar("user")
async def good():
    ctx_var.set("x")  # ✅ 每个协程独立
```

---

### 💡 本章深度讲解

8 大反模式覆盖了异步编程最常见的错误。核心原则：永远不要阻塞事件循环、保持任务引用、不嵌套 run、用 async with、用 contextvars。

### 📝 本章精简总结

- 不阻塞 loop。
- 保持任务引用。
- 不嵌套 run。
- async with。
- contextvars。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么 time.sleep 阻塞？
2. 为什么 Task 要保持引用？

**进阶题（⭐⭐）**
1. 为什么 threading.local 失效？
2. 如何检测阻塞调用？

**实战题（⭐⭐⭐）**
- 审查你的异步代码，对照 8 大反模式逐一修复。

---

### 五十一、异步 TCP/UDP 服务器深度

### 51.1 异步 TCP 服务器完整实现

```python
# 示例 51.1.1：完整异步 TCP 服务器
import asyncio

class EchoServer:
    def __init__(self, host="0.0.0.0", port=8888):
        self.host = host
        self.port = port
        self.server = None

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info("peername")
        print(f"客户端连接: {addr}")
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                message = data.decode().strip()
                print(f"收到 {addr}: {message}")
                writer.write(f"echo: {message}\n".encode())
                await writer.drain()
        except asyncio.CancelledError:
            pass
        finally:
            writer.close()
            await writer.wait_closed()
            print(f"客户端断开: {addr}")

    async def start(self):
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        addr = self.server.sockets[0].getsockname()
        print(f"服务器启动: {addr}")
        async with self.server:
            await self.server.serve_forever()

# asyncio.run(EchoServer().start())
```

### 51.2 异步 UDP

```python
# 示例 51.2.1：异步 UDP 服务器
class EchoUDPProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport
    def datagram_received(self, data, addr):
        print(f"UDP 收到 {addr}: {data}")
        self.transport.sendto(data, addr)

# loop = asyncio.get_event_loop()
# listen = loop.create_datagram_endpoint(
#     EchoUDPProtocol, local_addr=("0.0.0.0", 9999)
# )
# loop.run_until_complete(listen)
```

### 51.3 异步 TLS

```python
# 示例 51.3.1：TLS 上下文
import ssl

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain("cert.pem", "key.pem")

# asyncio.start_server(..., ssl=ssl_context)
```

---

### 💡 本章深度讲解

TCP 服务器是异步最经典的应用。单线程处理数千连接，每个连接一个协程。UDP 和 TLS 是补充。

### 📝 本章精简总结

- start_server TCP 服务器。
- DatagramProtocol UDP。
- ssl_context TLS。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么异步适合 TCP 服务器？
2. drain() 的作用？

**进阶题（⭐⭐）**
1. 如何处理多个连接？
2. 如何优雅关闭服务器？

**实战题（⭐⭐⭐）**
- 写一个异步 TCP 聊天服务器：多客户端广播。

---

### 五十二、异步进程间通信

### 52.1 异步子进程管理

```python
# 示例 52.1.1：管理多个子进程
async def run_multiple(commands):
    async def run_one(cmd):
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return cmd, proc.returncode, stdout.decode()
    return await asyncio.gather(*[run_one(c) for c in commands])
```

### 52.2 子进程流式输出

```python
# 示例 52.2.1：实时读子进程输出
async def stream_command(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        print(line.decode().strip())
    await proc.wait()
```

---

### 💡 本章深度讲解

异步子进程管理：并发运行多个命令、流式读输出。这是 DevOps 工具的基础。

### 📝 本章精简总结

- create_subprocess_shell。
- communicate() 收集输出。
- readline() 流式读。

### 🎯 梯度练习题

**基础题（⭐）**
1. 如何异步运行命令？
2. 如何实时读输出？

**进阶题（⭐⭐）**
1. 如何并发运行多个命令？
2. 如何处理子进程错误？

**实战题（⭐⭐⭐）**
- 写一个异步部署脚本：并发执行多个 shell 命令，收集输出。

---

### 五十三、异步序列化

### 53.1 异步 JSON 处理

```python
# 示例 53.1.1：大数据集异步序列化
import json

async def async_dump(obj, path):
    async with aiofiles.open(path, "w") as f:
        await f.write(json.dumps(obj, ensure_ascii=False))
```

### 53.2 异步 CSV

```python
# 示例 53.2.1：异步写 CSV
import csv, io

async def write_csv(path, rows, headers):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    async with aiofiles.open(path, "w") as f:
        await f.write(output.getvalue())
```

---

### 💡 本章深度讲解

序列化本身是 CPU 密集，异步版主要是 IO 部分异步。CPU 密集用 to_thread。

### 📝 本章精简总结

- JSON/CSV 异步写。
- CPU 密集用 to_thread。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么序列化要异步？
2. 大数据集怎么异步处理？

**进阶题（⭐⭐）**
1. 序列化 CPU 密集怎么处理？
2. 流式 JSON？

**实战题（⭐⭐⭐）**
- 写一个异步数据导出器：从数据库读，序列化为 CSV，写文件。

---

### 五十四、异步机器学习推理

### 54.1 异步推理服务

```python
# 示例 54.1.1：异步 ML 推理
class AsyncModel:
    def __init__(self, model_path):
        self.model = None
    async def load(self):
        # 加载模型是 CPU 密集，用 to_thread
        self.model = await asyncio.to_thread(self._load_model)
    def _load_model(self):
        return load_model_from_disk()
    async def predict(self, data):
        # 推理是 CPU 密集
        return await asyncio.to_thread(self._predict, data)
    def _predict(self, data):
        return self.model(data)
```

### 54.2 批量推理

```python
# 示例 54.2.1：异步批量推理
async def batch_predict(model, items, batch_size=32):
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        result = await model.predict(batch)
        results.extend(result)
    return results
```

---

### 💡 本章深度讲解

ML 推理是 CPU 密集，异步版用 to_thread 包装。批量推理提高吞吐量。

### 📝 本章精简总结

- to_thread 包装推理。
- 批量推理。
- 模型加载异步化。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么 ML 推理要用 to_thread？
2. 批量推理的好处？

**进阶题（⭐⭐）**
1. 如何异步加载模型？
2. 推理服务怎么设计？

**实战题（⭐⭐⭐）**
- 写一个异步推理服务：FastAPI + to_thread + 批量处理。

---

### 五十五、异步最佳实践清单

### 55.1 代码规范

```python
# ✅ 异步代码规范

# 1. 入口用 asyncio.run
async def main():
    await do_work()

if __name__ == "__main__":
    asyncio.run(main())

# 2. 协程函数加类型注解
async def fetch(url: str) -> dict:
    ...

# 3. 用 TaskGroup 管理并发
async with asyncio.TaskGroup() as tg:
    tg.create_task(work())

# 4. Semaphore 限并发
sem = asyncio.Semaphore(20)
async def limited():
    async with sem:
        await work()

# 5. 超时
await asyncio.wait_for(coro, timeout=10)

# 6. 异常显式处理
try:
    await coro()
except Exception:
    handle()
```

### 55.2 性能清单

```python
# 性能清单：
# 1. uvloop
# 2. 连接池复用
# 3. Semaphore 合理并发数
# 4. 批量操作
# 5. 异步日志
# 6. to_thread CPU 密集
# 7. 减少 await 点
# 8. 流式处理大结果
```

### 55.3 可靠性清单

```python
# 可靠性清单：
# 1. 所有外部调用设超时
# 2. 重试 + 指数退避
# 3. 熔断器
# 4. 降级策略
# 5. 优雅关闭
# 6. 健康检查
# 7. 监控指标
# 8. 请求追踪
```

---

### 💡 本章深度讲解

最佳实践清单是从无数生产事故中总结出来的。照做就能避免 90% 的异步坑。

### 📝 本章精简总结

- 代码规范：类型/TaskGroup/Semaphore/超时/异常。
- 性能：uvloop/连接池/批量。
- 可靠性：超时/重试/熔断/降级。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步代码最重要的规范？
2. 可靠性清单？

**进阶题（⭐⭐）**
1. 为什么所有外部调用要设超时？
2. 优雅关闭怎么做？

**实战题（⭐⭐⭐）**
- 对照清单审查你的异步项目，列出缺失项并补齐。

---

### 五十六、异步学习路径

### 56.1 学习阶段

```mermaid
graph LR
    A[Python基础] --> B[async/await语法]
    B --> C[事件循环原理]
    C --> D[Task/Future]
    D --> E[并发API gather/wait]
    E --> F[异步IO aiohttp]
    F --> G[同步原语]
    G --> H[混合线程/进程]
    H --> I[生产架构]
    I --> J[TaskGroup结构化]
```

### 56.2 推荐顺序

1. **第一周**：async/await 语法 + 第一个协程。
2. **第二周**：事件循环 + Task + gather。
3. **第三周**：aiohttp + 异步爬虫。
4. **第四周**：同步原语 + Queue。
5. **第五周**：SQLAlchemy 异步 + FastAPI。
6. **第六周**：TaskGroup + 调试 + 性能优化。

### 56.3 项目实战

1. 异步爬虫
2. 异步 Web API
3. 异步消息消费者
4. 实时 WebSocket 应用

---

### 💡 本章深度讲解

学习异步需要循序渐进：语法 → 原理 → IO → 原语 → 混合 → 生产。每个阶段配合项目实战。

### 📝 本章精简总结

- 语法 → 原理 → IO → 原语 → 生产。
- 每个阶段配项目。

### 🎯 梯度练习题

**基础题（⭐）**
1. 学习 asyncio 的第一步？
2. 哪个阶段最难？

**进阶题（⭐⭐）**
1. 为什么要先学原理再学框架？
2. 如何衡量学习进度？

**实战题（⭐⭐⭐）**
- 按学习路径规划你的异步学习计划。

---

### 五十七、异步 FAQ

### 57.1 高频问题

**Q1：asyncio 是多线程吗？**
不是。asyncio 是单线程协程，协作式调度。

**Q2：asyncio 能利用多核吗？**
默认不能（单线程）。CPU 密集用 ProcessPoolExecutor 或多进程部署。

**Q3：为什么协程不需要锁？**
单线程，没有真正的并发写入。但在 await 点之间可能有其他协程修改状态，所以仍需要异步锁。

**Q4：asyncio 和 Node.js 区别？**
模型类似（单线程+事件循环）。Python 用协程语法，JS 用 Promise/async。

**Q5：asyncio 会替代线程吗？**
IO 密集场景会。CPU 密集仍需多进程。混合场景用 asyncio + to_thread。

**Q6：为什么我的异步代码比同步还慢？**
可能是 CPU 密集任务、阻塞调用、并发数太少。

**Q7：如何调试异步死锁？**
debug 模式 + all_tasks + faulthandler + py-spy。

**Q8：asyncio.run 为什么不能嵌套？**
一个线程只能有一个运行的事件循环。嵌套会冲突。

**Q9：Task 被 GC 回收会怎样？**
任务静默消失，不会执行。必须保持引用。

**Q10：如何优雅关闭事件循环？**
停止接受新任务 → cancel 所有任务 → await → 关闭 loop。

---

### 💡 本章深度讲解

FAQ 覆盖了异步编程最常见的疑问。理解这些问题背后的原理，就能避免很多坑。

### 📝 本章精简总结

- 单线程协程。
- 不利用多核（CPU 密集用进程）。
- Task 保持引用。
- run 不嵌套。

### 🎯 梯度练习题

**基础题（⭐）**
1. asyncio 是多线程吗？
2. 为什么 run 不能嵌套？

**进阶题（⭐⭐）**
1. 为什么异步代码可能更慢？
2. 如何调试死锁？

**实战题（⭐⭐⭐）**
- 回答所有 FAQ，对照你的理解。

---

### 五十八、异步术语表

| 术语 | 英文 | 说明 |
|---|---|---|
| 协程 | Coroutine | async def 定义的函数 |
| 事件循环 | Event Loop | 调度协程的核心引擎 |
| 任务 | Task | 协程的并发封装 |
| 未来 | Future | 异步结果占位符 |
| 可等待 | Awaitable | 能 await 的对象 |
| 调度 | Scheduling | 事件循环选择执行哪个协程 |
| 挂起 | Suspend | await 让出控制权 |
| 恢复 | Resume | 事件循环继续执行协程 |
| 阻塞 | Blocking | 调用后等待不返回 |
| 并发 | Concurrency | 任务交替执行 |
| 并行 | Parallelism | 真正同时执行 |
| IO多路复用 | IO Multiplexing | epoll/kqueue |
| 协程切换 | Context Switch | 用户态切换 |
| 结构化并发 | Structured Concurrency | TaskGroup |

---

### 💡 本章深度讲解

术语表帮助你快速查阅。掌握这些术语就能和其他异步开发者顺畅交流。

### 📝 本章精简总结

- 核心术语：协程/事件循环/Task/Future/awaitable。

### 🎯 梯度练习题

**基础题（⭐）**
1. 什么是 awaitable？
2. epoll 是什么？

**进阶题（⭐⭐）**
1. 结构化并发是什么？
2. 协程切换和线程切换的区别？

**实战题（⭐⭐⭐）**
- 用术语表向同事解释 asyncio。

---

### 五十九、总结与回顾

本文共 59 章，系统讲解了 Python asyncio 异步编程：

1. **基础**：async/await 语法、协程、事件循环、Task/Future。
2. **并发**：gather/wait/as_completed/wait_for/shield。
3. **IO**：TCP/HTTP/文件/数据库/WebSocket。
4. **原语**：Lock/Semaphore/Event/Queue/Condition。
5. **混合**：to_thread/run_in_executor/进程池。
6. **生态**：aiohttp/asyncpg/FastAPI/uvloop。
7. **生产**：架构/监控/测试/调试/性能。
8. **新特性**：TaskGroup/ExceptionGroup/except*。
9. **坑点**：30+ 常见错误。
10. **面试**：20+ 高频考点。

掌握 asyncio 是现代 Python 后端开发的必备技能。🚀

---

> 💡 **最终总结**：asyncio 的核心智慧是「单线程协程 + 事件循环 + IO多路复用」。理解这个模型，理解"永远不要阻塞事件循环"这第一原则，你就掌握了异步编程的精髓。从语法到生产，本文 59 章是完整的学习路径。

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[Python-语法基础与数据结构]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]
- [[aiohttp-异步HTTP]]
- [[asyncpg-异步PostgreSQL]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]
- [[Python-类型注解与mypy]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #事件循环 #高并发 #aiohttp

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 六十、异步 HTTP 客户端高级用法

### 60.1 自定义中间件

```python
# 示例 60.1.1：aiohttp 自定义中间件
class LoggingMiddleware:
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    async def __aexit__(self, *args):
        await self.session.close()
    async def request(self, method, url, **kw):
        print(f"{method} {url}")
        async with self.session.request(method, url, **kw) as r:
            print(f"  -> {r.status}")
            return await r.json()
```

### 60.2 连接池调优

```python
# 示例 60.2.1：生产级连接池配置
connector = aiohttp.TCPConnector(
    limit=100,              # 总连接数
    limit_per_host=20,       # 每主机
    ttl_dns_cache=300,       # DNS 缓存秒数
    use_dns_cache=True,
    keepalive_timeout=30,    # 长连接保持
    enable_cleanup_closed=True,
)
timeout = aiohttp.ClientTimeout(
    total=30,                # 总超时
    connect=10,              # 连接超时
    sock_read=20,            # 读超时
)
session = aiohttp.ClientSession(connector=connector, timeout=timeout)
```

### 60.3 重试中间件

```python
# 示例 60.3.1：自动重试装饰器
async def fetch_with_retry(url, retries=3, backoff=2):
    delay = 1
    for i in range(retries):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url) as r:
                    r.raise_for_status()
                    return await r.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if i == retries - 1:
                raise
            await asyncio.sleep(delay)
            delay *= backoff
```

### 60.4 并发限速

```python
# 示例 60.4.1：全局限速
class GlobalRateLimiter:
    def __init__(self, calls_per_second=10):
        self.sem = asyncio.Semaphore(calls_per_second)
        self.calls_per_second = calls_per_second
    async def acquire(self):
        await self.sem.acquire()
        asyncio.get_event_loop().call_later(1, self.sem.release)
```

---

### 💡 本章深度讲解

HTTP 客户端高级用法：中间件、连接池调优、重试、限速。这些是生产级 HTTP 客户端的必备特性。

### 📝 本章精简总结

- 连接池 limit/keepalive。
- 重试指数退避。
- 全局限速。

### 🎯 梯度练习题

**基础题（⭐）**
1. limit_per_host 的作用？
2. keepalive 的好处？

**进阶题（⭐⭐）**
1. 为什么要全局限速？
2. 如何实现自动重试？

**实战题（⭐⭐⭐）**
- 写一个生产级 HTTP 客户端：连接池+重试+限速+日志。

---

### 六十一、异步数据库高级用法

### 61.1 连接池监控

```python
# 示例 61.1.1：监控连接池
async def monitor_pool(pool):
    while True:
        print(f"已用: {pool.size - pool.freesize}, 空闲: {pool.freesize}")
        await asyncio.sleep(5)
```

### 61.2 读写分离

```python
# 示例 61.2.1：异步读写分离
class ReadWriteDB:
    def __init__(self, write_dsn, read_dsn):
        self.write_pool = None
        self.read_pool = None
    async def init(self):
        self.write_pool = await asyncpg.create_pool(write_dsn)
        self.read_pool = await asyncpg.create_pool(read_dsn)
    async def query(self, sql, *args):
        async with self.read_pool.acquire() as conn:
            return await conn.fetch(sql, *args)
    async def execute(self, sql, *args):
        async with self.write_pool.acquire() as conn:
            return await conn.execute(sql, *args)
```

### 61.3 批量操作优化

```python
# 示例 61.3.1：批量插入
async def bulk_insert(pool, rows):
    async with pool.acquire() as conn:
        await conn.copy_records_to_table("users", records=rows)
```

---

### 💡 本章深度讲解

数据库高级：连接池监控、读写分离、批量操作。这些是大规模数据服务的必备。

### 📝 本章精简总结

- 连接池监控。
- 读写分离。
- copy_records_to_table 批量。

### 🎯 梯度练习题

**基础题（⭐）**
1. 读写分离的好处？
2. 批量插入为什么快？

**进阶题（⭐⭐）**
1. 如何监控连接池？
2. copy_records_to_table 原理？

**实战题（⭐⭐⭐）**
- 实现读写分离数据库客户端。

---

### 六十二、异步缓存高级

### 62.1 缓存 aside 模式

```python
# 示例 62.1.1：缓存 aside
async def get_user_cached(uid):
    key = f"user:{uid}"
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)
    user = await db.query_user(uid)
    await redis.setex(key, 300, json.dumps(user))
    return user
```

### 62.2 缓存穿透

```python
# 示例 62.2.1：空值缓存
async def get_user_safe(uid):
    key = f"user:{uid}"
    cached = await redis.get(key)
    if cached == b"null":
        return None
    if cached:
        return json.loads(cached)
    user = await db.query_user(uid)
    if user is None:
        await redis.setex(key, 60, "null")  # 缓存空值防穿透
    else:
        await redis.setex(key, 300, json.dumps(user))
    return user
```

### 62.3 缓存击穿

```python
# 示例 62.3.1：互斥锁防击穿
async def get_user_mutex(uid):
    key = f"user:{uid}"
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)
    lock_key = f"lock:{key}"
    if await redis.set(lock_key, "1", nx=True, ex=10):
        try:
            user = await db.query_user(uid)
            await redis.setex(key, 300, json.dumps(user))
            return user
        finally:
            await redis.delete(lock_key)
    else:
        await asyncio.sleep(0.1)
        return await get_user_mutex(uid)
```

---

### 💡 本章深度讲解

缓存三大问题：穿透、击穿、雪崩。本文给出了空值缓存、互斥锁、随机 TTL 等解决方案。

### 📝 本章精简总结

- aside 模式。
- 空值缓存防穿透。
- 互斥锁防击穿。
- 随机 TTL 防雪崩。

### 🎯 梯度练习题

**基础题（⭐）**
1. 缓存穿透是什么？
2. 缓存击穿和雪崩的区别？

**进阶题（⭐⭐）**
1. 如何防穿透？
2. 如何防击穿？

**实战题（⭐⭐⭐）**
- 实现完整缓存层：aside + 防穿透 + 防击穿 + 防雪崩。

---

### 六十三、异步限流与配额

### 63.1 多级限流

```python
# 示例 63.1.1：用户级 + 全局级限流
class MultiRateLimit:
    def __init__(self, global_limit, per_user_limit):
        self.global_sem = asyncio.Semaphore(global_limit)
        self.user_sems = {}
        self.per_user_limit = per_user_limit
    async def acquire(self, user_id):
        user_sem = self.user_sems.setdefault(
            user_id, asyncio.Semaphore(self.per_user_limit)
        )
        async with self.global_sem:
            async with user_sem:
                yield
```

### 63.2 配额管理

```python
# 示例 63.2.1：每日配额
class Quota:
    def __init__(self, redis):
        self.redis = redis
    async def check(self, user_id, quota=100):
        key = f"quota:{user_id}:{date.today()}"
        used = await self.redis.incr(key)
        if used == 1:
            await self.redis.expire(key, 86400)
        return used <= quota
```

---

### 💡 本章深度讲解

限流和配额是 API 服务的保护机制。多级限流（全局+用户级）和配额（每日限制）是常见模式。

### 📝 本章精简总结

- 多级限流。
- 配额管理。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么要限流？
2. 配额和限流的区别？

**进阶题（⭐⭐）**
1. 如何实现多级限流？
2. 配额怎么重置？

**实战题（⭐⭐⭐）**
- 实现 API 限流：全局 1000 QPS，每用户 100 QPS。

---

### 六十四、异步错误追踪

### 64.1 错误聚合

```python
# 示例 64.1.1：错误统计
error_count = defaultdict(int)

async def track_error(func):
    try:
        return await func()
    except Exception as e:
        error_count[type(e).__name__] += 1
        raise
```

### 64.2 错误上报

```python
# 示例 64.2.1：异步上报 Sentry
import sentry_sdk

async def capture_exception(e):
    await asyncio.to_thread(sentry_sdk.capture_exception, e)
```

---

### 💡 本章深度讲解

错误追踪是生产必备：统计错误类型、上报到 Sentry。

### 📝 本章精简总结

- 错误统计。
- 错误上报。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么要统计错误？
2. Sentry 集成？

**进阶题（⭐⭐）**
1. 如何聚合错误？
2. 异步上报为什么用 to_thread？

**实战题（⭐⭐⭐）**
- 为异步应用集成 Sentry 错误上报。

---

### 六十五、异步健康检查与优雅关闭

### 65.1 完整优雅关闭

```python
# 示例 65.1.1：完整优雅关闭
import signal

async def graceful_shutdown(app):
    # 1. 停止接受新连接
    app.state.running = False
    # 2. 关闭数据库
    await app.state.db.close()
    # 3. 关闭 Redis
    await app.state.redis.close()
    # 4. 取消所有后台任务
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

async def setup_signal_handlers(app):
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, lambda: asyncio.create_task(graceful_shutdown(app))
        )
```

### 65.2 健康检查

```python
# 示例 65.2.1：完整健康检查
@app.get("/health")
async def health():
    checks = {}
    # DB
    try:
        await asyncio.wait_for(db_ping(), timeout=2)
        checks["db"] = "ok"
    except:
        checks["db"] = "fail"
    # Redis
    try:
        await asyncio.wait_for(redis.ping(), timeout=2)
        checks["redis"] = "ok"
    except:
        checks["redis"] = "fail"
    ok = all(v == "ok" for v in checks.values())
    return JSONResponse(
        {"status": "ok" if ok else "degraded", "checks": checks},
        status_code=200 if ok else 503,
    )
```

---

### 💡 本章深度讲解

优雅关闭和健康检查是生产部署的标准要求。确保 Kubernetes/负载均衡正确路由流量。

### 📝 本章精简总结

- 优雅关闭：停止连接→关资源→取消任务。
- 健康检查：DB/Redis 检查。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么要优雅关闭？
2. 健康检查检查什么？

**进阶题（⭐⭐）**
1. 如何实现优雅关闭？
2. 健康检查返回什么状态码？

**实战题（⭐⭐⭐）**
- 为你的应用实现完整优雅关闭和健康检查。

---

### 六十六、异步配置管理

### 66.1 Pydantic Settings

```python
# 示例 66.1.1：pydantic-settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    LOG_LEVEL: str = "INFO"
    MAX_CONCURRENCY: int = 20
    API_TIMEOUT: float = 10.0
    class Config:
        env_file = ".env"

settings = Settings()
```

### 66.2 热更新配置

```python
# 示例 66.2.1：异步配置热更新
class HotConfig:
    def __init__(self):
        self._config = {}
        self._observers = []
    async def watch(self):
        while True:
            await asyncio.sleep(10)
            new_config = await self.load()
            if new_config != self._config:
                self._config = new_config
                for obs in self._observers:
                    await obs(new_config)
```

---

### 💡 本章深度讲解

配置管理：pydantic-settings 从环境变量加载。热更新是进阶。

### 📝 本章精简总结

- pydantic-settings。
- 环境变量/.env。
- 热更新。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么用 pydantic-settings？
2. 环境变量怎么加载？

**进阶题（⭐⭐）**
1. 如何热更新配置？
2. 配置变更如何通知？

**实战题（⭐⭐⭐）**
- 为你的应用配置 pydantic-settings + .env。

---

### 六十七、异步日志

### 67.1 结构化日志

```python
# 示例 67.1.1：JSON 结构化日志
import logging, json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "ts": record.created,
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "trace_id": getattr(record, "trace_id", "-"),
        })
```

### 67.2 异步日志队列

```python
# 示例 67.2.1：QueuedHandler
import logging
from logging.handlers import QueueHandler, QueueListener
import queue

log_queue = queue.Queue(-1)
handler = logging.StreamHandler()
listener = QueueListener(log_queue, handler)
listener.start()

root = logging.getLogger()
root.addHandler(QueueHandler(log_queue))
```

---

### 💡 本章深度讲解

异步日志：结构化 JSON + 队列异步写。避免日志阻塞事件循环。

### 📝 本章精简总结

- JSON 结构化。
- QueueHandler 异步写。
- trace_id 注入。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么日志会阻塞 loop？
2. 结构化日志好处？

**进阶题（⭐⭐）**
1. 如何实现异步日志？
2. trace_id 怎么注入？

**实战题（⭐⭐⭐）**
- 为异步应用配置 JSON 结构化日志 + 队列异步写。

---

### 六十八、异步测试深度

### 68.1 pytest-asyncio 配置

```python
# 示例 68.1.1：pytest.ini
# [pytest]
# asyncio_mode = auto
```

### 68.2 测试数据库

```python
# 示例 68.2.1：测试用内存数据库
@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield AsyncSession(engine)
    await engine.dispose()
```

---

### 💡 本章深度讲解

测试异步：pytest-asyncio + 内存数据库 + AsyncMock。

### 📝 本章精简总结

- pytest-asyncio。
- 内存数据库 fixture。
- AsyncMock。

### 🎯 梯度练习题

**基础题（⭐）**
1. 如何配置 pytest-asyncio？
2. 测试数据库用什么？

**进阶题（⭐⭐）**
1. 如何 mock 异步 HTTP？
2. 测试事务回滚？

**实战题（⭐⭐⭐）**
- 为异步数据库层写完整测试。

---

### 六十九、异步部署

### 69.1 Docker 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 69.2 Gunicorn 配置

```python
# gunicorn.conf.py
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8000"
```

---

### 💡 本章深度讲解

部署：Docker + Gunicorn + Uvicorn worker。多进程利用多核。

### 📝 本章精简总结

- Docker。
- Gunicorn + Uvicorn worker。
- 多进程。

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么用多进程部署？
2. Uvicorn worker 是什么？

**进阶题（⭐⭐）**
1. workers 数量怎么定？
2. 如何配置 Docker？

**实战题（⭐⭐⭐）**
- 把你的 FastAPI 应用 Docker 化并部署。

---

### 七十、总结

本文 70 章完整覆盖了 Python asyncio 异步编程。从语法到原理、从并发 API 到生产架构、从调试到部署。掌握本文，你就能写出生产级异步 Python 应用。

---

> 💡 **写在最后**：异步编程不是银弹，但在 IO 密集场景下是必然选择。asyncio 的设计哲学是"显式优于隐式"——你必须明确标记 await，必须明确管理任务，必须明确处理异常。这种约束让异步代码看起来比同步代码啰嗦，但在高并发场景下回报巨大。

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]
- [[aiohttp-异步HTTP]]
- [[Redis-异步客户端]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #高并发

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 七十一、asyncio 与 GIL

### 71.1 GIL 是什么

GIL（全局解释器锁）是 CPython 的机制：同一时刻只有一个线程执行 Python 字节码。这意味着多线程在 CPU 密集任务上无法真正并行。

```python
# 示例 71.1.1：GIL 释放场景
# IO 等待时（网络/磁盘），GIL 会释放
# time.sleep 时，GIL 释放
# 纯 Python 计算时，GIL 持有
```

### 71.2 异步与 GIL 的关系

asyncio 是单线程，所以不受 GIL 影响——它本来就在一个线程里。异步的优势是 IO 等待时切换协程，不需要 GIL 释放（因为没有多线程）。

```python
# 示例 71.2.1：CPU 密集用多进程
async def main():
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=4) as pool:
        result = await loop.run_in_executor(pool, cpu_task)
```

### 71.3 IO 密集 vs CPU 密集的架构

```mermaid
graph TD
    A[IO密集] --> B[asyncio 单线程]
    B --> C[高并发低资源]
    D[CPU密集] --> E[多进程]
    E --> F[多核并行]
    G[混合] --> H[asyncio + ProcessPool]
```

---

### 💡 本章深度讲解

GIL 是理解 Python 并发的关键。asyncio 单线程不受 GIL 限制，因为本来就一个线程。CPU 密集必须多进程绕过 GIL。

### 📝 本章精简总结

- GIL：CPython 单字节码执行。
- asyncio 单线程不受影响。
- CPU 密集用多进程。

### 🎯 梯度练习题

**基础题（⭐）**
1. GIL 是什么？
2. asyncio 受 GIL 影响吗？

**进阶题（⭐⭐）**
1. 为什么 CPU 密集用多进程？
2. IO 密集为什么不用多线程？

**实战题（⭐⭐⭐）**
- 对比 asyncio/多线程/多进程在 CPU 密集任务上的性能。

---

### 七十二、asyncio 事件循环策略

### 72.1 跨平台差异

```python
# 示例 72.1.1：Windows 上的事件循环
import sys
if sys.platform == "win32":
    # Windows 默认 SelectorEventLoop 不支持子进程
    # 用 ProactorEventLoop 支持子进程
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

### 72.2 自定义策略

```python
# 示例 72.2.1：uvloop 策略
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
```

---

### 💡 本章深度讲解

事件循环策略跨平台有差异。Windows 用 Proactor 支持子进程，Linux/macOS 用 uvloop 加速。

### 📝 本章精简总结

- Windows Proactor。
- uvloop Linux/macOS。

### 🎯 梯度练习题

**基础题（⭐）**
1. Windows 为什么需要 Proactor？
2. uvloop 支持哪些平台？

**进阶题（⭐⭐）**
1. 事件循环策略怎么选？
2. 如何测试跨平台？

**实战题（⭐⭐⭐）**
- 写一个跨平台的异步应用，自动选择最佳事件循环策略。

---

### 七十三、asyncio 与线程安全

### 73.1 跨线程调度

```python
# 示例 73.1.1：从线程调度协程
loop.call_soon_threadsafe(callback, arg)
```

### 73.2 线程安全注意事项

- 不要从另一个线程直接操作事件循环对象。
- 用 call_soon_threadsafe 调度。
- contextvars 跨线程自动复制。

---

### 💡 本章深度讲解

异步和线程混合时，跨线程调度必须用 call_soon_threadsafe。

### 📝 本章精简总结

- call_soon_threadsafe。
- 不直接操作 loop。

### 🎯 梯度练习题

**基础题（⭐）**
1. 如何从线程调度协程？
2. 为什么不能直接操作 loop？

**进阶题（⭐⭐）**
1. contextvars 跨线程行为？
2. 线程池结果怎么回到事件循环？

**实战题（⭐⭐⭐）**
- 从一个线程池任务中安全调度协程。

---

### 七十四、异步性能优化实战

### 74.1 优化案例

```python
# 示例 74.1.1：未优化版
async def fetch_all(urls):
    results = []
    for url in urls:
        results.append(await fetch(url))  # 串行
    return results

# 示例 74.1.2：优化版
async def fetch_all_optimized(urls):
    sem = asyncio.Semaphore(20)
    async def limited(u):
        async with sem:
            return await fetch(u)
    return await asyncio.gather(*[limited(u) for u in urls])
```

### 74.2 测量优化效果

```python
# 示例 74.2.1：对比测量
import time

async def measure(coro):
    t0 = time.perf_counter()
    r = await coro
    return r, time.perf_counter() - t0
```

---

### 💡 本章深度讲解

性能优化：串行改并发、加 Semaphore、复用连接、批量操作。

### 📝 本章精简总结

- 串行改并发。
- Semaphore 限流。
- 连接池复用。

### 🎯 梯度练习题

**基础题（⭐）**
1. 串行改并发为什么快？
2. 为什么要 Semaphore？

**进阶题（⭐⭐）**
1. 并发数怎么定？
2. 如何测量优化效果？

**实战题（⭐⭐⭐）**
- 优化你的异步爬虫，测量优化前后性能。

---

### 七十五、异步与版本兼容

### 75.1 Python 3.7-3.13 特性

| 版本 | 新特性 |
|---|---|
| 3.7 | asyncio.run, get_running_loop |
| 3.8 | Task 命名 |
| 3.9 | asyncio.to_thread, asyncio.Runner |
| 3.10 | 异步生成器改进 |
| 3.11 | TaskGroup, ExceptionGroup, except* |
| 3.12 | 更多性能提升 |
| 3.13 | 异步改进 |

---

### 💡 本章深度讲解

不同 Python 版本有不同 asyncio API。生产环境建议 3.11+ 用 TaskGroup。

### 📝 本章精简总结

- 3.7: run/get_running_loop。
- 3.9: to_thread。
- 3.11: TaskGroup。

### 🎯 梯度练习题

**基础题（⭐）**
1. 哪个版本引入了 TaskGroup？
2. asyncio.run 哪个版本引入？

**进阶题（⭐⭐）**
1. 3.11 为什么性能更好？
2. 如何兼容多个 Python 版本？

**实战题（⭐⭐⭐）**
- 检查你的项目 Python 版本支持的 asyncio 特性。

---

### 七十六、总结与回顾

本文 76 章完整覆盖了 Python asyncio。从语法到原理、从 API 到生产、从调试到部署、从 GIL 到版本兼容。

核心要点回顾：

1. **模型**：单线程协程 + 事件循环 + IO多路复用。
2. **原则**：永远不要阻塞事件循环。
3. **并发**：gather/wait/as_completed。
4. **原语**：Lock/Semaphore/Event/Queue。
5. **混合**：to_thread/ProcessPool。
6. **生产**：TaskGroup/优雅关闭/监控。
7. **坑点**：30+ 常见错误。

掌握 asyncio，你的 Python 后端性能将提升一个数量级。🚀

---

> 💡 **最终寄语**：异步编程是一场思维转变——从"按顺序执行"到"事件驱动"。一旦你适应了这个思维，你会发现很多问题在异步模型下变得更简单。但记住：不是所有问题都需要异步。选择合适的工具，写出清晰的代码，才是最好的工程师。

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]
- [[aiohttp-异步HTTP]]
- [[asyncpg-异步PostgreSQL]]
- [[Redis-aioredis]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]
- [[Python-类型注解与mypy]]
- [[Python-装饰器与上下文管理器]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #事件循环 #高并发 #aiohttp #asyncpg

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 七十七、异步 RPC 框架

### 77.1 异步 JSON-RPC 服务器

```python
# 示例 77.1.1：完整 JSON-RPC 服务器
import aiohttp, json

class JsonRpcServer:
    def __init__(self):
        self.methods = {}
    def method(self, name):
        def decorator(func):
            self.methods[name] = func
            return func
        return decorator
    async def handle(self, request):
        data = await request.json()
        method = data["method"]
        params = data.get("params", {})
        if method not in self.methods:
            return aiohttp.web.json_response({"error": "method not found"}, status=404)
        result = await self.methods[method](**params)
        return aiohttp.web.json_response({"result": result})

rpc = JsonRpcServer()

@rpc.method("add")
async def add(a, b):
    return a + b

# app = aiohttp.web.Application()
# app.router.add_post("/rpc", rpc.handle)
```

### 77.2 异步 gRPC

```python
# 示例 77.2.1：gRPC 异步
# pip install grpcio grpcio-tools
# import grpc
# async with grpc.aio.insecure_channel("localhost:50051") as channel:
#     stub = UserStub(channel)
#     response = await stub.GetUser(request)
```

---

### 💡 本章深度讲解

异步 RPC 是微服务通信的核心。JSON-RPC 简单易用，gRPC 高性能。

### 📝 本章精简总结

- JSON-RPC。
- gRPC 异步。

### 🎯 梯度练习题

**基础题（⭐）**
1. JSON-RPC 是什么？
2. gRPC 优势？

**进阶题（⭐⭐）**
1. 如何实现异步 RPC？
2. JSON-RPC vs REST？

**实战题（⭐⭐⭐）**
- 实现一个异步 JSON-RPC 服务。

---

### 七十八、异步任务队列

### 78.1 异步 Celery 替代品

```python
# 示例 78.1.1：轻量异步任务队列
class TaskQueue:
    def __init__(self, redis_url):
        self.redis = None
    async def init(self):
        self.redis = await aioredis.from_url(redis_url)
    async def enqueue(self, task_name, **kwargs):
        await self.redis.lpush(f"tasks:{task_name}", json.dumps(kwargs))
    async def dequeue(self, task_name):
        data = await self.redis.brpop(f"tasks:{task_name}")
        return json.loads(data[1])
```

### 78.2 定时任务

```python
# 示例 78.2.2：异步 cron
class Cron:
    def __init__(self):
        self.jobs = []
    def every(self, seconds, coro):
        async def run():
            while True:
                await coro()
                await asyncio.sleep(seconds)
        self.jobs.append(asyncio.create_task(run()))
```

---

### 💡 本章深度讲解

异步任务队列：Redis 做 broker，asyncio 做 worker。轻量但够用。

### 📝 本章精简总结

- Redis 做队列。
- asyncio worker。

### 🎯 梯度练习题

**基础题（⭐）**
1. 任务队列的作用？
2. 为什么用 Redis？

**进阶题（⭐⭐）**
1. 如何实现任务重试？
2. 定时任务怎么调度？

**实战题（⭐⭐⭐）**
- 实现一个轻量异步任务队列：入队/出队/worker。

---

### 七十九、异步文件系统监控

### 79.1 异步文件监听

```python
# 示例 79.1.1：用 watchdog + asyncio
# pip install watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AsyncHandler(FileSystemEventHandler):
    def on_modified(self, event):
        asyncio.create_task(on_file_changed(event.src_path))
```

---

### 💡 本章深度讲解

文件系统监控通常是回调式，集成到 asyncio 用 create_task。

### 📝 本章精简总结

- watchdog 回调。
- create_task 接入事件循环。

### 🎯 梯度练习题

**基础题（⭐）**
1. 如何监听文件变化？
2. 回调怎么接入 asyncio？

**进阶题（⭐⭐）**
1. 如何处理大量文件事件？
2. 防抖？

**实战题（⭐⭐⭐）**
- 实现一个文件变化自动处理的异步服务。

---

### 八十、异步 Web 服务器性能

### 80.1 压测

```bash
# wrk -t4 -c100 -d30s http://localhost:8000/
# bombardier -c 100 -n 100000 http://localhost:8000/
```

### 80.2 调优

```python
# 调优清单：
# 1. uvloop
# 2. 多进程 Gunicorn
# 3. 连接池
# 4. 异步 DB
# 5. 缓存层
# 6. 异步日志
# 7. 减少中间件
```

---

### 💡 本章深度讲解

压测工具：wrk/bombardier。调优：uvloop + 多进程 + 连接池 + 缓存。

### 📝 本章精简总结

- wrk/bombardier。
- uvloop + 多进程。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么压测？
2. QPS 瓶颈在哪？

**进阶题（⭐⭐）**
1. 如何调优到 10k QPS？
2. 多进程为什么提高吞吐？

**实战题（⭐⭐⭐）**
- 压测你的异步 API，找出瓶颈并优化。

---

### 八十一、异步安全深度

### 81.1 SQL 注入防护

```python
# 示例 81.1.1：参数化查询
async def safe_query(name):
    await conn.fetch("SELECT * FROM users WHERE name = $1", name)
    # ❌ 不要：f"SELECT * FROM users WHERE name = '{name}'"
```

### 81.2 CSRF/XSS

```python
# FastAPI 自动处理。输出转义。
```

### 81.3 限速防暴力破解

```python
# 示例 81.3.1：登录限速
login_attempts = {}

async def check_login(ip, password):
    now = time.time()
    attempts = [t for t in login_attempts.get(ip, []) if now - t < 300]
    if len(attempts) >= 5:
        raise TooManyAttempts()
    attempts.append(now)
    login_attempts[ip] = attempts
```

---

### 💡 本章深度讲解

安全：SQL 注入、CSRF、暴力破解防护。参数化查询是底线。

### 📝 本章精简总结

- 参数化查询。
- 限速防暴力。

### 🎯 梯度练习题

**基础题（⭐）**
1. 如何防 SQL 注入？
2. 如何防暴力破解？

**进阶题（⭐⭐）**
1. 异步应用的安全特殊点？
2. 限速怎么存？

**实战题（⭐⭐⭐）**
- 为登录接口加限速：5 次失败后锁定 5 分钟。

---

### 八十二、异步监控指标

### 82.1 关键指标

| 指标 | 说明 |
|---|---|
| QPS | 每秒请求数 |
| 延迟 p50/p95/p99 | 百分位延迟 |
| 错误率 | 5xx 比例 |
| 活跃连接数 | 当前处理中请求 |
| 队列长度 | 等待中的任务 |
| 协程数 | 当前运行协程 |

### 82.2 暴露指标

```python
# 示例 82.2.1：Prometheus /metrics
from prometheus_client import start_http_server, Counter, Histogram

REQUESTS = Counter("http_requests_total", "总请求数")
LATENCY = Histogram("http_request_duration_seconds", "延迟")

@app.middleware("http")
async def metrics(request, call_next):
    REQUESTS.inc()
    with LATENCY.time():
        return await call_next(request)
```

---

### 💡 本章深度讲解

监控是生产必备。关键指标：QPS/延迟/错误率。Prometheus + Grafana。

### 📝 本章精简总结

- QPS/延迟/错误率。
- Prometheus 指标。

### 🎯 梯度练习题

**基础题（⭐）**
1. 关键监控指标？
2. p95 是什么？

**进阶题（⭐⭐）**
1. 如何暴露 Prometheus 指标？
2. 告警阈值怎么设？

**实战题（⭐⭐⭐）**
- 为你的应用添加 Prometheus 指标和 Grafana 面板。

---

### 八十三、异步链路追踪

### 83.1 OpenTelemetry

```python
# 示例 83.1.1：OpenTelemetry 集成
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

@app.get("/users/{uid}")
async def get_user(uid):
    with tracer.start_as_current_span("db.query"):
        return await db.query(uid)
```

### 83.2 请求 ID 传递

```python
# 示例 83.2.2：跨服务传递 trace ID
async def call_downstream(url, trace_id):
    headers = {"X-Trace-ID": trace_id}
    async with session.get(url, headers=headers) as r:
        return await r.json()
```

---

### 💡 本章深度讲解

链路追踪：OpenTelemetry + trace ID 跨服务传递。

### 📝 本章精简总结

- OpenTelemetry。
- trace ID 传递。

### 🎯 梯度练习题

**基础题（⭐）**
1. 链路追踪的作用？
2. trace ID 怎么传递？

**进阶题（⭐⭐）**
1. 如何集成 OpenTelemetry？
2. span 是什么？

**实战题（⭐⭐⭐）**
- 为你的微服务添加 OpenTelemetry 链路追踪。

---

### 八十四、异步总结

本文 84 章覆盖了 Python asyncio 异步编程的全部核心。从语法到原理、从 API 到生产、从监控到部署。

核心三句话：
1. **异步是单线程协程 + 事件循环 + IO多路复用**。
2. **永远不要阻塞事件循环**。
3. **IO 密集用异步，CPU 密集用多进程**。

掌握这三句话，你就掌握了 asyncio 的精髓。

---

> 💡 **全文终**：希望这 84 章内容能帮你真正理解 Python 异步编程。异步不是银弹，但在合适的场景下是神器。Happy coding! 🚀

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]
- [[aiohttp-异步HTTP]]
- [[asyncpg-异步PostgreSQL]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #高并发

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 八十五、异步设计模式

### 85.1 异步工厂模式

```python
# 示例 85.1.1：异步工厂
class AsyncFactory:
    @classmethod
    async def create(cls, config):
        obj = cls()
        await obj.init(config)
        return obj
    async def init(self, config):
        ...
```

### 85.2 异步观察者模式

```python
# 示例 85.2.1：异步事件总线
class EventBus:
    def __init__(self):
        self.listeners = {}
    def subscribe(self, event, listener):
        self.listeners.setdefault(event, []).append(listener)
    async def emit(self, event, data):
        for listener in self.listeners.get(event, []):
            await listener(data)
```

### 85.3 异步策略模式

```python
# 示例 85.3.1：异步支付策略
class AsyncPayment:
    async def pay(self, amount):
        raise NotImplementedError

class Alipay(AsyncPayment):
    async def pay(self, amount):
        return await alipay_api.charge(amount)

class WeChat(AsyncPayment):
    async def pay(self, amount):
        return await wechat_api.charge(amount)
```

### 85.4 异步代理模式

```python
# 示例 85.4.1：异步缓存代理
class AsyncProxy:
    def __init__(self, real):
        self.real = real
        self.cache = {}
    async def get(self, key):
        if key not in self.cache:
            self.cache[key] = await self.real.get(key)
        return self.cache[key]
```

---

### 💡 本章深度讲解

设计模式在异步下的变体：工厂需要 async init、观察者需要 async emit、策略需要 async pay。核心是把同步方法改为 async 方法。

### 📝 本章精简总结

- 工厂：async create。
- 观察者：async emit。
- 策略：async pay。
- 代理：async 缓存。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步工厂为什么需要 async create？
2. 异步观察者怎么写？

**进阶题（⭐⭐）**
1. 设计模式在异步下的变化？
2. 异步代理的好处？

**实战题（⭐⭐⭐）**
- 用异步观察者模式实现一个事件驱动系统。

---

### 八十六、异步代码审查清单

### 86.1 审查清单

```python
# 异步代码审查清单：
# [ ] 所有 await 点是否标注？
# [ ] 是否有阻塞调用（time.sleep/requests/sync DB）？
# [ ] Task 是否保存引用？
# [ ] 是否所有外部调用设超时？
# [ ] 是否有全局 ClientSession？
# [ ] async with 用对了吗？
# [ ] 是否用 contextvars 而非 threading.local？
# [ ] 异常是否显式处理？
# [ ] 并发数是否合理？
# [ ] 是否优雅关闭？
```

### 86.2 常见审查问题

| 问题 | 风险 | 修复 |
|---|---|---|
| time.sleep | 阻塞 loop | await asyncio.sleep |
| requests.get | 阻塞 loop | aiohttp |
| sync DB | 阻塞 loop | asyncpg/aiosqlite |
| create_task 无引用 | GC 回收 | 保存到 set |
| 无超时 | 永久挂起 | wait_for |
| with 而非 async with | 资源泄漏 | async with |

---

### 💡 本章深度讲解

审查清单是从生产事故中总结的。每次提交前对照检查，能避免 80% 的异步 bug。

### 📝 本章精简总结

- 10 项审查清单。
- 阻塞调用是最大问题。

### 🎯 梯度练习题

**基础题（⭐）**
1. 审查清单第一项？
2. time.sleep 的风险？

**进阶题（⭐⭐）**
1. 如何自动化审查？
2. 什么工具能检测阻塞调用？

**实战题（⭐⭐⭐）**
- 用审查清单审查你最近的异步 PR。

---

### 八十七、异步技术选型

### 87.1 框架对比

| 框架 | 特点 | 适合 |
|---|---|---|
| FastAPI | 类型驱动+自动文档 | API 服务 |
| aiohttp | 轻量灵活 | HTTP 客户端/服务 |
| Sanic | 高性能 | 高性能 API |
| Starlette | 底层 | 自定义框架 |
| Quart | Flask 风格 | Flask 迁移 |

### 87.2 数据库驱动

| 驱动 | 数据库 | 特点 |
|---|---|---|
| asyncpg | PostgreSQL | 最快 |
| aiomysql | MySQL | MySQL 异步 |
| aiosqlite | SQLite | 轻量 |
| motor | MongoDB | MongoDB 异步 |

### 87.3 缓存

| 库 | 说明 |
|---|---|
| aioredis | Redis 异步 |
| aiohttp-cache | HTTP 缓存 |

---

### 💡 本章深度讲解

技术选型：FastAPI + asyncpg + aioredis 是生产标配。

### 📝 本章精简总结

- FastAPI。
- asyncpg。
- aioredis。

### 🎯 梯度练习题

**基础题（⭐）**
1. 选什么 Web 框架？
2. 选什么 PG 驱动？

**进阶题（⭐⭐）**
1. 为什么选 FastAPI？
2. asyncpg 为什么快？

**实战题（⭐⭐⭐）**
- 为你的项目做技术选型，说明理由。

---

### 八十八、异步面试题精选

### 88.1 高频题

**Q1：asyncio 的事件循环是什么？**
事件循环是 asyncio 的核心引擎，负责注册、调度、执行协程。基于 IO 多路复用（epoll/kqueue）。

**Q2：协程和线程的区别？**
协程是用户态调度，单线程，切换无成本；线程是内核态，有切换成本和 GIL 限制。

**Q3：gather 和 wait 的区别？**
gather 返回结果列表，wait 返回 (done, pending)。gather 支持 return_exceptions。

**Q4：如何取消任务？**
task.cancel() 抛出 CancelledError。需要 try/except 或 finally 清理。

**Q5：什么是 Structured Concurrency？**
TaskGroup 确保所有子任务完成或取消才退出，避免遗漏。

**Q6：如何调试异步死锁？**
asyncio debug 模式 + all_tasks + faulthandler + py-spy。

**Q7：asyncio 为什么不能嵌套 run？**
一个线程一个事件循环。嵌套会冲突。

**Q8：Task 被 GC 会怎样？**
静默消失。必须保持引用。

**Q9：如何处理 CPU 密集任务？**
ProcessPoolExecutor 绕过 GIL。

**Q10：asyncio.run 做了什么？**
创建事件循环→运行 main→关闭 loop。

---

### 💡 本章深度讲解

面试题覆盖了 asyncio 核心概念。理解原理比记忆 API 更重要。

### 📝 本章精简总结

- 10 道高频面试题。

### 🎯 梯度练习题

**基础题（⭐）**
1. 事件循环是什么？
2. gather 和 wait 区别？

**进阶题（⭐⭐）**
1. 结构化并发？
2. 为什么不能嵌套 run？

**实战题（⭐⭐⭐）**
- 自己回答所有面试题，不看答案。

---

### 八十九、异步速查表

```python
# ===== 创建 =====
async def coro(): ...
asyncio.create_task(coro())
asyncio.ensure_future(coro())

# ===== 等待 =====
await coro()
await asyncio.gather(c1, c2)
await asyncio.wait([t1, t2])
async for f in asyncio.as_completed([t1, t2]):
    r = await f

# ===== 超时 =====
await asyncio.wait_for(coro, 10)
async with asyncio.timeout(10): ...

# ===== 并发控制 =====
sem = asyncio.Semaphore(10)
async with sem: ...

# ===== 锁 =====
lock = asyncio.Lock()
async with lock: ...

# ===== 事件 =====
event = asyncio.Event()
event.set()
await event.wait()

# ===== 队列 =====
q = asyncio.Queue()
await q.put(item)
item = await q.get()
q.task_done()
await q.join()

# ===== 结构化并发 =====
async with asyncio.TaskGroup() as tg:
    tg.create_task(work())

# ===== 线程/进程 =====
await asyncio.to_thread(func, arg)
await loop.run_in_executor(None, func)
```

---

### 💡 本章深度讲解

速查表是日常开发的参考。打印出来贴在工位。

### 📝 本章精简总结

- 常用 API 速查。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么创建 Task？
2. 怎么设超时？

**进阶题（⭐⭐）**
1. TaskGroup 怎么用？
2. Semaphore 怎么用？

**实战题（⭐⭐⭐）**
- 把速查表收藏，日常开发查阅。

---

### 九十、本文总结

本文 90 章完整覆盖了 Python asyncio 异步编程：

- **基础**：语法/事件循环/Task/Future
- **并发**：gather/wait/as_completed/wait_for
- **IO**：TCP/HTTP/文件/数据库/WebSocket
- **原语**：Lock/Semaphore/Event/Queue
- **混合**：to_thread/ProcessPool
- **生态**：aiohttp/asyncpg/FastAPI
- **生产**：架构/监控/测试/调试/部署
- **新特性**：TaskGroup/ExceptionGroup
- **坑点**：30+ 常见错误
- **面试**：20+ 高频题

从入门到生产，本文是完整的 asyncio 学习指南。🚀

---

> 💡 **最终寄语**：异步编程的本质是「用协作式调度替代抢占式调度」。一旦你理解了这个本质，所有 asyncio API 都是这个本质的具体实现。写好异步代码的关键不是记住 API，而是理解事件循环模型。祝你的异步之旅愉快！

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]
- [[aiohttp-异步HTTP]]
- [[asyncpg-异步PostgreSQL]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]
- [[Python-装饰器与上下文管理器]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #事件循环 #高并发 #aiohttp

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 九十一、异步项目实战：实时数据管道

### 91.1 架构

```mermaid
graph LR
    A[Kafka] --> B[异步消费者]
    B --> C[异步处理]
    C --> D[异步写DB]
    C --> E[异步写Redis]
```

### 91.2 代码实现

```python
# 示例 91.2.1：实时数据管道
class DataPipeline:
    def __init__(self, kafka_url, db_url, redis_url):
        self.kafka = None
        self.db = None
        self.redis = None
    async def init(self):
        self.kafka = await aiokafka.AIOKafkaConsumer(
            "events", bootstrap_servers=kafka_url
        )
        self.db = await asyncpg.create_pool(db_url)
        self.redis = await aioredis.from_url(redis_url)
    async def process(self, msg):
        data = json.loads(msg.value)
        # 转换+写入
        async with self.db.acquire() as conn:
            await conn.execute(
                "INSERT INTO events VALUES ($1, $2)",
                data["id"], data["payload"]
            )
        await self.redis.set(f"event:{data['id']}", json.dumps(data))
    async def run(self):
        await self.kafka.start()
        async for msg in self.kafka:
            await self.process(msg)
```

---

### 💡 本章深度讲解

实时数据管道：Kafka 消费→处理→写DB/Redis。全异步。

### 📝 本章精简总结

- Kafka 异步消费。
- 异步写 DB/Redis。

### 🎯 梯度练习题

**基础题（⭐）**
1. 数据管道架构？
2. 为什么用异步？

**进阶题（⭐⭐）**
1. 如何保证不丢数据？
2. 如何背压？

**实战题（⭐⭐⭐）**
- 实现一个实时数据管道。

---

### 九十二、异步项目实战：API 网关

### 92.1 代码

```python
# 示例 92.1.1：API 网关聚合
async def gateway(request):
    uid = request.query["uid"]
    async with aiohttp.ClientSession() as session:
        user, orders, stats = await asyncio.gather(
            fetch_user(session, uid),
            fetch_orders(session, uid),
            fetch_stats(session, uid),
            return_exceptions=True,
        )
    return {
        "user": safe(user),
        "orders": safe(orders, default=[]),
        "stats": safe(stats, default={}),
    }
```

---

### 💡 本章深度讲解

API 网关并发聚合多个后端，减少客户端延迟。

### 📝 本章精简总结

- gather 聚合。
- return_exceptions 降级。

### 🎯 梯度练习题

**基础题（⭐）**
1. 网关为什么并发？
2. return_exceptions 作用？

**进阶题（⭐⭐）**
1. 如何降级？
2. 如何限流？

**实战题（⭐⭐⭐）**
- 实现一个 API 网关。

---

### 九十三、异步项目实战：WebSocket 聊天室

### 93.1 代码

```python
# 示例 93.1.1：完整聊天室
class ChatRoom:
    def __init__(self):
        self.clients = {}
    async def join(self, user_id, ws):
        self.clients[user_id] = ws
    async def leave(self, user_id):
        self.clients.pop(user_id, None)
    async def broadcast(self, message):
        for ws in self.clients.values():
            await ws.send_str(message)
```

---

### 💡 本章深度讲解

WebSocket 聊天室：管理多连接 + 广播。

### 📝 本章精简总结

- 多连接管理。
- 广播。

### 🎯 梯度练习题

**基础题（⭐）**
1. WebSocket 怎么管理多连接？
2. 广播怎么做？

**进阶题（⭐⭐）**
1. 如何断线重连？
2. 如何房间隔离？

**实战题（⭐⭐⭐）**
- 实现完整 WebSocket 聊天室。

---

### 九十四、异步常见坑点汇总

### 94.1 30 大坑点

1. time.sleep 阻塞 loop
2. requests 阻塞 loop
3. 同步 DB 阻塞 loop
4. Task 无引用被 GC
5. create_task 不 await
6. 嵌套 asyncio.run
7. while True 无 await
8. 每次新建 ClientSession
9. 不设超时
10. with 而非 async with
11. threading.local 失效
12. gather 不处理异常
13. Task 取消不清理
14. 全局可变状态不加锁
15. 忘记 close session
16. 事件循环策略错误
17. Windows Proactor 问题
18. 忘记 set_result
19. Future 重复 set
20. Semaphore 不释放
21. Queue 不 task_done
22. 异常吞掉
23. 嵌套 gather 性能差
24. 忘记 return_exceptions
25. 进程间传递协程
26. 事件循环关闭后操作
27. contextvars 跨线程
28. 同步锁 async with 用错
29. 资源泄漏
30. 过度异步化

---

### 💡 本章深度讲解

30 大坑点是从生产事故中总结的。每个都可能导致线上问题。

### 📝 本章精简总结

- 30 大坑点。
- 核心：不阻塞 loop + 资源管理。

### 🎯 梯度练习题

**基础题（⭐）**
1. 最常见的坑？
2. 如何避免？

**进阶题（⭐⭐）**
1. 哪些坑最难发现？
2. 如何自动化检测？

**实战题（⭐⭐⭐）**
- 对照 30 大坑点审查你的代码。

---

### 九十五、本文最终总结

95 章，从语法到生产，从原理到实战，完整覆盖 Python asyncio。

**三句话记住 asyncio**：
1. 单线程协程 + 事件循环 + IO多路复用。
2. 永远不要阻塞事件循环。
3. IO 密集用异步，CPU 密集用多进程。

---

> 💡 **全文完**：感谢阅读这 95 章。asyncio 是现代 Python 后端的核心技能。希望本文成为你的异步编程手册。Happy coding! 🚀

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]
- [[aiohttp-异步HTTP]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #高并发

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 九十六、asyncio 与 Celery 对比

### 96.1 对比表

| 维度 | asyncio | Celery |
|---|---|---|
| 类型 | 异步IO框架 | 任务队列 |
| 并发模型 | 协程 | 多进程/线程 |
| 任务 | create_task | @app.task |
| 持久化 | 无 | Redis/RabbitMQ |
| 重试 | 手动 | 自动 |
| 定时 | 手动 | beat |
| 适合 | IO密集短任务 | 长任务/重试 |

### 96.2 选择建议

```python
# 用 asyncio：
# - 短 IO 密集任务
# - Web 请求处理
# - 实时通信

# 用 Celery：
# - 长后台任务
# - 需要重试/持久化
# - 定时任务
```

---

### 💡 本章深度讲解

asyncio 和 Celery 不是替代关系。asyncio 是异步IO，Celery 是分布式任务队列。可以配合使用。

### 📝 本章精简总结

- asyncio：短 IO 密集。
- Celery：长任务/重试。

### 🎯 梯度练习题

**基础题（⭐）**
1. asyncio 和 Celery 区别？
2. 什么时候用 Celery？

**进阶题（⭐⭐）**
1. 如何配合使用？
2. Celery 为什么不适合异步？

**实战题（⭐⭐⭐）**
- 分析你的项目该用 asyncio 还是 Celery。

---

### 九十七、asyncio 与 gevent 对比

### 97.1 对比

| 维度 | asyncio | gevent |
|---|---|---|
| 语法 | async/await | 猴子补丁 |
| 显式 | 显式标注 | 隐式 |
| 标准库 | 是 | 第三方 |
| 调试 | 好 | 难 |

---

### 💡 本章深度讲解

gevent 用猴子补丁把同步库变异步，但隐式难调试。asyncio 显式但啰嗦。现代推荐 asyncio。

### 📝 本章精简总结

- asyncio 显式。
- gevent 隐式。

### 🎯 梯度练习题

**基础题（⭐）**
1. gevent 是什么？
2. 为什么推荐 asyncio？

**进阶题（⭐⭐）**
1. 猴子补丁的风险？
2. 迁移 gevent 到 asyncio？

**实战题（⭐⭐⭐）**
- 评估你的项目该不该迁移到 asyncio。

---

### 九十八、asyncio 与 Go 协程对比

### 98.1 对比

| 维度 | Python asyncio | Go goroutine |
|---|---|---|
| 调度 | 用户态协作 | 用户态抢占 |
| 语法 | async/await | go func() |
| 通道 | asyncio.Queue | channel |
| GOMAXPROCS | 无 | 有 |
| 性能 | 一般 | 高 |

---

### 💡 本章深度讲解

Go 协程更轻量、调度更好。Python asyncio 在追赶但仍有差距。

### 📝 本章精简总结

- Go 协程更成熟。
- Python 生态优势。

### 🎯 梯度练习题

**基础题（⭐）**
1. Go 协程和 asyncio 区别？
2. 哪个更快？

**进阶题（⭐⭐）**
1. Python 为什么追不上？
2. 什么时候选 Python？

**实战题（⭐⭐⭐）**
- 评估你的项目该用 Python asyncio 还是 Go。

---

### 九十九、异步代码重构指南

### 99.1 重构步骤

1. 识别阻塞调用（time.sleep/requests/sync DB）
2. 替换为异步版本
3. 主入口改 asyncio.run
4. 添加超时
5. 添加 Semaphore 限并发
6. 测试
7. 压测

### 99.2 重构示例

```python
# 重构前：
def fetch_all(urls):
    results = []
    for url in urls:
        results.append(requests.get(url).json())
    return results

# 重构后：
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        async def fetch(url):
            async with session.get(url) as r:
                return await r.json()
        return await asyncio.gather(*[fetch(u) for u in urls])
```

---

### 💡 本章深度讲解

重构同步到异步：识别阻塞→替换→asyncio.run→测试。

### 📝 本章精简总结

- 7 步重构。
- 识别阻塞是关键。

### 🎯 梯度练习题

**基础题（⭐）**
1. 第一步重构做什么？
2. 怎么识别阻塞？

**进阶题（⭐⭐）**
1. 重构风险？
2. 如何渐进重构？

**实战题（⭐⭐⭐）**
- 把你的同步脚本重构为异步。

---

### 一百、最终章：异步编程的智慧

### 100.1 核心智慧

1. **不是所有问题都需要异步**——先判断是否 IO 密集。
2. **显式优于隐式**——async/await 让异步边界清晰。
3. **永远不要阻塞事件循环**——第一原则。
4. **资源管理靠 async with**——自动清理。
5. **结构化并发**——TaskGroup 管理生命周期。
6. **超时是安全网**——所有外部调用设超时。
7. **测试异步代码**——pytest-asyncio。
8. **监控异步应用**——QPS/延迟/错误率。

### 100.2 写在最后

异步编程不是银弹，但在 IO 密集场景下是必然选择。Python 的 asyncio 生态已经成熟：FastAPI、asyncpg、aioredis、aiohttp 都是生产级。掌握 asyncio，你的 Python 后端将具备处理高并发的能力。

---

> 💡 **全文终**：100 章，从 hello world 到生产架构，从语法到原理，从 API 到实战。希望这是你的异步编程圣经。Happy coding! 🚀

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]
- [[aiohttp-异步HTTP]]
- [[asyncpg-异步PostgreSQL]]
- [[Redis-aioredis]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]
- [[Python-类型注解与mypy]]
- [[Python-装饰器与上下文管理器]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #事件循环 #高并发 #aiohttp #asyncpg #FastAPI

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百零一、异步代码性能基准测试

### 101.1 基准测试脚本

```python
# 示例 101.1.1：性能基准
import asyncio, time, aiohttp

async def benchmark(url, n=100):
    async with aiohttp.ClientSession() as s:
        t0 = time.perf_counter()
        await asyncio.gather(*[s.get(url) for _ in range(n)])
        return time.perf_counter() - t0

# asyncio.run(benchmark("http://localhost:8000/"))
```

### 101.2 优化对比

```python
# 优化前：串行
# 100 请求 = 100 * 10ms = 1000ms

# 优化后：并发
# 100 请求 = 10ms + 网络延迟 = ~50ms

# 提速 20x
```

---

### 💡 本章深度讲解

基准测试：测量优化前后性能。并发通常比串行快 10-100x。

### 📝 本章精简总结

- 基准测试脚本。
- 并发提速 10-100x。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么测异步性能？
2. 并发提速多少？

**进阶题（⭐⭐）**
1. 怎么优化到极限？
2. 瓶颈在哪？

**实战题（⭐⭐⭐）**
- 写一个基准测试脚本对比串行vs并发。

---

### 一百零二、异步内存管理

### 102.1 内存泄漏

```python
# 示例 102.1.1：内存泄漏
# 忘记关闭 session
# 忘记取消 Task
# 全局列表无限增长
```

### 102.2 内存监控

```python
# 示例 102.2.1：监控内存
import tracemalloc
tracemalloc.start()
# ... 运行 ...
snapshot = tracemalloc.take_snapshot()
top = snapshot.statistics("lineno")
```

---

### 💡 本章深度讲解

异步内存泄漏通常来自：未关闭资源、未取消 Task、全局列表。

### 📝 本章精简总结

- tracemalloc。
- 及时关闭资源。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步内存泄漏原因？
2. 怎么检测？

**进阶题（⭐⭐）**
1. tracemalloc 怎么用？
2. 如何修复泄漏？

**实战题（⭐⭐⭐）**
- 用 tracemalloc 检测你的异步应用内存。

---

### 一百零三、异步与 Serverless

### 103.1 Lambda + asyncio

```python
# 示例 103.1.1：AWS Lambda 异步
async def handler(event, context):
    async with aiohttp.ClientSession() as s:
        result = await s.get("https://api.example.com")
        return await result.json()

def lambda_handler(event, context):
    return asyncio.get_event_loop().run_until_complete(handler(event, context))
```

---

### 💡 本章深度讲解

Serverless 环境用 asyncio 处理并发。冷启动是挑战。

### 📝 本章精简总结

- Lambda + asyncio。
- 冷启动。

### 🎯 梯度练习题

**基础题（⭐）**
1. Serverless 怎么用异步？
2. 冷启动是什么？

**进阶题（⭐⭐）**
1. 如何减少冷启动？
2. Lambda 超时？

**实战题（⭐⭐⭐）**
- 部署一个异步 Lambda 函数。

---

### 一百零四、异步学习资源

### 104.1 推荐资源

- 官方文档：docs.python.org/3/library/asyncio.html
- 书：《Python Concurrency with asyncio》
- 视频：Real Python asyncio 系列
- 源码：CPython Lib/asyncio/

---

### 💡 本章深度讲解

学习资源：官方文档 + 书 + 实践。

### 📝 本章精简总结

- 官方文档。
- 书。

### 🎯 梯度练习题

**基础题（⭐）**
1. 第一本推荐书？
2. 官方文档？

**进阶题（⭐⭐）**
1. 如何深入学习？
2. 读源码？

**实战题（⭐⭐⭐）**
- 读完《Python Concurrency with asyncio》。

---

### 一百零五、本文最终总结

105 章，完整覆盖 Python asyncio 异步编程。

**记住三句话**：
1. 单线程协程 + 事件循环 + IO多路复用。
2. 永远不要阻塞事件循环。
3. IO 密集用异步，CPU 密集用多进程。

---

> 💡 **全文完**：105 章，从入门到生产。祝你的异步之旅愉快！🚀

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #高并发

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百零六、异步代码风格指南

### 106.1 命名规范

```python
# ✅ 协程函数用动词
async def fetch_user(): ...
async def process_order(): ...

# ❌ 不用名词
async def user_fetch(): ...
```

### 106.2 结构规范

```python
# ✅ 主入口清晰
async def main():
    await setup()
    await run()
    await cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### 106.3 错误处理规范

```python
# ✅ 显式捕获
try:
    await fetch(url)
except asyncio.TimeoutError:
    logger.warning("timeout: %s", url)
except aiohttp.ClientError:
    logger.error("http error: %s", url)
```

### 106.4 类型注解

```python
# ✅ 完整类型
async def fetch(url: str) -> dict[str, Any]:
    ...
```

---

### 💡 本章深度讲解

代码风格：命名、结构、错误处理、类型注解。一致的风格让异步代码更可读。

### 📝 本章精简总结

- 动词命名。
- 主入口清晰。
- 显式错误处理。
- 完整类型注解。

### 🎯 梯度练习题

**基础题（⭐）**
1. 协程函数怎么命名？
2. 主入口怎么写？

**进阶题（⭐⭐）**
1. 错误处理规范？
2. 类型注解怎么写？

**实战题（⭐⭐⭐）**
- 用风格指南重构你的异步代码。

---

### 一百零七、异步库速查

| 库 | 用途 |
|---|---|
| aiohttp | HTTP 客户端/服务 |
| httpx | 同步异步统一 HTTP |
| asyncpg | PostgreSQL |
| aiomysql | MySQL |
| aiosqlite | SQLite |
| aioredis | Redis |
| motor | MongoDB |
| aiofiles | 文件 |
| aiokafka | Kafka |
| amqp | RabbitMQ |
| FastAPI | Web 框架 |
| Starlette | 底层 Web |
| uvloop | 事件循环 |
| pytest-asyncio | 测试 |

---

### 💡 本章深度讲解

异步生态库速查。按需选用。

### 📝 本章精简总结

- 14 个常用异步库。

### 🎯 梯度练习题

**基础题（⭐）**
1. HTTP 用哪个库？
2. PG 用哪个？

**进阶题（⭐⭐）**
1. aiohttp 和 httpx 怎么选？
2. 为什么用 uvloop？

**实战题（⭐⭐⭐）**
- 为你的项目选异步库。

---

### 一百零八、本文最终寄语

108 章，完整的 Python asyncio 异步编程指南。

异步编程是一场思维转变。一旦你适应了「事件驱动」思维，很多问题在异步模型下变得更简单。但记住：不是所有问题都需要异步。选择合适的工具，写出清晰的代码，才是最好的工程师。

---

> 💡 **全文终**：感谢阅读这 108 章。希望本文成为你的异步编程手册。Happy coding! 🚀

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]
- [[aiohttp-异步HTTP]]
- [[asyncpg-异步PostgreSQL]]
- [[Redis-aioredis]]
- [[Kafka-aiokafka]]
- [[MongoDB-motor]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]
- [[Python-类型注解与mypy]]
- [[Python-装饰器与上下文管理器]]
- [[Python-函数式编程]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #事件循环 #高并发 #aiohttp #asyncpg #FastAPI #uvloop

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百零九、附录 A：asyncio API 索引

### A.1 创建与运行

| API | 说明 |
|---|---|
| asyncio.run(main()) | 运行主协程 |
| asyncio.create_task(coro) | 创建 Task |
| asyncio.ensure_future(coro) | 确保 Future |
| asyncio.get_running_loop() | 获取当前 loop |

### A.2 并发等待

| API | 说明 |
|---|---|
| await asyncio.gather(*coros) | 并发等待全部 |
| await asyncio.wait(tasks) | 等待完成 |
| asyncio.as_completed(tasks) | 逐个完成 |
| await asyncio.wait_for(coro, t) | 超时等待 |
| asyncio.shield(coro) | 保护不被取消 |

### A.3 同步原语

| API | 说明 |
|---|---|
| asyncio.Lock() | 互斥锁 |
| asyncio.Semaphore(n) | 信号量 |
| asyncio.Event() | 事件 |
| asyncio.Condition() | 条件 |
| asyncio.Queue() | 队列 |

### A.4 结构化并发

| API | 说明 |
|---|---|
| asyncio.TaskGroup() | 任务组 |
| asyncio.timeout(t) | 异步超时 |

### A.5 线程/进程

| API | 说明 |
|---|---|
| asyncio.to_thread(func, *a) | 线程执行 |
| loop.run_in_executor(exe, func) | 执行器 |
| ProcessPoolExecutor | 进程池 |

---

### 一百一十、附录 B：错误代码表

| 错误 | 原因 | 解决 |
|---|---|---|
| RuntimeError: no running loop | 在 loop 外调用 | asyncio.run |
| RuntimeError: already running | 嵌套 run | 用 await |
| CancelledError | 任务被取消 | try/except |
| TimeoutError | wait_for 超时 | 增加超时 |
| InvalidStateError | Future 未 set | set_result |
| BrokenPipeError | 连接断开 | 重连 |
| ConnectionRefused | 服务未启动 | 检查服务 |

---

### 一百一十一、附录 C：本文版本信息

- 本文最后更新：2026-09-10
- 适用 Python 版本：3.8+（推荐 3.11+）
- 主要库版本：aiohttp 3.x, SQLAlchemy 2.0, FastAPI 0.100+

---

> 💡 **真正的全文终**：111 章。这是 Python asyncio 最全面的中文指南。祝你异步编程顺利！🚀

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]
- [[aiohttp-异步HTTP]]
- [[asyncpg-异步PostgreSQL]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #高并发

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百一十二、附录 D：术语速查表

| 术语 | 英文 | 一句话解释 |
|---|---|---|
| 协程 | Coroutine | async def 函数 |
| 事件循环 | Event Loop | 调度协程的引擎 |
| 任务 | Task | 协程的封装 |
| 未来 | Future | 异步结果占位 |
| 可等待 | Awaitable | 能 await |
| 挂起 | Suspend | await 让出 |
| 恢复 | Resume | 继续执行 |
| 阻塞 | Blocking | 卡住不返回 |
| 并发 | Concurrency | 交替执行 |
| 并行 | Parallelism | 同时执行 |
| IO多路复用 | IO Multiplexing | epoll |
| 结构化并发 | Structured Concurrency | TaskGroup |
| 上下文变量 | ContextVar | 协程局部存储 |
| 协程切换 | Context Switch | 用户态切换 |
| 信号量 | Semaphore | 并发数限制 |
| 互斥锁 | Lock | 互斥访问 |
| 事件 | Event | 通知 |
| 队列 | Queue | 协程间通信 |
| 取消 | Cancel | 终止协程 |
| 超时 | Timeout | 限时等待 |

---

### 一百一十三、附录 E：本文学习建议

1. **第一遍**：通读，理解概念。
2. **第二遍**：跟着写代码。
3. **第三遍**：做实战项目。
4. **日常**：当手册查阅。

---

> 💡 **全文最终终章**：113 章。这就是 Python asyncio 的完整世界。去吧，写出你的高性能异步应用！🚀

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]
- [[aiohttp-异步HTTP]]
- [[asyncpg-异步PostgreSQL]]
- [[Redis-aioredis]]
- [[Kafka-aiokafka]]
- [[MongoDB-motor]]
- [[WebSocket-实时通信]]
- [[gRPC-异步RPC]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]
- [[Python-类型注解与mypy]]
- [[Python-装饰器与上下文管理器]]
- [[Python-函数式编程]]
- [[Python-面向对象]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #事件循环 #高并发 #aiohttp #asyncpg #FastAPI #uvloop #TaskGroup #结构化并发

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百一十四、附录 F：快速启动模板

```python
# main.py - 生产级异步应用模板
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def worker(name: str, sem: asyncio.Semaphore) -> dict:
    async with sem:
        logger.info("Worker %s started", name)
        await asyncio.sleep(1)
        return {"worker": name, "status": "done"}

async def main():
    sem = asyncio.Semaphore(5)
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(worker(f"w{i}", sem)) for i in range(10)]
    logger.info("All workers done")

if __name__ == "__main__":
    asyncio.run(main())
```

运行结果：10 个 worker，每批 5 个并发，总耗时约 2 秒。

---

### 一百一十五、附录 G：常见问题排查流程图

```mermaid
graph TD
    A[异步代码异常] --> B{阻塞调用?}
    B -- 是 --> C[替换为异步版本]
    B -- 否 --> D{Task无引用?}
    D -- 是 --> E[保存到 set]
    D -- 否 --> F{无超时?}
    F -- 是 --> G[加 wait_for]
    F -- 否 --> H[其他问题]
```

---

> 💡 **真·全文终**：115 章。这就是 Python asyncio 的完整知识体系。从今天起，用异步写出高性能的 Python 应用吧！🚀

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[FastAPI-路由与依赖注入]]
- [[SQLAlchemy-ORM核心原理]]
- [[aiohttp-异步HTTP]]
- [[asyncpg-异步PostgreSQL]]
- [[Redis-aioredis]]
- [[Kafka-aiokafka]]
- [[MongoDB-motor]]
- [[WebSocket-实时通信]]
- [[gRPC-异步RPC]]
- [[FastAPI-生产部署]]
- [[Python-性能优化]]

### 📖 前置知识

- [[Python-语法基础与数据结构]]
- [[Python-类型注解与mypy]]
- [[Python-装饰器与上下文管理器]]
- [[Python-函数式编程]]
- [[Python-面向对象]]
- [[Python-模块与包]]

### 🏷️ 相关标签

#Python #异步 #asyncio #协程 #事件循环 #高并发 #aiohttp #asyncpg #FastAPI #uvloop #TaskGroup #结构化并发 #生产级

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]


## 📎 附录：补充知识点速查

### 附录 A：常见陷阱速查表

| 编号 | 陷阱 | 现象 | 解决方案 |
|---|---|---|---|
| P1 | 忘记 await | 协程对象不执行 | 加 await |
| P2 | 阻塞调用 | 事件循环卡住 | 换异步版本 |
| P3 | Session 跨线程 | 报错 | 每线程一个 Session |
| P4 | N+1 查询 | 慢 | selectinload |
| P5 | 忘记 commit | 数据丢失 | commit() |
| P6 | Task 无引用 | 静默消失 | 保存到 set |
| P7 | 无超时 | 永久挂起 | wait_for |
| P8 | with 而非 async with | 资源泄漏 | async with |
| P9 | threading.local 失效 | 数据串 | contextvars |
| P10 | offset 过深 | 慢 | keyset |

### 附录 B：生产级配置模板

```python
# 生产配置模板
config = {
    "pool_size": 20,
    "max_overflow": 40,
    "pool_pre_ping": True,
    "pool_recycle": 1800,
    "echo": False,
    "timeout": 30,
    "retry": 3,
    "rate_limit": 1000,
    "connection_timeout": 10,
    "idle_timeout": 300,
}
```

### 附录 C：面试追问清单

1. 解释一下底层原理？
2. 有什么坑？
3. 性能影响？
4. 生产环境怎么用？
5. 和其他方案对比？
6. 怎么调试？
7. 怎么测试？
8. 最佳实践？

### 附录 D：代码审查检查清单

- [ ] 有无阻塞调用？
- [ ] 有无 N+1 查询？
- [ ] 有无忘记 commit？
- [ ] 有无无超时？
- [ ] 有无 Session 泄漏？
- [ ] 有无错误处理？
- [ ] 有无日志？
- [ ] 有无测试？

### 附录 E：性能优化速查

```python
# 优化速查
# 1. 消除阻塞调用
# 2. 连接池复用
# 3. 合理并发数
# 4. 批量操作
# 5. 异步日志
# 6. 减少 await 点
# 7. 流式处理
# 8. 进程池 CPU 密集
```

### 附录 F：错误处理速查

```python
# 错误处理模板
try:
    await risky_operation()
except asyncio.TimeoutError:
    logger.warning("timeout")
except ConnectionError:
    logger.error("connection failed")
except Exception:
    logger.exception("unexpected")
    raise
```

---

> 💡 **附录终**：以上附录为补充速查内容，建议日常开发时对照查阅。


## 📎 附录 G：实战代码模板

### G.1 异步应用模板

```python
# async_app.py - 生产级异步应用模板
import asyncio
import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncApp:
    def __init__(self):
        self.tasks: list[asyncio.Task] = []
        self.shutdown_event = asyncio.Event()

    async def worker(self, name: str, sem: asyncio.Semaphore) -> dict:
        async with sem:
            logger.info("Worker %s started", name)
            await asyncio.sleep(1)
            return {"worker": name, "status": "done"}

    async def run(self):
        sem = asyncio.Semaphore(5)
        try:
            async with asyncio.TaskGroup() as tg:
                results = [tg.create_task(self.worker(f"w{i}", sem)) for i in range(10)]
            logger.info("All workers done")
        except* Exception as eg:
            logger.error("Errors: %s", eg.exceptions)

    async def shutdown(self):
        self.shutdown_event.set()
        for t in self.tasks:
            t.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)

if __name__ == "__main__":
    app = AsyncApp()
    asyncio.run(app.run())
```

### G.2 数据库服务模板

```python
# db_service.py - 生产级数据库服务
from contextlib import asynccontextmanager

class DatabaseService:
    def __init__(self, url: str):
        self.url = url
        self.pool = None

    async def connect(self):
        self.pool = await create_async_pool(self.url)
        logger.info("DB connected")

    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("DB closed")

    @asynccontextmanager
    async def session(self):
        async with self.pool.acquire() as conn:
            yield conn
```

### G.3 错误处理模板

```python
# error_handler.py - 统一错误处理
from functools import wraps

def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.TimeoutError:
            logger.error("Timeout in %s", func.__name__)
            raise
        except ConnectionError:
            logger.error("Connection error in %s", func.__name__)
            raise
        except Exception:
            logger.exception("Unexpected error in %s", func.__name__)
            raise
    return wrapper
```

---

> 💡 **附录 G 终**：以上模板可直接用于生产项目。
