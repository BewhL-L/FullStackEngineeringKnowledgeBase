---
title: Python 数据库与缓存知识点系统梳理
tags: [Python全栈, Python, 数据库, ORM, SQLAlchemy, Redis, 缓存, 面试]
created: 2026-08-13
updated: 2026-08-13
---

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


# Python 数据库与缓存知识点系统梳理（优化版）

> **文档说明**：系统梳理 Python 生态的数据库访问层与缓存方案，涵盖 SQLAlchemy ORM、异步数据库、Redis 缓存、缓存策略与常见问题。

---

## 1. 概述

Python 数据库生态以 SQLAlchemy 为事实标准 ORM，Django 内置 ORM，异步场景用 SQLAlchemy 2.0 async 或 databases。缓存以 Redis 为主，配合缓存策略提升性能。

**技术栈**：
- **ORM**：SQLAlchemy（主流）、Django ORM、Peewee、SQLModel
- **驱动**：psycopg2（PostgreSQL）、pymysql（MySQL）、aiomysql（异步）
- **缓存**：redis-py、django-cache、Flask-Caching
- **迁移**：Alembic（SQLAlchemy）、Django Migrations

---


---
## 2. SQLAlchemy

### 2.1 核心概念

> 🔍 **知识点深度解析**
>
> **作用**：理解 SQLAlchemy 的核心抽象是高效使用它的前提。
>
> **原理**：Engine 管理连接池，Session 是工作单元（ORM 对话），MetaData 记录表结构，ORM 把类映射为表；1.x 命令式与 2.0 声明式风格并存。
>
> **用法要点**：① Engine 管理连接池 ② Session 是工作单元 ③ MetaData 描述结构 ④ ORM 映射类与表 ⑤ 2.0 风格统一 sync/async


- **Engine**：数据库连接引擎，管理连接池
- **Session**：会话，ORM 操作的工作单元
- **Model**：模型类，映射数据库表
- **Query**：查询构造器

### 2.2 模型定义（2.0 风格）

> 🔍 **知识点深度解析**
>
> **作用**：2.0 风格用 Mapped/declared_attr 等类型化声明，兼顾清晰与可检查。
>
> **原理**：用 DeclarativeBase + Mapped[Type] 声明列与关系，类型注解驱动；relationship 表达一对多/多对多，可配合类型检查。
>
> **用法要点**：① DeclarativeBase 基类 ② Mapped[Type] 类型化列 ③ relationship 表达关系 ④ 注解驱动更清晰 ⑤ 兼容旧式 Column 写法


```python
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    articles = relationship("Article", back_populates="author")

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="articles")
```

### 2.3 基本操作

> 🔍 **知识点深度解析**
>
> **作用**：掌握增删改查与会话提交是日常 ORM 开发的基础。
>
> **原理**：add() 入会话、commit() 落库、query()/select() 查询、flush() 推到数据库；理解会话的脏检查与事务边界。
>
> **用法要点**：① add 入会话 ② commit 提交事务 ③ select/query 查询 ④ flush 推库未提交 ⑤ 注意会话生命周期


```python
# 初始化
engine = create_engine("postgresql://user:pass@localhost/db", pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(bind=engine)

# 创建表
Base.metadata.create_all(engine)

# CRUD
with SessionLocal() as session:
    # 创建
    user = User(username="alice", email="alice@example.com")
    session.add(user)
    session.commit()
    
    # 查询
    user = session.get(User, 1)  # 按主键
    users = session.query(User).filter(User.username.like("%a%")).all()
    user = session.query(User).filter_by(username="alice").first()
    
    # 更新
    user.email = "new@example.com"
    session.commit()
    
    # 删除
    session.delete(user)
    session.commit()
```

### 2.4 关系查询与 N+1 优化

```python

> 🔍 **知识点深度解析**
>
> **作用**：ORM 关系查询的 N+1 问题：1 条查询获取列表 + N 条查询访问关联对象，用预加载优化为 2 条查询。
>
> **原理**：Django：QuerySet 惰性求值，访问外键/多对多时每次触发查询（N+1）。select_related（外键/一对一，JOIN 查询）、prefetch_related（多对多/反向外键，IN 查询+Python 拼接）。SQLAlchemy：joinedload（JOIN）、selectinload（IN 查询）、subqueryload（子查询）。async 版本用 selectinload 避免 joinedload 的笛卡尔积。
>
> **用法要点**：① N+1：1 条查列表 + N 条查关联，列表页性能杀手  ② Django select_related（FK/OneToOne JOIN）、prefetch_related（M2M IN）  ③ SQLAlchemy joinedload（JOIN）、selectinload（IN，async 友好）  ④ Django Debug Toolbar/SQLAlchemy echo 检测 N+1  ⑤ 面试常考：N+1 原因、select_related vs prefetch_related、joinedload vs selectinload

# 1. selectinload：分别查询，Python 端关联（一对多/多对多）
from sqlalchemy.orm import selectinload
users = session.query(User).options(selectinload(User.articles)).all()

# 2. joinedload：JOIN 一次查询（多对一/一对一）
from sqlalchemy.orm import joinedload
articles = session.query(Article).options(joinedload(Article.author)).all()

# 3. 直接 JOIN 查询
result = session.query(Article, User).join(User, Article.author_id == User.id).all()
```

> 🔍 **知识点深度解析**
>
> **作用**：SQLAlchemy 是 Python 最强大的 ORM，理解其查询和关系加载是性能优化的关键。
>
> **原理**：SQLAlchemy 分 Core（SQL 表达式语言）和 ORM（对象映射）两层。ORM 查询默认是惰性的，只有访问结果时才执行 SQL。关系属性默认懒加载（lazy="select"），访问时才查询，循环中访问会导致 N+1 查询。`selectinload` 用 IN 查询分两次获取，`joinedload` 用 LEFT JOIN 一次获取。2.0 版本统一了同步和异步 API，支持 `async with AsyncSession`。连接池由 Engine 管理，`pool_size` 控制常驻连接数，`max_overflow` 控制额外连接数。
>
> **用法要点**：① 永远不要在循环中访问关系属性（N+1），用 selectinload/joinedload；② 批量操作用 `bulk_insert_mappings`/`bulk_update_mappings`；③ 用 `with session.begin()` 自动 commit/rollback；④ 面试常考：N+1 问题、selectinload vs joinedload、连接池、Session 生命周期、SQLAlchemy 1.x vs 2.x。

---


---
## 3. 异步数据库

### 3.1 SQLAlchemy 2.0 Async

> 🔍 **知识点深度解析**
>
> **作用**：异步 SQLAlchemy 让 ORM 在 asyncio 中执行而不阻塞事件循环。
>
> **原理**：使用 AsyncSession 与 async engine，await session.execute(select(...))；底层基于 asyncio 驱动（如 asyncpg），适合 FastAPI 异步栈。
>
> **用法要点**：① AsyncSession 异步会话 ② await execute(select) ③ 底层 asyncpg 等驱动 ④ 配合 FastAPI 异步 ⑤ 事务用 async with


```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
```

### 3.2 其他异步库

> 🔍 **知识点深度解析**
>
> **作用**：除 SQLAlchemy Async 外，aiomysql/asyncpg/Tortoise 等覆盖不同数据库与风格。
>
> **原理**：asyncpg 是 PostgreSQL 高性能驱动，Tortoise ORM 提供 Django 风格异步模型，databases 库包装多种异步驱动。
>
> **用法要点**：① asyncpg 高性能 PG ② Tortoise 异步 ORM ③ databases 多驱动封装 ④ 适配 asyncio ⑤ 按数据库选型


- **asyncpg**：PostgreSQL 异步驱动（性能最好）
- **aiomysql**：MySQL 异步驱动
- **databases**：统一异步数据库接口（支持 SQLAlchemy 查询）
- **Tortoise ORM**：异步 ORM，类似 Django ORM 风格

---


---
## 4. Redis 缓存

### 4.1 基本使用

> 🔍 **知识点深度解析**
>
> **作用**：Redis 是最常用的缓存与数据结构存储，掌握基本命令是缓存层基础。
>
> **原理**：通过 SET/GET 存取值、EXPIRE 设过期、用 String/Hash/List 等结构；Python 用 redis-py 或异步 aioredis 客户端。
>
> **用法要点**：① SET/GET 基本读写 ② EXPIRE 设过期 ③ 多种数据结构 ④ redis-py/aioredis 客户端 ⑤ 连接池复用连接


```python
import redis

# 连接
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# 字符串
r.set("key", "value", ex=3600)  # 1小时过期
r.get("key")

# 哈希
r.hset("user:1", mapping={"name": "Alice", "age": 30})
r.hgetall("user:1")

# 列表
r.lpush("queue", "task1", "task2")
r.rpop("queue")

# 集合/有序集合
r.sadd("tags", "python", "web")
r.zadd("ranking", {"user1": 100, "user2": 90})

# 发布订阅
pubsub = r.pubsub()
pubsub.subscribe("channel")
```

### 4.2 缓存装饰器模式

```python
from functools import wraps
import json

def cache(key_prefix, expire=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{hash(str(args)+str(kwargs))}"
            cached = r.get(cache_key)
            if cached:
                return json.loads(cached)
            result = func(*args, **kwargs)
            r.setex(cache_key, expire, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator

@cache("articles", expire=600)
def get_articles():
    return Article.query.all()
```

> 🔍 **知识点深度解析**
>
> **作用**：Redis 缓存是 Python Web 性能优化的核心手段。
>
> **原理**：Redis 是内存数据库，读写速度极快（10万+ QPS）。缓存模式：① Cache Aside（旁路缓存）：读时先查缓存，没有查 DB 再写缓存；写时更新 DB 后删缓存。② Read/Write Through：缓存层封装读写。③ Write Behind：异步写回。缓存三大问题：穿透（查不存在的数据，用布隆过滤器/缓存空值）、击穿（热点 key 过期，用互斥锁/永不过期）、雪崩（大量 key 同时过期，用过期时间加随机值/多级缓存）。缓存一致性：先更新 DB 再删缓存（延迟双删），不要先删缓存（并发问题）。
>
> **用法要点**：① 缓存 key 设计要规范（`业务:实体:ID`）；② 序列化用 JSON 或 msgpack，不要 pickle（不安全）；③ 热点数据永不过期 + 异步更新；④ 面试常考：缓存三大问题、缓存一致性、缓存策略、Redis 数据结构、分布式锁（见分布式锁文档）。

---

## 4.5 数据库事务

### 4.5.1 ACID 与隔离级别

> 🔍 **知识点深度解析**
>
> **作用**：事务 ACID 与隔离级别决定并发下的数据正确性与性能取舍。
>
> **原理**：原子性/一致性/隔离性/持久性；隔离级别从读未提交到串行化，越高越安全但并发越低，常用可重复读/读已提交。
>
> **用法要点**：① ACID 四特性 ② 隔离级别递增安全 ③ 读已提交/可重复读常用 ④ 串行化性能最低 ⑤ 按业务容忍度选型


| 特性 | 说明 |
|------|------|
| **原子性（Atomicity）** | 事务中操作要么全部成功，要么全部回滚 |
| **一致性（Consistency）** | 事务前后数据保持一致状态 |
| **隔离性（Isolation）** | 并发事务互不干扰 |
| **持久性（Durability）** | 提交后数据永久保存 |

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|----------|------|-----------|------|
| Read Uncommitted | 可能 | 可能 | 可能 |
| Read Committed（Oracle/PG默认） | 否 | 可能 | 可能 |
| Repeatable Read（MySQL默认） | 否 | 否 | 可能（InnoDB用MVCC解决） |
| Serializable | 否 | 否 | 否 |

### 4.5.2 SQLAlchemy 事务管理

```python

> 🔍 **知识点深度解析**
>
> **作用**：SQLAlchemy 事务通过 Session 管理，自动 begin/commit/rollback，支持嵌套事务和保存点。
>
> **原理**：Session 首次操作时自动开启事务，session.commit() 提交，session.rollback() 回滚。with session.begin() 上下文管理器自动提交/回滚。嵌套事务用 session.begin_nested()（SAVEPOINT）。async 版本 AsyncSession 用 async with session.begin()。声明式事务：FastAPI Depends 注入 Session，请求结束自动 commit/rollback。
>
> **用法要点**：① Session 是事务边界，自动 begin，commit/rollback 结束  ② with session.begin() 自动提交异常回滚  ③ begin_nested() 创建 SAVEPOINT 支持部分回滚  ④ AsyncSession: async with session.begin()  ⑤ 面试常考：Session 生命周期、自动事务、SAVEPOINT、声明式事务

# 自动事务（推荐）
with SessionLocal() as session:
    with session.begin():
        session.add(user1)
        session.add(user2)
        # 退出 with 自动 commit，异常自动 rollback

# 手动事务
session = SessionLocal()
try:
    session.add(user)
    session.commit()
except Exception:
    session.rollback()
    raise
finally:
    session.close()

# 悲观锁（SELECT ... FOR UPDATE）
user = session.query(User).filter(User.id == 1).with_for_update().first()

# 乐观锁（版本号）
class User(Base):
    version = Column(Integer, default=0)
# 更新时 WHERE version = :version，影响行数为0则冲突
```

> 🔍 **知识点深度解析**
>
> **作用**：事务是数据库一致性的保证，理解隔离级别和锁机制是高并发开发的基础。
>
> **原理**：MySQL InnoDB 用 MVCC（多版本并发控制）实现 Repeatable Read 下的快照读，避免幻读。当前读（SELECT FOR UPDATE/UPDATE/DELETE）用 Next-Key Lock（记录锁+间隙锁）防止幻读。脏读是读到未提交数据，不可重复读是同一事务两次查询结果不同（其他事务更新），幻读是范围查询结果行数变化。SQLAlchemy 的 Session 是事务边界，`session.begin()` 开启事务，`commit()` 提交，`rollback()` 回滚。悲观锁加锁阻塞，乐观锁用版本号/CAS 无锁竞争。
>
> **用法要点**：① 长事务会持有锁，尽量缩短事务范围；② 高并发用乐观锁（version），低冲突用悲观锁；③ 死锁：固定加锁顺序、设置锁超时；④ 面试常考：ACID、隔离级别、脏读/不可重复读/幻读、MVCC、乐观锁vs悲观锁、死锁。

---

## 4.6 索引优化与执行计划

### 索引类型

> 🔍 **知识点深度解析**
>
> **作用**：不同索引类型适配不同查询模式，选错会既慢又占空间。
>
> **原理**：B+Tree 适合范围/排序，Hash 适合等值，联合索引遵循最左前缀，唯一索引保证唯一；覆盖索引可避免回表。
>
> **用法要点**：① B+Tree 通用 ② Hash 等值快 ③ 联合索引最左前缀 ④ 唯一索引保唯一 ⑤ 覆盖索引免回表


| 类型 | 说明 | 适用场景 |
|------|------|----------|
| B+树索引 | InnoDB 默认，有序，支持范围 | 等值/范围查询、排序 |
| 哈希索引 | O(1) 查找，不支持范围 | Memory 引擎、等值查询 |
| 全文索引 | 分词倒排索引 | 文本搜索（FULLTEXT） |
| 联合索引 | 多列组合，最左前缀 | 多条件查询 |
| 覆盖索引 | 查询列全在索引中，无需回表 | 高频查询优化 |

### EXPLAIN 执行计划

> 🔍 **知识点深度解析**
>
> **作用**：EXPLAIN 让你看见查询如何执行，是定位慢查询的利器。
>
> **原理**：查看 type（访问类型）、rows（扫描行数）、key（命中索引）、Extra（如 Using filesort）；全表扫描与 filesort 是优化重点。
>
> **用法要点**：① 看 type 访问类型 ② 看 rows 扫描行数 ③ 看 key 命中索引 ④ 关注 Using filesort ⑤ 目标减少扫描量


```sql
EXPLAIN SELECT * FROM users WHERE username = 'alice';
-- 关注字段：
-- type: system > const > eq_ref > ref > range > index > ALL（越左越好）
-- key: 实际使用的索引
-- rows: 预估扫描行数
-- Extra: Using index（覆盖索引）、Using filesort（需优化）、Using temporary（需优化）
```

### 索引使用原则

> 🔍 **知识点深度解析**
>
> **作用**：遵循索引使用原则才能让索引真正被命中。
>
> **原理**：遵循最左前缀、不在索引列上做函数/运算、避免隐式类型转换、区分度高才建索引、避免过多索引拖慢写。
>
> **用法要点**：① 最左前缀匹配 ② 索引列避免函数运算 ③ 避免隐式类型转换 ④ 高区分度才建 ⑤ 索引过多拖慢写


- 联合索引遵循**最左前缀**：`(a,b,c)` 可用于 `a`、`a,b`、`a,b,c`，不能用于 `b`、`c`
- 避免索引列上使用函数/运算：`WHERE YEAR(created_at)=2024` 会失效
- 避免 `!=`、`NOT IN`、`LIKE '%xxx'` 导致索引失效
- 字符串列不加引号会隐式转换导致失效
- 选择性低的列（如性别）不适合建索引

---


---
## 5. 数据库性能优化

### 5.1 查询优化

> 🔍 **知识点深度解析**
>
> **作用**：查询优化从减少扫描、避免 N+1、精简返回字段入手。
>
> **原理**：用索引、只查所需列（defer/only）、分页限制、预加载关联、避免 SELECT * 与 ORM 默认全字段加载。
>
> **用法要点**：① 用索引加速 ② 只取所需列 ③ 预加载防 N+1 ④ 分页限制结果 ⑤ 避免 SELECT *


- 添加合适的索引（`CREATE INDEX`）
- 避免 `SELECT *`，只查需要的字段
- 用 `EXPLAIN` 分析执行计划
- 批量操作代替循环单条
- 分页用游标（`WHERE id > last_id`）代替 OFFSET

### 5.2 连接池

> 🔍 **知识点深度解析**
>
> **作用**：连接池复用数据库连接，避免频繁建立连接的开销。
>
> **原理**：Engine 维护池（size/overflow 配置），请求借连接、用完归还；池过小会排队，过大占用数据库资源。
>
> **用法要点**：① 复用连接省开销 ② 配置 pool_size/overflow ③ 用毕归还连接 ④ 注意连接泄漏 ⑤ 异步用异步池


```python
# SQLAlchemy 连接池配置
engine = create_engine(
    "postgresql://user:pass@localhost/db",
    pool_size=10,           # 常驻连接数
    max_overflow=20,        # 最大额外连接
    pool_timeout=30,        # 获取连接超时
    pool_recycle=1800,      # 连接回收时间（避免 MySQL 8小时断开）
    pool_pre_ping=True,     # 连接前 ping 检查
)
```

### 5.3 读写分离

> 🔍 **知识点深度解析**
>
> **作用**：读写分离把读流量分摊到从库，提升整体吞吐与可用性。
>
> **原理**：写走主库、读走从库（可能有复制延迟）；通过绑定引擎/路由实现，对一致性要求高的读需走主库。
>
> **用法要点**：① 写主读从 ② 提升读吞吐 ③ 注意复制延迟 ④ 强一致读走主 ⑤ 借助 ORM 路由


- 主库写，从库读
- SQLAlchemy 用自定义 Session 路由
- Django 用 `DATABASES` 配置 + 路由

---

## 5.4 分库分表策略

当单表数据量过大（千万级以上），需要分库分表提升性能。

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| **垂直分库** | 按业务模块拆分到不同数据库 | 微服务架构 |
| **垂直分表** | 大字段拆到扩展表（冷热分离） | 宽表、大字段 |
| **水平分库** | 同结构数据按规则分到不同库 | 数据量超大 |
| **水平分表** | 同库内按规则拆成多张表 | 单表过大 |

**分片键选择**：
- 范围分片：按 ID/时间范围，易扩容但热点
- 哈希分片：`hash(user_id) % N`，均匀但跨片查询难
- 一致性哈希：扩容时只迁移部分数据

**中间件**：ShardingSphere、MyCat（Java）、Vitess（MySQL）

---


> 🔍 **知识点深度解析**
>
> **作用**：分库分表解决单库单表数据量过大问题，分为垂直拆分（按业务/字段）和水平拆分（按行）。
>
> **原理**：垂直分库：按业务拆库（用户库/订单库/商品库），微服务天然如此。垂直分表：冷热字段分离（大字段拆到扩展表）。水平分表：按分片键（user_id/order_id）将数据分散到多表多库，分片算法：取模（均匀但扩容难）、范围（按时间/ID 区间，易热点）、一致性哈希（扩容迁移少）。中间件：ShardingSphere（Java）、Vitess、Python 用 sqlalchemy-sharding 或应用层路由。
>
> **用法要点**：① 垂直拆分：按业务/字段，水平拆分：按行分片  ② 分片键选择：高基数、查询高频、避免跨片 JOIN  ③ 取模均匀但扩容需数据迁移，一致性哈希迁移少  ④ 跨片查询/分布式事务/全局唯一 ID 是主要挑战  ⑤ 面试常考：垂直 vs 水平、分片算法、扩容迁移、分布式 ID

## 5.5 MongoDB（PyMongo）

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["mydb"]
collection = db["users"]


> 🔍 **知识点深度解析**
>
> **作用**：MongoDB 是文档型 NoSQL，PyMongo/Motor 是 Python 驱动，适合半结构化数据和快速迭代场景。
>
> **原理**：PyMongo 同步驱动：MongoClient 连接，db.col.insert_one/find/update_one/delete_one。Motor 异步驱动（AsyncIO）：AsyncIOMotorClient，await 操作。文档是 BSON（二进制 JSON），支持嵌套文档和数组。索引：create_index（单字段/复合/文本/地理）。聚合管道：$match/$group/$sort/$lookup（JOIN）。适合：日志/内容管理/物联网/原型快速迭代；不适合：多文档事务要求高、复杂 JOIN。
>
> **用法要点**：① PyMongo 同步，Motor 异步（asyncio）  ② 文档 BSON 支持嵌套，schema 灵活适合半结构化数据  ③ 聚合管道 $lookup 实现类 JOIN，$group 分组统计  ④ 索引优化和关系型类似：explain() 分析查询计划  ⑤ 面试常考：MongoDB vs RDBMS、聚合管道、索引、适用场景

# CRUD
collection.insert_one({"name": "Alice", "age": 30})
collection.find({"age": {"$gt": 25}})
collection.update_one({"name": "Alice"}, {"$set": {"age": 31}})
collection.delete_one({"name": "Alice"})

# 聚合管道
pipeline = [
    {"$match": {"age": {"$gt": 20}}},
    {"$group": {"_id": "$city", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
collection.aggregate(pipeline)
```

**MongoDB vs MySQL 选型**：
- 结构化数据、事务、复杂 JOIN → MySQL
- 文档结构灵活、嵌套数据、高写入、无事务 → MongoDB
- 日志、IoT、内容管理 → MongoDB

---

## 5.6 Memcached

```python
import memcache
mc = memcache.Client(["127.0.0.1:11211"], debug=0)
mc.set("key", "value", time=3600)
mc.get("key")
mc.delete("key")
```

**Redis vs Memcached**：
| 维度 | Redis | Memcached |
|------|-------|-----------|
| 数据结构 | 丰富（5+种） | 仅字符串 |
| 持久化 | RDB/AOF | 无 |
| 集群 | 原生支持 | 客户端分片 |
| 内存管理 | 虚拟内存 | LRU 淘汰 |
| 适用 | 复杂缓存、队列、发布订阅 | 简单 KV 缓存 |

---


> 🔍 **知识点深度解析**
>
> **作用**：Memcached 是纯内存键值缓存，简单高效，适合小数据量缓存和 Session 存储。
>
> **原理**：Memcached 多线程架构（比 Redis 单线程在多核下吞吐更高），数据只在内存（重启丢失），LRU 淘汰。数据结构只有 String（value 最大 1MB），不支持持久化/主从/集群（客户端一致性哈希分片）。Python 客户端：pymemcache、python-memcached。与 Redis 对比：Memcached 更简单、多核多线程吞吐高；Redis 数据结构丰富、持久化、主从复制、功能更全面。
>
> **用法要点**：① 纯内存、多线程、多核高吞吐，简单 KV 缓存  ② 只支持 String，value ≤1MB，无持久化，重启丢失  ③ 客户端一致性哈希实现分布式，无服务端集群  ④ Redis 功能更丰富，Memcached 在纯 KV 场景性能更优  ⑤ 面试常考：Memcached vs Redis、多线程模型、一致性哈希


---
## 6. Alembic 数据库迁移

```bash
# 初始化
alembic init alembic

# 生成迁移脚本（自动检测模型变化）
alembic revision --autogenerate -m "create users table"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

---


---
## 7. 面试高频考点

1. **SQLAlchemy ORM**：QuerySet 惰性、Session 生命周期
2. **N+1 查询**：原因、selectinload/joinedload 解决方案
3. **连接池**：配置参数、连接泄漏、pool_recycle
4. **Redis 缓存**：数据结构、缓存策略、三大问题
5. **缓存一致性**：Cache Aside、延迟双删
6. **异步数据库**：asyncpg、SQLAlchemy 2.0 async
7. **数据库索引**：B+树、联合索引、最左前缀、覆盖索引
8. **事务**：ACID、隔离级别、MVCC、乐观锁/悲观锁
9. **读写分离**：主从复制、路由实现
10. **数据库迁移**：Alembic / Django migrations
11. **执行计划**：EXPLAIN 分析、type 级别、Extra 优化
12. **分库分表**：垂直/水平、分片键、一致性哈希
13. **MongoDB**：文档模型、聚合管道、与MySQL选型
14. **Redis vs Memcached**：数据结构、持久化、集群
15. **索引失效**：函数、隐式转换、!=、LIKE前缀%

---


---
## 📝 精简总结

- ORM：SQLAlchemy 是事实标准，Django ORM 内置，2.0 支持异步
- 查询优化：避免 N+1，用 selectinload/joinedload，批量操作
- 连接池：pool_size + max_overflow，pool_recycle 防断开，pool_pre_ping 检测
- 事务：ACID 四特性，四隔离级别，MVCC 解决快照读，乐观锁/悲观锁
- 索引：B+树为主，联合索引最左前缀，覆盖索引免回表，EXPLAIN 分析
- 索引失效：函数/运算、隐式转换、!=、NOT IN、LIKE '%前缀'
- Redis：内存缓存，五大数据结构，Cache Aside 模式
- 缓存三大问题：穿透（布隆过滤器）、击穿（互斥锁）、雪崩（随机过期）
- 缓存一致性：先更 DB 再删缓存，延迟双删
- 分库分表：垂直（业务/字段）、水平（范围/哈希），分片键选择关键
- MongoDB：文档数据库，灵活 schema，聚合管道，适合非结构化数据
- Memcached：简单 KV 缓存，无持久化，适合纯缓存场景
- 异步：asyncpg 性能最优，SQLAlchemy 2.0 统一 API
- 迁移：Alembic（SQLAlchemy）/ Django migrations

---

[[08-Python全栈/MOC-Python全栈|← 返回 Python 全栈 MOC]] | [[Home|🏠 返回首页]]
