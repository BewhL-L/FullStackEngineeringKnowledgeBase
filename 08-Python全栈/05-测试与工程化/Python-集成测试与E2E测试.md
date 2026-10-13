---
title: Python-集成测试与E2E测试
type: P1
tags: [Python, 测试, 集成测试, E2E, pytest, testcontainers, Playwright]
created: 2026-09-10
updated: 2026-09-10
---

# Python 集成测试与 E2E 测试完全指南

## 一、测试金字塔与测试策略

### 1.1 测试金字塔概念

测试金字塔（Test Pyramid）是 Mike Cohn 提出的测试分层模型，从下到上分为三层：

- **单元测试（Unit Tests）**：最底层，数量最多，测试单个函数/类
- **集成测试（Integration Tests）**：中间层，测试模块间交互
- **端到端测试（E2E Tests）**：最顶层，数量最少，测试完整流程

```
        /\
       /E2E\        ← 少量：慢、脆弱、维护成本高
      /------\
     /集成测试\      ← 适量：中等速度、覆盖模块交互
    /----------\
   /  单元测试  \    ← 大量：快、稳定、覆盖核心逻辑
  /--------------\
```

**核心原则**：
- 越底层，测试越多（快、稳定）
- 越顶层，测试越少（慢、脆弱）
- 不要"倒金字塔"：E2E 比单元测试还多

### 1.2 为什么需要集成测试

单元测试只验证单个组件逻辑，无法发现：
- 模块间接口不匹配
- 数据库连接失败
- API 响应格式错误
- 第三方服务集成问题

**集成测试的价值**：
- 验证组件真实协作
- 发现接口契约问题
- 验证数据库/缓存/消息队列集成
- 提供更高信心

```python
# 单元测试 vs 集成测试对比

# ❌ 单元测试：Mock 掉所有依赖
def test_calculate_price():
    service = PriceService(tax_calc=Mock())
    assert service.calculate(100) == 113  # Mock了税计算

# ✅ 集成测试：使用真实依赖
def test_calculate_price_integration(db_session):
    service = PriceService(tax_calc=TaxCalculator(), db=db_session)
    price = service.calculate(100)
    assert price == 113  # 真实计算+真实数据库验证
```

### 1.3 测试策略选择

| 测试类型 | 速度 | 稳定性 | 覆盖率 | 维护成本 |
|---------|------|--------|--------|----------|
| 单元测试 | 极快(<10ms) | 高 | 逻辑覆盖 | 低 |
| 集成测试 | 中(100ms-1s) | 中 | 模块交互 | 中 |
| E2E测试 | 慢(1-10s) | 低 | 业务流程 | 高 |

**实践建议**：
- 80% 单元测试 + 15% 集成测试 + 5% E2E 测试
- 核心业务逻辑：单元测试覆盖
- 关键用户流程：E2E 覆盖
- 模块接口：集成测试覆盖

```python
# 测试金字塔的实际比例
# 小项目（<1万行代码）：
# - 单元测试：100个
# - 集成测试：20个
# - E2E测试：5个
# 比例：80% / 16% / 4%

# 大项目（10万+行代码）：
# - 单元测试：1000个
# - 集成测试：150个
# - E2E测试：30个
# 比例：85% / 13% / 2%

# 核心逻辑用单元测试覆盖（快）
# 关键路径用E2E覆盖（信心）
# 模块接口用集成测试覆盖（平衡）
```

```python
# 测试金字塔的 Mermaid 图（描述版）
# graph TD
#   A[E2E测试 少量] --> B[集成测试 适量]
#   B --> C[单元测试 大量]
#   style A fill:#ff6b6b
#   style B fill:#ffd93d
#   style C fill:#6bcb77
```

```python
# 测试金字塔进阶：不同项目的测试策略

# 初创项目（快速迭代）
# - 单元测试：50%
# - 集成测试：30%
# - E2E测试：20%
# 原因：功能变化快，需要快速验证

# 成熟项目（稳定维护）
# - 单元测试：70%
# - 集成测试：20%
# - E2E测试：10%
# 原因：功能稳定，重点防回归

# 基础设施项目
# - 单元测试：60%
# - 集成测试：30%
# - E2E测试：10%
# 原因：依赖多，集成测试重要
```

```python
# 测试 ROI（投资回报率）分析
# | 测试类型    | 编写成本 | 维护成本 | 发现Bug价值 | ROI |
# |-------------|----------|----------|-------------|-----|
# | 单元测试    | 低       | 低       | 中          | 高  |
# | 集成测试    | 中       | 中       | 高          | 高  |
# | E2E测试     | 高       | 高       | 高          | 中  |
# | 手动测试    | 低       | 极高     | 高          | 低  |
# 结论：单元+集成测试ROI最高，E2E只覆盖关键路径
```

```python
# 测试金字塔的经典论文
# Mike Cohn《Succeeding with Agile》(2009)
# 原始模型：单元→服务→UI
# 现代演变：单元→集成→E2E

# 反模式：冰淇淋蛋筒（倒金字塔）
# E2E 多、集成少、单元少
# 问题：慢、脆弱、反馈慢

# 反模式：沙漏
# 单元多、集成少、E2E多
# 问题：集成层缺失，接口问题发现晚

# 最佳模型：金字塔
# 单元多、集成中、E2E少
# 快、稳、反馈及时
```

```python
# 测试金字塔的实际落地
# 项目初始化时：
# 1. 搭建测试框架（pytest + fixtures）
# 2. 写核心业务的单元测试
# 3. 写关键API的集成测试
# 4. 写2-3个E2E测试覆盖主流程

# 持续开发时：
# 1. 新功能先写单元测试
# 2. 集成测试跟着API走
# 3. E2E只覆盖新的关键路径
# 4. 修复Bug时写回归测试
```

```python
# 测试金字塔的量化指标
# 一个健康的测试套件：
# - 单元测试数：集成测试数 ≈ 5:1
# - 集成测试数：E2E测试数 ≈ 5:1
# - 测试通过率：100%
# - Flaky率：<1%
# - 本地运行时间：<5分钟
# - CI运行时间：<15分钟
```

```python
# 测试金字塔的常见误解
# 误解1：测试越多越好
# 正解：测试质量>测试数量，无意义的测试不如不写

# 误解2：E2E最重要
# 正解：E2E只覆盖关键路径，单元测试才是基础

# 误解3：覆盖率100%
# 正解：覆盖率是手段不是目的，80%+足够

# 误解4：TDD必须严格遵守
# 正解：TDD是工具，不是教条
```

```python
# 测试金字塔的实际应用案例
# 案例1：博客系统
# 单元测试：Markdown渲染、URL生成、权限检查
# 集成测试：文章CRUD、评论关联、标签搜索
# E2E：注册→写文章→发布→评论

# 案例2：电商系统
# 单元测试：价格计算、折扣逻辑、库存扣减
# 集成测试：下单流程、支付回调、库存联动
# E2E：浏览→加购→下单→支付

# 案例3：SaaS平台
# 单元测试：权限模型、计费逻辑、通知规则
# 集成测试：多租户隔离、API限流、Webhook
# E2E：注册→创建团队→邀请成员→使用功能
```

```python
# 面试题：如何设计测试策略？
# 答案要点：
# 1. 识别核心业务流程
# 2. 按测试金字塔分层
# 3. 选择工具（pytest/Testcontainers/Playwright）
# 4. 数据管理（工厂+事务）
# 5. CI/CD集成（分层执行）
# 6. 监控指标（覆盖率/flaky率）
```

```python
# 测试金字塔 ROI 分析
# 单元测试：投入1人天，发现10个Bug
# 集成测试：投入1人天，发现5个Bug
# E2E测试：投入1人天，发现2个Bug
# 结论：单元测试ROI最高，E2E只覆盖关键路径
```

```python
# 测试金字塔实际比例
# 1000个测试：
# 单元：800个（80%）
# 集成：150个（15%）
# E2E：50个（5%）
# 比例：16:3:1
```

```python
# 面试题：集成测试中如何处理数据库？
# 1. Testcontainers真实数据库
# 2. 事务回滚隔离
# 3. 工厂模式创建数据
# 4. 测试约束索引
# 5. 并行独立数据库
```

```python
# 测试金字塔落地步骤
# 1. 搭框架
# 2. 写单元
# 3. 写集成
# 4. 写E2E
# 5. CI集成
# 6. 持续改进
```

```python
# 测试ROI
# 单元：高
# 集成：高
# E2E：中
```

```python
# 面试题：测试策略
# 识别流程
# 分层测试
# 选工具
```

```python
# 面试题：集成测试vs单元测试
# 单元：快、细
# 集成：真、慢
# 策略：金字塔
```

```python
# 金字塔ROI
# 单元：高ROI
# 集成：中ROI
# E2E：低ROI
```

```python
# 测试金字塔总结
# 单元：多快细
# 集成：中真
# E2E：少信心
```

> 💡 **深度讲解**：测试金字塔不是教条，而是"性价比"模型。底层测试性价比最高（快、稳定、覆盖广），顶层测试性价比最低（慢、脆弱）。但完全没有顶层测试，就像只看地图不走路——可能路都不通。关键是平衡：用最少的 E2E 测试覆盖最关键的用户路径，用大量单元测试覆盖核心逻辑。

> 📝 **本章精简总结**：
> - 核心概念：测试金字塔（单元→集成→E2E）
> - 关键原理：底层测试多、顶层测试少
> - 常用工具：pytest、pytest-cov
> - 最佳实践：80/15/5 比例
> - 常见坑点：倒金字塔（E2E 太多）

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：测试金字塔从下到上三层是什么？
>   - 答案：单元测试、集成测试、E2E测试
> - **进阶题（⭐⭐）**：为什么不应该写大量 E2E 测试？
>   - 思考方向：速度、稳定性、维护成本
> - **实战题（⭐⭐⭐）**：为一个电商系统设计测试策略：哪些用单元测试、哪些用集成测试、哪些用 E2E？
>   - 提示：核心算法用单元、数据库交互用集成、下单流程用E2E

---

## 二、集成测试概述与框架

### 2.1 什么是集成测试

集成测试验证多个模块协同工作的正确性。与单元测试不同，集成测试：
- 使用真实数据库/缓存/消息队列
- 测试模块间接口
- 验证数据流转
- 发现"接口契约"问题

**集成测试 vs 单元测试**：
- 单元测试：Mock 所有外部依赖，验证单个函数
- 集成测试：使用真实或近似真实的依赖，验证模块交互

### 2.2 pytest 集成测试基础

```python
# tests/integration/test_user_service.py
import pytest

# 集成测试标记
pytestmark = pytest.mark.integration

class TestUserServiceIntegration:
    """用户服务集成测试"""

    def test_create_and_get_user(self, db_session):
        """创建用户后能查询到"""
        # Arrange
        service = UserService(db=db_session)

        # Act
        user = service.create_user(
            email="test@example.com",
            name="测试用户"
        )
        retrieved = service.get_user(user.id)

        # Assert
        assert retrieved.email == "test@example.com"
        assert retrieved.name == "测试用户"
```

```python
# pytest.ini 配置
[pytest]
markers =
    integration: 集成测试
    e2e: 端到端测试
    slow: 慢测试
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short
```

### 2.3 集成测试组织方式

```python
# 项目测试目录结构
# tests/
# ├── unit/              # 单元测试
# │   ├── test_calculator.py
# │   └── test_utils.py
# ├── integration/       # 集成测试
# │   ├── test_db_integration.py
# │   ├── test_api_integration.py
# │   └── test_service_integration.py
# └── e2e/               # E2E测试
#     ├── test_user_flow.py
#     └── test_checkout_flow.py
```

```bash
# 运行不同类型的测试
pytest tests/unit/ -v              # 只跑单元测试
pytest tests/integration/ -v       # 只跑集成测试
pytest tests/e2e/ -v               # 只跑E2E测试
pytest -m integration -v           # 按标记跑
pytest -m "not e2e" -v             # 排除E2E
pytest -m "integration or slow"   # 跑集成或慢测试
```

### 2.4 测试 Fixtures 基础

```python
# conftest.py - 共享 fixtures
import pytest

@pytest.fixture(scope="session")
def db_engine():
    """数据库引擎（整个测试会话共享）"""
    engine = create_engine("postgresql://test:test@localhost/test_db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """每个测试函数一个独立会话"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

```python
# pytest 高级配置
# pytest.ini 完整配置示例

[pytest]
# 测试路径
testpaths = tests

# 文件匹配模式
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 默认选项
addopts = -v --tb=short --strict-markers

# 自定义标记
markers =
    unit: 单元测试
    integration: 集成测试
    e2e: 端到端测试
    slow: 慢测试（>1秒）
    db: 需要数据库
    external: 需要外部服务

# 日志
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)s] %(name)s: %(message)s
```

```python
# pytest 命令行参数速查
# pytest -v              # 详细输出
# pytest -q               # 简洁输出
# pytest -x               # 第一个失败就停
# pytest --maxfail=5      # 最多失败5个
# pytest -k "test_login"  # 按名字过滤
# pytest -m integration   # 按标记过滤
# pytest --lf             # 只跑上次失败的
# pytest --ff             # 先跑上次失败的
# pytest -n 4             # 4个worker并行
# pytest --cov=app        # 覆盖率
# pytest -s               # 显示print输出
# pytest --pdb            # 失败时进入debugger
```

```python
# pytest fixture 作用域详解
# function：每个测试函数（默认）
# class：每个测试类
# module：每个测试文件
# session：整个测试会话

@pytest.fixture(scope="function")
def fresh_data():
    """每个测试函数全新数据"""
    data = {"value": 0}
    yield data
    # 每个测试后重置

@pytest.fixture(scope="session")
def shared_db():
    """整个测试会话共享数据库"""
    engine = create_engine("postgresql://...")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
```

```python
# 参数化测试
import pytest

@pytest.mark.parametrize("input,expected", [
    ("", 0),
    ("hello", 5),
    ("hello world", 11),
])
def test_string_length(input, expected):
    assert len(input) == expected

# 组合参数化
@pytest.mark.parametrize("user_type", ["admin", "user", "guest"])
@pytest.mark.parametrize("action", ["view", "edit", "delete"])
def test_permissions(user_type, action):
    # 6种组合
    ...
```

```python
# pytest 高级插件
# pytest-asyncio：异步测试
# pytest-cov：覆盖率
# pytest-xdist：并行
# pytest-mock：Mock
# pytest-rerunfailures：重试
# pytest-html：HTML报告
# pytest-django：Django集成
# pytest-sphinx：文档测试

# 异步测试示例
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

```python
# conftest.py 最佳实践
# 1. 不要放太多fixture在顶层
# 2. 按目录分层conftest
# 3. 公共fixture放根目录
# 4. 特定fixture放对应目录

# tests/conftest.py - 全局fixture
@pytest.fixture(scope="session")
def db_engine(): ...

# tests/unit/conftest.py - 单元测试fixture
@pytest.fixture
def mock_db(): ...

# tests/integration/conftest.py - 集成测试fixture
@pytest.fixture
def real_db(): ...
```

```python
# pytest fixture 进阶技巧
# 1. autouse=True：自动应用到所有测试
# 2. params：参数化fixture
# 3. request：访问测试上下文
# 4. yield fixture：setup+teardown
# 5. fixture工厂：返回函数
```

```python
# pytest 命令行技巧
# 1. pytest --lf：只跑上次失败的
# 2. pytest --ff：先跑上次失败的
# 3. pytest -k "test_login"：按名字过滤
# 4. pytest -x：第一个失败就停
# 5. pytest --maxfail=5：最多失败5个
# 6. pytest -v -s：详细+打印
# 7. pytest --pdb：失败进debugger
# 8. pytest -n auto：并行
```

```python
# pytest fixture 作用域选择指南
# | 场景                | 推荐scope   | 原因                  |
# |---------------------|-------------|-----------------------|
# | 数据库连接          | session     | 复用，快              |
# | 数据库会话          | function    | 隔离，安全            |
# | 测试用户            | function    | 隔离                  |
# | 测试配置            | session     | 不变                  |
# | Mock对象           | function    | 隔离                  |
# | 浏览器             | session     | 复用，快              |
```

```python
# pytest fixture 工厂模式
# 需要不同参数创建多个对象时，用工厂fixture

@pytest.fixture
def make_user():
    """用户工厂函数"""
    users = []
    def _make(name="test", email=None):
        user = User(
            name=name,
            email=email or f"{name.lower()}@test.com"
        )
        users.append(user)
        return user
    return _make

# 使用
def test_with_factory(make_user):
    user1 = make_user("Alice")
    user2 = make_user("Bob")
    assert user1.name == "Alice"
    assert user2.name == "Bob"
```

```python
# pytest 参数化测试最佳实践
# 1. 测试边界值（空、最大、最小）
# 2. 测试常见输入
# 3. 测试异常输入
# 4. 用 ids 标注参数名
# 5. 组合参数化用@pytest.mark.parametrize堆叠
```

```python
# pytest fixture 作用域选择
# function：每个测试函数（默认）
# class：每个测试类
# module：每个测试文件
# session：整个测试会话
# 选择原则：越短越隔离，越长越快
```

```python
# 测试金字塔量化指标
# 单元:集成:E2E = 80:15:5
# 通过率：100%
# Flaky率：<1%
# 覆盖率：>80%
# 本地运行：<5分钟
```

```python
# conftest最佳实践
# 分层目录
# 公共fixture放根
# 特定fixture放对应目录
```

```python
# pytest参数化
# 边界值
# 常见输入
# 异常输入
```

```python
# 量化指标
# 单元:集成:E2E = 80:15:5
# 通过率100%
# Flaky<1%
```

```python
# pytest fixture作用域
# function
# class
# module
# session
```

```python
# 集成测试类型
# 模块间集成
# DB集成
# API集成
# 服务间集成
```

```python
# 集成测试核心
# 真实组件
# 状态管理
# 隔离
```

> 💡 **深度讲解**：集成测试的核心挑战是"状态管理"——测试之间不能互相污染。最佳实践是：每个测试函数独立的事务，测试结束后回滚。这样既保证了测试隔离，又比每次重建数据库快得多。

> 📝 **本章精简总结**：
> - 核心概念：集成测试、pytest fixtures、测试标记
> - 关键原理：模块间交互验证
> - 常用操作：pytest.mark.integration、fixture scope
> - 最佳实践：按目录组织测试、事务回滚隔离
> - 常见坑点：测试间数据污染

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：集成测试和单元测试的主要区别？
>   - 答案：集成测试使用真实依赖，单元测试Mock所有依赖
> - **进阶题（⭐⭐）**：为什么每个测试需要独立的数据库会话？
>   - 思考方向：测试隔离、避免数据污染
> - **实战题（⭐⭐⭐）**：设计一个集成测试目录结构和pytest配置。
>   - 提示：unit/integration/e2e三层目录 + markers

---

## 三、数据库集成测试

### 3.1 Testcontainers 基础

Testcontainers 用 Docker 容器运行真实数据库，实现"测试用真实数据库"的集成测试。

```python
# pip install testcontainers[postgresql]

from testcontainers.postgres import PostgresContainer
import pytest

@pytest.fixture(scope="session")
def postgres_container():
    """启动 PostgreSQL 容器"""
    with PostgresContainer("postgres:16-alpine") as container:
        yield container

@pytest.fixture(scope="session")
def db_engine(postgres_container):
    """从容器创建数据库引擎"""
    from sqlalchemy import create_engine
    engine = create_engine(postgres_container.get_connection_url())
    Base.metadata.create_all(engine)
    yield engine
```

### 3.2 内存数据库（SQLite in-memory）

```python
# SQLite in-memory 快速测试
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
def db_session():
    """SQLite in-memory 数据库"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

# 注意：SQLite 不支持 PostgreSQL 特有功能
# - JSONB → 用 JSON
# - ARRAY → 用字符串序列化
# - 全文搜索 → 用 LIKE
# 建议：生产用 PostgreSQL，测试也用 PostgreSQL（Testcontainers）
```

### 3.3 数据库迁移测试

```python
# 测试数据库迁移是否正确
from alembic.config import Config
from alembic import command

def test_migrations_upgrade(db_container):
    """测试数据库迁移能正常升级"""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_container.get_connection_url())

    # 执行迁移
    command.upgrade(alembic_cfg, "head")

    # 验证表结构
    engine = create_engine(db_container.get_connection_url())
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "orders" in tables
```

### 3.4 事务隔离测试

```python
# 测试事务行为是否正确
def test_transaction_rollback(db_session):
    """测试事务回滚"""
    # 开始事务
    transaction = db_session.begin()

    # 插入数据
    user = User(name="test")
    db_session.add(user)
    db_session.flush()

    # 回滚
    transaction.rollback()

    # 验证数据不存在
    assert db_session.query(User).filter_by(name="test").first() is None

def test_transaction_commit(db_session):
    """测试事务提交"""
    user = User(name="test")
    db_session.add(user)
    db_session.commit()

    # 新会话查询
    new_session = Session(bind=db_session.bind)
    result = new_session.query(User).filter_by(name="test").first()
    assert result is not None
```

### 3.5 并发数据库测试

```python
# 测试并发访问数据库
import threading
from concurrent.futures import ThreadPoolExecutor

def test_concurrent_inserts(db_container):
    """测试并发插入"""
    engine = create_engine(db_container.get_connection_url())

    def insert_user(name):
        with Session(bind=engine) as session:
            user = User(name=name)
            session.add(user)
            session.commit()

    # 并发插入100个用户
    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(insert_user, [f"user_{i}" for i in range(100)]))

    # 验证全部插入成功
    with Session(bind=engine) as session:
        count = session.query(User).count()
        assert count == 100
```

```python
# Testcontainers 高级用法
from testcontainers.postgres import PostgresContainer
from testcontainers.core.container import DockerContainer
import psycopg2

# 自定义 PostgreSQL 容器
class CustomPostgresContainer(PostgresContainer):
    def __init__(self, version="16", **kwargs):
        super().__init__(f"postgres:{version}-alpine", **kwargs)

# 多容器测试栈
class TestStack:
    def __init__(self):
        self.postgres = PostgresContainer("postgres:16-alpine")
        self.redis = DockerContainer("redis:7-alpine")

    def start(self):
        self.postgres.start()
        self.redis.start()

    def stop(self):
        self.postgres.stop()
        self.redis.stop()

@pytest.fixture(scope="session")
def test_stack():
    stack = TestStack()
    stack.start()
    yield stack
    stack.stop()
```

```python
# 数据库迁移回滚测试
def test_migration_rollback(postgres_container):
    """测试数据库迁移回滚"""
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        postgres_container.get_connection_url()
    )

    # 升级到最新
    command.upgrade(alembic_cfg, "head")

    # 回滚一个版本
    command.downgrade(alembic_cfg, "-1")

    # 验证表结构
    engine = create_engine(postgres_container.get_connection_url())
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables  # 基本表还在
```

```python
# 数据库约束测试
def test_unique_constraint(db_session):
    """测试唯一约束"""
    # 创建第一个用户
    user1 = User(email="test@example.com", name="User1")
    db_session.add(user1)
    db_session.commit()

    # 创建相同 email 的用户 → 应该报错
    user2 = User(email="test@example.com", name="User2")
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
```

```python
# Testcontainers 常见数据库
from testcontainers.postgres import PostgresContainer
from testcontainers.mysql import MySqlContainer
from testcontainers.redis import RedisContainer
from testcontainers.kafka import KafkaContainer

# PostgreSQL
with PostgresContainer("postgres:16-alpine") as pg:
    conn = psycopg2.connect(pg.get_connection_url())

# MySQL
with MySqlContainer("mysql:8") as mysql:
    conn = mysql.connections()[0]

# Redis
with RedisContainer("redis:7-alpine") as redis:
    r = redis.Redis(**redis.get_connection_url())

# Kafka
with KafkaContainer("confluentinc/cp-kafka:7.5.0") as kafka:
    bootstrap = kafka.get_bootstrap_server()
```

```python
# SQLite vs PostgreSQL 测试对比
# SQLite 测试：
# - 优点：极快（<10ms）
# - 缺点：不支持JSONB/ARRAY/全文搜索
# - 适合：纯CRUD、简单查询

# PostgreSQL 测试（Testcontainers）：
# - 优点：与生产一致
# - 缺点：慢（~5s启动容器）
# - 适合：复杂查询、JSONB、全文搜索
```

```python
# 数据库集成测试性能优化
# 1. 事务回滚（比删除快10倍）
# 2. 会话级数据库（比每次重建快100倍）
# 3. 内存数据库（SQLite，比Docker快1000倍）
# 4. 并行测试（pytest-xdist）

# 性能对比：
# SQLite in-memory：0.1s
# PostgreSQL Testcontainers：5s
# PostgreSQL 本地：0.5s
# 结论：开发用SQLite，CI用PostgreSQL
```

```python
# 数据库集成测试最佳实践
# 1. 用真实数据库（PostgreSQL），不用SQLite
# 2. 事务回滚隔离（每个测试独立）
# 3. 测试约束（唯一、外键、检查）
# 4. 测试迁移升级/回滚
# 5. 测试索引存在（避免遗漏索引）
```

```python
# Testcontainers 性能优化
# 1. 复用容器（session scope）
# 2. 预拉取镜像
# 3. 用alpine版本（更小更快）
# 4. 并行测试用不同容器
# 5. 本地开发用本地PostgreSQL（不用Docker）
```

```python
# 数据库测试常见问题
# 问题1：测试太慢 → 用事务回滚
# 问题2：测试间污染 → 独立事务
# 问题3：连接数不够 → 连接池
# 问题4：CI失败 → Testcontainers
# 问题5：迁移失败 → 测试迁移
```

```python
# 测试覆盖率工具对比
# | 工具        | 语言    | 特点                  |
# |-------------|---------|-----------------------|
# | coverage.py | Python  | 标准，pytest-cov封装  |
# | pytest-cov  | Python  | pytest插件，易用      |
# | SonarQube   | 多语言  | 质量平台，历史趋势    |
# | Codecov     | 多语言  | 在线报告，PR评论      |
```

```python
# 数据库迁移测试
# 1. 测试升级（upgrade）
# 2. 测试回滚（downgrade）
# 3. 测试从空库到最新
# 4. 测试从旧版本到最新
```

```python
# 数据库测试性能基准
# SQLite in-memory：0.1s
# PostgreSQL本地：0.5s
# PostgreSQL Testcontainers：5s
# 结论：开发用SQLite，CI用PostgreSQL
```

```python
# Testcontainers 支持的数据库
# PostgreSQL
# MySQL
# MongoDB
# Redis
# Kafka
# Elasticsearch
# 几乎所有主流数据库
```

```python
# 数据库测试最佳实践
# 1. 真实数据库
# 2. 事务回滚
# 3. 测试约束
# 4. 测试迁移
# 5. 测试索引
```

```python
# 数据库测试性能
# SQLite：0.1s
# PG本地：0.5s
# PG容器：5s
```

```python
# 迁移测试
# 升级
# 回滚
# 空库到最新
```

```python
# Testcontainers支持
# PostgreSQL
# MySQL
# Redis
# Kafka
```

```python
# 测试策略选择
# 小项目：单元+集成
# 中项目：+API E2E
# 大项目：+UI E2E
```

```python
# 数据库测试要点
# 约束
# 索引
# 迁移
# 真实DB
```

```python
# Testcontainers
# 真实DB
# 自动启停
```

> 💡 **深度讲解**：数据库集成测试的黄金标准是 Testcontainers——用 Docker 启动真实 PostgreSQL/MySQL，确保测试环境与生产一致。SQLite in-memory 虽然快，但语法差异大（不支持 JSONB、ARRAY 等），容易出现"测试通过但生产报错"的问题。生产用什么数据库，测试就用什么数据库。

> 📝 **本章精简总结**：
> - 核心概念：Testcontainers、事务隔离、迁移测试
> - 关键原理：测试环境与生产环境一致
> - 常用工具：testcontainers、SQLAlchemy、Alembic
> - 最佳实践：用真实数据库做集成测试
> - 常见坑点：SQLite 与 PostgreSQL 语法差异

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：Testcontainers 的作用是什么？
>   - 答案：用Docker容器运行真实数据库做集成测试
> - **进阶题（⭐⭐）**：为什么不建议用 SQLite 做 PostgreSQL 的集成测试？
>   - 思考方向：语法差异、功能不支持
> - **实战题（⭐⭐⭐）**：用 Testcontainers 写一个完整的数据库集成测试。
>   - 提示：启动PostgreSQL容器→建表→插入数据→验证

---

## 四、API 集成测试（FastAPI TestClient）

### 4.1 FastAPI TestClient 基础

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

# 创建 FastAPI 应用
app = FastAPI()

@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id, "name": "测试用户"}

# TestClient 基础用法
def test_get_user():
    client = TestClient(app)
    response = client.get("/api/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "测试用户"
```

### 4.2 数据库集成的 API 测试

```python
# 带数据库的 API 测试
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

app = FastAPI()

# 依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 测试：覆盖依赖
def test_create_user(db_session):
    # 覆盖依赖，使用测试数据库
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    response = client.post(
        "/api/users",
        json={"email": "test@example.com", "name": "测试"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

    # 清理依赖覆盖
    app.dependency_overrides.clear()
```

### 4.3 请求/响应验证

```python
# 详细的 API 测试
def test_user_api_full_flow(db_session):
    client = TestClient(app)
    app.dependency_overrides[get_db] = lambda: iter([db_session])

    # 1. 创建用户
    response = client.post("/api/users", json={
        "email": "test@example.com",
        "name": "测试用户"
    })
    assert response.status_code == 200
    user_id = response.json()["id"]

    # 2. 查询用户
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

    # 3. 更新用户
    response = client.put(f"/api/users/{user_id}", json={
        "name": "新名字"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "新名字"

    # 4. 删除用户
    response = client.delete(f"/api/users/{user_id}")
    assert response.status_code == 204

    app.dependency_overrides.clear()
```

### 4.4 错误处理测试

```python
def test_api_error_handling(db_session):
    client = TestClient(app)
    app.dependency_overrides[get_db] = lambda: iter([db_session])

    # 404 测试
    response = client.get("/api/users/99999")
    assert response.status_code == 404

    # 422 验证错误
    response = client.post("/api/users", json={
        "email": "invalid-email",  # 格式错误
        "name": ""
    })
    assert response.status_code == 422
    assert "detail" in response.json()

    app.dependency_overrides.clear()
```

```python
# FastAPI TestClient 高级用法
from fastapi.testclient import TestClient
from fastapi import status

# 带请求头的测试
def test_with_headers():
    client = TestClient(app)
    response = client.get(
        "/api/protected",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 200

# 带 Cookies 的测试
def test_with_cookies():
    client = TestClient(app)
    # 设置 cookie
    client.cookies["session"] = "test-session-id"
    response = client.get("/api/profile")
    assert response.status_code == 200

# 文件上传测试
def test_file_upload():
    client = TestClient(app)
    with open("test_file.txt", "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", f, "text/plain")}
        )
    assert response.status_code == 200
```

```python
# TestClient 依赖覆盖工厂
def override_dependencies(db_session):
    """创建依赖覆盖的工厂"""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return app

# 使用
def test_endpoint(db_session):
    client = TestClient(override_dependencies(db_session))
    response = client.get("/api/users")
    assert response.status_code == 200
    app.dependency_overrides.clear()
```

```python
# FastAPI 测试覆盖率优化
# 确保所有路由都有测试

from fastapi.testclient import TestClient
import pytest

def test_all_routes_have_tests(app):
    """自动验证所有路由都有测试"""
    client = TestClient(app)
    routes = [r for r in app.routes if hasattr(r, 'methods')]

    for route in routes:
        path = route.path
        methods = route.methods - {"HEAD", "OPTIONS"}
        for method in methods:
            # 这里只是示例，实际应该检查测试是否存在
            print(f"Route: {method} {path}")
```

```python
# API 契约测试
# 确保 API 响应格式与预期一致
def test_user_response_schema(client):
    response = client.get("/api/users/1")
    data = response.json()

    # 验证字段存在
    assert "id" in data
    assert "email" in data
    assert "name" in data
    assert "created_at" in data

    # 验证字段类型
    assert isinstance(data["id"], int)
    assert isinstance(data["email"], str)
    assert "@" in data["email"]
```

```python
# FastAPI 测试最佳实践
# 1. 用 dependency_overrides 替换依赖
# 2. 每个测试独立数据库会话
# 3. 测试完整请求/响应生命周期
# 4. 验证状态码+响应体+Header
# 5. 测试错误场景（404、422、500）

# 完整的 API 测试模板
def test_endpoint_template(client, db_session):
    # Arrange
    test_data = {...}

    # Act
    response = client.post("/api/endpoint", json=test_data)

    # Assert
    assert response.status_code == 201
    assert response.json()["field"] == test_data["field"]
```

```python
# API 测试最佳实践
# 1. 测试所有HTTP方法（GET/POST/PUT/DELETE）
# 2. 测试所有状态码（200/201/400/401/403/404/422/500）
# 3. 测试请求参数校验
# 4. 测试认证/授权
# 5. 测试分页/排序/过滤
# 6. 测试错误消息格式
```

```python
# FastAPI 测试性能优化
# 1. 用 httpx.ASGITransport（不用真实HTTP）
# 2. 用 in-memory 数据库（SQLite）
# 3. 并行运行测试
# 4. session scope的fixture
```

```python
# API测试常见问题
# 问题1：依赖太多 → dependency_overrides
# 问题2：测试数据重复 → 工厂模式
# 问题3：异步测试 → pytest-asyncio
# 问题4：认证测试 → 认证fixture
# 问题5：性能测试 → Locust
```

```python
# 测试断言风格
# | 风格        | 示例                  | 优点              |
# |-------------|-----------------------|-------------------|
# | assert语句  | assert x == 1         | 简单直接          |
# | assert语句  | assert "name" in data | 可读性好          |
# | pytest.raises | pytest.raises(ValueError) | 异常测试  |
# | expect()    | expect(locator).to_be_visible() | Playwright |
```

```python
# API测试数据验证
# 1. 验证状态码
# 2. 验证响应体结构
# 3. 验证字段类型
# 4. 验证字段值范围
# 5. 验证Header
# 6. 验证分页元数据
```

```python
# API测试覆盖率目标
# 所有路由都有测试
# 所有状态码都有测试
# 所有错误场景都有测试
# 核心业务流程覆盖
# 目标：>90%路由覆盖
```

```python
# FastAPI 测试最佳实践
# 1. dependency_overrides替换依赖
# 2. 每个测试独立数据库会话
# 3. 测试完整请求/响应
# 4. 验证状态码+响应体
# 5. 测试错误场景
```

```python
# API测试最佳实践
# 1. 所有HTTP方法
# 2. 所有状态码
# 3. 参数校验
# 4. 认证授权
# 5. 分页排序
```

```python
# API测试覆盖率
# 所有路由
# 所有状态码
# 所有错误场景
```

```python
# API数据验证
# 状态码
# 响应体
# 字段类型
```

```python
# FastAPI测试最佳实践
# dependency_overrides
# 独立会话
# 完整流程
```

```python
# 测试覆盖率
# 语句覆盖
# 分支覆盖
# 路径覆盖
```

```python
# API测试要点
# 状态码
# Schema
# 认证
# 错误码
```

> 💡 **深度讲解**：FastAPI TestClient 的核心优势是 `dependency_overrides`——可以在测试中替换生产依赖。比如生产中用真实数据库，测试中用测试数据库；生产中调用真实支付API，测试中用 Mock。这让 API 测试既快又可控。

> 📝 **本章精简总结**：
> - 核心概念：TestClient、依赖注入覆盖
> - 关键原理：HTTP 请求/响应全链路测试
> - 常用工具：fastapi.testclient.TestClient
> - 最佳实践：覆盖依赖、测试完整CRUD流程
> - 常见坑点：忘记清理 dependency_overrides

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：TestClient 是什么？
>   - 答案：FastAPI的测试客户端，模拟HTTP请求
> - **进阶题（⭐⭐）**：如何在测试中替换数据库依赖？
>   - 思考方向：app.dependency_overrides
> - **实战题（⭐⭐⭐）**：为一个完整的CRUD API写集成测试。
>   - 提示：创建→查询→更新→删除全流程

---

## 五、Mock 与 Stub 的边界

### 5.1 Mock vs Stub vs Fake

```python
# 三种测试替身的区别

# Stub：返回预设数据
class StubPaymentGateway:
    def charge(self, amount):
        return {"success": True, "transaction_id": "stub_123"}

# Mock：验证交互行为
class MockPaymentGateway:
    def __init__(self):
        self.charged_amount = None
        self.called = False

    def charge(self, amount):
        self.called = True
        self.charged_amount = amount
        return {"success": True}

# Fake：可工作的简化实现
class FakePaymentGateway:
    def __init__(self):
        self.transactions = []

    def charge(self, amount):
        txn = {"id": len(self.transactions), "amount": amount}
        self.transactions.append(txn)
        return {"success": True, "transaction_id": txn["id"]}
```

### 5.2 unittest.mock 基础

```python
from unittest.mock import Mock, patch, MagicMock

# Mock 基础
def test_with_mock():
    # 创建 Mock 对象
    mock_service = Mock()
    mock_service.get_user.return_value = {"id": 1, "name": "test"}

    # 使用 Mock
    result = mock_service.get_user(1)
    assert result == {"id": 1, "name": "test"}

    # 验证调用
    mock_service.get_user.assert_called_once_with(1)
    mock_service.get_user.assert_called_with(1)

# patch 装饰器
@patch("app.services.payment.PaymentGateway")
def test_payment_process(mock_gateway_class):
    mock_gateway = mock_gateway_class.return_value
    mock_gateway.charge.return_value = {"success": True}

    service = OrderService()
    result = service.checkout(100)

    assert result["success"] is True
    mock_gateway.charge.assert_called_once_with(100)
```

### 5.3 Mock 边界原则

```python
# ✅ 应该 Mock 的：
# - 外部 API（支付、短信、邮件）
# - 第三方服务（AWS、GitHub）
# - 时间（datetime.now()）
# - 随机数（random.random()）

# ❌ 不应该 Mock 的：
# - 自己写的数据模型
# - 纯函数
# - 内存中的简单对象

# 示例：正确的 Mock 边界
def test_order_service():
    # ✅ Mock 外部支付服务
    payment_gateway = Mock()
    payment_gateway.charge.return_value = {"success": True}

    # ✅ 使用真实订单模型（不Mock）
    service = OrderService(payment=payment_gateway)
    order = Order(items=[Item(price=100)], total=100)

    result = service.process(order)
    assert result["paid"] is True
    payment_gateway.charge.assert_called_once_with(100)
```

### 5.4 pytest-mock 插件

```python
# pip install pytest-mock

# pytest-mock 提供 mocker fixture
def test_with_mocker(mocker):
    # Mock 外部 API 调用
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"status": "ok"}

    service = ExternalService()
    result = service.check_status()
    assert result == "ok"
    mock_get.assert_called_once_with("https://api.example.com/status")

# Mock 时间
def test_time_business(mocker):
    mock_datetime = mocker.patch("datetime.datetime")
    mock_datetime.now.return_value = datetime(2026, 1, 1)

    result = BusinessLogic.get_today()
    assert result == datetime(2026, 1, 1)
```

```python
# Mock 高级技巧：side_effect
from unittest.mock import Mock

# side_effect 返回序列
mock = Mock(side_effect=[1, 2, 3])
assert mock() == 1
assert mock() == 2
assert mock() == 3

# side_effect 抛出异常
mock = Mock(side_effect=ValueError("出错了"))
try:
    mock()
except ValueError:
    pass

# side_effect 动态计算
def side_effect_func(x):
    return x * 2

mock = Mock(side_effect=side_effect_func)
assert mock(5) == 10

# side_effect 根据参数返回不同值
mock = Mock(side_effect=lambda x: "admin" if x == 1 else "user")
assert mock(1) == "admin"
assert mock(2) == "user"
```

```python
# Mock 断言技巧
# 验证调用次数
mock = Mock()
mock(1)
mock(2)
mock(3)
assert mock.call_count == 3

# 验证所有调用参数
mock.assert_has_calls([call(1), call(2), call(3)])

# 验证至少调用一次
mock.assert_any_call(2)

# 验证没有调用
mock.reset_mock()
mock.assert_not_called()

# 获取所有调用
for call_args in mock.call_args_list:
    print(call_args)
```

```python
# pytest-mock 高级用法
def test_mock_external_service(mocker):
    # Mock 整个模块
    mock_requests = mocker.patch("requests.get")
    mock_requests.return_value.status_code = 200
    mock_requests.return_value.json.return_value = {"data": "test"}

    service = MyService()
    result = service.fetch_data()
    assert result == {"data": "test"}

    # 验证调用
    mock_requests.assert_called_once_with("https://api.example.com/data")
```

```python
# Mock vs 真实依赖决策树
# 1. 是外部API吗？→ Mock
# 2. 是数据库吗？→ 真实（集成测试）
# 3. 是时间吗？→ Mock
# 4. 是随机数吗？→ Mock
# 5. 是自己的业务逻辑吗？→ 真实
# 6. 是第三方SDK吗？→ Mock

# 示例：测试一个发送邮件的函数
def test_send_email():
    # Mock 外部SMTP服务
    mock_smtp = Mock()

    service = EmailService(smtp=mock_smtp)
    service.send(to="test@example.com", subject="Hello")

    # 验证调用了SMTP
    mock_smtp.sendmail.assert_called_once()
    # 验证自己的逻辑正确（邮件内容格式）
    call_args = mock_smtp.sendmail.call_args
    assert "Hello" in call_args[0][2]
```

```python
# Mock 边界决策矩阵
# | 依赖类型        | 单元测试 | 集成测试 | E2E测试 |
# |-----------------|----------|----------|---------|
# | 外部API         | Mock     | Mock     | 真实    |
# | 数据库          | Mock     | 真实     | 真实    |
# | 缓存            | Mock     | 真实     | 真实    |
# | 时间            | Mock     | Mock     | Mock    |
# | 随机数          | Mock     | Mock     | Mock    |
# | 业务逻辑        | 真实     | 真实     | 真实    |
```

```python
# Mock 最佳实践
# 1. Mock 外部依赖，不Mock自己的代码
# 2. 验证Mock被正确调用
# 3. 测试结束清理Mock
# 4. 不要Mock太多（否则测试无意义）
# 5. 优先用Fake而非Mock（Fake可工作的简化版）
```

```python
# Mock 性能优化
# 1. 只Mock必须Mock的
# 2. 用Fake替代Mock（更快）
# 3. session scope的Mock
# 4. 不要在测试循环中创建Mock
```

```python
# Mock常见问题
# 问题1：Mock太多 → 只Mock外部依赖
# 问题2：测试无意义 → 测试行为不测试实现
# 问题3：Mock没清理 → 用fixture自动清理
# 问题4：Mock不对 → 验证调用参数
```

```python
# 测试命名规范
# 推荐格式：test_should_<预期结果>_when_<条件>
# ✅ test_should_return_404_when_user_not_found
# ✅ test_should_create_user_when_valid_data
# ✅ test_should_raise_error_when_email_invalid
# ❌ test_user
# ❌ test_user_not_found
# ❌ test_create
```

```python
# Mock 验证技巧
# 1. assert_called_once()：验证调用一次
# 2. assert_called_with()：验证参数
# 3. assert_not_called()：验证没调用
# 4. call_args_list：查看所有调用
# 5. call_count：调用次数
```

```python
# Mock 边界决策总结
# 外部API → Mock
# 数据库 → 真实（集成测试）
# 时间 → Mock
# 随机数 → Mock
# 业务逻辑 → 真实
# 第三方SDK → Mock
```

```python
# Mock 最佳实践
# 1. Mock外部依赖
# 2. 验证Mock调用
# 3. 测试结束清理
# 4. 不要Mock太多
# 5. 优先Fake而非Mock
```

```python
# Mock边界决策矩阵
# 外部API → Mock
# 数据库 → 真实
# 时间 → Mock
# 随机数 → Mock
# 业务逻辑 → 真实
# 第三方SDK → Mock
```

```python
# Mock验证技巧
# assert_called_once
# assert_called_with
# assert_not_called
```

```python
# Mock边界总结
# 外部API
# 数据库真实
# 时间Mock
```

```python
# Mock最佳实践
# Mock外部
# 验证调用
# 清理
```

```python
# Mock vs Stub vs Fake
# Mock：验证交互
# Stub：返回数据
# Fake：简化实现
```

```python
# Mock边界
# 外部API Mock
# 数据库真实
# 时间Mock
# 业务逻辑真实
```

> 💡 **深度讲解**：Mock 的黄金法则是"Mock 别人的代码，不要 Mock 自己的代码"。Mock 外部依赖（API、时间、随机数），但真实测试自己的业务逻辑。如果需要 Mock 自己的代码，说明设计有问题——应该拆分职责。

> 📝 **本章精简总结**：
> - 核心概念：Mock、Stub、Fake、Spy
> - 关键原理：Mock外部依赖，测试自己的逻辑
> - 常用工具：unittest.mock、pytest-mock
> - 最佳实践：Mock别人的代码，不Mock自己的
> - 常见坑点：过度Mock导致测试无意义

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：Mock 和 Stub 的区别？
>   - 答案：Stub返回预设数据，Mock验证交互行为
> - **进阶题（⭐⭐）**：哪些东西应该Mock？哪些不应该？
>   - 思考方向：外部API vs 自己的业务逻辑
> - **实战题（⭐⭐⭐）**：用pytest-mock测试一个调用外部API的函数。
>   - 提示：mocker.patch + mock.return_value

---

## 六、E2E 测试概述

### 6.1 什么是 E2E 测试

端到端测试（End-to-End Testing）模拟真实用户操作，验证整个应用流程是否正确。

**E2E 测试特点**：
- 从用户视角测试
- 使用真实环境（数据库、API）
- 测试完整业务流程
- 慢、脆弱、维护成本高

**E2E 测试适用场景**：
- 注册→登录→下单→支付完整流程
- 核心业务路径
- 回归测试

```python
# E2E 测试 vs 集成测试对比

# 集成测试：测试 API 端点
def test_create_user_api():
    client = TestClient(app)
    response = client.post("/users", json={...})
    assert response.status_code == 200

# E2E 测试：测试用户完整操作流程
async def test_user_registration_flow(page):
    # 1. 打开注册页
    await page.goto("https://app.example.com/register")

    # 2. 填写表单
    await page.fill("#email", "test@example.com")
    await page.fill("#password", "secure123")

    # 3. 点击注册
    await page.click("#register-btn")

    # 4. 验证跳转到首页
    await page.wait_for_url("https://app.example.com/dashboard")
    assert await page.text_content(".welcome") == "欢迎，test@example.com"
```

### 6.2 E2E 测试框架选择

| 框架 | 语言 | 特点 | 适合场景 |
|------|------|------|----------|
| Playwright | Python/JS | 现代、稳定、自动等待 | Web UI E2E |
| Selenium | 多语言 | 老牌、生态成熟 | 传统Web |
| Cypress | JS | 开发体验好 | 前端项目 |
| httpx | Python | API级E2E | API流程测试 |

**推荐**：Python 项目用 Playwright，API E2E 用 httpx

### 6.3 E2E 测试设计原则

```python
# E2E 测试设计原则
# 1. 测试关键路径（Happy Path）
# 2. 测试少量关键场景（不要覆盖所有分支）
# 3. 使用测试数据工厂（不要手动准备数据）
# 4. 等待元素出现（不要 sleep）
# 5. 测试失败时截图/录像

# ✅ 好的 E2E 测试
async def test_checkout_flow(page, test_data):
    # 登录
    await page.goto("/login")
    await page.fill("#username", test_data["user"])
    await page.fill("#password", test_data["password"])
    await page.click("#login")

    # 添加商品
    await page.goto("/products")
    await page.click(".add-to-cart:first-child")

    # 结账
    await page.goto("/cart")
    await page.click("#checkout")

    # 验证订单
    await page.wait_for_url("/orders/*")
    assert await page.text_content(".order-status") == "已下单"

# ❌ 坏的 E2E 测试
async def test_all_features(page):
    # 测试所有功能 → 太脆弱、维护成本高
    await page.goto("/settings")
    await page.fill("#name", "...")
    await page.click("#save")
    # ... 几百行
```

```python
# E2E 测试场景设计
# 一个典型的电商系统 E2E 场景

# 场景1：用户注册→登录→浏览→加购→下单
async def test_shopping_flow(page):
    # 注册新用户
    await page.goto("/register")
    await page.fill("#email", "newuser@test.com")
    await page.fill("#password", "test123")
    await page.click("#register")

    # 自动登录
    await page.wait_for_url("/dashboard")

    # 浏览商品
    await page.goto("/products")
    await page.click(".product:first-child .add-to-cart")

    # 查看购物车
    await page.goto("/cart")
    assert await page.text_content(".cart-count") == "1"

    # 下单
    await page.click("#checkout-btn")
    await page.wait_for_url("/orders/*")
    assert await page.text_content(".order-status") == "已下单"

# 场景2：支付流程
async def test_payment_flow(page, auth_state):
    await page.goto("/cart")
    await page.click("#checkout")
    await page.select_option("#payment-method", "credit_card")
    await page.fill("#card-number", "4111-1111-1111-1111")
    await page.click("#pay")
    await page.wait_for_selector(".payment-success")
```

```python
# E2E 测试 vs 手动测试对比
# | 方面        | 手动测试        | E2E自动化测试    |
# |-------------|-----------------|------------------|
# | 速度        | 慢（分钟级）    | 快（秒级）       |
# | 重复性      | 低（人会累）    | 高（机器不知疲倦）|
# | 一致性      | 低（主观）      | 高（每次相同）   |
# | 覆盖范围    | 有限            | 可全覆盖         |
# | 维护成本    | 低              | 高               |
# | 首次成本    | 低              | 高               |
# | 适合阶段    | 探索性测试      | 回归测试         |
```

```python
# E2E 测试环境搭建
# 1. 启动应用
# 2. 启动依赖（数据库、缓存）
# 3. 准备测试数据
# 4. 运行E2E测试
# 5. 清理

# conftest.py
import pytest
import subprocess
import time
import httpx

@pytest.fixture(scope="session")
def e2e_app():
    """启动E2E测试应用"""
    # 启动应用
    proc = subprocess.Popen([
        "uvicorn", "app.main:app", "--port", "8001"
    ])

    # 等待启动
    for _ in range(30):
        try:
            response = httpx.get("http://localhost:8001/health")
            if response.status_code == 200:
                break
        except:
            time.sleep(1)

    yield "http://localhost:8001"

    # 关闭应用
    proc.terminate()
    proc.wait()
```

```python
# E2E 测试覆盖率策略
# 不需要覆盖所有页面和操作
# 只覆盖关键用户路径：
# 1. 新用户注册→首次登录
# 2. 核心业务流程（如下单、支付）
# 3. 高频使用路径
# 4. 最近修改的功能

# 示例：电商系统E2E场景
# ✅ 注册→登录→浏览→加购→下单
# ✅ 支付成功流程
# ❌ 设置页修改昵称
# ❌ 修改密码
```

```python
# E2E 测试最佳实践
# 1. 只覆盖关键用户路径（5-10个）
# 2. 用 testid 选择器（最稳定）
# 3. 自动等待元素（不要sleep）
# 4. 失败时截图/录像
# 5. 测试数据自动创建+清理
# 6. 并行运行（多浏览器）
# 7. nightly运行（不阻塞开发）
```

```python
# E2E 测试性能优化
# 1. 并行运行（多浏览器）
# 2. 复用登录状态
# 3. 减少E2E测试数量
# 4. 用API E2E替代UI E2E
# 5. nightly运行（不阻塞开发）
```

```python
# E2E常见问题
# 问题1：测试太脆弱 → 用testid选择器
# 问题2：测试太慢 → 减少E2E数量
# 问题3：flaky → wait_for替代sleep
# 问题4：维护成本高 → 只测关键路径
```

```python
# 测试结构最佳实践
# Arrange-Act-Assert 模式
# 1. Arrange：准备测试数据和依赖
# 2. Act：执行被测操作
# 3. Assert：验证结果

# 示例
def test_calculate_total():
    # Arrange
    cart = Cart()
    cart.add(Item(price=100))
    cart.add(Item(price=50))

    # Act
    total = cart.calculate_total()

    # Assert
    assert total == 150
```

```python
# E2E 测试覆盖率
# 不需要覆盖所有页面
# 只覆盖关键用户路径
# 每个关键路径一个E2E测试
# 其他用API集成测试覆盖
```

```python
# E2E 测试数量控制
# 小项目：3-5个E2E测试
# 中项目：5-10个E2E测试
# 大项目：10-20个E2E测试
# 原则：只覆盖关键路径
```

```python
# E2E 测试最佳实践
# 1. 覆盖关键路径
# 2. 用testid选择器
# 3. 自动等待
# 4. 失败截图
# 5. 数据自动清理
```

```python
# E2E覆盖策略
# 关键路径覆盖
# 高频使用路径
# 最近修改功能
# 核心业务流程
```

```python
# E2E数量控制
# 小项目：3-5个
# 中项目：5-10个
# 大项目：10-20个
```

```python
# E2E覆盖
# 关键路径
# 高频路径
# 最近修改
```

```python
# E2E最佳实践
# 关键路径
# testid
# 自动等待
```

```python
# E2E选择策略
# 关键路径必须
# 高频路径
# 最近修改
```

```python
# E2E覆盖原则
# 关键路径必测
# 高频路径
# 最近修改
# 核心流程
```

> 💡 **深度讲解**：E2E 测试的价值在于"信心"——确保真实用户操作流程能走通。但 E2E 测试维护成本极高，因为 UI 经常变。所以 E2E 测试要"少而精"：只覆盖最关键的用户路径（如注册、登录、下单），其他分支用集成测试覆盖。

> 📝 **本章精简总结**：
> - 核心概念：E2E测试、用户视角、完整流程
> - 关键原理：模拟真实用户操作
> - 常用工具：Playwright、Selenium、httpx
> - 最佳实践：少而精、覆盖关键路径
> - 常见坑点：E2E 太多导致维护噩梦

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：E2E测试和集成测试的区别？
>   - 答案：E2E从用户视角测试完整流程，集成测试模块间交互
> - **进阶题（⭐⭐）**：为什么E2E测试要"少而精"？
>   - 思考方向：维护成本、UI变化频繁
> - **实战题（⭐⭐⭐）**：设计一个电商系统的E2E测试场景。
>   - 提示：注册→登录→浏览→加购→下单→支付

---

## 七、Playwright E2E 测试

### 7.1 Playwright 安装与基础

```bash
# 安装 Playwright
pip install playwright
playwright install chromium
```

```python
# tests/e2e/test_login.py
import pytest
from playwright.sync_api import sync_playwright, Page

# Fixture：浏览器
@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    page = browser.new_page()
    yield page
    page.close()

# 基础测试
def test_login_success(page: Page):
    # 打开登录页
    page.goto("https://app.example.com/login")

    # 填写表单
    page.fill("#email", "test@example.com")
    page.fill("#password", "password123")

    # 点击登录
    page.click("#login-btn")

    # 验证跳转
    page.wait_for_url("**/dashboard")
    assert page.text_content(".welcome") == "欢迎，test@example.com"
```

### 7.2 Playwright 选择器

```python
# Playwright 选择器策略

# 1. CSS 选择器
page.click("#submit-btn")           # ID
page.click(".nav-item")             # Class
page.click("button[type='submit']") # 属性

# 2. 文本选择器
page.click("text=登录")              # 文本内容
page.click("text=/确认/")            # 正则匹配

# 3. Role 选择器（推荐，最稳定）
page.get_by_role("button", name="登录").click()
page.get_by_label("邮箱").fill("test@example.com")
page.get_by_placeholder("请输入密码").fill("123456")

# 4. Test ID（最稳定，推荐）
# HTML: <button data-testid="login-btn">登录</button>
page.click("[data-testid=login-btn]")
# 或
page.get_by_test_id("login-btn").click()
```

### 7.3 Playwright 异步模式

```python
# 异步 Playwright（适合异步应用）
import pytest
from playwright.async_api import async_playwright, Page

@pytest.fixture(scope="function")
async def async_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        yield page
        await browser.close()

@pytest.mark.asyncio
async def test_async_login(async_page: Page):
    await async_page.goto("https://app.example.com/login")
    await async_page.fill("#email", "test@example.com")
    await async_page.fill("#password", "password123")
    await async_page.click("#login-btn")
    await async_page.wait_for_url("**/dashboard")
```

### 7.4 失败截图与录像

```python
# 测试失败时自动截图
@pytest.fixture(scope="function")
def page(browser, request):
    page = browser.new_page()
    yield page
    # 测试失败时截图
    if request.node.rep_call.failed:
        page.screenshot(
            path=f"screenshots/{request.node.name}.png",
            full_page=True
        )
    page.close()

# 录像
@pytest.fixture(scope="function")
def recorded_page(browser):
    context = browser.new_context(
        record_video_dir="videos/"
    )
    page = context.new_page()
    yield page
    context.close()
```

```python
# Playwright 高级操作
from playwright.sync_api import Page, expect

# 断言
def test_assertions(page: Page):
    # 文本断言
    expect(page.locator(".title")).to_have_text("Welcome")
    expect(page.locator(".message")).to_contain_text("success")

    # 可见性断言
    expect(page.locator("#modal")).to_be_visible()
    expect(page.locator("#spinner")).to_be_hidden()

    # 启用状态断言
    expect(page.locator("#submit")).to_be_enabled()
    expect(page.locator("#submit")).to_be_disabled()

    # URL 断言
    expect(page).to_have_url("**/dashboard")

    # 标题断言
    expect(page).to_have_title("Dashboard | My App")

# 截图对比（视觉回归测试）
def test_visual_regression(page: Page):
    page.goto("/dashboard")
    # 截图对比（首次创建基线，后续对比）
    expect(page).to_have_screenshot("dashboard.png")
```

```python
# Playwright 网络拦截
def test_network_interception(page: Page):
    # 拦截 API 请求
    page.route("**/api/user", lambda route: route.fulfill(
        status=200,
        json={"id": 1, "name": "Mocked User"}
    ))

    page.goto("/profile")
    # 页面应该显示 Mocked User

# 修改请求头
def test_modify_headers(page: Page):
    def handle_route(route):
        headers = route.request.headers
        headers["X-Custom-Header"] = "test"
        route.continue_(headers=headers)

    page.route("**/*", handle_route)
```

```python
# Playwright 多浏览器测试
# 同时测试 Chrome、Firefox、Safari

@pytest.fixture(params=["chromium", "firefox", "webkit"])
def browser(page_browser, request):
    browser_type = request.param
    browser = page_browser[browser_type].launch()
    yield browser
    browser.close()

# 只跑特定浏览器
# pytest --browser chromium
```

```python
# Playwright 移动端测试
async def test_mobile_view(page):
    # 模拟 iPhone
    iphone = page.context
    await page.goto("/")
    await page.screenshot(path="mobile_view.png")

# 模拟视口
@pytest.fixture
def mobile_page(browser):
    context = browser.new_context(
        viewport={"width": 375, "height": 667},  # iPhone X
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"
    )
    page = context.new_page()
    yield page
    context.close()
```

```python
# Playwright vs Selenium 对比
# | 特性          | Playwright      | Selenium        |
# |---------------|-----------------|-----------------|
# | 自动等待      | ✅ 内置         | ❌ 需要WebDriverWait|
# | 浏览器        | Chromium/Firefox/WebKit | 多浏览器 |
# | 速度          | 快              | 慢              |
# | 并行          | ✅ 内置         | 需插件          |
# | 截图/录像     | ✅ 内置         | 需代码          |
# | 网络拦截      | ✅ 内置         | 需代理          |
# | 移动端模拟    | ✅ 内置         | 有限            |
# 结论：新项目用Playwright，老项目用Selenium
```

```python
# Playwright 最佳实践
# 1. 用 get_by_role/get_by_test_id 选择器
# 2. 用 expect() 断言（自动等待）
# 3. 用 fixture 管理浏览器生命周期
# 4. 失败时自动截图
# 5. 用 page.pause() 调试
# 6. 用 codegen 录制生成代码
```

```python
# Playwright 调试技巧
# 1. page.pause()：暂停测试，打开交互模式
# 2. headed=True：显示浏览器窗口
# 3. headed=False + 慢动作：slow_mo=1000
# 4. 生成代码：playwright codegen URL
# 5. 录制视频：record_video_dir
```

```python
# Playwright常见问题
# 问题1：元素找不到 → 用get_by_test_id
# 问题2：测试不稳定 → 自动等待
# 问题3：截图失败 → 加timeout
# 问题4：多浏览器 → 参数化fixture
```

```python
# Playwright 选择器优先级
# 1. get_by_test_id（最稳定，推荐）
# 2. get_by_role（语义化，稳定）
# 3. get_by_label（表单元素）
# 4. get_by_text（文本内容）
# 5. CSS选择器（最不稳定）
```

```python
# Playwright 代码生成
# 命令：playwright codegen https://example.com
# 自动生成Python代码
# 适合快速学习和录制
# 生成后需要手动优化
```

```python
# Playwright 运行模式
# headed=False：无头模式（CI用）
# headed=True：有头模式（本地调试）
# slow_mo=1000：慢动作（调试）
# video_dir：录像（调试）
# screenshot：截图（失败时）
```

```python
# Playwright 最佳实践
# 1. get_by_test_id选择器
# 2. expect()断言
# 3. fixture管理生命周期
# 4. 失败截图
# 5. codegen录制
```

```python
# Playwright vs Selenium
# Playwright：自动等待、快、现代
# Selenium：老牌、生态成熟
# 新项目：Playwright
# 老项目：Selenium
```

```python
# Playwright运行模式
# headed=False
# headed=True
# slow_mo
# video
# screenshot
```

```python
# Playwright选择器优先级
# testid
# role
# label
# text
# CSS
```

```python
# Playwright最佳实践
# testid
# expect
# fixture
```

```python
# Selenium vs Playwright
# 新项目：Playwright
# 老项目：Selenium
# 理由：自动等待快
```

```python
# Playwright选择器
# get_by_test_id
# get_by_role
# get_by_label
```

> 💡 **深度讲解**：Playwright 的自动等待（auto-waiting）是它比 Selenium 强大的关键。Playwright 会自动等待元素可交互（可见、稳定、可点击），不需要手动 `time.sleep()` 或 `WebDriverWait`。这让 E2E 测试更稳定、代码更简洁。

> 📝 **本章精简总结**：
> - 核心概念：Playwright、自动等待、选择器策略
> - 关键原理：浏览器自动化、模拟用户操作
> - 常用工具：playwright.sync_api、playwright.async_api
> - 最佳实践：用 testid 选择器、失败截图
> - 常见坑点：flaky test、选择器不稳定

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：Playwright 的自动等待是什么？
>   - 答案：自动等待元素可交互，不需要手动sleep
> - **进阶题（⭐⭐）**：哪种选择器最稳定？
>   - 思考方向：CSS class会变、testid最稳定
> - **实战题（⭐⭐⭐）**：用Playwright写一个完整的注册→登录E2E测试。
>   - 提示：playwright install + get_by_test_id

---

## 八、API E2E 测试（httpx）

### 8.1 httpx 基础

```python
# pip install httpx

import httpx
import pytest

# httpx 同步客户端
def test_api_health():
    client = httpx.Client(base_url="https://api.example.com")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# httpx 异步客户端
@pytest.mark.asyncio
async def test_api_health_async():
    async with httpx.AsyncClient(base_url="https://api.example.com") as client:
        response = await client.get("/health")
        assert response.status_code == 200
```

### 8.2 API 流程 E2E 测试

```python
# 用户完整流程 E2E 测试
class TestUserFlowE2E:
    """用户注册→登录→操作→注销 完整流程"""

    def test_full_user_flow(self):
        client = httpx.Client(base_url="https://api.example.com")

        # 1. 注册
        response = client.post("/auth/register", json={
            "email": "e2e_test@example.com",
            "password": "secure123"
        })
        assert response.status_code == 201
        user_id = response.json()["id"]

        # 2. 登录获取 token
        response = client.post("/auth/login", json={
            "email": "e2e_test@example.com",
            "password": "secure123"
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. 获取用户信息
        response = client.get(f"/users/{user_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == "e2e_test@example.com"

        # 4. 更新用户信息
        response = client.put(f"/users/{user_id}", json={
            "name": "E2E Test User"
        }, headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "E2E Test User"

        # 5. 删除用户
        response = client.delete(f"/users/{user_id}", headers=headers)
        assert response.status_code == 204
```

### 8.3 认证与会话管理

```python
# 带认证的 E2E 测试 fixture
import pytest

@pytest.fixture(scope="module")
def auth_client():
    """带认证的 API 客户端"""
    client = httpx.Client(base_url="https://api.example.com")

    # 登录获取 token
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "test123"
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    yield client
    client.close()

# 使用认证客户端
def test_get_profile(auth_client):
    response = auth_client.get("/users/me")
    assert response.status_code == 200
    assert "email" in response.json()
```

```python
# httpx 高级用法
import httpx
import pytest

# 超时配置
def test_with_timeout():
    client = httpx.Client(
        base_url="https://api.example.com",
        timeout=httpx.Timeout(
            connect=5.0,   # 连接超时5秒
            read=10.0,     # 读取超时10秒
            write=10.0,    # 写入超时10秒
            pool=5.0       # 连接池超时5秒
        )
    )

# 重试机制
def test_with_retry():
    transport = httpx.HTTPTransport(retries=3)
    client = httpx.Client(transport=transport)

# 请求历史
async def test_request_history():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://httpbin.org/redirect/1")
        # 重定向历史
        print(response.history)  # [302响应]
        print(response.url)      # 最终URL
```

```python
# API E2E 测试数据清理
@pytest.fixture(scope="module")
def api_client():
    """API 客户端 + 自动清理"""
    client = httpx.Client(base_url="https://api.example.com")
    created_ids = []

    # 登录
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "test123"
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    yield client, created_ids

    # 清理：删除所有创建的资源
    for resource_id in created_ids:
        client.delete(f"/api/items/{resource_id}")
    client.close()
```

```python
# API E2E 测试框架封装
class ApiE2ETest:
    """API E2E 测试基类"""

    def __init__(self, base_url: str):
        self.client = httpx.Client(base_url=base_url)

    def login(self, email: str, password: str):
        response = self.client.post("/auth/login", json={
            "email": email,
            "password": password
        })
        token = response.json()["access_token"]
        self.client.headers["Authorization"] = f"Bearer {token}"

    def create_user(self, email: str, name: str):
        response = self.client.post("/api/users", json={
            "email": email,
            "name": name
        })
        return response.json()

    def get_user(self, user_id: int):
        return self.client.get(f"/api/users/{user_id}").json()

    def cleanup(self):
        self.client.close()

# 使用
def test_user_flow():
    api = ApiE2ETest("https://api.example.com")
    api.login("test@example.com", "test123")
    user = api.create_user("new@test.com", "New User")
    assert user["email"] == "new@test.com"
    api.cleanup()
```

```python
# API E2E 测试 vs UI E2E 测试
# | 方面        | API E2E         | UI E2E          |
# |-------------|-----------------|-----------------|
# | 速度        | 极快（100ms）   | 慢（2-5s）      |
# | 稳定性      | 高              | 低              |
# | 维护成本    | 低              | 高              |
# | 覆盖范围    | 接口层          | 用户交互层      |
# 策略：API E2E 覆盖流程，UI E2E 覆盖关键路径
```

```python
# API E2E 最佳实践
# 1. 用 httpx.AsyncClient（异步更快）
# 2. 复用认证 token
# 3. 测试完整CRUD流程
# 4. 清理测试数据
# 5. 并行运行测试
# 6. 验证响应 schema
```

```python
# httpx 性能优化
# 1. 复用Client（不要每次创建）
# 2. 用异步Client
# 3. 设置合理超时
# 4. 连接池配置
```

```python
# httpx常见问题
# 问题1：超时 → 设置合理timeout
# 问题2：连接池耗尽 → 复用Client
# 问题3：认证 → headers设置
# 问题4：异步 → AsyncClient
```

```python
# httpx 请求技巧
# 1. GET：client.get(url, params={...})
# 2. POST：client.post(url, json={...})
# 3. PUT：client.put(url, json={...})
# 4. DELETE：client.delete(url)
# 5. 文件上传：client.post(url, files={...})
# 6. Headers：client.headers["X-Custom"] = "value"
```

```python
# httpx 高级特性
# 1. 重定向跟踪
# 2. Cookie管理
# 3. 代理支持
# 4. SSL验证
# 5. 压缩响应
# 6. 流式响应
```

```python
# httpx 超时配置
# connect=5s：连接超时
# read=10s：读取超时
# write=10s：写入超时
# pool=5s：连接池超时
# 推荐：合理超时，不要太长也不要太短
```

```python
# API E2E 最佳实践
# 1. httpx.AsyncClient
# 2. 复用认证token
# 3. 完整CRUD流程
# 4. 清理测试数据
# 5. 验证响应schema
```

```python
# API E2E vs UI E2E
# API E2E：快、稳、维护低
# UI E2E：慢、脆、维护高
# 策略：API覆盖流程，UI覆盖关键路径
```

```python
# httpx高级特性
# 重定向
# Cookie
# 代理
# SSL
# 压缩
# 流式
```

```python
# httpx请求
# GET
# POST
# PUT
# DELETE
```

```python
# API E2E最佳实践
# AsyncClient
# 复用token
# 完整CRUD
```

```python
# httpx vs requests
# httpx：异步支持
# requests：同步
# E2E用httpx
```

```python
# API E2E场景
# 注册→登录→下单→支付
# 完整业务流程
# 用httpx.AsyncClient
```

> 💡 **深度讲解**：API E2E 测试比 UI E2E 测试快10-100倍，而且更稳定。所以策略是：API 流程用 httpx E2E 覆盖，UI 流程用 Playwright 覆盖关键路径。两者结合，既快又稳。

> 📝 **本章精简总结**：
> - 核心概念：httpx、API流程测试
> - 关键原理：HTTP请求全链路验证
> - 常用工具：httpx.Client、httpx.AsyncClient
> - 最佳实践：认证fixture、完整CRUD流程
> - 常见坑点：忘记清理测试数据

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：API E2E 和 UI E2E 的区别？
>   - 答案：API测接口流程，UI测用户操作
> - **进阶题（⭐⭐）**：为什么API E2E比UI E2E好？
>   - 思考方向：速度、稳定性
> - **实战题（⭐⭐⭐）**：用httpx写一个完整的API E2E测试。
>   - 提示：注册→登录→操作→注销

---

## 九、测试数据管理

### 9.1 Factory Pattern

```python
# factories.py - 测试数据工厂
# pip install factory-boy

import factory
from factory.faker import faker

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n)
    email = factory.LazyAttribute(lambda obj: f"user_{obj.id}@example.com")
    name = factory.Faker("name")
    created_at = factory.LazyFunction(datetime.now)

# 使用工厂
def test_create_user():
    user = UserFactory()
    assert user.email == "user_0@example.com"
    assert "@" in user.email

# 创建不同变体
def test_admin_user():
    admin = UserFactory(role="admin")
    assert admin.role == "admin"
```

### 9.2 Fixture 管理测试数据

```python
# conftest.py
import pytest

@pytest.fixture(scope="function")
def test_user(db_session):
    """创建测试用户"""
    user = User(
        email="fixture@example.com",
        name="Fixture User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    # 清理
    db_session.delete(user)
    db_session.commit()

@pytest.fixture(scope="function")
def test_users(db_session):
    """创建多个测试用户"""
    users = [
        User(email=f"user_{i}@example.com", name=f"User {i}")
        for i in range(5)
    ]
    db_session.add_all(users)
    db_session.commit()
    yield users
```

### 9.3 测试数据隔离

```python
# 测试数据隔离策略
# 1. 每个测试函数独立数据（最严格）
# 2. 每个测试类共享数据（折中）
# 3. 每个测试会话共享数据（最快）

@pytest.fixture(scope="function")
def fresh_db(db_engine):
    """每个测试函数重建数据库"""
    Base.metadata.create_all(db_engine)
    yield
    Base.metadata.drop_all(db_engine)

@pytest.fixture(scope="class")
def class_db(db_engine):
    """每个测试类共享数据库"""
    Base.metadata.create_all(db_engine)
    yield
    Base.metadata.drop_all(db_engine)
```

```python
# factory-boy 高级用法
import factory
from factory.faker import faker
from models import User, Post, Comment

# 子工厂（关联对象）
class PostFactory(factory.Factory):
    class Meta:
        model = Post

    id = factory.Sequence(lambda n: n)
    title = factory.Faker("sentence")
    content = factory.Faker("paragraph")
    author = factory.SubFactory(UserFactory)  # 嵌套创建用户
    created_at = factory.LazyFunction(datetime.now)

# 多对多关系
class CommentFactory(factory.Factory):
    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    content = factory.Faker("text")

# 懒属性（依赖其他字段）
class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    item_count = 3
    unit_price = Decimal("99.99")
    total_price = factory.LazyAttribute(
        lambda o: o.unit_price * o.item_count
    )

# 使用
order = OrderFactory()
assert order.total_price == Decimal("299.97")
```

```python
# 测试数据清理策略
# 策略1：事务回滚（最快）
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# 策略2：删除所有数据（中等）
@pytest.fixture(autouse=True)
def clean_db(db_session):
    yield
    db_session.query(Comment).delete()
    db_session.query(Post).delete()
    db_session.query(User).delete()
    db_session.commit()

# 策略3：重建数据库（最慢最干净）
@pytest.fixture(scope="session")
def fresh_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
```

```python
# 测试数据工厂进阶
import factory
from factory.faker import faker
from factory.django import DjangoModelFactory  # Django项目

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)  # 避免重复创建

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.LazyAttribute(lambda obj: obj.email.split('@')[0])
    password = factory.PostGenerationMethodCall('set_password', 'test123')
    is_active = True

# 不同角色
class AdminFactory(UserFactory):
    is_staff = True
    is_superuser = True

# 批量创建
users = UserFactory.create_batch(10)  # 创建10个用户
```

```python
# 测试数据工厂高级技巧
# 1. 懒属性（依赖其他字段计算）
# 2. 子工厂（关联对象自动创建）
# 3. 后处理钩子（创建后修改）
# 4. 批量创建（create_batch）
# 5. 自定义策略（不同场景不同数据）

# 示例：订单工厂
class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    id = factory.Sequence(lambda n: n)
    user = factory.SubFactory(UserFactory)
    total = factory.LazyAttribute(lambda o: sum(i.price for i in o.items))
    status = "pending"

    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for item in extracted:
                self.items.append(item)
```

```python
# 测试数据管理最佳实践
# 1. 用 factory-boy 创建数据
# 2. 用事务回滚隔离测试
# 3. 不要手动准备数据
# 4. 测试数据要可读（不要随机生成无意义数据）
# 5. 批量创建用 create_batch
```

```python
# factory-boy 性能优化
# 1. 批量创建用 create_batch
# 2. session scope的关联对象
# 3. 不要在循环中创建工厂
# 4. 用 build() 代替 create()（不入库）
```

```python
# 测试数据常见问题
# 问题1：数据重复 → 工厂get_or_create
# 问题2：数据污染 → 事务回滚
# 问题3：数据太多 → 批量创建
# 问题4：数据不可读 → Faker生成有意义数据
```

```python
# factory-boy 数据质量
# 1. 用Faker生成真实数据
# 2. 数据要有业务意义
# 3. 边界值测试（空、最大、最小）
# 4. 异常数据测试（格式错误、越界）
# 5. 不要用随机数（要可复现）
```

```python
# 测试数据清理策略对比
# | 策略        | 速度 | 干净度 | 复杂度 | 推荐场景      |
# |-------------|------|--------|--------|---------------|
# | 事务回滚    | 极快 | 高     | 低     | 数据库测试    |
# | 删除数据    | 中   | 高     | 低     | 少量数据      |
# | 重建数据库  | 慢   | 极高   | 中     | CI/CD         |
```

```python
# 测试数据工厂最佳实践
# 1. 用Faker生成真实数据
# 2. 关联对象自动创建（SubFactory）
# 3. 批量创建用create_batch
# 4. 自定义变体（AdminFactory）
# 5. 不要硬编码测试数据
```

```python
# 测试数据管理最佳实践
# 1. factory-boy创建
# 2. 事务回滚隔离
# 3. 不要手动准备
# 4. 数据可读
# 5. 批量创建
```

```python
# 测试数据管理对比
# 事务回滚：快、隔离好
# 删除数据：中、干净
# 重建DB：慢、最干净
# 推荐：事务回滚
```

```python
# factory-boy数据质量
# Faker
# 业务意义
# 边界值
# 异常数据
```

```python
# factory-boy最佳实践
# Faker
# SubFactory
# create_batch
```

```python
# 测试数据最佳实践
# factory-boy
# 事务回滚
# 不手动
```

```python
# factory-boy最佳实践
# Faker真实
# SubFactory关系
# create_batch批量
```

```python
# 测试数据管理
# factory-boy
# Faker
# 事务回滚
# 独立DB
```

> 💡 **深度讲解**：测试数据管理是测试工程化的核心难题。最佳实践是"工厂模式 + 事务回滚"：用 factory-boy 快速创建测试数据，用事务回滚保证测试间隔离。不要手动准备测试数据，用工厂自动生成。

> 📝 **本章精简总结**：
> - 核心概念：Factory、Fixture、数据隔离
> - 关键原理：自动生成测试数据
> - 常用工具：factory-boy、pytest fixtures
> - 最佳实践：工厂模式、事务回滚
> - 常见坑点：测试间数据污染

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：为什么要用工厂模式创建测试数据？
>   - 答案：自动生成、可配置、减少重复代码
> - **进阶题（⭐⭐）**：测试数据隔离有哪些策略？
>   - 思考方向：function/class/session scope
> - **实战题（⭐⭐⭐）**：用factory-boy创建一个Order工厂。
>   - 提示：factory.Factory + SubFactory

---

## 十、测试环境管理

### 10.1 多环境配置

```python
# config/settings.py
import os
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class Settings:
    def __init__(self):
        self.env = os.getenv("APP_ENV", "development")
        self.debug = self.env == "development"

        if self.env == "testing":
            self.database_url = "sqlite:///:memory:"
            self.cache_url = "memory://"
            self.external_api_url = "https://test-api.example.com"
        elif self.env == "production":
            self.database_url = os.getenv("DATABASE_URL")
            self.cache_url = os.getenv("REDIS_URL")
            self.external_api_url = "https://api.example.com"

settings = Settings()
```

### 10.2 Docker Compose 测试环境

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test_db
    ports:
      - "5433:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"

  app:
    build: .
    environment:
      DATABASE_URL: postgresql://test:test@postgres:5432/test_db
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
```

```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行测试
pytest tests/integration/ -v

# 清理
docker-compose -f docker-compose.test.yml down -v
```

```python
# 环境变量管理
# .env.test
DATABASE_URL=postgresql://test:test@localhost:5433/test_db
REDIS_URL=redis://localhost:6380/0
DEBUG=true
EXTERNAL_API_URL=https://test-api.example.com
SECRET_KEY=test-secret-key

# 使用 python-dotenv
from dotenv import load_dotenv
import os

def load_test_env():
    load_dotenv(".env.test")
    return {
        "database_url": os.getenv("DATABASE_URL"),
        "redis_url": os.getenv("REDIS_URL"),
    }
```

```python
# 测试环境健康检查
def test_environment_healthy():
    """验证测试环境可用"""
    # 检查数据库
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

    # 检查 Redis
    import redis
    r = redis.from_url(settings.redis_url)
    assert r.ping()

    # 检查外部 API
    import httpx
    response = httpx.get(f"{settings.external_api_url}/health")
    assert response.status_code == 200
```

```python
# 测试环境启动脚本
#!/bin/bash
# scripts/test_env.sh

# 启动依赖
docker-compose -f docker-compose.test.yml up -d postgres redis

# 等待数据库就绪
echo "等待 PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U test; do
  sleep 1
done

# 运行迁移
echo "运行数据库迁移..."
alembic upgrade head

# 运行测试
echo "运行测试..."
pytest "$@"

# 清理
echo "清理..."
docker-compose -f docker-compose.test.yml down -v
```

```python
# 测试环境版本管理
# 确保本地、CI、生产使用相同版本：
# Python版本：.python-version 或 .tool-versions
# 依赖版本：requirements.txt 或 pyproject.toml
# 数据库版本：Dockerfile 或 docker-compose.yml
# Node版本（前端）：.nvmrc

# 锁定文件
# pip freeze > requirements-lock.txt
# poetry.lock
# 确保每次安装的依赖版本完全一致
```

```python
# 测试环境管理最佳实践
# 1. Docker Compose 一键启动
# 2. 环境变量配置
# 3. 健康检查等待依赖就绪
# 4. 测试后自动清理
# 5. 与生产环境版本一致
```

```python
# 测试环境启动时间优化
# 1. 预拉取Docker镜像
# 2. 用alpine版本
# 3. 缓存依赖
# 4. session scope的容器
```

```python
# 测试环境常见问题
# 问题1：本地CI不一致 → Docker Compose
# 问题2：启动慢 → 缓存镜像
# 问题3：端口冲突 → 自动分配端口
# 问题4：依赖没就绪 → 健康检查
```

```python
# 测试环境一致性检查
# 1. Python版本一致
# 2. 依赖版本一致（lock文件）
# 3. 数据库版本一致
# 4. 环境变量一致
# 5. 操作系统一致（CI用Linux）
```

```python
# 测试环境版本锁定
# requirements-lock.txt
# pytest==7.4.0
# pytest-cov==4.1.0
# testcontainers==3.7.0
# playwright==1.40.0
# httpx==0.25.0
```

```python
# 测试环境启动脚本
# scripts/test.sh
# docker-compose up -d postgres redis
# wait_for_postgres
# alembic upgrade head
# pytest "$@"
# docker-compose down -v
```

```python
# 测试环境管理最佳实践
# 1. Docker Compose
# 2. 环境变量
# 3. 健康检查
# 4. 自动清理
# 5. 版本一致
```

```python
# 测试环境一致性
# Python版本
# 依赖版本
# 数据库版本
# 环境变量
# 操作系统
```

```python
# 环境版本锁定
# Python版本
# 依赖版本
# 数据库版本
# 环境变量
```

```python
# 环境一致性
# Docker Compose
# 健康检查
# 自动清理
```

```python
# 测试环境最佳实践
# Docker Compose
# 环境变量
# 健康检查
```

```python
# 环境管理
# dev/test/prod
# 环境变量
# 配置中心
```

```python
# 环境管理最佳实践
# Docker Compose
# 环境变量
# 健康检查
# 版本锁定
```

> 💡 **深度讲解**：测试环境的核心原则是"与生产环境一致"。用 Docker Compose 启动完整的依赖（数据库、缓存、消息队列），确保集成测试在真实环境中运行。Testcontainers 是更轻量的替代——按需启动单个容器。

> 📝 **本章精简总结**：
> - 核心概念：多环境配置、Docker测试环境
> - 关键原理：测试环境与生产一致
> - 常用工具：Docker Compose、环境变量
> - 最佳实践：Docker Compose 一键启动测试环境
> - 常见坑点：本地环境与CI环境不一致

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：为什么测试环境要与生产一致？
>   - 答案：避免"本地通过但CI失败"
> - **进阶题（⭐⭐）**：Docker Compose 测试环境的优势？
>   - 思考方向：一键启动、版本一致
> - **实战题（⭐⭐⭐）**：写一个Docker Compose测试环境配置。
>   - 提示：postgres + redis + app

---

## 十一、CI/CD 中的集成测试

### 11.1 GitHub Actions 集成测试

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
        run: pytest tests/integration/ -v --cov=app
```

### 11.2 测试分层执行策略

```yaml
# 分层测试策略
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/unit/ -v

  integration-tests:
    needs: unit-tests
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/integration/ -v

  e2e-tests:
    needs: integration-tests
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/e2e/ -v
```

**策略**：
- 单元测试：每次提交都跑（快）
- 集成测试：PR 时跑（中速）
- E2E 测试：每晚跑（慢）

### 11.3 测试报告

```python
# pytest 测试报告生成
# pytest --html=report.html --self-contained-html
# pytest --junitxml=report.xml

# 覆盖率报告
# pytest --cov=app --cov-report=html --cov-report=term
```

```yaml
# GitHub Actions 上传测试报告
- name: Upload test results
  uses: actions/upload-artifact@v3
  with:
    name: test-report
    path: report.html
```

```yaml
# 完整的 GitHub Actions 测试流水线
name: Test Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements-dev.txt
      - run: flake8 app/ tests/
      - run: pytest tests/unit/ -v --cov=app --cov-report=xml

  integration:
    needs: lint-and-unit
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements-dev.txt
      - env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
        run: pytest tests/integration/ -v

  e2e-nightly:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest tests/e2e/ -v
```

```python
# 测试覆盖率目标
# 单元测试覆盖率目标：80%+
# 集成测试覆盖率目标：60%+
# 关键路径覆盖率：100%

# 覆盖率排除配置
# .coveragerc
[run]
source = app
omit =
    app/migrations/*
    app/tests/*
    app/__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
```

```yaml
# 测试报告通知
- name: Notify test results
  uses: slackapi/slack-github-action@v1
  if: always()
  with:
    slack-message: |
      *测试结果*
      单元测试: ${{ job.status }}
      集成测试: ...
      E2E测试: ...
```

```python
# CI/CD 测试缓存
# GitHub Actions 缓存依赖
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# 缓存测试结果
- uses: actions/cache@v3
  with:
    path: .pytest_cache
    key: ${{ runner.os }}-pytest-${{ github.sha }}
```

```python
# CI/CD 测试最佳实践
# 1. 分层执行（单元→集成→E2E）
# 2. 缓存依赖加速
# 3. 测试失败立即通知
# 4. 上传测试报告
# 5. nightly跑E2E
```

```python
# CI/CD 测试时间优化
# 1. 并行化测试
# 2. 缓存依赖和测试结果
# 3. 只跑受影响的测试（smart testing）
# 4. 分层执行（先跑快的）
# 5. E2E nightly跑
```

```python
# CI/CD常见问题
# 问题1：测试太慢 → 并行化+分层
# 问题2：测试不稳定 → 修复flaky
# 问题3：缓存不生效 → 正确配置key
# 问题4：报告不清晰 → HTML报告
```

```python
# CI/CD 测试策略总结
# 1. PR触发：单元测试 + 集成测试
# 2. 合并main：全量测试 + 部署到staging
# 3. nightly：E2E + 性能测试
# 4. release：全量测试 + 生产部署
```

```python
# CI/CD 测试时间分解
# 单元测试：1分钟
# 集成测试：5分钟
# E2E测试：10分钟
# 总计：16分钟（串行）
# 并行后：6分钟

# 优化方向：
# 1. 并行化
# 2. 减少E2E
# 3. 缓存依赖
# 4. 分层执行
```

```python
# CI/CD 测试缓存
# 1. pip缓存
# 2. 测试结果缓存
# 3. Docker镜像缓存
# 4. 二进制依赖缓存
# 目标：减少重复工作
```

```python
# CI/CD 测试最佳实践
# 1. 分层执行
# 2. 缓存依赖
# 3. 失败通知
# 4. 测试报告
# 5. nightly跑E2E
```

```python
# CI/CD分层策略
# PR：单元+集成
# main：全量+staging
# nightly：E2E+性能
# release：全量+生产
```

```python
# CI/CD测试时间
# 单元：1min
# 集成：5min
# E2E：10min
# 优化：并行化
```

```python
# CI/CD缓存
# pip缓存
# 测试结果
# Docker镜像
```

```python
# CI/CD最佳实践
# 分层执行
# 缓存
# 失败通知
```

```python
# CI/CD流程
# PR触发
# main触发
# nightly
# release
```

```python
# CI/CD分层策略
# PR：单元+集成
# main：全量
# nightly：E2E+性能
```

> 💡 **深度讲解**：CI/CD 中的测试策略是"快速反馈"——每次提交都跑单元测试（秒级），PR 时跑集成测试（分钟级）， nightly 跑 E2E 测试（小时级）。这样开发者能快速知道是否破坏了什么，同时不会被慢测试阻塞。

> 📝 **本章精简总结**：
> - 核心概念：CI/CD、分层测试、快速反馈
> - 关键原理：按测试类型分层执行
> - 常用工具：GitHub Actions、pytest
> - 最佳实践：单元每次跑、集成PR跑、E2E nightly跑
> - 常见坑点：所有测试一起跑太慢

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：CI/CD 中测试分层策略？
>   - 答案：单元每次跑、集成PR跑、E2E nightly跑
> - **进阶题（⭐⭐）**：为什么不应该每次都跑E2E测试？
>   - 思考方向：速度、反馈时间
> - **实战题（⭐⭐⭐）**：写一个GitHub Actions集成测试workflow。
>   - 提示：postgres service + pytest

---

## 十二、测试并行化

### 12.1 pytest-xdist 并行测试

```bash
# 安装
pip install pytest-xdist

# 并行运行（4个worker）
pytest -n 4

# 自动检测CPU核数
pytest -n auto

# 并行 + 按类型
pytest tests/integration/ -n 4
```

### 12.2 并行测试注意事项

```python
# 并行测试的挑战
# 1. 测试间不能共享状态
# 2. 数据库连接数要够
# 3. 文件系统冲突

# 解决方案：
# 1. 每个worker独立数据库（不同schema/数据库名）
# 2. 使用 Testcontainers（每个worker独立容器）
# 3. 用唯一前缀避免文件冲突

# conftest.py
import os

@pytest.fixture(scope="session")
def db_name():
    """每个worker独立数据库"""
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "master")
    return f"test_db_{worker_id}"
```

```python
# pytest-xdist 并行配置
# pytest.ini
[pytest]
addopts = -n auto --dist=loadfile

# --dist=loadfile：按文件分配worker（同文件测试在同一worker）
# --dist=loadgroup：按标记分组

# 并行测试的 fixtures
@pytest.fixture(scope="session")
def unique_db_name():
    """每个worker唯一的数据库名"""
    import os
    worker = os.getenv("PYTEST_XDIST_WORKER", "main")
    return f"test_db_{worker}"

@pytest.fixture(scope="session")
def db_engine(unique_db_name):
    """为每个worker创建独立数据库"""
    # 先创建数据库
    admin_engine = create_engine("postgresql://test:test@localhost/postgres")
    admin_engine.execute(f"CREATE DATABASE {unique_db_name}")

    # 连接到新数据库
    engine = create_engine(f"postgresql://test:test@localhost/{unique_db_name}")
    Base.metadata.create_all(engine)
    yield engine
    # 清理
    engine.dispose()
    admin_engine.execute(f"DROP DATABASE {unique_db_name}")
```

```python
# 并行测试常见问题
# 问题1：端口冲突
# 解决方案：每个worker用不同端口
# 问题2：文件冲突
# 解决方案：用 worker_id 作为前缀
# 问题3：数据库冲突
# 解决方案：每个worker独立数据库
# 问题4：外部API限流
# 解决方案：减少并发或Mock外部API
```

```python
# 并行测试性能对比
# 测试套件：1000个测试
# 串行执行：100秒
# 并行4worker：30秒（加速3.3倍）
# 并行8worker：18秒（加速5.5倍）
# 注意：加速比不是线性的，因为有fixture开销

# 并行测试最佳worker数
# CPU密集型：= CPU核数
# IO密集型：= CPU核数 × 2
# 数据库密集型：= 连接池大小 / 每连接测试数
```

```python
# 并行测试数据库隔离策略
# 策略1：每个worker独立数据库（推荐）
# 策略2：每个worker独立schema
# 策略3：每个worker独立表前缀
# 策略4：串行跑数据库测试（不并行）

# 策略1实现（推荐）
@pytest.fixture(scope="session")
def db_url(worker_id):
    db_name = f"test_{worker_id}"
    # 创建数据库
    admin_conn = psycopg2.connect("postgresql:///postgres")
    admin_conn.autocommit = True
    admin_conn.cursor().execute(f"CREATE DATABASE {db_name}")
    return f"postgresql:///{db_name}"
```

```python
# 并行测试最佳实践
# 1. 测试必须隔离
# 2. 每个worker独立数据库
# 3. 用 -n auto 自动检测CPU
# 4. 不要并行跑E2E（资源冲突）
# 5. 并行跑单元+集成测试
```

```python
# 并行测试时间优化
# 1. 按文件分组（同文件在同一worker）
# 2. 长测试分散到不同worker
# 3. session scope的fixture复用
# 4. 不要并行跑E2E
```

```python
# 并行测试常见问题
# 问题1：测试间冲突 → 独立数据库
# 问题2：连接数不够 → 连接池配置
# 问题3：端口冲突 → 自动分配
# 问题4：fixture冲突 → 调整scope
```

```python
# 并行测试效果
# 测试套件：1000个测试，串行100秒
# 4worker并行：30秒（3.3倍加速）
# 8worker并行：18秒（5.5倍加速）
# 注意：加速比不是线性的
```

```python
# 并行测试最佳worker数
# CPU密集型：= CPU核数
# IO密集型：= CPU核数 × 2
# 数据库密集型：= 连接池大小
# 推荐：-n auto（自动检测）
```

```python
# 并行测试策略
# 1. 按文件分组
# 2. 每个worker独立数据库
# 3. 长测试分散
# 4. session fixture复用
# 5. 不并行跑E2E
```

```python
# 并行测试最佳实践
# 1. 测试隔离
# 2. 独立数据库
# 3. -n auto
# 4. 不并行E2E
# 5. 并行单元+集成
```

```python
# 并行测试效果
# 串行：100s
# 4worker：30s
# 8worker：18s
# 加速比不是线性的
```

```python
# 并行worker数
# CPU密集：=核数
# IO密集：=核数×2
# DB密集：=连接池
```

```python
# 并行策略
# 按文件分组
# 独立数据库
# session fixture
```

```python
# 并行最佳实践
# 独立DB
# -n auto
# 不并行E2E
```

```python
# 并行化收益
# 串行100s → 并行20s
# 加速比5x
# 注意隔离
```

```python
# 并行测试策略
# -n auto
# 独立DB
# 不并行E2E
```

> 💡 **深度讲解**：并行化是测试提速的最有效手段。但并行化的前提是测试隔离——测试之间不能共享状态。如果测试共享数据库，就需要给每个 worker 独立的数据库。Testcontainers 天然适合并行化，因为每个测试可以启动自己的容器。

> 📝 **本章精简总结**：
> - 核心概念：pytest-xdist、并行执行
> - 关键原理：多worker同时跑测试
> - 常用工具：pytest -n auto
> - 最佳实践：测试隔离、独立数据库
> - 常见坑点：测试间共享状态导致flaky

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：pytest-xdist 的作用？
>   - 答案：并行运行测试，加速测试
> - **进阶题（⭐⭐）**：并行测试的前提条件？
>   - 思考方向：测试隔离
> - **实战题（⭐⭐⭐）**：配置并行测试并解决数据库冲突。
>   - 提示：每个worker独立数据库

---

## 十三、测试稳定性与 Flaky Test

### 13.1 什么是 Flaky Test

Flaky Test 是"有时通过有时失败"的测试——同一代码、同一环境，结果不确定。

**常见原因**：
- 依赖执行顺序
- 时间相关（datetime.now()）
- 网络不稳定
- 并发竞争
- 硬编码 sleep

### 13.2 识别与处理 Flaky Test

```python
# 标记 flaky 测试
@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_unreliable():
    # 偶尔失败的测试
    assert random.random() > 0.5

# 跳过已知问题
@pytest.mark.skip(reason="等待API修复")
def test_external_api():
    ...

# 条件跳过
@pytest.mark.skipif(sys.platform == "win32", reason="不支持Windows")
def test_unix_only():
    ...
```

```python
# 消除 flaky test 的方法

# ❌ 不好：硬编码 sleep
def test_bad():
    page.click("#load-data")
    time.sleep(2)  # 不确定等多久
    assert page.text_content("#result") == "data"

# ✅ 好：等待元素
def test_good():
    page.click("#load-data")
    page.wait_for_selector("#result")  # 等元素出现
    assert page.text_content("#result") == "data"
```

### 13.3 测试隔离最佳实践

```python
# 测试隔离检查清单
# ✅ 每个测试函数独立数据
# ✅ 每个测试函数独立事务
# ✅ 不依赖执行顺序
# ✅ 不使用全局状态
# ✅ 时间相关用 mock
# ✅ 随机数用固定种子
# ✅ 外部API用mock
```

```python
# Flaky Test 检测与统计
# pytest-rerunfailures 插件
# pip install pytest-rerunfailures

# 自动重试失败的测试
# pytest --reruns 3 --reruns-delay 1

# 标记特定测试需要重试
@pytest.mark.flaky(reruns=5, reruns_delay=2)
def test_network_call():
    response = requests.get("https://api.example.com")
    assert response.status_code == 200

# 统计 flaky test
# pytest --reruns 3 -v | grep "RERUN"
# 频繁 RERUN 的测试就是 flaky test
```

```python
# 消除 Flaky Test 的实战技巧

# 技巧1：固定时间
# ❌ 不好
def test_time_dependent():
    assert datetime.now().hour > 9  # 晚上跑就失败

# ✅ 好
def test_time_dependent(mocker):
    mock_dt = mocker.patch("datetime.datetime")
    mock_dt.now.return_value = datetime(2026, 1, 1, 10, 0)
    assert datetime.now().hour == 10

# 技巧2：固定随机种子
# ❌ 不好
def test_random():
    result = random.sample(range(100), 5)
    assert len(result) == 5

# ✅ 好
def test_random(mocker):
    mocker.patch("random.sample", return_value=[1, 2, 3, 4, 5])
    result = random.sample(range(100), 5)
    assert result == [1, 2, 3, 4, 5]

# 技巧3：等待元素而非sleep
# ❌ 不好
time.sleep(2)
assert page.text == "loaded"

# ✅ 好
page.wait_for_selector(".loaded")
assert page.text == "loaded"
```

```python
# 测试稳定性度量
# Flaky率 = 失败后重试成功的测试数 / 总测试数
# 目标：< 1%

# 监控 flaky test
# pytest --reruns 3 -v | grep "RERUN"
# 统计每个测试的 flaky 率

# 常见 flaky test 来源：
# 1. 时间依赖（占40%）
# 2. 网络不稳定（占25%）
# 3. 并发竞争（占20%）
# 4. 执行顺序依赖（占15%）
```

```python
# Flaky Test 处理流程
# 1. 发现：测试有时通过有时失败
# 2. 复现：多次运行，确认是flaky
# 3. 定位：看失败日志，找原因
# 4. 修复：
#    - 时间问题 → Mock时间
#    - 网络问题 → Mock外部API
#    - 并发问题 → 加锁或串行化
#    - 顺序问题 → 确保测试隔离
# 5. 验证：多次运行都通过
# 6. 删除：修复不了的测试删除
```

```python
# Flaky Test 最佳实践
# 1. 发现flaky就修复，不要重试
# 2. 用 wait_for 替代 sleep
# 3. Mock时间和随机数
# 4. 确保测试隔离
# 5. 修复不了的测试删除
```

```python
# Flaky Test 监控指标
# 1. Flaky率：flaky测试数/总测试数
# 2. 重试次数：平均重试次数
# 3. 失败模式：失败原因分类
# 4. 趋势：flaky率随时间变化
```

```python
# Flaky Test常见问题
# 问题1：时间依赖 → Mock时间
# 问题2：网络不稳定 → Mock外部API
# 问题3：并发竞争 → 串行化或加锁
# 问题4：执行顺序 → 确保隔离
```

```python
# Flaky Test 预防策略
# 1. 写测试前思考：有哪些不确定性？
# 2. Mock所有时间相关代码
# 3. Mock所有随机数
# 4. Mock所有外部API
# 5. 确保测试间无共享状态
# 6. 用 wait_for 替代 sleep
```

```python
# Flaky Test 统计
# 假设：1000个测试
# Flaky：10个（1%）
# 每次运行：10个随机失败
# 开发体验：差（不知道是真失败还是flaky）
# 解决：修复flaky，降低到<1%
```

```python
# Flaky Test 处理流程
# 1. 发现flaky
# 2. 多次运行复现
# 3. 看失败日志定位
# 4. 修复或删除
# 5. 验证稳定
# 6. 防止再次出现
```

```python
# Flaky Test 最佳实践
# 1. 发现就修复
# 2. wait_for替代sleep
# 3. Mock时间随机数
# 4. 确保隔离
# 5. 修复不了就删除
```

```python
# Flaky率监控
# 目标：<1%
# 统计：flaky/总数
# 趋势：随时间下降
```

```python
# Flaky统计
# 1000测试
# 10个flaky
# 1%率
```

```python
# Flaky处理流程
# 发现
# 复现
# 定位
# 修复
```

```python
# Flaky最佳实践
# wait_for
# Mock时间
# 隔离
```

```python
# Flaky统计
# 1000测试中
# 10个flaky
# 1%率
```

```python
# Flaky Test预防
# wait_for替代sleep
# Mock时间
# 确保隔离
```

> 💡 **深度讲解**：Flaky Test 是测试工程化的最大敌人。一个 flaky test 会让团队失去对测试的信任，最终所有人都忽略失败的测试——这比没有测试还糟糕。处理 flaky test 的原则：不是"重试"，而是"修复"或"删除"。

> 📝 **本章精简总结**：
> - 核心概念：Flaky Test、测试稳定性
> - 关键原理：消除不确定性
> - 常用工具：pytest.mark.flaky、wait_for
> - 最佳实践：测试隔离、不硬编码sleep
> - 常见坑点：flaky test导致团队不信任测试

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：什么是 flaky test？
>   - 答案：有时通过有时失败的测试
> - **进阶题（⭐⭐）**：flaky test 的常见原因？
>   - 思考方向：时间、网络、并发、执行顺序
> - **实战题（⭐⭐⭐）**：修复一个 flaky 的 E2E 测试。
>   - 提示：用 wait_for 替代 sleep

---

## 十四、性能测试基础

### 14.1 性能测试类型

```python
# 性能测试类型
# 1. 负载测试（Load Testing）：模拟预期用户量
# 2. 压力测试（Stress Testing）：超出预期，找极限
# 3. 浸泡测试（Soak Testing）：长时间运行，找内存泄漏
# 4.  Spike 测试：突然流量激增

# 工具：locust、k6、JMeter
```

### 14.2 Locust 性能测试

```python
# locustfile.py
# pip install locust
# locust -f locustfile.py

from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # 每个操作间隔1-3秒

    @task
    def index_page(self):
        self.client.get("/")

    @task(3)  # 权重3倍
    def view_products(self):
        self.client.get("/api/products")

    @task
    def search_product(self):
        self.client.get("/api/products?search=phone")

    def on_start(self):
        """模拟用户登录"""
        self.client.post("/api/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
```

```bash
# 运行 locust
# locust -f locustfile.py --host=http://localhost:8000
# 打开 http://localhost:8089 设置并发用户数

# 无UI模式
# locust -f locustfile.py --host=http://localhost:8000 \
#   --users 100 --spawn-rate 10 --run-time 60s
```

```python
# Locust 高级用法
from locust import HttpUser, task, between, events
import logging

# 自定义用户行为
class AdvancedUser(HttpUser):
    wait_time = between(1, 3)
    abstract = True  # 抽象基类，不直接运行

    def login(self):
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
        self.token = response.json()["access_token"]
        self.client.headers["Authorization"] = f"Bearer {self.token}"

class GuestUser(AdvancedUser):
    @task
    def browse(self):
        self.client.get("/")

    @task(2)
    def search(self):
        self.client.get("/api/products?search=phone")

class LoggedInUser(AdvancedUser):
    def on_start(self):
        self.login()

    @task
    def view_orders(self):
        self.client.get("/api/orders")

    @task
    def checkout(self):
        self.client.post("/api/checkout", json={"cart_id": 1})
```

```python
# 性能指标监控
# 关键指标：
# 1. 响应时间：p50（中位数）、p95、p99
# 2. 吞吐量：每秒请求数（RPS）
# 3. 错误率：失败请求占比
# 4. 并发用户数

# 性能基线示例：
# 首页：p95 < 200ms, RPS > 1000
# 搜索：p95 < 500ms, RPS > 500
# 下单：p95 < 1s, RPS > 100
# 错误率 < 0.1%
```

```python
# 性能测试结果分析
# Locust 输出示例：
# Type     Name                # reqs  # fails  Avg     Min     Max     Median  Req/s
# -------- ------------------  ------ ------- ------- ------- ------- ------- ------
# GET      /                   1000   0       50ms    10ms    200ms   45ms    100
# GET      /api/products       800    0       80ms    20ms    300ms   70ms    80
# POST     /api/checkout       200    2       150ms   50ms    500ms   140ms   20

# 分析：
# - 首页 p95 < 200ms ✓
# - 产品列表 p95 < 300ms ✓
# - 结账 0.1% 错误率 ⚠️ 需要关注
```

```python
# 性能测试 vs 功能测试
# 功能测试：验证"做对了吗？"
# 性能测试：验证"做快了吗？"

# 功能测试：
# assert response.status_code == 200
# assert data["id"] == 1

# 性能测试：
# assert response.elapsed.total_seconds() < 0.5  # p95 < 500ms
```

```python
# 性能测试最佳实践
# 1. 建立性能基线
# 2. 监控 p50/p95/p99
# 3. 每次发版对比基线
# 4. 性能退化告警
# 5. 用 Locust/k6 做负载测试
```

```python
# 性能测试持续监控
# 1. 每次发版跑性能测试
# 2. 对比性能基线
# 3. 性能退化告警
# 4. 监控p95响应时间
# 5. 监控错误率
```

```python
# 性能测试常见问题
# 问题1：不知道测什么 → 关键API端点
# 问题2：不知道标准 → 业务需求定义SLA
# 问题3：测试不稳定 → 固定环境
# 问题4：结果难分析 → 监控p95/p99
```

```python
# 性能测试场景设计
# 1. 基准测试：单用户正常操作
# 2. 负载测试：预期用户量
# 3. 压力测试：超出预期，找极限
# 4. 浸泡测试：长时间运行，找泄漏
# 5. Spike测试：突然流量激增
```

```python
# 性能测试SLA示例
# 首页加载：p95 < 200ms
# API查询：p95 < 500ms
# 下单流程：p95 < 1s
# 搜索：p95 < 800ms
# 错误率：< 0.1%
# RPS：> 100
```

```python
# 性能测试工具对比
# | 工具    | 语言 | 特点              |
# |---------|------|-------------------|
# | Locust  | Python | Python脚本，灵活 |
# | k6      | JS   | 现代，轻量        |
# | JMeter  | Java | 老牌，GUI         |
# 推荐：Python项目用Locust
```

```python
# 性能测试最佳实践
# 1. 建立基线
# 2. 监控p95/p99
# 3. 每次发版对比
# 4. 性能退化告警
# 5. Locust/k6
```

```python
# 性能测试持续监控
# 每次发版跑
# 对比基线
# 退化告警
# p95监控
```

```python
# 性能SLA
# 首页：p95<200ms
# API：p95<500ms
# 下单：p95<1s
```

```python
# 性能测试类型
# 负载
# 压力
# 浸泡
# Spike
```

```python
# 性能最佳实践
# Locust
# SLA
# 持续监控
```

```python
# 性能监控
# p50
# p95
# p99
# 均值
```

```python
# 性能测试SLA
# p95 < 500ms
# p99 < 1s
# 错误率 < 0.1%
```

> 💡 **深度讲解**：性能测试不是"测一下快不快"，而是"建立性能基线"。关键指标：响应时间（p50/p95/p99）、吞吐量（RPS）、错误率。每次发版对比性能基线，确保没有性能退化。

> 📝 **本章精简总结**：
> - 核心概念：负载测试、压力测试、性能基线
> - 关键原理：模拟真实用户负载
> - 常用工具：locust、k6
> - 最佳实践：建立性能基线、监控关键指标
> - 常见坑点：不测就上线，性能问题线上才发现

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：性能测试有哪些类型？
>   - 答案：负载、压力、浸泡、Spike
> - **进阶题（⭐⭐）**：为什么要建立性能基线？
>   - 思考方向：性能退化检测
> - **实战题（⭐⭐⭐）**：用locust写一个API性能测试。
>   - 提示：HttpUser + @task

---

## 十五、最佳实践与常见坑点

### 15.1 测试最佳实践清单

```python
# 测试最佳实践

# 1. 命名规范
# ✅ test_should_return_error_when_email_invalid
# ❌ test_email

# 2. Arrange-Act-Assert 模式
def test_calculate_total():
    # Arrange
    cart = Cart()
    cart.add(Item(price=100))
    cart.add(Item(price=50))

    # Act
    total = cart.calculate_total()

    # Assert
    assert total == 150

# 3. 每个测试只测一件事
# ✅ 一个测试一个断言主题
# ❌ 一个测试测所有功能

# 4. 测试公共行为，不测试实现细节
# ✅ test_create_user_returns_201
# ❌ test_create_user_calls_insert
```

### 15.2 常见坑点

```python
# 常见坑点速查

# 坑1：测试实现细节而非行为
# ❌ 测试内部调用了什么方法
# ✅ 测试输入输出是什么

# 坑2：过度Mock
# ❌ Mock太多，测试变成"测试Mock"
# ✅ 只Mock外部依赖

# 坑3：测试间共享状态
# ❌ 模块级变量
# ✅ 每个测试独立fixture

# 坑4：不清理测试数据
# ❌ 测试残留数据影响下个测试
# ✅ fixture yield后清理

# 坑5：忽略测试失败
# ❌ "偶尔失败不管它"
# ✅ flaky test必须修复或删除

# 坑6：测试太复杂
# ❌ 测试代码比业务代码还长
# ✅ 简洁、清晰、可读
```

### 15.3 面试高频考点

```python
# 面试考点速答

# Q1: 测试金字塔是什么？
# A: 单元测试多、集成测试中、E2E测试少

# Q2: Mock的原则？
# A: Mock外部依赖，测试自己的代码

# Q3: 如何处理flaky test？
# A: 修复或删除，不要重试

# Q4: 集成测试和单元测试的区别？
# A: 集成测试用真实依赖，单元测试Mock所有

# Q5: CI/CD中测试策略？
# A: 单元每次跑、集成PR跑、E2E nightly跑

# Q6: 如何加速测试？
# A: 并行化（pytest-xdist）、减少E2E、用内存数据库

# Q7: Testcontainers的作用？
# A: 用Docker容器运行真实依赖做集成测试

# Q8: 测试数据管理最佳实践？
# A: 工厂模式 + 事务回滚隔离
```

```python
# 测试代码审查清单
# 命名规范
# ✅ test_should_return_404_when_user_not_found
# ❌ test_user_not_found

# 结构规范
# ✅ Arrange-Act-Assert 三段式
# ❌ 混合在一起

# 断言规范
# ✅ 精确断言：assert result == 42
# ❌ 模糊断言：assert result is not None

# Mock规范
# ✅ 只Mock外部依赖
# ❌ Mock自己的业务逻辑

# 数据规范
# ✅ 工厂创建数据
# ❌ 硬编码数据

# 隔离规范
# ✅ 每个测试独立数据
# ❌ 共享全局状态
```

```python
# 测试反模式（Anti-patterns）

# 反模式1：巨型测试
# ❌ 一个测试测所有功能
def test_everything():
    # 注册
    # 登录
    # 加购
    # 下单
    # 支付
    ...

# ✅ 拆分成多个小测试
def test_registration(): ...
def test_login(): ...
def test_checkout(): ...

# 反模式2：测试实现细节
# ❌ 测试内部方法被调用
def test_internal_method_called():
    spy = mocker.spy(service, "_private_method")
    service.do_work()
    spy.assert_called_once()

# ✅ 测试行为结果
def test_do_work_returns_expected():
    result = service.do_work()
    assert result == expected

# 反模式3：过度Mock
# ❌ Mock太多，测试无意义
def test_service():
    mock_a = Mock()
    mock_b = Mock()
    mock_c = Mock()
    # 全是Mock，测试什么？
```

```python
# 面试题：如何设计一个测试策略？
# 答案框架：
# 1. 识别核心业务流程
# 2. 确定测试金字塔比例（80/15/5）
# 3. 选择测试工具（pytest、Testcontainers、Playwright）
# 4. 设计测试数据管理（工厂+事务）
# 5. 规划CI/CD集成（分层执行）
# 6. 建立监控（覆盖率、flaky统计）
# 7. 持续改进（定期审查测试质量）
```

```python
# 测试最佳实践速查表
# | 场景              | 推荐做法              | 避免              |
# |-------------------|-----------------------|-------------------|
# | 业务逻辑          | 单元测试              | E2E测试           |
# | 数据库交互        | 集成测试(Testcontainers)| SQLite           |
# | API端点           | 集成测试(TestClient)  | 手动测试          |
# | 用户流程          | E2E(Playwright)       | 太多E2E           |
# | 外部依赖          | Mock                  | 真实调用          |
# | 测试数据          | 工厂模式              | 硬编码            |
# | 测试隔离          | 事务回滚              | 共享状态          |
# | 并行化            | pytest-xdist          | 共享数据库        |
# | CI/CD            | 分层执行              | 全量跑            |
```

```python
# 测试代码质量度量
# 1. 测试覆盖率：多少代码被测试执行
# 2. 测试密度：每行生产代码有多少测试代码
# 3. Flaky率：多少测试不稳定
# 4. 运行时间：测试套件跑多久
# 5. 通过率：多少测试通过

# 目标值：
# 覆盖率：>80%
# 测试密度：1:1（1行生产代码配1行测试）
# Flaky率：<1%
# 运行时间：<5分钟（本地）
# 通过率：100%
```

```python
# 面试题：集成测试中如何处理数据库？
# 答案框架：
# 1. 测试环境用真实数据库（Testcontainers）
# 2. 每个测试独立事务，结束后回滚
# 3. 用工厂模式创建测试数据
# 4. 测试约束和索引
# 5. 并行测试用独立数据库
```

```python
# 测试团队协作
# 1. 测试代码和业务代码同仓库
# 2. 测试代码也要code review
# 3. 新功能必须配测试
# 4. Bug修复必须配回归测试
# 5. 定期审查测试质量
```

```python
# 测试反模式速查
# 1. 巨型测试 → 拆分成多个小测试
# 2. 测试实现细节 → 测试行为结果
# 3. 过度Mock → 只Mock外部依赖
# 4. 共享状态 → 每个测试独立
# 5. 忽略失败 → flaky必须修复
# 6. 测试太复杂 → 简洁可读
# 7. 覆盖率执念 → 质量>数量
# 8. 手动测试为主 → 自动化关键路径
```

```python
# 测试工程化检查清单
# [ ] 测试金字塔比例合理（80/15/5）
# [ ] 测试隔离（无共享状态）
# [ ] 测试数据工厂化
# [ ] CI/CD分层执行
# [ ] Flaky率<1%
# [ ] 覆盖率>80%
# [ ] 并行化加速
# [ ] 测试报告清晰
# [ ] 失败自动通知
# [ ] 定期审查测试质量
```

```python
# 测试质量度量指标
# 1. 测试通过率：>99%
# 2. Flaky率：<1%
# 3. 覆盖率：>80%
# 4. 运行时间：<5分钟（本地）
# 5. 测试密度：1:1
```

```python
# 测试最佳实践总结
# 1. 测试行为不测试实现
# 2. 每个测试只测一件事
# 3. AAA模式
# 4. 测试隔离
# 5. 工厂模式创建数据
# 6. Mock外部依赖
# 7. 定期审查测试质量
```

```python
# 测试最佳实践总结
# 1. AAA模式
# 2. 测试行为
# 3. 测试隔离
# 4. 工厂数据
# 5. Mock边界
# 6. CI分层
# 7. 并行化
# 8. 修复flaky
```

```python
# 测试代码质量
# 测试覆盖率
# 测试密度
# Flaky率
# 运行时间
# 通过率
```

```python
# 测试质量度量
# 通过率：>99%
# Flaky率：<1%
# 覆盖率：>80%
```

```python
# 最佳实践清单
# AAA
# 测试行为
# 测试隔离
```

```python
# 最佳实践总结
# AAA
# 行为
# 隔离
# 工厂
# CI分层
# 并行
# 修复flaky
```

```python
# 测试度量
# 通过率
# Flaky率
# 覆盖率
# 运行时间
```

```python
# 最佳实践清单
# AAA模式
# 测试行为
# 测试隔离
```

> 💡 **深度讲解**：好的测试不是"写得多"，而是"写得准"。一个测试只验证一件事，命名清晰、结构规范、隔离干净。测试代码也是代码——需要维护、需要评审、需要重构。把测试当一等公民对待，测试质量自然就上来了。

> 📝 **本章精简总结**：
> - 核心概念：最佳实践、常见坑点
> - 关键原理：测试质量=代码质量
> - 常用工具：pytest、Testcontainers、Playwright
> - 最佳实践：AAA模式、测试行为不测试实现、保持隔离
> - 常见坑点：过度Mock、flaky test、忽略失败

> 🎯 **梯度练习题**：
> - **基础题（⭐）**：AAA模式是什么？
>   - 答案：Arrange-Act-Assert
> - **进阶题（⭐⭐）**：为什么不要测试实现细节？
>   - 思考方向：重构时测试不应该失败
> - **实战题（⭐⭐⭐）**：审查一个测试代码，找出其中的问题并修复。
>   - 提示：检查Mock、隔离、命名、断言

---

**关联笔记**：[[Python-pytest入门指南]]、[[FastAPI测试实战]]、[[CI-CD最佳实践]]

**前置知识**：[[Python基础]]、[[pytest]]、[[FastAPI]]

**相关标签**：#Python #测试 #集成测试 #E2E #pytest #Testcontainers #Playwright
