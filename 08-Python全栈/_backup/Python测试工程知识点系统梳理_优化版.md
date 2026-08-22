---
title: Python 测试工程知识点系统梳理
tags: [Python全栈, Python, 测试, pytest, unittest, mock, 覆盖率, CI, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# Python 测试工程知识点系统梳理（优化版）

> **文档说明**：系统梳理 Python 测试工程体系，涵盖 pytest、unittest、mock、测试覆盖率、TDD、接口测试、性能测试、CI 集成等。

---

## 1. 概述

测试是保证代码质量的核心手段。Python 测试生态以 pytest 为事实标准，配合 unittest（标准库）、mock、coverage 等工具构建完整测试体系。

**测试金字塔**：
- **单元测试（Unit）**：测试单个函数/类，速度快，数量最多
- **集成测试（Integration）**：测试模块间协作，速度中
- **端到端测试（E2E）**：测试完整流程，速度慢，数量最少

---

## 2. pytest

### 2.1 基本用法

```python
# test_sample.py
def test_add():
    assert 1 + 1 == 2

def test_list():
    assert [1, 2, 3] == [1, 2, 3]
    assert len([1, 2, 3]) == 3
```

```bash
pytest                          # 运行所有测试
pytest test_sample.py           # 运行指定文件
pytest test_sample.py::test_add # 运行指定函数
pytest -v                       # 详细输出
pytest -x                       # 遇到第一个失败就停止
pytest -k "add"                 # 按名称筛选
pytest --tb=short               # 简短错误信息
```

### 2.2 Fixture（夹具）

```python
import pytest

@pytest.fixture
def db_session():
    """测试用数据库会话，测试后自动回滚"""
    session = create_test_session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="session")  # 整个测试会话只创建一次
def app():
    app = create_test_app()
    return app

def test_create_user(db_session):
    user = User(name="Alice")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

### 2.3 参数化测试

```python
@pytest.mark.parametrize("input, expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (0, 0),
])
def test_double(input, expected):
    assert input * 2 == expected

# 多组参数
@pytest.mark.parametrize("x", [0, 1])
@pytest.mark.parametrize("y", [2, 3])
def test_combination(x, y):
    assert x + y > 0
```

### 2.4 异常测试

```python
import pytest

def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_value_error():
    with pytest.raises(ValueError, match="must be positive"):
        raise ValueError("value must be positive")
```

> 🔍 **知识点深度解析**
>
> **作用**：pytest 是 Python 最流行的测试框架，比 unittest 更简洁强大。
>
> **原理**：pytest 通过断言重写（assert rewriting）实现详细的失败信息——它在导入测试模块前修改字节码，让 `assert` 失败时输出左右值的详细对比。Fixture 是 pytest 的核心特性，通过依赖注入方式为测试函数提供资源，支持 scope（function/class/module/session）控制生命周期，`yield` 前是 setup，后是 teardown。参数化测试用一组参数运行多次测试，减少重复代码。pytest 兼容 unittest 测试用例，可以渐进迁移。
>
> **用法要点**：① 用 fixture 管理测试资源（数据库、客户端、mock）；② 参数化减少重复测试代码；③ 用 `conftest.py` 共享 fixture；④ 面试常考：pytest vs unittest、fixture 原理与 scope、参数化、mock 用法、测试覆盖率。

---

## 3. unittest（标准库）

```python
import unittest

class TestMath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("整个测试类开始前执行一次")
    
    def setUp(self):
        print("每个测试方法前执行")
        self.value = 10
    
    def tearDown(self):
        print("每个测试方法后执行")
    
    def test_add(self):
        self.assertEqual(self.value + 5, 15)
        self.assertTrue(True)
        self.assertIn(3, [1, 2, 3])
    
    @unittest.skip("跳过原因")
    def test_skip(self):
        pass

if __name__ == "__main__":
    unittest.main()
```

---

## 4. Mock（模拟）

### 4.1 unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock

# 基本 Mock
mock = Mock()
mock.method.return_value = 42
assert mock.method() == 42
mock.method.assert_called_once()

# patch 替换对象
@patch("module.requests.get")
def test_api(mock_get):
    mock_get.return_value.json.return_value = {"id": 1}
    result = fetch_data()
    mock_get.assert_called_with("https://api.example.com")
    assert result["id"] == 1

# patch 上下文管理器
with patch("module.os.path.exists", return_value=True):
    result = check_file()
```

### 4.2 pytest-mock

```python
def test_api(mocker):
    mock_get = mocker.patch("module.requests.get")
    mock_get.return_value.json.return_value = {"id": 1}
    result = fetch_data()
    mock_get.assert_called_once()
```

> 🔍 **知识点深度解析**
>
> **作用**：Mock 用于隔离测试对象，替换外部依赖（API、数据库、文件），让测试快速且确定。
>
> **原理**：`unittest.mock.Mock` 是一个动态对象，访问任何属性/方法都会创建新的 Mock，可以设置 `return_value`（返回值）、`side_effect`（异常/迭代器），并断言调用情况（`assert_called_once`、`assert_called_with`）。`patch` 通过修改模块的属性引用来替换对象，测试结束后自动恢复。`patch("module.func")` 替换的是 module 中对 func 的引用，所以路径要写使用方的模块路径，而不是定义方。`MagicMock` 支持魔术方法（`__str__`、`__iter__` 等）。
>
> **用法要点**：① patch 路径写"使用方模块.对象"，不是"定义方模块.对象"；② 不要 mock 被测对象本身，只 mock 外部依赖；③ 过度 mock 会降低测试价值；④ 面试常考：mock 原理、patch 路径规则、return_value vs side_effect、mock 断言。

---

## 5. 测试覆盖率

```bash
# 安装
pip install pytest-cov

# 运行并生成覆盖率报告
pytest --cov=myapp --cov-report=term-missing --cov-report=html

# 输出
# Name                 Stmts   Miss  Cover   Missing
# myapp/models.py        120      5    96%   45-49
# myapp/views.py          80     20    75%   30-50
```

**覆盖率指标**：
- 行覆盖率（Line）：执行到的行比例
- 分支覆盖率（Branch）：条件分支都走到
- 目标：核心业务逻辑 > 80%，不要追求 100%

---

## 6. Web 应用测试

### 6.1 FastAPI 测试

```python
from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    response = await async_client.post(
        "/api/users",
        json={"name": "Alice", "email": "alice@example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
```

### 6.2 Django 测试

```python
from django.test import TestCase, Client

class UserAPITest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_list_users(self):
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, 200)
```

---

## 7. TDD（测试驱动开发）

**红-绿-重构循环**：
1. **红**：写一个失败的测试（描述期望行为）
2. **绿**：写最少的代码让测试通过
3. **重构**：优化代码，保持测试通过

```python
# 1. 红：先写测试
def test_fizzbuzz():
    assert fizzbuzz(3) == "Fizz"
    assert fizzbuzz(5) == "Buzz"
    assert fizzbuzz(15) == "FizzBuzz"
    assert fizzbuzz(1) == "1"

# 2. 绿：写实现
def fizzbuzz(n):
    if n % 15 == 0: return "FizzBuzz"
    if n % 3 == 0: return "Fizz"
    if n % 5 == 0: return "Buzz"
    return str(n)

# 3. 重构：优化代码
```

---

## 8.1 契约测试（Contract Testing）

微服务间接口测试，消费者驱动契约（CDC）。

```python
# Pact Python 示例
# 消费者端定义期望
from pact import Consumer, Provider

pact = Consumer("UserService").has_pact_with(Provider("OrderService"))
pact.start_service()

with pact:
    (pact
     .given("订单存在")
     .upon_receiving("获取订单请求")
     .with_request(method="GET", path="/orders/1")
     .will_respond_with(status=200, body={"id": 1, "status": "paid"}))
    
    # 消费者代码调用，验证契约
```

**契约测试价值**：确保服务间接口兼容，避免集成时才发现不兼容。

---

## 8.2 测试数据管理

```python
# factory_boy：测试数据工厂
import factory
from .models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    is_active = True

# 使用
user = UserFactory()  # 创建一个用户
users = UserFactory.create_batch(10)  # 批量创建

# faker：假数据生成
from faker import Faker
fake = Faker("zh_CN")
fake.name()  # "张三"
fake.email()  # "zhangsan@example.com"
fake.phone_number()  # "13800138000"
```

---

## 8.3 突变测试（Mutation Testing）

评估测试质量：故意修改代码（变异体），看测试能否发现。

```bash
pip install mutmut
mutmut run           # 运行突变测试
mutmut results       # 查看结果
# 指标：Mutation Score = 杀死的变异体 / 总变异体
# 分数高说明测试质量好
```

---

## 8.4 测试报告与并行测试

```bash
# allure-pytest：美观的测试报告
pytest --alluredir=allure-results
allure serve allure-results

# JUnit XML：CI 集成
pytest --junitxml=test-results.xml

# 并行测试（pytest-xdist）
pip install pytest-xdist
pytest -n auto       # 自动用 CPU 核心数并行
pytest -n 4          # 指定4个进程
# 注意：并行测试需要测试隔离，不能共享状态
```

---

## 8.5 测试金字塔与策略

```
        /\
       /E2E\        少而慢（UI/完整流程）
      /------\
     /集成测试\      中等（模块协作/API）
    /----------\
   /  单元测试   \    多而快（函数/类）
  /--------------\
```

- **单元测试**：70%，测试单个函数/类，mock 外部依赖
- **集成测试**：20%，测试模块协作、数据库、API
- **E2E 测试**：10%，测试完整用户流程
- **反模式**：测试冰锥（E2E 多，单元测试少），维护成本高

---

## 9. 性能测试

```python
# Locust 示例
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_articles(self):
        self.client.get("/api/articles")
    
    @task(3)  # 权重3倍
    def get_article_detail(self):
        self.client.get("/api/articles/1")
```

```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## 9. CI 集成

```yaml
# GitHub Actions
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest --cov=myapp --cov-fail-under=80
```

---

## 11. 面试高频考点

1. **pytest vs unittest**：区别、优缺点
2. **Fixture**：原理、scope、yield teardown
3. **参数化测试**：减少重复代码
4. **Mock**：原理、patch 路径、断言
5. **测试覆盖率**：指标、工具、目标
6. **TDD**：红绿重构循环、优缺点
7. **单元测试 vs 集成测试**：区别、金字塔
8. **测试隔离**：每个测试独立，不依赖执行顺序
9. **接口测试**：FastAPI/Django 测试客户端
10. **CI 集成**：自动化测试、覆盖率门禁
11. **契约测试**：Pact、消费者驱动、微服务接口
12. **测试数据**：factory_boy、faker、数据隔离
13. **突变测试**：mutmut、Mutation Score、测试质量
14. **测试报告**：allure、JUnit XML、pytest-xdist 并行
15. **测试金字塔**：单元/集成/E2E 比例、测试冰锥反模式

---

## 📝 精简总结

- pytest 是 Python 测试首选，assert 重写 + fixture + 参数化
- fixture 管理测试资源，scope 控制生命周期，yield 做 teardown
- unittest 是标准库，TestCase + setUp/tearDown
- Mock 隔离外部依赖，patch 路径写使用方模块
- 覆盖率：pytest-cov，核心逻辑 >80%，不追求100%
- TDD：红（失败测试）→ 绿（最小实现）→ 重构
- 测试金字塔：单元测试(70%)多而快，集成(20%)，E2E(10%)少而慢
- 契约测试：Pact 消费者驱动，微服务接口兼容保障
- 测试数据：factory_boy 工厂模式 + faker 假数据，保证数据隔离
- 突变测试：mutmut 评估测试质量，Mutation Score 越高越好
- 测试报告：allure 美观报告，JUnit XML CI 集成
- 并行测试：pytest-xdist -n auto，需保证测试隔离
- Web测试：httpx（FastAPI）、Django Client
- 性能测试：Locust，CI 集成自动化

---

[[08-Python全栈/MOC-Python全栈|← 返回 Python 全栈 MOC]] | [[Home|🏠 返回首页]]
