---
title: Pytest 测试驱动开发
category: 测试与工程化
tags: [Python, Pytest, TDD, 单元测试, 测试驱动开发, fixture, mock]
priority: P1
status: completed
created: 2026-09-10
updated: 2026-09-10
version: 2.0
author: BewhY_L
pre: ["[[Python-项目结构最佳实践]]", "[[Poetry-依赖与虚拟环境管理]]"]
description: 系统讲解 Pytest 测试框架的核心机制、fixture 依赖注入、参数化测试、Mock 系统、插件生态、TDD 方法论与 CI 集成
---

# Pytest 测试驱动开发

> **文档定位**：本文档是 Pytest 测试框架与 TDD 方法论的完整实战指南，从安装配置到高级 fixture 设计、Mock 系统、异步测试、并行执行、覆盖率统计，再到测试金字塔与 CI 集成，覆盖 Python 项目测试体系的全部核心知识点。
>
> **适用人群**：Python 开发者、需要建立测试体系的全栈工程师、实践 TDD 的开发团队
>
> **前置知识**：[[Python-项目结构最佳实践]]、[[Poetry-依赖与虚拟环境管理]]、基础 Python 语法与函数编程

---

## 一、概述与学习路径

### 1.1 什么是 Pytest

**Pytest** 是 Python 生态中最流行、最强大的测试框架。它允许开发者用纯 Python 函数编写测试（无需继承任何基类），使用原生 `assert` 语句做断言（而非 `self.assertEqual`），并通过强大的 **fixture 依赖注入系统** 和 **3000+ 插件生态** 解决了 unittest 的诸多痛点。

**生活化比喻**：如果 unittest 像一份必须按固定格式填写的行政表格（必须继承 TestCase、必须用 self.assertEqual），那么 Pytest 就像一个智能助手——你只需要告诉它"我要验证什么"（写个普通函数 + assert），它会自动帮你准备数据（fixture）、自动对比差异（断言重写）、自动生成报告（插件）。

**核心价值**：用最少的样板代码写出可读性最强、维护成本最低的测试。

### 1.2 与 unittest 对比

| 维度 | unittest | pytest |
|------|----------|--------|
| 测试写法 | 必须继承 `unittest.TestCase` | 普通函数即可，无需继承 |
| 断言方式 | `self.assertEqual(a, b)` 等十几种方法 | 直接 `assert a == b`，自动重写输出差异 |
| 前置/后置 | `setUp()`/`tearDown()`，类级别继承 | fixture 系统：可复用、可组合、可参数化、有作用域 |
| 参数化 | 需手写循环或 `ddt` 库 | `@pytest.mark.parametrize` 一行搞定 |
| 测试选择 | 不灵活 | `-k`/`-m`/按路径/节点 ID 多种方式 |
| 插件生态 | 薄弱 | 3000+ 插件 |
| 失败调试 | 仅 traceback | `--pdb` 自动进调试器，`--lf` 重跑失败 |
| 异常测试 | `assertRaises` 上下文管理器 | `pytest.raises` 更简洁 |

> 🎯 面试高频：Pytest 相比 unittest 的核心优势是什么？——断言重写（assert rewrite）让失败信息极其详细；fixture 系统的依赖注入和作用域管理是 unittest 的 setUp/tearDown 无法比拟的；插件生态是 Pytest 成为事实标准的关键。

### 1.3 测试驱动开发（TDD）概述

**测试驱动开发（TDD, Test-Driven Development）** 是一种开发方法论，核心循环是 **红-绿-重构（Red-Green-Refactor）**：

```mermaid
graph LR
    A[Red 红<br/>写失败的测试] --> B[Green 绿<br/>写最少代码使测试通过]
    B --> C[Refactor 重构<br/>优化代码结构]
    C --> A
```

| 阶段 | 目标 | 规则 | 时间占比 |
|------|------|------|---------|
| **红（Red）** | 测试失败，证明测试有效 | 只写测试，不写实现代码 | 20% |
| **绿（Green）** | 测试通过，功能可用 | 写最少代码使测试通过，允许"丑陋" | 30% |
| **重构（Refactor）** | 代码整洁，测试仍通过 | 重构实现，不改变行为，测试保持通过 | 50% |

> ✅ 最佳实践：TDD 的核心不是"先写测试"，而是"每个步骤只做一件事"——红阶段证明测试能抓住错误，绿阶段证明功能能工作，重构阶段保持行为不变同时改善结构。

### 1.4 学习路径与知识依赖

```mermaid
graph TB
    A[Python 基础语法] --> B[测试基础概念<br/>test函数/assert]
    B --> C[Fixture 系统<br/>依赖注入]
    C --> D[参数化测试]
    D --> E[标记与分组]
    E --> F[Mock 与 Monkeypatch]
    F --> G[插件生态<br/>cov/xdist/asyncio]
    G --> H[TDD 方法论]
    H --> I[CI/CD 集成]
    I --> J[测试金字塔与覆盖率]
```

### 1.5 安装与快速开始

```bash
# 使用 pip 安装
pip install pytest

# 验证安装
pytest --version
# 预期输出：pytest 8.x.x

# 使用 Poetry 安装（推荐）
poetry add --group dev pytest

# 运行测试（自动发现 test_*.py 文件）
pytest
```

```bash
# 第一个测试
# 文件：tests/test_smoke.py
def test_true():
    assert True

# 运行
pytest tests/test_smoke.py -v
# 预期输出：
# tests/test_smoke.py::test_true PASSED
```

> ❌ 常见坑点：如果运行 pytest 时提示"no tests ran"，检查文件名是否以 `test_` 开头（或 `_test.py` 结尾），测试函数是否以 `test_` 开头。Pytest 的默认发现规则是硬性的。

---

> 💡 **本章深度讲解**：本章建立了 Pytest 的整体认知框架。Pytest 的核心设计哲学是"约定优于配置"和"最小样板代码"——它通过断言重写、fixture 依赖注入和插件系统三大支柱，解决了 unittest 的繁琐问题。TDD 则是一种方法论，Pytest 是实践 TDD 的工具。理解"为什么选 Pytest"和"TDD 为什么有效"，比记住具体命令更重要。
>
> **📝 精简总结**：
> - 核心概念：Pytest 是 Python 测试框架；TDD 是红-绿-重构方法论
> - 关键原理：断言重写让失败信息详细；fixture 是依赖注入系统
> - 常用操作：`pip install pytest`；`pytest -v` 运行测试
> - 最佳实践：测试文件 `test_*.py`；测试函数 `test_*`；新代码配测试
> - 常见坑点：文件名/函数名不符合发现规则导致"no tests ran"
> - 面试高频：Pytest vs unittest 优势；TDD 红绿重构循环

### 🎯 梯度练习题

**基础题（⭐）**
1. 写出一个最简单的 Pytest 测试函数，验证 `1 + 1 == 2`。
   - 答案：`def test_add(): assert 1 + 1 == 2`
2. Pytest 默认从哪些文件和函数中发现测试？
   - 答案：文件名匹配 `test_*.py` 或 `*_test.py`；函数名以 `test_` 开头。

**进阶题（⭐⭐）**
1. 为什么 Pytest 的 `assert a == b` 比 unittest 的 `self.assertEqual(a, b)` 更好？
   - 思考方向：断言重写机制；失败时自动收集左右值；错误信息可读性。
2. TDD 中"红"阶段为什么必须先看到测试失败？
   - 思考方向：证明测试本身有效；防止"永远通过的假测试"；建立信任。

**实战题（⭐⭐⭐）**
- **背景**：团队从 unittest 迁移到 Pytest，有 50 个 unittest.TestCase 类。
- **需求**：制定迁移策略，确保零停机、渐进式迁移。
- **要求**：① Pytest 可以直接运行 unittest 测试（无需修改）；② 新功能用 Pytest 风格编写；③ 逐步将旧测试转为 Pytest fixture。
- **验收标准**：所有现有测试在 Pytest 中通过；新测试无需继承 TestCase。
- **提示**：Pytest 原生兼容 unittest.TestCase，不需要重写旧测试。

---

## 二、Pytest 核心架构与断言重写原理

### 2.1 执行流程全景

Pytest 的执行分为三个阶段：**收集（Collection）→ 执行（Execution）→ 报告（Reporting）**。

```mermaid
graph TB
    subgraph 收集阶段
        A[扫描文件<br/>testpaths] --> B[匹配文件<br/>test_*.py]
        B --> C[导入测试模块]
        C --> D[收集测试函数<br/>test_*]
        D --> E[收集 fixture<br/>conftest.py]
        E --> F[应用标记<br/>@pytest.mark]
    end

    subgraph 执行阶段
        G[按顺序/并行执行] --> H[解析 fixture 依赖图]
        H --> I[执行 setup 部分]
        I --> J[执行测试函数体]
        J --> K[断言重写检查]
        K --> L[执行 teardown 部分]
    end

    subgraph 报告阶段
        M[结果汇总] --> N[终端输出<br/>PASSED/FAILED/ERROR]
        N --> O[覆盖率报告]
        N --> P[HTML/XML 报告]
    end

    F --> G
    L --> M
```

### 2.2 断言重写（Assert Rewriting）原理

Pytest 最核心的黑科技是**断言重写**。普通 Python 的 `assert result == expected` 失败时只会抛出 `AssertionError`，没有任何附加信息。Pytest 在导入测试模块时，会用 `ast.parse` 重写模块的 AST，将每个 `assert` 表达式改写成能自动收集上下文信息的形式。

```python
# 你写的代码
def test_add():
    result = add(2, 3)
    assert result == 5

# Pytest 在导入时重写（概念示意）
def test_add():
    result = add(2, 3)
    if not (result == 5):
        # 自动收集：result 的值、期望值、调用栈
        raise AssertionError(
            f"assert result == 5\n"
            f"  where result = {result!r}\n"
            f"  where 5 = 5"
        )
```

**重写的效果对比**：

```python
# test_demo.py
def test_list():
    a = [1, 2, 3]
    b = [1, 2, 4]
    assert a == b

# 普通 Python assert 的输出：
# AssertionError

# Pytest 的输出（极其详细）：
# =================================== FAILURES ===================================
# __________________________________ test_list ___________________________________
#
#     def test_list():
#         a = [1, 2, 3]
#         b = [1, 2, 4]
# >       assert a == b
# E       assert [1, 2, 3] == [1, 2, 4]
# E
# E         At index 2 diff: 3 != 4
# E
# E         Full diff:
# E         - [1, 2, 4]
# E         ?         ^
# E         + [1, 2, 3]
# E         ?         ^
```

> 🎯 面试高频：Pytest 的断言重写是如何实现的？——Pytest 使用 `meta_path` 导入钩子，在测试模块被导入前拦截，用 `ast` 模块解析源码，将 `assert` 节点替换为带详细信息收集的版本，然后编译执行。这就是为什么 Pytest 需要导入测试文件（而 unittest 不需要特殊机制）。

### 2.3 fixture 依赖注入原理

Fixture 是 Pytest 的核心创新。它通过**测试函数参数名匹配**实现依赖注入：测试函数声明需要的 fixture 作为参数，Pytest 在执行时自动找到并注入。

```python
# fixture 定义
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value", "count": 42}

# 测试函数通过参数声明依赖
def test_sample(sample_data):
    assert sample_data["key"] == "value"
    assert sample_data["count"] == 42
```

**依赖注入的工作流程**：

```mermaid
graph LR
    A[测试函数参数列表] --> B{参数名匹配<br/>fixture?}
    B -->|是| C[查找 fixture 定义]
    C --> D{fixture 有依赖?}
    D -->|是| E[递归解析依赖]
    E --> F[按依赖顺序执行 setup]
    D -->|否| F
    F --> G[注入返回值到测试函数]
    G --> H[执行测试函数]
    H --> I[按反向顺序执行 teardown]
```

### 2.4 conftest.py 机制

`conftest.py` 是 Pytest 的特殊文件，其中定义的 fixture 可以被同目录及子目录的所有测试文件使用，**无需 import**。

```python
# tests/conftest.py
import pytest

@pytest.fixture
def db_connection():
    """所有 tests/ 下的测试都可以直接用 db_connection fixture"""
    conn = create_db_connection()
    yield conn
    conn.close()

@pytest.fixture
def sample_user(db_connection):
    """fixture 可以依赖其他 fixture"""
    user = db_connection.create_user("test@example.com")
    yield user
    db_connection.delete_user(user.id)
```

```python
# tests/api/test_users.py
# 不需要 import db_connection 或 sample_user
def test_get_user(db_connection, sample_user):
    # 直接使用，Pytest 自动注入
    result = db_connection.query_user(sample_user.id)
    assert result.email == "test@example.com"
```

> ❌ 常见坑点：fixture 定义在 `conftest.py` 中不需要 import，但如果定义在普通的工具模块中，必须显式 import。很多新手把 fixture 写在 `utils.py` 里然后抱怨"fixture not found"——记住：**conftest.py 中的 fixture 自动可用，其他模块中的 fixture 必须 import**。

### 2.5 测试收集规则

Pytest 遵循以下默认收集规则：

```python
# ✅ 正确的命名
test_something.py          # 文件名：test_*.py
class TestSomething:       # 类名：Test*（不能有 __init__ 方法）
    def test_method(self): # 方法名：test_*
def test_function():       # 函数名：test_*
    pass

# ❌ 不会被收集
something_test.py          # 不会被收集（必须 test_*.py 或 *_test.py）
class SomethingTest:       # 不会被收集（类名必须 Test*）
    def test_method(self):
        pass
def something_test():      # 不会被收集（函数名必须 test_*）
    pass
```

> ❌ 常见坑点：测试类中如果定义了 `__init__` 方法，Pytest 不会收集该类的测试方法。Pytest 会用默认构造函数实例化测试类，自定义 `__init__` 会破坏这个机制。

---

> 💡 **本章深度讲解**：理解 Pytest 底层原理是写出高质量测试的基础。断言重写让你"写最少的 assert，获得最详细的错误信息"；fixture 依赖注入让测试 setup 变成可组合的积木块而非继承链；conftest.py 是 fixture 的共享仓库。这三个机制共同构成了 Pytest 区别于其他测试框架的核心竞争力。
>
> **📝 精简总结**：
> - 核心概念：收集/执行/报告三阶段；断言重写；fixture 依赖注入；conftest.py
> - 关键原理：AST 重写 assert 节点；参数名匹配注入；conftest 自动发现
> - 常用操作：`pytest -v`；`conftest.py` 放共享 fixture；遵守 test_* 命名
> - 最佳实践：共享 fixture 放 conftest.py；测试类不要 __init__
> - 常见坑点：fixture not found（忘了 import 或放错位置）；测试不被收集
> - 面试高频：断言重写原理；fixture 依赖注入机制；conftest.py 作用

### 🎯 梯度练习题

**基础题（⭐）**
1. Pytest 的三个执行阶段是什么？
   - 答案：收集（Collection）、执行（Execution）、报告（Reporting）。
2. 为什么 Pytest 的 `assert a == b` 比 `self.assertEqual(a, b)` 更好？
   - 答案：断言重写自动收集上下文，失败信息极其详细。

**进阶题（⭐⭐）**
1. Pytest 如何在不修改源码的情况下重写 assert 语句？
   - 思考方向：meta_path 导入钩子；AST 解析；字节码重写。
2. conftest.py 中的 fixture 为什么不需要 import？
   - 思考方向：Pytest 在收集阶段自动导入 conftest.py；fixture 注册到全局 fixture 管理器。

**实战题（⭐⭐⭐）**
- **背景**：你的测试失败了，但输出只显示 `AssertionError`，没有任何详细信息。
- **需求**：排查为什么 Pytest 没有重写断言。
- **要求**：① 检查 `--assert=plain` 参数；② 检查测试文件是否在 testpaths 中；③ 检查是否用了 `-p no:assertion`。
- **验收标准**：恢复详细的断言失败输出。
- **提示**：`pytest --showconfig` 可以查看当前配置。

---

## 三、测试基础：test 函数、assert 与 setup/teardown

### 3.1 第一个测试函数

Pytest 测试的最小单元是一个以 `test_` 开头的 Python 函数。函数体内用 `assert` 验证预期行为。

```python
# tests/test_calculator.py

# 被测代码（假设在 my_project/calculator.py 中）
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b


# 测试函数
def test_add_positive():
    result = add(2, 3)
    assert result == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_add_zero():
    assert add(0, 0) == 0

def test_divide_normal():
    assert divide(10, 2) == 5.0
```

**运行方式**：

```bash
# 运行单个文件
pytest tests/test_calculator.py -v

# 运行单个测试函数
pytest tests/test_calculator.py::test_add_positive -v

# 按关键字运行
pytest -k "add" -v

# 预期输出：
# tests/test_calculator.py::test_add_positive PASSED
# tests/test_calculator.py::test_add_negative PASSED
# tests/test_calculator.py::test_add_zero PASSED
# tests/test_calculator.py::test_divide_normal PASSED
```

### 3.2 assert 断言的各种形式

Pytest 的 `assert` 可以断言任何 Python 表达式。以下是常见的断言模式：

```python
# 1. 相等性断言
assert result == expected
assert result != unexpected

# 2. 数值断言
assert count > 0
assert len(items) >= 3
assert 0 < temperature < 100

# 3. 布尔断言
assert is_valid(user)
assert not is_admin

# 4. 包含性断言
assert "error" in response.text
assert item in cart_items
assert key in config

# 5. 类型断言（mypy 不管这个，这是运行时断言）
assert isinstance(result, dict)
assert isinstance(value, (int, float))

# 6. None 断言
assert result is None
assert result is not None

# 7. 字符串匹配
assert message.startswith("Error")
assert message.endswith("failed")
assert "timeout" in message.lower()
```

> ✅ 最佳实践：一个测试函数只验证一个行为。如果一个测试函数中有 5 个 assert，那么第一个 assert 失败后后面的都不会执行。将多个无关的断言拆成多个测试函数，每个测试函数独立运行。

### 3.3 类形式的测试

虽然 Pytest 推荐用函数写测试，但也支持类形式（与 unittest 兼容）：

```python
# tests/test_calculator_class.py

class TestCalculator:
    """类形式的测试：同一个类中的测试共享 setup_method"""

    def setup_method(self, method):
        """每个测试方法执行前调用（类似 unittest.setUp）"""
        print(f"Setting up for {method.__name__}")
        self.calc = Calculator()
        self.test_data = [1, 2, 3, 4, 5]

    def teardown_method(self, method):
        """每个测试方法执行后调用（类似 unittest.tearDown）"""
        print(f"Tearing down after {method.__name__}")

    def test_add(self):
        assert self.calc.add(2, 3) == 5

    def test_multiply(self):
        assert self.calc.multiply(3, 4) == 12

    def test_division(self):
        assert self.calc.divide(10, 2) == 5.0
```

```python
# 模块级 setup/teardown
def setup_module(module):
    """整个模块开始前执行一次"""
    print(f"Module {module.__name__} starting")

def teardown_module(module):
    """整个模块结束后执行一次"""
    print(f"Module {module.__name__} finished")

class TestClass:
    def setup_class(self):
        """整个类开始前执行一次（注意：不是每个方法）"""
        print("Class setup")

    def teardown_class(self):
        """整个类结束后执行一次"""
        print("Class teardown")

    def setup_method(self, method):
        """每个方法前执行"""
        pass

    def teardown_method(self, method):
        """每个方法后执行"""
        pass
```

> ❌ 常见坑点：`setup_class` 是类方法（在类级别执行一次），而 `setup_method` 是实例方法（每个测试方法执行一次）。混淆这两个会导致测试间数据污染。现代 Pytest 推荐用 fixture 替代这些 setup/teardown 方法。

### 3.4 内置 fixture：tmp_path 和 tmp_path_factory

Pytest 提供了创建临时文件/目录的内置 fixture：

```python
# tests/test_files.py

def test_write_file(tmp_path):
    # tmp_path 是 pathlib.Path 对象，指向临时目录
    # 每个测试函数有独立的临时目录
    file_path = tmp_path / "test.txt"

    # 写入文件
    file_path.write_text("Hello, Pytest!")

    # 验证文件内容
    content = file_path.read_text()
    assert content == "Hello, Pytest!"

    # 验证文件存在
    assert file_path.exists()

def test_create_directory(tmp_path):
    # 创建子目录
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # 在子目录中创建文件
    (data_dir / "config.json").write_text('{"debug": true}')

    assert (data_dir / "config.json").exists()
```

```python
# tmp_path_factory：模块/会话级别的临时目录
import pytest

@pytest.fixture(scope="module")
def shared_tmp_dir(tmp_path_factory):
    """模块级临时目录：整个模块共享一个目录"""
    return tmp_path_factory.mktemp("shared_data")

def test_file_1(shared_tmp_dir):
    (shared_tmp_dir / "file1.txt").write_text("data1")
    assert (shared_tmp_dir / "file1.txt").exists()

def test_file_2(shared_tmp_dir):
    # file1.txt 在同一个目录中存在
    assert (shared_tmp_dir / "file1.txt").exists()
```

### 3.5 测试命名规范

```python
# ✅ 好的命名：描述测试场景和预期结果
def test_create_user_with_valid_data_returns_201():
    ...

def test_create_user_with_duplicate_email_returns_409():
    ...

def test_get_user_with_nonexistent_id_returns_404():
    ...

def test_login_with_correct_password_succeeds():
    ...

def test_login_with_wrong_password_fails():
    ...

# ❌ 不好的命名：模糊不清
def test_user_1():
    ...

def test_create():
    ...

def test_it_works():
    ...

def test_case1():
    ...
```

> ✅ 最佳实践：测试命名格式为 `test_<被测行为>_<场景>_<预期结果>`。这样当测试失败时，从测试名就能知道哪里出了什么问题，不需要读测试代码。

---

> 💡 **本章深度讲解**：测试函数、assert 和 setup/teardown 是 Pytest 的最基础层。看似简单，但"一个测试一个行为"和"命名即文档"这两个原则直接决定了测试套件的可维护性。类形式的 setup_method 是从 unittest 过渡的桥梁，但现代 Pytest 项目几乎全部用 fixture 替代。tmp_path 等内置 fixture 展示了 Pytest 设计哲学的一致性——一切都是可注入的。
>
> **📝 精简总结**：
> - 核心概念：test_ 函数、assert 表达式、setup/teardown、tmp_path
> - 关键原理：函数即测试；assert 任意表达式；类级别和方法级别的生命周期
> - 常用操作：`pytest -v`；`pytest -k "keyword"`；`tmp_path` 临时文件
> - 最佳实践：一个测试一个行为；命名描述场景和预期；用 fixture 替代 setup_method
> - 常见坑点：一个测试多个 assert；setup_class vs setup_method 混淆
> - 面试高频：Pytest 测试发现规则；tmp_path vs tmp_path_factory 区别

### 🎯 梯度练习题

**基础题（⭐）**
1. 写出一个测试函数，验证 `"hello".upper()` 返回 `"HELLO"`。
   - 答案：`def test_upper(): assert "hello".upper() == "HELLO"`
2. `tmp_path` 和 `tmp_path_factory` 的区别是什么？
   - 答案：tmp_path 是 function 级别的 Path；tmp_path_factory 可以创建 module/session 级别的临时目录。

**进阶题（⭐⭐）**
1. 为什么建议一个测试函数只验证一个行为？
   - 思考方向：第一个 assert 失败后后续不执行；失败定位；可读性。
2. `setup_method` 和 fixture 的本质区别是什么？
   - 思考方向：继承 vs 组合；可复用性；参数化能力；作用域。

**实战题（⭐⭐⭐）**
- **背景**：你有一个 `User` 类，有 `name`、`email` 属性和 `validate()` 方法。
- **需求**：为 User 类编写完整的测试套件。
- **要求**：① 测试创建 User 对象；② 测试 validate() 正常情况；③ 测试 validate() 异常情况；④ 使用 tmp_path 保存测试输出。
- **验收标准**：所有测试通过；测试命名清晰；每个测试独立。
- **提示**：考虑使用参数化测试减少重复代码。

---

## 四、Fixture 深度用法

### 4.1 Fixture 基础与作用域

Fixture 是 Pytest 最强大的特性。用 `@pytest.fixture` 装饰器定义，测试函数通过参数声明依赖。

```python
# tests/conftest.py
import pytest

# 最简单的 fixture
@pytest.fixture
def sample_user():
    """每个测试函数执行一次（function 作用域，默认）"""
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}

# module 作用域：整个测试模块只创建一次
@pytest.fixture(scope="module")
def large_dataset():
    """模块级 fixture：模拟大数据集，只加载一次"""
    data = [{"id": i, "value": f"item_{i}"} for i in range(10000)]
    return data

# session 作用域：整个测试会话只执行一次
@pytest.fixture(scope="session")
def database_engine():
    """会话级 fixture：数据库引擎只创建一次"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    # yield 之后的代码是 teardown
    engine.dispose()
```

**Fixture 作用域对比**：

| 作用域 | 生命周期 | 适用场景 | 创建成本 |
|--------|---------|---------|---------|
| `function`（默认） | 每个测试函数执行一次 | 无状态数据、临时对象 | 低 |
| `class` | 每个测试类执行一次 | 类内共享的设置 | 中 |
| `module` | 每个测试模块执行一次 | 模块级共享资源 | 较高 |
| `package` | 每个包执行一次 | 包级共享资源 | 高 |
| `session` | 整个测试会话执行一次 | 数据库连接、浏览器实例 | 最高 |

```python
# tests/test_fixture_scopes.py

def test_user_function(sample_user, large_dataset):
    # sample_user 是 function 级别：每次测试新建
    # large_dataset 是 module 级别：整个模块共用
    assert sample_user["name"] == "Alice"
    assert len(large_dataset) == 10000

def test_user_function_2(sample_user, large_dataset):
    # sample_user 是新的对象
    # large_dataset 还是同一个对象
    assert sample_user["id"] == 1
```

> 🎯 面试高频：fixture 的 scope 参数有哪些值？应该如何选择？——function（默认，每个测试一次）、class（每个类一次）、module（每个文件一次）、package（每个包一次）、session（整个测试会话一次）。选择原则：**最小必要作用域**——能用 function 就不用 module/session，减少测试间的隐式依赖。

### 4.2 yield 与 setup/teardown 分离

Fixture 可以用 `yield` 关键字将 setup 和 teardown 分离：yield 之前是 setup，yield 之后是 teardown。

```python
import pytest

@pytest.fixture
def db_session():
    # --- Setup 阶段 ---
    connection = create_connection("sqlite:///:memory:")
    connection.execute("CREATE TABLE users (id INTEGER, name TEXT)")

    yield connection  # 这里返回值给测试函数使用

    # --- Teardown 阶段 ---
    connection.execute("DROP TABLE users")
    connection.close()

# 测试函数
def test_insert_user(db_session):
    db_session.execute(
        "INSERT INTO users VALUES (?, ?)", (1, "Alice")
    )
    result = db_session.execute("SELECT * FROM users WHERE id=1")
    assert result.fetchone()[1] == "Alice"
```

> ❌ 常见坑点：fixture 中的 yield 之后如果有异常，teardown 可能不会执行。最佳实践是用 try/finally 包裹 yield：
```python
@pytest.fixture
def safe_resource():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)  # 确保资源被释放
```

### 4.3 Fixture 依赖注入与组合

Fixture 可以依赖其他 fixture，形成依赖图：

```python
# tests/conftest.py

@pytest.fixture
def db_engine():
    """最底层的 fixture：数据库引擎"""
    engine = create_engine("sqlite:///:memory:")
    yield engine
    engine.dispose()

@pytest.fixture
def db_connection(db_engine):
    """依赖 db_engine 的 fixture：数据库连接"""
    conn = db_engine.connect()
    yield conn
    conn.close()

@pytest.fixture
def db_session(db_connection):
    """依赖 db_connection 的 fixture：事务会话"""
    transaction = db_connection.begin()
    session = Session(bind=db_connection)
    yield session
    session.close()
    transaction.rollback()  # 每个测试后回滚，不污染其他测试

@pytest.fixture
def sample_user(db_session):
    """依赖 db_session 的 fixture：测试用户数据"""
    user = User(name="Test User", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.delete(user)
    db_session.commit()
```

```python
# tests/test_user.py

def test_user_email(sample_user):
    # Pytest 自动解析依赖链：
    # sample_user -> db_session -> db_connection -> db_engine
    assert sample_user.email == "test@example.com"

def test_user_repr(sample_user):
    assert repr(sample_user) == "<User Test User>"
```

```mermaid
graph TD
    A[db_engine<br/>session 作用域] --> B[db_connection<br/>function 作用域]
    B --> C[db_session<br/>function 作用域]
    C --> D[sample_user<br/>function 作用域]
    D --> E[test_user_email]
    D --> F[test_user_repr]
```

### 4.4 参数化 Fixture

Fixture 可以通过 `params` 参数实现参数化：同一个 fixture 对每组参数运行一次。

```python
import pytest

@pytest.fixture(params=["sqlite", "postgresql", "mysql"])
def database_url(request):
    """参数化 fixture：对每种数据库运行所有依赖它的测试"""
    urls = {
        "sqlite": "sqlite:///:memory:",
        "postgresql": "postgresql://localhost/test",
        "mysql": "mysql://localhost/test",
    }
    return urls[request.param]

def test_database_connection(database_url):
    # 这个测试会运行 3 次，每次 database_url 不同
    assert database_url.startswith(("sqlite://", "postgresql://", "mysql://"))
```

**运行结果**：

```bash
pytest test_db.py -v
# 预期输出：
# test_db.py::test_database_connection[sqlite] PASSED
# test_db.py::test_database_connection[postgresql] PASSED
# test_db.py::test_database_connection[mysql] PASSED
```

### 4.5 autouse Fixture

`autouse=True` 的 fixture 会自动应用于同作用域的所有测试，无需显式声明：

```python
import pytest
import time

@pytest.fixture(autouse=True)
def timer():
    """自动计时 fixture：所有测试都会被计时"""
    start = time.time()
    yield
    duration = time.time() - start
    if duration > 1.0:
        print(f"\n[WARNING] Slow test: {duration:.2f}s")

@pytest.fixture(autouse=True)
def setup_test_env():
    """自动设置测试环境变量"""
    import os
    os.environ["TESTING"] = "true"
    yield
    del os.environ["TESTING"]

def test_env_var():
    # 不需要声明 setup_test_env，它自动执行
    import os
    assert os.environ["TESTING"] == "true"
```

> ❌ 常见坑点：autouse fixture 很方便但也很危险——如果一个 autouse fixture 有副作用（如删除数据库数据），它会影响你不想影响的测试。最佳实践：autouse fixture 只用于"所有测试都需要"的通用设置（如环境变量、计时），不要用于特定测试的数据准备。

### 4.6 fixture 的 override 机制

子目录中的 conftest.py 可以覆盖父目录中的 fixture：

```
tests/
├── conftest.py          # 定义 db_session fixture
├── test_unit/
│   ├── conftest.py      # 覆盖 db_session（内存数据库）
│   └── test_*.py
└── test_integration/
    ├── conftest.py      # 覆盖 db_session（真实测试数据库）
    └── test_*.py
```

```python
# tests/conftest.py（全局）
@pytest.fixture
def db_session():
    """默认：内存 SQLite"""
    return create_session("sqlite:///:memory:")

# tests/test_integration/conftest.py（覆盖）
@pytest.fixture
def db_session():
    """集成测试：真实 PostgreSQL 测试数据库"""
    return create_session("postgresql://localhost/test_db")
```

> ✅ 最佳实践：利用 fixture override 机制，单元测试用内存数据库，集成测试用真实数据库，而测试代码本身不需要修改。这是 fixture 设计的精髓——**测试代码只声明"我需要一个 db_session"，不关心它是什么**。

### 4.7 request 对象与 fixture 自省

`request` 对象提供了关于当前测试的元信息：

```python
import pytest

@pytest.fixture
def custom_fixture(request):
    # request.module：当前测试模块
    # request.cls：当前测试类
    # request.function：当前测试函数
    # request.scope：当前 fixture 作用域
    # request.node：完整的测试节点对象
    # request.param：参数化 fixture 的当前参数（仅 params 时）

    print(f"Running in module: {request.module.__name__}")
    print(f"Test function: {request.function.__name__}")

    if hasattr(request.node, "get_closest_marker"):
        marker = request.node.get_closest_marker("slow")
        if marker:
            print("This is a slow test")

    return {"module": request.module.__name__}

def test_with_request_info(custom_fixture):
    assert "module" in custom_fixture
```

---

> 💡 **本章深度讲解**：Fixture 是 Pytest 的灵魂。理解 fixture 的关键是理解"依赖注入"思想——测试只声明需要什么（参数），不关心如何创建。作用域决定了资源复用的粒度；yield 分离了 setup 和 teardown；参数化让一套测试逻辑跑多组数据；autouse 让通用设置自动化；override 让不同测试目录有不同实现。组合这些特性，可以优雅地管理复杂的测试基础设施。
>
> **📝 精简总结**：
> - 核心概念：fixture、scope、yield teardown、参数化 fixture、autouse、override
> - 关键原理：参数名匹配依赖注入；fixture 依赖图递归解析；conftest.py 层级 override
> - 常用操作：`@pytest.fixture`；`yield`；`params=[...]`；`autouse=True`
> - 最佳实践：最小作用域；yield 配 try/finally；共享 fixture 放 conftest.py
> - 常见坑点：autouse 滥用导致隐式副作用；teardown 中异常导致清理失败
> - 面试高频：fixture scope 选择；fixture override 机制；request 对象用法

### 🎯 梯度练习题

**基础题（⭐）**
1. fixture 的 `yield` 关键字前后分别代表什么？
   - 答案：yield 前是 setup（前置准备），yield 后是 teardown（后置清理）。
2. `autouse=True` 的 fixture 需要在测试函数参数中声明吗？
   - 答案：不需要，自动应用。

**进阶题（⭐⭐）**
1. 为什么推荐用 try/finally 包裹 yield？
   - 思考方向：测试失败时 teardown 是否执行；资源泄漏风险。
2. fixture override 机制是如何工作的？
   - 思考方向：conftest.py 的层级关系；同名 fixture 就近原则。

**实战题（⭐⭐⭐）**
- **背景**：你的项目有单元测试和集成测试，需要不同的数据库配置。
- **需求**：设计一套 fixture 体系。
- **要求**：① 单元测试用内存 SQLite；② 集成测试用真实 PostgreSQL；③ 所有测试共享同一个 Session 接口；④ 每个测试后数据回滚。
- **验收标准**：单元测试快速运行；集成测试使用真实数据库；测试间无数据污染。
- **提示**：用两个 conftest.py 分别定义不同的 db_session fixture。

---

## 五、参数化测试

### 5.1 @pytest.mark.parametrize 基础

参数化测试允许你用一个测试函数跑多组输入数据，大幅减少重复代码。

```python
import pytest

# 基本语法：参数名 + 参数列表
@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

**运行结果**：

```bash
pytest test_param.py -v
# test_param.py::test_add[2-3-5] PASSED
# test_param.py::test_add[0-0-0] PASSED
# test_param.py::test_add[-1-1-0] PASSED
# test_param.py::test_add[100-200-300] PASSED
```

### 5.2 为参数命名（ids）

默认的参数 ID 是参数值的拼接，可以用 `ids` 参数自定义有意义的名称：

```python
import pytest

@pytest.mark.parametrize("input_str, expected", [
    ("hello", "HELLO"),
    ("", ""),
    ("123", "123"),
    ("Hello World", "HELLO WORLD"),
], ids=["lowercase", "empty_string", "digits", "mixed_case"])
def test_uppercase(input_str, expected):
    assert input_str.upper() == expected
```

**运行结果**：

```bash
pytest test_upper.py -v
# test_upper.py::test_uppercase[lowercase] PASSED
# test_upper.py::test_uppercase[empty_string] PASSED
# test_upper.py::test_uppercase[digits] PASSED
# test_upper.py::test_uppercase[mixed_case] PASSED
```

### 5.3 参数化 fixture

除了 `@pytest.mark.parametrize`，fixture 也可以参数化：

```python
import pytest

@pytest.fixture(params=[
    ("sqlite", "sqlite:///:memory:"),
    ("postgresql", "postgresql://localhost/test"),
    ("mysql", "mysql://localhost/test"),
], ids=["sqlite", "postgres", "mysql"])
def db_config(request):
    return {"engine": request.param[0], "url": request.param[1]}

def test_db_connection(db_config):
    assert db_config["url"] is not None
```

### 5.4 多层参数化（参数组合）

多个 parametrize 装饰器会产生笛卡尔积：

```python
import pytest

@pytest.mark.parametrize("x", [1, 2, 3])
@pytest.mark.parametrize("y", [10, 20])
def test_multiply(x, y):
    assert x * y in [10, 20, 20, 40, 30, 60]
```

**运行结果**：

```bash
# 6 个测试用例：
# test_multiply[1-10], test_multiply[1-20]
# test_multiply[2-10], test_multiply[2-20]
# test_multiply[3-10], test_multiply[3-20]
```

### 5.5 使用 pytest.param 增强参数

`pytest.param()` 可以为单个参数设置标记：

```python
import pytest

@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    pytest.param(0, 0, 0, marks=pytest.mark.smoke),
    pytest.param(-1, 1, 0, marks=pytest.mark.xfail(reason="已知问题")),
    pytest.param(100, 200, 300, id="large_numbers"),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### 5.6 参数化中的 None 和复杂对象

```python
import pytest

# None 和空值参数化
@pytest.mark.parametrize("value, expected", [
    (None, None),
    ("", ""),
    ([], []),
    ({}, {}),
    (0, 0),
    (False, False),
])
def test_empty_values(value, expected):
    assert value == expected

# 复杂对象参数化
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def is_adult(self):
        return self.age >= 18

@pytest.mark.parametrize("user, expected", [
    (User("Alice", 20), True),
    (User("Bob", 15), False),
    (User("Charlie", 18), True),
])
def test_is_adult(user, expected):
    assert user.is_adult() == expected
```

### 5.7 参数化最佳实践

```python
# ✅ 好的参数化：数据和逻辑分离
import pytest

# 测试数据独立维护
ADD_TEST_CASES = [
    pytest.param(2, 3, 5, id="positive_positive"),
    pytest.param(-1, 1, 0, id="negative_positive"),
    pytest.param(0, 0, 0, id="zeros"),
    pytest.param(1000000, 2000000, 3000000, id="large_numbers"),
]

@pytest.mark.parametrize("a, b, expected", ADD_TEST_CASES)
def test_add(a, b, expected):
    assert add(a, b) == expected

# ❌ 不好的参数化：测试数据混在装饰器中，难以维护
# @pytest.mark.parametrize("a, b, expected", [
#     (2, 3, 5), (-1, 1, 0), (0, 0, 0), (1000000, 2000000, 3000000),
#     (1, 2, 3), (4, 5, 9), (10, 20, 30), ...
# ])
```

> ✅ 最佳实践：参数化测试用例数量适中（5-20组）。过多的参数化会导致测试报告冗长且难以定位问题。如果参数化空间很大（如所有组合），考虑用表驱动测试或随机测试（hypothesis 库）。

> 🎯 面试高频：`@pytest.mark.parametrize` 和参数化 fixture 的区别？——parametrize 作用于测试函数，直接注入参数；参数化 fixture 作用于 fixture，每个参数值都会执行一次 fixture setup。当需要为每组参数做不同的 setup 时用参数化 fixture，否则用 parametrize 更简单。

---

> 💡 **本章深度讲解**：参数化测试是消除测试重复的利器。没有参数化时，你需要为每组输入写一个测试函数；有了参数化，测试逻辑只写一次，数据驱动测试。`ids` 参数让测试报告可读；`pytest.param()` 让单个用例可以加标记；多层 parametrize 产生笛卡尔积，适合组合测试。在实际项目中，参数化测试通常占单元测试的 30-50%。
>
> **📝 精简总结**：
> - 核心概念：parametrize、ids、参数化 fixture、pytest.param
> - 关键原理：参数名匹配；笛卡尔积组合；每个参数值生成独立测试用例
> - 常用操作：`@pytest.mark.parametrize("a,b", [...])`；`ids=[...]`；`pytest.param(..., marks=...)`
> - 最佳实践：数据和逻辑分离；合理使用 ids 让报告可读；控制参数化数量
> - 常见坑点：参数化过多导致报告冗长；笛卡尔积爆炸
> - 面试高频：parametrize vs 参数化 fixture；多层 parametrize 的笛卡尔积

### 🎯 梯度练习题

**基础题（⭐）**
1. 写出参数化测试，测试 `abs()` 函数对负数、正数和零的行为。
   - 答案：`@pytest.mark.parametrize("x, expected", [(-5, 5), (3, 3), (0, 0)])`
2. `ids` 参数的作用是什么？
   - 答案：为参数化测试用例提供人类可读的名称。

**进阶题（⭐⭐）**
1. 两个 parametrize 装饰器叠在一起会产生多少个测试用例？
   - 思考方向：笛卡尔积；参数数量相乘。
2. 什么时候应该用参数化 fixture 而不是 parametrize？
   - 思考方向：每组参数需要不同的 setup；setup 成本高；需要 teardown。

**实战题（⭐⭐⭐）**
- **背景**：你有一个密码验证函数 `validate_password(pwd: str) -> bool`。
- **需求**：为它编写全面的参数化测试。
- **要求**：① 测试长度边界（<8, =8, >8）；② 测试无数字/有数字；③ 测试无大写/有大写；④ 测试空字符串；⑤ 每个用例有描述性 ids。
- **验收标准**：覆盖所有边界情况；测试报告清晰可读。
- **提示**：用 `pytest.param()` 和 `id` 参数命名每个用例。

---

## 六、标记与分组（mark / skip / xfail）

### 6.1 自定义标记

标记（mark）是给测试贴标签的机制，用于筛选和分组测试：

```python
import pytest
import time

# 定义标记的测试
@pytest.mark.slow
def test_large_dataset_processing():
    """慢速测试：处理大数据集"""
    time.sleep(2)
    result = process_large_data()
    assert result is not None

@pytest.mark.integration
def test_database_integration():
    """集成测试：需要数据库"""
    assert database.ping() == True

@pytest.mark.unit
def test_unit_logic():
    """单元测试：纯逻辑"""
    assert add(1, 2) == 3
```

**在 pytest.ini 中注册标记**（避免 Pytest 警告）：

```ini
# pytest.ini
[pytest]
markers =
    slow: 慢速测试（处理大数据集，默认跳过）
    integration: 集成测试（需要外部服务）
    unit: 单元测试（纯逻辑，快速）
    smoke: 冒烟测试（核心功能快速验证）
```

### 6.2 按标记筛选测试

```bash
# 只运行 unit 标记的测试
pytest -m unit -v

# 运行 slow 标记的测试
pytest -m slow -v

# 排除 slow 测试
pytest -m "not slow" -v

# 运行 unit 或 integration
pytest -m "unit or integration" -v

# 运行 unit 且非 slow
pytest -m "unit and not slow" -v

# 预期输出（pytest -m "not slow"）：
# 12 passed, 2 deselected in 0.5s
```

### 6.3 skip 跳过测试

```python
import pytest
import sys
import platform

# 无条件跳过
@pytest.mark.skip(reason="功能尚未实现，等 API 稳定后再测试")
def test_future_feature():
    assert future_feature() == True

# 条件跳过：满足条件时跳过
@pytest.mark.skipif(sys.version_info < (3, 10), reason="需要 Python 3.10+")
def test_python310_feature():
    match = {"key": "value"}
    assert match["key"] == "value"

# 平台相关跳过
@pytest.mark.skipif(platform.system() != "Windows", reason="仅 Windows 平台")
def test_windows_specific():
    assert get_windows_path() == "C:\\"

# 运行时跳过
def test_optional_dependency():
    try:
        import optional_module
    except ImportError:
        pytest.skip("optional_module 未安装")

    optional_module.do_something()
```

### 6.4 xfail 预期失败

`xfail` 表示"这个测试预期会失败"——测试运行但不报告为失败：

```python
import pytest

# 标记为预期失败（已知 bug）
@pytest.mark.xfail(reason="已知 bug #123：负数除以正数结果错误")
def test_division_bug():
    assert divide(-1, 2) == -0.5  # 当前返回 0

# xfail(strict=True)：如果意外通过（bug 修复了），报告为失败
# 这样你就知道该移除 xfail 标记了
@pytest.mark.xfail(reason="等修复后移除", strict=True)
def test_recently_fixed_bug():
    assert recently_fixed_function() == expected
```

**运行结果**：

```bash
pytest test_xfail.py -v
# test_xfail.py::test_division_bug XFAIL (已知 bug #123)
# 如果 bug 修复了，会显示 XPASS（unexpectedly passing）
# strict=True 时 XPASS 会变成 FAILED
```

> ❌ 常见坑点：xfail 和 skip 的区别——skip 是"不运行这个测试"，xfail 是"运行这个测试但预期失败"。xfail 的价值在于：当 bug 修复后你会收到通知（XPASS），提醒你移除 xfail 标记。长期保留 xfail 标记会让真正的 bug 被忽略。

### 6.5 标记传递与组合

```python
# 标记可以堆叠
@pytest.mark.slow
@pytest.mark.integration
def test_slow_integration():
    time.sleep(5)
    assert run_integration_test()

# 类级别的标记（应用于类中所有测试方法）
@pytest.mark.integration
class TestDatabase:
    def test_insert(self):
        ...  # 自动获得 integration 标记

    def test_query(self):
        ...  # 自动获得 integration 标记

# 模块级别的标记（应用于整个文件）
pytestmark = [pytest.mark.integration, pytest.mark.slow]

def test_module_marked_1():
    ...  # 自动获得 integration + slow 标记

def test_module_marked_2():
    ...  # 自动获得 integration + slow 标记
```

### 6.6 标记实战：CI 中的测试分层

```python
# tests/test_api.py
import pytest

@pytest.mark.smoke
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200

@pytest.mark.smoke
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200

@pytest.mark.unit
def test_add():
    assert add(1, 2) == 3

@pytest.mark.integration
def test_full_user_flow(client, db):
    # 创建用户 -> 登录 -> 获取信息 -> 删除
    user = create_user(client)
    token = login(client, user)
    info = get_user(client, token)
    assert info["email"] == user["email"]
```

```yaml
# CI 中的分层运行策略
# .github/workflows/test.yml
jobs:
  smoke:
    steps:
      - run: pytest -m smoke  # 快速验证（<30s）

  unit:
    steps:
      - run: pytest -m unit  # 单元测试（<1min）

  integration:
    needs: [unit]
    steps:
      - run: pytest -m integration  # 集成测试（几分钟）
```

---

> 💡 **本章深度讲解**：标记系统是大型测试套件的组织工具。当测试数量从几十增长到几千时，你需要能够"只跑快速测试""只跑冒烟测试""跳过已知 bug"。mark/skip/xfail 三个标记分别解决"分组筛选""暂时跳过""已知问题跟踪"三个场景。在 CI 中，标记让你实现分层测试策略——快速反馈（smoke）+ 全面验证（unit）+ 深度集成（integration）。
>
> **📝 精简总结**：
> - 核心概念：mark、skip、skipif、xfail、pytestmark
> - 关键原理：标记存储在测试节点上；-m 表达式筛选；xfail strict 检测修复
> - 常用操作：`@pytest.mark.slow`；`-m "not slow"`；`@pytest.mark.skipif(...)`
> - 最佳实践：注册所有标记；CI 分层运行；xfail 加 strict=True
> - 常见坑点：未注册标记导致警告；xfail 长期不清理
> - 面试高频：skip vs xfail 区别；-m 表达式；pytestmark 模块级标记

### 🎯 梯度练习题

**基础题（⭐）**
1. `skip` 和 `xfail` 的区别是什么？
   - 答案：skip 不运行测试；xfail 运行测试但预期失败。
2. 如何只运行标记为 `slow` 的测试？
   - 答案：`pytest -m slow`。

**进阶题（⭐⭐）**
1. `xfail(strict=True)` 的作用是什么？
   - 思考方向：bug 修复后 XPASS 变 FAILED；提醒移除 xfail。
2. 为什么需要在 pytest.ini 中注册标记？
   - 思考方向：防止拼写错误；--strict-markers 模式；文档化标记。

**实战题（⭐⭐⭐）**
- **背景**：你的项目有 200 个测试，其中 50 个是慢速集成测试。
- **需求**：配置标记系统让 CI 快速反馈。
- **要求**：① 标记 slow 测试；② 标记 smoke 测试；③ CI 先跑 smoke+unit；④ 通过后再跑 slow。
- **验收标准**：CI 总时间 <5 分钟；失败时快速定位。
- **提示**：用 pytest.ini 注册标记；用 GitHub Actions 的 needs 依赖。

---

## 七、测试配置：pytest.ini / conftest.py / pyproject.toml

### 7.1 配置文件优先级

Pytest 按以下优先级查找配置文件（先找到的优先）：

1. `pytest.ini`（最常用）
2. `pyproject.toml`（PEP 621 标准，推荐新项目使用）
3. `tox.ini`
4. `setup.cfg`

### 7.2 pyproject.toml 配置（推荐）

```toml
# pyproject.toml
[tool.pytest.ini_options]
# 测试搜索路径
testpaths = ["tests"]

# 文件/类/函数匹配规则
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# 默认命令行参数
addopts = "-v --tb=short --strict-markers"

# 注册标记
markers = [
    "slow: 慢速测试（处理大数据集）",
    "integration: 集成测试（需要外部服务）",
    "unit: 单元测试（纯逻辑）",
    "smoke: 冒烟测试（核心功能快速验证）",
]

# pytest-asyncio 配置
asyncio_mode = "auto"

# 覆盖率配置（pytest-cov）
[tool.coverage.run]
source = ["my_project"]
omit = ["*/tests/*", "*/migrations/*", "*/alembic/*"]

[tool.coverage.report]
show_missing = true
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if __name__ == .__main__.:",
]
```

### 7.3 pytest.ini 配置

```ini
# pytest.ini（传统方式，与 pyproject.toml 二选一）
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: 慢速测试
    integration: 集成测试
    unit: 单元测试
asyncio_mode = auto
```

### 7.4 conftest.py 进阶配置

conftest.py 不仅可以放 fixture，还可以放 hook 函数：

```python
# tests/conftest.py
import pytest

# Hook：在收集测试之前调用
def pytest_collection_modifyitems(config, items):
    """修改收集到的测试列表"""
    # 自动给所有 tests/integration/ 下的测试添加 integration 标记
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

# Hook：报告每个测试的结果
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        # 测试失败时自动截图（用于 UI 测试）
        if hasattr(item, "browser"):
            screenshot_path = f"screenshots/{item.name}.png"
            item.browser.save_screenshot(screenshot_path)
```

### 7.5 常用命令行参数速查

```bash
# 基础运行
pytest                          # 运行所有测试
pytest -v                       # 详细输出
pytest -q                       # 简洁输出
pytest -x                       # 第一个失败就停止
pytest --maxfail=5              # 失败 5 次后停止

# 测试选择
pytest tests/test_api.py        # 指定文件
pytest tests/test_api.py::test_create_user  # 指定函数
pytest -k "user and not slow"   # 按关键字
pytest -m "integration"         # 按标记
pytest --lf                     # 只运行上次失败的（last failed）
pytest --ff                     # 先运行失败的，再运行其他的（failed first）
pytest --nf                     # 只运行上次通过的（new failed）

# 输出格式
pytest --tb=short               # 简洁 traceback
pytest --tb=long                # 完整 traceback
pytest --tb=no                  # 不显示 traceback
pytest -l                       # 失败时显示局部变量
pytest --showlocals              # 显示局部变量

# 调试
pytest --pdb                    # 失败时进入 PDB 调试器
pytest --trace                  # 每个测试开始时进入调试器
pytest --trace-test=test_func   # 指定测试进入调试器

# 并行与随机
pytest -n auto                  # 并行运行（需要 pytest-xdist）
pytest -n 4                     # 指定 4 个 worker
pytest --randomly-seed=12345    # 随机顺序运行（需要 pytest-randomly）
```

> ❌ 常见坑点：`addopts` 中的参数和命令行参数会叠加。如果 `addopts` 里写了 `-v`，命令行再加 `-q` 会冲突。Pytest 以后者为准，但可能产生意想不到的行为。建议 addopts 只放固定选项，动态选项从命令行传入。

---

> 💡 **本章深度讲解**：配置系统是 Pytest 工程化的基础。pyproject.toml 统一了所有 Python 工具的配置（Poetry、pytest、mypy、ruff），避免了配置文件碎片化。conftest.py 不仅是 fixture 仓库，还是 hook 函数的载体，可以自定义测试收集、报告和执行行为。掌握这些配置项后，你可以将 Pytest 调整到团队需要的工作方式。
>
> **📝 精简总结**：
> - 核心概念：pyproject.toml 配置、addopts、markers、conftest hook
> - 关键原理：配置文件优先级；conftest 层级覆盖；hook 函数扩展
> - 常用操作：`addopts`；`markers` 注册；`-k`/`-m`/`--lf` 选择
> - 最佳实践：用 pyproject.toml 统一配置；注册所有标记；--strict-markers
> - 常见坑点：addopts 与命令行冲突；未注册标记
> - 面试高频：配置文件优先级；conftest.py 的作用；--strict-markers

### 🎯 梯度练习题

**基础题（⭐）**
1. Pytest 配置文件有哪几种格式？优先级如何？
   - 答案：pytest.ini > pyproject.toml > tox.ini > setup.cfg。
2. `--lf` 参数的作用是什么？
   - 答案：只运行上次失败的测试（last failed）。

**进阶题（⭐⭐）**
1. `addopts` 的作用是什么？为什么推荐放在 pyproject.toml 而不是命令行？
   - 思考方向：团队统一配置；减少 CI 脚本中的重复参数。
2. conftest.py 中可以定义哪些类型的内容？
   - 思考方向：fixture；hook 函数；pytestmark；临时工具函数。

**实战题（⭐⭐⭐）**
- **背景**：团队新成员抱怨"每次运行 pytest 都要输入一长串参数"。
- **需求**：将常用配置固化到项目中。
- **要求**：① 默认 verbose 输出；② 默认显示简短 traceback；③ 严格检查标记；④ 注册 slow/unit/integration/smoke 标记。
- **验收标准**：直接 `pytest` 命令即可获得一致的输出。
- **提示**：配置放在 pyproject.toml 的 `[tool.pytest.ini_options]` 段。

---

## 八、Mock 与 Monkeypatch

### 8.1 为什么需要 Mock

在单元测试中，你只想测试当前函数的逻辑，不想真正调用数据库、外部 API 或发送邮件。Mock 就是用假对象替换真实对象，隔离被测代码的外部依赖。

```python
# 被测代码：user_service.py
class UserService:
    def __init__(self, db, email_client):
        self.db = db
        self.email_client = email_client

    def register_user(self, email, password):
        # 1. 创建用户
        user = self.db.create_user(email, password)
        # 2. 发送欢迎邮件
        self.email_client.send(
            to=email,
            subject="欢迎注册",
            body="感谢注册我们的服务"
        )
        return user
```

```python
# 测试：我们不想真的发邮件，也不想真的写数据库
def test_register_user(user_service, mock_db, mock_email):
    # mock_db.create_user 返回假用户
    mock_db.create_user.return_value = {"id": 1, "email": "test@example.com"}

    result = user_service.register_user("test@example.com", "pass123")

    # 验证数据库被调用了
    mock_db.create_user.assert_called_once_with("test@example.com", "pass123")
    # 验证邮件被发送了
    mock_email.send.assert_called_once_with(
        to="test@example.com",
        subject="欢迎注册",
        body="感谢注册我们的服务"
    )
    # 验证返回值
    assert result["id"] == 1
```

### 8.2 pytest-mock 插件

`pytest-mock` 提供了 `mocker` fixture，简化了 Mock 的使用：

```python
# 安装：poetry add --group dev pytest-mock

def test_send_email(mocker):
    # mocker.patch 替换指定路径的函数
    # 注意：patch 的是"使用处"而非"定义处"
    mock_send = mocker.patch("app.services.email.send_email")
    mock_send.return_value = True

    # 调用被测函数
    result = register_user("test@example.com", "password123")

    # 验证 mock 被调用
    assert result.success
    mock_send.assert_called_once_with(
        to="test@example.com",
        subject="欢迎注册",
    )
```

### 8.3 mock.patch 的关键规则：Where to patch

```python
# ❌ 错误：patch 的是函数定义的位置
# 如果 email_service.py 中定义了 send_email：
# app/services/email_service.py
def send_email(to, subject, body):
    ...

# 正确做法：patch 使用处，不是定义处
# app/services/user_service.py 中 import 了 send_email：
# from app.services.email_service import send_email
# user_service.py 中有自己的 send_email 引用

# ✅ 正确：patch 使用处
mocker.patch("app.services.user_service.send_email")

# ❌ 错误：patch 定义处（不会影响 user_service 中的引用）
mocker.patch("app.services.email_service.send_email")
```

> 🎯 面试高频：mock.patch 应该在哪里 patch？——**Patch where it's used, not where it's defined.** 因为 Python 的 import 是绑定引用，当 `user_service.py` 执行 `from email_service import send_email` 时，它创建了一个自己的 `send_email` 引用。如果你 patch `email_service.send_email`，`user_service` 中的引用不会变。你必须 patch `user_service.send_email`。

### 8.4 Mock 的常用断言方法

```python
def test_mock_assertions(mocker):
    mock_func = mocker.patch("module.function")

    # 调用被测代码
    some_function()

    # 断言调用次数
    mock_func.assert_called_once()           # 恰好调用一次
    mock_func.assert_called_with(arg1, arg2)  # 最后一次调用的参数
    mock_func.assert_any_call(arg1, arg2)    # 至少一次用这些参数调用

    # 断言未被调用
    mock_func.assert_not_called()

    # 获取所有调用记录
    all_calls = mock_func.call_args_list
    first_call = mock_func.call_args_list[0]

    # 调用次数
    assert mock_func.call_count == 3
```

### 8.5 side_effect：模拟异常和序列

```python
def test_retry_logic(mocker):
    # side_effect 可以抛出异常
    mock_get = mocker.patch("httpx.get")

    # 前两次调用失败，第三次成功
    mock_get.side_effect = [
        ConnectionError("第一次失败"),
        ConnectionError("第二次失败"),
        MagicMock(status_code=200, json=lambda: {"data": "ok"}),
    ]

    # 调用带重试逻辑的函数
    result = fetch_with_retry("https://api.example.com", max_retries=3)

    assert result == {"data": "ok"}
    assert mock_get.call_count == 3  # 重试了 3 次
```

### 8.6 Monkeypatch：修改环境变量和系统函数

`monkeypatch` fixture 用于安全地修改环境变量、字典、属性等，测试结束后自动恢复：

```python
def test_env_variable(monkeypatch):
    # 设置环境变量
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    # 测试读取环境变量的函数
    config = load_config()
    assert config.database_url == "sqlite:///:memory:"

    # 测试结束后，monkeypatch 自动恢复环境变量
    # os.environ["DATABASE_URL"] 回到原始值

def test_dict_modification(monkeypatch):
    original = {"key": "value"}

    # 修改字典（自动恢复）
    monkeypatch.setitem(original, "key", "modified")
    assert original["key"] == "modified"

def test_attribute(monkeypatch):
    class App:
        version = "1.0.0"

    # 修改对象属性
    monkeypatch.setattr(App, "version", "2.0.0")
    assert App.version == "2.0.0"

    # 测试结束后自动恢复为 "1.0.0"

def test_chdir(monkeypatch, tmp_path):
    # 改变当前工作目录
    monkeypatch.chdir(tmp_path)
    # 所有用相对路径的代码都会在 tmp_path 中运行
    # 测试结束后自动恢复原工作目录
```

### 8.7 完整的 API Mock 示例

```python
# tests/test_api_client.py
import pytest
from unittest.mock import MagicMock

class TestAPIClient:
    def test_get_user_success(self, mocker):
        # Mock httpx.AsyncClient.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1, "name": "Alice", "email": "alice@example.com"
        }
        mock_get = mocker.patch("httpx.AsyncClient.get")
        mock_get.return_value = mock_response

        client = APIClient("https://api.example.com")
        user = client.get_user(1)

        assert user["name"] == "Alice"
        mock_get.assert_called_once_with("https://api.example.com/users/1")

    def test_get_user_not_found(self, mocker):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get = mocker.patch("httpx.AsyncClient.get")
        mock_get.return_value = mock_response

        client = APIClient("https://api.example.com")
        with pytest.raises(UserNotFoundError):
            client.get_user(999)

    def test_network_error_retries(self, mocker):
        mock_get = mocker.patch("httpx.AsyncClient.get")
        # 模拟网络错误
        mock_get.side_effect = ConnectionError("Network down")

        client = APIClient("https://api.example.com")
        result = client.get_user_with_retry(1, max_retries=3)

        assert result is None
        assert mock_get.call_count == 3  # 重试 3 次
```

---

> 💡 **本章深度讲解**：Mock 是单元测试的核心技术——你必须隔离被测代码的外部依赖，否则你的测试就变成了集成测试。`mocker.patch` 的"patch 使用处而非定义处"规则是最容易踩的坑。`side_effect` 模拟异常和重试场景；`monkeypatch` 安全地修改环境变量和系统状态。掌握这些工具后，你可以为任何代码写出快速、可靠的单元测试。
>
> **📝 精简总结**：
> - 核心概念：Mock、patch、side_effect、monkeypatch
> - 关键原理：替换对象引用；断言调用参数；自动 teardown 恢复
> - 常用操作：`mocker.patch("module.func")`；`assert_called_once_with()`；`monkeypatch.setenv()`
> - 最佳实践：patch 使用处；验证交互而非内部状态；少用 mock 多用真实对象
> - 常见坑点：patch 定义处而非使用处；过度 mock 导致测试无意义
> - 面试高频：where to patch；side_effect vs return_value；mock vs stub vs spy

### 🎯 梯度练习题

**基础题（⭐）**
1. `mocker.patch` 应该 patch 定义处还是使用处？
   - 答案：使用处（where it's used, not where it's defined）。
2. `monkeypatch` 和直接修改环境变量有什么区别？
   - 答案：monkeypatch 测试后自动恢复原状态。

**进阶题（⭐⭐）**
1. `side_effect` 和 `return_value` 的区别是什么？
   - 思考方向：return_value 固定返回值；side_effect 可以抛出异常或按序列返回。
2. 为什么"过度 mock"会导致测试无意义？
   - 思考方向：mock 了所有东西后测试的是 mock 的交互；不是真实代码行为。

**实战题（⭐⭐⭐）**
- **背景**：你有一个支付服务 `PaymentService.charge(amount, card)`，调用外部支付 API。
- **需求**：为 charge 方法写单元测试。
- **要求**：① 成功支付场景；② 余额不足场景；③ 网络超时重试场景；④ 不真的调用支付 API。
- **验收标准**：所有测试快速运行；验证了重试逻辑；验证了错误处理。
- **提示**：用 side_effect 模拟异常和多次调用。

---

## 九、异常测试与异步测试

### 9.1 pytest.raises 异常测试

```python
import pytest

# 基本用法：验证抛出了指定异常
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)

# 匹配异常消息
def test_value_error_message():
    with pytest.raises(ValueError, match="must be positive"):
        set_age(-5)

# match 使用正则表达式
def test_file_not_found():
    with pytest.raises(FileNotFoundError, match=r"No such file.*missing\.txt"):
        open("missing.txt")

# 获取异常对象的详细信息
def test_exception_details():
    with pytest.raises(ValueError) as exc_info:
        validate_email("not-an-email")

    # exc_info.value 是实际抛出的异常对象
    exception = exc_info.value
    assert "Invalid email" in str(exception)
    assert exc_info.type is ValueError
    assert exc_info.value.args[0] == "Invalid email format"
```

### 9.2 异常测试的最佳实践

```python
# ✅ 好的异常测试：精确验证异常类型和消息
def test_invalid_email_raises_value_error():
    with pytest.raises(ValueError, match="Invalid email format: .*"):
        validate_email("bad-email")

# ❌ 不好的异常测试：太宽泛
def test_bad():
    with pytest.raises(Exception):  # 太宽泛，任何异常都算通过
        validate_email("bad-email")

# ❌ 不好的异常测试：没有验证消息
def test_bad2():
    with pytest.raises(ValueError):
        validate_email("bad-email")  # 可能因为任何原因抛出 ValueError
```

> ✅ 最佳实践：异常测试应该精确到异常类型 + 消息匹配。使用 `match` 参数验证异常消息，确保抛出的是"预期的异常"而不是"任何异常"。

### 9.3 pytest.raises 作为函数

```python
# 除了上下文管理器，pytest.raises 也可以直接调用
def test_simple():
    pytest.raises(ZeroDivisionError, divide, 1, 0)
    # 等价于：
    # with pytest.raises(ZeroDivisionError):
    #     divide(1, 0)
```

### 9.4 异步测试（pytest-asyncio）

```bash
# 安装
poetry add --group dev pytest-asyncio
```

```python
# tests/test_async.py
import pytest
import asyncio

# 标记异步测试
@pytest.mark.asyncio
async def test_async_add():
    result = await async_add(2, 3)
    assert result == 5

# 多个异步测试
@pytest.mark.asyncio
async def test_async_fetch():
    data = await fetch_data("https://api.example.com/data")
    assert data["status"] == "ok"

@pytest.mark.asyncio
async def test_async_db():
    user = await get_user_from_db(1)
    assert user.name == "Alice"
```

### 9.5 自动异步模式

在 pyproject.toml 中配置 `asyncio_mode = "auto"`，Pytest 会自动识别 `async def` 测试函数，不需要 `@pytest.mark.asyncio`：

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

```python
# 配置 auto 后，不需要 @pytest.mark.asyncio
async def test_auto_detection():
    result = await async_computation()
    assert result == 42
```

### 9.6 异步 fixture

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture(scope="session")
def event_loop():
    """会话级事件循环（旧版 pytest-asyncio 需要）"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_engine():
    """异步数据库引擎"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def async_db_session(async_engine):
    """异步数据库会话"""
    async_session = AsyncSession(async_engine, expire_on_commit=False)
    yield async_session
    await async_session.close()
```

### 9.7 超时测试

```python
# 安装 pytest-timeout
# poetry add --group dev pytest-timeout

# 命令行设置超时
# pytest --timeout=5  # 每个测试最多 5 秒

# 装饰器设置超时
@pytest.mark.timeout(10)
def test_long_running():
    result = process_large_data()
    assert result is not None

# 异步测试超时
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_async_timeout():
    result = await async_api_call()
    assert result is not None
```

---

> 💡 **本章深度讲解**：异常测试确保代码在错误场景下正确失败。`pytest.raises` 的 `match` 参数让你不仅验证"抛了异常"，还验证"抛了正确的异常"。异步测试是现代 Python Web 开发的标配——FastAPI、asyncio SQLAlchemy 全是异步的，pytest-asyncio 让你用同样的心智模型测试异步代码。session 级别的异步 fixture 避免了每个测试都创建数据库连接的开销。
>
> **📝 精简总结**：
> - 核心概念：pytest.raises、match、asyncio marker、异步 fixture
> - 关键原理：上下文管理器捕获异常；asyncio_mode auto 自动识别
> - 常用操作：`pytest.raises(Error, match="...")`；`@pytest.mark.asyncio`；`asyncio_mode = "auto"`
> - 最佳实践：精确匹配异常消息；session 级异步连接；设置超时
> - 常见坑点：太宽泛的 `pytest.raises(Exception)`；忘记 asyncio marker
> - 面试高频：pytest.raises match 参数；异步 fixture 设计；event_loop scope

### 🎯 梯度练习题

**基础题（⭐）**
1. 写出测试：验证 `int("abc")` 抛出 ValueError。
   - 答案：`with pytest.raises(ValueError): int("abc")`
2. pytest-asyncio 的 `asyncio_mode = "auto"` 有什么好处？
   - 答案：自动识别 async def 测试函数，不需要 @pytest.mark.asyncio。

**进阶题（⭐⭐）**
1. 为什么 `pytest.raises(Exception)` 是不好的实践？
   - 思考方向：任何异常都算通过；可能掩盖了非预期错误。
2. 异步 fixture 为什么需要 session 级别的 event_loop？
   - 思考方向：事件循环线程绑定；function 级别会导致 "Event loop is closed" 错误。

**实战题（⭐⭐⭐）**
- **背景**：你有一个异步 API 客户端，需要测试成功、404 和超时三种场景。
- **需求**：编写完整的异步测试。
- **要求**：① 成功返回数据；② 404 返回 None；③ 超时重试 3 次后失败；④ 每个测试有独立 mock。
- **验收标准**：异步测试通过；超时逻辑被验证；无事件循环泄漏。
- **提示**：用 `pytest.mark.asyncio` + `mocker.patch` 组合。

---

## 十、插件系统：cov / xdist / mock / asyncio

### 10.1 插件生态概览

Pytest 的强大在于其插件生态。以下是最常用的插件：

| 插件 | 用途 | 安装命令 |
|------|------|---------|
| `pytest-asyncio` | 异步测试支持 | `poetry add --group dev pytest-asyncio` |
| `pytest-cov` | 测试覆盖率统计 | `poetry add --group dev pytest-cov` |
| `pytest-mock` | Mock 简化（mocker fixture） | `poetry add --group dev pytest-mock` |
| `pytest-xdist` | 并行运行测试 | `poetry add --group dev pytest-xdist` |
| `pytest-randomly` | 随机顺序运行 | `poetry add --group dev pytest-randomly` |
| `pytest-html` | HTML 测试报告 | `poetry add --group dev pytest-html` |
| `pytest-timeout` | 测试超时 | `poetry add --group dev pytest-timeout` |
| `pytest-benchmark` | 性能基准测试 | `poetry add --group dev pytest-benchmark` |
| `pytest-env` | 环境变量管理 | `poetry add --group dev pytest-env` |
| `factory_boy` | 测试数据工厂 | `poetry add --group dev factory_boy` |

### 10.2 pytest-cov：测试覆盖率

```bash
# 运行测试并生成覆盖率报告
pytest --cov=my_project --cov-report=term-missing

# 输出示例：
# Name                  Stmts   Miss  Cover   Missing
# ---------------------------------------------------
# my_project/__init__       5      0   100%
# my_project/calculator    20      5    75%   45-48
# my_project/api           50     20    60%   100-120
# ---------------------------------------------------
# TOTAL                    75     25    67%
```

```bash
# 生成 HTML 报告（可在浏览器中查看哪些行未覆盖）
pytest --cov=my_project --cov-report=html
# 打开 htmlcov/index.html

# 生成 XML 报告（CI 上传用）
pytest --cov=my_project --cov-report=xml
# 生成 coverage.xml

# 覆盖率低于 80% 则失败
pytest --cov=my_project --cov-fail-under=80
```

```toml
# pyproject.toml 中配置覆盖率
[tool.coverage.run]
source = ["my_project"]
omit = ["*/tests/*", "*/migrations/*", "*/alembic/*"]
branch = true  # 分支覆盖率（if/else 都算）

[tool.coverage.report]
show_missing = true
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
]
```

> ❌ 常见坑点：覆盖率 100% 不代表测试质量好。覆盖率只衡量"代码是否被执行到"，不衡量"断言是否充分"。一个只调用函数但不验证返回值的测试也能增加覆盖率。**追求覆盖率数字不如追求测试的有效性。**

### 10.3 pytest-xdist：并行运行

```bash
# 自动检测 CPU 核心数，并行运行
pytest -n auto

# 指定 worker 数量
pytest -n 4

# 分布式模式：load（自动分配）
pytest -n auto --dist=load

# 每个 worker 运行不同的测试文件（更稳定）
pytest -n auto --dist=loadfile
```

> ⚠️ 新手注意：并行运行测试要求测试之间没有共享状态。如果你的测试依赖执行顺序（如测试 A 创建数据，测试 B 使用），并行运行会偶发失败。用 `pytest-randomly` 检测顺序依赖。

### 10.4 pytest-randomly：随机顺序检测依赖

```bash
# 安装
poetry add --group dev pytest-randomly

# 默认就会随机化测试顺序（每次种子不同）
pytest

# 指定种子（复现失败）
pytest --randomly-seed=12345

# 禁用随机化
pytest -p no:randomly
```

> ✅ 最佳实践：在 CI 中始终启用 pytest-randomly。它能在 CI 中持续检测测试间的隐式依赖。如果你的测试在随机顺序下偶发失败，说明测试间有数据污染或顺序依赖。

### 10.5 pytest-benchmark：性能基准测试

```python
# tests/test_performance.py

def test_sort_performance(benchmark):
    """基准测试：测量 sort 的性能"""
    data = list(range(10000))

    # benchmark 会运行函数多次并统计
    result = benchmark(sorted, data)

    assert result == sorted(data)
```

```bash
# 运行基准测试
pytest test_performance.py --benchmark-only

# 输出：
# Name (time in ms)           Min    Max   Mean   StdDev
# --------------------------------------------------------
# test_sort_performance     1.23   1.56   1.35    0.10
```

### 10.6 pytest-env：环境变量管理

```toml
# pyproject.toml
[tool.pytest_env]
TESTING = "true"
DATABASE_URL = "sqlite:///:memory:"
DEBUG = "false"
```

```python
# 所有测试自动获得这些环境变量
import os

def test_env():
    assert os.environ["TESTING"] == "true"
```

### 10.7 factory_boy：测试数据工厂

```python
# factories.py
import factory
from my_project.models import User

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    email = factory.Faker("email")
    age = factory.Faker("random_int", min=18, max=80)
    is_active = True
```

```python
# 在测试中使用
def test_user_creation(db_session):
    # 创建一个随机用户
    user = UserFactory()
    assert user.id is not None
    assert "@" in user.email

    # 创建批量用户
    users = UserFactory.create_batch(10)
    assert len(users) == 10

    # 自定义属性
    admin = UserFactory(role="admin", is_active=False)
    assert admin.role == "admin"
```

---

> 💡 **本章深度讲解**：插件系统是 Pytest 生态繁荣的根本原因。每个插件解决一个特定问题：cov 解决覆盖率可视化，xdist 解决执行速度，randomly 解决测试依赖，benchmark 解决性能回归。在实际项目中，你通常会同时使用 5-10 个插件，它们通过 conftest.py 和 fixture 系统无缝协作。理解插件机制后，你甚至可以写自己的插件来定制测试流程。
>
> **📝 精简总结**：
> - 核心概念：pytest-cov、pytest-xdist、pytest-randomly、pytest-benchmark、factory_boy
> - 关键原理：插件通过 hook 函数扩展 Pytest；fixture 注入额外能力
> - 常用操作：`--cov=pkg`；`-n auto`；`--benchmark-only`；`UserFactory()`
> - 最佳实践：CI 中启用 random 检测依赖；追求有效测试而非覆盖率数字
> - 常见坑点：并行运行有顺序依赖的测试；覆盖率 100% 但测试无效
> - 面试高频：pytest-xdist 并行前提；覆盖率的意义和局限；factory_boy vs fixture

### 🎯 梯度练习题

**基础题（⭐）**
1. `pytest --cov=my_project` 的作用是什么？
   - 答案：运行测试并生成 my_project 的覆盖率报告。
2. `pytest -n auto` 的前提条件是什么？
   - 答案：测试之间没有共享状态和顺序依赖。

**进阶题（⭐⭐）**
1. 为什么说"100% 覆盖率不代表测试充分"？
   - 思考方向：覆盖率只衡量执行到，不衡量断言；可能调用函数但不验证返回值。
2. pytest-randomly 如何帮助发现测试问题？
   - 思考方向：随机顺序暴露隐式依赖；偶发失败可通过 seed 复现。

**实战题（⭐⭐⭐）**
- **背景**：你的测试套件有 500 个测试，运行需要 10 分钟。
- **需求**：优化测试执行时间。
- **要求**：① 并行运行；② 分离慢速测试；③ CI 中先跑快速测试。
- **验收标准**：总时间 <3 分钟；失败时快速定位。
- **提示**：pytest-xdist 并行 + 标记 slow 测试分层运行。

---

## 十一、TDD 方法论与测试金字塔

### 11.1 TDD 红绿重构循环详解

TDD 不是"先写测试再写代码"那么简单，它有严格的纪律：

```mermaid
graph TD
    A[Red: 写一个失败的测试] --> B[看到测试失败<br/>确认测试有效]
    B --> C[Green: 写最少代码<br/>使测试通过]
    C --> D[看到测试通过<br/>确认功能可用]
    D --> E[Refactor: 重构代码<br/>改善结构]
    E --> F[测试仍然通过<br/>确认重构安全]
    F --> A
```

**TDD 三步纪律**：

| 步骤 | 做什么 | 不做什么 |
|------|--------|---------|
| **Red** | 写一个小测试，描述期望的行为 | 不写任何实现代码 |
| **Green** | 写最简单的代码让测试通过 | 不写多余的功能，不追求优雅 |
| **Refactor** | 消除重复，改善命名，提取函数 | 不改变外部行为，不增加新功能 |

### 11.2 TDD 实战：密码验证器

**Step 1: Red — 写第一个失败测试**

```python
# tests/test_password.py
def test_password_too_short():
    # 需求：密码至少 8 位
    assert validate_password("abc") == False
```

运行测试：

```bash
pytest tests/test_password.py -v
# 预期：FAILED（validate_password 未定义）
```

**Step 2: Green — 写最少代码**

```python
# my_project/password.py
def validate_password(password: str) -> bool:
    # 最简单的实现
    if len(password) < 8:
        return False
    return True
```

```bash
pytest tests/test_password.py -v
# 预期：PASSED
```

**Step 3: Refactor — 优化代码**

```python
# my_project/password.py（重构后）
def validate_password(password: str) -> bool:
    """验证密码强度。规则：至少 8 位。"""
    return len(password) >= 8
```

**Step 4: 新的 Red — 添加需求**

```python
def test_password_no_digit():
    # 新需求：密码必须包含数字
    assert validate_password("abcdefgh") == False

def test_valid_password():
    assert validate_password("abc12345") == True
```

**Step 5: 新的 Green — 更新实现**

```python
def validate_password(password: str) -> bool:
    has_min_length = len(password) >= 8
    has_digit = any(c.isdigit() for c in password)
    return has_min_length and has_digit
```

### 11.3 测试金字塔

```
           /\
          /  \        E2E 测试（少量，慢，贵）~10%
         /----\
        /      \      集成测试（适量）~20%
       /--------\
      /          \     单元测试（大量，快，便宜）~70%
     /------------\
```

| 测试类型 | 占比 | 速度 | 用途 | 例子 |
|---------|------|------|------|------|
| **单元测试** | 70% | <10ms | 函数/类级别纯逻辑 | 密码验证、字符串处理 |
| **集成测试** | 20% | <100ms | 数据库/API/服务交互 | 用户注册流程、API 端点 |
| **E2E 测试** | 10% | >1s | 完整用户流程 | Selenium 点击按钮 |

```python
# 单元测试示例（纯逻辑，无外部依赖）
def test_validate_password():
    assert validate_password("abc12345") == True
    assert validate_password("short") == False

# 集成测试示例（需要数据库）
@pytest.mark.integration
def test_user_registration_flow(db_session, client):
    # 创建用户 -> 登录 -> 获取信息
    response = client.post("/users/", json={"email": "test@test.com"})
    assert response.status_code == 201

# E2E 测试示例（浏览器自动化）
@pytest.mark.e2e
def test_user_login_page(browser):
    browser.get("https://example.com/login")
    browser.find_element_by_id("email").send_keys("test@test.com")
    browser.find_element_by_id("password").send_keys("pass123")
    browser.find_element_by_id("submit").click()
    assert "Welcome" in browser.page_source
```

> ✅ 最佳实践：测试金字塔的核心是"快速反馈"。70% 的测试应该在毫秒级完成，这样你可以在开发时频繁运行。E2E 测试慢且脆弱，只保留关键用户流程的 E2E 测试。

### 11.4 TDD 的常见误解

```python
# ❌ 误解1：TDD 是"先写测试"
# 正确：TDD 是"先写一个小测试，看它失败，再写最小代码通过"
# 重点是"小步快跑"，不是"先写测试"

# ❌ 误解2：TDD 让设计变差（因为你只写让测试通过的代码）
# 正确：Refactor 阶段就是改善设计的时机
# TDD 的纪律恰恰是"先让测试通过，再重构"

# ❌ 误解3：所有代码都应该 TDD
# 正确：探索性开发、原型、UI 布局不太适合 TDD
# 核心业务逻辑、算法、工具函数非常适合 TDD

# ❌ 误解4：有了测试就不用 TDD
# 正确：先写实现再补测试，你会不自觉地写"让测试通过"的测试
# TDD 的价值在于"测试驱动设计"——先思考接口再写实现
```

---

> 💡 **本章深度讲解**：TDD 不只是一种测试方法，更是一种设计方法。红-绿-重构循环强迫你小步前进，每一步都有反馈。测试金字塔告诉你测试资源应该如何分配——大量快速单元测试，适量集成测试，少量 E2E 测试。在实际项目中，严格 TDD 可能过于理想，但"先写测试再写实现"的思维方式会显著提升代码质量。
>
> **📝 精简总结**：
> - 核心概念：Red-Green-Refactor、测试金字塔、单元/集成/E2E
> - 关键原理：小步快跑；快速反馈；测试分层
> - 常用操作：先写失败测试；最小实现；重构保持测试通过
> - 最佳实践：单元测试占 70%；E2E 只保留关键流程；重构阶段改善设计
> - 常见坑点：Green 阶段写多余代码；Refactor 阶段改变行为
> - 面试高频：TDD 红绿重构；测试金字塔比例；TDD vs 事后测试

### 🎯 梯度练习题

**基础题（⭐）**
1. TDD 三个步骤是什么？
   - 答案：Red（写失败测试）→ Green（最小实现）→ Refactor（重构）。
2. 测试金字塔中单元测试占比约多少？
   - 答案：约 70%。

**进阶题（⭐⭐）**
1. 为什么 Green 阶段要"写最少的代码"？
   - 思考方向：避免过度设计；先验证测试有效；Refactor 阶段再优化。
2. 为什么 E2E 测试应该最少？
   - 思考方向：执行慢；维护成本高；脆弱（UI 变化就挂）；定位问题难。

**实战题（⭐⭐⭐）**
- **背景**：你需要实现一个 `EmailValidator` 类，验证邮箱格式。
- **需求**：用 TDD 方法实现。
- **要求**：① 从最简单的测试开始；② 每个 Red 只加一个新需求；③ 每轮 Green 后重构；④ 最终覆盖：空字符串、无@、无域名、正常邮箱。
- **验收标准**：代码经过 TDD 循环；每个测试独立；最终实现简洁。
- **提示**：从"空字符串返回 False"开始，逐步加规则。

---

## 十二、测试覆盖率与 CI 集成

### 12.1 覆盖率类型

```python
# 行覆盖率（line coverage）：代码行是否被执行
def example(x):
    if x > 0:
        return x     # ← 如果只调用 example(-1)，这行没执行到
    else:
        return -x

# 分支覆盖率（branch coverage）：if/else 两个分支是否都被执行
# 即使 example(1) 和 example(-1) 都调用了，两个分支都覆盖
# 开启方式：coverage run --branch
```

### 12.2 CI 中的覆盖率门禁

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install --no-root

      - name: Run tests with coverage
        run: |
          poetry run pytest \
            --cov=my_project \
            --cov-report=xml \
            --cov-fail-under=80 \
            -v

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
```

### 12.3 CI 中的分层测试策略

```yaml
# .github/workflows/test.yml
# 分层策略：快速反馈 + 完整验证

jobs:
  # 第一层：冒烟测试（<30秒）
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install poetry && poetry install
      - name: Smoke tests
        run: poetry run pytest -m smoke -v

  # 第二层：单元测试（<2分钟）
  unit:
    needs: smoke
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install poetry && poetry install
      - name: Unit tests
        run: poetry run pytest -m unit --cov=my_project --cov-report=xml

  # 第三层：集成测试（<5分钟）
  integration:
    needs: unit
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install poetry && poetry install
      - name: Integration tests
        run: poetry run pytest -m integration -v
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
```

### 12.4 多 Python 版本测试

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install poetry && poetry install
      - run: poetry run pytest -v
```

### 12.5 pre-commit 集成

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: poetry run pytest -m unit
        language: system
        pass_filenames: false
        stages: [commit]
```

```bash
# 安装 pre-commit
poetry add --group dev pre-commit
pre-commit install

# 手动运行
pre-commit run --all-files

# 只运行 pytest
pre-commit run pytest --all-files
```

---

> 💡 **本章深度讲解**：CI 集成是测试体系的最后一公里。在本地写的测试，必须在 CI 中自动运行才能持续保护代码质量。分层测试策略（smoke → unit → integration）让 CI 既快速又全面。覆盖率门禁确保新代码必须被测试覆盖。pre-commit 在代码提交前就拦截问题，比 CI 反馈更快。
>
> **📝 精简总结**：
> - 核心概念：覆盖率门禁、分层 CI、pre-commit、矩阵测试
> - 关键原理：fail_under 强制覆盖率；needs 依赖控制分层；pre-commit 本地拦截
> - 常用操作：`--cov-fail-under=80`；GitHub Actions matrix；pre-commit install
> - 最佳实践：CI 分层运行；覆盖率 80% 起步；pre-commit 跑快速测试
> - 常见坑点：CI 通过本地失败（环境差异）；覆盖率数字游戏
> - 面试高频：CI 测试策略；覆盖率门禁；pre-commit vs CI

### 🎯 梯度练习题

**基础题（⭐）**
1. `--cov-fail-under=80` 的作用是什么？
   - 答案：覆盖率低于 80% 时 pytest 返回非零退出码，CI 会失败。
2. 为什么 CI 中要分 smoke/unit/integration 三层？
   - 答案：快速反馈 + 分层验证；避免每次都跑全部测试浪费时间。

**进阶题（⭐⭐）**
1. 什么是分支覆盖率？它和行覆盖率有什么区别？
   - 思考方向：行覆盖率只看代码行是否执行；分支覆盖率检查 if/else 两个分支是否都走了。
2. 为什么 pre-commit 跑单元测试比 CI 更快？
   - 思考方向：pre-commit 在本地运行；不需要等待 CI 排队；只检查改动相关的测试。

**实战题（⭐⭐⭐）**
- **背景**：你的团队 CI 需要 15 分钟才能跑完所有测试。
- **需求**：优化 CI 时间。
- **要求**：① 提交时 pre-commit 跑单元测试；② PR 时 CI 跑单元+集成；③ 合并 main 时跑全量+覆盖率。
- **验收标准**：开发者每次提交 <30 秒获得反馈；PR <5 分钟；main <10 分钟。
- **提示**：用 GitHub Actions 的 paths 过滤和 needs 分层。

---

## 十三、完整项目实战：FastAPI 测试体系

### 13.1 项目背景与测试策略

本节将构建一个完整的 FastAPI 用户管理项目测试体系，整合前面所有知识点。项目包括：用户 CRUD、JWT 认证、数据库会话管理、邮件发送、缓存等组件。

```mermaid
graph TB
    subgraph 测试分层
        A[单元测试<br/>纯逻辑函数] --> B[集成测试<br/>API + 数据库]
        B --> C[E2E 测试<br/>完整用户流程]
    end

    subgraph 被测组件
        D[UserService<br/>业务逻辑]
        E[AuthService<br/>JWT 认证]
        F[EmailService<br/>邮件发送]
        G[CacheService<br/>Redis 缓存]
    end

    subgraph Mock 策略
        H[Mock EmailService<br/>不真发邮件]
        I[Mock CacheService<br/>用内存字典]
        J[真实 SQLite<br/>测试数据库]
    end
```

### 13.2 项目结构与 fixture 设计

```python
# tests/conftest.py - 全局 fixture 体系
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import Base, get_db
from app.core.config import settings

# ============ 数据库 fixture ============

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """会话级事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """测试数据库引擎（会话级，只创建一次）"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """每个测试独立的数据库会话（事务回滚隔离）"""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()

# ============ API 客户端 fixture ============

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """FastAPI 测试客户端，覆盖数据库依赖"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()

# ============ Mock 外部服务 ============

@pytest.fixture
def mock_email_service(mocker):
    """Mock 邮件服务：不真发邮件"""
    return mocker.patch("app.services.email.EmailService.send_welcome_email")

@pytest.fixture
def mock_redis_cache(mocker):
    """Mock Redis 缓存：用内存字典替代"""
    mock_cache = {}

    async def mock_get(key):
        return mock_cache.get(key)

    async def mock_set(key, value, expire=3600):
        mock_cache[key] = value

    mocker.patch("app.services.cache.CacheService.get", side_effect=mock_get)
    mocker.patch("app.services.cache.CacheService.set", side_effect=mock_set)
    return mock_cache

# ============ 测试数据 fixture ============

@pytest.fixture
def test_user_data():
    """标准测试用户数据"""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
    }

@pytest.fixture
async def created_user(client: AsyncClient, test_user_data: dict, mock_email_service):
    """创建一个已注册的用户"""
    response = await client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    return response.json()

@pytest.fixture
async def auth_headers(client: AsyncClient, created_user: dict, test_user_data: dict):
    """登录并返回认证头"""
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### 13.3 单元测试：业务逻辑层

```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.user_service import UserService
from app.models.user import User

class TestUserService:
    """UserService 单元测试：所有外部依赖都被 Mock"""

    def test_create_user_success(self, mocker):
        """测试用户创建成功"""
        # Arrange
        mock_db = MagicMock()
        mock_email = MagicMock()
        service = UserService(db=mock_db, email_service=mock_email)

        user_data = {"email": "new@example.com", "password": "pass123", "full_name": "New User"}

        # Act
        result = service.create_user(user_data)

        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_email.send_welcome_email.assert_called_once()
        assert result.email == "new@example.com"

    def test_create_user_duplicate_email(self, mocker):
        """测试重复邮箱注册"""
        mock_db = MagicMock()
        # 模拟数据库中已存在该邮箱
        mock_db.query(User).filter().first.return_value = User(
            email="existing@example.com"
        )
        service = UserService(db=mock_db, email_service=MagicMock())

        with pytest.raises(ValueError, match="Email already registered"):
            service.create_user({
                "email": "existing@example.com",
                "password": "pass123",
                "full_name": "Test",
            })

    @pytest.mark.parametrize("password, expected_valid", [
        ("short", False),
        ("nodigitshere", False),
        ("NoSpecial1", False),
        ("Valid1!", True),
        ("Another1@Pass", True),
    ])
    def test_password_validation(self, password, expected_valid):
        """参数化测试密码验证规则"""
        service = UserService(db=MagicMock(), email_service=MagicMock())
        result = service.validate_password(password)
        assert result == expected_valid

    def test_authenticate_wrong_password(self, mocker):
        """测试密码错误"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.check_password.return_value = False
        mock_db.query(User).filter().first.return_value = mock_user

        service = UserService(db=mock_db, email_service=MagicMock())
        result = service.authenticate("user@example.com", "wrongpassword")
        assert result is None
```

### 13.4 集成测试：API 端点

```python
# tests/integration/test_auth_api.py
import pytest
from httpx import AsyncClient

class TestAuthAPI:
    """认证 API 集成测试：使用真实数据库 + 真实 HTTP 请求"""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, mock_email_service):
        """测试注册成功"""
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "password" not in data  # 不返回密码

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user_data: dict):
        """测试重复邮箱注册"""
        # 第一次注册
        await client.post("/api/v1/auth/register", json=test_user_data)
        # 第二次注册相同邮箱
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """测试无效邮箱格式"""
        response = await client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "SecurePass123!",
            "full_name": "Test",
        })
        assert response.status_code == 422  # Pydantic 验证错误

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user_data: dict):
        """测试登录成功"""
        # 先注册
        await client.post("/api/v1/auth/register", json=test_user_data)
        # 登录
        response = await client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user_data: dict):
        """测试密码错误"""
        await client.post("/api/v1/auth/register", json=test_user_data)
        response = await client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": "WrongPassword",
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_profile_unauthorized(self, client: AsyncClient):
        """测试未登录访问受保护路由"""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_profile_success(self, client: AsyncClient, auth_headers: dict):
        """测试获取当前用户信息"""
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
```

### 13.5 参数化 API 测试

```python
# tests/integration/test_user_api.py
import pytest
from httpx import AsyncClient

class TestUserAPI:
    """用户 API 的参数化测试"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint, method, expected_status", [
        ("/api/v1/users/me", "GET", 200),
        ("/api/v1/users/me", "PUT", 200),
        ("/api/v1/users/me", "DELETE", 204),
    ])
    async def test_user_endpoints_authenticated(
        self, client: AsyncClient, auth_headers: dict,
        endpoint: str, method: str, expected_status: int
    ):
        """所有受保护端点在已认证时返回预期状态码"""
        response = await client.request(method, endpoint, headers=auth_headers)
        assert response.status_code == expected_status

    @pytest.mark.asyncio
    @pytest.mark.parametrize("invalid_data, field", [
        ({"email": "bad-email", "password": "Pass123!"}, "email"),
        ({"email": "test@test.com", "password": "short"}, "password"),
        ({"password": "Pass123!"}, "email"),  # 缺少必填字段
        ({}, "email"),  # 空数据
    ])
    async def test_register_validation_errors(
        self, client: AsyncClient, invalid_data: dict, field: str
    ):
        """注册接口的各种验证错误"""
        response = await client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422
```

### 13.6 缓存与重试测试

```python
# tests/unit/test_cache_service.py
import pytest

class TestCacheService:
    """缓存服务测试"""

    @pytest.mark.asyncio
    async def test_cache_set_and_get(self, mock_redis_cache):
        """测试缓存写入和读取"""
        from app.services.cache import CacheService
        cache = CacheService()

        await cache.set("user:1", {"name": "Alice"})
        result = await cache.get("user:1")
        assert result == {"name": "Alice"}

    @pytest.mark.asyncio
    async def test_cache_miss(self, mock_redis_cache):
        """测试缓存未命中"""
        from app.services.cache import CacheService
        cache = CacheService()
        result = await cache.get("nonexistent:key")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_expiration(self, mocker):
        """测试缓存过期"""
        mock_redis = mocker.patch("app.services.cache.redis")
        mock_redis.get.return_value = None  # 过期后返回 None

        from app.services.cache import CacheService
        cache = CacheService()
        result = await cache.get("expired:key")
        assert result is None
```

```python
# tests/unit/test_retry_logic.py
import pytest

class TestRetryLogic:
    """重试逻辑测试"""

    def test_retry_on_network_error(self, mocker):
        """测试网络错误时自动重试"""
        mock_get = mocker.patch("httpx.get")
        mock_get.side_effect = [
            ConnectionError("Attempt 1 failed"),
            ConnectionError("Attempt 2 failed"),
            mocker.MagicMock(status_code=200, json=lambda: {"data": "ok"}),
        ]

        from app.services.external_api import fetch_with_retry
        result = fetch_with_retry("https://api.example.com", max_retries=3)

        assert result == {"data": "ok"}
        assert mock_get.call_count == 3

    def test_retry_exhausted(self, mocker):
        """测试重试次数用尽"""
        mock_get = mocker.patch("httpx.get")
        mock_get.side_effect = ConnectionError("Always fails")

        from app.services.external_api import fetch_with_retry
        with pytest.raises(ConnectionError):
            fetch_with_retry("https://api.example.com", max_retries=3)

        assert mock_get.call_count == 3
```

### 13.7 测试数据库事务隔离详解

```python
# 关键设计：每个测试后回滚事务，确保测试间无数据污染

# tests/conftest.py 中的 db_session fixture 核心逻辑：
#
# 1. 连接到测试数据库
# 2. 开启一个事务
# 3. 在事务内创建 Session
# 4. 测试在事务内运行（所有 commit 都在事务内）
# 5. 测试结束后回滚整个事务
# 6. 关闭连接
#
# 这样即使测试中 commit 了数据，回滚后数据库恢复到初始状态

@pytest.fixture
async def db_session(test_engine):
    connection = await test_engine.connect()
    # 开启外层事务
    transaction = await connection.begin()
    # Session 绑定到这个连接
    session = AsyncSession(bind=connection, expire_on_commit=False)
    try:
        yield session  # 测试运行
    finally:
        await session.close()
        # 回滚外层事务，所有测试中的 commit 都被撤销
        await transaction.rollback()
        await connection.close()
```

```python
# 验证隔离性的测试
class TestDatabaseIsolation:
    def test_user_visible_in_this_test(self, db_session):
        from app.models.user import User
        user = User(email="isolated@test.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()
        # 在此测试中用户存在
        assert db_session.query(User).filter_by(email="isolated@test.com").first() is not None

    def test_user_not_visible_in_next_test(self, db_session):
        from app.models.user import User
        # 上一个测试的用户不存在（因为回滚了）
        assert db_session.query(User).filter_by(email="isolated@test.com").first() is None
```

> ✅ 最佳实践：事务回滚隔离是数据库测试的黄金标准。它比"每个测试后删除所有数据"快得多——因为回滚是数据库级别的操作，而 DELETE 需要逐行扫描。

---

> 💡 **本章深度讲解**：本章将前面所有知识点整合到一个完整的 FastAPI 项目测试体系中。关键设计决策包括：session 级别的数据库引擎（只创建一次）、function 级别的事务会话（每个测试回滚）、Mock 外部服务（邮件/Redis）、覆盖 FastAPI 依赖注入（override_get_db）、参数化 API 测试、缓存和重试测试。这套 fixture 体系可以直接用于生产项目。
>
> **📝 精简总结**：
> - 核心概念：依赖覆盖、事务隔离、分层 fixture、API 集成测试
> - 关键原理：override dependency；事务回滚隔离；Mock 外部服务
> - 常用操作：`app.dependency_overrides[get_db]`；`ASGITransport`；事务回滚
> - 最佳实践：session 级连接 + function 级事务；Mock 邮件和外部 API
> - 常见坑点：忘记清理 dependency_overrides；事务未正确回滚
> - 面试高频：FastAPI 测试客户端；数据库事务隔离；依赖覆盖

### 🎯 梯度练习题

**基础题（⭐）**
1. 为什么 FastAPI 测试需要 `app.dependency_overrides`？
   - 答案：用测试数据库替换生产数据库依赖。
2. 事务回滚隔离比"删除所有数据"好在哪里？
   - 答案：数据库级别的 ROLLBACK 比逐行 DELETE 快得多。

**进阶题（⭐⭐）**
1. 为什么数据库引擎用 session 作用域而 session 用 function 作用域？
   - 思考方向：连接池复用 vs 数据隔离；创建连接昂贵但数据需要隔离。
2. `expire_on_commit=False` 在测试中为什么重要？
   - 思考方向：commit 后对象过期需要重新查询；测试中跨 commit 访问对象会报错。

**实战题（⭐⭐⭐）**
- **背景**：你需要为一个 TODO 列表 API 编写测试。
- **需求**：完整测试 CRUD 操作。
- **要求**：① 创建 TODO；② 读取单个 TODO；③ 列出所有 TODO；④ 更新 TODO；⑤ 删除 TODO；⑥ 未认证返回 401；⑦ 验证数据校验。
- **验收标准**：覆盖所有端点；事务隔离；Mock 外部依赖。
- **提示**：参考本章的 fixture 体系和参数化测试。

---

## 十四、最佳实践与常见坑点

### 14.1 测试组织最佳实践

```python
# ✅ 好的项目结构
my_project/
├── my_project/           # 源代码
│   ├── __init__.py
│   ├── calculator.py
│   └── api.py
├── tests/                # 测试目录
│   ├── __init__.py
│   ├── conftest.py       # 全局 fixture
│   ├── unit/             # 单元测试
│   │   ├── __init__.py
│   │   ├── test_calculator.py
│   │   └── test_api.py
│   ├── integration/      # 集成测试
│   │   ├── __init__.py
│   │   └── test_db_integration.py
│   └── e2e/              # E2E 测试
│       └── test_user_flow.py
├── pyproject.toml
└── poetry.lock
```

### 14.2 测试代码质量原则

| 原则 | 说明 | 例子 |
|------|------|------|
| **AAA 模式** | Arrange-Act-Assert | 准备数据 → 执行操作 → 验证结果 |
| **一个测试一个行为** | 每个测试函数只验证一个场景 | 不要在一个测试中验证成功+异常 |
| **独立可重复** | 测试不依赖执行顺序 | 每个测试自己 setup，不共享状态 |
| **快速** | 单元测试 <10ms | 不要在单元测试中连接真实数据库 |
| **有意义的断言** | 验证重要的行为 | 不要只验证"没报错" |

```python
# ✅ AAA 模式示例
def test_add_positive_numbers():
    # Arrange：准备
    a, b = 2, 3

    # Act：执行
    result = add(a, b)

    # Assert：验证
    assert result == 5

# ❌ 不好的示例：没有验证
def test_bad():
    result = add(2, 3)
    # 没有 assert！这个测试永远通过
```

### 14.3 常见坑点汇总

| 坑点 | 现象 | 原因 | 解决方案 |
|------|------|------|---------|
| fixture not found | `fixture 'xxx' not found` | fixture 定义在非 conftest 文件且未 import | 移到 conftest.py 或显式 import |
| patch 不生效 | Mock 了但代码没走 Mock | patch 了定义处而非使用处 | patch 使用处：`mocker.patch("module.using.func")` |
| 测试顺序依赖 | 随机顺序下偶发失败 | 测试间共享状态 | 每个测试独立 setup；用 pytest-randomly 检测 |
| 数据污染 | 上一个测试的数据影响下一个 | 数据库 fixture 未回滚 | 事务回滚 fixture；每个测试 rollback |
| 异步测试报错 | `coroutine was never awaited` | 未安装 pytest-asyncio 或忘记 marker | 安装并设置 `asyncio_mode = "auto"` |
| 覆盖率 0% | `--cov` 路径错误 | source 路径不对 | 确认 `source = ["my_project"]` 路径正确 |
| 测试运行慢 | 集成测试过多 | 标记 slow 但没跳过 | `pytest -m "not slow"`；CI 分层运行 |
| 断言不详细 | 只有 AssertionError | `--assert=plain` 或文件不在 testpaths | 确保默认 assert 重写开启 |
| CI 通过本地失败 | 环境不一致 | Python 版本/依赖版本不同 | 锁定 poetry.lock；CI 用相同 Python 版本 |
| 测试类不收集 | Test 类的测试没运行 | 类有 `__init__` 方法 | 移除 `__init__` 或用函数式测试 |
| Event loop is closed | 异步测试报事件循环错误 | event_loop fixture 作用域不匹配 | 升级 pytest-asyncio；定义 session 级 event_loop |
| 过度 mock | 测试全是 mock 没有真实逻辑 | mock 了太多内部细节 | 只 mock 外部依赖；内部逻辑用真实对象 |
| 测试名称模糊 | 失败时不知道测了什么 | 命名不描述场景 | `test_<行为>_<场景>_<预期>` |
| xfail 长期不清理 | 已知 bug 标记永远在 | 修复后忘记移除 xfail | `strict=True` 自动提醒；定期清理 |
| 全局可变状态 | 测试间互相影响 | 使用了模块级全局变量 | fixture 返回新对象；避免全局可变状态 |

### 14.4 面试高频考点汇总

> 🎯 **面试考点 1**：Pytest 的断言重写是什么原理？
> 在导入测试模块时，Pytest 通过 meta_path 钩子拦截，用 AST 解析源码，将 assert 节点重写为能自动收集左右值的版本。失败时输出详细的差异信息。

> 🎯 **面试考点 2**：fixture 的 scope 有哪些？如何选择？
> function（默认，每个测试一次）、class（每个类一次）、module（每个文件一次）、package（每个包一次）、session（整个会话一次）。选择原则：最小必要作用域。

> 🎯 **面试考点 3**：mock.patch 应该在哪里 patch？
> Patch where it's used, not where it's defined。因为 import 绑定的是引用，必须 patch 使用处的引用。

> 🎯 **面试考点 4**：TDD 的红绿重构循环是什么？
> Red（写失败测试）→ Green（最小实现）→ Refactor（重构）。每步只做一件事，小步快跑。

> 🎯 **面试考点 5**：测试金字塔是什么？
> 单元测试（70%，快，纯逻辑）→ 集成测试（20%，中，外部交互）→ E2E 测试（10%，慢，完整流程）。

> 🎯 **面试考点 6**：skip 和 xfail 的区别？
> skip 不运行测试；xfail 运行测试但预期失败。xfail(strict=True) 在 bug 修复后会 XPASS 变 FAILED，提醒清理。

> 🎯 **面试考点 7**：pytest 如何发现测试？
> 默认查找 `testpaths` 目录下 `test_*.py` 文件中的 `test_*` 函数和 `Test*` 类中的 `test_*` 方法。

> 🎯 **面试考点 8**：如何在 CI 中加速测试？
> pytest-xdist 并行；分层运行（smoke/unit/integration）；标记慢速测试按需运行；pytest --lf 只跑失败的。

> 🎯 **面试考点 9**：什么是测试覆盖率？100% 覆盖率够吗？
> 覆盖率衡量代码被测试执行到的比例。100% 不代表测试充分——覆盖率不衡量断言质量。

> 🎯 **面试考点 10**：conftest.py 的作用是什么？
> 存放共享 fixture 和 hook 函数。同目录及子目录的测试自动可用其中的 fixture，无需 import。

> 🎯 **面试考点 11**：fixture 如何实现依赖注入？
> 测试函数通过参数名声明需要的 fixture，Pytest 在执行时根据参数名查找 fixture 定义，按依赖图递归解析并注入。

> 🎯 **面试考点 12**：pytest-randomly 解决什么问题？
> 随机化测试执行顺序，发现测试间的隐式依赖和顺序耦合。偶发失败可通过 seed 复现。

### 14.5 进阶学习资源

- [Pytest 官方文档](https://docs.pytest.org/) — 最权威的参考
- [pytest-asyncio 文档](https://pytest-asyncio.readthedocs.io/) — 异步测试指南
- [testyourpython.com](https://testyourpython.com/) — Pytest 实战教程
- 《Python Testing with pytest》— Brian Okken 著，Pytest 经典书籍
- [Awesome pytest](https://github.com/augustogoulart/awesome-pytest) — 插件和资源汇总

---

> 💡 **本章深度讲解**：最佳实践和坑点是从实际项目中总结的经验。AAA 模式让测试可读；测试金字塔让资源分配合理；CI 集成让测试持续生效。15 个常见坑点覆盖了 Pytest 使用中 90% 的问题。面试考点则总结了 Pytest 知识体系中最常被考察的核心概念。掌握这些，你就能在任何 Python 项目中高效使用 Pytest。
>
> **📝 精简总结**：
> - 核心概念：AAA 模式、测试金字塔、覆盖率、CI 分层
> - 关键原理：独立可重复；快速反馈；分层验证
> - 常用操作：`pytest -m "not slow"`；`--cov-fail-under=80`；pre-commit
> - 最佳实践：一个测试一个行为；共享 fixture 放 conftest；patch 使用处
> - 常见坑点：fixture not found；patch 位置错误；测试顺序依赖
> - 面试高频：断言重写；fixture scope；where to patch；TDD 循环

### 🎯 梯度练习题

**基础题（⭐）**
1. AAA 模式是什么？
   - 答案：Arrange（准备）、Act（执行）、Assert（验证）。
2. 为什么测试要独立可重复？
   - 答案：测试不应该依赖执行顺序；每次运行结果一致。

**进阶题（⭐⭐）**
1. 为什么"过度 mock"是一个反模式？
   - 思考方向：mock 了太多内部实现细节；测试和实现强耦合；重构时测试全部失败。
2. 如何判断测试是否"有效"而不只是"通过"？
   - 思考方向：测试能抓住 bug 吗？断言验证了重要行为吗？删掉测试代码还能通过吗？

**实战题（⭐⭐⭐）**
- **背景**：你的项目测试套件有 500 个测试，但经常出现偶发失败。
- **需求**：系统排查并修复测试质量问题。
- **要求**：① 用 pytest-randomly 检测顺序依赖；② 找出共享状态的 fixture；③ 确保每个测试独立 setup；④ 添加 CI 分层策略。
- **验收标准**：连续 10 次随机运行全部通过；CI <5 分钟完成。
- **提示**：从失败最频繁的测试开始，逐个分析它依赖了什么共享状态。

---

## 附录：Pytest 速查表

### 常用命令速查

```bash
# 运行测试
pytest                          # 全部运行
pytest -v                       # 详细输出
pytest -q                       # 简洁输出
pytest -x                       # 第一个失败就停
pytest --maxfail=5              # 失败5次停

# 选择测试
pytest tests/test_api.py        # 指定文件
pytest tests/test_api.py::test_create  # 指定函数
pytest -k "user and not slow"  # 关键字过滤
pytest -m "unit or smoke"      # 标记过滤
pytest --lf                     # 上次失败的
pytest --ff                     # 失败的先跑

# 调试
pytest --pdb                    # 失败进调试器
pytest -l                       # 显示局部变量
pytest --tb=short               # 简洁 traceback

# 覆盖率
pytest --cov=my_project         # 终端报告
pytest --cov=my_project --cov-report=html  # HTML
pytest --cov=my_project --cov-fail-under=80  # 门禁

# 并行
pytest -n auto                  # 自动并行
pytest -n 4                     # 4个worker
```

### Fixture 速查

```python
import pytest

# function 作用域（默认）
@pytest.fixture
def my_fixture():
    return data

# module 作用域
@pytest.fixture(scope="module")
def my_module_fixture():
    return shared_data

# session 作用域
@pytest.fixture(scope="session")
def my_session_fixture():
    return connection

# 参数化 fixture
@pytest.fixture(params=["a", "b", "c"])
def param_fixture(request):
    return request.param

# autouse fixture
@pytest.fixture(autouse=True)
def auto_fixture():
    setup()
    yield
    teardown()

# yield 分离 setup/teardown
@pytest.fixture
def resource():
    r = acquire()
    try:
        yield r
    finally:
        release(r)
```

### 标记速查

```python
import pytest

# 自定义标记
@pytest.mark.slow
def test_slow(): ...

# 跳过
@pytest.mark.skip(reason="未实现")
def test_future(): ...

# 条件跳过
@pytest.mark.skipif(sys.version_info < (3, 10), reason="需要 3.10+")
def test_new_feature(): ...

# 预期失败
@pytest.mark.xfail(reason="已知 bug", strict=True)
def test_buggy(): ...

# 模块级标记
pytestmark = [pytest.mark.integration, pytest.mark.slow]

# 类级标记
@pytest.mark.database
class TestDB:
    def test_insert(self): ...
```

### Mock 速查

```python
# pytest-mock: mocker fixture
def test_example(mocker):
    # 替换函数
    mock_func = mocker.patch("module.using.func")

    # 设置返回值
    mock_func.return_value = "result"

    # 设置异常
    mock_func.side_effect = ConnectionError("timeout")

    # 设置序列返回
    mock_func.side_effect = [result1, result2, result3]

    # 断言
    mock_func.assert_called_once()
    mock_func.assert_called_with(arg1, arg2)
    mock_func.assert_not_called()
    assert mock_func.call_count == 3
```

### Monkeypatch 速查

```python
def test_example(monkeypatch):
    # 环境变量
    monkeypatch.setenv("KEY", "value")
    monkeypatch.delenv("KEY")

    # 字典
    monkeypatch.setitem(d, "key", "value")

    # 属性
    monkeypatch.setattr(obj, "attr", value)

    # 工作目录
    monkeypatch.chdir("/tmp")

    # 测试后自动恢复
```

### 配置速查

```toml
# pyproject.toml - pytest 配置
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "slow: 慢速测试",
    "integration: 集成测试",
    "unit: 单元测试",
    "smoke: 冒烟测试",
]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["my_project"]
omit = ["*/tests/*", "*/migrations/*"]
branch = true

[tool.coverage.report]
show_missing = true
fail_under = 80
```

### 环境变量速查

```bash
# PYTEST_ADDOPTS: 环境变量传参
export PYTEST_ADDOPTS="-v --tb=short"
pytest  # 自动带上 -v --tb=short

# PYTEST_DEBUG: 调试模式
export PYTEST_DEBUG=1
pytest

# pytest 缓存目录
.pytest_cache/  # 存放 --lf, --ff 状态
```

### 插件推荐清单

| 插件 | 用途 | 何时使用 |
|------|------|---------|
| pytest-asyncio | 异步测试 | 任何 async 代码项目 |
| pytest-cov | 覆盖率 | 所有项目 |
| pytest-mock | Mock 简化 | 所有项目（替代 unittest.mock） |
| pytest-xdist | 并行 | 测试 >100 个时 |
| pytest-randomly | 随机顺序 | 所有项目（检测依赖） |
| pytest-timeout | 超时保护 | 集成测试/E2E |
| pytest-html | HTML 报告 | CI 上传报告 |
| factory_boy | 数据工厂 | 需要复杂测试数据时 |
| pytest-benchmark | 性能基准 | 性能敏感项目 |
| hypothesis | 属性测试 | 算法/数据处理项目 |
| pytest-env | 环境变量 | 测试需要特定环境变量时 |
| pytest-django | Django 支持 | Django 项目 |
| pytest-flask | Flask 支持 | Flask 项目 |
| pytest-selenium | Selenium 集成 | 浏览器 E2E 测试 |
| pytest-playwright | Playwright 集成 | 现代浏览器 E2E 测试 |

### 快速故障排查流程

```bash
# 当测试失败时，按以下步骤排查：
# 1. 看失败信息
pytest -v --tb=short

# 2. 看局部变量
pytest -l

# 3. 进入调试器
pytest --pdb

# 4. 只跑失败的
pytest --lf

# 5. 检查 fixture 依赖
pytest --fixtures -v

# 6. 检查配置
pytest --showconfig

# 7. 检查收集了哪些测试
pytest --collect-only -q
```

---

**🔗 关联笔记**

- [[Python-项目结构最佳实践]] — Python 项目结构与工程化规范
- [[Poetry-依赖与虚拟环境管理]] — Python 依赖管理与虚拟环境
- [[Python-类型注解与mypy]] — 静态类型检查提升代码质量

**📖 前置知识**

- [[Python-语法基础与数据结构]]
- [[Python-模块与包管理原理]]

**🏷️ 相关标签**

#Python #Pytest #TDD #单元测试 #测试驱动开发 #fixture #mock

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]
