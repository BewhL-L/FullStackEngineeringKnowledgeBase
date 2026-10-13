---
title: PostgreSQL-Python高级用法
category: Python全栈
tags: [Python, PostgreSQL, psycopg2, asyncpg, SQLAlchemy, 数据库, JSONB, 全文搜索, 索引优化]
priority: P1
status: completed
created: 2026-09-10
updated: 2026-09-10
version: 2.0
author: BewhY_L
pre: ["[[SQLAlchemy-ORM核心原理]]", "[[Python-异步编程asyncio]]"]
description: Python操作PostgreSQL完整指南，涵盖psycopg2/asyncpg驱动、连接池、JSONB/数组高级类型、全文搜索、窗口函数CTE、事务锁、索引优化、分区表与物化视图
---

# PostgreSQL Python 高级用法深度指南

> **文档定位**：本文系统讲解 Python 生态中操作 PostgreSQL 的完整知识体系，从基础连接到高级特性优化全覆盖。PostgreSQL 是最强大的开源关系型数据库，Python 通过 psycopg2/psycopg3/asyncpg 三大驱动与其交互。掌握本文内容，你将能够充分利用 PostgreSQL 的高级特性而非仅仅做 CRUD。
>
> **学习目标**：掌握 psycopg2/asyncpg 驱动、连接池管理、JSONB/数组/范围类型、全文搜索、窗口函数与CTE、事务隔离级别、锁机制、索引优化、分区表、物化视图、与FastAPI集成。
>
> **前置知识**：SQL基础、Python异步编程、SQLAlchemy ORM基础

---

## 一、概述与学习路径

### 1.1 PostgreSQL 是什么

**概念解释**：PostgreSQL 是一款开源的对象-关系型数据库系统，以其标准符合性、扩展性和高级特性而闻名。它支持复杂查询、外键、触发器、视图以及存储过程，同时支持 JSON/JSONB 半结构化数据、数组类型、全文搜索等高级功能。

**生活化比喻**：如果把 MySQL 比作一把好用的瑞士军刀（常见任务都能快速完成），PostgreSQL 就像一个专业工作台——工具更齐全、功能更强大，但需要学习如何使用。它适合复杂查询、数据分析、需要严格数据一致性的场景。

**核心价值**：
- **功能最丰富**：支持复杂 SQL、CTE、窗口函数、递归查询、自定义类型
- **数据完整性**：完整 ACID 支持、丰富的约束类型、事务性 DDL
- **扩展性**：丰富的扩展生态（PostGIS、pgvector、pg_trgm 等）
- **性能优秀**：高级查询优化器、多种索引类型、JIT 编译

```python
# 最简连接示例
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="mydb",
    user="postgres",
    password="secret",
)

cur = conn.cursor()
cur.execute("SELECT version()")
version = cur.fetchone()
print(version[0])
# 预期输出：PostgreSQL 16.0 on x86_64-pc-linux-gnu ...

cur.close()
conn.close()
```

### 1.2 Python PostgreSQL 驱动对比

| 驱动 | 类型 | 性能 | 特点 | 适用场景 |
|------|------|------|------|---------|
| **psycopg2** | 同步 | 高 | 最成熟稳定，生态完善 | Flask/Django 同步应用 |
| **psycopg3** | 同步+异步 | 极高 | 新一代，原生异步支持 | 新项目推荐 |
| **asyncpg** | 异步 | 极高 | 纯异步，二进制协议 | FastAPI 异步应用 |
| **SQLAlchemy** | ORM | 中 | ORM 抽象层 | 需要 ORM 的项目 |

```python
# 驱动选型决策树
#
# 需要 ORM 吗？
#   ├── 是 → SQLAlchemy + psycopg2(同步) / asyncpg(异步)
#   └── 否 → 应用是异步的吗？
#              ├── 是（FastAPI/Tornado）→ asyncpg
#              └── 否（Flask/Django）→ psycopg2
#
# 新项目推荐：psycopg3（同时支持同步和异步）
```

### 1.3 学习路线图

```text
PostgreSQL Python 学习路径：

第一阶段：基础连接
  ├── psycopg2 连接与游标
  ├── 参数化查询（防SQL注入）
  ├── CRUD 操作
  └── 连接池管理

第二阶段：高级特性
  ├── JSONB 存储与查询
  ├── 数组类型操作
  ├── 全文搜索
  ├── 窗口函数与 CTE
  └── 事务与隔离级别

第三阶段：性能优化
  ├── 索引类型与选择
  ├── EXPLAIN ANALYZE 分析
  ├── 慢查询优化
  ├── 连接池调优
  └── 批量操作优化

第四阶段：生产实践
  ├── 异步驱动 asyncpg
  ├── SQLAlchemy 集成
  ├── 分区表与物化视图
  ├── 与 FastAPI 集成
  └── 监控与故障排查
```

```python
# 从 MySQL 迁移到 PostgreSQL 的注意事项
# 1. 占位符：MySQL 用 %s 或 ?，PostgreSQL 也用 %s（psycopg2）
# 2. 自增主键：MySQL AUTO_INCREMENT → PostgreSQL SERIAL/BIGSERIAL
# 3. 分页：MySQL LIMIT offset, count → PostgreSQL LIMIT count OFFSET offset
# 4. 字符串连接：MySQL CONCAT() → PostgreSQL ||
# 5. 日期函数：MySQL NOW() → PostgreSQL NOW()（相同）
# 6. 布尔类型：MySQL TINYINT(1) → PostgreSQL BOOLEAN
# 7. 正则：MySQL REGEXP → PostgreSQL ~
# 8. INSERT IGNORE → ON CONFLICT DO NOTHING
```

```python
# SQL 注入防范最佳实践
# ✅ 正确：参数化查询
cur.execute("SELECT * FROM users WHERE email = %s", (user_email,))

# ✅ 正确：标识符用参数化（表名/列名）
cur.execute("SELECT * FROM {} WHERE id = %s".format(
    AsIs(table_name)  # psycopg2.sql.Identifier
), (user_id,))

# ❌ 危险：字符串拼接
# cur.execute(f"SELECT * FROM users WHERE email = '{user_email}'")

# 使用 psycopg2.sql 安全拼接
from psycopg2 import sql
query = sql.SQL("SELECT {} FROM {} WHERE {} = %s").format(
    sql.Identifier("email"),
    sql.Identifier("users"),
    sql.Identifier("id"),
)
cur.execute(query, (1,))
```

```python
# 事务 DDL 支持
# PostgreSQL 支持事务性 DDL（CREATE/ALTER/DROP 在事务中）
# 这意味着 DDL 失败可以回滚！

async def transactional_ddl(conn):
    async with conn.transaction():
        await conn.execute("CREATE TABLE new_table (id INT)")
        await conn.execute("ALTER TABLE new_table ADD COLUMN name TEXT")
        # 如果这里出错，整个 DDL 事务回滚
    # MySQL 的 DDL 是隐式提交，无法回滚
```

```python
# PostgreSQL 数据类型选择速查
# | 业务场景          | 推荐类型      | 原因                  |
# |-------------------|---------------|-----------------------|
# | 主键              | BIGINT/UUID   | 自增或UUIDv7          |
# | 金额              | NUMERIC(10,2) | 精确十进制            |
# | 布尔             | BOOLEAN       | 原生布尔              |
# | 时间戳           | TIMESTAMPTZ   | 带时区                |
# | 短文本           | VARCHAR(255)  | 有限长度              |
# | 长文本           | TEXT          | 无限制                |
# | JSON配置         | JSONB         | 支持索引查询          |
# | 标签数组         | TEXT[]        | 数组类型              |
# | 范围             | TSTZRANGE     | 范围类型              |
# | IP地址           | INET          | 原生类型              |
```

```python
# PostgreSQL 性能监控仪表盘关键指标
# 1. 缓存命中率 > 99%
# 2. 连接使用率 < 80% max_connections
# 3. 慢查询占比 < 5%
# 4. 锁等待时间 < 100ms
# 5. 检查点间隔 = 配置值
# 6. WAL 生成速率 < IOPS 上限
```

> 💡 **深度讲解**：PostgreSQL 与 Python 的结合是 Web 后端开发的黄金组合。PostgreSQL 提供强大的数据存储和查询能力，Python 提供灵活的业务逻辑层。理解 PostgreSQL 的高级特性（JSONB、窗口函数、CTE）能让你在数据库层完成复杂的数据处理，而不需要拉到 Python 层做循环计算——这是从 CRUD 工程师向高级数据库工程师进阶的关键。

> 📝 **本章精简总结**：
> - 核心概念：PostgreSQL 高级特性、驱动选型、连接池
> - 关键原理：进程模型、二进制协议、异步驱动优势
> - 常用操作：连接数据库、执行查询、关闭连接
> - 最佳实践：参数化查询、连接池复用
> - 常见坑点：连接泄漏、SQL 注入
> - 面试高频：驱动选型、连接池大小配置

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：psycopg2 和 asyncpg 的本质区别是什么？
>   - 答案：psycopg2 同步阻塞；asyncpg 原生异步不阻塞事件循环
> - **进阶题（⭐⭐）**：为什么 PostgreSQL 每个连接对应一个后端进程？这对连接池设计有什么影响？
>   - 思考方向：进程模型 vs 线程模型、连接开销
> - **实战题（⭐⭐⭐）**：为一个 FastAPI 异步 API 选择 PostgreSQL 驱动并设计连接池配置。
>   - 提示：asyncpg + create_pool，max_size 根据 CPU 核数调整

---

## 二、PostgreSQL 架构与驱动原理

### 2.1 PostgreSQL 进程模型

**概念解释**：PostgreSQL 采用多进程架构——每个客户端连接由一个独立的后端进程处理。这与 MySQL 的线程模型不同。进程模型的好处是隔离性好（一个连接崩溃不影响其他），缺点是连接开销大（每个进程独立内存）。

```mermaid
graph TB
    subgraph 客户端应用
        A[Python 应用]
        B[连接池<br/>psycopg2.pool / asyncpg]
    end

    subgraph PostgreSQL 服务端
        C[Postmaster<br/>主进程]
        D[Backend Process 1]
        E[Backend Process 2]
        F[Backend Process N]
        G[Shared Buffer<br/>共享内存缓冲区]
        H[WAL<br/>预写日志]
        I[Checkpointer]
        J[Background Writer]
    end

    subgraph 存储
        K[(数据文件)]
        L[(WAL 文件)]
    end

    A --> B
    B -->|TCP 连接| C
    C --> D
    C --> E
    C --> F
    D --> G
    E --> G
    F --> G
    G --> K
    G --> H
    H --> L
    I --> G
    J --> G
```

### 2.2 asyncpg 高性能原理

**概念解释**：asyncpg 是专为异步场景设计的 PostgreSQL 驱动，性能显著优于 psycopg2。

**性能优势来源**：

| 特性 | 说明 | 性能提升 |
|------|------|---------|
| **二进制协议** | 数据以二进制传输，无需文本解析 | 2-5倍 |
| **Prepared Statement** | 自动缓存执行计划 | 重复查询 2-5倍 |
| **零拷贝** | 数据直接从 socket 读入 Python 对象 | 减少内存拷贝 |
| **原生异步** | 基于 asyncio，等待查询不阻塞事件循环 | 并发能力提升 |

```python
# asyncpg vs psycopg2 性能对比（参考值）
# 简单 SELECT 1000 行：
#   psycopg2:    ~50ms
#   asyncpg:     ~15ms  (约3倍快)
#   psycopg3:    ~20ms

# 高频点查询（Prepared Statement）：
#   psycopg2:    ~10ms/次
#   asyncpg:     ~2ms/次  (约5倍快)
```

### 2.3 查询执行流程

```mermaid
flowchart LR
    A[Python 应用] -->|SQL 文本| B[驱动层<br/>psycopg2/asyncpg]
    B -->|TCP/消息| C[Postmaster]
    C --> D[Backend Process]
    D --> E[Parser<br/>语法分析]
    E --> F[Rewriter<br/>查询重写]
    F --> G[Planner<br/>生成执行计划]
    G --> H[Executor<br/>执行查询]
    H --> I[Shared Buffer<br/>读/写数据页]
    I --> J[结果集]
    J -->|二进制/文本| B
    B -->|Python 对象| A
```

```python
# PostgreSQL 架构：WAL 预写日志
# WAL（Write-Ahead Logging）是 PostgreSQL 事务持久性的核心
# 原理：先写日志，再写数据页 → 崩溃恢复
# 类比：先写购物清单，再拿商品 → 清单在，就不会丢东西

# WAL 相关配置
# wal_level = replica       # 日志级别
# max_wal_size = 4GB        # 最大 WAL
# checkpoint_timeout = 5min # 检查点间隔

# 查看 WAL 状态
async def wal_status(conn):
    rows = await conn.fetch("""
        SELECT
            name,
            setting,
            unit
        FROM pg_settings
        WHERE name LIKE 'wal_%'
    """)
    return [dict(r) for r in rows]
```

```python
# 共享缓冲区（Shared Buffers）
# 所有后端进程共享的内存区域，缓存热点数据页
# 推荐设置：物理内存的 25%

# 查看缓存命中率
async def cache_hit_ratio(conn):
    row = await conn.fetchrow("""
        SELECT
            sum(heap_blks_read) as reads,
            sum(heap_blks_hit) as hits,
            round(
                sum(heap_blks_hit) /
                NULLIF(sum(heap_blks_read + heap_blks_hit), 0) * 100,
                2
            ) as hit_ratio
        FROM pg_stat_database
        WHERE datname = current_database()
    """)
    return dict(row)
    # hit_ratio > 99% 表示缓存配置良好
```

```python
# 检查点（Checkpoint）
# 检查点将 Shared Buffer 中的脏页刷盘
# 频繁检查点 → IO 压力大
# 不频繁检查点 → 恢复时间长

# 查看检查点统计
async def checkpoint_stats(conn):
    row = await conn.fetchrow("SELECT * FROM pg_stat_bgwriter")
    return dict(row)
```

> 💡 **深度讲解**：理解 PostgreSQL 架构的关键是进程模型和共享内存。每个连接一个后端进程意味着连接数不能无限增长（每个进程约占 5-10MB 内存），这就是连接池重要的原因。Shared Buffer 是所有后端进程共享的内存区域，缓存了热点数据页——调大 shared_buffers 能显著提升读性能但不能太大（推荐 25% 内存）。WAL 预写日志保证了事务持久性。

> 📝 **本章精简总结**：
> - 核心概念：进程模型、Shared Buffer、WAL、二进制协议
> - 关键原理：一连接一进程、共享内存缓存、异步驱动性能优势
> - 常用操作：连接、查询、关闭
> - 最佳实践：连接池复用、用 asyncpg 处理异步高并发
> - 常见坑点：连接数过多导致内存爆炸
> - 面试高频：PostgreSQL 进程模型、asyncpg 性能原理

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：PostgreSQL 为什么需要连接池？
>   - 答案：每个连接一个后端进程，创建/销毁开销大
> - **进阶题（⭐⭐）**：asyncpg 为什么比 psycopg2 快？
>   - 思考方向：二进制协议、Prepared Statement、原生异步
> - **实战题（⭐⭐⭐）**：一个 FastAPI 应用需要多少数据库连接？如何计算？
>   - 提示：连接数 = (CPU核数 × 2 + 磁盘数) × 应用实例数，不超过 max_connections

---

## 三、psycopg2 深度使用

### 3.1 连接与游标

**概念解释**：psycopg2 是 PostgreSQL 最成熟的 Python 驱动。Connection 对象表示数据库连接，Cursor 对象用于执行 SQL 和获取结果。

```python
# psycopg2 基础连接
import psycopg2
from psycopg2.extras import RealDictCursor, RealDictRow

# 方式一：连接参数
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="mydb",
    user="postgres",
    password="secret",
    connect_timeout=10,
)

# 方式二：DSN 连接字符串
# conn = psycopg2.connect("postgresql://postgres:secret@localhost:5432/mydb")

# 使用字典游标（返回 dict 而非 tuple）
cur = conn.cursor(cursor_factory=RealDictCursor)

# 执行查询
cur.execute("SELECT id, name, email FROM users WHERE id = %s", (1,))

# 获取结果
user = cur.fetchone()  # 返回 RealDictRow（类似 dict）
print(user["name"])    # 预期输出：张三
print(user["email"])   # 预期输出：zhangsan@example.com

cur.close()
conn.close()
```

```python
# 参数化查询（防 SQL 注入）
# ❌ 危险：字符串拼接
# cur.execute(f"SELECT * FROM users WHERE name = '{user_input}'")
# 如果 user_input = "'; DROP TABLE users;--" → 严重安全问题

# ✅ 正确：参数化查询
cur.execute(
    "SELECT * FROM users WHERE name = %s AND status = %s",
    ("张三", "active"),
)
# psycopg2 自动转义参数，防止 SQL 注入

# 注意：psycopg2 的占位符是 %s（不是 ? 或 :name）
# 多个参数用元组传递
```

### 3.2 CRUD 操作

```python
# CREATE（插入）
cur.execute(
    "INSERT INTO users (email, name, age) VALUES (%s, %s, %s) RETURNING id, created_at",
    ("new@example.com", "新用户", 25),
)
new_user = cur.fetchone()
print(f"新用户ID: {new_user['id']}")
conn.commit()  # 必须提交事务
```

```python
# READ（查询）
# 单条
cur.execute("SELECT * FROM users WHERE id = %s", (1,))
user = cur.fetchone()

# 多条
cur.execute("SELECT * FROM users WHERE status = %s ORDER BY created_at DESC LIMIT %s", ("active", 10))
users = cur.fetchall()

# 迭代（大结果集）
cur.execute("SELECT * FROM large_table")
for row in cur:  # 逐行迭代，不一次性加载到内存
    process(row)
```

```python
# UPDATE（更新）
cur.execute(
    "UPDATE users SET name = %s, updated_at = NOW() WHERE id = %s",
    ("新名字", 1),
)
print(f"更新了 {cur.rowcount} 行")  # rowcount 返回影响行数
conn.commit()
```

```python
# DELETE（删除）
cur.execute("DELETE FROM users WHERE id = %s", (999,))
print(f"删除了 {cur.rowcount} 行")
conn.commit()
```

### 3.3 批量操作

```python
# 批量插入：execute_values（比循环 execute 快 10 倍）
from psycopg2.extras import execute_values

users_data = [
    ("user1@example.com", "用户1", 20),
    ("user2@example.com", "用户2", 25),
    ("user3@example.com", "用户3", 30),
]

execute_values(
    cur,
    "INSERT INTO users (email, name, age) VALUES %s",
    users_data,
    template="(%s, %s, %s)",  # 可选，默认自动推断
    page_size=1000,  # 每批插入1000行
)
conn.commit()
```

```python
# 批量插入并返回所有 ID
from psycopg2.extras import execute_values

cur = conn.cursor()
execute_values(
    cur,
    "INSERT INTO users (email, name) VALUES %s RETURNING id",
    [("a@test.com", "A"), ("b@test.com", "B")],
)
new_ids = [row[0] for row in cur.fetchall()]
print(f"新插入的ID: {new_ids}")
```

```python
# COPY 协议（最快的批量导入）
# 适合百万行级数据导入
with open('users.csv', 'r') as f:
    cur.copy_expert(
        "COPY users (email, name) FROM STDIN WITH CSV HEADER",
        f,
    )
conn.commit()
# 预期：百万行数据几秒内完成导入
```

```python
# psycopg3（psycopg）新一代驱动
# 安装：pip install "psycopg[binary,pool]"
import psycopg

# psycopg3 同步用法
with psycopg.connect("postgresql://user:pass@localhost/db") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (1,))
        user = cur.fetchone()

# psycopg3 异步用法
import psycopg

async def async_query():
    async with await psycopg.AsyncConnection.connect(
        "postgresql://user:pass@localhost/db"
    ) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM users")
            rows = await cur.fetchall()

# psycopg3 vs psycopg2 优势：
# - 原生异步支持
# - 更好的类型映射
# - 二进制协议支持
# - 连接池内置
```

```python
# psycopg2 RealDictCursor 详解
from psycopg2.extras import RealDictCursor

# 使用 RealDictCursor 返回字典而不是元组
with conn.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute("SELECT id, name, email FROM users WHERE id = %s", (1,))
    user = cur.fetchone()
    print(user['name'])  # 通过列名访问
    print(user['email'])

# RealDictRow 支持 dict 操作
print(user.keys())   # ['id', 'name', 'email']
print(user.values()) # (1, '张三', 'zhangsan@example.com')

# 全局设置默认字典游标
# conn = psycopg2.connect(..., cursor_factory=RealDictCursor)
```

```python
# psycopg2 错误处理
import psycopg2
from psycopg2 import OperationalError, IntegrityError, ProgrammingError

try:
    cur.execute("INSERT INTO users (email) VALUES (%s)", ("test@test.com",))
    conn.commit()
except IntegrityError as e:
    # 唯一约束冲突（重复 email）
    conn.rollback()
    print(f"数据冲突: {e}")
except OperationalError as e:
    # 连接错误
    conn.rollback()
    print(f"连接失败: {e}")
except ProgrammingError as e:
    # SQL 语法错误
    conn.rollback()
    print(f"SQL错误: {e}")
```

```python
# psycopg2 服务端游标（大结果集处理）
# 当查询返回百万行时，一次性 fetchall() 会 OOM
# 使用命名游标分批获取

def iterate_large_table(conn, table: str, batch_size: int = 1000):
    """服务端游标：分批处理大表"""
    with conn.cursor(name='server_cursor') as cur:
        cur.itersize = batch_size
        cur.execute(f"SELECT * FROM {table}")
        total = 0
        for row in cur:
            process_row(row)
            total += 1
        print(f"处理了 {total} 行")

# 服务端游标 vs 客户端游标：
# 客户端游标：全部结果加载到客户端内存 → 大结果集 OOM
# 服务端游标：结果保留在服务端，分批拉取 → 内存稳定
```

```python
# psycopg2 复制操作（COPY）
# COPY 是 PostgreSQL 最快的数据导入导出方式

# 从文件导入
def copy_from_csv(conn, csv_path: str, table: str):
    with open(csv_path, 'r') as f:
        conn.cursor.copy_from(f, table, sep=',', null='NULL')
    conn.commit()

# 导出到文件
def copy_to_csv(conn, table: str, csv_path: str):
    with open(csv_path, 'w') as f:
        conn.cursor.copy_to(f, table, sep=',')

# 预期性能：百万行 CSV 导入 < 10秒
```

```python
# psycopg2 通知监听
import select
import psycopg2

def listen_notification(conn, channel: str):
    """监听 PostgreSQL NOTIFY"""
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"LISTEN {channel}")
    print(f"正在监听 {channel}...")

    while True:
        if select.select([conn], [], [], 5) == ([], [], []):
            continue  # 超时
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            print(f"收到通知: channel={notify.channel} payload={notify.payload}")
```

> ❌ **常见坑点**：psycopg2 中未 commit 的事务会一直持有锁。如果执行了 INSERT/UPDATE 但忘记 commit，其他连接的查询会被阻塞。**正确做法**：使用上下文管理器自动管理事务，或确保每个写操作后 commit/rollback。

```python
# 上下文管理器自动管理事务
with conn:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO users VALUES (...)")
        cur.execute("UPDATE accounts SET ...")
# 退出 with 块时自动 commit，异常时自动 rollback
```

### 3.4 服务端游标（大结果集）

```python
# 当查询返回百万行时，一次性 fetchall() 会 OOM
# 使用服务端游标（命名游标）分批获取

def process_large_table(table_name: str, batch_size: int = 1000):
    """使用服务端游标分批处理大表"""
    with conn.cursor(name='server_side_cursor') as cur:
        cur.itersize = batch_size  # 每次从服务端获取的行数
        cur.execute(f"SELECT * FROM {table_name}")

        total = 0
        for row in cur:
            process_row(row)
            total += 1
            if total % 10000 == 0:
                print(f"已处理 {total} 行")

    print(f"总计处理 {total} 行")
```

> 💡 **深度讲解**：psycopg2 是 Python PostgreSQL 生态的基石。核心要点：(1) 参数化查询防注入——永远不要字符串拼接 SQL；(2) 事务管理——写操作必须 commit，使用上下文管理器自动管理；(3) 批量操作用 execute_values 而非循环——性能提升 10 倍以上；(4) 大结果集用服务端游标——避免内存爆炸。这些是从"能用"到"好用"的关键差异。

> 📝 **本章精简总结**：
> - 核心概念：Connection/Cursor、参数化查询、服务端游标
> - 关键原理：事务自动管理、批量插入优化、防 SQL 注入
> - 常用操作：execute/fetchone/fetchall、execute_values、copy_expert
> - 最佳实践：参数化查询、上下文管理器、批量操作
> - 常见坑点：忘记 commit 导致锁、fetchall() 大结果集 OOM
> - 面试高频：SQL 注入防范、批量插入优化

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：psycopg2 的占位符是什么？为什么不用 ? 或 :name？
>   - 答案：%s，psycopg2 风格，与 Python 字符串格式化语法一致
> - **进阶题（⭐⭐）**：execute_values 为什么比循环 execute 快？
>   - 思考方向：单条 INSERT vs 多值 INSERT、网络往返次数
> - **实战题（⭐⭐⭐）**：需要将一个 100 万行的 CSV 文件导入 PostgreSQL，要求 30 秒内完成。设计方案。
>   - 提示：COPY 协议 + 临时表 + 批量插入

---

## 四、asyncpg 异步驱动

### 4.1 异步连接池

**概念解释**：asyncpg 是专为异步 Python 设计的 PostgreSQL 驱动，在 FastAPI 等异步框架中性能最优。它使用 PostgreSQL 扩展查询协议，支持二进制数据传输和 Prepared Statement 缓存。

```python
# asyncpg 连接池创建
import asyncio
import asyncpg

async def create_db_pool():
    """创建异步连接池"""
    pool = await asyncpg.create_pool(
        dsn="postgresql://postgres:secret@localhost:5432/mydb",
        min_size=5,          # 最小空闲连接数
        max_size=20,         # 最大连接数
        max_queries=50000,   # 连接上执行多少查询后重建
        max_inactive_connection_lifetime=300,  # 空闲连接5分钟后回收
        command_timeout=30,  # 单条命令超时30秒
    )
    return pool

# 预期使用：
# pool = await create_db_pool()
# async with pool.acquire() as conn:
#     result = await conn.fetchval("SELECT 1")
# print(result)  # 1
```

### 4.2 CRUD 操作

```python
# asyncpg CRUD 示例
class UserRepository:
    def __init__(self, pool):
        self.pool = pool

    async def create(self, email: str, name: str, age: int = None) -> dict:
        """创建用户"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO users (email, name, age)
                VALUES ($1, $2, $3)
                RETURNING id, email, name, age, created_at
                """,
                email, name, age,
            )
            return dict(row)

    async def get_by_id(self, user_id: int) -> dict | None:
        """根据 ID 查询用户"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, email, name, age FROM users WHERE id = $1",
                user_id,
            )
            return dict(row) if row else None

    async def list_active(self, limit: int = 20, offset: int = 0) -> list[dict]:
        """查询活跃用户列表"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, email, name, created_at
                FROM users
                WHERE status = 'active'
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
                """,
                limit, offset,
            )
            return [dict(r) for r in rows]

    async def update_name(self, user_id: int, name: str) -> bool:
        """更新用户名"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE users SET name = $1, updated_at = NOW() WHERE id = $2",
                name, user_id,
            )
            # result 格式："UPDATE 1"
            return "UPDATE 1" in result

    async def delete(self, user_id: int) -> bool:
        """删除用户"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM users WHERE id = $1",
                user_id,
            )
            return "DELETE 1" in result
```

```python
# asyncpg 的占位符：$1, $2, $3（不是 %s）
# 这是 asyncpg 与 psycopg2 的重要区别

# psycopg2: cur.execute("INSERT INTO t VALUES (%s, %s)", (a, b))
# asyncpg:  await conn.execute("INSERT INTO t VALUES ($1, $2)", a, b)

# asyncpg 自动序列化：
# Python dict → JSONB
# Python list → array
# Python datetime → timestamptz
# Python uuid → uuid
```

### 4.3 事务管理

```python
# asyncpg 事务（自动管理）
async def transfer_money(from_id: int, to_id: int, amount: float):
    """转账事务：两个操作要么都成功，要么都失败"""
    async with self.pool.acquire() as conn:
        async with conn.transaction():
            # 扣减转出账户
            await conn.execute(
                "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
                amount, from_id,
            )
            # 增加转入账户
            await conn.execute(
                "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
                amount, to_id,
            )
            # 记录交易流水
            await conn.execute(
                "INSERT INTO transactions (from_id, to_id, amount) VALUES ($1, $2, $3)",
                from_id, to_id, amount,
            )
            # 退出 transaction 上下文时自动 commit
            # 任何异常都会自动 rollback
```

```python
# 嵌套事务（保存点）
async def complex_operation():
    async with self.pool.acquire() as conn:
        async with conn.transaction():
            # 外层事务
            await do_step_one(conn)

            try:
                async with conn.transaction():  # 嵌套 = SAVEPOINT
                    # 内层事务（保存点）
                    await do_step_two(conn)
                    await do_risky_thing(conn)  # 可能失败
            except Exception:
                # 内层回滚到保存点，外层继续
                logger.warning("步骤二失败，跳过继续")

            await do_step_three(conn)
```

### 4.4 类型自动映射

```python
# asyncpg 自动类型映射
# Python ↔ PostgreSQL 自动转换

# dict ↔ JSONB
await conn.execute(
    "INSERT INTO products (name, attributes) VALUES ($1, $2)",
    "iPhone", {"color": "black", "storage": "256GB"},  # dict 自动→JSONB
)

row = await conn.fetchrow("SELECT attributes FROM products WHERE name = $1", "iPhone")
print(row["attributes"])  # Python dict: {"color": "black", "storage": "256GB"}

# list ↔ array
await conn.execute(
    "INSERT INTO posts (title, tags) VALUES ($1, $2)",
    "Post Title", ["python", "tutorial"],  # list 自动→text[]
)

# datetime ↔ timestamptz
from datetime import datetime, timezone
await conn.execute(
    "INSERT INTO events (name, event_time) VALUES ($1, $2)",
    "Launch", datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
)

# UUID ↔ uuid
import uuid
user_uuid = uuid.uuid4()
await conn.execute("INSERT INTO users (id) VALUES ($1)", user_uuid)
```

```python
# 自定义类型编解码器
from asyncpg import custom

# 注册自定义类型（如 PostgreSQL ENUM）
async def setup_enum(conn):
    # 方式一：使用 PGJSONB 自动处理 dict
    # 方式二：自定义编解码器
    pass

# 使用 record_class 返回 dict
async with pool.acquire() as conn:
    conn.set_type_codec(
        'jsonb',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog',
    )
```

```python
# asyncpg 批量插入
async def batch_insert_asyncpg(conn, users: list[dict]):
    """asyncpg 批量插入（executemany）"""
    # asyncpg 的 executemany 比循环 execute 快很多
    await conn.executemany(
        "INSERT INTO users (email, name, age) VALUES ($1, $2, $3)",
        [(u["email"], u["name"], u.get("age")) for u in users],
    )

# asyncpg COPY 协议
async def copy_from_csv(conn, csv_path: str, table: str):
    """COPY 批量导入（最快的方式）"""
    with open(csv_path, 'r') as f:
        await conn.copy_from_table(
            table_name=table,
            source=f,
            columns=["email", "name"],
            format="csv",
            header=True,
        )
```

```python
# asyncpg 监听通知（LISTEN/NOTIFY）
# 实现数据库级别的实时通知
import asyncio
import asyncpg

async def notification_listener():
    """监听 PostgreSQL NOTIFY 事件"""
    conn = await asyncpg.connect(
        "postgresql://postgres:secret@localhost:5432/mydb"
    )

    # 定义通知回调
    async def listen_user_created():
        await conn.add_listener(
            "user_created",
            lambda connection, pid, channel, payload: print(
                f"新用户: {payload}"
            )
        )

    await listen_user_created()
    print("正在监听 user_created 频道...")
    while True:
        await asyncio.sleep(1)

# 发送通知的端
async def notify_user_created(conn, user_id: int):
    await conn.execute(f"NOTIFY user_created, '{user_id}'")
```

```python
# asyncpg 自定义类型转换器
from asyncpg import custom

async def setup_custom_types(conn):
    """注册自定义类型转换"""
    # 处理 PostgreSQL INET 类型
    await conn.set_type_codec(
        'inet',
        encoder=str,
        decoder=str,
        schema='pg_catalog',
    )

# 使用 JSONB 类型
async def jsonb_query(conn):
    # asyncpg 自动将 JSONB 转为 Python dict
    row = await conn.fetchrow(
        "SELECT attributes FROM products WHERE id = $1", 1
    )
    attrs = row['attributes']  # 自动是 dict
    print(attrs['color'])
```

```python
# asyncpg Prepared Statement 详解
# asyncpg 自动缓存 SQL 的执行计划
# 首次查询编译计划，后续查询直接复用

# 自动缓存（默认开启）
await conn.execute("SELECT * FROM users WHERE id = $1", 1)  # 编译
await conn.execute("SELECT * FROM users WHERE id = $1", 2)  # 复用

# 手动 Prepared Statement
stmt = await conn.prepare("SELECT * FROM users WHERE id = $1")
row = await stmt.fetchrow(1)
row = await stmt.fetchrow(2)

# 关闭 statement cache（特殊场景）
pool = await asyncpg.create_pool(
    dsn=dsn,
    statement_cache_size=0,  # 关闭缓存
)
```

```python
# asyncpg 类型转换详解
# asyncpg 自动处理 Python ↔ PostgreSQL 类型映射

# Python int ↔ INTEGER/BIGINT
await conn.fetchval("SELECT $1::int", 42)  # → 42

# Python float ↔ NUMERIC/REAL
await conn.fetchval("SELECT $1::float", 3.14)  # → 3.14

# Python str ↔ TEXT/VARCHAR
await conn.fetchval("SELECT $1::text", "hello")  # → "hello"

# Python bool ↔ BOOLEAN
await conn.fetchval("SELECT $1::bool", True)  # → True

# Python datetime ↔ TIMESTAMPTZ
from datetime import datetime, timezone
await conn.fetchval("SELECT $1::timestamptz", datetime.now(timezone.utc))

# Python dict ↔ JSONB
await conn.fetchval("SELECT $1::jsonb", {"key": "value"})  # → {"key": "value"}

# Python list ↔ ARRAY
await conn.fetchval("SELECT $1::int[]", [1, 2, 3])  # → [1, 2, 3]
```

```python
# asyncpg 服务端游标
async def iterate_large_dataset(conn):
    """asyncpg 服务端游标"""
    async with conn.transaction():
        cur = await conn.cursor("SELECT * FROM large_table ORDER BY id")
        while True:
            rows = await cur.fetch(1000)
            if not rows:
                break
            for row in rows:
                process(row)
```

> ❌ **常见坑点**：asyncpg 的占位符是 `$1, $2` 而不是 psycopg2 的 `%s`。从 psycopg2 迁移到 asyncpg 时最容易犯的错误。**正确做法**：搜索替换所有 `%s` 为 `$N`，或使用命名参数 `$name`。

> 💡 **深度讲解**：asyncpg 的性能优势来自三个层面：协议层（二进制传输减少解析开销）、执行计划层（Prepared Statement 缓存避免重复编译）、异步层（等待查询时释放事件循环）。在 FastAPI 异步应用中使用 asyncpg，可以充分利用 Python 的异步能力，单机并发处理能力比 psycopg2 高数倍。asyncpg 还自动处理 Python ↔ PostgreSQL 类型映射，不需要手动序列化/反序列化。

> 📝 **本章精简总结**：
> - 核心概念：asyncpg 连接池、$N 占位符、自动类型映射
> - 关键原理：二进制协议、Prepared Statement、异步事务
> - 常用操作：pool.acquire()、conn.fetchrow/fetch/execute
> - 最佳实践：连接池管理、async with 自动事务
> - 常见坑点：占位符 $N vs %s、连接泄漏
> - 面试高频：asyncpg vs psycopg2 性能、异步连接池

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：asyncpg 的占位符语法是什么？
>   - 答案：$1, $2, $3（位置参数）
> - **进阶题（⭐⭐）**：asyncpg 的 Prepared Statement 缓存是什么？为什么能提升性能？
>   - 思考方向：执行计划编译开销、重复查询缓存
> - **实战题（⭐⭐⭐）**：将一个 psycopg2 同步的数据访问层迁移到 asyncpg 异步。列出所有需要修改的地方。
>   - 提示：占位符语法、连接池、事务管理、async/await 语法

---

## 五、SQLAlchemy 与 PostgreSQL

### 5.1 SQLAlchemy 2.0 异步集成

**概念解释**：SQLAlchemy 是 Python 最流行的 ORM，2.0 版本原生支持异步。结合 asyncpg 驱动，可以在异步应用中使用 ORM。

```python
# SQLAlchemy 2.0 + asyncpg 异步引擎
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func
import datetime

# 创建异步引擎
async_engine = create_async_engine(
    "postgresql+asyncpg://postgres:secret@localhost:5432/mydb",
    echo=False,                # SQL 日志（开发时设 True）
    pool_size=10,              # 连接池大小
    max_overflow=20,           # 最大溢出连接
    pool_recycle=3600,         # 连接1小时后回收
    pool_pre_ping=True,        # 获取连接前检测是否有效
)

# 创建异步 Session 工厂
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,    # commit 后不自动过期对象
)

Base = declarative_base()

# 定义模型
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
```

```python
# SQLAlchemy 异步 CRUD
class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, email: str, name: str) -> User:
        """创建用户"""
        user = User(email=email, name=name)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user(self, user_id: int) -> User | None:
        """查询用户"""
        from sqlalchemy import select
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_users(self, limit: int = 20) -> list[User]:
        """用户列表"""
        from sqlalchemy import select
        result = await self.session.execute(
            select(User).order_by(User.created_at.desc()).limit(limit)
        )
        return result.scalars().all()

    async def update_user(self, user_id: int, name: str) -> User | None:
        """更新用户"""
        user = await self.get_user(user_id)
        if user:
            user.name = name
            await self.session.commit()
            await self.session.refresh(user)
        return user
```

### 5.2 PostgreSQL 特定类型

```python
# SQLAlchemy 映射 PostgreSQL 高级类型
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import (
    JSONB, ARRAY, UUID, INET, CIDR,
    TSVECTOR, INTERVAL, ENUM,
)
import uuid

class Article(Base):
    __tablename__ = 'articles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    content = Column(String)
    tags = Column(ARRAY(String))              # text[]
    metadata_ = Column(JSONB)                  # JSONB
    search_vector = Column(TSVECTOR)          # 全文搜索向量
    view_count = Column(Integer, default=0)
```

```python
# JSONB 查询（SQLAlchemy 语法）
from sqlalchemy import select, cast, String

# 查询 JSONB 字段
stmt = select(Product).where(
    Product.metadata_['color'].as_string() == 'red'
)

# JSONB 包含查询
stmt = select(Product).where(
    Product.metadata_.contains({"brand": "Apple", "category": "phone"})
)

# JSONB 路径查询
stmt = select(Product).where(
    Product.metadata_['specs']['storage'].as_integer() >= 256
)
```

```python
# SQLAlchemy 查询示例（2.0 风格）
from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

async def query_examples(session: AsyncSession):
    # 基本查询
    stmt = select(User).where(User.email == "test@example.com")
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    # 多条件查询
    stmt = select(User).where(
        User.status == "active",
        User.created_at >= "2026-01-01"
    ).order_by(desc(User.created_at)).limit(10)

    # 聚合查询
    stmt = select(
        User.status,
        func.count(User.id).label("count")
    ).group_by(User.status)

    # JOIN 查询
    from sqlalchemy import join
    stmt = select(User, Order).join(
        Order, User.id == Order.user_id
    ).where(User.id == 1)

    # 子查询
    subq = select(Order.user_id).group_by(
        Order.user_id
    ).having(func.count(Order.id) > 5).subquery()
    stmt = select(User).where(User.id.in_(subq))
```

```python
# SQLAlchemy JSONB 查询进阶
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import cast, String

# JSONB 路径查询
stmt = select(Product).where(
    Product.data['specs']['ram'].astext.cast(Integer) >= 8
)

# JSONB 包含查询
stmt = select(Product).where(
    Product.data.contains({"category": "electronics", "in_stock": True})
)

# JSONB 键存在
stmt = select(Product).where(
    Product.data.has_key("warranty")
)
```

```python
# SQLAlchemy 迁移（Alembic）
# alembic init migrations
# alembic revision --autogenerate -m "create users table"
# alembic upgrade head

# 编程式迁移
# from alembic.config import Config
# from alembic import command
# alembic_cfg = Config("alembic.ini")
# command.upgrade(alembic_cfg, "head")
```

```python
# SQLAlchemy 关系定义
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]

    # 关系：一个用户有多个订单
    orders: Mapped[List["Order"]] = relationship(back_populates="user")

class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float]

    # 关系：多个订单属于一个用户
    user: Mapped["User"] = relationship(back_populates="orders")
```

```python
# SQLAlchemy 预加载（避免 N+1 查询）
from sqlalchemy.orm import selectinload, joinedload

# N+1 问题示例
async def bad_query(session):
    # 1次查询
    users = await session.execute(select(User))
    for user in users.scalars():
        # N次查询每个用户的订单
        orders = await session.execute(
            select(Order).where(Order.user_id == user.id)
        )

# ✅ 解决：selectinload（二次查询，IN 批量）
async def good_query(session):
    stmt = select(User).options(selectinload(User.orders))
    result = await session.execute(stmt)
    users = result.scalars().unique()
    # 只有2次查询：1次查用户 + 1次查所有订单（IN user_ids）
    for user in users:
        print(user.orders)  # 已预加载，无额外查询
```

```python
# SQLAlchemy 异步会话管理
from contextlib import asynccontextmanager

@asynccontextmanager
async def transactional_session():
    """带事务的会话上下文管理器"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# 使用
async with transactional_session() as session:
    user = User(name="test")
    session.add(user)
    await session.flush()  # 获取 ID 但不提交
    order = Order(user_id=user.id, amount=99.9)
    session.add(order)
    # 退出时自动 commit
```

```python
# SQLAlchemy 连接池配置（生产推荐）
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=10,          # 基础连接数
    max_overflow=20,       # 突发最大连接数
    pool_timeout=30,       # 获取连接超时秒数
    pool_recycle=3600,     # 1小时回收（防止连接断开）
    pool_pre_ping=True,    # 每次使用前检测连接活性
    echo=False,            # 生产关闭SQL日志
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,  # commit后不自动刷新
)
```

```python
# SQLAlchemy 性能优化技巧
# 1. 使用 selectinload 避免 N+1
# 2. 使用 load_only 只加载需要的列
# 3. 使用 AsyncSession.execute 批量查询
# 4. 使用 bulk_insert_mappings 批量插入
# 5. 使用 update().where() 批量更新
# 6. 使用 delete().where() 批量删除
```

> 💡 **深度讲解**：SQLAlchemy 在 PostgreSQL 上的最佳实践是使用 2.0 异步 API + asyncpg 驱动。关键配置：`pool_pre_ping=True` 防止获取到已断开的连接；`expire_on_commit=False` 避免 commit 后访问属性触发额外查询。PostgreSQL 特定类型（JSONB、ARRAY、UUID）通过 `sqlalchemy.dialects.postgresql` 模块映射，ORM 层自动处理 Python ↔ SQL 类型转换。

> 📝 **本章精简总结**：
> - 核心概念：异步引擎、AsyncSession、PostgreSQL 方言类型
> - 关键原理：连接池配置、JSONB/ARRAY 类型映射
> - 常用操作：create_async_engine、sessionmaker、select()
> - 最佳实践：pool_pre_ping、expire_on_commit=False
> - 常见坑点：同步/异步引擎混用、commit 后访问过期对象
> - 面试高频：SQLAlchemy 异步配置、JSONB ORM 查询

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：`pool_pre_ping=True` 的作用是什么？
>   - 答案：获取连接前发送探测查询，确保连接有效
> - **进阶题（⭐⭐）**：为什么 `expire_on_commit=False` 很重要？
>   - 思考方向：commit 后对象过期→再次访问触发额外 SELECT
> - **实战题（⭐⭐⭐）**：用 SQLAlchemy 2.0 + asyncpg 实现一个完整的用户 CRUD 服务，含分页查询。
>   - 提示：select() + limit/offset + AsyncSession

---

## 六、连接池管理

### 6.1 为什么需要连接池

**概念解释**：数据库连接池复用已建立的数据库连接，避免每次查询都新建连接的开销（TCP握手+认证+进程创建约10-50ms），是高并发数据库访问的核心优化。

```python
# psycopg2 连接池
from psycopg2 import pool
import contextlib

# 创建连接池
connection_pool = pool.SimpleConnectionPool(
    minconn=5,       # 最小空闲连接
    maxconn=20,      # 最大连接数
    host="localhost",
    dbname="mydb",
    user="postgres",
    password="secret",
)

@contextlib.contextmanager
def get_db_connection():
    """从连接池获取连接，用完自动归还"""
    conn = connection_pool.getconn()
    try:
        yield conn
        conn.commit()  # 成功自动提交
    except Exception:
        conn.rollback()  # 失败自动回滚
        raise
    finally:
        connection_pool.putconn(conn)  # 归还连接
```

```python
# asyncpg 连接池
import asyncpg

async def init_pool():
    """初始化 asyncpg 连接池"""
    pool = await asyncpg.create_pool(
        dsn="postgresql://postgres:secret@localhost:5432/mydb",
        min_size=5,
        max_size=20,
        max_inactive_connection_lifetime=300,
        command_timeout=30,
    )
    return pool

# 使用连接池
async def query_user(pool, user_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        )
```

### 6.2 连接池大小计算

```text
连接池大小计算公式：

单实例连接池 max_size = CPU核心数 × 2 + 磁盘数
通常取 5-20（不要太大！）

总连接数（多实例部署）：
  应用实例数 × 单实例max_size < PostgreSQL max_connections
  （通常 max_connections = 100-500）

示例：
  4核CPU，1个磁盘 → max_size = 4*2+1 = 9
  3个应用实例 → 总连接数 = 3*9 = 27 < max_connections=100 ✓
  20个应用实例 → 总连接数 = 20*9 = 180 > max_connections=100 ✗
  → 这种情况需要 PgBouncer 连接池中间件
```

### 6.3 PgBouncer 连接池中间件

**概念解释**：PgBouncer 是 PostgreSQL 专用的连接池中间件，支持在应用服务器和 PostgreSQL 之间维护大量客户端连接，但只打开少量后端连接到 PostgreSQL。

```text
为什么需要 PgBouncer：

场景：20个应用实例 × 每实例 max_size=10 = 200 连接
      PostgreSQL max_connections=100
      → 连接数超限！

PgBouncer 方案：
  应用 → PgBouncer(200个客户端连接) → PostgreSQL(10个后端连接)

PgBouncer 池模式：
  - session：会话级（连接整个事务持续）
  - transaction：事务级（事务结束后归还连接）← 推荐
  - statement：语句级（每条语句后归还）← 极少用
```

```ini
# pgbouncer.ini 关键配置
[databases]
mydb = host=localhost dbname=mydb

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0

auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

pool_mode = transaction     # 事务级池化
max_client_conn = 1000      # 最大客户端连接
default_pool_size = 20      # 每个数据库的后端连接数
```

```python
# 连接池监控
async def pool_stats(pool):
    """查看连接池状态"""
    info = {
        "min_size": pool._minsize,
        "max_size": pool._maxsize,
        "size": pool._queue.qsize() + pool._used,  # 总连接数
        "idle": pool._queue.qsize(),  # 空闲连接数
        "in_use": pool._used,  # 使用中连接数
    }
    return info

# 连接泄漏检测
# 如果 in_use 持续增长不释放，说明有连接泄漏
# 检查：是否所有 acquire() 都有对应的 release()
# 最佳实践：始终用 async with pool.acquire() as conn:
```

```python
# ThreadedConnectionPool（多线程同步应用）
from psycopg2.pool import ThreadedConnectionPool

# 多线程安全的连接池
pool = ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    dbname="mydb",
    user="postgres",
    password="secret",
)

# 在多线程中使用
import threading

def worker_thread():
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
    finally:
        pool.putconn(conn)

threads = [threading.Thread(target=worker_thread) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

```python
# 连接池健康检查
async def check_pool_health(pool):
    """检查连接池中连接的健康状态"""
    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            return result == 1
    except Exception as e:
        return False
```

```python
# 连接池配置最佳实践汇总
# 1. psycopg2 SimpleConnectionPool（同步应用）
# pool = SimpleConnectionPool(5, 20, ...)

# 2. asyncpg create_pool（异步应用）
# pool = await asyncpg.create_pool(..., min_size=5, max_size=20)

# 3. SQLAlchemy pool_size
# engine = create_async_engine(..., pool_size=10, max_overflow=20)

# 连接池参数对照表：
# | 参数           | psycopg2    | asyncpg     | SQLAlchemy  |
# |----------------|-------------|-------------|-------------|
# | 最小连接       | minconn     | min_size    | pool_size   |
# | 最大连接       | maxconn     | max_size    | pool_size+max_overflow |
# | 连接超时       | -           | timeout     | pool_timeout|
# | 空闲回收       | -           | max_inactive| pool_recycle|
# | 连接检测       | -           | -           | pool_pre_ping|
```

```python
# PgBouncer 事务级池化原理
# 客户端连接 PgBouncer → PgBouncer 从后端连接池获取连接
# 一个事务期间使用同一个后端连接
# 事务结束后，后端连接归还池，给其他客户端连接使用

# 效果：
# 1000个客户端连接 → PgBouncer → 20个后端连接
# 1000个客户端共享20个后端连接
# 大幅降低 PostgreSQL 连接数

# 注意：PgBouncer transaction 模式不支持 Prepared Statement
# 因为不同事务可能复用同一个后端连接，statement 会冲突
# asyncpg 需要设置 statement_cache_size=0（在 PgBouncer 后面）
```

```python
# asyncpg 连接池生产配置
# pool = await asyncpg.create_pool(
#     dsn="postgresql://user:pass@host/db",
#     min_size=5,          # 最小空闲连接
#     max_size=20,         # 最大连接
#     max_queries=50000,   # 连接最大查询数后重建
#     max_inactive_connection_lifetime=300,  # 空闲5分钟回收
#     timeout=30,          # 获取连接超时
#     command_timeout=60,  # 单命令超时
#     statement_cache_size=1000,  # Prepared Statement缓存
# )
```

```python
# 连接泄漏排查
# 症状：pool._used 持续增长，最终 max_size 耗尽
# 排查：
# 1. 检查所有 acquire() 是否都有 release()
# 2. 检查是否在异常路径忘记释放
# 3. 最佳实践：永远用 async with pool.acquire() as conn:
# 4. 监控：定期记录 pool._used，设置告警阈值
```

> ❌ **常见坑点**：连接池过大超过 PostgreSQL 的 `max_connections`，导致新连接被拒绝（`FATAL: too many connections`）。**正确做法**：总连接数 < `max_connections` 的 80%；多实例部署用 PgBouncer 中间件。

> 💡 **深度讲解**：连接池是 PostgreSQL Python 应用最关键的性能优化之一。核心原则：(1) 连接池大小不是越大越好——PostgreSQL 每个连接对应一个后端进程，过多连接反而因上下文切换降低性能；(2) 高并发多实例场景用 PgBouncer 做事务级池化；(3) 始终使用上下文管理器确保连接归还，防止泄漏；(4) `pool_pre_ping` 或 `max_inactive_connection_lifetime` 防止使用已断开的连接。

> 📝 **本章精简总结**：
> - 核心概念：连接池、PgBouncer、池大小计算
> - 关键原理：连接复用、一连接一进程、池化模式
> - 常用操作：create_pool、pool.acquire()、getconn/putconn
> - 最佳实践：池大小 CPU*2+磁盘、pool_pre_ping、PgBouncer 多实例
> - 常见坑点：连接池过大超 max_connections、连接泄漏
> - 面试高频：连接池大小计算、PgBouncer 原理

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：为什么不能无限增大连接池？
>   - 答案：每个连接一个后端进程，内存开销大，过多连接反而降性能
> - **进阶题（⭐⭐）**：PgBouncer 的 transaction 模式和 session 模式有什么区别？
>   - 思考方向：连接复用粒度、是否支持 prepared statement
> - **实战题（⭐⭐⭐）**：一个微服务系统有10个服务实例，每个实例需要多少连接？如何部署？
>   - 提示：10实例×10连接=100连接 → 用PgBouncer降到10个后端连接

---

## 七、高级数据类型

### 7.1 JSONB 深度使用

**概念解释**：JSONB 是 PostgreSQL 的二进制 JSON 类型，支持索引、查询、更新 JSON 文档中的嵌套字段。它比纯 JSON 类型更高效（二进制存储、自动去重键）。

```python
# JSONB 表创建和索引
CREATE_TABLE_SQL = """
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    attributes JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- GIN 索引：加速 JSONB 查询
CREATE INDEX idx_products_attributes
ON products USING GIN (attributes);

-- 表达式索引：加速特定字段查询
CREATE INDEX idx_products_color
ON products ((attributes->>'color'))
WHERE attributes ? 'color';
"""
```

```python
# asyncpg JSONB 操作示例
async def jsonb_examples(conn):
    # 插入 JSONB 数据（dict 自动转换）
    await conn.execute(
        """
        INSERT INTO products (name, attributes)
        VALUES ($1, $2)
        """,
        "iPhone 15 Pro",
        {"color": "black", "storage": "256GB", "brand": "Apple", "price": 9999},
    )

    # 查询：->> 操作符提取文本
    rows = await conn.fetch(
        "SELECT * FROM products WHERE attributes->>'color' = $1",
        "black",
    )

    # 包含查询：@> 检查 JSONB 是否包含指定对象
    rows = await conn.fetch(
        "SELECT * FROM products WHERE attributes @> $1::jsonb",
        '{"brand": "Apple"}',
    )

    # 存在查询：? 检查 key 是否存在
    rows = await conn.fetch(
        "SELECT * FROM products WHERE attributes ? $1",
        "warranty",
    )

    # 更新单个字段：jsonb_set
    await conn.execute(
        """
        UPDATE products
        SET attributes = jsonb_set(attributes, '{price}', $1::jsonb)
        WHERE id = $2
        """,
        "8999",
        1,
    )

    # 删除字段：- 操作符
    await conn.execute(
        "UPDATE products SET attributes = attributes - $1 WHERE id = $2",
        "temp_field",
        1,
    )
```

```python
# JSONB 聚合查询
async def aggregate_jsonb_keys(conn):
    """统计所有 JSONB 中的 key 频率"""
    rows = await conn.fetch("""
        SELECT
            key,
            COUNT(*) as count
        FROM products,
        jsonb_object_keys(attributes) as key
        GROUP BY key
        ORDER BY count DESC
    """)
    return [dict(r) for r in rows]
```

### 7.2 数组类型

```python
# 数组类型操作
async def array_examples(conn):
    # 创建带数组字段的表
    await conn.execute("""
        CREATE TABLE posts (
            id SERIAL PRIMARY KEY,
            title TEXT,
            tags TEXT[]
        )
    """)

    # 插入数组（Python list 自动转换）
    await conn.execute(
        "INSERT INTO posts (title, tags) VALUES ($1, $2)",
        "PostgreSQL Tutorial",
        ["postgresql", "database", "tutorial"],
    )

    # 包含任意元素查询：&& 操作符
    rows = await conn.fetch(
        "SELECT * FROM posts WHERE tags && $1::text[]",
        ["tutorial", "python"],
    )

    # 包含所有元素查询：@> 操作符
    rows = await conn.fetch(
        "SELECT * FROM posts WHERE tags @> $1::text[]",
        ["postgresql", "database"],
    )

    # 数组展开：unnest
    rows = await conn.fetch("""
        SELECT tag, COUNT(*) as count
        FROM posts, unnest(tags) as tag
        GROUP BY tag
        ORDER BY count DESC
    """)

    # 添加元素到数组
    await conn.execute(
        "UPDATE posts SET tags = array_append(tags, $1) WHERE id = $2",
        "newtag", 1,
    )
```

### 7.3 范围类型与 UUID

```python
# 范围类型（int4range, daterange, tsrange）
async def range_examples(conn):
    await conn.execute("""
        CREATE TABLE bookings (
            id SERIAL PRIMARY KEY,
            room_id INT,
            during TSRANGE  -- 时间范围
        )
    """)

    # 插入范围
    from datetime import datetime
    await conn.execute(
        "INSERT INTO bookings (room_id, during) VALUES ($1, $2)",
        101,
        "(2026-09-01 14:00, 2026-09-01 16:00)",
    )

    # 重叠查询：&& 检查时间冲突
    conflicts = await conn.fetch("""
        SELECT * FROM bookings
        WHERE room_id = $1 AND during && $2::tsrange
    """, 101, "(2026-09-01 15:00, 2026-09-01 17:00)")
```

```python
# UUID 类型
import uuid

async def uuid_example(conn):
    # 使用 UUID 作为主键（分布式友好）
    await conn.execute("""
        CREATE TABLE events (
            id UUID PRIMARY KEY,
            name TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    # 插入 UUID
    event_id = uuid.uuid4()
    await conn.execute(
        "INSERT INTO events (id, name) VALUES ($1, $2)",
        event_id, "Launch Party",
    )

    # 查询
    row = await conn.fetchrow("SELECT * FROM events WHERE id = $1", event_id)
    return dict(row)
```

```python
# JSONB 高级查询操作
async def jsonb_advanced(conn):
    # JSONB 数组操作
    # 查询标签数组中包含特定值的记录
    rows = await conn.fetch("""
        SELECT id, tags
        FROM posts
        WHERE tags @> $1::jsonb
    """, '["python", "tutorial"]')

    # JSONB 数值比较
    rows = await conn.fetch("""
        SELECT * FROM products
        WHERE (attributes->>'price')::numeric < $1
        ORDER BY (attributes->>'price')::numeric
    """, 1000)

    # JSONB 聚合
    rows = await conn.fetch("""
        SELECT
            attributes->>'brand' as brand,
            COUNT(*) as product_count,
            AVG((attributes->>'price')::numeric) as avg_price
        FROM products
        GROUP BY attributes->>'brand'
    """)

    # JSONB 拼接
    await conn.execute("""
        UPDATE products
        SET attributes = attributes || $1::jsonb
        WHERE id = $2
    """, '{"discount": 0.1}', 1)
```

```python
# 数组类型高级操作
async def array_advanced(conn):
    # 数组包含任意元素
    rows = await conn.fetch("""
        SELECT title FROM posts
        WHERE tags && $1::text[]
    """, ["python", "django"])

    # 数组包含所有元素
    rows = await conn.fetch("""
        SELECT title FROM posts
        WHERE tags @> $1::text[]
    """, ["python", "tutorial"])

    # 数组长度
    rows = await conn.fetch("""
        SELECT title, array_length(tags, 1) as tag_count
        FROM posts
        ORDER BY tag_count DESC
    """)

    # 数组去重
    rows = await conn.fetch("""
        SELECT title, array_agg(DISTINCT tag) as unique_tags
        FROM posts, unnest(tags) as tag
        GROUP BY title
    """)
```

```python
# JSONB 索引策略
# 1. 全文档 GIN 索引（适合任意字段查询）
CREATE INDEX idx_products_data ON products USING GIN (data);

# 2. 表达式索引（适合特定字段等值查询）
CREATE INDEX idx_products_brand ON products ((data->>'brand'));

# 3. 部分 GIN 索引（只索引活跃产品）
CREATE INDEX idx_products_active_gin ON products USING GIN (data) WHERE active = true;

# 查询性能对比：
# 无索引：全表扫描，O(N)
# GIN 索引：索引扫描，O(log N)
# 表达式索引：B-tree 等值查询，O(log N)
```

```python
# 范围类型高级查询
# tstzrange 重叠查询
async def find_conflicts(conn, start_time, end_time):
    rows = await conn.fetch("""
        SELECT * FROM bookings
        WHERE during && tstzrange($1, $2)
    """, start_time, end_time)
    # && = 范围重叠
    # @> = 包含
    # <@ = 被包含
    # -|- = 相邻
```

```python
# UUID 主键 vs 自增主键
# 自增主键（SERIAL/BIGSERIAL）：
#   - 优点：紧凑、有序、索引效率高
#   - 缺点：暴露业务量、分布式冲突

# UUID 主键：
#   - 优点：分布式友好、不暴露业务量
#   - 缺点：索引碎片、查询略慢

# UUID v7（时间有序）解决了 UUID 无序问题
# 推荐：分布式系统用 UUIDv7，单机用自增 ID
```

> ❌ **常见坑点**：JSONB 查询使用 `->>` 操作符提取文本时，GIN 索引无法加速等值查询。`->>` 返回 text，需要函数索引才能用索引。**正确做法**：等值查询用 `@>` 操作符配合 GIN 索引；或为常用路径创建表达式索引 `CREATE INDEX ON t ((data->>'key'))`。

> 💡 **深度讲解**：JSONB 是 PostgreSQL 最强大的特性之一。它让你在关系型数据库中存储半结构化数据，同时保持 SQL 的查询能力。设计原则：经常查询的字段用关系型列，不经常查询或结构多变的字段用 JSONB。数组类型适合标签、多选等场景，比中间表查询更高效。UUID 主键适合分布式系统——无需中心化 ID 生成器，天然分散。

> 📝 **本章精简总结**：
> - 核心概念：JSONB、ARRAY、范围类型、UUID、GIN 索引
> - 关键原理：二进制 JSON 存储、数组操作符、范围重叠
> - 常用操作：->>/@>/? 操作符、unnest、jsonb_set
> - 最佳实践：GIN 索引加速 JSONB、常用字段建表达式索引
> - 常见坑点：->> 不走索引、数组类型参数需要显式 ::text[]
> - 面试高频：JSONB vs JSON、数组类型 vs 中间表

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：JSONB 和 JSON 类型有什么区别？
>   - 答案：JSONB 二进制存储可索引查询；JSON 文本存储原样保留
> - **进阶题（⭐⭐）**：什么时候用数组类型，什么时候用中间表？
>   - 思考方向：数据量、查询模式、是否需要独立操作标签
> - **实战题（⭐⭐⭐）**：设计一个商品表，商品有可变规格（颜色/尺寸/材质），需要支持按规格筛选。用 JSONB 还是关系表？
>   - 提示：规格组合多变用 JSONB+GIN；需要独立查询规格用关系表

---

## 八、全文搜索

### 8.1 基础全文搜索

**概念解释**：PostgreSQL 内置全文搜索引擎，通过 `tsvector`（文本向量）和 `tsquery`（查询向量）实现中文/英文全文检索，无需 Elasticsearch。

```python
# 创建全文搜索表和索引
async def setup_fulltext_search(conn):
    """配置文章全文搜索"""
    # 创建带 tsvector 列的表
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            search_vector TSVECTOR
        )
    """)

    # GIN 索引加速全文搜索
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_articles_search
        ON articles USING GIN (search_vector)
    """)

    # 触发器：自动更新 search_vector
    await conn.execute("""
        CREATE OR REPLACE FUNCTION articles_search_update()
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'B');
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
    """)

    await conn.execute("""
        DROP TRIGGER IF EXISTS trg_articles_search ON articles;
        CREATE TRIGGER trg_articles_search
        BEFORE INSERT OR UPDATE ON articles
        FOR EACH ROW EXECUTE FUNCTION articles_search_update()
    """)
```

```python
# 执行全文搜索
async def search_articles(conn, query: str, limit: int = 20):
    """全文搜索文章，按相关性排序"""
    rows = await conn.fetch("""
        SELECT
            id,
            title,
            -- 相关性排名
            ts_rank(search_vector, plainto_tsquery('english', $1)) as rank,
            -- 高亮匹配片段
            ts_headline('english', content, plainto_tsquery('english', $1),
                        'StartSel=<mark>, StopSel=</mark>, MaxWords=35, MinWords=15') as headline
        FROM articles
        WHERE search_vector @@ plainto_tsquery('english', $1)
        ORDER BY rank DESC
        LIMIT $2
    """, query, limit)

    return [
        {
            "id": r["id"],
            "title": r["title"],
            "rank": float(r["rank"]),
            "headline": r["headline"],
        }
        for r in rows
    ]
```

### 8.2 中文全文搜索

```python
# 中文全文搜索需要安装分词扩展
# Linux: apt install postgresql-15-chinese (zhparser)
# 或使用 pg_jieba

# 安装 zhparser 后创建中文配置
# CREATE EXTENSION zhparser;
# CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
# ALTER TEXT SEARCH CONFIGURATION chinese
#     ADD MAPPING FOR n,v,a,i,e,l,t WITH simple;

async def search_chinese_articles(conn, query: str):
    """中文全文搜索"""
    rows = await conn.fetch("""
        SELECT id, title
        FROM articles
        WHERE search_vector @@ plainto_tsquery('chinese', $1)
        ORDER BY ts_rank(search_vector, plainto_tsquery('chinese', $1)) DESC
        LIMIT 10
    """, query)
    return rows
```

### 8.3 模糊搜索（pg_trgm）

```python
# pg_trgm 扩展：模糊搜索、相似度匹配
async def setup_trigram(conn):
    await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    await conn.execute("""
        CREATE INDEX idx_products_name_trgm
        ON products USING GIN (name gin_trgm_ops)
    """)

async def fuzzy_search(conn, query: str):
    """模糊搜索：处理拼写错误"""
    rows = await conn.fetch("""
        SELECT name, similarity(name, $1) as sim
        FROM products
        WHERE name % $1
        ORDER BY sim DESC
        LIMIT 10
    """, query)
    # 预期：搜索 "iphon" 也能找到 "iPhone"
    return rows
```

```python
# 高级全文搜索功能
async def advanced_search(conn, query: str):
    # 使用 websearch_to_tsquery（更友好的查询语法）
    rows = await conn.fetch("""
        SELECT title, ts_rank(search_vector, websearch_to_tsquery('english', $1)) as rank
        FROM articles
        WHERE search_vector @@ websearch_to_tsquery('english', $1)
        ORDER BY rank DESC
        LIMIT 10
    """, query)
    # websearch_to_tsquery 支持：
    # - 引号短语：'"exact phrase"'
    # - 排除词：'-exclude'
    # - OR：'term1 OR term2'

    return [dict(r) for r in rows]

# 同义词扩展
async def search_with_synonyms(conn, word: str):
    """使用同义词词典扩展搜索"""
    # 需要配置同义词词典
    # CREATE TEXT SEARCH DICTIONARY synonyms (
    #     TEMPLATE = synonym,
    #     SYNONYMS = my_synonyms
    # );
    rows = await conn.fetch("""
        SELECT title FROM articles
        WHERE search_vector @@ plainto_tsquery('english_syn', $1)
    """, word)
    return rows
```

```python
# 全文搜索性能优化
# 1. 使用 GIN 索引加速
# CREATE INDEX ON articles USING GIN(search_vector);

# 2. 部分索引（只索引公开文章）
# CREATE INDEX ON articles USING GIN(search_vector) WHERE status='public';

# 3. 触发器自动更新 search_vector（避免手动维护）

# 4. 搜索结果缓存（高频查询用 Redis 缓存）
import redis
r = redis.Redis()

async def cached_search(conn, query: str):
    cache_key = f"search:{query}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    results = await advanced_search(conn, query)
    r.setex(cache_key, 300, json.dumps(results))  # 缓存5分钟
    return results
```

```python
# 全文搜索 vs LIKE 查询
# LIKE 查询：
#   WHERE title LIKE '%python%'
#   - 全表扫描，O(N)
#   - 不支持分词
#   - 不支持排序相关性

# 全文搜索：
#   WHERE search_vector @@ plainto_tsquery('english', 'python')
#   - GIN 索引，O(log N)
#   - 分词（词干提取：running → run）
#   - 相关性排序（ts_rank）
#   - 支持短语搜索
#   - 支持同义词
```

```python
# 中文全文搜索配置
# PostgreSQL 默认不支持中文分词
# 需要安装 zhparser 扩展或使用 pg_jieba

# CREATE EXTENSION pg_jieba;
# CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = jieba_parser);
# ALTER TEXT SEARCH CONFIGURATION chinese
#   ADD MAPPING FOR english, numeric, hword
#   WITH simple, jieba;
```

> ❌ **常见坑点**：默认 `english` 配置不支持中文。中文全文搜索必须安装 `zhparser` 或 `pg_jieba` 扩展，并创建中文文本搜索配置。**正确做法**：安装扩展 → 创建配置 → 使用 `plainto_tsquery('chinese', query)`。

> 💡 **深度讲解**：PostgreSQL 全文搜索是轻量级搜索引擎的完美替代。对于中小规模的搜索需求（万级到百万级文档），内置全文搜索 + GIN 索引完全够用，不需要引入 Elasticsearch。中文搜索的关键是分词器——`zhparser` 基于 SCWS 分词，`pg_jieba` 基于结巴分词。对于更复杂的搜索需求（同义词、多语言、搜索分析），再考虑 Elasticsearch。

> 📝 **本章精简总结**：
> - 核心概念：tsvector、tsquery、GIN 索引、相关性排名
> - 关键原理：文本分词、权重设置、触发器自动更新
> - 常用操作：to_tsvector、plainto_tsquery、ts_rank、ts_headline
> - 最佳实践：触发器自动更新 search_vector、GIN 索引
> - 常见坑点：中文不支持默认 english 配置
> - 面试高频：全文搜索 vs Elasticsearch、tsvector 触发器

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：`tsvector` 和 `tsquery` 分别是什么？
>   - 答案：tsvector 是文档分词后的向量；tsquery 是查询词的向量
> - **进阶题（⭐⭐）**：为什么要用触发器自动更新 search_vector？
>   - 思考方向：手动维护容易遗漏、性能影响
> - **实战题（⭐⭐⭐）**：为一个博客系统实现中文文章搜索功能。要求：标题权重>正文权重、高亮匹配片段。
>   - 提示：zhparser + setweight + ts_headline

---

## 九、窗口函数与CTE

### 9.1 窗口函数

**概念解释**：窗口函数在不合并行的情况下，对一组行进行计算。它可以在每一行中看到"窗口"内的其他行，实现排名、累计、移动平均等复杂计算。

```python
# 窗口函数：每个分类取浏览量前3的文章
async def top_posts_per_category(conn):
    rows = await conn.fetch("""
        WITH ranked AS (
            SELECT
                id, title, category, views,
                ROW_NUMBER() OVER (
                    PARTITION BY category
                    ORDER BY views DESC
                ) as rn,
                RANK() OVER (
                    PARTITION BY category
                    ORDER BY views DESC
                ) as rank,
                DENSE_RANK() OVER (
                    PARTITION BY category
                    ORDER BY views DESC
                ) as dense_rank
            FROM posts
        )
        SELECT id, title, category, views, rn
        FROM ranked
        WHERE rn <= 3
        ORDER BY category, views DESC
    """)
    return [dict(r) for r in rows]
```

```python
# 常用窗口函数
async def window_functions_demo(conn):
    rows = await conn.fetch("""
        SELECT
            date,
            revenue,
            -- 累计求和
            SUM(revenue) OVER (ORDER BY date) as cumulative_revenue,
            -- 移动平均（7天）
            AVG(revenue) OVER (
                ORDER BY date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ) as ma_7day,
            -- 同比增长（与前一天比较）
            revenue - LAG(revenue) OVER (ORDER BY date) as daily_change,
            -- 占比
            revenue / SUM(revenue) OVER () * 100 as pct_of_total
        FROM daily_revenue
        ORDER BY date
    """)
    return [dict(r) for r in rows]
```

| 窗口函数 | 说明 | 示例 |
|---------|------|------|
| `ROW_NUMBER()` | 行号（连续） | 1,2,3,4,5 |
| `RANK()` | 排名（并列跳号） | 1,2,2,4 |
| `DENSE_RANK()` | 密集排名（不跳号） | 1,2,2,3 |
| `LAG(col, n)` | 前n行的值 | 同比/环比 |
| `LEAD(col, n)` | 后n行的值 | 预测 |
| `SUM() OVER()` | 累计求和 | 累计收入 |
| `AVG() OVER()` | 移动平均 | MA均线 |

### 9.2 CTE（WITH 子句）

```python
# 普通 CTE：简化复杂查询
async def cte_example(conn):
    rows = await conn.fetch("""
        WITH active_users AS (
            SELECT id, name, email
            FROM users
            WHERE status = 'active'
        ),
        user_stats AS (
            SELECT user_id, COUNT(*) as order_count, SUM(amount) as total_spent
            FROM orders
            WHERE created_at > NOW() - INTERVAL '30 days'
            GROUP BY user_id
        )
        SELECT u.id, u.name, COALESCE(s.order_count, 0) as orders,
               COALESCE(s.total_spent, 0) as spent
        FROM active_users u
        LEFT JOIN user_stats s ON u.id = s.user_id
        ORDER BY spent DESC
    """)
    return [dict(r) for r in rows]
```

```python
# 递归 CTE：树形结构查询
async def category_tree(conn, root_id: int):
    """递归查询分类树"""
    rows = await conn.fetch("""
        WITH RECURSIVE category_tree AS (
            -- 基础查询：根节点
            SELECT id, name, parent_id, 1 as level
            FROM categories
            WHERE id = $1

            UNION ALL

            -- 递归部分：关联子节点
            SELECT c.id, c.name, c.parent_id, ct.level + 1
            FROM categories c
            INNER JOIN category_tree ct ON c.parent_id = ct.id
        )
        SELECT id, name, parent_id, level
        FROM category_tree
        ORDER BY level, id
    """, root_id)
    return [dict(r) for r in rows]
```

```python
# 更多窗口函数实战案例
async def window_functions_extra(conn):
    # 同比环比分析
    rows = await conn.fetch("""
        SELECT
            month,
            revenue,
            LAG(revenue, 12) OVER (ORDER BY month) as yoy_revenue,
            revenue - LAG(revenue, 12) OVER (ORDER BY month) as yoy_diff,
            ROUND(
                (revenue - LAG(revenue, 12) OVER (ORDER BY month)) /
                LAG(revenue, 12) OVER (ORDER BY month) * 100,
                2
            ) as yoy_growth_pct
        FROM monthly_revenue
    """)

    # 累计百分比分布
    rows = await conn.fetch("""
        SELECT
            product,
            sales,
            SUM(sales) OVER (ORDER BY sales DESC) as cumulative_sales,
            ROUND(
                SUM(sales) OVER (ORDER BY sales DESC)::numeric /
                SUM(sales) OVER () * 100,
                2
            ) as cumulative_pct
        FROM product_sales
    """)

    # 移动窗口（7天滚动平均）
    rows = await conn.fetch("""
        SELECT
            date,
            temperature,
            AVG(temperature) OVER (
                ORDER BY date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ) as ma_7day
        FROM weather_data
    """)
    return [dict(r) for r in rows]
```

```python
# 递归 CTE 进阶：图遍历
async def graph_traversal(conn, start_node: int):
    """图的最短路径（广度优先）"""
    rows = await conn.fetch("""
        WITH RECURSIVE bfs AS (
            -- 起点
            SELECT node_id, 1 as depth, ARRAY[node_id] as path
            FROM graph WHERE node_id = $1

            UNION ALL

            -- 邻居
            SELECT g.node_id, b.depth + 1, b.path || g.node_id
            FROM graph g
            JOIN bfs b ON g.prev_id = b.node_id
            WHERE NOT g.node_id = ANY(b.path)  -- 防止循环
        )
        SELECT * FROM bfs
        WHERE node_id = $2
    """, start_node, start_node)  # 回到起点=环检测
    return [dict(r) for r in rows]
```

> 💡 **深度讲解**：窗口函数和 CTE 是 PostgreSQL 分析查询的两大利器。窗口函数让你在不 GROUP BY 合并行的情况下进行聚合计算，是排名/累计/移动平均场景的标准方案。CTE（WITH 子句）将复杂查询拆分为逻辑步骤，提高可读性；递归 CTE 用于树形结构、图遍历等层级数据查询。在 Python 应用中，这些高级 SQL 特性让你把复杂计算推到数据库层，而不是拉到 Python 层循环处理——后者性能差且代码复杂。

> 📝 **本章精简总结**：
> - 核心概念：窗口函数（OVER/PARTITION BY）、CTE、递归查询
> - 关键原理：窗口帧、LAG/LEAD、WITH RECURSIVE
> - 常用操作：ROW_NUMBER、SUM OVER、递归树形查询
> - 最佳实践：用 SQL 窗口函数替代 Python 循环计算
> - 常见坑点：窗口帧 ROWS BETWEEN 语法容易混淆
> - 面试高频：ROW_NUMBER vs RANK、递归CTE原理

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：ROW_NUMBER、RANK、DENSE_RANK 有什么区别？
>   - 答案：ROW_NUMBER 连续；RANK 并列跳号；DENSE_RANK 并列不跳号
> - **进阶题（⭐⭐）**：递归 CTE 的终止条件是什么？
>   - 思考方向：UNION ALL 的递归部分无结果时自动终止
> - **实战题（⭐⭐⭐）**：计算每个部门工资排名前3的员工，以及其工资与部门平均工资的差值。
>   - 提示：窗口函数 PARTITION BY + 子查询

---

## 十、事务与锁机制

### 10.1 事务隔离级别

**概念解释**：事务隔离级别控制多个并发事务之间的可见性。PostgreSQL 支持四种标准隔离级别，但实际上只有三种（Read Uncommitted 等同于 Read Committed）。

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|---------|------|-----------|------|------|
| Read Committed（默认） | 防止 | 可能 | 可能 | 最高 |
| Repeatable Read | 防止 | 防止 | 可能 | 中等 |
| Serializable | 防止 | 防止 | 防止 | 最低 |

```python
# asyncpg 事务隔离级别
async def transaction_isolation_example(conn):
    # Read Committed（默认）：每条语句看到最新提交的数据
    async with conn.transaction(isolation='read_committed'):
        await conn.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        # 其他事务此时可能看到中间状态

    # Repeatable Read：整个事务看到同一快照
    async with conn.transaction(isolation='repeatable_read'):
        balance1 = await conn.fetchval("SELECT balance FROM accounts WHERE id = 1")
        # 其他事务修改了 balance
        balance2 = await conn.fetchval("SELECT balance FROM accounts WHERE id = 1")
        # balance1 == balance2（同一快照）

    # Serializable：最高隔离，类似串行执行
    async with conn.transaction(isolation='serializable'):
        # 最严格但性能最差，可能 serialization failure
        pass
```

### 10.2 锁机制

```python
# 行级锁：SELECT FOR UPDATE
async def deduct_stock(conn, product_id: int, quantity: int):
    """扣库存：使用行锁防止超卖"""
    async with conn.transaction():
        # 锁定库存行，其他事务必须等待
        row = await conn.fetchrow(
            "SELECT stock FROM products WHERE id = $1 FOR UPDATE",
            product_id,
        )
        if row['stock'] < quantity:
            raise ValueError("库存不足")

        await conn.execute(
            "UPDATE products SET stock = stock - $1 WHERE id = $2",
            quantity, product_id,
        )
```

```python
# 锁模式对比
# FOR UPDATE：锁行，其他事务不能修改也不能读取（阻塞）
# FOR NO KEY UPDATE：较弱的锁，允许并发读取
# FOR SHARE：共享锁，其他事务可以读但不能写
# NOWAIT：如果拿不到锁立即报错（不等待）

async def safe_lock_example(conn, product_id: int):
    async with conn.transaction():
        # NOWAIT：拿不到锁立即报错，避免长时间等待
        row = await conn.fetchrow(
            "SELECT stock FROM products WHERE id = $1 FOR UPDATE NOWAIT",
            product_id,
        )
```

```python
# 死锁检测
# PostgreSQL 自动检测死锁并回滚其中一个事务
# 错误：asyncpg.exceptions.DeadlockDetectedError

# 预防死锁：
# 1. 始终按相同顺序锁定资源（如按 ID 升序）
# 2. 保持事务简短
# 3. 设置 lock_timeout
await conn.execute("SET lock_timeout = '3s'")
```

```python
# 悲观锁 vs 乐观锁
# 悲观锁：SELECT FOR UPDATE（适合短事务高并发）
async def pessimistic_lock(conn, account_id: int):
    async with conn.transaction():
        row = await conn.fetchrow(
            "SELECT balance FROM accounts WHERE id = $1 FOR UPDATE",
            account_id,
        )
        await conn.execute(
            "UPDATE accounts SET balance = balance - 100 WHERE id = $1",
            account_id,
        )

# 乐观锁：版本号控制（适合读多写少）
async def optimistic_lock(conn, account_id: int, version: int):
    result = await conn.execute("""
        UPDATE accounts
        SET balance = balance - 100, version = version + 1
        WHERE id = $1 AND version = $2
    """, account_id, version)
    if "UPDATE 0" in result:
        raise ConcurrentModificationError("记录已被其他事务修改")
```

```python
# 隔离级别实战示例
async def isolation_demo(conn):
    # Read Committed：每条语句看到最新数据
    async with conn.transaction(isolation='read_committed'):
        a = await conn.fetchval("SELECT balance FROM accounts WHERE id=1")
        # 其他事务提交了修改
        b = await conn.fetchval("SELECT balance FROM accounts WHERE id=1")
        # a != b（看到了新提交的数据）

    # Repeatable Read：事务内同一快照
    async with conn.transaction(isolation='repeatable_read'):
        a = await conn.fetchval("SELECT balance FROM accounts WHERE id=1")
        # 其他事务提交了修改
        b = await conn.fetchval("SELECT balance FROM accounts WHERE id=1")
        # a == b（快照不变）
```

```python
# 死锁避免最佳实践
# 1. 统一加锁顺序（按 ID 升序）
async def transfer_safe(conn, from_id: int, to_id: int, amount: float):
    async with conn.transaction():
        # 始终先锁 ID 较小的账户，避免死锁
        first = min(from_id, to_id)
        second = max(from_id, to_id)

        await conn.execute("SELECT 1 FROM accounts WHERE id=$1 FOR UPDATE", first)
        await conn.execute("SELECT 1 FROM accounts WHERE id=$1 FOR UPDATE", second)

        await conn.execute("UPDATE accounts SET balance = balance - $1 WHERE id=$2", amount, from_id)
        await conn.execute("UPDATE accounts SET balance = balance + $1 WHERE id=$2", amount, to_id)

# 2. 设置锁超时
await conn.execute("SET lock_timeout = '3s'")

# 3. 保持事务简短
# 不要在事务中做 HTTP 请求等慢操作
```

```python
# 事务隔离级别详解
# PostgreSQL 支持4种标准隔离级别：

# 1. Read Uncommitted（读未提交）
#    - 可读到未提交数据（脏读）
#    - PostgreSQL 实际上等同 Read Committed

# 2. Read Committed（读已提交，默认）
#    - 每条语句看到最新提交的数据
#    - 解决脏读，不可重复读
#    - 适合大多数场景

# 3. Repeatable Read（可重复读）
#    - 事务内同一快照
#    - 解决脏读、不可重复读
#    - 适合报表、数据一致性场景

# 4. Serializable（串行化）
#    - 最高隔离级别
#    - 解决所有并发异常（含幻读）
#    - 通过 SSI 实现，性能略差
#    - 适合金融、交易场景
```

```python
# 隔离级别选择指南
# | 场景                | 推荐隔离级别   | 原因                  |
# |---------------------|----------------|-----------------------|
# | 常规 CRUD           | Read Committed | 默认，性能好          |
# | 报表查询            | Repeatable Read| 保证快照一致          |
# | 金融转账            | Serializable   | 严格一致性            |
# | 库存扣减            | Repeatable Read| 防止超卖              |
# | 多步操作            | Repeatable Read| 防止中间态变化        |
```

> ❌ **常见坑点**：忘记在事务中使用 `SELECT FOR UPDATE` 导致超卖。高并发下多个事务同时读到相同库存，然后都扣减，最终库存变为负数。**正确做法**：在事务中使用 `SELECT ... FOR UPDATE` 锁定行，确保串行化。

> 💡 **深度讲解**：事务和锁是 PostgreSQL 数据一致性的核心。Read Committed 是默认级别，大多数场景够用。Repeatable Read 适合需要"事务内一致快照"的场景（如对账）。Serializable 最严格但性能差，只在必要时使用。行锁 `FOR UPDATE` 是防止并发修改冲突的标准手段——电商扣库存、银行转账都必须使用。死锁预防的关键是统一加锁顺序和保持事务简短。

> 📝 **本章精简总结**：
> - 核心概念：隔离级别、行级锁、死锁、FOR UPDATE
> - 关键原理：MVCC 多版本并发控制、锁等待
> - 常用操作：transaction(isolation=...)、FOR UPDATE、NOWAIT
> - 最佳实践：扣库存用 FOR UPDATE、统一加锁顺序
> - 常见坑点：忘记 FOR UPDATE 导致超卖
> - 面试高频：隔离级别、MVCC、死锁预防

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：Read Committed 和 Repeatable Read 的区别？
>   - 答案：RC 每条语句看到最新提交；RR 整个事务看到同一快照
> - **进阶题（⭐⭐）**：什么是 MVCC？为什么 PostgreSQL 读不阻塞写？
>   - 思考方向：多版本、快照、undo 链
> - **实战题（⭐⭐⭐）**：设计一个秒杀场景的库存扣减，防止超卖。
>   - 提示：SELECT FOR UPDATE + 事务 + 库存检查

---

## 十一、索引类型与优化

### 11.1 索引类型选择

**概念解释**：PostgreSQL 提供多种索引类型，适用于不同查询模式。选择正确的索引类型是查询性能的关键。

| 索引类型 | 适用场景 | 示例 |
|---------|---------|------|
| B-tree（默认） | 等值、范围、排序 | `CREATE INDEX ON t (created_at)` |
| Hash | 纯等值查询 | `CREATE INDEX ON t USING HASH (email)` |
| GIN | JSONB、数组、全文搜索 | `CREATE INDEX ON t USING GIN (tags)` |
| GiST | 地理空间、范围类型 | `CREATE INDEX ON t USING GiST (location)` |
| BRIN | 大表、物理顺序一致 | `CREATE INDEX ON t USING BRIN (created_at)` |
| 部分索引 | 只索引满足条件的行 | `CREATE INDEX ON t (email) WHERE active=true` |
| 覆盖索引 | 索引包含所有查询列 | `CREATE INDEX ON t (email) INCLUDE (name)` |

```python
# 各种索引创建示例
async def create_indexes(conn):
    # B-tree：最常用，等值和范围查询
    await conn.execute("""
        CREATE INDEX idx_users_email ON users (email)
    """)

    # 复合 B-tree：多列查询
    await conn.execute("""
        CREATE INDEX idx_orders_user_status ON orders (user_id, status)
    """)

    # GIN：JSONB/数组/全文搜索
    await conn.execute("""
        CREATE INDEX idx_products_attributes ON products
        USING GIN (attributes)
    """)

    # BRIN：超大表，物理顺序与逻辑一致（如时间序列）
    await conn.execute("""
        CREATE INDEX idx_events_time ON events
        USING BRIN (event_time) WITH (pages_per_range = 32)
    """)

    # 部分索引：只索引活跃用户（减少索引大小）
    await conn.execute("""
        CREATE INDEX idx_active_users_email ON users (email)
        WHERE status = 'active'
    """)

    # 覆盖索引：查询只需要索引列（Index Only Scan）
    await conn.execute("""
        CREATE INDEX idx_users_email_covering ON users (email)
        INCLUDE (name, created_at)
    """)
```

### 11.2 EXPLAIN ANALYZE

```python
# 使用 EXPLAIN ANALYZE 分析查询计划
async def analyze_query(conn, sql: str):
    """分析 SQL 查询执行计划"""
    rows = await conn.fetch(f"EXPLAIN ANALYZE {sql}")
    for row in rows:
        print(row[0])
    # 典型输出：
    # Seq Scan on users  (cost=0.00..180.00 rows=1000 width=36) (actual time=0.01..5.20 rows=1000 loops=1)
    #   Filter: (status = 'active'::text)
    #   Rows Removed by Filter: 500
    # Planning Time: 0.30 ms
    # Execution Time: 6.10 ms
```

```python
# 常见执行计划解读
#
# Seq Scan（顺序扫描）→ 全表扫描，慢！
#   原因：缺少索引或索引选择性低
#   解决：添加合适的索引

# Index Scan（索引扫描）→ 通过索引查找
#   好的性能

# Bitmap Index Scan（位图索引扫描）→ 多条件索引合并
#   中等性能

# Index Only Scan（仅索引扫描）→ 只查索引，不回表
#   最快！覆盖索引实现
```

### 11.3 索引优化实战

```python
# 慢查询优化示例：深分页
# ❌ 慢：OFFSET 100000 需要扫描并跳过前10万行
# SELECT * FROM posts ORDER BY id LIMIT 20 OFFSET 100000;

# ✅ 快：Keyset 分页（游标分页）
async def keyset_pagination(conn, last_id: int = 0, limit: int = 20):
    """基于游标的分页（避免深分页慢）"""
    rows = await conn.fetch("""
        SELECT id, title, created_at
        FROM posts
        WHERE id > $1
        ORDER BY id
        LIMIT $2
    """, last_id, limit)
    return [dict(r) for r in rows]
    # 预期：无论翻到第几页，查询时间都相同
```

```python
# 索引维护
# REINDEX：重建索引（索引膨胀后）
async def reindex_example(conn):
    await conn.execute("REINDEX INDEX idx_users_email")
    # 注意：REINDEX 在 PG12+ 支持 CONCURRENTLY 不锁表

# ANALYZE：更新统计信息（查询优化器依赖）
async def update_statistics(conn):
    await conn.execute("ANALYZE users")
```

```python
# 索引优化实战：识别未使用的索引
async def find_unused_indexes(conn):
    """查找从未使用的索引（可以删除以节省写入开销）"""
    rows = await conn.fetch("""
        SELECT
            schemaname,
            relname as table_name,
            indexrelname as index_name,
            idx_scan as index_scans
        FROM pg_stat_user_indexes
        WHERE idx_scan = 0
        AND schemaname = 'public'
        ORDER BY relname
    """)
    return [dict(r) for r in rows]
    # 预期输出：从未被扫描的索引 → 可以 DROP INDEX

# 索引膨胀监控
async def check_index_bloat(conn):
    """检查索引膨胀程度"""
    rows = await conn.fetch("""
        SELECT
            relname as table_name,
            indexrelname as index_name,
            pg_size_pretty(pg_relation_size(indexrelid)) as index_size
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
        ORDER BY pg_relation_size(indexrelid) DESC
        LIMIT 10
    """)
    return [dict(r) for r in rows]
```

```python
# 并行查询配置
# PostgreSQL 支持并行执行查询（PG10+）
# 适合大表扫描、聚合分析

# postgresql.conf 配置：
# max_parallel_workers_per_gather = 4  # 每个查询最多4个工作线程
# max_parallel_workers = 8              # 总共最多8个并行工作线程
# parallel_setup_cost = 1000           # 并行启动成本
# parallel_tuple_cost = 0.1            # 每元组的并行成本

# 手动强制并行查询
# SET max_parallel_workers_per_gather = 4;
```

```python
# 统计信息维护
# 查询优化器依赖统计信息来选择执行计划
# 统计信息过期会导致执行计划变差

# 手动更新统计信息
async def update_stats(conn, table_name: str):
    await conn.execute(f"ANALYZE {table_name}")

# 自动统计（autovacuum 自动运行，通常不需要手动）
# 检查 autovacuum 状态
async def check_autovacuum(conn):
    rows = await conn.fetch("""
        SELECT relname, n_tup_ins, n_tup_upd, n_tup_del, last_autovacuum
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
    """)
    return [dict(r) for r in rows]
```

```python
# EXPLAIN 解读示例
# 慢查询：SELECT * FROM orders WHERE user_id = 123 ORDER BY created_at DESC LIMIT 20;

# EXPLAIN ANALYZE 输出：
# Limit  (cost=0.56..8.58 rows=20 width=120) (actual time=0.05..10.20 rows=20 loops=1)
#   ->  Index Scan using idx_orders_user_time on orders  (cost=0.56..400.00 rows=1000 width=120)
#         Index Cond: (user_id = 123)
#         Actual Rows Removed by Index Recheck: 0
# Planning Time: 0.50 ms
# Execution Time: 10.30 ms

# 解读：
# cost=0.56..8.58 → 估计成本
# actual time=0.05..10.20 → 实际耗时10ms
# Index Scan → 使用了索引（好）
# 如果看到 Seq Scan → 没走索引（需要优化）
```

```python
# 慢查询排查流程
# 1. 开启慢查询日志
#    log_min_duration_statement = 1000

# 2. 找到慢查询
#    SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC;

# 3. EXPLAIN ANALYZE 分析执行计划
# 4. 找全表扫描/低效操作
# 5. 添加索引/优化SQL
# 6. 验证优化效果
```

```python
# 索引类型选择指南
# | 查询模式                | 推荐索引类型 | 原因                  |
# |-------------------------|--------------|-----------------------|
# | 等值查询 = IN           | B-tree       | 默认，最通用          |
# | 范围查询 > < BETWEEN    | B-tree       | B-tree 天然支持范围   |
# | LIKE '%xxx%'            | GIN(pg_trgm) | 模糊搜索              |
# | JSONB 字段查询          | GIN          | JSONB 倒排索引        |
# | 全文搜索                | GIN          | 词项倒排              |
# | 几何/地理空间           | GiST         | R-tree                |
# | 大表时序数据            | BRIN         | 块范围索引，极小      |
# | 数组包含查询            | GIN          | 数组元素倒排          |
# | UUID 主键               | B-tree       | 默认主键索引          |
```

```python
# 复合索引最左前缀原则
# CREATE INDEX idx_user_status_date ON users (status, created_at);
#
# ✅ 走索引：
#   WHERE status = 'active'
#   WHERE status = 'active' AND created_at > '2026-01-01'
#
# ❌ 不走索引（跳过最左列）：
#   WHERE created_at > '2026-01-01'
#
# 💡 原则：索引 (a, b, c) 等价于：
#   (a)
#   (a, b)
#   (a, b, c)
```

> ❌ **常见坑点**：索引不是越多越好。每个索引都会增加写操作（INSERT/UPDATE/DELETE）的开销——写数据时需要同时更新所有索引。**正确做法**：只为高频查询创建索引；定期检查未使用的索引（`pg_stat_user_indexes`）并删除。

> 💡 **深度讲解**：索引优化是数据库性能调优的核心。关键原则：(1) WHERE/ORDER BY/JOIN 条件中的列适合建索引；(2) 复合索引遵循最左前缀原则；(3) EXPLAIN ANALYZE 是分析慢查询的唯一方法；(4) 深分页用 keyset 替代 OFFSET；(5) 定期清理未使用索引。PostgreSQL 的索引类型丰富，理解每种类型的适用场景才能做出正确选择。

> 📝 **本章精简总结**：
> - 核心概念：B-tree/GIN/GiST/BRIN、EXPLAIN ANALYZE、深分页
> - 关键原理：索引扫描 vs 顺序扫描、最左前缀
> - 常用操作：CREATE INDEX、EXPLAIN ANALYZE、keyset分页
> - 最佳实践：只为高频查询建索引、keyset分页、定期清理
> - 常见坑点：索引过多拖慢写入、OFFSET深分页慢
> - 面试高频：索引类型选择、EXPLAIN解读、最左前缀

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：GIN 索引和 B-tree 索引的适用场景有什么不同？
>   - 答案：B-tree 等值/范围；GIN JSONB/数组/全文搜索
> - **进阶题（⭐⭐）**：为什么 OFFSET 深分页慢？如何优化？
>   - 思考方向：OFFSET 需要扫描并跳过前面所有行
> - **实战题（⭐⭐⭐）**：一个表有100万行，按 created_at 降序查询第1000页。优化查询。
>   - 提示：keyset 分页 WHERE created_at < (上一页最后时间)

---

## 十二、分区表与物化视图

### 12.1 分区表

**概念解释**：分区表将大表按规则拆分为多个物理子表（分区），查询时只扫描相关分区，提升大表查询性能。

```python
# 范围分区（按时间）
async def create_partitioned_table(conn):
    await conn.execute("""
        CREATE TABLE sensor_data (
            id BIGSERIAL,
            sensor_id INT,
            temperature FLOAT,
            recorded_at TIMESTAMPTZ NOT NULL
        ) PARTITION BY RANGE (recorded_at)
    """)

    # 创建分区
    await conn.execute("""
        CREATE TABLE sensor_data_2026_09
        PARTITION OF sensor_data
        FOR VALUES FROM ('2026-09-01') TO ('2026-10-01')
    """)
    await conn.execute("""
        CREATE TABLE sensor_data_2026_10
        PARTITION OF sensor_data
        FOR VALUES FROM ('2026-10-01') TO ('2026-11-01')
    """)
    # 自动创建未来分区（pg_partman 扩展）
```

```python
# 查询自动裁剪分区（Pruning）
async def query_partitioned(conn, start_date, end_date):
    rows = await conn.fetch("""
        SELECT * FROM sensor_data
        WHERE recorded_at >= $1 AND recorded_at < $2
    """, start_date, end_date)
    # PostgreSQL 自动只扫描相关分区，不扫描全表
    # 预期：EXPLAIN 显示 "Append" 只包含匹配的分区
```

### 12.2 物化视图

```python
# 物化视图：预计算复杂查询结果
async def create_materialized_view(conn):
    await conn.execute("""
        CREATE MATERIALIZED VIEW daily_revenue_summary AS
        SELECT
            date_trunc('day', created_at) as day,
            COUNT(*) as order_count,
            SUM(amount) as total_revenue,
            AVG(amount) as avg_order_value
        FROM orders
        GROUP BY day
        ORDER BY day DESC
    """)

    # 创建唯一索引（支持 CONCURRENTLY 刷新）
    await conn.execute("""
        CREATE UNIQUE INDEX idx_daily_revenue_day
        ON daily_revenue_summary (day)
    """)
```

```python
# 刷新物化视图
async def refresh_materialized_view(conn):
    # 阻塞式刷新（普通场景）
    # await conn.execute("REFRESH MATERIALIZED VIEW daily_revenue_summary")

    # 并发刷新（不阻塞查询，需要唯一索引）
    await conn.execute(
        "REFRESH MATERIALIZED VIEW CONCURRENTLY daily_revenue_summary"
    )
```

```python
# 使用物化视图
async def query_daily_revenue(conn, days: int = 30):
    """查询最近N天收入汇总（毫秒级响应）"""
    rows = await conn.fetch("""
        SELECT * FROM daily_revenue_summary
        WHERE day >= NOW() - INTERVAL '%s days'
        ORDER BY day
    """ % days)
    return [dict(r) for r in rows]
    # 对比：直接查 orders 表需要扫描百万行 → 秒级
    # 查物化视图 → 毫秒级
```

```python
# 分区表自动管理（pg_partman）
# 安装：CREATE EXTENSION pg_partman;

# 按小时自动创建分区
# SELECT partman.create_parent(
#     p_parent_table => 'public.sensor_data',
#     p_control => 'recorded_at',
#     p_type => 'native',
#     p_interval => '1 hour',
#     p_premake => 4  -- 预创建未来4个分区
# );

# 查询分区信息
async def list_partitions(conn, table_name: str):
    rows = await conn.fetch("""
        SELECT
            inhrelid::regclass as partition_name,
            pg_size_pretty(pg_total_relation_size(inhrelid)) as size
        FROM pg_inherits
        WHERE inhparent = $1::regclass
        ORDER BY inhrelid::regclass::text
    """, table_name)
    return [dict(r) for r in rows]
```

```python
# 物化视图自动化刷新
# 1. 创建刷新函数
# 2. 用 pg_cron 定时刷新

# 手动刷新物化视图
async def refresh_mv(conn, mv_name: str, concurrently: bool = True):
    if concurrently:
        await conn.execute(
            f"REFRESH MATERIALIZED VIEW CONCURRENTLY {mv_name}"
        )
    else:
        await conn.execute(f"REFRESH MATERIALIZED VIEW {mv_name}")

# pg_cron 定时刷新（每小时）
# SELECT cron.schedule(
#     'refresh-daily-revenue',
#     '0 * * * *',
#     'REFRESH MATERIALIZED VIEW CONCURRENTLY daily_revenue_summary'
# );
```

```python
# 物化视图 vs 普通视图 vs 临时表
# 普通视图：
#   - 不存储数据，只是查询的预定义
#   - 每次查询实时计算
#   - 适合简化复杂 SQL

# 物化视图：
#   - 存储计算结果
#   - 查询快，但需要手动刷新
#   - 适合聚合分析、报表

# 临时表：
#   - 会话级别的表
#   - 会话结束自动删除
#   - 适合中间结果集

# 选择建议：
# - 数据实时性要求高 → 普通视图
# - 查询性能要求高 → 物化视图
# - 中间计算 → 临时表
```

```python
# 分区表策略选择
# | 数据特征          | 推荐分区策略 | 示例              |
# |-------------------|--------------|-------------------|
# | 按时间增长        | 范围分区     | 日志、时序数据    |
# | 按租户/客户       | 列表分区     | SaaS 多租户       |
# | 均匀分布大表     | 哈希分区     | 用户表            |
# | 时间+租户         | 多级分区     | 先按月再按租户    |
```

> 💡 **深度讲解**：分区表和物化视图是 PostgreSQL 处理大数据量的两大武器。分区表适合时间序列数据（日志、监控数据）——按时间分区，自动裁剪只查相关分区，老数据可以直接 DROP 分区而不是 DELETE。物化视图适合复杂聚合查询——预计算结果存储为物理表，查询时直接读结果，不需要重新聚合。两者结合可以让亿级数据的查询保持毫秒级响应。

> 📝 **本章精简总结**：
> - 核心概念：分区表、分区裁剪、物化视图、CONCURRENTLY 刷新
> - 关键原理：物理分区、预计算结果
> - 常用操作：PARTITION BY RANGE、CREATE MATERIALIZED VIEW、REFRESH
> - 最佳实践：时间序列数据分区、复杂聚合用物化视图
> - 常见坑点：物化视图刷新阻塞、分区键选择不当
> - 面试高频：分区表原理、物化视图 vs 普通视图

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：普通视图和物化视图有什么区别？
>   - 答案：普通视图不存储数据（每次执行查询）；物化视图存储结果
> - **进阶题（⭐⭐）**：什么是分区裁剪（Partition Pruning）？
>   - 思考方向：查询只扫描满足条件的分区，而非全表
> - **实战题（⭐⭐⭐）**：一张日志表有10亿行，按天查询很慢。设计优化方案。
>   - 提示：按天范围分区 + 物化视图汇总日报表

---

## 十三、性能优化与生产配置

### 13.1 postgresql.conf 关键配置

```text
# postgresql.conf 生产配置参考

# 连接
max_connections = 200              # 最大连接数（配合 PgBouncer 可降低）

# 内存
shared_buffers = 4GB              # 共享缓冲区（25% 内存）
effective_cache_size = 12GB       # 有效缓存（75% 内存）
work_mem = 16MB                   # 排序/哈希操作内存
maintenance_work_mem = 512MB      # VACUUM/创建索引内存

# WAL
wal_buffers = 16MB                # WAL 缓冲区
checkpoint_completion_target = 0.9 # 检查点分散写入
max_wal_size = 4GB                # WAL 最大大小
min_wal_size = 1GB                # WAL 最小大小

# 并行
max_worker_processes = 8          # 最大工作进程
max_parallel_workers = 8          # 最大并行查询
max_parallel_workers_per_gather = 4 # 单查询最大并行
```

### 13.2 Python 端性能优化

```python
# 优化1：批量操作替代逐条
# ❌ 慢：循环单条插入
for user in users:
    await conn.execute("INSERT ...", user)  # N次网络往返

# ✅ 快：批量插入
from psycopg2.extras import execute_values
execute_values(cur, "INSERT ... VALUES %s", users)  # 1次网络往返
```

```python
# 优化2：Prepared Statement（asyncpg 自动缓存）
# asyncpg 自动缓存重复 SQL 的执行计划
# 首次查询编译执行计划，后续查询直接用缓存

# 优化3：避免 SELECT *
# ❌ 慢：SELECT * FROM users（返回所有列）
# ✅ 快：SELECT id, name, email FROM users（只查需要的列）

# 优化4：连接池合理配置
# 不要在请求处理中创建新连接！
# ✅ 使用连接池复用连接
```

### 13.3 性能优化 Checklist

| 优化项 | 说明 | 预期收益 |
|--------|------|---------|
| 连接池 | 复用连接 | 减少 90% 连接开销 |
| Prepared Statement | asyncpg 自动缓存 | 重复查询快 2-5 倍 |
| 合适索引 | B-tree/GIN 索引 | 查询快 10-100 倍 |
| 批量操作 | execute_values/COPY | 导入快 10-100 倍 |
| 服务端游标 | 大结果集分批 | 内存从 O(N) 到 O(batch) |
| EXPLAIN ANALYZE | 定位慢查询 | 针对性优化 |
| 物化视图 | 预计算聚合 | 报表从秒级到毫秒级 |
| 分区表 | 大表拆分 | 查询从分钟到毫秒 |
| PgBouncer | 事务级池化 | 支持数千并发连接 |

```python
# PostgreSQL 监控查询
async def pg_stat_activity(conn):
    """查看当前活跃连接"""
    rows = await conn.fetch("""
        SELECT
            pid,
            usename,
            state,
            query_start,
            query
        FROM pg_stat_activity
        WHERE datname = current_database()
        ORDER BY query_start
    """)
    return [dict(r) for r in rows]

async def pg_locks(conn):
    """查看当前锁"""
    rows = await conn.fetch("""
        SELECT
            l.pid,
            l.mode,
            l.granted,
            c.relname
        FROM pg_locks l
        JOIN pg_class c ON l.relation = c.oid
        WHERE l.granted = false
    """)
    return [dict(r) for r in rows]

async def pg_stat_statements(conn):
    """慢查询统计（需要 pg_stat_statements 扩展）"""
    rows = await conn.fetch("""
        SELECT
            query,
            calls,
            total_time,
            mean_time,
            rows
        FROM pg_stat_statements
        ORDER BY mean_time DESC
        LIMIT 10
    """)
    return [dict(r) for r in rows]
```

```python
# 备份与恢复
# pg_dump 备份（命令行）
# pg_dump -U postgres -d mydb > backup.sql

# 恢复
# psql -U postgres -d mydb < backup.sql

# 仅备份表结构
# pg_dump -U postgres -d mydb --schema-only > schema.sql

# 仅备份数据
# pg_dump -U postgres -d mydb --data-only > data.sql

# 压缩备份
# pg_dump -U postgres -d mydb | gzip > backup.sql.gz
```

```python
# PostgreSQL 扩展生态
# PostGIS：地理空间数据
# CREATE EXTENSION postgis;

# pgvector：向量搜索
# CREATE EXTENSION vector;

# pg_trgm：模糊搜索
# CREATE EXTENSION pg_trgm;

# uuid-ossp：UUID 生成
# CREATE EXTENSION "uuid-ossp";

# hstore：键值对存储
# CREATE EXTENSION hstore;

# pgcrypto：加密函数
# CREATE EXTENSION pgcrypto;
```

```python
# 复制与高可用方案
# 1. 流复制（Streaming Replication）
#    - 主库→从库实时同步 WAL
#    - 异步复制（性能优先，可能丢数据）
#    - 同步复制（数据安全，性能略差）

# 2. 逻辑复制（Logical Replication）
#    - 基于 WAL 逻辑解码
#    - 支持表级选择性复制
#    - 支持跨大版本升级

# 3. 高可用方案对比
# | 方案           | RPO     | RTO     | 复杂度  |
# |----------------|---------|---------|---------|
# | 流复制+VIP     | ~0      | ~30s    | 中      |
# | Patroni+ETCD   | ~0      | ~10s    | 高      |
# | WAL-G+S3       | 分钟级  | 分钟级  | 低      |
```

```python
# 连接池配置参数详解
# postgresql.conf 关键参数：
# max_connections = 200           # 最大连接数
# superuser_reserved_connections = 3  # 超级用户保留
# shared_buffers = 256MB           # 共享缓冲区
# effective_cache_size = 1GB        # 优化器预估缓存大小
# work_mem = 4MB                   # 排序/哈希内存
# maintenance_work_mem = 64MB      # VACUUM/建索引内存
```

```python
# 常见坑点速查表
# | 问题                   | 原因                  | 解决方案              |
# |------------------------|-----------------------|-----------------------|
# | too many connections   | 连接池过大            | 减小池大小或用PgBouncer|
# | SQL注入                | 字符串拼接            | 用参数化查询           |
# | 连接泄漏               | acquire未release      | 用async with          |
# | 慢查询                 | 缺索引/全表扫描       | EXPLAIN分析+加索引    |
# | 死锁                   | 加锁顺序不一致        | 统一加锁顺序          |
# | N+1查询                | ORM懒加载            | selectinload预加载    |
# | 锁等待超时             | 长事务持有锁          | 缩短事务              |
# | 索引不生效             | 函数/类型转换         | 表达式索引            |
# | OOM                    | fetchall大结果集      | 服务端游标            |
# | 数据不一致             | 隔离级别太低          | 提高隔离级别          |
```

```python
# 面试高频问题速答
# Q1: PostgreSQL vs MySQL 区别？
# A: PG功能更强大（JSONB、全文搜索、CTE、窗口函数、事务性DDL）
#    MySQL更简单（InnoDB、生态成熟）
#
# Q2: 连接池为什么重要？
# A: 连接创建成本高（TCP+认证），复用连接大幅降低开销
#
# Q3: 如何处理慢查询？
# A: EXPLAIN ANALYZE → 找全表扫描 → 加索引 → 验证
#
# Q4: JSONB vs JSON？
# A: JSONB存储二进制，支持索引和查询；JSON存原始文本
#
# Q5: 如何防止死锁？
# A: 统一加锁顺序、设置锁超时、保持事务简短
```

```python
# 面试加分项：了解 PG 的 MVCC 实现
# PostgreSQL 使用 MVCC（多版本并发控制）
# 读写不互斥：读看到旧版本，写创建新版本
# 不需要读锁，性能好
# 代价：死元组需要 VACUUM 清理
# VACUUM FULL 会锁表（谨慎使用）
# autovacuum 自动清理死元组
# 长事务会阻止 autovacuum 清理
# 所以长事务是性能杀手
# 最佳实践：保持事务简短，不要在事务中做IO
# 不要在事务中调用外部API
# 事务要快进快出
# 保持事务在毫秒级
# 这是性能优化的黄金法则
# 永远记住这一点
```

> 💡 **深度讲解**：PostgreSQL 性能优化是系统工程数据库层面：合理配置内存参数、创建正确索引、分区大表。应用层面：使用连接池、批量操作、避免 N+1 查询、选择合适的驱动。监控层面：慢查询日志、pg_stat_statements、EXPLAIN ANALYZE。核心方法论是"测量→定位→优化→验证"——不要凭感觉优化，用数据驱动。

> 📝 **本章精简总结**：
> - 核心概念：postgresql.conf、连接池、慢查询分析
> - 关键原理：shared_buffers、work_mem、并行查询
> - 常用操作：EXPLAIN ANALYZE、ANALYZE、REINDEX
> - 最佳实践：连接池+批量操作+合适索引
> - 常见坑点：连接池过大、缺索引导致全表扫描
> - 面试高频：shared_buffers 配置、慢查询排查流程

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：shared_buffers 推荐设为多少？
>   - 答案：物理内存的 25%
> - **进阶题（⭐⭐）**：如何排查一个慢查询？
>   - 思考方向：EXPLAIN ANALYZE → 看执行计划 → 找全表扫描 → 加索引
> - **实战题（⭐⭐⭐）**：一个 API 接口 P99 延迟从 50ms 升到 2s。给出排查步骤。
>   - 提示：慢查询日志 → EXPLAIN → 索引检查 → 连接池 → N+1查询

---

## 十四、与 FastAPI 集成及常见坑点

### 14.1 FastAPI + asyncpg 集成

```python
# main.py —— FastAPI + asyncpg 完整集成
from fastapi import FastAPI, Depends
import asyncpg

app = FastAPI()

# 全局连接池
pool = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(
        "postgresql://postgres:secret@localhost:5432/mydb",
        min_size=5,
        max_size=20,
    )

@app.on_event("shutdown")
async def shutdown():
    await pool.close()

# 依赖注入：获取数据库连接
async def get_db():
    async with pool.acquire() as conn:
        yield conn

# API 路由
@app.get("/api/users/{user_id}")
async def get_user(user_id: int, conn=Depends(get_db)):
    row = await conn.fetchrow(
        "SELECT id, email, name FROM users WHERE id = $1",
        user_id,
    )
    if not row:
        return {"error": "用户不存在"}
    return dict(row)

@app.get("/api/users")
async def list_users(
    page: int = 1,
    page_size: int = 20,
    conn=Depends(get_db),
):
    offset = (page - 1) * page_size
    rows = await conn.fetch(
        "SELECT id, email, name FROM users ORDER BY id LIMIT $1 OFFSET $2",
        page_size, offset,
    )
    return {"items": [dict(r) for r in rows], "page": page}
```

```python
# FastAPI + SQLAlchemy 异步集成
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from myapp.database import AsyncSessionLocal, engine

app = FastAPI()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from myapp.models import User

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return {"error": "not found"}
    return {"id": user.id, "email": user.email, "name": user.name}
```

### 14.2 常见坑点汇总

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `connection refused` | PG 未启动/防火墙 | 检查 `pg_isready`、`listen_addresses` |
| `too many connections` | 连接池过大 | 调小 max_size、用 PgBouncer |
| JSONB 查询慢 | 缺 GIN 索引 | 创建 GIN 索引、用 @> 操作符 |
| 数组查询报错 | 类型不匹配 | 显式 `$1::text[]` |
| 中文全文搜索无效 | 默认 english 配置 | 安装 zhparser |
| 深分页极慢 | OFFSET 扫描过多行 | keyset 分页 |
| 事务中 DDL 无法回滚 | CREATE INDEX CONCURRENTLY | 该操作不能在事务中 |
| 连接泄漏 | 获取后未归还 | 用 `async with` 确保归还 |

### 14.3 面试高频考点

```text
PostgreSQL Python 面试考点：

1. psycopg2 vs asyncpg 区别？
   → 同步 vs 异步、%s vs $N、性能差异

2. 连接池大小如何确定？
   → CPU*2+磁盘数、不超过 max_connections

3. JSONB vs JSON？
   → 二进制存储可索引 vs 文本存储

4. 索引类型有哪些？怎么选？
   → B-tree(默认)/GIN(JSONB)/GiST(空间)/BRIN(大表)

5. 事务隔离级别？
   → Read Committed(默认)/Repeatable Read/Serializable

6. MVCC 原理？
   → 多版本并发控制，读不阻塞写

7. 什么是 N+1 查询？如何解决？
   → 循环查数据库；用 JOIN 或批量查询

8. 物化视图 vs 普通视图？
   → 物化存储结果；普通视图每次执行查询

9. 如何优化慢查询？
   → EXPLAIN ANALYZE → 加索引 → 优化SQL

10. 如何防止 SQL 注入？
    → 参数化查询，永不字符串拼接
```

```python
# FastAPI 数据库健康检查端点
@app.get("/health/db")
async def db_health():
    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
        return {"status": "healthy", "db": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# 慢查询日志配置
# postgresql.conf:
# log_min_duration_statement = 1000  # 记录超过1秒的查询
# log_statement = 'mod'              # 记录所有修改语句
```

```python
# FastAPI 依赖注入：按请求创建 Session
from fastapi import Request

async def get_db_session(request: Request):
    """每个请求一个独立的数据库会话"""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

# 在路由中使用
@app.get("/api/items")
async def list_items(db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Item))
    return result.scalars().all()
```

```python
# 错误处理：数据库异常 → HTTP 响应
from fastapi import HTTPException
from asyncpg import PostgresError

@app.exception_handler(PostgresError)
async def db_exception_handler(request, exc):
    return HTTPException(
        status_code=500,
        detail=f"Database error: {str(exc)}"
    )
```

```python
# 事务管理：FastAPI 中使用事务
async def get_db_with_transaction():
    """带事务的数据库会话"""
    async with AsyncSessionLocal() as session:
        async with session.begin():  # 自动 commit/rollback
            yield session
```

```python
# 生产环境部署检查清单
# 1. 连接池配置合理（< max_connections 的 80%）
# 2. pool_pre_ping = True（防止死连接）
# 3. 所有查询参数化（防 SQL 注入）
# 4. 慢查询日志开启（log_min_duration_statement）
# 5. 关键表有合适索引
# 6. 大表分区或物化视图
# 7. 定期 ANALYZE 更新统计信息
# 8. 备份策略（pg_dump + WAL 归档）
# 9. 监控（pg_stat_statements + Prometheus）
# 10. 连接泄漏检测（pool.in_use 监控）
```

```python
# Docker 部署 PostgreSQL
# docker-compose.yml
# version: '3.8'
# services:
#   postgres:
#     image: postgres:16-alpine
#     environment:
#       POSTGRES_USER: myapp
#       POSTGRES_PASSWORD: secret
#       POSTGRES_DB: myapp
#     volumes:
#       - pg_data:/var/lib/postgresql/data
#     ports:
#       - "5432:5432"
#     command:
#       - "max_connections=200"
#       - "shared_buffers=256MB"
# volumes:
#   pg_data:
```

```python
# FastAPI 分页查询最佳实践
from fastapi import Query

@app.get("/api/users")
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * size
    result = await db.execute(
        select(User).offset(offset).limit(size).order_by(User.id)
    )
    total = await db.scalar(select(func.count(User.id)))
    return {
        "items": result.scalars().all(),
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
    }
```

> 💡 **深度讲解**：与 FastAPI 集成的关键是依赖注入模式——每个请求从连接池获取连接，请求结束自动归还。asyncpg 在异步框架中性能最优，但 SQLAlchemy 提供 ORM 抽象。选择原则：简单查询用 asyncpg 直写 SQL（更快更灵活）；复杂业务用 SQLAlchemy ORM（更易维护）。生产环境必须用连接池，永远不要在请求处理中创建新连接。

> 📝 **本章精简总结**：
> - 核心概念：FastAPI 依赖注入、连接池生命周期
> - 关键原理：请求级连接获取/归还
> - 常用操作：Depends(get_db)、async with pool.acquire()
> - 最佳实践：连接池在 startup 创建、shutdown 关闭
> - 常见坑点：连接泄漏、too many connections
> - 面试高频：驱动选型、连接池配置、SQL注入防范

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：FastAPI 中数据库连接应该在哪里创建和关闭？
>   - 答案：startup 时创建连接池，shutdown 时关闭
> - **进阶题（⭐⭐）**：什么是 N+1 查询？如何用 ORM 解决？
>   - 思考方向：1次主查询+N次子查询；用 JOIN/selectinload
> - **实战题（⭐⭐⭐）**：为 FastAPI 项目设计完整的数据库层：连接池、依赖注入、错误处理、健康检查。
>   - 提示：startup 初始化 pool + get_db 依赖 + /health 检查端点

---

## 🔗 关联笔记

- [[SQLAlchemy-ORM核心原理]] — ORM 框架详解
- [[Python-异步编程asyncio]] — 异步编程基础
- [[Redis-Python客户端与缓存策略]] — 缓存策略
- [[PgVector-PostgreSQL向量扩展]] — 向量搜索

**📖 前置知识**

- [[SQLAlchemy-ORM核心原理]]
- [[Python-异步编程asyncio]]

**🏷️ 相关标签**

#Python #PostgreSQL #psycopg2 #asyncpg #SQLAlchemy #JSONB #数据库 #索引优化 #全文搜索

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]
