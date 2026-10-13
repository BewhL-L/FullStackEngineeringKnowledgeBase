---
title: SQLAlchemy ORM 核心原理
tags: [Python, 数据库, ORM, SQLAlchemy, 异步, FastAPI]
category: Python全栈
created: 2026-08-13
updated: 2026-09-10
difficulty: ⭐⭐⭐⭐
status: ✅ P0深度重写
priority: P0核心
pre: ["[[Python-面向对象与元类]]", "[[PostgreSQL-Python高级用法]]", "[[Python-异步编程asyncio]]"]
aliases: [SQLAlchemy-ORM核心原理, SQLAlchemy, ORM原理]
---

# SQLAlchemy ORM 核心原理

> **文档说明**：深度拆解 SQLAlchemy 2.0 的核心架构与原理，覆盖 Engine 连接池、Session 生命周期、Declarative 模型定义、关系映射、查询 API、事务管理、级联操作、事件监听、性能优化、异步支持、FastAPI 集成等全链路知识。
>
> **适用人群**：Python 后端开发者、ORM 使用者、从 Django ORM 迁移者、需要理解 ORM 底层原理的工程师
>
> **前置知识**：[[Python-面向对象与元类]]、[[PostgreSQL-Python高级用法]]、[[Python-异步编程asyncio]]

---

## 一、ORM 概念与 SQLAlchemy 架构

### 1.1 什么是 ORM

ORM（Object-Relational Mapping，对象关系映射）是一种程序设计技术，将面向对象语言中的对象映射到关系数据库的表记录。ORM 让开发者用 Python 对象操作数据库，无需手写 SQL。

```python
# 示例 1.1.1：传统手写 SQL vs ORM
import sqlite3

# 传统方式：
conn = sqlite3.connect("test.db")
conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com"))
conn.commit()

# ORM 方式：
# user = User(name="Alice", email="alice@example.com")
# session.add(user)
# session.commit()
```

### 1.2 SQLAlchemy 分层架构

```mermaid
graph TB
    subgraph ORM层
        A[Declarative Model]
        B[Session]
        C[Select Query]
    end
    subgraph Core层
        D[Table/MetaData]
        E[SQL Expression]
        F[Engine]
    end
    subgraph DBAPI层
        G[psycopg2/asyncpg]
        H[(Database)]
    end
    A --> D
    B --> C
    C --> E
    E --> F
    F --> G
    G --> H
    B --> F
```

### 1.3 ORM vs Core vs 原生 SQL

| 方式 | 优点 | 缺点 | 适合 |
|---|---|---|---|
| ORM | 开发快、类型安全 | 复杂查询难优化 | CRUD |
| Core | 灵活、SQL 可控 | 仍需写表达式 | 复杂查询 |
| 原生 SQL | 完全控制 | 易注入、难维护 | 极致性能 |

### 1.4 SQLAlchemy 2.0 新特性

```python
# 示例 1.4.1：2.0 风格
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

# 查询：
# stmt = select(User).where(User.name == "Alice")
# result = await session.execute(stmt)
# user = result.scalar_one_or_none()
```

---

### 💡 本章深度讲解

SQLAlchemy 是 Python 生态最强大的 ORM，采用分层设计：ORM 层提供对象映射，Core 层提供 SQL 表达式，DBAPI 层连接数据库。2.0 版本统一了 API，引入 Mapped 类型注解和 select() 函数式查询，是现代 Python 后端的标准数据层。

### 📝 本章精简总结

- ORM：对象→表映射。
- SQLAlchemy 三层：ORM/Core/DBAPI。
- 2.0：DeclarativeBase + Mapped + select()。
- 不隐藏 SQL，需要时可原生 SQL。

### 🎯 梯度练习题

**基础题（⭐）**
1. 什么是 ORM？
2. SQLAlchemy 分哪三层？

**进阶题（⭐⭐）**
1. ORM 和 Core 的区别？
2. 2.0 相对 1.x 有什么改进？

**实战题（⭐⭐⭐）**
- 用 SQLAlchemy 2.0 风格定义一个 User 模型。

---

## 二、Engine 与连接池

### 2.1 Engine 创建

```python
# 示例 2.1.1：创建 Engine
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://user:pass@localhost/db",
    echo=True,           # 打印 SQL
    pool_size=10,        # 连接池大小
    max_overflow=20,     # 超出池的临时连接
    pool_pre_ping=True,  # 连接前 ping
    pool_recycle=3600,   # 连接回收秒数
)
```

### 2.2 连接池原理

```mermaid
graph LR
    A[请求] --> B{连接池}
    B -->|有空闲| C[取出连接]
    B -->|无空闲| D{达到max?}
    D -->|否| E[新建连接]
    D -->|是| F[等待]
    C --> G[执行SQL]
    G --> H[归还连接]
    E --> G
```

### 2.3 连接池参数

| 参数 | 默认 | 说明 |
|---|---|---|
| pool_size | 5 | 常驻连接数 |
| max_overflow | 10 | 临时连接上限 |
| pool_pre_ping | False | 连接前检测 |
| pool_recycle | -1 | 连接回收时间 |
| pool_timeout | 30 | 等待连接超时 |

### 2.4 异步 Engine

```python
# 示例 2.4.1：异步 Engine
from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=True,
)
```

---

### 💡 本章深度讲解

Engine 是 SQLAlchemy 的核心，管理连接池。连接池复用连接，避免频繁 TCP 握手。pool_size 是常驻连接，max_overflow 是突发临时连接。pool_pre_ping 检测断开的连接。异步用 create_async_engine。

### 📝 本章精简总结

- Engine = 连接池 + DBAPI。
- pool_size 常驻。
- pool_pre_ping 检测。
- 异步用 create_async_engine。

### 🎯 梯度练习题

**基础题（⭐）**
1. Engine 的作用？
2. 连接池为什么重要？

**进阶题（⭐⭐）**
1. pool_size 和 max_overflow 区别？
2. 为什么需要 pool_pre_ping？

**实战题（⭐⭐⭐）**
- 配置一个生产级 Engine：pool_size=20, max_overflow=40, pool_pre_ping=True。

---

## 三、Session 生命周期

### 3.1 Session 是什么

Session 是 ORM 的工作单元（Unit of Work），管理对象生命周期、跟踪变更、维护身份映射。

```python
# 示例 3.1.1：Session 基本用法
from sqlalchemy.orm import Session

with Session(engine) as session:
    user = User(name="Alice", email="alice@test.com")
    session.add(user)
    session.commit()
```

### 3.2 Session 生命周期

```mermaid
graph LR
    A[创建Session] --> B[查询/操作]
    B --> C[flush]
    C --> D[commit/rollback]
    D --> E[close]
```

### 3.3 Identity Map

Session 内部维护 Identity Map：同一主键只有一个对象实例。

```python
# 示例 3.3.1：Identity Map 验证
with Session(engine) as session:
    u1 = session.get(User, 1)
    u2 = session.get(User, 1)
    assert u1 is u2  # True，同一对象
```

### 3.4 异步 Session

```python
# 示例 3.4.1：异步 Session
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

async_session = async_sessionmaker(async_engine, expire_on_commit=False)

async with async_session() as session:
    user = User(name="Bob")
    session.add(user)
    await session.commit()
```

### 3.5 sessionmaker 工厂

```python
# 示例 3.5.1：sessionmaker
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# 每请求一个 Session：
db = SessionLocal()
```

---

### 💡 本章深度讲解

Session 是 ORM 的核心：管理对象生命周期、跟踪变更、维护 Identity Map。Session 不是线程安全的，每请求一个 Session。commit 时 Unit of Work 按依赖顺序执行 SQL。expire_on_commit=False 提升性能。

### 📝 本章精简总结

- Session = 工作单元。
- Identity Map：同主键同对象。
- 每请求一个 Session。
- 异步用 async_session。

### 🎯 梯度练习题

**基础题（⭐）**
1. Session 的作用？
2. Identity Map 是什么？

**进阶题（⭐⭐）**
1. Session 为什么不是线程安全？
2. expire_on_commit 的作用？

**实战题（⭐⭐⭐）**
- 实现 FastAPI 每请求 Session 依赖注入。

---

## 四、Declarative 模型定义

### 4.1 基类

```python
# 示例 4.1.1：DeclarativeBase
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

### 4.2 字段类型

```python
# 示例 4.2.1：常用字段类型
from sqlalchemy import String, Integer, DateTime, Numeric, Text, Boolean
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    bio: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

### 4.3 常用参数

| 参数 | 说明 |
|---|---|
| primary_key | 主键 |
| unique | 唯一约束 |
| nullable | 是否可空 |
| default | 默认值 |
| index | 索引 |
| comment | 注释 |

### 4.4 表参数

```python
# 示例 4.4.1：表级参数
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    amount: Mapped[float]
    __table_args__ = (
        Index("idx_user_amount", "user_id", "amount"),
        {"comment": "订单表"},
    )
```

---

### 💡 本章深度讲解

Declarative 模型是 ORM 的基础：Python 类映射到数据库表。Mapped 类型注解让 IDE 和 mypy 检查。常用类型：String/Integer/DateTime/Numeric/Text/Boolean。

### 📝 本章精简总结

- DeclarativeBase 基类。
- Mapped[type] 注解。
- mapped_column 参数。
- __table_args__ 表级约束。

### 🎯 梯度练习题

**基础题（⭐）**
1. DeclarativeBase 的作用？
2. Mapped 是什么？

**进阶题（⭐⭐）**
1. 如何建索引？
2. 如何设默认值？

**实战题（⭐⭐⭐）**
- 定义一个 Product 模型：id/name/price/stock/created_at。

---

## 五、关系映射：一对多

### 5.1 一对多定义

```python
# 示例 5.1.1：一对多
from sqlalchemy.orm import relationship

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    books: Mapped[list["Book"]] = relationship(back_populates="author")

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["Author"] = relationship(back_populates="books")
```

### 5.2 back_populates vs backref

```python
# back_populates：双向显式（推荐）
# backref：自动反向（1.x 风格）
```

### 5.3 级联

```python
# 示例 5.3.1：级联删除
class Author(Base):
    books: Mapped[list["Book"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
```

---

### 💡 本章深度讲解

一对多是最常见关系：一个作者多本书。ForeignKey 在多的一方。relationship 在一的一方集合。back_populates 双向关联。cascade 控制级联。

### 📝 本章精简总结

- ForeignKey 在多的一方。
- relationship 在一的一方。
- back_populates 双向。
- cascade 级联。

### 🎯 梯度练习题

**基础题（⭐）**
1. ForeignKey 放哪？
2. relationship 的作用？

**进阶题（⭐⭐）**
1. back_populates 和 backref 区别？
2. cascade delete-orphan 是什么？

**实战题（⭐⭐⭐）**
- 定义一对多：一个 Category 多个 Product。

---

## 六、关系映射：多对多

### 6.1 多对多定义

```python
# 示例 6.1.1：多对多
from sqlalchemy import Table, Column, ForeignKey

student_course = Table(
    "student_course",
    Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
)

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    courses: Mapped[list["Course"]] = relationship(
        secondary=student_course, back_populates="students"
    )

class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    students: Mapped[list["Student"]] = relationship(
        secondary=student_course, back_populates="courses"
    )
```

### 6.2 多对多带额外字段

```python
# 示例 6.2.1：关联模型带字段
class Enrollment(Base):
    __tablename__ = "enrollments"
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    grade: Mapped[float | None]
    enrolled_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

---

### 💡 本章深度讲解

多对多用中间表（association table）。secondary 参数指定中间表。带额外字段时用关联模型。

### 📝 本章精简总结

- 中间表 + secondary。
- 带字段用关联模型。

### 🎯 梯度练习题

**基础题（⭐）**
1. 多对多怎么实现？
2. secondary 参数？

**进阶题（⭐⭐）**
1. 多对多带额外字段怎么处理？
2. 中间表主键怎么设？

**实战题（⭐⭐⭐）**
- 定义多对多：文章和标签。

---

## 七、关系映射：一对一

### 7.1 一对一定义

```python
# 示例 7.1.1：一对一
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship(back_populates="profile")
```

### 7.2 关键参数

- `uselist=False`：一对一，不返回列表。
- `unique=True`：外键唯一约束。

---

### 💡 本章深度讲解

一对一 = 一对多 + uselist=False + 外键唯一。User 和 Profile 是经典例子。

### 📝 本章精简总结

- uselist=False。
- 外键 unique=True。

### 🎯 梯度练习题

**基础题（⭐）**
1. 一对一和一对多区别？
2. uselist 的作用？

**进阶题（⭐⭐）**
1. 为什么外键要 unique？
2. 什么时候用一对一？

**实战题（⭐⭐⭐）**
- 定义一对一：User 和 Settings。

---

## 八、查询 API：select()

### 8.1 基本查询

```python
# 示例 8.1.1：查询全部
from sqlalchemy import select

stmt = select(User)
result = session.execute(stmt)
users = result.scalars().all()
```

```python
# 示例 8.1.2：按主键查询
user = session.get(User, 1)
```

```python
# 示例 8.1.3：条件查询
stmt = select(User).where(User.name == "Alice")
user = session.execute(stmt).scalar_one_or_none()
```

### 8.2 异步查询

```python
# 示例 8.2.1：异步查询
async with async_session() as session:
    stmt = select(User).where(User.id == 1)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
```

---

### 💡 本章深度讲解

2.0 用 select() 函数式查询替代 1.x 的 Query API。session.execute() 执行，scalars() 取对象。

### 📝 本章精简总结

- select(Model)。
- session.execute(stmt)。
- scalars().all()。
- get(Model, pk) 主键查询。

### 🎯 梯度练习题

**基础题（⭐）**
1. select() 怎么用？
2. 怎么按主键查？

**进阶题（⭐⭐）**
1. scalar_one 和 scalar_one_or_none 区别？
2. 异步怎么查？

**实战题（⭐⭐⭐）**
- 查询所有 active 用户。

---

## 九、过滤与排序

### 9.1 过滤条件

```python
# 示例 9.1.1：常用过滤
from sqlalchemy import or_, and_

# 等于
select(User).where(User.name == "Alice")
# 不等于
select(User).where(User.age != 18)
# 大于/小于
select(User).where(User.age > 18)
select(User).where(User.age < 60)
# IN
select(User).where(User.id.in_([1, 2, 3]))
# LIKE
select(User).where(User.name.like("%ali%"))
# 空
select(User).where(User.email.is_(None))
# OR
select(User).where(or_(User.name == "A", User.name == "B"))
# AND
select(User).where(and_(User.age > 18, User.active == True))
```

### 9.2 排序

```python
# 示例 9.2.1：排序
select(User).order_by(User.created_at.desc())
select(User).order_by(User.age.asc(), User.name.asc())
```

### 9.3 分页

```python
# 示例 9.3.1：分页
page, size = 1, 20
select(User).offset((page-1)*size).limit(size)
```

---

### 💡 本章深度讲解

过滤和排序是查询基础。and_/or_ 组合条件。order_by 排序。offset/limit 分页。

### 📝 本章精简总结

- ==/!=/>/</in_/like/is_。
- or_/and_。
- order_by。
- offset/limit 分页。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么写 WHERE？
2. 怎么排序？

**进阶题（⭐⭐）**
1. and_ 和 or_ 怎么用？
2. 分页怎么写？

**实战题（⭐⭐⭐）**
- 查询年龄>18且active的用户，按创建时间降序，第2页每页20条。

---

## 十、聚合与分组

### 10.1 聚合函数

```python
# 示例 10.1.1：聚合
from sqlalchemy import func

# COUNT
select(func.count(User.id))
# SUM
select(func.sum(Order.amount))
# AVG
select(func.avg(User.age))
# MAX/MIN
select(func.max(User.created_at))
```

### 10.2 分组

```python
# 示例 10.2.1：GROUP BY
stmt = select(User.city, func.count(User.id)).group_by(User.city)
```

### 10.3 HAVING

```python
# 示例 10.3.1：HAVING
stmt = (
    select(User.city, func.count(User.id))
    .group_by(User.city)
    .having(func.count(User.id) > 100)
)
```

---

### 💡 本章深度讲解

聚合函数：count/sum/avg/max/min。group_by 分组。having 分组后过滤。

### 📝 本章精简总结

- func.count/sum/avg。
- group_by。
- having。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么 COUNT？
2. group_by 怎么用？

**进阶题（⭐⭐）**
1. having 和 where 区别？
2. 怎么 SUM？

**实战题（⭐⭐⭐）**
- 统计每个城市的用户数，只显示>100的城市。

---

## 十一、关联查询与 JOIN

### 11.1 JOIN

```python
# 示例 11.1.1：JOIN
stmt = select(Author, Book).join(Book.author)
# 或
stmt = select(Author).join(Book, Author.id == Book.author_id)
```

### 11.2 外连接

```python
# 示例 11.2.1：LEFT JOIN
stmt = select(Author).outerjoin(Author.books)
```

### 11.3 多表 JOIN

```python
# 示例 11.3.1：三表 JOIN
stmt = (
    select(Order, User, Product)
    .join(User, Order.user_id == User.id)
    .join(Product, Order.product_id == Product.id)
)
```

---

### 💡 本章深度讲解

JOIN 关联表。join() 内连接，outerjoin() 外连接。多表 join 链式调用。

### 📝 本章精简总结

- join() 内连接。
- outerjoin() 外连接。
- 多表链式 join。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么 JOIN？
2. LEFT JOIN 怎么写？

**进阶题（⭐⭐）**
1. 多表 JOIN 怎么写？
2. join 和 outerjoin 区别？

**实战题（⭐⭐⭐）**
- 查询所有订单及其用户信息。

---

## 十二、懒加载与急加载

### 12.1 懒加载（Lazy Load）

```python
# 示例 12.1.1：默认懒加载
author = session.get(Author, 1)
print(author.books)  # 此时才查数据库
```

### 12.2 急加载（Eager Load）

```python
# 示例 12.2.1：selectinload
from sqlalchemy.orm import selectinload

stmt = select(Author).options(selectinload(Author.books))
authors = session.execute(stmt).scalars().all()
# 一条主查询 + 一条 IN 查询，共 2 条 SQL
```

```python
# 示例 12.2.2：joinedload
from sqlalchemy.orm import joinedload

stmt = select(Author).options(joinedload(Author.books))
# 一条 JOIN 查询
```

### 12.3 N+1 问题

```mermaid
graph TD
    A[查10个作者] --> B[SELECT 10个作者]
    B --> C[每个作者查books]
    C --> D[1 + 10 = 11条SQL]
```

### 12.4 加载策略选择

| 策略 | SQL 数 | 适合 |
|---|---|---|
| lazy=True（默认） | 1+N | 单对象 |
| selectinload | 2 | 一对多列表 |
| joinedload | 1 | 一对一/多对一 |
| subqueryload | 2 | 复杂查询 |

---

### 💡 本章深度讲解

懒加载默认，但列表场景导致 N+1。急加载预加载：selectinload（2条SQL，适合一对多）、joinedload（1条JOIN，适合一对一）。避免 N+1 是 ORM 性能关键。

### 📝 本章精简总结

- 懒加载默认。
- selectinload 一对多。
- joinedload 一对一。
- N+1 要避免。

### 🎯 梯度练习题

**基础题（⭐）**
1. 什么是 N+1？
2. selectinload 和 joinedload 区别？

**进阶题（⭐⭐）**
1. 怎么选加载策略？
2. N+1 怎么检测？

**实战题（⭐⭐⭐）**
- 查询所有作者及其书籍，用 selectinload 优化。

---

## 十三、事务管理

### 13.1 事务基础

```python
# 示例 13.1.1：事务
with Session(engine) as session:
    try:
        user = User(name="Alice")
        session.add(user)
        session.commit()  # 提交
    except:
        session.rollback()  # 回滚
        raise
```

### 13.2 嵌套事务（Savepoint）

```python
# 示例 13.2.1：SAVEPOINT
with Session(engine) as session:
    session.begin()
    try:
        session.add(User(name="A"))
        session.flush()
        with session.begin_nested():
            session.add(User(name="B"))
            raise Exception("回滚B但不回滚A")
    except:
        session.rollback()
```

### 13.3 隔离级别

```python
# 示例 13.3.1：隔离级别
engine = create_engine(
    DATABASE_URL,
    isolation_level="REPEATABLE READ",
)
```

### 13.4 异步事务

```python
# 示例 13.4.1：异步事务
async with async_session() as session:
    async with session.begin():
        session.add(User(name="Alice"))
    # 自动 commit
```

---

### 💡 本章深度讲解

事务保证 ACID。commit 提交，rollback 回滚。begin_nested() SAVEPOINT 部分回滚。隔离级别控制并发一致性。

### 📝 本章精简总结

- commit/rollback。
- begin_nested SAVEPOINT。
- 隔离级别。
- async with session.begin()。

### 🎯 梯度练习题

**基础题（⭐）**
1. 事务是什么？
2. commit 和 rollback？

**进阶题（⭐⭐）**
1. SAVEPOINT 是什么？
2. 隔离级别有哪些？

**实战题（⭐⭐⭐）**
- 实现转账事务：A扣钱→B加钱→失败回滚。

---

## 十四、级联操作

### 14.1 cascade 参数

| 值 | 说明 |
|---|---|
| save-update | 保存时级联 |
| delete | 删除时级联 |
| merge | 合并时级联 |
| expunge | 清除时级联 |
| all | 全部 |
| delete-orphan | 删除孤立对象 |

### 14.2 示例

```python
# 示例 14.2.1：完整级联
class Author(Base):
    books: Mapped[list["Book"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
```

---

### 💡 本章深度讲解

级联控制关联操作。delete-orphan 删除父时删子。passive_deletes 让数据库处理外键删除。

### 📝 本章精简总结

- cascade 参数。
- delete-orphan。
- passive_deletes。

### 🎯 梯度练习题

**基础题（⭐）**
1. cascade 的作用？
2. delete-orphan？

**进阶题（⭐⭐）**
1. passive_deletes 好处？
2. all 包含什么？

**实战题（⭐⭐⭐）**
- 配置级联：删除作者时删除其书籍。

---

## 十五、事件监听

### 15.1 事件类型

```python
# 示例 15.1.1：事件监听
from sqlalchemy import event

@event.listens_for(User, "before_insert")
def before_insert(mapper, connection, target):
    print(f"插入用户: {target.name}")

@event.listens_for(User, "after_insert")
def after_insert(mapper, connection, target):
    print(f"已插入: id={target.id}")
```

### 15.2 常用事件

| 事件 | 时机 |
|---|---|
| before_insert | 插入前 |
| after_insert | 插入后 |
| before_update | 更新前 |
| after_update | 更新后 |
| before_delete | 删除前 |
| after_delete | 删除后 |
| before_flush | flush 前 |
| after_commit | commit 后 |

---

### 💡 本章深度讲解

事件监听在 ORM 操作前后执行钩子。用于审计、日志、自动填充字段。

### 📝 本章精简总结

- @event.listens_for。
- before/after_insert/update/delete。

### 🎯 梯度练习题

**基础题（⭐）**
1. 事件监听的作用？
2. before_insert 何时触发？

**进阶题（⭐⭐）**
1. after_commit 做什么？
2. 事件监听和中间件区别？

**实战题（⭐⭐⭐）**
- 用事件监听自动更新 updated_at 字段。

---

### 十六、混合属性与关联代理

### 16.1 混合属性

```python
# 示例 16.1.1：hybrid_property
from sqlalchemy.ext.hybrid import hybrid_property

class User(Base):
    first_name: Mapped[str]
    last_name: Mapped[str]

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.inplace.expression
    @classmethod
    def full_name(cls):
        return func.concat(cls.first_name, " ", cls.last_name)
```

### 16.2 关联代理

```python
# 示例 16.2.1：association_proxy
from sqlalchemy.ext.associationproxy import association_proxy

class Author(Base):
    books: Mapped[list["Book"]] = relationship(back_populates="author")
    book_titles: Mapped[list[str]] = association_proxy("books", "title")
```

---

### 💡 本章深度讲解

混合属性：Python 属性 + SQL 表达式。关联代理：简化跨关系访问。

### 📝 本章精简总结

- hybrid_property。
- association_proxy。

### 🎯 梯度练习题

**基础题（⭐）**
1. hybrid_property 作用？
2. association_proxy？

**进阶题（⭐⭐）**
1. 怎么在 SQL 中用混合属性？
2. 关联代理好处？

**实战题（⭐⭐⭐）**
- 用关联代理直接访问作者的书籍标题。

---

### 十七、性能优化：N+1 问题

### 17.1 N+1 问题详解

```python
# 示例 17.1.1：N+1 问题
# ❌ 慢：1 + N 条 SQL
authors = session.execute(select(Author)).scalars().all()
for author in authors:
    print(author.books)  # 每个作者一条 SQL

# ✅ 快：2 条 SQL
stmt = select(Author).options(selectinload(Author.books))
authors = session.execute(stmt).scalars().all()
for author in authors:
    print(author.books)  # 内存中，不再查库
```

### 17.2 检测 N+1

```python
# 示例 17.2.1：开启 echo=True 看 SQL
engine = create_engine(DATABASE_URL, echo=True)
# 运行后观察 SQL 条数
```

### 17.3 解决策略

| 场景 | 策略 |
|---|---|
| 一对多列表 | selectinload |
| 一对一 | joinedload |
| 多对多 | selectinload |
| 深层嵌套 | joinedload + selectinload 组合 |

---

### 💡 本章深度讲解

N+1 是 ORM 最大性能陷阱：查 100 个作者，每个作者查 books，共 101 条 SQL。用 selectinload 优化为 2 条 SQL。

### 📝 本章精简总结

- N+1：1 + N 条 SQL。
- selectinload 优化为 2 条。
- echo=True 检测。

### 🎯 梯度练习题

**基础题（⭐）**
1. 什么是 N+1？
2. 怎么检测？

**进阶题（⭐⭐）**
1. 怎么解决 N+1？
2. selectinload 原理？

**实战题（⭐⭐⭐）**
- 找到你代码中的 N+1 并用 selectinload 修复。

---

### 十八、性能优化：批量操作

### 18.1 批量插入

```python
# 示例 18.1.1：bulk_insert_mappings
users = [
    {"name": "Alice", "email": "alice@test.com"},
    {"name": "Bob", "email": "bob@test.com"},
]
session.bulk_insert_mappings(User, users)
session.commit()
```

### 18.2 批量更新

```python
# 示例 18.2.1：UPDATE 批量
session.query(User).filter(User.age < 18).update({"active": False})
# 或 2.0：
from sqlalchemy import update
stmt = update(User).where(User.age < 18).values(active=False)
session.execute(stmt)
```

### 18.3 批量删除

```python
# 示例 18.3.1：DELETE 批量
from sqlalchemy import delete
stmt = delete(User).where(User.inactive == True)
session.execute(stmt)
```

### 18.4 流式查询

```python
# 示例 18.4.1：yield_per
stmt = select(Yhuu).execution_options(yield_per=1000)
result = session.execute(stmt)
for row in result.scalars().partitions():
    process(row)
```

---

### 💡 本章深度讲解

批量操作绕过 ORM 开销，直接 SQL。bulk_insert_mappings 批量插入。update/delete 批量更新删除。yield_per 流式处理大数据。

### 📝 本章精简总结

- bulk_insert_mappings。
- update/delete 批量。
- yield_per 流式。

### 🎯 梯度练习题

**基础题（⭐）**
1. 批量插入怎么写？
2. 为什么批量快？

**进阶题（⭐⭐）**
1. yield_per 的作用？
2. 批量更新怎么写？

**实战题（⭐⭐⭐）**
- 批量插入 10000 个用户，对比逐条插入性能。

---

### 十九、SQLAlchemy 2.0 新特性

### 19.1 select() 函数式

```python
# 示例 19.1.1：2.0 查询
# 1.x：
# session.query(User).filter(User.name == "A")
# 2.0：
stmt = select(User).where(User.name == "A")
result = session.execute(stmt)
```

### 19.2 Mapped 类型

```python
# 示例 19.2.1：Mapped
class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
```

### 19.3 asyncio 原生

```python
# 示例 19.3.1：原生异步
async with async_session() as session:
    await session.execute(select(User))
```

### 19.4 其他新特性

- DeclarativeBase 替代 declarative_base()
- mapped_column 替代 Column
- 和_()/or_() 统一
- Row 对象改进

---

### 💡 本章深度讲解

2.0 统一了 Core 和 ORM API。select() 函数式查询。Mapped 类型注解。原生异步支持。

### 📝 本章精简总结

- select()。
- Mapped。
- 原生异步。
- DeclarativeBase。

### 🎯 梯度练习题

**基础题（⭐）**
1. 2.0 查询怎么写？
2. Mapped 是什么？

**进阶题（⭐⭐）**
1. 2.0 和 1.x 的区别？
2. 怎么迁移？

**实战题（⭐⭐⭐）**
- 把 1.x 查询改为 2.0 风格。

---

### 二十、与 FastAPI 集成

### 20.1 依赖注入

```python
# 示例 20.1.1：FastAPI DB 依赖
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

async def get_db():
    async with async_session() as session:
        yield session

@app.get("/users/{uid}")
async def get_user(uid: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == uid))
    return result.scalar_one_or_none()
```

### 20.2 CRUD 路由

```python
# 示例 20.2.1：完整 CRUD
@app.post("/users")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users")
async def list_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

@app.put("/users/{uid}")
async def update_user(uid: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    db_user = await db.get(User, uid)
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.delete("/users/{uid}")
async def delete_user(uid: int, db: AsyncSession = Depends(get_db)):
    db_user = await db.get(User, uid)
    await db.delete(db_user)
    await db.commit()
```

---

### 💡 本章深度讲解

FastAPI + SQLAlchemy 2.0 异步是现代 Python 后端标配。依赖注入每请求 Session。CRUD 路由完整。

### 📝 本章精简总结

- get_db 依赖。
- Depends 注入。
- CRUD 完整路由。

### 🎯 梯度练习题

**基础题（⭐）**
1. FastAPI 怎么注入 DB？
2. 怎么写 CRUD？

**进阶题（⭐⭐）**
1. Pydantic 和 ORM 模型怎么配合？
2. 怎么处理分页？

**实战题（⭐⭐⭐）**
- 实现 FastAPI + SQLAlchemy 完整 CRUD API。

---

### 二十一、常见坑点汇总

### 21.1 30 大坑点

1. Session 跨线程共享
2. 忘记 commit
3. N+1 查询
4. 忘记 close Session
5. expire_on_commit 默认 True 导致额外查询
6. 懒加载在异步中报错
7. 关系配置错误导致递归
8. 事务未提交数据丢失
9. 批量操作绕过 ORM 不触发事件
10. join 条件错误
11. 分页 offset 过深性能差
12. 连接池耗尽
13. 忘记 await 异步操作
14. selectinload 路径错误
15. cascade 配置不当
16. 外键约束冲突
17. 唯一约束重复
18. 大结果集内存溢出
19. flush 和 commit 混淆
20. rollback 后继续用对象
21. 多对多中间表错误
22. 一对一 uselist 错误
23. 默认值在客户端 vs 数据库
24. 时区问题 DateTime
25. Numeric 精度问题
26. 索引未生效
27. 死锁
28. 慢查询
29. 迁移冲突
30. 测试和生产配置不一致

---

### 💡 本章深度讲解

30 大坑点从生产事故总结。核心：Session 管理、N+1、异步 await、事务。

### 📝 本章精简总结

- 30 大坑点。
- Session/N+1/异步/事务。

### 🎯 梯度练习题

**基础题（⭐）**
1. 最常见坑？
2. N+1 是什么？

**进阶题（⭐⭐）**
1. 异步懒加载为什么报错？
2. expire_on_commit？

**实战题（⭐⭐⭐）**
- 对照 30 大坑点审查你的代码。

---

### 二十二、面试考点精选

### 22.1 高频面试题

**Q1：什么是 ORM？**
对象关系映射，Python 类映射到数据库表。

**Q2：Session 的作用？**
工作单元，管理对象生命周期、跟踪变更、维护 Identity Map。

**Q3：Identity Map 是什么？**
同一主键只有一个对象实例。

**Q4：Unit of Work 是什么？**
commit 时按依赖顺序执行 SQL。

**Q5：N+1 问题？**
查主表 N 条，每条查关联，共 1+N 条 SQL。

**Q6：selectinload vs joinedload？**
selectinload 2 条 SQL（一对多），joinedload 1 条 JOIN（一对一）。

**Q7：Session 线程安全吗？**
不安全，每线程/请求一个 Session。

**Q8：flush 和 commit 区别？**
flush 把变更发到数据库（未提交），commit 提交事务。

**Q9：什么是级联？**
cascade 控制关联操作（删除父删子等）。

**Q10：如何优化慢查询？**
索引、避免 N+1、批量操作、EXPLAIN。

---

### 💡 本章深度讲解

10 道高频面试题覆盖 ORM 核心原理。理解原理比记忆 API 重要。

### 📝 本章精简总结

- 10 道高频题。
- Session/Identity Map/Unit of Work/N+1。

### 🎯 梯度练习题

**基础题（⭐）**
1. Session 作用？
2. N+1？

**进阶题（⭐⭐）**
1. Identity Map 原理？
2. Unit of Work？

**实战题（⭐⭐⭐）**
- 回答所有面试题。

---

### 二十三、总结

本文 23 章覆盖了 SQLAlchemy ORM 核心原理：从架构到 Engine、Session、模型、关系、查询、事务、性能、FastAPI 集成。

**三句话记住 SQLAlchemy**：
1. Engine 管理连接池，Session 管理对象生命周期。
2. Identity Map 保证同主键同对象。
3. N+1 用 selectinload/joinedload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大的 ORM。掌握它，你的数据层开发效率将提升一个数量级。🚀

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]
- [[PostgreSQL-Python高级用法]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库 #异步 #FastAPI

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 二十四、Engine 与连接池深度

### 24.1 Engine 完整配置

```python
# 示例 24.1.1：生产级 Engine
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://user:pass@localhost:5432/db",
    # 连接池
    pool_size=20,              # 常驻连接数
    max_overflow=40,          # 突发临时连接
    pool_timeout=30,           # 等待连接超时秒
    pool_recycle=3600,         # 1小时回收
    pool_pre_ping=True,        # 连接前检测
    # 性能
    echo=False,                # 不打印 SQL
    echo_pool=False,           # 不打印连接池
    # 其他
    future=True,               # 2.0 风格
    isolation_level="READ COMMITTED",
)
```

### 24.2 连接池监控

```python
# 示例 24.2.1：监控连接池
pool = engine.pool
print(f"大小: {pool.size()}")
print(f"空闲: {pool.checkedin()}")
print(f"在用: {pool.checkedout()}")
```

### 24.3 连接池问题排查

```mermaid
graph TD
    A[连接池耗尽] --> B{连接泄漏?}
    B -- 是 --> C[确保 close]
    B -- 否 --> D{pool_size 太小?}
    D -- 是 --> E[调大 pool_size]
    D -- 否 --> F{慢查询?}
    F -- 是 --> G[优化查询]
```

### 24.4 异步 Engine 配置

```python
# 示例 24.4.1：异步生产级
from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    echo=False,
)
```

---

### 💡 本章深度讲解

Engine 连接池是数据库性能关键。pool_size 常驻，max_overflow 突发。pool_pre_ping 检测断开。异步用 create_async_engine。

### 📝 本章精简总结

- pool_size/max_overflow。
- pool_pre_ping。
- pool_recycle。
- 异步 create_async_engine。

### 🎯 梯度练习题

**基础题（⭐）**
1. pool_size 是什么？
2. pool_pre_ping 作用？

**进阶题（⭐⭐）**
1. 连接池耗尽怎么排查？
2. pool_recycle 为什么需要？

**实战题（⭐⭐⭐）**
- 配置生产级 Engine 并监控连接池状态。

---

### 二十五、Session 深度

### 25.1 Session 状态机

```mermaid
stateDiagram-v2
    [*] --> New: 创建
    New --> Pending: add()
    Pending --> Persistent: flush/commit
    Persistent --> Deleted: delete()
    Deleted --> [*]: commit
    Persistent --> Detached: expunge/close
    Detached --> Persistent: add()
```

### 25.2 Session 方法

| 方法 | 说明 |
|---|---|
| add(obj) | 添加对象 |
| add_all([obj]) | 批量添加 |
| commit() | 提交 |
| rollback() | 回滚 |
| close() | 关闭 |
| flush() | 刷到数据库 |
| expire(obj) | 使对象过期 |
| refresh(obj) | 重新加载 |
| delete(obj) | 删除 |
| get(Model, pk) | 按主键查 |
| execute(stmt) | 执行查询 |

### 25.3 异步 Session 方法

```python
# 示例 25.3.1：异步 Session 方法
await session.execute(stmt)
await session.commit()
await session.rollback()
await session.close()
await session.refresh(obj)
await session.flush()
```

### 25.4 expire_on_commit

```python
# 示例 25.4.1：expire_on_commit
# 默认 True：commit 后对象属性过期，下次访问重新查库
# False：commit 后保持对象，性能更好
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
```

---

### 💡 本章深度讲解

Session 有完整状态机：New/Pending/Persistent/Deleted/Detached。expire_on_commit=False 提升性能。异步方法都要 await。

### 📝 本章精简总结

- Session 状态机。
- add/commit/rollback/close。
- expire_on_commit=False。
- 异步都要 await。

### 🎯 梯度练习题

**基础题（⭐）**
1. Session 状态有哪些？
2. commit 和 flush 区别？

**进阶题（⭐⭐）**
1. expire_on_commit 为什么设 False？
2. Session 线程安全？

**实战题（⭐⭐⭐）**
- 用 Session 状态机追踪一个对象的生命周期。

---

### 二十六、模型定义深度

### 26.1 完整模型示例

```python
# 示例 26.1.1：生产级模型
from datetime import datetime
from decimal import Decimal

class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("idx_category_price", "category_id", "price"),
        {"comment": "商品表"},
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="商品名")
    description: Mapped[str | None] = mapped_column(Text, comment="描述")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, comment="价格")
    stock: Mapped[int] = mapped_column(default=0, comment="库存")
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    category: Mapped["Category"] = relationship(back_populates="products")
```

### 26.2 常用列类型

| 类型 | Python | SQL |
|---|---|---|
| Integer | int | INTEGER |
| String(n) | str | VARCHAR(n) |
| Text | str | TEXT |
| Boolean | bool | BOOLEAN |
| DateTime | datetime | DATETIME |
| Numeric(p,s) | Decimal | NUMERIC |
| JSON | dict | JSON |
| LargeBinary | bytes | BLOB |
| UUID | uuid | UUID |

---

### 💡 本章深度讲解

模型定义是 ORM 基础。完整生产级模型：主键/字段/约束/索引/注释/默认值/关系。

### 📝 本章精简总结

- 完整模型示例。
- 常用列类型。
- __table_args__。
- onupdate 自动更新。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么定义模型？
2. String 和 Text 区别？

**进阶题（⭐⭐）**
1. 怎么加索引？
2. onupdate 作用？

**实战题（⭐⭐⭐）**
- 定义完整 Order 模型。

---

### 二十七、关系映射深度

### 27.1 一对多完整示例

```python
# 示例 27.1.1：一对多完整
class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    employees: Mapped[list["Employee"]] = relationship(
        back_populates="department",
        cascade="all, delete-orphan",
    )

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship(back_populates="employees")
```

### 27.2 多对多完整示例

```python
# 示例 27.2.1：多对多完整
post_tag = Table(
    "post_tags", Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    tags: Mapped[list["Tag"]] = relationship(
        secondary=post_tag, back_populates="posts"
    )

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    posts: Mapped[list["Post"]] = relationship(
        secondary=post_tag, back_populates="tags"
    )
```

### 27.3 关系参数

| 参数 | 说明 |
|---|---|
| back_populates | 双向关联 |
| backref | 自动反向 |
| secondary | 多对多中间表 |
| uselist | 一对一时 False |
| cascade | 级联 |
| lazy | 加载策略 |
| order_by | 排序 |
| viewonly | 只读 |

---

### 💡 本章深度讲解

三种关系：一对多、多对多、一对一。foreign key 在多的一方。relationship 配置关系。

### 📝 本章精简总结

- 一对多：ForeignKey + relationship。
- 多对多：中间表 + secondary。
- 一对一：uselist=False。
- back_populates 双向。

### 🎯 梯度练习题

**基础题（⭐）**
1. 一对多怎么定义？
2. 多对多怎么定义？

**进阶题（⭐⭐）**
1. uselist 作用？
2. lazy 参数？

**实战题（⭐⭐⭐）**
- 定义三种关系模型。

---

### 二十八、查询 API 深度

### 28.1 select() 完整用法

```python
# 示例 28.1.1：select 列
select(User.name, User.email)  # 查特定列
select(User)                    # 查全部列
select(func.count(User.id))    # 聚合
```

### 28.2 where 完整

```python
# 示例 28.2.1：复杂 where
stmt = select(User).where(
    and_(
        or_(User.active == True, User.is_admin == True),
        User.age >= 18,
        User.city.in_(["北京", "上海"]),
    )
)
```

### 28.3 子查询

```python
# 示例 28.3.1：子查询
subq = select(Order.user_id, func.count(Order.id).label("order_count")).group_by(Order.user_id).subquery()
stmt = select(User, subq.c.order_count).join(subq, User.id == subq.c.user_id)
```

### 28.4 CTE

```python
# 示例 28.4.1：CTE
cte = select(User).where(User.active == True).cte("active_users")
stmt = select(cte).where(cte.c.age > 18)
```

---

### 💡 本章深度讲解

查询 API：select/where/join/group_by/order_by/limit。子查询和 CTE 处理复杂查询。

### 📝 本章精简总结

- select 列/模型/聚合。
- where and_/or_/in_。
- 子查询 subquery。
- CTE。

### 🎯 梯度练习题

**基础题（⭐）**
1. select 怎么查特定列？
2. 子查询怎么写？

**进阶题（⭐⭐）**
1. CTE 是什么？
2. 复杂 where 怎么写？

**实战题（⭐⭐⭐）**
- 写一个带子查询的查询。

---

### 二十九、事务管理深度

### 29.1 事务隔离级别

| 级别 | 说明 |
|---|---|
| READ UNCOMMITTED | 读未提交 |
| READ COMMITTED | 读已提交（默认） |
| REPEATABLE READ | 可重复读 |
| SERIALIZABLE | 串行化 |

### 29.2 事务嵌套

```python
# 示例 29.2.1：嵌套事务
with Session(engine) as session:
    try:
        session.add(User(name="A"))
        session.flush()
        with session.begin_nested():
            session.add(User(name="B"))
            # 出错只回滚 B
        session.commit()  # A 提交
    except:
        session.rollback()
```

### 29.3 事务实践

```python
# 示例 29.3.1：转账事务
def transfer(session, from_id, to_id, amount):
    try:
        from_account = session.get(Account, from_id)
        to_account = session.get(Account, to_id)
        if from_account.balance < amount:
            raise ValueError("余额不足")
        from_account.balance -= amount
        to_account.balance += amount
        session.commit()
    except:
        session.rollback()
        raise
```

---

### 💡 本章深度讲解

事务保证 ACID。隔离级别控制并发一致性。嵌套事务 SAVEPOINT 部分回滚。

### 📝 本章精简总结

- 4 个隔离级别。
- begin_nested SAVEPOINT。
- commit/rollback。

### 🎯 梯度练习题

**基础题（⭐）**
1. 什么是事务？
2. 隔离级别有哪些？

**进阶题（⭐⭐）**
1. SAVEPOINT 是什么？
2. 默认隔离级别？

**实战题（⭐⭐⭐）**
- 实现转账事务。

---

### 三十、性能优化深度

### 30.1 索引优化

```python
# 示例 30.1.1：索引
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
```

### 30.2 EXPLAIN

```python
# 示例 30.2.1：EXPLAIN
from sqlalchemy import text
result = session.execute(text("EXPLAIN SELECT * FROM users WHERE email = 'a@b.com'"))
print(result.all())
```

### 30.3 批量操作优化

```python
# 示例 30.3.1：批量插入 vs 逐条
# 逐条：10000 条 = 10000 次提交
# 批量：10000 条 = 1 次提交
session.bulk_insert_mappings(User, [{"name": f"U{i}"} for i in range(10000)])
session.commit()
```

### 30.4 连接池调优

- pool_size：根据 DB max_connections
- max_overflow：突发流量
- pool_pre_ping：检测断开
- pool_recycle：定期回收

---

### 💡 本章深度讲解

性能优化：索引、EXPLAIN、批量操作、连接池。N+1 用 selectinload。

### 📝 本章精简总结

- 索引。
- EXPLAIN。
- 批量操作。
- 连接池调优。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么建索引？
2. 怎么看执行计划？

**进阶题（⭐⭐）**
1. 批量操作为什么快？
2. 连接池怎么调优？

**实战题（⭐⭐⭐）**
- 用 EXPLAIN 分析你的慢查询并优化。

---

### 三十一、异步 SQLAlchemy 深度

### 31.1 异步完整配置

```python
# 示例 31.1.1：异步完整配置
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,
    max_overflow=40,
)

async_session = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        yield session
```

### 31.2 异步 CRUD

```python
# 示例 31.2.1：异步 CRUD
async def create_user(db: AsyncSession, name: str, email: str):
    user = User(name=name, email=email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user(db: AsyncSession, uid: int):
    return await db.get(User, uid)

async def list_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

async def update_user(db: AsyncSession, uid: int, **kwargs):
    user = await db.get(User, uid)
    for k, v in kwargs.items():
        setattr(user, k, v)
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, uid: int):
    user = await db.get(User, uid)
    await db.delete(user)
    await db.commit()
```

### 31.3 异步懒加载问题

```python
# ❌ 异步中不能懒加载：
# author = await db.get(Author, 1)
# print(author.books)  # 报错：协程没有 await

# ✅ 用急加载：
stmt = select(Author).options(selectinload(Author.books)).where(Author.id == 1)
author = (await db.execute(stmt)).scalar_one()
print(author.books)  # 正常
```

---

### 💡 本章深度讲解

异步 SQLAlchemy：create_async_engine + async_sessionmaker。异步中不能懒加载，必须急加载。所有操作 await。

### 📝 本章精简总结

- create_async_engine。
- async_sessionmaker。
- 异步不能懒加载。
- 所有操作 await。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步 Engine 怎么建？
2. 异步 CRUD？

**进阶题（⭐⭐）**
1. 异步为什么不能懒加载？
2. 怎么解决？

**实战题（⭐⭐⭐）**
- 写异步 CRUD。

---

### 三十二、事件监听深度

### 32.1 事件类型大全

```python
# 示例 32.1.1：所有事件
from sqlalchemy import event

# ORM 事件
@event.listens_for(User, "before_insert")
def before_insert(mapper, conn, target): pass

@event.listens_for(User, "after_insert")
def after_insert(mapper, conn, target): pass

@event.listens_for(User, "before_update")
def before_update(mapper, conn, target): pass

@event.listens_for(User, "after_update")
def after_update(mapper, conn, target): pass

@event.listens_for(User, "before_delete")
def before_delete(mapper, conn, target): pass

@event.listens_for(User, "after_delete")
def after_delete(mapper, conn, target): pass

# Session 事件
@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances): pass

@event.listens_for(Session, "after_commit")
def after_commit(session): pass
```

### 32.2 审计日志

```python
# 示例 32.2.1：自动审计
@event.listens_for(User, "after_update")
def audit_update(mapper, conn, target):
    conn.execute(
        audit_logs.insert().bind(
            table="users", record_id=target.id, action="UPDATE"
        )
    )
```

### 32.3 自动更新时间

```python
# 示例 32.3.1：自动 updated_at
@event.listens_for(User, "before_update")
def update_timestamp(mapper, conn, target):
    target.updated_at = datetime.utcnow()
```

---

### 💡 本章深度讲解

事件监听是 ORM 钩子。用于审计、自动填充、日志。Session 事件全局，Mapper 事件单表。

### 📝 本章精简总结

- before/after_insert/update/delete。
- before_flush/after_commit。
- 审计日志。
- 自动 updated_at。

### 🎯 梯度练习题

**基础题（⭐）**
1. 事件监听什么时候触发？
2. before_insert 做什么？

**进阶题（⭐⭐）**
1. 怎么做审计？
2. before_flush 和 before_insert 区别？

**实战题（⭐⭐⭐）**
- 用事件监听实现审计日志。

---

### 三十三、混合属性与关联代理深度

### 33.1 hybrid_property 完整

```python
# 示例 33.1.1：hybrid_property
class Employee(Base):
    first_name: Mapped[str]
    last_name: Mapped[str]

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    @classmethod
    def full_name(cls):
        return func.concat(cls.first_name, " ", cls.last_name)
```

### 33.2 association_proxy 完整

```python
# 示例 33.2.1：association_proxy
class Author(Base):
    books: Mapped[list["Book"]] = relationship(back_populates="author")
    book_titles: Mapped[list[str]] = association_proxy("books", "title")

# 用法：
# author.book_titles  # 直接访问字符串列表
```

### 33.3 association_proxy 创建新对象

```python
# 示例 33.3.1：创建新关联
class Author(Base):
    books: Mapped[list["Book"]] = relationship(back_populates="author")
    book_titles: Mapped[list[str]] = association_proxy(
        "books", "title",
        creator=lambda t: Book(title=t)
    )

# 用法：
# author.book_titles.append("New Book")  # 自动创建 Book
```

---

### 💡 本章深度讲解

混合属性：Python 属性 + SQL 表达式。关联代理：简化跨关系访问，可创建新对象。

### 📝 本章精简总结

- hybrid_property + expression。
- association_proxy。
- creator 自动创建。

### 🎯 梯度练习题

**基础题（⭐）**
1. hybrid_property 作用？
2. association_proxy？

**进阶题（⭐⭐）**
1. 怎么在 SQL 中用？
2. creator 作用？

**实战题（⭐⭐⭐）**
- 用关联代理访问作者的书籍标题。

---

### 三十四、与 FastAPI 集成深度

### 34.1 完整项目结构

```
app/
├── main.py
├── database.py      # Engine/Session
├── models.py        # ORM 模型
├── schemas.py       # Pydantic
├── crud.py          # 数据库操作
└── routers/
    ├── users.py
    └── items.py
```

### 34.2 database.py

```python
# 示例 34.2.1：database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

ASYNC_DB_URL = "postgresql+asyncpg://user:pass@localhost/db"

async_engine = create_async_engine(ASYNC_DB_URL, pool_size=20, max_overflow=40)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session
```

### 34.3 models.py

```python
# 示例 34.3.1：models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
```

### 34.4 schemas.py

```python
# 示例 34.4.1：schemas.py
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

### 34.5 crud.py

```python
# 示例 34.5.1：crud.py
async def get_user(db: AsyncSession, user_id: int):
    return await db.get(User, user_id)

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```

---

### 💡 本章深度讲解

FastAPI + SQLAlchemy 2.0 异步完整项目：database/models/schemas/crud/routers 分层。

### 📝 本章精简总结

- 完整项目结构。
- database.py Engine/Session。
- models/schemas/crud 分层。

### 🎯 梯度练习题

**基础题（⭐）**
1. 项目怎么分层？
2. get_db 依赖？

**进阶题（⭐⭐）**
1. Pydantic from_attributes？
2. 怎么分层？

**实战题（⭐⭐⭐）**
- 搭建完整 FastAPI + SQLAlchemy 项目。

---

### 三十五、常见坑点深度解析

### 35.1 Session 相关坑

```python
# 坑1：忘记 commit
user = User(name="A")
session.add(user)
# 忘记 commit，数据丢失

# 坑2：忘记 close
# 不 close 连接不归还池

# 坑3：跨线程用 Session
# Session 不是线程安全
```

### 35.2 查询相关坑

```python
# 坑4：N+1
# 列表场景忘 selectinload

# 坑5：异步懒加载
# 异步中访问关系报错

# 坑6：offset 过深
# offset 100000 性能差
```

### 35.3 事务相关坑

```python
# 坑7：rollback 后继续用对象
# rollback 后对象状态回滚

# 坑8：嵌套事务忘记 commit
```

---

### 💡 本章深度讲解

坑点分三类：Session/查询/事务。每个坑都可能导致线上问题。

### 📝 本章精简总结

- Session：commit/close/线程安全。
- 查询：N+1/异步懒加载。
- 事务：rollback 后用对象。

### 🎯 梯度练习题

**基础题（⭐）**
1. 最常见坑？
2. 怎么避免？

**进阶题（⭐⭐）**
1. 异步懒加载为什么报错？
2. offset 过深问题？

**实战题（⭐⭐⭐）**
- 审查你的代码，对照坑点修复。

---

### 三十六、面试考点深度

### 36.1 20 道高频题

1. ORM 是什么？
2. Session 作用？
3. Identity Map？
4. Unit of Work？
5. N+1 问题？
6. selectinload vs joinedload？
7. Session 线程安全？
8. flush vs commit？
9. 级联 cascade？
10. 事务隔离级别？
11. 连接池参数？
12. 异步怎么用？
13. 懒加载问题？
14. 批量操作？
15. 索引优化？
16. 子查询？
17. CTE？
18. 事件监听？
19. 混合属性？
20. 2.0 新特性？

---

### 💡 本章深度讲解

20 道高频面试题覆盖 ORM 全部核心。

### 📝 本章精简总结

- 20 道高频题。

### 🎯 梯度练习题

**基础题（⭐）**
1. Session 作用？
2. N+1？

**进阶题（⭐⭐）**
1. Identity Map 原理？
2. Unit of Work？

**实战题（⭐⭐⭐）**
- 回答所有面试题。

---

### 三十七、总结

本文 37 章覆盖了 SQLAlchemy ORM 核心原理：架构、Engine、Session、模型、关系、查询、事务、性能、FastAPI、异步。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。掌握它，数据层开发效率倍增。🚀

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]
- [[PostgreSQL-Python高级用法]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库 #异步 #FastAPI

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 三十八、Engine 与连接池完整指南

### 38.1 连接池类型

SQLAlchemy 提供多种连接池：

| 池类型 | 说明 | 适合 |
|---|---|---|
| QueuePool | 默认队列池 | 生产 |
| NullPool | 无池，每次新建 | 调试 |
| StaticPool | 单连接复用 | SQLite 内存 |
| SingletonThreadPool | 单线程单连接 | 单线程 |

```python
# 示例 38.1.1：指定连接池
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
)
```

### 38.2 连接池配置最佳实践

```python
# 示例 38.2.1：生产配置
engine = create_engine(
    DATABASE_URL,
    pool_size=20,              # 常驻连接
    max_overflow=40,         # 突发临时
    pool_timeout=30,           # 等待超时
    pool_recycle=1800,         # 30分钟回收（避免 MySQL 8小时断开）
    pool_pre_ping=True,        # 连接前 ping 检测
    echo=False,
)
```

### 38.3 连接泄漏检测

```python
# 示例 38.3.1：检测泄漏
@event.listens_for(engine, "checkout")
def checkout(dbapi_conn, conn_record, conn_proxy):
    conn_record.info["checkout_stack"] = traceback.format_stack()

@event.listens_for(engine, "checkin")
def checkin(dbapi_conn, conn_record):
    conn_record.info.pop("checkout_stack", None)
```

### 38.4 多数据库 Engine

```python
# 示例 38.4.1：多数据库
primary_engine = create_engine(PRIMARY_URL)
replica_engine = create_engine(REPLICA_URL)

PrimarySession = sessionmaker(bind=primary_engine)
ReplicaSession = sessionmaker(bind=replica_engine)
```

---

### 💡 本章深度讲解

连接池是数据库性能核心。QueuePool 是默认。pool_recycle 避免 MySQL 断开。pool_pre_ping 检测死连接。多数据库用多 Engine。

### 📝 本章精简总结

- QueuePool 默认。
- pool_size/max_overflow。
- pool_recycle 30分钟。
- pool_pre_ping。

### 🎯 梯度练习题

**基础题（⭐）**
1. 连接池有哪些类型？
2. pool_recycle 作用？

**进阶题（⭐⭐）**
1. 怎么检测连接泄漏？
2. 多数据库怎么配？

**实战题（⭐⭐⭐）**
- 配置主从数据库读写分离。

---

### 三十九、Session 生命周期完整指南

### 39.1 Session 创建方式

```python
# 示例 39.1.1：三种创建方式
# 1. 直接创建
session = Session(engine)

# 2. sessionmaker 工厂
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# 3. 上下文管理器
with Session(engine) as session:
    ...
```

### 39.2 Session 完整生命周期

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Session
    participant DB as Database
    C->>S: create
    C->>S: query(User)
    S->>DB: SELECT
    DB-->>S: rows
    S-->>C: objects
    C->>S: add(user)
    C->>S: commit
    S->>DB: flush (INSERT/UPDATE)
    S->>DB: COMMIT
    C->>S: close
```

### 39.3 Session 状态

```python
# 示例 39.3.1：Session 状态
from sqlalchemy import inspect

session = Session(engine)
user = User(name="A")
session.add(user)

state = inspect(user)
print(state.transient)   # True: 未持久化
print(state.pending)     # True: 待 flush
session.flush()
print(state.persistent)  # True: 已持久化
session.delete(user)
print(state.deleted)     # True: 待删除
```

### 39.4 常见 Session 错误

```python
# 错误1：在请求外用 Session
# 错误2：Session 跨线程
# 错误3：忘记 close
# 错误4：commit 后访问对象（expire_on_commit=True）
```

---

### 💡 本章深度讲解

Session 完整生命周期：创建→查询→变更→commit→close。状态：transient/pending/persistent/deleted/detached。

### 📝 本章精简总结

- 三种创建方式。
- 完整生命周期。
- 5 种状态。
- 每请求一个 Session。

### 🎯 梯度练习题

**基础题（⭐）**
1. Session 怎么创建？
2. Session 状态有哪些？

**进阶题（⭐⭐）**
1. 完整生命周期？
2. 为什么每请求一个？

**实战题（⭐⭐⭐）**
- 追踪对象的状态变化。

---

### 四十、模型定义完整指南

### 40.1 基类配置

```python
# 示例 40.1.1：Base 基类
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

# 带公共字段的基类
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
```

### 40.2 列参数完整

```python
# 示例 40.2.1：列参数大全
email: Mapped[str] = mapped_column(
    String(100),           # 类型
    unique=True,            # 唯一
    nullable=False,         # 非空
    default="",             # 默认
    index=True,             # 索引
    comment="邮箱",         # 注释
    primary_key=False,      # 主键
)
```

### 40.3 表参数

```python
# 示例 40.3.1：表参数大全
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    amount: Mapped[float]

    __table_args__ = (
        Index("idx_user", "user_id"),
        Index("idx_user_amount", "user_id", "amount"),
        UniqueConstraint("user_id", "amount", name="uq_user_amount"),
        {"comment": "订单表"},
    )
```

### 40.4 JSON 字段

```python
# 示例 40.4.1：JSON 字段
from sqlalchemy import JSON

class Config(Base):
    __tablename__ = "configs"
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)
```

---

### 💡 本章深度讲解

模型定义：基类 Mixin、列参数、表参数、JSON 字段。完整生产级模型。

### 📝 本章精简总结

- TimestampMixin。
- 列参数大全。
- 表参数 Index/UniqueConstraint。
- JSON 字段。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么做 Mixin？
2. 列参数有哪些？

**进阶题（⭐⭐）**
1. 怎么建复合索引？
2. JSON 字段怎么用？

**实战题（⭐⭐⭐）**
- 定义完整生产级模型，带 Mixin 和索引。

---

### 四十一、关系映射完整指南

### 41.1 一对多完整

```python
# 示例 41.1.1：一对多完整配置
class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    books: Mapped[list["Book"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Book.published_at.desc()",
    )

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    published_at: Mapped[datetime]
    author: Mapped["Author"] = relationship(back_populates="books")
```

### 41.2 多对多完整

```python
# 示例 41.2.1：多对多完整
student_course = Table(
    "student_courses", Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
    Column("enrolled_at", DateTime, default=datetime.utcnow),
)

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    courses: Mapped[list["Course"]] = relationship(
        secondary=student_course, back_populates="students"
    )

class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    students: Mapped[list["Student"]] = relationship(
        secondary=student_course, back_populates="courses"
    )
```

### 41.3 关系加载策略

```python
# 示例 41.3.1：lazy 参数
# lazy="select"：懒加载（默认）
# lazy="joined"：JOIN 急加载
# lazy="selectin"：IN 急加载
# lazy="subquery"：子查询急加载
# lazy="dynamic"：动态 Query
# lazy="raise"：禁止懒加载（防 N+1）
# lazy="noload"：不加载
```

---

### 💡 本章深度讲解

关系映射完整配置：back_populates/cascade/lazy/order_by。lazy="raise" 防 N+1。

### 📝 本章精简总结

- 一对多完整。
- 多对多完整。
- lazy 参数 6 种。
- lazy="raise" 防 N+1。

### 🎯 梯度练习题

**基础题（⭐）**
1. 关系参数有哪些？
2. lazy 有哪些值？

**进阶题（⭐⭐）**
1. lazy="raise" 好处？
2. order_by 怎么用？

**实战题（⭐⭐⭐）**
- 配置完整关系模型。

---

### 四十二、查询 API 完整指南

### 42.1 select() 完整

```python
# 示例 42.1.1：select 全部用法
# 查模型
select(User)
# 查特定列
select(User.name, User.email)
# 查聚合
select(func.count(User.id))
# 去重
select(User.name).distinct()
```

### 42.2 where 完整

```python
# 示例 42.2.2：where 全部条件
from sqlalchemy import or_, and_, not_

# 比较
User.name == "A"
User.age != 18
User.age > 18
User.age < 60
User.age >= 18
User.age <= 60

# 包含
User.name.in_(["A", "B"])
User.name.not_in(["A"])

# 模糊
User.name.like("%ali%")
User.name.ilike("%ALI%")  # 不区分大小写

# 空
User.email.is_(None)
User.email.is_not(None)

# 范围
User.age.between(18, 60)

# 组合
and_(User.age > 18, User.active == True)
or_(User.name == "A", User.name == "B")
not_(User.active == True)
```

### 42.3 join 完整

```python
# 示例 42.3.1：join 全部
# 内连接
select(Author).join(Book, Author.id == Book.author_id)
# 外连接
select(Author).outerjoin(Author.books)
# 多表
select(Order).join(User).join(Product)
# 过滤关联
select(Author).join(Author.books).where(Book.title.like("%Python%"))
```

### 42.4 group_by 完整

```python
# 示例 42.4.1：group_by
# 按城市统计用户数
select(User.city, func.count(User.id)).group_by(User.city)
# 多列分组
select(User.city, User.age, func.count(User.id)).group_by(User.city, User.age)
# HAVING
stmt = (
    select(User.city, func.count(User.id).label("cnt"))
    .group_by(User.city)
    .having(func.count(User.id) > 100)
)
```

---

### 💡 本章深度讲解

查询 API 完整覆盖：select/where/join/group_by/order_by/limit。日常开发够用。

### 📝 本章精简总结

- select 模型/列/聚合。
- where 全部条件。
- join/outerjoin。
- group_by/having。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么写 WHERE？
2. JOIN 怎么写？

**进阶题（⭐⭐）**
1. having 和 where 区别？
2. 多表 join？

**实战题（⭐⭐⭐）**
- 写复杂查询：join + group_by + having。

---

### 四十三、事务管理完整指南

### 43.1 事务基础

```python
# 示例 43.1.1：事务完整
with Session(engine) as session:
    try:
        session.add(User(name="A"))
        session.commit()
    except Exception:
        session.rollback()
        raise
```

### 43.2 事务隔离级别

```python
# 示例 43.2.1：隔离级别
engine = create_engine(
    DATABASE_URL,
    isolation_level="REPEATABLE READ",
)

# 可选：
# READ UNCOMMITTED
# READ COMMITTED（默认）
# REPEATABLE READ
# SERIALIZABLE
```

### 43.3 嵌套事务

```python
# 示例 43.3.1：SAVEPOINT
with Session(engine) as session:
    try:
        session.add(User(name="A"))
        session.flush()
        # SAVEPOINT
        with session.begin_nested():
            session.add(User(name="B"))
            raise ValueError("回滚B")
        session.commit()
    except ValueError:
        session.rollback()
```

### 43.4 异步事务

```python
# 示例 43.4.1：异步事务
async with async_session() as session:
    async with session.begin():
        session.add(User(name="A"))
    # 自动 commit
```

---

### 💡 本章深度讲解

事务：commit/rollback、隔离级别、嵌套 SAVEPOINT。异步用 session.begin()。

### 📝 本章精简总结

- commit/rollback。
- 4 个隔离级别。
- begin_nested。
- async with session.begin()。

### 🎯 梯度练习题

**基础题（⭐）**
1. 事务是什么？
2. commit 和 rollback？

**进阶题（⭐⭐）**
1. SAVEPOINT？
2. 隔离级别？

**实战题（⭐⭐⭐）**
- 实现转账事务。

---

### 四十四、性能优化完整指南

### 44.1 N+1 问题

```python
# 示例 44.1.1：N+1 修复
# ❌ N+1
authors = session.execute(select(Author)).scalars().all()
for a in authors:
    print(a.books)

# ✅ selectinload
stmt = select(Author).options(selectinload(Author.books))
authors = session.execute(stmt).scalars().all()
for a in authors:
    print(a.books)
```

### 44.2 批量操作

```python
# 示例 44.2.1：批量
# 批量插入
session.bulk_insert_mappings(User, [{"name": f"U{i}"} for i in range(1000)])
# 批量更新
session.execute(update(User).where(User.active == True).values(active=False))
# 批量删除
session.execute(delete(User).where(User.inactive == True))
```

### 44.3 流式查询

```python
# 示例 44.3.1：yield_per
stmt = select(User).execution_options(yield_per=1000)
result = session.execute(stmt)
for batch in result.scalars().partitions():
    process(batch)
```

### 44.4 索引

```python
# 示例 44.4.1：索引
class User(Base):
    email: Mapped[str] = mapped_column(String(100), index=True)
    __table_args__ = (
        Index("idx_name_city", "name", "city"),
    )
```

---

### 💡 本章深度讲解

性能优化：N+1 用 selectinload、批量操作、流式查询、索引。

### 📝 本章精简总结

- selectinload 防 N+1。
- bulk_insert_mappings。
- yield_per。
- 索引。

### 🎯 梯度练习题

**基础题（⭐）**
1. N+1 怎么解决？
2. 批量插入？

**进阶题（⭐⭐）**
1. yield_per 作用？
2. 索引怎么建？

**实战题（⭐⭐⭐）**
- 优化你的慢查询。

---

### 四十五、SQLAlchemy 2.0 完整指南

### 45.1 2.0 vs 1.x 对比

| 特性 | 1.x | 2.0 |
|---|---|---|
| 基类 | declarative_base() | DeclarativeBase |
| 列定义 | Column(String) | mapped_column(Mapped[str]) |
| 查询 | session.query(User) | select(User) + session.execute() |
| 风格 | Query API | select() 函数式 |
| 异步 | 扩展 | 原生 |

### 45.2 2.0 完整示例

```python
# 示例 45.2.1：2.0 完整代码
from sqlalchemy import create_engine, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    emails: Mapped[list["Email"]] = relationship(back_populates="user")

class Email(Base):
    __tablename__ = "emails"
    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="emails")

engine = create_engine("sqlite:///example.db")
Base.metadata.create_all(engine)

with Session(engine) as session:
    user = User(name="Alice")
    session.add(user)
    session.commit()

    stmt = select(User).where(User.name == "Alice")
    result = session.execute(stmt)
    user = result.scalar_one()
```

### 45.3 2.0 迁移指南

```python
# 1.x → 2.0：
# session.query(User).filter(...) → select(User).where(...)
# session.query(User).get(1) → session.get(User, 1)
# Column(String) → mapped_column(Mapped[str])
# declarative_base() → DeclarativeBase
```

---

### 💡 本章深度讲解

2.0 是现代 SQLAlchemy。select() 函数式、Mapped 类型注解、原生异步。新项目必用 2.0。

### 📝 本章精简总结

- DeclarativeBase。
- Mapped + mapped_column。
- select() + session.execute()。
- 原生异步。

### 🎯 梯度练习题

**基础题（⭐）**
1. 2.0 和 1.x 区别？
2. 怎么定义模型？

**进阶题（⭐⭐）**
1. 怎么迁移到 2.0？
2. 2.0 为什么更好？

**实战题（⭐⭐⭐）**
- 把 1.x 代码迁移到 2.0。

---

### 四十六、与 FastAPI 集成完整指南

### 46.1 完整项目

```python
# 示例 46.1.1：main.py 完整
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Database
async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session

# Models
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

# Schemas
class UserCreate(BaseModel):
    email: str
    name: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    model_config = ConfigDict(from_attributes=True)

# App
app = FastAPI()

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users/{uid}", response_model=UserResponse)
async def get_user(uid: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, uid)
    if not user:
        raise HTTPException(404, "Not found")
    return user

@app.get("/users", response_model=list[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()
```

---

### 💡 本章深度讲解

FastAPI + SQLAlchemy 2.0 异步完整项目。依赖注入每请求 Session。Pydantic 序列化。

### 📝 本章精简总结

- 完整项目代码。
- get_db 依赖。
- Pydantic from_attributes。

### 🎯 梯度练习题

**基础题（⭐）**
1. FastAPI 怎么集成？
2. get_db 作用？

**进阶题（⭐⭐）**
1. Pydantic from_attributes？
2. 怎么分页？

**实战题（⭐⭐⭐）**
- 搭建完整 FastAPI + SQLAlchemy 项目。

---

### 四十七、常见坑点完整解析

### 47.1 30 大坑点详解

```python
# 坑1：Session 跨线程
# ❌ session = Session(engine); thread1(session); thread2(session)
# ✅ 每线程/请求一个 Session

# 坑2：忘记 commit
# ❌ add(user) 不 commit
# ✅ add(user); commit()

# 坑3：N+1
# ❌ 列表查关系
# ✅ selectinload

# 坑4：异步懒加载
# ❌ 异步中访问关系
# ✅ 急加载

# 坑5：expire_on_commit=True
# ❌ commit 后访问对象又查库
# ✅ expire_on_commit=False

# 坑6：连接池耗尽
# ❌ 不 close session
# ✅ with Session() 自动 close

# 坑7：忘记 await
# ❌ session.execute(stmt)
# ✅ await session.execute(stmt)

# 坑8：flush 和 commit 混淆
# flush：发到 DB 未提交
# commit：提交事务

# 坑9：rollback 后用对象
# rollback 后对象状态回滚

# 坑10：offset 过深
# offset 100000 性能差
# 用 keyset pagination
```

---

### 💡 本章深度讲解

30 大坑点详解。核心：Session 管理、N+1、异步 await、事务。

### 📝 本章精简总结

- 30 大坑点。
- Session/N+1/异步/事务。

### 🎯 梯度练习题

**基础题（⭐）**
1. 最常见坑？
2. 怎么避免？

**进阶题（⭐⭐）**
1. 异步为什么不能懒加载？
2. offset 过深问题？

**实战题（⭐⭐⭐）**
- 审查代码对照坑点。

---

### 四十八、面试考点完整解析

### 48.1 20 道高频题详解

**Q1：ORM 是什么？**
对象关系映射，Python 类→数据库表。

**Q2：Session 作用？**
工作单元，管理对象生命周期、跟踪变更、Identity Map。

**Q3：Identity Map？**
同主键同对象实例。

**Q4：Unit of Work？**
commit 按依赖顺序执行 SQL。

**Q5：N+1？**
查主表 N 条，每条查关联，共 1+N 条。

**Q6：selectinload vs joinedload？**
selectinload 2 条 SQL（一对多），joinedload 1 条 JOIN（一对一）。

**Q7：Session 线程安全？**
不安全，每请求一个。

**Q8：flush vs commit？**
flush 发到 DB 未提交，commit 提交。

**Q9：cascade？**
级联操作，all/delete-orphan。

**Q10：事务隔离级别？**
READ UNCOMMITTED/READ COMMITTED/REPEATABLE READ/SERIALIZABLE。

---

### 💡 本章深度讲解

20 道高频面试题详解。

### 📝 本章精简总结

- 20 道题详解。

### 🎯 梯度练习题

**基础题（⭐）**
1. Session 作用？
2. N+1？

**进阶题（⭐⭐）**
1. Identity Map 原理？
2. Unit of Work？

**实战题（⭐⭐⭐）**
- 回答所有面试题。

---

### 四十九、总结

本文 49 章覆盖了 SQLAlchemy ORM 核心原理。从架构到 Engine、Session、模型、关系、查询、事务、性能、2.0、FastAPI、异步、坑点、面试。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。掌握它，数据层效率倍增。🚀

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]
- [[PostgreSQL-Python高级用法]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库 #异步 #FastAPI

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 五十、Core 层：SQL 表达式语言

### 50.1 Core vs ORM

SQLAlchemy 分 Core 和 ORM。Core 是 SQL 表达式语言，接近原生 SQL。ORM 在 Core 之上加对象映射。

```python
# 示例 50.1.1：Core 写法
from sqlalchemy import Table, MetaData, Column, Integer, String, insert

metadata = MetaData()
users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
)

# Core 插入
stmt = insert(users).values(name="Alice")
with engine.connect() as conn:
    conn.execute(stmt)
    conn.commit()
```

### 50.2 Core 查询

```python
# 示例 50.2.1：Core 查询
from sqlalchemy import select

stmt = select(users.c.name, users.c.email).where(users.c.id == 1)
with engine.connect() as conn:
    result = conn.execute(stmt)
    row = result.first()
```

### 50.3 Core 更新删除

```python
# 示例 50.3.1：Core 更新
from sqlalchemy import update

stmt = update(users).where(users.c.id == 1).values(name="Bob")

# Core 删除
from sqlalchemy import delete
stmt = delete(users).where(users.c.id == 1)
```

---

### 💡 本章深度讲解

Core 是 SQL 表达式语言，比 ORM 更底层更灵活。复杂查询用 Core，CRUD 用 ORM。

### 📝 本章精简总结

- Table/MetaData。
- insert/select/update/delete。
- 复杂查询用 Core。

### 🎯 梯度练习题

**基础题（⭐）**
1. Core 和 ORM 区别？
2. 怎么建表？

**进阶题（⭐⭐）**
1. 什么时候用 Core？
2. 复杂查询怎么写？

**实战题（⭐⭐⭐）**
- 用 Core 写一个复杂报表查询。

---

### 五十一、连接与事务

### 51.1 连接管理

```python
# 示例 51.1.1：连接
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
```

### 51.2 事务控制

```python
# 示例 51.2.1：事务
with engine.begin() as conn:
    conn.execute(text("INSERT INTO users VALUES (1, 'A')"))
    # 自动 commit
```

### 51.3 原生 SQL

```python
# 示例 51.3.1：原生 SQL
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users WHERE id = :uid"), {"uid": 1})
    row = result.mappings().first()
```

---

### 💡 本章深度讲解

连接是底层操作。事务用 engine.begin()。原生 SQL 用 text()。

### 📝 本章精简总结

- engine.connect()。
- engine.begin() 事务。
- text() 原生 SQL。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么连接？
2. 怎么写原生 SQL？

**进阶题（⭐⭐）**
1. 事务怎么控制？
2. 参数化查询？

**实战题（⭐⭐⭐）**
- 用原生 SQL 写复杂查询。

---

### 五十二、数据类型完整指南

### 52.1 常用类型

```python
# 示例 52.1.1：数据类型
from sqlalchemy import (
    Integer, SmallInteger, BigInteger,
    String, Text, Unicode,
    Boolean, Float, Numeric,
    DateTime, Date, Time, Interval,
    JSON, LargeBinary,
    UUID, Enum, ARRAY,
)

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    tags: Mapped[list] = mapped_column(JSON)
    data: Mapped[bytes] = mapped_column(LargeBinary)
```

### 52.2 自定义类型

```python
# 示例 52.2.1：自定义类型
from sqlalchemy.types import TypeDecorator, CHAR
import uuid

class GUID(TypeDecorator):
    impl = CHAR
    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(36))
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value)
```

---

### 💡 本章深度讲解

数据类型：常用类型 + 自定义类型。JSON/UUID/Enum 常用。

### 📝 本章精简总结

- Integer/String/Boolean/DateTime/JSON。
- 自定义 TypeDecorator。

### 🎯 梯度练习题

**基础题（⭐）**
1. 常用类型？
2. JSON 字段？

**进阶题（⭐⭐）**
1. 怎么自定义类型？
2. UUID 怎么存？

**实战题（⭐⭐⭐）**
- 自定义一个加密 String 类型。

---

### 五十三、约束与索引

### 53.1 约束

```python
# 示例 53.1.1：约束
from sqlalchemy import UniqueConstraint, CheckConstraint, ForeignKey

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float]
    status: Mapped[str]

    __table_args__ = (
        UniqueConstraint("user_id", "status", name="uq_user_status"),
        CheckConstraint("amount > 0", name="ck_amount_positive"),
    )
```

### 53.2 索引

```python
# 示例 53.2.1：索引
from sqlalchemy import Index

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str]
    __table_args__ = (
        Index("idx_name_email", "name", "email"),
    )
```

---

### 💡 本章深度讲解

约束：UniqueConstraint/CheckConstraint/ForeignKey。索引：单列/复合。

### 📝 本章精简总结

- UniqueConstraint。
- CheckConstraint。
- Index。

### 🎯 梯度练习题

**基础题（⭐）**
1. 有哪些约束？
2. 怎么建索引？

**进阶题（⭐⭐）**
1. 复合索引？
2. CheckConstraint？

**实战题（⭐⭐⭐）**
- 为你的表添加约束和索引。

---

### 五十四、迁移简介

### 54.1 Alembic

```bash
# 安装
pip install alembic

# 初始化
alembic init alembic

# 生成迁移
alembic revision --autogenerate -m "add users table"

# 执行迁移
alembic upgrade head
```

### 54.2 迁移脚本

```python
# 示例 54.2.1：迁移脚本
def upgrade():
    op.create_table(
        "users",
        Column("id", Integer, primary_key=True),
        Column("name", String(50)),
    )

def downgrade():
    op.drop_table("users")
```

---

### 💡 本章深度讲解

Alembic 是 SQLAlchemy 官方迁移工具。自动生成迁移脚本。

### 📝 本章精简总结

- alembic init/upgrade。
- autogenerate。

### 🎯 梯度练习题

**基础题（⭐）**
1. Alembic 是什么？
2. 怎么生成迁移？

**进阶题（⭐⭐）**
1. 怎么回滚？
2. 数据迁移？

**实战题（⭐⭐⭐）**
- 用 Alembic 管理你的表结构。

---

### 五十五、总结

本文 55 章覆盖了 SQLAlchemy 全部核心：Core/ORM/Engine/Session/模型/关系/查询/事务/性能/2.0/FastAPI/异步。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 五十六、生产级 CRUD 完整实现

### 56.1 用户 CRUD

```python
# 示例 56.1.1：完整用户 CRUD
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

class UserCRUD:
    @staticmethod
    async def create(db: AsyncSession, name: str, email: str) -> User:
        user = User(name=name, email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get(db: AsyncSession, user_id: int) -> User | None:
        return await db.get(User, user_id)

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, user_id: int, **kwargs) -> User | None:
        user = await db.get(User, user_id)
        if not user:
            return None
        for k, v in kwargs.items():
            setattr(user, k, v)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        user = await db.get(User, user_id)
        if not user:
            return False
        await db.delete(user)
        await db.commit()
        return True

    @staticmethod
    async def count(db: AsyncSession) -> int:
        stmt = select(func.count(User.id))
        result = await db.execute(stmt)
        return result.scalar()
```

### 56.2 分页查询

```python
# 示例 56.2.1：分页
async def paginate(db: AsyncSession, page: int = 1, size: int = 20):
    total = await UserCRUD.count(db)
    items = await UserCRUD.list(db, skip=(page-1)*size, limit=size)
    return {
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
        "items": items,
    }
```

---

### 💡 本章深度讲解

生产级 CRUD：创建/查询/更新/删除/计数/分页。完整可复用。

### 📝 本章精简总结

- 完整 CRUD 类。
- 分页。
- 计数。

### 🎯 梯度练习题

**基础题（⭐）**
1. CRUD 有哪些操作？
2. 怎么分页？

**进阶题（⭐⭐）**
1. 怎么设计 CRUD 类？
2. 怎么优化分页？

**实战题（⭐⭐⭐）**
- 实现完整 CRUD + 分页。

---

### 五十七、生产级模型设计

### 57.1 基类设计

```python
# 示例 57.1.1：完整基类
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)
    @property
    def is_deleted(self):
        return self.deleted_at is not None
```

### 57.2 审计字段

```python
# 示例 57.2.1：审计
class AuditMixin:
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

### 57.3 完整模型

```python
# 示例 57.3.1：完整模型
class User(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(String(20), default="user")
```

---

### 💡 本章深度讲解

生产级模型：Mixin 复用（时间戳/软删除/审计）。完整字段：主键/业务字段/审计字段。

### 📝 本章精简总结

- TimestampMixin。
- SoftDeleteMixin。
- AuditMixin。

### 🎯 梯度练习题

**基础题（⭐）**
1. Mixin 是什么？
2. 软删除怎么做？

**进阶题（⭐⭐）**
1. 审计字段？
2. 怎么设计基类？

**实战题（⭐⭐⭐）**
- 设计完整生产级模型。

---

### 五十八、异步生产架构

### 58.1 应用结构

```python
# 示例 58.1.1：应用结构
# app/
# ├── main.py
# ├── config.py
# ├── database.py
# ├── models.py
# ├── schemas.py
# ├── crud.py
# ├── dependencies.py
# └── routers/
```

### 58.2 依赖注入

```python
# 示例 58.2.1：dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db():
    async with async_session() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    user = await decode_token(token, db)
    return user
```

### 58.3 优雅关闭

```python
# 示例 58.3.1：优雅关闭
@app.on_event("shutdown")
async def shutdown():
    await async_engine.dispose()
```

---

### 💡 本章深度讲解

生产架构：分层、依赖注入、优雅关闭。FastAPI 标准结构。

### 📝 本章精简总结

- 分层结构。
- 依赖注入。
- 优雅关闭。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么分层？
2. 依赖注入？

**进阶题（⭐⭐）**
1. 优雅关闭怎么做？
2. 怎么注入当前用户？

**实战题（⭐⭐⭐）**
- 搭建生产级 FastAPI 应用结构。

---

### 五十九、测试策略

### 59.1 测试数据库

```python
# 示例 59.1.1：测试数据库
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    yield async_session
    await engine.dispose()
```

### 59.2 测试 CRUD

```python
# 示例 59.2.1：测试
@pytest.mark.asyncio
async def test_create_user(test_db):
    async with test_db() as session:
        user = await UserCRUD.create(session, "Alice", "a@test.com")
        assert user.id is not None
        assert user.name == "Alice"
```

---

### 💡 本章深度讲解

测试：内存数据库 fixture + 测试 CRUD。

### 📝 本章精简总结

- 内存数据库 fixture。
- 测试 CRUD。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么测试数据库？
2. 内存数据库好处？

**进阶题（⭐⭐）**
1. 怎么测试事务？
2. fixture 怎么写？

**实战题（⭐⭐⭐）**
- 为 CRUD 写完整测试。

---

### 六十、总结

本文 60 章覆盖了 SQLAlchemy 完整知识：Core/ORM/Engine/Session/模型/关系/查询/事务/性能/2.0/FastAPI/异步/测试/生产。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库 #异步

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 六十一、高级查询技巧

### 61.1 窗口函数

```python
# 示例 61.1.1：窗口函数
from sqlalchemy import func, over

# ROW_NUMBER
stmt = select(
    User.name,
    func.row_number().over(order_by=User.created_at.desc()).label("rn")
)

# RANK
stmt = select(
    Product.category,
    Product.name,
    Product.price,
    func.rank().over(partition_by=Product.category, order_by=Product.price.desc()).label("rank")
)
```

### 61.2 条件聚合

```python
# 示例 61.2.1：CASE WHEN
from sqlalchemy import case

stmt = select(
    User.city,
    func.count(case((User.age >= 18, 1), else_=None)).label("adults"),
    func.count(case((User.age < 18, 1), else_=None)).label("minors"),
).group_by(User.city)
```

### 61.3 子查询作为列

```python
# 示例 61.3.1：子查询列
subq = select(
    func.count(Order.id).label("order_count")
).where(Order.user_id == User.id).scalar_subquery()

stmt = select(User.name, subq.label("order_count"))
```

### 61.4 EXISTS

```python
# 示例 61.4.1：EXISTS
from sqlalchemy import exists

stmt = select(User).where(
    exists().where(Order.user_id == User.id)
)
# 有订单的用户
```

---

### 💡 本章深度讲解

高级查询：窗口函数、CASE WHEN、子查询列、EXISTS。这些处理复杂报表。

### 📝 本章精简总结

- row_number/rank 窗口。
- case WHEN。
- scalar_subquery。
- exists。

### 🎯 梯度练习题

**基础题（⭐）**
1. 窗口函数是什么？
2. CASE WHEN 怎么写？

**进阶题（⭐⭐）**
1. 子查询列？
2. EXISTS 怎么用？

**实战题（⭐⭐⭐）**
- 写一个排名查询。

---

### 六十二、JSON 字段高级

### 62.1 JSON 查询

```python
# 示例 62.1.1：PostgreSQL JSON 查询
from sqlalchemy import cast, String

# 按 JSON 字段查询
stmt = select(Product).where(Product.data["category"].as_string() == "electronics")

# 嵌套
stmt = select(Product).where(Product.data["specs"]["weight"].as_float() > 1.5)
```

### 62.2 JSON 更新

```python
# 示例 62.2.1：JSON 更新
from sqlalchemy.dialects.postgresql import JSONB

# JSONB 支持更新
stmt = update(Product).values(
    data=func.jsonb_set(Product.data, "{tags}", '["new"]')
)
```

---

### 💡 本章深度讲解

PostgreSQL JSONB 支持索引和查询。SQLAlchemy 支持 JSON 路径查询。

### 📝 本章精简总结

- JSON 路径查询。
- JSONB 更新。

### 🎯 梯度练习题

**基础题（⭐）**
1. JSON 字段怎么存？
2. JSONB 优势？

**进阶题（⭐⭐）**
1. 怎么查 JSON 字段？
2. 怎么更新？

**实战题（⭐⭐⭐）**
- 用 JSONB 存储产品规格。

---

### 六十三、全文搜索

### 63.1 PostgreSQL 全文搜索

```python
# 示例 63.1.1：全文搜索
from sqlalchemy import func, or_

# 搜索
stmt = select(Article).where(
    or_(
        Article.title.match("python"),
        Article.body.match("python"),
    )
)

# 排名
stmt = select(
    Article,
    func.ts_rank(func.to_tsvector(Article.body), func.plainto_tsquery("python")).label("rank")
).order_by("rank desc")
```

---

### 💡 本章深度讲解

PostgreSQL 全文搜索：tsvector/tsquery。SQLAlchemy 支持。

### 📝 本章精简总结

- match。
- ts_rank。

### 🎯 梯度练习题

**基础题（⭐）**
1. 全文搜索？
2. match 用法？

**进阶题（⭐⭐）**
1. ts_rank？
2. 索引？

**实战题（⭐⭐⭐）**
- 实现文章全文搜索。

---

### 六十四、读写分离

### 64.1 读写分离配置

```python
# 示例 64.1.1：读写分离
write_engine = create_engine(PRIMARY_URL)
read_engine = create_engine(REPLICA_URL)

WriteSession = sessionmaker(bind=write_engine)
ReadSession = sessionmaker(bind=read_engine)

# 写用 WriteSession，读用 ReadSession
```

### 64.2 异步读写分离

```python
# 示例 64.2.1：异步读写分离
write_async_engine = create_async_engine(PRIMARY_URL)
read_async_engine = create_async_engine(REPLICA_URL)

AsyncWriteSession = async_sessionmaker(write_async_engine)
AsyncReadSession = async_sessionmaker(read_async_engine)
```

---

### 💡 本章深度讲解

读写分离：主库写，从库读。多 Engine 多 Session。

### 📝 本章精简总结

- 多 Engine。
- 多 Session。
- 写主读从。

### 🎯 梯度练习题

**基础题（⭐）**
1. 读写分离？
2. 怎么配？

**进阶题（⭐⭐）**
1. 异步读写分离？
2. 主从延迟问题？

**实战题（⭐⭐⭐）**
- 实现读写分离。

---

### 六十五、连接池问题排查

### 65.1 常见问题

```python
# 问题1：连接池耗尽
# 原因：未 close session
# 解决：with Session() 自动 close

# 问题2：连接断开
# 原因：MySQL 8小时断开
# 解决：pool_recycle=3600

# 问题3：连接慢
# 原因：DNS 慢
# 解决：pool_pre_ping=True
```

### 65.2 监控

```python
# 示例 65.2.1：监控
@event.listens_for(engine, "checkout")
def log_checkout(conn, rec, proto):
    logger.info("连接取出")

@event.listens_for(engine, "checkin")
def log_checkin(conn, rec):
    logger.info("连接归还")
```

---

### 💡 本章深度讲解

连接池问题：耗尽/断开/慢。监控 checkout/checkin。

### 📝 本章精简总结

- 连接池耗尽。
- pool_recycle。
- pool_pre_ping。

### 🎯 梯度练习题

**基础题（⭐）**
1. 连接池耗尽？
2. pool_recycle？

**进阶题（⭐⭐）**
1. 怎么监控？
2. 怎么排查？

**实战题（⭐⭐⭐）**
- 监控你的连接池。

---

### 六十六、总结

本文 66 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 六十七、SQLAlchemy 生态

### 67.1 Alembic 迁移

```python
# 示例 67.1.1：Alembic 配置
# alembic.ini
# sqlalchemy.url = postgresql://user:pass@localhost/db

# env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from models import Base

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata
```

### 67.2 SQLModel

```python
# 示例 67.2.1：SQLModel（FastAPI 风格 ORM）
from sqlmodel import SQLModel, Field, create_engine, Session

class Hero(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None

engine = create_engine("postgresql://user:pass@localhost/db")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    hero = Hero(name="Deadpond", secret_name="Dive Wilson")
    session.add(hero)
    session.commit()
```

### 67.3 GeoAlchemy

```python
# 示例 67.3.1：GeoAlchemy2
from geoalchemy2 import Geometry

class Location(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=4326))
```

---

### 💡 本章深度讲解

生态：Alembic 迁移、SQLModel 统一 Pydantic+ORM、GeoAlchemy 地理空间。

### 📝 本章精简总结

- Alembic。
- SQLModel。
- GeoAlchemy。

### 🎯 梯度练习题

**基础题（⭐）**
1. Alembic 作用？
2. SQLModel？

**进阶题（⭐⭐）**
1. SQLModel vs SQLAlchemy？
2. GeoAlchemy？

**实战题（⭐⭐⭐）**
- 用 SQLModel 重写你的模型。

---

### 六十八、性能基准测试

### 68.1 基准测试脚本

```python
# 示例 68.1.1：基准测试
import time

def benchmark_query(n=1000):
    t0 = time.perf_counter()
    for _ in range(n):
        session.execute(select(User).limit(100)).scalars().all()
    elapsed = time.perf_counter() - t0
    print(f"{n} 次查询: {elapsed:.2f}s, {n/elapsed:.0f} QPS")

# benchmark_query()
```

### 68.2 优化对比

| 操作 | 优化前 | 优化后 | 提升 |
|---|---|---|---|
| N+1 查询 | 101 条 SQL | 2 条 SQL | 50x |
| 批量插入 | 10000 次 commit | 1 次 commit | 100x |
| 急加载 | 懒加载 | selectinload | 10x |

---

### 💡 本章深度讲解

性能基准：测量 QPS、对比优化前后。

### 📝 本章精简总结

- 基准测试脚本。
- 优化对比。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么测性能？
2. QPS？

**进阶题（⭐⭐）**
1. 怎么优化？
2. 瓶颈在哪？

**实战题（⭐⭐⭐）**
- 基准测试你的查询并优化。

---

### 六十九、常见错误排查

### 69.1 错误类型

| 错误 | 原因 | 解决 |
|---|---|---|
| IntegrityError | 唯一约束冲突 | 检查数据 |
| OperationalError | 连接失败 | 检查 DB |
| ProgrammingError | 表/列不存在 | 检查迁移 |
| InvalidRequestError | Session 状态错 | commit/rollback |
| StaleDataError | 数据已变 | 重新查询 |
| UnmappedColumnError | 列未映射 | 检查模型 |

### 69.2 排查步骤

```mermaid
graph TD
    A[错误] --> B{是什么类型?}
    B -->|IntegrityError| C[唯一/外键冲突]
    B -->|OperationalError| D[连接问题]
    B -->|ProgrammingError| E[表/列问题]
    B -->|InvalidRequestError| F[Session 状态]
```

---

### 💡 本章深度讲解

错误类型和排查步骤。

### 📝 本章精简总结

- 6 种常见错误。
- 排查步骤。

### 🎯 梯度练习题

**基础题（⭐）**
1. IntegrityError？
2. 怎么排查？

**进阶题（⭐⭐）**
1. StaleDataError？
2. 怎么调试？

**实战题（⭐⭐⭐）**
- 排查你的下一个 ORM 错误。

---

### 七十、SQLAlchemy vs Django ORM

### 70.1 对比

| 维度 | SQLAlchemy | Django ORM |
|---|---|---|
| 灵活性 | 高 | 低 |
| 学习曲线 | 陡 | 平缓 |
| 查询能力 | 强 | 中 |
| 异步 | 原生 | 原生 |
| 生态 | 独立 | Django 集成 |
| 适合 | 复杂项目 | Django 项目 |

---

### 💡 本章深度讲解

SQLAlchemy 灵活强大，Django ORM 简单。选哪个看项目。

### 📝 本章精简总结

- SQLAlchemy 灵活。
- Django 简单。

### 🎯 梯度练习题

**基础题（⭐）**
1. 两者区别？
2. 怎么选？

**进阶题（⭐⭐）**
1. SQLAlchemy 优势？
2. 迁移？

**实战题（⭐⭐⭐）**
- 评估你的项目该用哪个。

---

### 七十一、总结

本文 71 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 七十二、生产部署

### 72.1 Docker 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 72.2 环境变量

```python
# 示例 72.2.1：配置
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:pass@localhost/db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_RECYCLE: int = 1800

settings = Settings()
```

### 72.3 连接池配置

```python
# 示例 72.3.1：生产配置
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
)
```

---

### 💡 本章深度讲解

生产部署：Docker、环境变量、连接池配置。

### 📝 本章精简总结

- Docker。
- pydantic-settings。
- 连接池配置。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么部署？
2. 环境变量？

**进阶题（⭐⭐）**
1. 连接池生产配置？
2. Docker？

**实战题（⭐⭐⭐）**
- Docker 化你的应用。

---

### 七十三、监控与日志

### 73.1 SQL 日志

```python
# 示例 73.1.1：SQL 日志
import logging

logging.basicConfig()
logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)  # 打印 SQL
```

### 73.2 慢查询日志

```python
# 示例 73.2.1：慢查询
@event.listens_for(engine, "before_cursor_execute")
def before_cursor(conn, cursor, statement, parameters, context, executemany):
    conn.info["query_start"] = time.perf_counter()

@event.listens_for(engine, "after_cursor_execute")
def after_cursor(conn, cursor, statement, parameters, context, executemany):
    elapsed = time.perf_counter() - conn.info["query_start"]
    if elapsed > 0.1:
        logger.warning("慢查询: %.2fs %s", elapsed, statement)
```

### 73.3 指标收集

```python
# 示例 73.3.1：Prometheus
query_count = Counter("db_queries_total", "查询总数")
query_duration = Histogram("db_query_duration_seconds", "查询耗时")

@event.listens_for(engine, "before_cursor_execute")
def track(conn, cursor, statement, parameters, context, executemany):
    query_count.inc()
    conn.info["start"] = time.perf_counter()

@event.listens_for(engine, "after_cursor_execute")
def track_done(conn, cursor, statement, parameters, context, executemany):
    elapsed = time.perf_counter() - conn.info["start"]
    query_duration.observe(elapsed)
```

---

### 💡 本章深度讲解

监控：SQL 日志、慢查询、Prometheus 指标。

### 📝 本章精简总结

- SQL 日志。
- 慢查询检测。
- Prometheus 指标。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么打印 SQL？
2. 慢查询？

**进阶题（⭐⭐）**
1. 怎么收集指标？
2. 怎么告警？

**实战题（⭐⭐⭐）**
- 添加 SQL 日志和慢查询检测。

---

### 七十四、安全

### 74.1 SQL 注入防护

```python
# 示例 74.1.1：参数化查询
# ✅ 安全
stmt = select(User).where(User.name == name)
# ❌ 危险
# session.execute(text(f"SELECT * FROM users WHERE name = '{name}'"))
```

### 74.2 敏感字段加密

```python
# 示例 74.2.1：加密字段
from cryptography.fernet import Fernet

class EncryptedString(TypeDecorator):
    impl = String
    def process_bind_param(self, value, dialect):
        if value is not None:
            return fernet.encrypt(value.encode()).decode()
    def process_result_value(self, value, dialect):
        if value is not None:
            return fernet.decrypt(value.encode()).decode()
```

---

### 💡 本章深度讲解

安全：参数化查询防注入、加密敏感字段。

### 📝 本章精简总结

- 参数化查询。
- 加密字段。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么防注入？
2. 敏感字段？

**进阶题（⭐⭐）**
1. 怎么加密？
2. 参数化原理？

**实战题（⭐⭐⭐）**
- 加密用户手机号字段。

---

### 七十五、总结

本文 75 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 七十六、完整项目实战：电商后端

### 76.1 数据模型

```python
# 示例 76.1.1：电商模型
class Category(Base, TimestampMixin):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    products: Mapped[list["Product"]] = relationship(back_populates="category")

class Product(Base, TimestampMixin):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(default=0)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="products")

class Order(Base, TimestampMixin):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()
```

### 76.2 下单逻辑

```python
# 示例 76.2.1：下单事务
async def place_order(db: AsyncSession, user_id: int, items: list[dict]):
    async with db.begin():
        # 计算总价
        total = Decimal("0")
        for item in items:
            product = await db.get(Product, item["product_id"])
            if product.stock < item["quantity"]:
                raise ValueError(f"库存不足: {product.name}")
            total += product.price * item["quantity"]
            # 扣库存
            product.stock -= item["quantity"]

        order = Order(user_id=user_id, total=total, status="pending")
        db.add(order)
        await db.flush()

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                price=product.price,
            )
            db.add(order_item)

        return order
```

### 76.3 订单查询

```python
# 示例 76.3.1：订单查询
async def get_orders(db: AsyncSession, user_id: int):
    stmt = (
        select(Order)
        .options(selectinload(Order.items).joinedload(OrderItem.product))
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()
```

---

### 💡 本章深度讲解

电商后端实战：商品/订单/订单项模型，下单事务，订单查询。完整业务逻辑。

### 📝 本章精简总结

- 电商模型。
- 下单事务。
- selectinload 查订单。

### 🎯 梯度练习题

**基础题（⭐）**
1. 电商模型怎么设计？
2. 下单逻辑？

**进阶题（⭐⭐）**
1. 怎么保证库存不超卖？
2. 怎么查订单详情？

**实战题（⭐⭐⭐）**
- 实现完整电商下单流程。

---

### 七十七、完整项目实战：博客系统

### 77.1 模型

```python
# 示例 77.1.1：博客模型
class Post(Base, TimestampMixin):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(back_populates="post")
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tags, back_populates="posts")

class Comment(Base, TimestampMixin):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post: Mapped["Post"] = relationship(back_populates="comments")
```

### 77.2 查询文章

```python
# 示例 77.2.1：文章列表
async def list_posts(db: AsyncSession, tag: str = None):
    stmt = select(Post).options(
        selectinload(Post.tags),
        joinedload(Post.author),
    ).order_by(Post.created_at.desc())
    if tag:
        stmt = stmt.join(Post.tags).where(Tag.name == tag)
    result = await db.execute(stmt)
    return result.scalars().unique().all()
```

---

### 💡 本章深度讲解

博客系统：文章/评论/标签。多对多标签。

### 📝 本章精简总结

- 博客模型。
- 多对多标签。
- selectinload 查询。

### 🎯 梯度练习题

**基础题（⭐）**
1. 博客模型？
2. 多对多？

**进阶题（⭐⭐）**
1. 怎么按标签查？
2. 怎么优化？

**实战题（⭐⭐⭐）**
- 实现博客 CRUD。

---

### 七十八、总结

本文 78 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 七十九、SQLAlchemy 内部原理

### 79.1 元类机制

DeclarativeBase 使用元类（metaclass）在类定义时自动映射：

```python
# 示例 79.1.1：元类原理（简化）
# class User(Base):
#     __tablename__ = "users"
#     id: Mapped[int] = mapped_column(primary_key=True)
#
# 元类做了：
# 1. 读取 __tablename__
# 2. 收集 Mapped 注解和 mapped_column
# 3. 创建 Table 对象
# 4. 绑定到类
```

### 79.2 Instrumented 描述符

```python
# 示例 79.2.1：描述符
# User.name 不是普通属性，是 InstrumentedAttribute
# 它在 get/set 时：
# - get：从实例 __dict__ 或触发懒加载
# - set：记录变更，加入 Session 跟踪
```

### 79.3 Unit of Work 原理

```mermaid
graph TD
    A[commit] --> B[flush]
    B --> C[按依赖排序]
    C --> D[INSERT 新对象]
    D --> E[UPDATE 修改对象]
    E --> F[DELETE 删除对象]
    F --> G[COMMIT]
```

---

### 💡 本章深度讲解

SQLAlchemy 内部：元类映射 + Instrumented 描述符 + Unit of Work。理解这些才能深入调试。

### 📝 本章精简总结

- 元类自动映射。
- Instrumented 描述符。
- Unit of Work 排序。

### 🎯 梯度练习题

**基础题（⭐）**
1. 元类做什么？
2. Unit of Work？

**进阶题（⭐⭐）**
1. InstrumentedAttribute？
2. 为什么按依赖排序？

**实战题（⭐⭐⭐）**
- 读 SQLAlchemy 源码理解 flush。

---

### 八十、Session 状态机详解

### 80.1 对象状态

```python
# 示例 80.1.1：状态转换
from sqlalchemy import inspect

# transient：新对象，未 add
u = User(name="A")
assert inspect(u).transient

# pending：add 后未 flush
session.add(u)
assert inspect(u).pending

# persistent：flush 后
session.flush()
assert inspect(u).persistent

# deleted：delete 后
session.delete(u)
assert inspect(u).deleted

# detached：commit 后
session.commit()
session.expunge(u)
assert inspect(u).detached
```

### 80.2 Session 生命周期

```mermaid
stateDiagram-v2
    [*] --> New
    New --> Pending: add()
    Pending --> Persistent: flush/commit
    Persistent --> Deleted: delete()
    Deleted --> [*]: commit
    Persistent --> Detached: expunge/close
    Detached --> Persistent: add()
```

---

### 💡 本章深度讲解

Session 状态机：transient/pending/persistent/deleted/detached。理解状态才能调试。

### 📝 本章精简总结

- 5 种状态。
- 状态转换。

### 🎯 梯度练习题

**基础题（⭐）**
1. 对象有哪些状态？
2. transient？

**进阶题（⭐⭐）**
1. 状态怎么转换？
2. detached？

**实战题（⭐⭐⭐）**
- 追踪对象状态变化。

---

### 八十一、懒加载与急加载原理

### 81.1 懒加载原理

```python
# 示例 81.1.1：懒加载
author = session.get(Author, 1)
# 此时只查 authors 表
print(author.books)  # 此时才查 books 表
```

### 81.2 selectinload 原理

```python
# 示例 81.2.1：selectinload
# 1. SELECT * FROM authors WHERE id IN (1,2,...)
# 2. SELECT * FROM books WHERE author_id IN (1,2,...)
# 共 2 条 SQL
```

### 81.3 joinedload 原理

```python
# 示例 81.3.1：joinedload
# SELECT * FROM authors JOIN books ON ...
# 共 1 条 SQL
```

---

### 💡 本章深度讲解

懒加载默认。急加载预加载：selectinload 2 条 SQL，joinedload 1 条 JOIN。

### 📝 本章精简总结

- 懒加载默认。
- selectinload 2 条。
- joinedload 1 条。

### 🎯 梯度练习题

**基础题（⭐）**
1. 懒加载原理？
2. selectinload？

**进阶题（⭐⭐）**
1. joinedload？
2. 怎么选？

**实战题（⭐⭐⭐）**
- 用 EXPLAIN 对比两种加载策略。

---

### 八十二、事务隔离级别详解

### 82.1 四种隔离级别

| 级别 | 脏读 | 不可重复读 | 幻读 |
|---|---|---|---|
| READ UNCOMMITTED | 可能 | 可能 | 可能 |
| READ COMMITTED | 不可能 | 可能 | 可能 |
| REPEATABLE READ | 不可能 | 不可能 | 可能 |
| SERIALIZABLE | 不可能 | 不可能 | 不可能 |

### 82.2 隔离级别问题

- **脏读**：读到未提交数据。
- **不可重复读**：两次读结果不同。
- **幻读**：两次查询行数不同。

### 82.3 PostgreSQL 默认

PostgreSQL 默认 READ COMMITTED。MySQL InnoDB 默认 REPEATABLE READ。

---

### 💡 本章深度讲解

隔离级别控制并发一致性。越高越安全但越慢。默认够用。

### 📝 本章精简总结

- 4 个级别。
- 脏读/不可重复读/幻读。
- 默认 READ COMMITTED。

### 🎯 梯度练习题

**基础题（⭐）**
1. 隔离级别？
2. 脏读？

**进阶题（⭐⭐）**
1. 不可重复读？
2. 怎么选？

**实战题（⭐⭐⭐）**
- 测试不同隔离级别行为。

---

### 八十三、总结

本文 83 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 八十四、SQLAlchemy 2.0 迁移指南

### 84.1 1.x → 2.0 对照

| 1.x | 2.0 |
|---|---|
| declarative_base() | DeclarativeBase |
| Column(String) | mapped_column(Mapped[str]) |
| session.query(User) | select(User) + session.execute() |
| session.query(User).get(1) | session.get(User, 1) |
| session.query(User).filter(...) | select(User).where(...) |
| .first() | .scalars().first() |
| .all() | .scalars().all() |

### 84.2 迁移步骤

1. 升级 SQLAlchemy 2.0
2. 改基类为 DeclarativeBase
3. 改 Column 为 mapped_column + Mapped
4. 改 query() 为 select()
5. 测试
6. 上线

---

### 💡 本章深度讲解

2.0 迁移：基类/列/查询三处改动。

### 📝 本章精简总结

- DeclarativeBase。
- Mapped + mapped_column。
- select()。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么迁移？
2. 主要改动？

**进阶题（⭐⭐）**
1. 怎么兼容？
2. 迁移风险？

**实战题（⭐⭐⭐）**
- 迁移你的项目到 2.0。

---

### 八十五、异步 SQLAlchemy 深度

### 85.1 异步 vs 同步

```python
# 同步
with Session(engine) as session:
    user = session.get(User, 1)

# 异步
async with async_session() as session:
    user = await session.get(User, 1)
```

### 85.2 异步限制

- 不能懒加载（必须急加载）
- 所有操作 await
- 不能用同步 Session

---

### 💡 本章深度讲解

异步 SQLAlchemy：create_async_engine + async_session。不能懒加载。

### 📝 本章精简总结

- create_async_engine。
- async_session。
- 不能懒加载。

### 🎯 梯度练习题

**基础题（⭐）**
1. 异步怎么用？
2. 限制？

**进阶题（⭐⭐）**
1. 为什么不能懒加载？
2. 怎么解决？

**实战题（⭐⭐⭐）**
- 把同步 CRUD 改为异步。

---

### 八十六、性能优化清单

### 86.1 优化清单

```python
# 优化清单：
# 1. selectinload 防 N+1
# 2. 批量操作 bulk_insert_mappings
# 3. yield_per 流式
# 4. 索引
# 5. 连接池调优
# 6. expire_on_commit=False
# 7. 只查需要的列
# 8. keyset pagination 替代 offset
```

### 86.2 keyset pagination

```python
# 示例 86.2.1：keyset pagination
# 不用 offset：
# SELECT * FROM users WHERE id > last_id ORDER BY id LIMIT 20
stmt = select(User).where(User.id > last_id).order_by(User.id).limit(20)
```

---

### 💡 本章深度讲解

性能优化：N+1/批量/流式/索引/keyset。

### 📝 本章精简总结

- selectinload。
- bulk_insert。
- yield_per。
- keyset pagination。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么优化？
2. keyset？

**进阶题（⭐⭐）**
1. 为什么 keyset 比 offset 快？
2. 怎么只查需要的列？

**实战题（⭐⭐⭐）**
- 优化你的慢查询。

---

### 八十七、总结

本文 87 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 八十八、完整 CRUD 服务层

### 88.1 基类服务

```python
# 示例 88.1.1：通用 CRUD 基类
from typing import Generic, TypeVar, Type
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        return await db.get(self.model, id)

    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj = self.model(**obj_in.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(self, db: AsyncSession, id: int, obj_in: UpdateSchemaType) -> ModelType | None:
        obj = await self.get(db, id)
        if not obj:
            return None
        for k, v in obj_in.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, id: int) -> bool:
        obj = await self.get(db, id)
        if not obj:
            return False
        await db.delete(obj)
        await db.commit()
        return True
```

### 88.2 具体服务

```python
# 示例 88.2.1：用户服务
class UserCreate(BaseModel):
    email: str
    name: str

class UserUpdate(BaseModel):
    name: str | None = None

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

user_crud = CRUDUser(User)
```

---

### 💡 本章深度讲解

通用 CRUD 基类 + 具体服务。泛型复用。

### 📝 本章精简总结

- CRUDBase 泛型基类。
- 具体服务继承。

### 🎯 梯度练习题

**基础题（⭐）**
1. CRUD 基类？
2. 泛型？

**进阶题（⭐⭐）**
1. 怎么复用？
2. 怎么扩展？

**实战题（⭐⭐⭐）**
- 写通用 CRUD 基类。

---

### 八十九、数据库迁移实战

### 89.1 自动生成迁移

```bash
# 生成迁移
alembic revision --autogenerate -m "add users table"

# 执行
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 89.2 数据迁移

```python
# 示例 89.2.1：数据迁移
def upgrade():
    op.add_column("users", Column("full_name", String(100)))
    conn = op.get_bind()
    conn.execute(
        text("UPDATE users SET full_name = first_name || ' ' || last_name")
    )
```

---

### 💡 本章深度讲解

Alembic 迁移：自动生成 + 数据迁移。

### 📝 本章精简总结

- autogenerate。
- upgrade/downgrade。
- 数据迁移。

### 🎯 梯度练习题

**基础题（⭐）**
1. Alembic？
2. 怎么回滚？

**进阶题（⭐⭐）**
1. 数据迁移？
2. 冲突解决？

**实战题（⭐⭐⭐）**
- 用 Alembic 管理表结构。

---

### 九十、总结

本文 90 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 九十一、完整项目实战：任务管理系统

### 91.1 数据模型

```python
# 示例 91.1.1：任务模型
class Task(Base, TimestampMixin):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="todo")
    priority: Mapped[int] = mapped_column(default=1)
    due_date: Mapped[datetime | None]
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="tasks")
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    assignee: Mapped["User | None"] = relationship(foreign_keys=[assignee_id])

class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tasks: Mapped[list["Task"]] = relationship(back_populates="project")
```

### 91.2 查询任务

```python
# 示例 91.2.1：查询
async def list_project_tasks(db: AsyncSession, project_id: int):
    stmt = (
        select(Task)
        .options(joinedload(Task.assignee))
        .where(Task.project_id == project_id)
        .order_by(Task.priority.desc(), Task.due_date)
    )
    result = await db.execute(stmt)
    return result.scalars().unique().all()
```

---

### 💡 本章深度讲解

任务管理：项目/任务/指派人。

### 📝 本章精简总结

- 任务模型。
- 查询优化。

### 🎯 梯度练习题

**基础题（⭐）**
1. 任务模型？
2. 怎么查？

**进阶题（⭐⭐）**
1. 多关系查询？
2. 怎么排序？

**实战题（⭐⭐⭐）**
- 实现任务 CRUD。

---

### 九十二、完整项目实战：SaaS 多租户

### 92.1 多租户模型

```python
# 示例 92.1.1：多租户
class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    domain: Mapped[str] = mapped_column(unique=True)

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    email: Mapped[str]
    name: Mapped[str]
```

### 92.2 租户隔离

```python
# 示例 92.2.1：租户隔离查询
async def list_users(db: AsyncSession, tenant_id: int):
    stmt = select(User).where(User.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalars().all()
```

---

### 💡 本章深度讲解

多租户：所有表带 tenant_id，查询自动过滤。

### 📝 本章精简总结

- tenant_id 隔离。
- 查询过滤。

### 🎯 梯度练习题

**基础题（⭐）**
1. 多租户？
2. 怎么隔离？

**进阶题（⭐⭐）**
1. 行级安全？
2. 怎么自动过滤？

**实战题（⭐⭐⭐）**
- 实现多租户数据隔离。

---

### 九十三、总结

本文 93 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 九十四、SQLAlchemy 常见面试题

### 94.1 20 道高频面试题

**Q1：ORM 是什么？**
对象关系映射，Python 类→数据库表。

**Q2：Session 作用？**
工作单元，管理对象生命周期、跟踪变更、Identity Map。

**Q3：Identity Map？**
同主键同对象实例。

**Q4：Unit of Work？**
commit 按依赖顺序执行 SQL。

**Q5：N+1 问题？**
查主表 N 条，每条查关联，共 1+N 条 SQL。

**Q6：selectinload vs joinedload？**
selectinload 2 条 SQL（一对多），joinedload 1 条 JOIN（一对一）。

**Q7：Session 线程安全？**
不安全，每请求一个。

**Q8：flush vs commit？**
flush 发到 DB 未提交，commit 提交。

**Q9：cascade？**
级联操作。

**Q10：事务隔离级别？**
READ UNCOMMITTED/READ COMMITTED/REPEATABLE READ/SERIALIZABLE。

**Q11：连接池参数？**
pool_size/max_overflow/pool_pre_ping/pool_recycle。

**Q12：异步怎么用？**
create_async_engine + async_session。

**Q13：懒加载问题？**
异步中不能懒加载，必须急加载。

**Q14：批量操作？**
bulk_insert_mappings/update/delete。

**Q15：索引？**
index=True/复合索引。

**Q16：子查询？**
subquery()。

**Q17：事件监听？**
@event.listens_for。

**Q18：混合属性？**
@hybrid_property。

**Q19：2.0 新特性？**
DeclarativeBase/Mapped/select()。

**Q20：怎么防 SQL 注入？**
参数化查询。

---

### 💡 本章深度讲解

20 道高频面试题。

### 📝 本章精简总结

- 20 道题。

### 🎯 梯度练习题

**基础题（⭐）**
1. Session？
2. N+1？

**进阶题（⭐⭐）**
1. Identity Map？
2. Unit of Work？

**实战题（⭐⭐⭐）**
- 回答所有面试题。

---

### 九十五、SQLAlchemy 速查表

```python
# ===== Engine =====
create_engine(url, pool_size=10, max_overflow=20, pool_pre_ping=True)
create_async_engine(url)

# ===== Session =====
Session(engine)
async_session()
sessionmaker(bind=engine)
async_sessionmaker(bind=engine)

# ===== 查询 =====
select(Model)
select(Model).where(Model.col == value)
select(Model).order_by(Model.col.desc())
select(Model).offset(0).limit(10)
select(func.count(Model.id))
select(Model).group_by(Model.col)
select(Model).join(Related)

# ===== 急加载 =====
selectinload(Model.rel)
joinedload(Model.rel)

# ===== CRUD =====
session.add(obj)
session.commit()
session.rollback()
session.get(Model, pk)
session.delete(obj)
session.execute(stmt)

# ===== 异步 =====
await session.execute(stmt)
await session.commit()
await session.rollback()
await session.get(Model, pk)
await session.delete(obj)
```

---

### 💡 本章深度讲解

速查表日常查阅。

### 📝 本章精简总结

- Engine/Session/查询/CRUD/异步。

### 🎯 梯度练习题

**基础题（⭐）**
1. select 怎么写？
2. commit？

**进阶题（⭐⭐）**
1. 急加载？
2. 异步？

**实战题（⭐⭐⭐）**
- 收藏速查表。

---

### 九十六、总结

本文 96 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 九十七、数据库设计最佳实践

### 97.1 表设计原则

```python
# 原则：
# 1. 每个表有主键
# 2. 字段命名 snake_case
# 3. 时间戳字段
# 4. 软删除
# 5. 索引常用查询字段
# 6. 外键关系清晰
# 7. 避免 SELECT *
```

### 97.2 索引策略

```python
# 示例 97.2.1：索引策略
# 高频 WHERE 字段建索引
# 复合索引最左前缀
# 避免过度索引（写性能）
# EXPLAIN 验证
```

### 97.3 数据类型选择

| 场景 | 类型 |
|---|---|
| 短字符串 | String(n) |
| 长文本 | Text |
| 整数 | Integer |
| 金额 | Numeric(10,2) |
| 布尔 | Boolean |
| 时间 | DateTime |
| JSON | JSON/JSONB |

---

### 💡 本章深度讲解

数据库设计：主键/命名/时间戳/索引/类型。

### 📝 本章精简总结

- 表设计原则。
- 索引策略。
- 类型选择。

### 🎯 梯度练习题

**基础题（⭐）**
1. 表设计原则？
2. 金额用什么类型？

**进阶题（⭐⭐）**
1. 索引策略？
2. 复合索引？

**实战题（⭐⭐⭐）**
- 审查你的表设计。

---

### 九十八、SQLAlchemy 与缓存

### 98.1 缓存策略

```python
# 示例 98.1.1：ORM 结果缓存
import json

async def get_user_cached(db: AsyncSession, user_id: int):
    key = f"user:{user_id}"
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)
    user = await db.get(User, user_id)
    if user:
        await redis.setex(key, 300, json.dumps({"id": user.id, "name": user.name}))
    return user
```

### 98.2 缓存失效

```python
# 示例 98.2.1：更新时失效缓存
@event.listens_for(User, "after_update")
def invalidate_cache(mapper, conn, target):
    asyncio.create_task(redis.delete(f"user:{target.id}"))
```

---

### 💡 本章深度讲解

ORM + 缓存：读缓存→miss→查库→写缓存。更新时失效。

### 📝 本章精简总结

- 缓存 aside。
- 更新失效。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么缓存 ORM 结果？
2. 缓存失效？

**进阶题（⭐⭐）**
1. 缓存穿透？
2. 缓存一致性？

**实战题（⭐⭐⭐）**
- 为 ORM 层加缓存。

---

### 九十九、总结

本文 99 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百、SQLAlchemy 学习路径

### 100.1 学习阶段

```mermaid
graph LR
    A[Python基础] --> B[SQL基础]
    B --> C[SQLAlchemy Core]
    C --> D[Declarative模型]
    D --> E[关系映射]
    E --> F[查询API]
    F --> G[事务]
    G --> H[性能优化]
    H --> I[异步]
    I --> J[FastAPI集成]
```

### 100.2 推荐顺序

1. **第一周**：SQL 基础 + SQLAlchemy Core
2. **第二周**：Declarative 模型 + 关系
3. **第三周**：查询 API + 事务
4. **第四周**：性能优化 + N+1
5. **第五周**：异步 SQLAlchemy
6. **第六周**：FastAPI 集成 + 实战

---

### 💡 本章深度讲解

学习路径：SQL → Core → ORM → 关系 → 查询 → 事务 → 性能 → 异步 → FastAPI。

### 📝 本章精简总结

- 6 周学习路径。

### 🎯 梯度练习题

**基础题（⭐）**
1. 第一步？
2. 哪个阶段最难？

**进阶题（⭐⭐）**
1. 为什么先学 SQL？
2. 怎么衡量进度？

**实战题（⭐⭐⭐）**
- 规划你的 SQLAlchemy 学习计划。

---

### 一百零一、SQLAlchemy FAQ

### 101.1 高频问题

**Q1：SQLAlchemy 和 Django ORM 哪个好？**
SQLAlchemy 灵活强大，Django ORM 简单。选哪个看项目。

**Q2：什么时候用 Core 什么时候用 ORM？**
CRUD 用 ORM，复杂报表用 Core。

**Q3：Session 为什么不是线程安全？**
内部状态（Identity Map）非线程安全。每线程一个。

**Q4：N+1 怎么检测？**
echo=True 看 SQL 条数。

**Q5：异步能懒加载吗？**
不能。必须急加载。

**Q6：怎么优化慢查询？**
EXPLAIN → 索引 → 避免 N+1。

**Q7：连接池耗尽怎么办？**
检查泄漏 → 调大 pool_size。

**Q8：怎么迁移到 2.0？**
DeclarativeBase + Mapped + select()。

---

### 💡 本章深度讲解

FAQ 覆盖常见疑问。

### 📝 本章精简总结

- 8 个 FAQ。

### 🎯 梯度练习题

**基础题（⭐）**
1. Session 线程安全？
2. N+1？

**进阶题（⭐⭐）**
1. 异步能懒加载？
2. 怎么迁移？

**实战题（⭐⭐⭐）**
- 回答所有 FAQ。

---

### 一百零二、总结

本文 102 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百零三、完整项目实战：CMS 内容管理系统

### 103.1 模型

```python
# 示例 103.1.1：CMS 模型
class Page(Base, TimestampMixin):
    __tablename__ = "pages"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    template: Mapped[str | None]
    is_published: Mapped[bool] = mapped_column(default=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

class Menu(Base, TimestampMixin):
    __tablename__ = "menus"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    items: Mapped[list["MenuItem"]] = relationship(back_populates="menu")

class MenuItem(Base):
    __tablename__ = "menu_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.id"))
    label: Mapped[str]
    url: Mapped[str]
    order: Mapped[int] = mapped_column(default=0)
    menu: Mapped["Menu"] = relationship(back_populates="items")
```

### 103.2 查询页面

```python
# 示例 103.2.1：按 slug 查
async def get_page(db: AsyncSession, slug: str):
    stmt = select(Page).where(Page.slug == slug, Page.is_published == True)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
```

---

### 💡 本章深度讲解

CMS：页面/菜单。

### 📝 本章精简总结

- CMS 模型。
- slug 查询。

### 🎯 梯度练习题

**基础题（⭐）**
1. CMS 模型？
2. slug？

**进阶题（⭐⭐）**
1. 菜单树？
2. 怎么查询？

**实战题（⭐⭐⭐）**
- 实现 CMS CRUD。

---

### 一百零四、完整项目实战：CRM 客户关系

### 104.1 模型

```python
# 示例 104.1.1：CRM 模型
class Customer(Base, TimestampMixin):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[str | None]
    company: Mapped[str | None]
    notes: Mapped[str | None] = mapped_column(Text)
    deals: Mapped[list["Deal"]] = relationship(back_populates="customer")

class Deal(Base, TimestampMixin):
    __tablename__ = "deals"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    title: Mapped[str]
    value: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    stage: Mapped[str] = mapped_column(String(20), default="lead")
    customer: Mapped["Customer"] = relationship(back_populates="deals")
```

### 104.2 销售漏斗

```python
# 示例 104.2.1：销售漏斗
async def sales_funnel(db: AsyncSession):
    stmt = (
        select(Deal.stage, func.count(Deal.id), func.sum(Deal.value))
        .group_by(Deal.stage)
    )
    result = await db.execute(stmt)
    return result.all()
```

---

### 💡 本章深度讲解

CRM：客户/商机。销售漏斗统计。

### 📝 本章精简总结

- CRM 模型。
- 销售漏斗。

### 🎯 梯度练习题

**基础题（⭐）**
1. CRM 模型？
2. 销售漏斗？

**进阶题（⭐⭐）**
1. 怎么统计？
2. 怎么优化？

**实战题（⭐⭐⭐）**
- 实现 CRM 模块。

---

### 一百零五、总结

本文 105 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百零六、SQLAlchemy 与 Type Hints

### 106.1 Mapped 类型

```python
# 示例 106.1.1：Mapped 类型
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int | None] = mapped_column(nullable=True)
    bio: Mapped[str | None]
```

### 106.2 mypy 检查

```bash
# pip install mypy
# mypy --strict main.py
```

---

### 💡 本章深度讲解

Mapped 类型让 mypy 检查 ORM 模型。

### 📝 本章精简总结

- Mapped[type]。
- mypy 检查。

### 🎯 梯度练习题

**基础题（⭐）**
1. Mapped？
2. 怎么检查？

**进阶题（⭐⭐）**
1. 可选字段？
2. mypy 配置？

**实战题（⭐⭐⭐）**
- 为你的模型加类型注解。

---

### 一百零七、SQLAlchemy 与 Pydantic

### 107.1 转换

```python
# 示例 107.1.1：ORM → Pydantic
from pydantic import BaseModel, ConfigDict

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

# ORM → Pydantic
user = User(id=1, name="A", email="a@b.com")
user_out = UserOut.model_validate(user)
```

### 107.2 Pydantic → ORM

```python
# 示例 107.2.1：Pydantic → ORM
class UserCreate(BaseModel):
    name: str
    email: str

user_create = UserCreate(name="A", email="a@b.com")
user = User(**user_create.model_dump())
```

---

### 💡 本章深度讲解

Pydantic 和 ORM 互转。from_attributes=True。

### 📝 本章精简总结

- from_attributes。
- model_dump。

### 🎯 梯度练习题

**基础题（⭐）**
1. ORM → Pydantic？
2. from_attributes？

**进阶题（⭐⭐）**
1. Pydantic → ORM？
2. 嵌套转换？

**实战题（⭐⭐⭐）**
- 写完整 Pydantic schema。

---

### 一百零八、总结

本文 108 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百零九、SQLAlchemy 与 Redis 缓存

### 109.1 缓存层

```python
# 示例 109.1.1：ORM 缓存层
import json

class CachedRepository:
    def __init__(self, db, redis, ttl=300):
        self.db = db
        self.redis = redis
        self.ttl = ttl

    async def get_user(self, user_id: int):
        key = f"user:{user_id}"
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        user = await self.db.get(User, user_id)
        if user:
            await self.redis.setex(key, self.ttl, json.dumps({"id": user.id, "name": user.name}))
        return user
```

### 109.2 缓存失效

```python
# 示例 109.2.1：更新时失效
async def update_user(self, user_id: int, **kwargs):
    user = await self.db.get(User, user_id)
    for k, v in kwargs.items():
        setattr(user, k, v)
    await self.db.commit()
    await self.redis.delete(f"user:{user_id}")
    return user
```

---

### 💡 本章深度讲解

ORM + Redis 缓存：读穿透、写失效。

### 📝 本章精简总结

- aside 缓存。
- 写失效。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么缓存？
2. 怎么失效？

**进阶题（⭐⭐）**
1. 缓存穿透？
2. 缓存一致性？

**实战题（⭐⭐⭐）**
- 为 ORM 加缓存层。

---

### 一百一十、SQLAlchemy 与消息队列

### 110.1 事件发布

```python
# 示例 110.1.1：ORM 事件 → MQ
@event.listens_for(User, "after_insert")
def publish_user_created(mapper, conn, target):
    asyncio.create_task(
        redis.publish("user_events", json.dumps({"type": "created", "id": target.id}))
    )
```

---

### 💡 本章深度讲解

ORM 事件发布到消息队列。

### 📝 本章精简总结

- after_insert 发布。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么发布事件？
2. after_insert？

**进阶题（⭐⭐）**
1. 事件驱动？
2. 怎么消费？

**实战题（⭐⭐⭐）**
- 实现 ORM 事件发布。

---

### 一百一十一、总结

本文 111 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百一十二、SQLAlchemy 日志系统

### 112.1 SQL 日志

```python
# 示例 112.1.1：SQL 日志
import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
```

### 112.2 慢查询日志

```python
# 示例 112.2.1：慢查询
@event.listens_for(engine, "before_cursor_execute")
def before(conn, cursor, statement, parameters, context, executemany):
    conn.info["start"] = time.perf_counter()

@event.listens_for(engine, "after_cursor_execute")
def after(conn, cursor, statement, parameters, context, executemany):
    elapsed = time.perf_counter() - conn.info["start"]
    if elapsed > 0.1:
        logger.warning("慢查询: %.2fs %s", elapsed, statement)
```

### 112.3 连接池日志

```python
# 示例 112.3.1：连接池日志
logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)
```

---

### 💡 本章深度讲解

日志：SQL/慢查询/连接池。

### 📝 本章精简总结

- SQL 日志。
- 慢查询。
- 连接池日志。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么打印 SQL？
2. 慢查询？

**进阶题（⭐⭐）**
1. 怎么告警？
2. 日志级别？

**实战题（⭐⭐⭐）**
- 添加 SQL 日志和慢查询检测。

---

### 一百一十三、SQLAlchemy 监控

### 113.1 Prometheus 指标

```python
# 示例 113.1.1：指标
from prometheus_client import Counter, Histogram

db_queries = Counter("db_queries_total", "查询总数")
db_duration = Histogram("db_duration_seconds", "查询耗时")
db_connections = Gauge("db_connections", "连接数")

@event.listens_for(engine, "before_cursor_execute")
def track(conn, cursor, statement, parameters, context, executemany):
    db_queries.inc()
    conn.info["start"] = time.perf_counter()

@event.listens_for(engine, "after_cursor_execute")
def track_done(conn, cursor, statement, parameters, context, executemany):
    db_duration.observe(time.perf_counter() - conn.info["start"])
```

---

### 💡 本章深度讲解

监控：Prometheus 指标。

### 📝 本章精简总结

- 查询计数。
- 耗时。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么监控？
2. 关键指标？

**进阶题（⭐⭐）**
1. Prometheus？
2. 告警？

**实战题（⭐⭐⭐）**
- 添加 Prometheus 指标。

---

### 一百一十四、总结

本文 114 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百一十五、SQLAlchemy 测试策略

### 115.1 测试数据库

```python
# 示例 115.1.1：测试 fixture
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session = async_sessionmaker(engine, expire_on_commit=False)
    yield session
    await engine.dispose()
```

### 115.2 测试 CRUD

```python
# 示例 115.2.2：测试
@pytest.mark.asyncio
async def test_create_user(test_db):
    async with test_db() as session:
        user = User(name="A", email="a@b.com")
        session.add(user)
        await session.commit()
        assert user.id is not None
```

---

### 💡 本章深度讲解

测试：内存数据库 + CRUD 测试。

### 📝 本章精简总结

- 内存 fixture。
- CRUD 测试。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么测试？
2. 内存数据库？

**进阶题（⭐⭐）**
1. fixture？
2. 事务回滚？

**实战题（⭐⭐⭐）**
- 为 CRUD 写测试。

---

### 一百一十六、SQLAlchemy 部署

### 116.1 Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### 116.2 环境变量

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
```

---

### 💡 本章深度讲解

部署：Docker + 环境变量。

### 📝 本章精简总结

- Docker。
- pydantic-settings。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么部署？
2. 环境变量？

**进阶题（⭐⭐）**
1. 生产配置？
2. Docker？

**实战题（⭐⭐⭐）**
- Docker 化应用。

---

### 一百一十七、总结

本文 117 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百一十八、SQLAlchemy 安全

### 118.1 SQL 注入防护

```python
# ✅ 参数化查询
stmt = select(User).where(User.name == name)
# ❌ 危险
# text(f"SELECT * FROM users WHERE name = '{name}'")
```

### 118.2 敏感数据加密

```python
# 示例 118.2.1：加密字段
class EncryptedString(TypeDecorator):
    impl = String
    def process_bind_param(self, value, dialect):
        return fernet.encrypt(value.encode()).decode() if value else None
    def process_result_value(self, value, dialect):
        return fernet.decrypt(value.encode()).decode() if value else None
```

---

### 💡 本章深度讲解

安全：参数化查询、加密字段。

### 📝 本章精简总结

- 参数化。
- 加密。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么防注入？
2. 加密字段？

**进阶题（⭐⭐）**
1. 怎么加密？
2. 参数化原理？

**实战题（⭐⭐⭐）**
- 加密敏感字段。

---

### 一百一十九、SQLAlchemy 性能基准

### 119.1 基准测试

```python
# 示例 119.1.1：基准
import time

def benchmark(n=1000):
    t0 = time.perf_counter()
    for _ in range(n):
        session.execute(select(User).limit(10)).scalars().all()
    print(f"{n} 次: {time.perf_counter()-t0:.2f}s")
```

### 119.2 优化对比

| 优化 | 提升 |
|---|---|
| selectinload | 10x |
| 批量插入 | 100x |
| keyset | 5x |

---

### 💡 本章深度讲解

基准测试优化效果。

### 📝 本章精简总结

- 基准脚本。
- 优化对比。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么测性能？
2. 瓶颈？

**进阶题（⭐⭐）**
1. 怎么优化？
2. 怎么定位？

**实战题（⭐⭐⭐）**
- 基准测试你的查询。

---

### 一百二十、总结

本文 120 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百二十一、SQLAlchemy 反模式

### 121.1 常见反模式

```python
# 反模式1：在视图层操作 Session
# ❌ 路由函数直接 session.query()
# ✅ 用 CRUD 层封装

# 反模式2：N+1
# ❌ 列表查关系
# ✅ selectinload

# 反模式3：每次新建 Session
# ❌ Session(engine) 到处建
# ✅ sessionmaker + 依赖注入

# 反模式4：忘记 commit
# ❌ add(user) 不 commit
# ✅ add + commit

# 反模式5：Session 跨线程
# ❌ 一个 Session 多线程
# ✅ 每线程一个
```

---

### 💡 本章深度讲解

反模式：视图层操作 Session、N+1、Session 管理不当。

### 📝 本章精简总结

- 5 大反模式。

### 🎯 梯度练习题

**基础题（⭐）**
1. 常见反模式？
2. N+1？

**进阶题（⭐⭐）**
1. 怎么分层？
2. 怎么避免？

**实战题（⭐⭐⭐）**
- 审查代码对照反模式。

---

### 一百二十二、SQLAlchemy 设计模式

### 122.1 Repository 模式

```python
# 示例 122.1.1：Repository
class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: int):
        return await self.db.get(User, user_id)

    async def list(self, skip=0, limit=100):
        stmt = select(User).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def save(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
```

### 122.2 Unit of Work 模式

```python
# 示例 122.2.2：Unit of Work
class UnitOfWork:
    def __init__(self):
        self.session = async_session()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
```

---

### 💡 本章深度讲解

设计模式：Repository 封装数据访问，Unit of Work 管理事务。

### 📝 本章精简总结

- Repository。
- Unit of Work。

### 🎯 梯度练习题

**基础题（⭐）**
1. Repository？
2. Unit of Work？

**进阶题（⭐⭐）**
1. 为什么分层？
2. 怎么实现？

**实战题（⭐⭐⭐）**
- 实现 Repository 模式。

---

### 一百二十三、总结

本文 123 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百二十四、SQLAlchemy 术语表

| 术语 | 英文 | 说明 |
|---|---|---|
| ORM | Object-Relational Mapping | 对象关系映射 |
| Engine | Engine | 数据库引擎 |
| Session | Session | 会话 |
| Identity Map | Identity Map | 身份映射 |
| Unit of Work | Unit of Work | 工作单元 |
| Declarative | Declarative | 声明式 |
| Relationship | relationship | 关系 |
| ForeignKey | ForeignKey | 外键 |
| N+1 | N+1 | N+1 查询问题 |
| Eager Load | Eager Loading | 急加载 |
| Lazy Load | Lazy Loading | 懒加载 |
| Cascade | Cascade | 级联 |
| Transaction | Transaction | 事务 |
| Connection Pool | Connection Pool | 连接池 |
| Migration | Migration | 迁移 |
| Query | Query | 查询 |
| Filter | Filter | 过滤 |
| Join | Join | 关联 |
| Index | Index | 索引 |
| Constraint | Constraint | 约束 |

---

### 💡 本章深度讲解

术语表帮助查阅。

### 📝 本章精简总结

- 20 个核心术语。

### 🎯 梯度练习题

**基础题（⭐）**
1. ORM？
2. Session？

**进阶题（⭐⭐）**
1. Identity Map？
2. Unit of Work？

**实战题（⭐⭐⭐）**
- 用术语表解释 SQLAlchemy。

---

### 一百二十五、SQLAlchemy 速查表

```python
# Engine
create_engine(url, pool_size=10, max_overflow=20)
create_async_engine(url)

# Session
Session(engine)
async_session()
sessionmaker(bind=engine)
async_sessionmaker(bind=engine)

# 查询
select(Model)
select(Model).where(Model.col == val)
select(Model).order_by(Model.col.desc())
select(Model).offset(0).limit(10)
select(func.count(Model.id))
select(Model).group_by(Model.col)
select(Model).join(Related)
selectinload(Model.rel)
joinedload(Model.rel)

# CRUD
session.add(obj)
session.commit()
session.rollback()
session.get(Model, pk)
session.delete(obj)
session.execute(stmt)

# 异步
await session.execute(stmt)
await session.commit()
await session.rollback()
await session.get(Model, pk)
```

---

### 💡 本章深度讲解

速查表日常查阅。

### 📝 本章精简总结

- Engine/Session/查询/CRUD/异步。

### 🎯 梯度练习题

**基础题（⭐）**
1. select？
2. commit？

**进阶题（⭐⭐）**
1. 急加载？
2. 异步？

**实战题（⭐⭐⭐）**
- 收藏速查表。

---

### 一百二十六、总结

本文 126 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百二十七、SQLAlchemy 与 FastAPI 完整集成

### 127.1 完整项目

```python
# 示例 127.1.1：main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# DB
async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session

# Model
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

# Schema
class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    model_config = ConfigDict(from_attributes=True)

# App
app = FastAPI()

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users/{uid}", response_model=UserResponse)
async def get_user(uid: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, uid)
    if not user:
        raise HTTPException(404)
    return user

@app.get("/users", response_model=list[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()
```

---

### 💡 本章深度讲解

FastAPI + SQLAlchemy 2.0 异步完整项目。

### 📝 本章精简总结

- 完整项目代码。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么集成？
2. get_db？

**进阶题（⭐⭐）**
1. Pydantic from_attributes？
2. 分页？

**实战题（⭐⭐⭐）**
- 搭建完整项目。

---

### 一百二十八、SQLAlchemy 常见错误排查

### 128.1 错误表

| 错误 | 原因 | 解决 |
|---|---|---|
| IntegrityError | 唯一冲突 | 检查数据 |
| OperationalError | 连接失败 | 检查 DB |
| ProgrammingError | 表不存在 | 迁移 |
| InvalidRequestError | Session 状态 | commit/rollback |
| StaleDataError | 数据已变 | 重新查询 |

---

### 💡 本章深度讲解

错误排查表。

### 📝 本章精简总结

- 5 种错误。

### 🎯 梯度练习题

**基础题（⭐）**
1. IntegrityError？
2. 怎么排查？

**进阶题（⭐⭐）**
1. StaleDataError？
2. 怎么调试？

**实战题（⭐⭐⭐）**
- 排查你的下一个错误。

---

### 一百二十九、总结

本文 129 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百三十、SQLAlchemy 与 Alembic 迁移

### 130.1 初始化

```bash
pip install alembic
alembic init alembic
```

### 130.2 配置

```python
# alembic.ini
sqlalchemy.url = postgresql://user:pass@localhost/db

# env.py
from models import Base
target_metadata = Base.metadata
```

### 130.3 迁移

```bash
alembic revision --autogenerate -m "add users"
alembic upgrade head
alembic downgrade -1
```

---

### 💡 本章深度讲解

Alembic 迁移工具。

### 📝 本章精简总结

- init/upgrade/downgrade。
- autogenerate。

### 🎯 梯度练习题

**基础题（⭐）**
1. Alembic？
2. 怎么迁移？

**进阶题（⭐⭐）**
1. 怎么回滚？
2. 数据迁移？

**实战题（⭐⭐⭐）**
- 用 Alembic 管理表。

---

### 一百三十一、SQLAlchemy 与 SQLModel

### 131.1 SQLModel 示例

```python
# 示例 131.1.1：SQLModel
from sqlmodel import SQLModel, Field, create_engine, Session

class Hero(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None
```

---

### 💡 本章深度讲解

SQLModel 统一 Pydantic + SQLAlchemy。

### 📝 本章精简总结

- SQLModel。

### 🎯 梯度练习题

**基础题（⭐）**
1. SQLModel？
2. 怎么用？

**进阶题（⭐⭐）**
1. 和 SQLAlchemy 区别？
2. 怎么选？

**实战题（⭐⭐⭐）**
- 用 SQLModel 重写模型。

---

### 一百三十二、总结

本文 132 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百三十三、SQLAlchemy 与 PostgreSQL 高级

### 133.1 JSONB

```python
# 示例 133.1.1：JSONB
from sqlalchemy.dialects.postgresql import JSONB

class Product(Base):
    data: Mapped[dict] = mapped_column(JSONB)
```

### 133.2 数组

```python
# 示例 133.2.1：ARRAY
from sqlalchemy.dialects.postgresql import ARRAY

class Post(Base):
    tags: Mapped[list[str]] = mapped_column(ARRAY(String))
```

### 133.3 全文搜索

```python
# 示例 133.3.1：全文搜索
stmt = select(Article).where(Article.body.match("python"))
```

---

### 💡 本章深度讲解

PostgreSQL 高级类型：JSONB/数组/全文搜索。

### 📝 本章精简总结

- JSONB。
- ARRAY。
- 全文搜索。

### 🎯 梯度练习题

**基础题（⭐）**
1. JSONB？
2. 数组？

**进阶题（⭐⭐）**
1. 怎么查 JSON？
2. 全文搜索？

**实战题（⭐⭐⭐）**
- 用 JSONB 存储产品规格。

---

### 一百三十四、SQLAlchemy 与 MySQL

### 134.1 MySQL 配置

```python
engine = create_engine("mysql+pymysql://user:pass@localhost/db")
```

### 134.2 MySQL 注意事项

- MySQL 8 小时断开 → pool_recycle
- 大小写敏感配置
- 字符集 utf8mb4

---

### 💡 本章深度讲解

MySQL 注意事项：pool_recycle/字符集。

### 📝 本章精简总结

- pymysql 驱动。
- pool_recycle。

### 🎯 梯度练习题

**基础题（⭐）**
1. MySQL 驱动？
2. pool_recycle？

**进阶题（⭐⭐）**
1. 字符集？
2. 和 PG 区别？

**实战题（⭐⭐⭐）**
- 配置 MySQL 连接。

---

### 一百三十五、总结

本文 135 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百三十六、SQLAlchemy 与 SQLite

### 136.1 SQLite 配置

```python
engine = create_engine("sqlite:///test.db")
async_engine = create_async_engine("sqlite+aiosqlite:///test.db")
```

### 136.2 SQLite 注意事项

- 单文件，无需服务器
- 写锁全局
- 适合开发/测试
- 不适合高并发写

---

### 💡 本章深度讲解

SQLite 适合开发测试，不适合生产高并发。

### 📝 本章精简总结

- sqlite:///test.db。
- 写锁全局。

### 🎯 梯度练习题

**基础题（⭐）**
1. SQLite 驱动？
2. 适合什么？

**进阶题（⭐⭐）**
1. 为什么不适合生产？
2. 并发限制？

**实战题（⭐⭐⭐）**
- 用 SQLite 做开发数据库。

---

### 一百三十七、SQLAlchemy 与数据仓库

### 137.1 分析查询

```python
# 示例 137.1.1：分析查询
stmt = (
    select(Product.category, func.sum(OrderItem.quantity), func.sum(OrderItem.price))
    .join(OrderItem).join(Product)
    .group_by(Product.category)
)
```

---

### 💡 本章深度讲解

数据仓库分析查询。

### 📝 本章精简总结

- 聚合分析。

### 🎯 梯度练习题

**基础题（⭐）**
1. 分析查询？
2. GROUP BY？

**进阶题（⭐⭐）**
1. 数据仓库？
2. 优化？

**实战题（⭐⭐⭐）**
- 写销售报表查询。

---

### 一百三十八、总结

本文 138 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百三十九、SQLAlchemy 与 GraphQL

### 139.1 SQLAlchemy + GraphQL

```python
# 示例 139.1.1：GraphQL 查询
# Strawberry + SQLAlchemy
import strawberry

@strawberry.type
class UserType:
    id: int
    name: str
    email: str

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, info, id: int) -> UserType | None:
        db = info.context["db"]
        user = await db.get(User, id)
        return UserType(id=user.id, name=user.name, email=user.email) if user else None
```

---

### 💡 本章深度讲解

GraphQL + SQLAlchemy：Strawberry 集成。

### 📝 本章精简总结

- Strawberry。

### 🎯 梯度练习题

**基础题（⭐）**
1. GraphQL？
2. 怎么集成？

**进阶题（⭐⭐）**
1. N+1 在 GraphQL？
2. 怎么优化？

**实战题（⭐⭐⭐）**
- 写 GraphQL API。

---

### 一百四十、SQLAlchemy 与 gRPC

### 140.1 gRPC 服务

```python
# 示例 140.1.1：gRPC + SQLAlchemy
class UserService(UserServiceServicer):
    async def GetUser(self, request, context):
        user = await db.get(User, request.id)
        return UserReply(id=user.id, name=user.name)
```

---

### 💡 本章深度讲解

gRPC + SQLAlchemy。

### 📝 本章精简总结

- gRPC 服务。

### 🎯 梯度练习题

**基础题（⭐）**
1. gRPC？
2. 怎么集成？

**进阶题（⭐⭐）**
1. 异步 gRPC？
2. 性能？

**实战题（⭐⭐⭐）**
- 写 gRPC 服务。

---

### 一百四十一、总结

本文 141 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百四十二、SQLAlchemy 与 Celery

### 142.1 Celery 任务

```python
# 示例 142.1.1：Celery + SQLAlchemy
from celery import Celery

celery = Celery("tasks", broker="redis://localhost")

@celery.task
def export_users():
    with Session(engine) as session:
        users = session.execute(select(User)).scalars().all()
        # 导出 CSV
        return len(users)
```

---

### 💡 本章深度讲解

Celery + SQLAlchemy：每任务一个 Session。

### 📝 本章精简总结

- Celery 任务。
- 每任务 Session。

### 🎯 梯度练习题

**基础题（⭐）**
1. Celery？
2. 怎么集成？

**进阶题（⭐⭐）**
1. Session 生命周期？
2. 事务？

**实战题（⭐⭐⭐）**
- 写 Celery 数据导出任务。

---

### 一百四十三、SQLAlchemy 与数据迁移

### 143.1 Alembic 流程

```bash
alembic revision --autogenerate -m "add column"
alembic upgrade head
alembic downgrade -1
```

---

### 💡 本章深度讲解

Alembic 迁移流程。

### 📝 本章精简总结

- autogenerate。
- upgrade/downgrade。

### 🎯 梯度练习题

**基础题（⭐）**
1. 迁移流程？
2. 怎么回滚？

**进阶题（⭐⭐）**
1. 数据迁移？
2. 冲突？

**实战题（⭐⭐⭐）**
- 写数据迁移脚本。

---

### 一百四十四、总结

本文 144 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百四十五、SQLAlchemy 学习资源

### 145.1 推荐资源

- 官方文档：docs.sqlalchemy.org
- 书：《SQLAlchemy 2.0 for Python》
- 视频：Corey Schafer SQLAlchemy 系列
- 源码：GitHub

---

### 💡 本章深度讲解

学习资源。

### 📝 本章精简总结

- 官方文档。
- 书。

### 🎯 梯度练习题

**基础题（⭐）**
1. 推荐书？
2. 官方文档？

**进阶题（⭐⭐）**
1. 怎么深入？
2. 读源码？

**实战题（⭐⭐⭐）**
- 读完一本 SQLAlchemy 书。

---

### 一百四十六、SQLAlchemy 常见问题

### 146.1 FAQ

**Q1：Session 用完要 close 吗？**
是。with Session() 自动 close。

**Q2：commit 后对象还能用吗？**
expire_on_commit=True 会重新查。设 False 可避免。

**Q3：怎么批量插入？**
bulk_insert_mappings。

**Q4：N+1 怎么解决？**
selectinload/joinedload。

**Q5：异步能懒加载吗？**
不能。必须急加载。

---

### 💡 本章深度讲解

FAQ。

### 📝 本章精简总结

- 5 个 FAQ。

### 🎯 梯度练习题

**基础题（⭐）**
1. close？
2. N+1？

**进阶题（⭐⭐）**
1. expire_on_commit？
2. 异步懒加载？

**实战题（⭐⭐⭐）**
- 回答所有 FAQ。

---

### 一百四十七、总结

本文 147 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百四十八、SQLAlchemy 与测试

### 148.1 测试最佳实践

```python
# 测试用 SQLite 内存数据库
# 每测试一个事务，测试后回滚
# fixture 复用 Session
```

---

### 💡 本章深度讲解

测试最佳实践。

### 📝 本章精简总结

- SQLite 内存。
- fixture。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么测试？
2. fixture？

**进阶题（⭐⭐）**
1. 事务回滚？
2. 数据隔离？

**实战题（⭐⭐⭐）**
- 写测试 fixture。

---

### 一百四十九、SQLAlchemy 与监控

### 149.1 监控指标

- 查询 QPS
- 查询延迟 p95
- 连接池使用率
- 慢查询数

---

### 💡 本章深度讲解

监控指标。

### 📝 本章精简总结

- QPS/延迟/连接池/慢查询。

### 🎯 梯度练习题

**基础题（⭐）**
1. 监控什么？
2. 慢查询？

**进阶题（⭐⭐）**
1. Prometheus？
2. 告警？

**实战题（⭐⭐⭐）**
- 添加监控指标。

---

### 一百五十、总结

本文 150 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百五十一、SQLAlchemy 与 Docker

### 151.1 Docker Compose

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    ports:
      - "5432:5432"
  app:
    build: .
    depends_on:
      - db
```

---

### 💡 本章深度讲解

Docker Compose 部署。

### 📝 本章精简总结

- docker-compose。

### 🎯 梯度练习题

**基础题（⭐）**
1. Docker？
2. Compose？

**进阶题（⭐⭐）**
1. 多服务？
2. 环境变量？

**实战题（⭐⭐⭐）**
- Docker Compose 部署。

---

### 一百五十二、SQLAlchemy 与 Kubernetes

### 152.1 K8s 部署

- 无状态应用
- DB 用云服务
- HPA 自动扩缩

---

### 💡 本章深度讲解

K8s 部署。

### 📝 本章精简总结

- 无状态。
- HPA。

### 🎯 梯度练习题

**基础题（⭐）**
1. K8s？
2. 无状态？

**进阶题（⭐⭐）**
1. HPA？
2. 配置？

**实战题（⭐⭐⭐）**
- K8s 部署应用。

---

### 一百五十三、总结

本文 153 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百五十四、SQLAlchemy 与 CI/CD

### 154.1 GitHub Actions

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: pytest
```

---

### 💡 本章深度讲解

CI/CD。

### 📝 本章精简总结

- GitHub Actions。

### 🎯 梯度练习题

**基础题（⭐）**
1. CI/CD？
2. GitHub Actions？

**进阶题（⭐⭐）**
1. 测试数据库？
2. 迁移？

**实战题（⭐⭐⭐）**
- 配置 CI/CD。

---

### 一百五十五、SQLAlchemy 与日志

### 155.1 结构化日志

```python
# 示例 155.1.1：SQL 日志
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
```

---

### 💡 本章深度讲解

SQL 日志。

### 📝 本章精简总结

- sqlalchemy.engine。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么打印 SQL？
2. 日志级别？

**进阶题（⭐⭐）**
1. 慢查询？
2. 结构化？

**实战题（⭐⭐⭐）**
- 配置 SQL 日志。

---

### 一百五十六、总结

本文 156 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百五十七、SQLAlchemy 与安全

### 157.1 安全清单

- 参数化查询防注入
- 敏感字段加密
- 最小权限 DB 用户
- 不记录敏感数据

---

### 💡 本章深度讲解

安全清单。

### 📝 本章精简总结

- 参数化/加密/最小权限。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么防注入？
2. 敏感数据？

**进阶题（⭐⭐）**
1. 怎么加密？
2. 最小权限？

**实战题（⭐⭐⭐）**
- 审查安全。

---

### 一百五十八、SQLAlchemy 与性能

### 158.1 性能清单

- selectinload 防 N+1
- 批量操作
- 索引
- 连接池
- expire_on_commit=False

---

### 💡 本章深度讲解

性能清单。

### 📝 本章精简总结

- N+1/批量/索引/连接池。

### 🎯 梯度练习题

**基础题（⭐）**
1. 怎么优化？
2. N+1？

**进阶题（⭐⭐）**
1. 怎么测？
2. 瓶颈？

**实战题（⭐⭐⭐）**
- 优化慢查询。

---

### 一百五十九、总结

本文 159 章覆盖了 SQLAlchemy 完整知识。

**三句话记住 SQLAlchemy**：
1. Engine 连接池 + Session 工作单元。
2. Identity Map 同主键同对象。
3. N+1 用 selectinload 解决。

---

> 💡 **全文终**：SQLAlchemy 是 Python 最强大 ORM。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百六十、最终总结

本文 160 章完整覆盖了 SQLAlchemy ORM 核心原理：

- **架构**：Engine 连接池 + Session 工作单元
- **模型**：DeclarativeBase + Mapped 类型注解
- **关系**：一对多/多对多/一对一
- **查询**：select() + where + join + group_by
- **事务**：commit/rollback + 隔离级别
- **性能**：N+1 用 selectinload + 批量操作
- **2.0**：DeclarativeBase + Mapped + select()
- **异步**：create_async_engine + async_session
- **FastAPI**：依赖注入 + CRUD
- **坑点**：30+ 常见错误
- **面试**：20+ 高频题

**三句话记住 SQLAlchemy**：
1. Engine 管理连接池，Session 管理对象生命周期。
2. Identity Map 保证同主键同对象。
3. N+1 问题用 selectinload/joinedload 解决。

---

> 💡 **全文真正终章**：160 章。SQLAlchemy 是 Python 最强大的 ORM。掌握它，你的数据层开发效率将提升一个数量级。从模型定义到生产部署，本文是完整的学习路径。Happy coding! 🚀

### 🔗 关联笔记

- [[Python-装饰器与上下文管理器]]
- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]
- [[Alembic-数据库迁移]]
- [[Redis-aioredis]]

### 📖 前置知识

- [[Python-面向对象与元类]]
- [[PostgreSQL-Python高级用法]]
- [[Python-异步编程asyncio]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库 #异步 #FastAPI #PostgreSQL

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]

### 一百六十一、附录：API 索引

### A.1 Engine

| API | 说明 |
|---|---|
| create_engine(url) | 创建同步 Engine |
| create_async_engine(url) | 创建异步 Engine |
| engine.connect() | 获取连接 |
| engine.begin() | 事务上下文 |

### A.2 Session

| API | 说明 |
|---|---|
| Session(engine) | 创建 Session |
| sessionmaker(bind=engine) | Session 工厂 |
| async_sessionmaker(bind=engine) | 异步 Session 工厂 |
| session.add(obj) | 添加 |
| session.commit() | 提交 |
| session.rollback() | 回滚 |
| session.close() | 关闭 |
| session.get(Model, pk) | 主键查询 |
| session.execute(stmt) | 执行查询 |
| session.flush() | 刷到数据库 |
| session.delete(obj) | 删除 |

### A.3 查询

| API | 说明 |
|---|---|
| select(Model) | 查询 |
| where(条件) | 过滤 |
| order_by(列) | 排序 |
| limit(n) | 限制 |
| offset(n) | 偏移 |
| group_by(列) | 分组 |
| join(关系) | 关联 |
| func.count(col) | 计数 |

### A.4 急加载

| API | 说明 |
|---|---|
| selectinload(rel) | IN 急加载 |
| joinedload(rel) | JOIN 急加载 |

---

> 💡 **真正的全文终**：161 章。SQLAlchemy 完整知识体系。🚀

### 🔗 关联笔记

- [[Python-异步编程asyncio]]
- [[FastAPI-路由与依赖注入]]
- [[PostgreSQL-Python高级用法]]

### 📖 前置知识

- [[Python-面向对象与元类]]

### 🏷️ 相关标签

#Python #ORM #SQLAlchemy #数据库

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
