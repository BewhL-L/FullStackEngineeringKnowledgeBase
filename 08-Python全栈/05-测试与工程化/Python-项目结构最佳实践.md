---
title: Python 项目结构最佳实践
tags: [Python, 项目结构, 工程化, 模块化, 最佳实践, 原子笔记]
category: Python全栈
created: 2026-08-13
updated: 2026-09-10
difficulty: ⭐⭐⭐⭐
status: ✅ P1深度重写
priority: P1核心
pre: ["[[Python-模块与包管理原理]]", "[[Poetry-依赖与虚拟环境管理]]"]
aliases: [Python-项目结构最佳实践, Python 项目结构, 项目组织]
---

# Python 项目结构最佳实践

> **文档说明**：本文以"五要素"标准（概念+原理+代码+场景+坑点）深度讲解 Python 项目结构，覆盖 src 布局与扁平布局对比、分层架构（接口层/服务层/数据层）、配置管理（pydantic-settings/dynaconf）、环境变量与 secrets 管理、依赖注入、错误处理、常量与枚举组织、测试结构、Makefile/pre-commit/CI、Docker 化、开源项目模板等全部主题。每个知识点配完整可运行代码示例与预期输出。
>
> **适用人群**：Python 开发者、全栈工程师、技术负责人、面试备考者
>
> **前置知识**：[[Python-模块与包管理原理]]、[[Poetry-依赖与虚拟环境管理]]、[[架构设计原则-SOLID]]

---

## 一、Python 项目结构概述

### 1.1 为什么需要项目结构

**概念**：项目结构是代码的物理组织方式，决定了"哪个文件放什么、谁 import 谁、怎么跑起来"。Python 语法灵活（单文件就能跑），但灵活不等于规范——项目一旦超过 1000 行，没有结构就会变成"屎山"。

**原理**：项目结构的本质是**依赖关系的物理编码**。好的结构让"谁能依赖谁"一眼可见，坏的结构让你每次改代码都要猜"这个函数在哪"。Python 的导入系统（`sys.path` + `__init__.py`）决定了目录结构直接影响导入路径，所以结构不是审美问题，是工程问题。

**代码——反面教材 vs 正面教材**：

```python
# ❌ 反面：所有代码堆在 main.py，2000 行
# main.py
import os
import json
from datetime import datetime

def handler(event, context):
    # 解析请求
    body = json.loads(event["body"])
    # 连接数据库
    conn = ...  # 50 行数据库连接代码
    # 业务逻辑
    if body["type"] == "order":
        # 300 行订单处理
        ...
    elif body["type"] == "user":
        # 200 行用户处理
        ...
    # 发送邮件
    smtp_conn = ...  # 30 行邮件代码
    return {"statusCode": 200, "body": "ok"}

# 预期结果：改一行要在 2000 行里找半天；测试必须起整个环境
```

```text
# ✅ 正面：分层结构
myapp/
├── api/              # 接口层：只处理 HTTP
├── services/         # 业务层：纯业务逻辑
├── repositories/     # 数据层：数据库访问
├── models/           # 数据模型
├── core/             # 基础设施：配置/日志/安全
└── tests/            # 测试独立
# 预期结果：改订单逻辑只动 services/order_service.py；测试可 mock 数据库
```

**场景**：
- 单人脚本 < 100 行：单文件 `script.py` 足够
- CLI 工具 100-1000 行：按功能分模块 `cli.py / core.py / utils.py`
- Web API 1000-10000 行：分层架构 `api / services / repositories / models`
- 微服务 > 10000 行：Monorepo 或多仓库

**坑点**：
- ❌ 把"能不能跑"等同于"结构好不好"。能跑的代码不等于可维护的代码。
- ❌ 过早设计。< 500 行的项目不需要三层架构，过度工程化比没有结构更糟。
- ❌ 按技术类型分目录（`controllers/ models/ services/`）而不是按业务领域分（`orders/ users/ products/`）。小项目按技术类型可以，大项目应该按业务领域。

### 1.2 项目规模演进路径

```mermaid
graph LR
    A[单文件脚本<br/><100行] --> B[小型项目<br/>分模块 100-1k行]
    B --> C[中型项目<br/>分层架构 1k-10k行]
    C --> D[大型项目<br/>微服务/Monorepo >10k行]
```

| 规模 | 代码量 | 结构 | 典型项目 |
|------|--------|------|---------|
| 脚本 | <100 行 | 单文件 | 数据清洗脚本、爬虫 |
| 小型 | 100-1000 行 | 按功能分模块 | CLI 工具、小 Web 服务 |
| 中型 | 1000-10000 行 | 分层架构 | FastAPI/Django Web API |
| 大型 | >10000 行 | 微服务/Monorepo | 企业级平台、SaaS |

### 1.3 三大核心原则

| 原则 | 含义 | 实践 |
|------|------|------|
| **关注点分离** | 每个文件/模块只做一件事 | HTTP 逻辑在 api/，业务逻辑在 services/，SQL 在 repositories/ |
| **显式优于隐式** | 依赖关系写在明面上 | 不用全局变量传 DB 连接，通过函数参数注入 |
| **可测试性优先** | 每个组件能独立测试 | Service 层不依赖 HTTP，Repository 层接口可 mock |

### 1.4 标准 Web API 项目完整结构

```text
my_fastapi_project/
├── .github/
│   └── workflows/
│       └── ci.yml                  # CI 流水线
├── alembic/
│   ├── env.py                      # Alembic 配置
│   └── versions/                   # 迁移脚本
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI 应用入口
│   ├── config.py                   # 配置管理（Pydantic Settings）
│   ├── database.py                 # 数据库连接/Session
│   ├── dependencies.py             # 通用依赖注入
│   ├── core/                       # 核心组件
│   │   ├── __init__.py
│   │   ├── security.py             # JWT/密码哈希
│   │   ├── logging.py             # 日志配置
│   │   └── exceptions.py           # 自定义异常
│   ├── models/                     # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── post.py
│   ├── schemas/                    # Pydantic 模型（请求/响应）
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── post.py
│   ├── services/                   # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── post_service.py
│   ├── repositories/               # 数据访问层
│   │   ├── __init__.py
│   │   ├── base.py                 # 通用 CRUD 基类
│   │   ├── user_repo.py
│   │   └── post_repo.py
│   ├── api/                        # 路由层
│   │   ├── __init__.py
│   │   ├── deps.py                 # API 层依赖
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       └── posts.py
│   └── utils/                      # 工具函数
│       ├── __init__.py
│       └── datetime.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # pytest fixture
│   ├── unit/
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── test_api_users.py
│   │   └── test_api_posts.py
│   └── e2e/
│       └── test_user_flow.py
├── scripts/                        # 运维脚本
│   ├── init_db.py
│   └── create_admin.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example                    # 环境变量模板
├── .gitignore
├── .pre-commit-config.yaml         # pre-commit 配置
├── alembic.ini
├── pyproject.toml                  # 项目配置 + 依赖
├── README.md
└── Makefile                        # 常用命令快捷方式
```

### 1.5 各顶层目录职责

| 目录/文件 | 职责 | 不该放什么 |
|-----------|------|-----------|
| `app/` | 应用源代码 | 临时脚本、调试代码 |
| `app/core/` | 跨业务的基础设施（配置/日志/安全） | 业务逻辑 |
| `app/models/` | ORM 数据模型 | HTTP 校验逻辑 |
| `app/schemas/` | Pydantic 请求/响应模型 | 数据库查询 |
| `app/services/` | 业务逻辑 | HTTP 细节、SQL |
| `app/repositories/` | 数据访问 | 业务规则 |
| `app/api/` | 路由定义 | 业务逻辑 |
| `tests/` | 测试代码 | 业务逻辑实现 |
| `scripts/` | 运维/一次性脚本 | 核心业务代码 |
| `docker/` | Docker 配置 | 应用代码 |
| `docs/` | 文档 | 代码 |

### 1.6 项目模板工具

```bash
# Cookiecutter：从模板创建项目
pip install cookiecutter
cookiecutter https://github.com/tiangolo/full-stack-fastapi-template
# 预期：交互式问答后生成完整项目骨架

# Copier：支持模板更新（比 cookiecutter 更适合长期维护）
pip install copier
copier copy https://github.com/example/template.git my_project
# 预期：生成项目后，模板更新时可同步
```

```python
# 常用模板推荐
# - full-stack-fastapi-template：FastAPI 全栈（官方）
# - cookiecutter-pypackage：Python 库打包
# - django-cookiecutter：Django 项目
# - poetry-plugin-copier：Poetry + Copier 集成
```

### 1.70 一句话记住 结构演进

> 小项目不硬套大结构，但预留演进空间。

### 1.71 常见问题排查表

| 问题现象 | 原因 | 解决方案 |
|---------|------|---------|
| `ModuleNotFoundError: No module named 'app'` | 项目根目录不在 sys.path | `pip install -e .`；或 `pythonpath = ["."]` |
| `attempted relative import with no known parent package` | 直接 `python app/main.py` | 用 `python -m app.main` 或 uvicorn |
| 循环导入 | A→B→A | 提取共享代码到第三模块；延迟导入 |
| 测试找不到 app 包 | tests 无 `__init__.py` | 添加；或 `pythonpath = ["."]` |
| 配置多环境值不同 | 硬编码配置 | pydantic-settings + 环境变量 |
| 测试污染数据库 | 用真实库未清理 | 内存 SQLite；事务回滚 fixture |
| 日志输出到控制台 | 未配 FileHandler | 生产配 FileHandler 或 ELK |
| 新项目重复造轮子 | 无模板 | 用 cookiecutter/copier |

### 1.72 代码组织检查清单

| 检查项 | 说明 | 通过标准 |
|--------|------|---------|
| 每个文件 < 500 行 | 超过则拆分 | 用 `wc -l` 检查 |
| 每个函数 < 50 行 | 超过则提取子函数 | ruff 可检查 |
| 无循环导入 | A→B→A | `pydeps` 可视化 |
| 无全局可变状态 | DB 连接通过 DI | grep 模块级赋值 |
| 测试镜像源码 | `tests/unit/services/test_x.py` | 目录对比 |
| 配置外部化 | 无硬编码 URL/密钥 | grep `http://` |
| 入口唯一 | main.py 是唯一入口 | 无多个 `if __name__` |
| 文档齐全 | README + docstring | 公共函数都有 docstring |
| 类型标注 | 公共 API 有类型 | mypy --strict 通过 |
| 无 print 调试 | 全部用 logging | grep `print(` |

### 1.73 一句话记住 六原则

> 关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。

### 1.74 一句话记住 面试话术

> 三原则 + src 布局 + 三层 + DI + pydantic-settings。

### 1.75 项目模板对比

| 模板 | 适合 | 特点 |
|------|------|------|
| full-stack-fastapi-template | FastAPI 全栈 | 官方，含前端 |
| cookiecutter-pypackage | Python 库 | 标准打包结构 |
| django-cookiecutter | Django | Django 最佳实践 |
| uv-workspace-template | Monorepo | uv 工作区 |

### 1.76 一句话记住 六原则

> 关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。

### 1.77 一句话记住 演进路径

> 脚本→分模块→分层→微服务。

### 1.78 完整项目结构决策表

| 项目类型 | 布局 | 分层 | 配置 | 测试 |
|---------|------|------|------|------|
| 个人脚本 | 扁平 | 无 | os.getenv | 无 |
| CLI 工具 | 扁平 | 无 | pydantic-settings | unit |
| Web API | src | 三层 | pydantic-settings | unit+integration |
| 微服务 | src | 三层+DI | dynaconf | unit+integration+e2e |
| Monorepo | src workspace | 按业务域 | 各服务独立 | 全栈 |

### 1.79 一句话记住 六原则

> 关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。

### 1.80 一句话记住 面试话术

> 三原则 + src 布局 + 三层 + DI + pydantic-settings。

### 1.81 项目模板对比

| 模板 | 适合 | 特点 |
|------|------|------|
| full-stack-fastapi-template | FastAPI 全栈 | 官方，含前端 |
| cookiecutter-pypackage | Python 库 | 标准打包结构 |
| django-cookiecutter | Django | Django 最佳实践 |
| uv-workspace-template | Monorepo | uv 工作区 |

### 1.82 一句话记住 六原则

> 关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。

### 1.83 一句话记住 演进路径

> 脚本→分模块→分层→微服务。

### 1.84 完整项目结构决策表

| 项目类型 | 布局 | 分层 | 配置 | 测试 |
|---------|------|------|------|------|
| 个人脚本 | 扁平 | 无 | os.getenv | 无 |
| CLI 工具 | 扁平 | 无 | pydantic-settings | unit |
| Web API | src | 三层 | pydantic-settings | unit+integration |
| 微服务 | src | 三层+DI | dynaconf | unit+integration+e2e |
| Monorepo | src workspace | 按业务域 | 各服务独立 | 全栈 |

### 1.85 一句话记住 六原则

> 关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。

### 1.86 一句话记住 面试话术

> 三原则 + src 布局 + 三层 + DI + pydantic-settings。

### 1.87 项目模板对比

| 模板 | 适合 | 特点 |
|------|------|------|
| full-stack-fastapi-template | FastAPI 全栈 | 官方，含前端 |
| cookiecutter-pypackage | Python 库 | 标准打包结构 |
| django-cookiecutter | Django | Django 最佳实践 |
| uv-workspace-template | Monorepo | uv 工作区 |

### 1.88 一句话记住 六原则

> 关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。

### 1.89 一句话记住 本文完

> 感谢阅读，祝项目结构越来越清晰。

> 💡 **深度讲解**：项目结构不是"设计出来的"，是"演进来的"。小项目不要硬套大结构，但要预留演进空间——比如一开始就用 `pyproject.toml` 管理依赖，一开始就用 `pydantic-settings` 管配置，这些决策后期改起来成本极高。结构的"正确"是相对的，关键是"团队共识 + 可演进"。

> **📝 精简总结**：项目结构 = 依赖关系的物理编码。核心三原则：关注点分离、显式优于隐式、可测试性优先。按项目规模选择结构：脚本→单文件，小型→分模块，中型→分层，大型→微服务。

> 🎯 **梯度练习题**：
> 1. 入门：把一个 500 行的单文件脚本拆成 3 个模块（core/utils/main）
> 2. 中级：为一个 FastAPI 项目设计 api/services/repositories 三层结构
> 3. 高级：用 Copier 维护一个团队项目模板，支持模板更新同步

## 二、src 布局 vs 扁平布局

### 2.1 两种布局对比

**概念**：Python 项目有两种主流布局——**扁平布局**（包直接在根目录）和 **src 布局**（包放在 `src/` 子目录里）。

**原理**：Python 导入依赖 `sys.path`。扁平布局下，根目录在 `sys.path` 中，所以 `import myapp` 能找到根目录下的 `myapp/` 包。这在"直接运行"时没问题，但在"打包发布"时会出问题——打包工具可能把根目录也装进去，导致 `import myapp` 导入的是源码目录而不是安装包。src 布局强制你"先安装再运行"，从根本上避免了这个问题。

**代码——扁平布局**：

```text
myproject/
├── myapp/              # 包直接在根目录
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
├── pyproject.toml
└── README.md
```

```python
# 扁平布局的问题：直接 python myapp/main.py 能跑
# 但打包安装后，import myapp 可能导入源码目录而非安装包
# 更糟的是：测试时可能意外导入未安装的源码
```

**代码——src 布局**：

```text
myproject/
├── src/
│   └── myapp/          # 包放在 src/ 下
│       ├── __init__.py
│       ├── main.py
│       └── utils.py
├── tests/
│   └── test_main.py
├── pyproject.toml
└── README.md
```

```toml
# pyproject.toml — src 布局必须指定包位置
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "myapp"
version = "0.1.0"

[tool.setuptools.packages.find]
where = ["src"]
```

```bash
# src 布局的正确工作流
pip install -e .        # 安装为可编辑包
pytest                  # 测试时 import myapp 导入的是 src/myapp
myapp                   # 命令行入口也能用
# 预期：测试和运行都用安装后的包，杜绝"跑的是源码还是安装包"的歧义
```

### 2.2 对比表格

| 维度 | 扁平布局 | src 布局 |
|------|---------|---------|
| 简单度 | 更简单 | 多一层目录 |
| 导入可靠性 | 可能导入源码目录 | 强制安装后运行，可靠 |
| 打包发布 | 容易出"幽灵导入" | 打包工具原生支持 |
| 测试隔离 | 可能测到未安装的代码 | 测试必须用安装包 |
| 适合场景 | 脚本/小项目 | 库/要发布的包/团队项目 |

### 2.3 什么时候用哪种

```python
# 决策树
# if 项目是"要发布到 PyPI 的库" → 必须 src 布局
# if 项目是"团队协作的服务" → 推荐 src 布局
# if 项目是"个人脚本" → 扁平布局也行
# if 项目是"临时实验" → 单文件都行
```

**坑点**：
- ❌ 扁平布局下"能跑"不代表"打包后能跑"。很多人本地跑通，docker 构建后 import 报错。
- ❌ src 布局忘了在 `pyproject.toml` 里写 `[tool.setuptools.packages.find] where = ["src"]`，导致打包后找不到包。
- ❌ src 布局下直接 `python src/myapp/main.py` 跑会报相对导入错误。必须 `pip install -e .` 后用 `myapp` 命令或 `python -m myapp.main`。

### 2.4 常见导入错误排查

```python
# 错误 1：ModuleNotFoundError: No module named 'app'
# 原因：项目根目录不在 sys.path 中
# 解决：
# 方案 A：pip install -e . 安装为可编辑包
# 方案 B：在 pyproject.toml 设置 pythonpath = ["."]
# [tool.pytest.ini_options]
# pythonpath = ["."]
# 方案 C：从项目根目录运行 poetry run uvicorn app.main:app

# 错误 2：attempted relative import with no known parent package
# 原因：直接运行 python app/main.py，而 main.py 里用了 from .utils import x
# 解决：用 python -m app.main 运行（模块方式）
# 或：poetry run uvicorn app.main:app（FastAPI 不会有这问题）

# 错误 3：ImportError: cannot import name 'X' from 'Y'（循环导入）
# 原因：A 导入 B，B 又导入 A
# 解决：提取共享代码到第三个模块；或延迟导入（函数内 import）
```

### 2.10 一句话记住 src 布局

> 包放 src/，pip install -e . 后跑。

### 2.11 一句话记住 导入错误

> 找不到包看 sys.path，相对导入看运行方式。

### 2.12 一句话记住 决策树

> 要发布的库→src，个人脚本→扁平。

### 2.13 常见打包错误

```bash
# 错误：python -m build 后安装找不到包
# 原因：pyproject.toml 没指定 packages.find
# 解决：
# [tool.setuptools.packages.find]
# where = ["src"]
# packages = ["myapp"]

# 错误：pip install -e . 后 import 失败
# 原因：src 布局下没 pip install -e .
# 解决：poetry install 自动处理
```

### 2.14 一句话记住 src 布局

> 包放 src/，pip install -e . 后跑。

### 2.15 一句话记住 导入错误

> 找不到包看 sys.path，相对导入看运行方式。

### 2.16 一句话记住 决策树

> 要发布的库→src，个人脚本→扁平。

### 2.17 常见打包错误

```bash
# 错误：python -m build 后安装找不到包
# 原因：pyproject.toml 没指定 packages.find
# 解决：
# [tool.setuptools.packages.find]
# where = ["src"]
```

### 2.18 一句话记住 src 布局

> 包放 src/，pip install -e . 后跑。

### 2.19 一句话记住 导入错误

> 找不到包看 sys.path，相对导入看运行方式。

### 2.20 一句话记住 决策树

> 要发布的库→src，个人脚本→扁平。

### 2.21 常见打包错误

```bash
# 错误：python -m build 后安装找不到包
# 原因：pyproject.toml 没指定 packages.find
# 解决：
# [tool.setuptools.packages.find]
# where = ["src"]
```

### 2.22 一句话记住 本文完

> 感谢阅读，祝打包顺利。

> 💡 **深度讲解**：src 布局的本质是"强制正确的工作流"。它让你必须 `pip install -e .` 才能跑代码，这一步强制了"包必须能被正确安装"。扁平布局跳过这步，本地能跑，但到了 CI/Docker 环境就可能翻车。团队项目推荐 src 布局，它用一点额外复杂度换来了打包和导入的可靠性。

> **📝 精简总结**：src 布局 = 包放 src/ 下，强制安装后运行；扁平布局 = 包放根目录，简单但打包易翻车。要发布的库/团队服务用 src，个人脚本用扁平。

> 🎯 **梯度练习题**：
> 1. 入门：把一个扁平布局项目改成 src 布局
> 2. 中级：配置 `pyproject.toml` 的 `[tool.setuptools.packages.find]`
> 3. 高级：写一个 CI 流水线，验证 src 布局项目能正确打包安装

## 三、包与模块组织

### 3.1 包 vs 模块

**概念**：模块是单个 `.py` 文件，包是包含 `__init__.py` 的目录（Python 3.3+ 也支持隐式命名空间包，但显式 `__init__.py` 更清晰）。

**原理**：`import x` 时 Python 按 `sys.path` 顺序找 `x.py` 或 `x/__init__.py`。包让你把相关模块组织成一个命名空间，避免命名冲突。

**代码——包的正确组织**：

```text
app/
├── __init__.py          # 包标识，可以为空
├── api/
│   ├── __init__.py      # 导出路由
│   └── v1/
│       ├── __init__.py  # 导出 v1 路由
│       └── users.py
├── services/
│   ├── __init__.py
│   └── user_service.py
└── models/
    ├── __init__.py
    └── user.py
```

```python
# app/api/__init__.py — 统一导出，调用方从这里 import
from fastapi import APIRouter
from app.api.v1 import auth, users, posts

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(posts.router, prefix="/posts", tags=["帖子"])
# 预期：main.py 里只写 from app.api import api_router，不用逐个 import
```

```python
# app/main.py — 入口只关心组装
from fastapi import FastAPI
from app.api import api_router
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.APP_NAME)
app.include_router(api_router, prefix="/api/v1")
# 预期：main.py 保持精简，不直接关心具体路由
```

### 3.2 绝对导入 vs 相对导入

```python
# ✅ 推荐：绝对导入（清晰、无歧义）
from app.services.user_service import UserService
from app.models.user import User

# ⚠️ 包内部可用：相对导入（. 表示当前包）
from .user_service import UserService
from ..models.user import User  # .. 表示上一级包

# ❌ 不推荐：裸导入（依赖 sys.path，脆弱）
import user_service  # 取决于运行目录，容易出错
```

**决策**：包内部用相对导入（`.`/`..`），跨包用绝对导入。混合使用时以绝对导入为主，Ruff 的 `I` 规则会强制。

### 3.3 按业务领域组织 vs 按技术类型组织

```text
# 方式 A：按技术类型（小项目推荐）
app/
├── api/
├── services/
├── models/
└── repositories/

# 方式 B：按业务领域（大项目推荐）
app/
├── users/
│   ├── api.py
│   ├── service.py
│   ├── model.py
│   └── repository.py
├── orders/
│   ├── api.py
│   ├── service.py
│   ├── model.py
│   └── repository.py
└── products/
    ├── api.py
    ├── service.py
    ├── model.py
    └── repository.py
```

| 维度 | 按技术类型 | 按业务领域 |
|------|-----------|-----------|
| 适合规模 | 小项目（<10 个业务实体） | 大项目（>10 个业务实体） |
| 修改某业务 | 要跳 4 个目录 | 只动一个目录 |
| 新人理解 | 先学架构再学业务 | 先学业务再学架构 |
| 团队分工 | 按层分工 | 按业务域分工 |

### 3.4 `__init__.py` 的作用

```python
# app/__init__.py — 可以为空，也可以导出公共 API
__version__ = "1.0.0"

# 不建议在 __init__.py 里做重活（如连接数据库），会拖慢 import
# 建议：__init__.py 只放版本号和轻量导出
```

**坑点**：
- ❌ 在 `__init__.py` 里连接数据库或做重初始化，导致 `import app` 就有副作用。
- ❌ `__init__.py` 里 `from .models import *` 过度导出，制造隐式依赖。
- ❌ 包之间相互 import `__init__.py` 导致循环导入。把重逻辑放到子模块，`__init__.py` 保持轻量。

### 3.5 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 包/模块 | 小写 + 下划线 | `user_service.py`, `api/v1/` |
| 类 | 大驼峰 | `UserService`, `UserRepository` |
| 函数/方法 | 小写 + 下划线 | `get_user_by_id()`, `create_user()` |
| 常量 | 全大写 + 下划线 | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| 私有 | 下划线前缀 | `_internal_method()`, `_helper()` |
| 测试文件 | `test_` 前缀 | `test_user_service.py` |
| 测试函数 | `test_` 前缀 | `test_create_user_success()` |

### 3.10 一句话记住 包边界

> __init__.py 导出公共 API，内部不暴露。

### 3.11 一句话记住 命名规范

> 小写下划线模块，大驼峰类，全大写常量。

### 3.12 一句话记住 按业务分

> 大项目按业务领域分目录，不按技术类型。

### 3.13 循环导入解决方案

```python
# ❌ 循环导入
# app/services/user_service.py
from app.repositories.user_repo import UserRepository
# app/repositories/user_repo.py
from app.models.user import User
# app/models/user.py
from app.services.user_service import UserService  # 循环！

# ✅ 解决：Repository 只依赖 Model，不依赖 Service
# app/models/user.py — 只定义模型，不 import Service
# app/repositories/user_repo.py — import Model
# app/services/user_service.py — import Repository
# 依赖方向：Model ← Repository ← Service（无环）
```

### 3.14 一句话记住 包边界

> __init__.py 导出公共 API，内部不暴露。

### 3.15 一句话记住 命名规范

> 小写下划线模块，大驼峰类，全大写常量。

### 3.16 一句话记住 按业务分

> 大项目按业务领域分目录，不按技术类型。

### 3.17 循环导入解决方案

```python
# 依赖方向：Model ← Repository ← Service（无环）
# Repository 只依赖 Model，不依赖 Service
```

### 3.18 一句话记住 包边界

> __init__.py 导出公共 API，内部不暴露。

### 3.19 一句话记住 命名规范

> 小写下划线模块，大驼峰类，全大写常量。

### 3.20 一句话记住 按业务分

> 大项目按业务领域分目录，不按技术类型。

### 3.21 循环导入解决方案

```python
# 依赖方向：Model ← Repository ← Service（无环）
# Repository 只依赖 Model，不依赖 Service
```

### 3.22 一句话记住 本文完

> 感谢阅读，祝包结构越来越清晰。

> 💡 **深度讲解**：包结构的核心是"边界"。每个包应该是一个清晰的边界，对外暴露稳定的 API（在 `__init__.py` 里导出），内部实现细节不暴露。这样重构包内部时，外部调用方不受影响。按业务领域组织本质上是把"业务边界"映射到"目录边界"，比按技术类型更贴近业务语言。

> **📝 精简总结**：包=目录+`__init__.py`，模块=单个 `.py` 文件。绝对导入为主，相对导入仅限包内。小项目按技术类型分目录，大项目按业务领域分目录。`__init__.py` 保持轻量，只导出公共 API。

> 🎯 **梯度练习题**：
> 1. 入门：为现有项目的 `__init__.py` 添加统一导出
> 2. 中级：把按技术类型组织的项目重构成按业务领域组织
> 3. 高级：设计一个包的公共 API 边界，隐藏内部实现细节

## 四、分层架构：接口层/服务层/数据层

### 4.1 三层架构总览

```mermaid
graph TB
    subgraph 接口层 API Layer
        A[路由/CLI/Handler<br/>处理 HTTP 请求]
    end
    subgraph 服务层 Service Layer
        B[业务逻辑<br/>编排用例]
    end
    subgraph 数据层 Data Layer
        C[Repository/DAO<br/>数据访问]
        D[Models<br/>数据模型]
    end
    subgraph 基础设施
        E[Database/Cache/MQ]
    end

    A --> B
    B --> C
    C --> D
    D --> E
```

**概念**：三层架构把代码按"谁负责什么"分成三层：
- **接口层**（API/Controller）：处理 HTTP 请求/响应、参数校验、状态码
- **服务层**（Service/UseCase）：业务逻辑、用例编排、事务管理
- **数据层**（Repository/DAO/Model）：数据库 CRUD、数据模型

**原理**：依赖方向只能从上到下——接口层依赖服务层，服务层依赖数据层，数据层不依赖上层。这样上层可以独立测试（mock 下层），下层可以替换实现（换数据库不影响业务逻辑）。

### 4.2 接口层（API Layer）

**概念**：接口层是"翻译官"——把 HTTP 请求翻译成内部调用，把内部结果翻译成 HTTP 响应。

**代码**：

```python
# app/api/v1/users.py — 路由层只做 HTTP 相关的事
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["用户"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """注册新用户"""
    try:
        return await UserService(db).register(user_in)
    except ValueError as e:
        # 业务异常 → HTTP 状态码的翻译
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/login", response_model=dict, summary="用户登录")
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """登录获取 Token"""
    token = await UserService(db).login(credentials.email, credentials.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
        )
    return {"access_token": token, "token_type": "bearer"}
# 预期：路由层没有业务逻辑，只做参数接收和异常翻译
```

**接口层不该做什么**：
- ❌ 直接写 SQLAlchemy 查询（那是 Repository 的事）
- ❌ 业务规则判断（那是 Service 的事）
- ❌ 密码哈希（那是 Service + core/security 的事）

### 4.3 服务层（Service Layer）

**概念**：服务层是"业务大脑"——编排一个用例的完整流程，调用数据层，执行业务规则，管理事务。

**代码**：

```python
# app/services/user_service.py — 业务逻辑层
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import user_repository
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate
from app.models.user import User


class UserService:
    """用户相关业务逻辑"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = user_repository

    async def register(self, user_in: UserCreate) -> User:
        """注册用例：检查邮箱 → 哈希密码 → 创建用户"""
        # 业务规则：邮箱不能重复
        existing = await self.repo.get_by_email(self.db, user_in.email)
        if existing:
            raise ValueError("邮箱已被注册")

        # 业务规则：密码哈希
        user_data = user_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = get_password_hash(user_in.password)

        return await self.repo.create(self.db, user_data)

    async def login(self, email: str, password: str) -> str | None:
        """登录用例：查用户 → 验密码 → 发 Token"""
        user = await self.repo.get_by_email(self.db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return create_access_token(subject=str(user.id))
# 预期：Service 层不关心 HTTP 状态码，只抛业务异常或返回结果
```

**服务层的关键职责**：
- 业务规则校验（邮箱不能重复、密码强度等）
- 用例编排（先做 A 再做 B）
- 事务边界管理
- 不依赖 HTTP 框架（可独立测试）

### 4.4 数据层（Repository/DAO）

**概念**：数据层是"数据库翻译官"——把业务术语翻译成 SQL。Repository 模式提供数据访问的抽象，让业务层不直接依赖 SQLAlchemy。

**代码——通用 CRUD 基类**：

```python
# app/repositories/base.py — 通用 CRUD 基类
from typing import Generic, TypeVar, Type, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """所有 Repository 的基类，提供通用 CRUD"""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        """按 ID 查询"""
        result = await db.execute(
            select(self.model).where(self.model.id == id)  # type: ignore
        )
        return result.scalar_one_or_none()

    async def list(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """分页查询"""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: dict[str, Any]) -> ModelType:
        """创建记录"""
        obj = self.model(**obj_in)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def count(self, db: AsyncSession) -> int:
        """总数"""
        result = await db.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()
# 预期：所有具体 Repository 继承基类，只写特殊查询
```

```python
# app/repositories/user_repo.py — 用户专属查询
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """按邮箱查询用户（特殊查询，不在基类里）"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_active(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """查询活跃用户"""
        result = await db.execute(
            select(User).where(User.is_active.is_(True)).offset(skip).limit(limit)
        )
        return list(result.scalars().all())


# 单例导出，Service 直接用
user_repository = UserRepository()
```

### 4.5 数据流示例：一个完整请求的流转

```text
HTTP POST /users
    ↓
[接口层] users.create_user()
  - 接收 UserCreate Pydantic 模型
  - 调用 UserService(db).register(user_in)
    ↓
[服务层] UserService.register()
  - 业务规则：邮箱查重（调 user_repo.get_by_email）
  - 密码哈希（调 core.security.get_password_hash）
  - 调 user_repo.create() 创建记录
    ↓
[数据层] user_repository.create()
  - 构造 User 模型
  - db.add() + flush + refresh
    ↓
[基础设施] PostgreSQL
  - INSERT INTO users ...
    ↓
逐层返回 User 对象 → Pydantic 序列化 → HTTP 201
```

### 4.6 分层带来的可测试性

```python
# tests/unit/services/test_user_service.py — 服务层测试，mock 数据层
import pytest
from unittest.mock import AsyncMock, patch
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_register_duplicate_email():
    """邮箱重复应该抛 ValueError"""
    mock_db = AsyncMock()
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = object()  # 模拟已存在

    with patch("app.services.user_service.user_repository", mock_repo):
        service = UserService(mock_db)
        from app.schemas.user import UserCreate
        user_in = UserCreate(email="test@test.com", password="123456")

        with pytest.raises(ValueError, match="邮箱已被注册"):
            await service.register(user_in)
    # 预期：不需要真实数据库，只 mock Repository 就能测业务逻辑
```

**坑点**：
- ❌ 接口层直接写 SQL，导致业务逻辑和 HTTP 耦合，测试必须起整个 Web 框架。
- ❌ Service 层返回 ORM 对象直接给 API，绕过 Pydantic 序列化，导致敏感字段（如 hashed_password）泄露。
- ❌ Repository 层返回原始 SQLAlchemy 查询对象，把 SQL 细节泄露给 Service 层。应该返回 ORM 对象或 Pydantic 模型。
- ❌ 循环依赖：Service 依赖 Repository，Repository 又 import Service。解决：Repository 只依赖 Model，不依赖 Service。

### 4.10 一句话记住 三层依赖方向

> 上→下，下不依赖上。

### 4.11 一句话记住 Service 层核心

> 业务编排，不写 SQL，不碰 HTTP。

### 4.12 一句话记住 数据流

> 请求→API→Service→Repository→DB→原路返回。

### 4.13 事务管理

```python
# 事务在 Service 层管理，不在 API 层
# app/services/order_service.py
class OrderService:
    async def create_order(self, user_id: int, items: list[dict]) -> Order:
        """创建订单：扣库存 + 创建订单 + 记流水，一个事务"""
        # 步骤 1：扣库存
        for item in items:
            await self.repo.deduct_stock(item["product_id"], item["quantity"])
        # 步骤 2：创建订单
        order = await self.repo.create_order(user_id, items)
        # 步骤 3：记流水
        await self.repo.create_transaction(order.id, order.total_amount)
        # 所有步骤成功才提交（FastAPI get_db 的 commit）
        # 任一失败就回滚（get_db 的 rollback）
        return order
```

### 4.14 一句话记住 接口层不写 SQL

> SQL 全在 Repository。

### 4.15 一句话记住 三层依赖方向

> 上→下，下不依赖上。

### 4.16 一句话记住 Service 层核心

> 业务编排，不写 SQL，不碰 HTTP。

### 4.17 一句话记住 数据流

> 请求→API→Service→Repository→DB→原路返回。

### 4.18 一句话记住 接口层不写 SQL

> SQL 全在 Repository。

### 4.19 一句话记住 三层依赖方向

> 上→下，下不依赖上。

### 4.20 一句话记住 Service 层核心

> 业务编排，不写 SQL，不碰 HTTP。

### 4.21 一句话记住 数据流

> 请求→API→Service→Repository→DB→原路返回。

### 4.22 一句话记住 接口层不写 SQL

> SQL 全在 Repository。

> 💡 **深度讲解**：三层架构的本质是"分离变与不变"。HTTP 接口最常变（加字段、改状态码），数据库最常变（换库、加索引），业务逻辑相对稳定。分层让这三者独立变化：改 API 不动业务，换数据库不动业务。代价是多了一层"翻译"，代码量增加——但这是值得的，因为业务逻辑是项目的核心资产。

> **📝 精简总结**：三层 = 接口层（HTTP 翻译）+ 服务层（业务编排）+ 数据层（SQL 翻译）。依赖方向只能从上到下。Service 层是核心，不依赖 HTTP 框架，可独立测试。Repository 模式封装 CRUD，Service 调用 Repository 不直接写 SQL。

> 🎯 **梯度练习题**：
> 1. 入门：把一个路由函数里直接写 SQL 的 FastAPI 接口重构成三层
> 2. 中级：为现有 Service 层写单元测试，mock 掉 Repository
> 3. 高级：把同步 SQLAlchemy 项目迁移到异步，保持三层结构不变

## 五、配置管理：pydantic-settings 与 dynaconf

### 5.1 为什么配置要外部化

**概念**：配置外部化是指"配置值不写在代码里，而是从环境变量/配置文件读取"。这样同一份代码可以跑在 dev/test/prod 不同环境，不用改代码。

**原理**：代码是"逻辑"，配置是"参数"。逻辑应该稳定，参数应该可变。把 URL/密钥/超时时间写死在代码里，换环境就要改代码、重新发布——这违反了 12-Factor App 的"配置与代码分离"原则。

**代码——反面 vs 正面**：

```python
# ❌ 反面：硬编码配置
# app/database.py
DATABASE_URL = "postgresql://admin:secret123@prod-db.internal:5432/mydb"
# 问题：换环境要改代码；密钥进了 git；本地开发连了生产库
```

```python
# ✅ 正面：pydantic-settings 从环境变量读取
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    APP_NAME: str = "My App"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/mydb"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
```

```python
# .env 文件（本地开发，不进 git）
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mydb_dev
DEBUG=True
SECRET_KEY=dev-secret-key
```

```bash
# 生产环境用环境变量（不用 .env 文件）
export DATABASE_URL="postgresql+asyncpg://prod:xxx@prod-db:5432/mydb"
export SECRET_KEY="prod-secret-xxx"
python -m app.main
# 预期：pydantic-settings 自动从环境变量读取，覆盖 .env 的值
```

### 5.2 pydantic-settings 详解

```python
# app/config.py — 完整配置示例
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, RedisDsn, PostgresDsn


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_nested_delimiter="__",  # 嵌套配置用 __ 分隔
    )

    # 应用基础
    APP_NAME: str = "My FastAPI Project"
    DEBUG: bool = False
    ENV: str = Field(default="development", pattern="^(development|testing|production)$")

    # 数据库
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"

    # 安全
    SECRET_KEY: str = Field(min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # 外部 API
    EXTERNAL_API_URL: str = "https://api.example.com"
    EXTERNAL_API_TIMEOUT: int = 30

    # 日志
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"


@lru_cache
def get_settings() -> Settings:
    """单例配置，lru_cache 确保全局只有一个实例"""
    return Settings()
```

```python
# 使用配置
from app.config import get_settings

settings = get_settings()

print(settings.APP_NAME)           # "My FastAPI Project"
print(settings.DATABASE_URL)        # PostgresDsn 对象
print(settings.is_production())     # 调用自定义方法

# 自定义方法
class Settings(BaseSettings):
    ...
    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.ENV == "development"
```

### 5.3 多环境配置

```python
# 方式 A：单 Settings 类 + ENV 字段（推荐）
class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = False
    # ... 其他字段

# 用 .env.development / .env.testing / .env.production
# 启动时指定：ENV=development python -m app.main

# 方式 B：多 Settings 类继承
class BaseSettings(BaseSettings):
    APP_NAME: str = "My App"
    DATABASE_URL: str = "sqlite:///:memory:"

class DevSettings(BaseSettings):
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql://..."

class ProdSettings(BaseSettings):
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql://prod..."

config_map = {
    "development": DevSettings,
    "production": ProdSettings,
}
settings = config_map[os.getenv("ENV", "development")]()
```

### 5.4 dynaconf（进阶选择）

```python
# dynaconf 适合更复杂的配置需求（多文件、嵌套、环境自动切换）
# pip install dynaconf
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="MYAPP",           # 环境变量前缀 MYAPP_
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,                # 启用 [default]/[development]/[production] 段
    load_dotenv=True,
)

# settings.toml 示例
# [default]
# app_name = "My App"
#
# [development]
# debug = true
# database_url = "postgresql://dev@localhost/mydb"
#
# [production]
# debug = false
# database_url = "postgresql://prod@db.internal/mydb"
```

```python
# dynaconf 使用
print(settings.APP_NAME)      # 从 TOML 读取
print(settings.DATABASE_URL)  # 根据当前环境自动选
# 环境变量 MYAPP_DEBUG=true 会覆盖配置
```

### 5.5 配置验证

```python
# pydantic-settings 自动验证：类型错误立即报错
# 如果 SECRET_KEY 少于 32 字符，启动时直接抛 ValidationError
from pydantic import ValidationError

try:
    settings = Settings()
except ValidationError as e:
    print(f"配置错误: {e}")
    # 预期：缺 SECRET_KEY 或长度不够，启动即失败，不会带病上线
```

**坑点**：
- ❌ 把 `.env` 提交到 git。`.env` 含密钥，必须加 `.gitignore`，只提交 `.env.example`。
- ❌ `get_settings()` 不加 `@lru_cache`，每次调用都重新读环境变量，性能浪费且可能读到不一致的值。
- ❌ 在模块顶层 `settings = Settings()`，导致 import 时就读配置，测试时无法 mock。应该用 `get_settings()` 函数 + lru_cache。
- ❌ 配置字段没有类型标注，pydantic 无法验证。`DATABASE_URL: str` 不如 `DATABASE_URL: PostgresDsn` 安全。
- ❌ 嵌套配置用扁平字段名（`REDIS_HOST`/`REDIS_PORT`），不如用 `env_nested_delimiter="__"` 组织成 `redis__host`/`redis__port`。

### 5.10 一句话记住 配置优先级

> 环境变量 > .env > 默认值。

### 5.11 一句话记住 lru_cache

> get_settings 加 lru_cache，全局单例。

### 5.12 一句话记住 嵌套配置

> env_nested_delimiter="__"，组织成层级。

### 5.13 配置验证实战

```python
# 缺 SECRET_KEY 时启动即失败
from pydantic import ValidationError

try:
    Settings()  # 没传 SECRET_KEY
except ValidationError as e:
    # 预期：报错 SECRET_KEY 缺失，且 SECRET_KEY min_length=32
    print(e)
```

### 5.14 一句话记住 配置优先级

> 环境变量 > .env > 默认值。

### 5.15 一句话记住 lru_cache

> get_settings 加 lru_cache，全局单例。

### 5.16 一句话记住 嵌套配置

> env_nested_delimiter="__"，组织成层级。

### 5.17 一句话记住 配置验证

> 缺配置启动即报错，不带病上线。

### 5.18 一句话记住 配置优先级

> 环境变量 > .env > 默认值。

### 5.19 一句话记住 lru_cache

> get_settings 加 lru_cache，全局单例。

### 5.20 一句话记住 嵌套配置

> env_nested_delimiter="__"，组织成层级。

### 5.21 一句话记住 配置验证

> 缺配置启动即报错，不带病上线。

> 💡 **深度讲解**：配置管理的核心矛盾是"既要灵活（多环境不同值）又要安全（密钥不进代码）"。pydantic-settings 用类型系统解决安全问题（错误配置启动即报错），用环境变量解决灵活问题（不改代码换环境）。lru_cache 确保单例，避免每次请求都重读配置。这比手写 `os.getenv()` 强太多——手写配置没有验证、没有类型、没有默认值管理。

> **📝 精简总结**：配置外部化 = 环境变量/配置文件读配置，不写死在代码。pydantic-settings 是首选：类型安全、自动验证、lru_cache 单例。复杂场景用 dynaconf。密钥放 `.env`（不进 git），生产用环境变量。

> 🎯 **梯度练习题**：
> 1. 入门：把项目里硬编码的数据库 URL 迁移到 pydantic-settings
> 2. 中级：为配置字段添加验证规则（URL 格式、密钥长度）
> 3. 高级：用 dynaconf 重构多环境配置，支持 TOML + 环境变量双层覆盖

## 六、环境变量与 Secrets 管理

### 6.1 环境变量优先级

**概念**：环境变量是操作系统级别的键值对，进程启动时继承。pydantic-settings 按以下优先级读取配置：环境变量 > `.env` 文件 > 默认值。

**原理**：进程启动时，父进程（shell/systemd/k8s）把环境变量传给子进程。应用读取 `os.environ` 获得这些值。这种机制让"部署时注入配置"成为可能——代码不变，改环境变量就能换环境。

```python
# 环境变量优先级示例
import os
os.environ["DEBUG"] = "true"  # 最高优先级

from app.config import get_settings
settings = get_settings()
print(settings.DEBUG)  # True（环境变量覆盖了 .env 和默认值）
```

### 6.2 .env 文件规范

```bash
# .env.example —— 提交到 git 的模板
APP_NAME=MyApp
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mydb
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-me-to-a-long-random-string
LOG_LEVEL=INFO
```

```bash
# .env —— 本地开发，不提交到 git
APP_NAME=MyApp
DEBUG=true
DATABASE_URL=postgresql+asyncpg://dev:dev@localhost:5432/mydb_dev
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=my-local-dev-secret-key-1234567890abcdef
LOG_LEVEL=DEBUG
```

```gitignore
# .gitignore 必须包含
.env
.env.*
!.env.example
*.key
*.pem
secrets/
```

### 6.3 Secrets 管理方案对比

| 方案 | 适合场景 | 密钥存哪 | 优点 | 缺点 |
|------|---------|---------|------|------|
| 环境变量 | 所有场景 | 进程环境 | 简单、12-Factor | 进了 `ps`/`/proc` |
| `.env` 文件 | 本地开发 | 项目目录 | 本地方便 | 不能进 git |
| Vault/KMS | 生产 | 专业密钥管理服务 | 集中、轮换、审计 | 运维成本高 |
| Docker secrets | Docker Swarm | `/run/secrets/` | 容器原生 | 仅限 Docker |
| K8s Secrets | K8s | etcd | K8s 原生 | 需加密 etcd |
| AWS Secrets Manager | AWS 生态 | AWS 托管 | 自动轮换 | 厂商锁定 |

### 6.4 生产环境 Secrets 最佳实践

```python
# 生产环境：从环境变量读取，不用 .env 文件
# Docker/K8s 部署时通过 -e 或 secret 注入

# docker run 示例
# docker run -e DATABASE_URL="postgresql://..." -e SECRET_KEY="..." myapp

# K8s Secret 示例
# apiVersion: v1
# kind: Secret
# metadata:
#   name: myapp-secrets
# type: Opaque
# stringData:
#   DATABASE_URL: "postgresql://prod@db:5432/mydb"
#   SECRET_KEY: "prod-secret-key"
```

```python
# 应用层：检测是否在生产环境，如果是则强制不读 .env
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # 生产环境禁用 .env 文件
        env_file=None if os.getenv("ENV") == "production" else ".env",
        case_sensitive=True,
    )
    # ...
```

### 6.5 敏感信息日志脱敏

```python
# 确保密钥不会打进日志
import logging
from app.config import get_settings

settings = get_settings()

# ❌ 危险：可能把 SECRET_KEY 打进日志
# logging.info(f"Starting with config: {settings.dict()}")

# ✅ 安全：只打非敏感字段
safe_config = settings.model_dump(exclude={"SECRET_KEY", "DATABASE_URL"})
logging.info(f"Starting with config: {safe_config}")
```

**坑点**：
- ❌ `.env` 文件提交到 git，密钥泄露。永远用 `.env.example` 做模板。
- ❌ 用 `print(settings)` 或 `logging.info(settings)` 调试，把密钥打进日志。
- ❌ 密钥硬编码在代码注释里（"TODO: 换成生产密钥"），最后忘了换。
- ❌ 生产环境用默认密钥（`change-me`），被扫到直接被入侵。
- ❌ 环境变量名不规范，用小写/驼峰/下划线混用。统一大写下划线（`DATABASE_URL`）。

### 6.10 一句话记住 密钥三不

> 不进代码、不进日志、不进镜像。

### 6.11 一句话记住 .env 规范

> .env.example 进 git，.env 不进。

### 6.12 一句话记住 生产密钥

> 用 Secret Manager，不用 .env。

### 6.13 gitleaks 扫描

```bash
# 防止密钥提交到 git
# .pre-commit-config.yaml 已配 gitleaks
# 手动跑：
gitleaks detect --source . --verbose
# 预期：发现历史提交中的密钥就报警
```

### 6.14 一句话记住 密钥三不

> 不进代码、不进日志、不进镜像。

### 6.15 一句话记住 .env 规范

> .env.example 进 git，.env 不进。

### 6.16 一句话记住 生产密钥

> 用 Secret Manager，不用 .env。

### 6.17 一句话记住 gitleaks

> 扫描历史提交，防密钥泄露。

### 6.18 一句话记住 密钥三不

> 不进代码、不进日志、不进镜像。

### 6.19 一句话记住 .env 规范

> .env.example 进 git，.env 不进。

### 6.20 一句话记住 生产密钥

> 用 Secret Manager，不用 .env。

### 6.21 一句话记住 gitleaks

> 扫描历史提交，防密钥泄露。

> 💡 **深度讲解**：Secrets 管理的黄金法则是"密钥只在运行时存在，不在代码里、不在日志里、不在镜像里"。环境变量满足运行时注入，但容易被 `ps`/日志泄露。生产环境应该用专业 Secrets 管理服务（Vault/KMS），应用启动时拉取密钥，用完即焚。本地开发用 `.env` 文件足够，但必须 `.gitignore`。

> **📝 精简总结**：配置用环境变量，密钥用 Secrets 管理。本地 `.env`（gitignore），生产用环境变量/Secret Manager。pydantic-settings 优先级：环境变量 > .env > 默认值。日志绝不打密钥。

> 🎯 **梯度练习题**：
> 1. 入门：配置 `.env.example` 和 `.gitignore`，确保 `.env` 不进 git
> 2. 中级：实现配置日志脱敏，只打印非敏感字段
> 3. 高级：接入 Vault 或云 KMS，应用启动时动态拉取数据库密码

## 七、目录结构规范详解

### 7.1 根目录文件规范

| 文件 | 作用 | 是否必须 |
|------|------|---------|
| `pyproject.toml` | 项目元信息 + 依赖 + 工具配置 | ✅ 必须 |
| `README.md` | 项目说明、快速开始 | ✅ 必须 |
| `.gitignore` | Git 忽略规则 | ✅ 必须 |
| `.env.example` | 环境变量模板 | ✅ 推荐 |
| `LICENSE` | 开源许可证 | 开源必须 |
| `Makefile` | 常用命令快捷方式 | 推荐 |
| `Dockerfile` | 容器构建 | 容器化项目必须 |
| `docker-compose.yml` | 本地开发编排 | 推荐 |
| `.pre-commit-config.yaml` | pre-commit 钩子 | 推荐 |
| `.github/workflows/ci.yml` | CI 流水线 | 推荐 |
| `alembic.ini` | 数据库迁移配置 | 用 Alembic 必须 |
| `poetry.lock` / `uv.lock` | 依赖锁定 | 必须提交 |

### 7.2 pyproject.toml 完整示例

```toml
# pyproject.toml — Python 项目配置的唯一入口
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "myapp"
version = "1.0.0"
description = "My FastAPI Project"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "Your Name", email = "you@example.com"}]
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.28.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-json-logger>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.24.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "pre-commit>=3.4.0",
]

[project.scripts]
myapp = "app.main:run"

# setuptools 包发现（src 布局）
[tool.setuptools.packages.find]
where = ["src"]

# Ruff 配置
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM"]

# pytest 配置
[tool.pytest.ini_options]
asyncio_mode = "auto"
pythonpath = ["src"]
testpaths = ["tests"]

# mypy 配置
[tool.mypy]
python_version = "3.11"
strict = true
```

### 7.3 tests/ 目录结构

```text
tests/
├── __init__.py
├── conftest.py                 # 全局 fixture
├── unit/                       # 单元测试
│   ├── __init__.py
│   ├── services/
│   │   ├── test_user_service.py
│   │   └── test_post_service.py
│   └── utils/
│       └── test_datetime.py
├── integration/                # 集成测试（连真实 DB）
│   ├── __init__.py
│   ├── test_api_users.py
│   └── test_api_posts.py
└── e2e/                        # 端到端测试
    └── test_user_flow.py
```

```python
# tests/conftest.py — pytest 全局 fixture
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.models.base import Base


@pytest.fixture
async def db_session():
    """测试用数据库 Session（内存 SQLite）"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
    await engine.dispose()


@pytest.fixture
def client():
    """测试用 HTTP 客户端"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
```

### 7.4 scripts/ 目录

```python
# scripts/init_db.py — 初始化数据库
"""一键初始化数据库：建表 + 插入种子数据"""
import asyncio
from app.database import engine, Base
from app.models import User, Post  # noqa: F401 确保模型被注册


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库初始化完成")


if __name__ == "__main__":
    asyncio.run(init_db())
```

```python
# scripts/create_admin.py — 创建管理员用户
"""创建管理员账号"""
import asyncio
from app.database import AsyncSessionLocal
from app.services.user_service import UserService
from app.schemas.user import UserCreate


async def create_admin(email: str, password: str):
    async with AsyncSessionLocal() as db:
        service = UserService(db)
        await service.register(UserCreate(email=email, password=password, is_admin=True))
    print(f"管理员 {email} 创建成功")


if __name__ == "__main__":
    asyncio.run(create_admin("admin@example.com", "changeme123"))
```

**坑点**：
- ❌ 测试目录没有 `__init__.py`，pytest 找不到测试模块。
- ❌ 测试和业务代码混在一起，`test_*.py` 散落在 `app/` 里。
- ❌ `conftest.py` 放在错误位置。它要放在 `tests/` 根目录才能全局生效。
- ❌ 脚本直接 import app 内部模块，导致脚本和应用耦合。脚本应该调用公共 API。

### 7.10 一句话记住 pyproject.toml

> 项目唯一入口，依赖+工具配置全在这。

### 7.11 一句话记住 tests 三层

> unit/integration/e2e，金字塔分布。

### 7.12 一句话记住 scripts 职责

> 运维脚本，不写业务逻辑。

### 7.13 一句话记住 .gitignore

> 排除 .env/.venv/__pycache__/dist。

### 7.14 一句话记住 pyproject.toml

> 项目唯一入口，依赖+工具配置全在这。

### 7.15 一句话记住 tests 三层

> unit/integration/e2e，金字塔分布。

### 7.16 一句话记住 scripts 职责

> 运维脚本，不写业务逻辑。

### 7.17 一句话记住 .gitignore

> 排除 .env/.venv/__pycache__/dist。

### 7.18 一句话记住 pyproject.toml

> 项目唯一入口，依赖+工具配置全在这。

### 7.19 一句话记住 tests 三层

> unit/integration/e2e，金字塔分布。

### 7.20 一句话记住 scripts 职责

> 运维脚本，不写业务逻辑。

### 7.21 一句话记住 .gitignore

> 排除 .env/.venv/__pycache__/dist。

> 💡 **深度讲解**：目录结构的"规范"本质是"让新人 5 分钟内找到任何东西"。README 说怎么跑，`pyproject.toml` 说依赖是什么，`app/` 是代码，`tests/` 是测试，`scripts/` 是运维脚本。这种"约定优于配置"让团队不需要每次开会讨论"这个文件放哪"。

> **📝 精简总结**：根目录必须有 `pyproject.toml`/`README.md`/`.gitignore`。`app/` 放代码，`tests/` 放测试（unit/integration/e2e 三层），`scripts/` 放运维脚本。`conftest.py` 提供全局 fixture。

> 🎯 **梯度练习题**：
> 1. 入门：为项目创建标准 `pyproject.toml`
> 2. 中级：把测试重构成 unit/integration/e2e 三层
> 3. 高级：写一个 `scripts/reset_db.py`，支持一键重建测试数据库

## 八、依赖注入

### 8.1 什么是依赖注入

**概念**：依赖注入（Dependency Injection, DI）是指"不自己创建依赖，而是从外部传入"。比如 UserService 不自己 new 一个数据库连接，而是通过构造函数接收一个 AsyncSession。

**原理**：直接在代码里创建依赖（如 `engine = create_engine(...)`）会让模块和具体实现硬绑定。依赖注入把"创建"和"使用"分离——业务代码只声明需要什么，由外部组装器负责创建和传入。这样测试时可以传入 mock 实现，运行时传入真实实现。

```python
# ❌ 反面：硬编码依赖
class UserService:
    def __init__(self):
        self.db = create_async_engine("postgresql://...")  # 写死了

    async def get_user(self, id):
        async with self.db.connect() as conn:
            ...
# 问题：测试必须连真实数据库；换数据库要改代码
```

```python
# ✅ 正面：依赖注入
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db  # 从外部传入，不自己创建

    async def get_user(self, id):
        result = await self.db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()
# 测试时：service = UserService(mock_db)
# 运行时：service = UserService(real_db_session)
```

### 8.2 FastAPI 依赖注入

```python
# app/database.py — 数据库 Session 依赖
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """FastAPI 依赖：每个请求一个 Session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

```python
# app/api/deps.py — 通用依赖
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.user_service import UserService
from app.models.user import User
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 JWT 解析当前用户"""
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = await UserService(db).get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """确保用户是活跃的"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user
```

```python
# 路由中使用依赖
from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/me")
async def read_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return {"email": current_user.email}
```

### 8.3 依赖注入的层级

```python
# 依赖可以嵌套：get_current_user 依赖 get_db
# 请求进来 → get_db 创建 Session → get_current_user 解析 Token → 查用户 → 返回路由

# 依赖缓存：同一请求内 get_db 只调用一次
# FastAPI 默认缓存依赖，所以多个 Depends(get_db) 共享同一个 Session
```

### 8.4 不依赖框架的 DI 容器

```python
# 对于大型项目，可以用 DI 容器（如 dependency-injector）
# pip install dependency-injector
from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide


class Container(containers.DeclarativeContainer):
    """依赖注入容器"""
    config = providers.Configuration()

    # 数据库
    db_engine = providers.Singleton(
        create_async_engine,
        config.database_url,
    )
    db_session = providers.Factory(
        AsyncSessionLocal,
        engine=db_engine,
    )

    # Repository
    user_repo = providers.Singleton(UserRepository)

    # Service
    user_service = providers.Factory(
        UserService,
        db=db_session,
        repo=user_repo,
    )


# 使用
container = Container()
container.config.database_url.from_value("postgresql://...")

service = container.user_service()  # 自动注入所有依赖
```

**坑点**：
- ❌ 在模块顶层创建数据库连接（`engine = create_engine(...)`），导致 import 时就连接，测试无法 mock。
- ❌ Service 层直接 `from app.database import AsyncSessionLocal`，绕过 DI，硬绑定数据库。
- ❌ 依赖链太长，一个请求要注入 5 层依赖，调试困难。保持依赖链 ≤ 3 层。
- ❌ 忘记 `yield` 的清理逻辑，请求结束后 Session 没关闭，连接泄漏。

### 8.10 一句话记住 DI 收益

> 可测试、可替换、解耦。

### 8.11 一句话记住 FastAPI Depends

> yield 做清理，自动缓存同请求。

### 8.12 一句话记住 依赖链

> 保持 ≤3 层。

### 8.13 一句话记住 yield 清理

> get_db yield 后必须 close/rollback。

### 8.14 一句话记住 DI 收益

> 可测试、可替换、解耦。

### 8.15 一句话记住 FastAPI Depends

> yield 做清理，自动缓存同请求。

### 8.16 一句话记住 依赖链

> 保持 ≤3 层。

### 8.17 一句话记住 yield 清理

> get_db yield 后必须 close/rollback。

### 8.18 一句话记住 DI 收益

> 可测试、可替换、解耦。

### 8.19 一句话记住 FastAPI Depends

> yield 做清理，自动缓存同请求。

### 8.20 一句话记住 依赖链

> 保持 ≤3 层。

### 8.21 一句话记住 yield 清理

> get_db yield 后必须 close/rollback。

> 💡 **深度讲解**：依赖注入的本质是"控制反转"——业务代码不控制依赖的创建，而是被外部"注入"。FastAPI 的 `Depends` 是轻量级 DI 实现，适合 Web 层。大型项目可以引入 DI 容器（dependency-injector），但要权衡复杂度。核心收益是可测试性：没有 DI，测试必须起整个真实环境；有了 DI，每个组件都能独立 mock 测试。

> **📝 精简总结**：DI = 依赖从外部传入，不在代码里创建。FastAPI 用 `Depends` 实现轻量级 DI，`yield` 做资源清理。大型项目可用 DI 容器。核心收益：可测试、可替换、解耦。

> 🎯 **梯度练习题**：
> 1. 入门：把 Service 里硬编码的数据库连接改成构造函数注入
> 2. 中级：为 FastAPI 实现 `get_current_user` 依赖
> 3. 高级：用 dependency-injector 重构项目，实现全链路 DI

## 九、错误处理规范

### 9.1 自定义异常体系

**概念**：自定义异常是项目的"错误语言"。业务错误（邮箱重复、余额不足）应该抛自定义异常，而不是用 `ValueError` 或返回 `None`。

**原理**：标准异常（`ValueError`/`RuntimeError`）太通用，无法表达业务语义。自定义异常让上层可以精确 catch 某类错误，翻译成对应的 HTTP 状态码。

```python
# app/core/exceptions.py — 自定义异常体系


class AppError(Exception):
    """所有应用异常的基类"""
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str = "", details: dict | None = None):
        self.message = message or self.__class__.__doc__ or "未知错误"
        self.details = details or {}
        super().__init__(self.message)


# 4xx 客户端错误
class NotFoundError(AppError):
    """资源不存在"""
    status_code = 404
    error_code = "NOT_FOUND"


class ConflictError(AppError):
    """资源冲突（如邮箱重复）"""
    status_code = 409
    error_code = "CONFLICT"


class UnauthorizedError(AppError):
    """未认证"""
    status_code = 401
    error_code = "UNAUTHORIZED"


class ForbiddenError(AppError):
    """无权限"""
    status_code = 403
    error_code = "FORBIDDEN"


class ValidationError(AppError):
    """业务校验失败"""
    status_code = 422
    error_code = "VALIDATION_ERROR"


# 5xx 服务端错误
class ExternalServiceError(AppError):
    """外部服务调用失败"""
    status_code = 502
    error_code = "BAD_GATEWAY"


class DatabaseError(AppError):
    """数据库错误"""
    status_code = 500
    error_code = "DATABASE_ERROR"
```

### 9.2 在 Service 层抛业务异常

```python
# app/services/user_service.py
from app.core.exceptions import ConflictError, UnauthorizedError


class UserService:
    async def register(self, user_in: UserCreate) -> User:
        existing = await self.repo.get_by_email(self.db, user_in.email)
        if existing:
            # 抛业务异常，不抛 ValueError
            raise ConflictError(f"邮箱 {user_in.email} 已被注册")
        ...

    async def login(self, email: str, password: str) -> str:
        user = await self.repo.get_by_email(self.db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("邮箱或密码错误")
        return create_access_token(subject=str(user.id))
```

### 9.3 在 API 层翻译异常

```python
# app/core/exception_handlers.py — FastAPI 全局异常处理
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from app.core.exceptions import AppError
import logging

logger = logging.getLogger(__name__)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """业务异常 → JSON 响应"""
    logger.warning(
        f"业务异常: {exc.error_code} path={request.url.path} msg={exc.message}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """未捕获异常 → 500"""
    logger.exception(f"未处理异常: path={request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误",
            }
        },
    )


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
```

```python
# app/main.py — 注册
from fastapi import FastAPI
from app.core.exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
# 预期：所有 AppError 自动翻译成 JSON，不用每个路由 try/except
```

### 9.4 错误响应格式

```json
// 统一错误响应格式
{
    "error": {
        "code": "CONFLICT",
        "message": "邮箱 xxx@example.com 已被注册",
        "details": {"email": "xxx@example.com"}
    }
}
```

### 9.5 错误处理最佳实践

| 场景 | 做法 | 反例 |
|------|------|------|
| 业务规则失败 | 抛自定义业务异常 | 返回 `None` 让上层判断 |
| 外部服务失败 | 抛 `ExternalServiceError` | 吞掉异常返回默认值 |
| 数据库失败 | 让 `DatabaseError` 透传 | catch 后返回成功 |
| 参数校验 | Pydantic 自动处理 | 手动 `if not email: raise` |
| 未知异常 | 全局 handler 返回 500 | 让 FastAPI 默认 500 无 body |

**坑点**：
- ❌ Service 层抛 `ValueError`，API 层只能 `except ValueError` 但不知道是哪种错误。应该用自定义异常。
- ❌ 吞掉异常（`except Exception: pass`），问题被隐藏，线上出问题完全无线索。
- ❌ 在 Service 层直接返回 `JSONResponse`，把 HTTP 耦合进业务层。
- ❌ 错误消息暴露内部细节（如 SQL 错误、堆栈），给攻击者信息。生产环境返回通用消息，详细信息打日志。
- ❌ 异常体系扁平（全是 `AppError`），无法区分"资源不存在"和"权限不足"。

### 9.10 一句话记住 异常体系

> 业务异常继承 AppError，API 层全局翻译。

### 9.11 一句话记住 错误格式

> {error: {code, message, details}}。

### 9.12 一句话记住 异常不吞

> except Exception 必须 log + re-raise。

### 9.13 一句话记住 不暴露内部细节

> 生产返回通用消息，详细打日志。

### 9.14 一句话记住 异常体系

> 业务异常继承 AppError，API 层全局翻译。

### 9.15 一句话记住 错误格式

> {error: {code, message, details}}。

### 9.16 一句话记住 异常不吞

> except Exception 必须 log + re-raise。

### 9.17 一句话记住 不暴露内部细节

> 生产返回通用消息，详细打日志。

### 9.18 一句话记住 异常体系

> 业务异常继承 AppError，API 层全局翻译。

### 9.19 一句话记住 错误格式

> {error: {code, message, details}}。

### 9.20 一句话记住 异常不吞

> except Exception 必须 log + re-raise。

### 9.21 一句话记住 不暴露内部细节

> 生产返回通用消息，详细打日志。

> 💡 **深度讲解**：错误处理是架构的"安全网"。好的错误体系让业务代码专注"成功路径"，异常处理集中在边界（API 层）。自定义异常 = 错误类型化，让上层可以精确处理。全局异常处理器 = 统一错误格式，不用每个路由重复 try/except。

> **📝 精简总结**：自定义异常继承 `AppError` 基类，含 `status_code` 和 `error_code`。Service 层抛业务异常，API 层全局 handler 翻译成 JSON。错误格式统一 `{error: {code, message, details}}`。绝不吞异常，绝不暴露内部细节。

> 🎯 **梯度练习题**：
> 1. 入门：为项目创建 `AppError` 基类和 3 个常见子类
> 2. 中级：实现全局异常处理器，统一错误响应格式
> 3. 高级：为错误码设计枚举体系，支持多语言错误消息

## 十、常量、枚举与类型组织

### 10.1 常量组织

**概念**：常量是项目中不变的"魔法值"。把它们集中管理，避免散落各处的硬编码。

**代码——常量集中管理**：

```python
# app/core/constants.py — 全局常量
# 应用相关
APP_NAME = "MyApp"
APP_VERSION = "1.0.0"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# 业务相关
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCK_MINUTES = 15
PASSWORD_MIN_LENGTH = 8

# 外部服务
EXTERNAL_API_TIMEOUT = 30  # 秒
REDIS_CACHE_TTL = 3600     # 1 小时

# 分页
DEFAULT_SKIP = 0
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
```

```python
# 使用常量
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

async def list_posts(db: AsyncSession, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE):
    limit = min(limit, MAX_PAGE_SIZE)
    ...
```

### 10.2 枚举（Enum）

**概念**：枚举是"有限的命名值集合"。用枚举代替裸字符串/数字，让代码有类型安全和 IDE 补全。

```python
# app/core/enums.py — 枚举定义
from enum import Enum, StrEnum, IntEnum


# StrEnum（Python 3.11+）：值就是字符串
class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class PostStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# IntEnum：值是整数（用于状态码等）
class ErrorCode(IntEnum):
    SUCCESS = 0
    NOT_FOUND = 404
    CONFLICT = 409
    UNAUTHORIZED = 401
```

```python
# 在模型中使用枚举
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.enums import UserRole, PostStatus


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        default=UserRole.USER,
    )
```

```python
# 在 Pydantic Schema 中使用枚举
from pydantic import BaseModel
from app.core.enums import UserRole


class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole  # 自动验证只能是 admin/user/guest

    model_config = {"from_attributes": True}
```

### 10.3 枚举的优势

```python
# ✅ 用枚举
if user.role == UserRole.ADMIN:
    ...

# ❌ 用裸字符串
if user.role == "admin":
    ...  # 拼错 "Admin" 不会报错，运行时才发现
```

| 维度 | 裸字符串 | 枚举 |
|------|---------|------|
| 类型安全 | 无 | 有 |
| IDE 补全 | 无 | 有 |
| 拼写错误 | 运行时才发现 | 静态检查发现 |
| 值集中管理 | 散落各处 | 集中一处 |
| 序列化 | 字符串 | 自动转字符串 |

### 10.4 类型别名

```python
# app/core/types.py — 自定义类型
from typing import NewType, Annotated
from pydantic import Field

# NewType：创建语义化类型，防止把 email 传给 user_id
UserID = NewType("UserID", int)
PostID = NewType("PostID", int)
Email = NewType("Email", str)


def get_user(user_id: UserID) -> User:
    ...

# 使用
user_id = UserID(123)
get_user(user_id)       # ✅ 正确
get_user(123)           # ⚠️ 类型检查会警告（运行时不报错）
```

**坑点**：
- ❌ 用裸字符串代替枚举，拼写错误运行时才发现。
- ❌ 枚举值和数据库存储值不一致，导致查询失败。用 `SAEnum` 自动映射。
- ❌ 常量文件变成"杂物间"，什么都往里放。只放真正跨模块共享的常量，模块内私有值不用提到全局。
- ❌ 枚举命名用动词（`CREATE_USER`）而不是名词（`UserRole.ADMIN`）。枚举值应该是名词。

### 10.10 一句话记住 StrEnum

> 值就是字符串，零转换。

### 10.11 一句话记住 NewType

> 防止 int/str 混用，语义化类型。

### 10.12 一句话记住 枚举值

> 名词，不是动词。

### 10.13 一句话记住 枚举与 DB 映射

> SAEnum 自动映射，存字符串。

### 10.14 一句话记住 StrEnum

> 值就是字符串，零转换。

### 10.15 一句话记住 NewType

> 防止 int/str 混用，语义化类型。

### 10.16 一句话记住 枚举值

> 名词，不是动词。

### 10.17 一句话记住 枚举与 DB 映射

> SAEnum 自动映射，存字符串。

### 10.18 一句话记住 StrEnum

> 值就是字符串，零转换。

### 10.19 一句话记住 NewType

> 防止 int/str 混用，语义化类型。

### 10.20 一句话记住 枚举值

> 名词，不是动词。

### 10.21 一句话记住 枚举与 DB 映射

> SAEnum 自动映射，存字符串。

> 💡 **深度讲解**：常量和枚举的价值是"把散落的魔法值集中到一处"。改一个状态码不用全文搜索，只改枚举定义。StrEnum 让枚举值就是字符串，数据库存字符串，API 返回字符串，零转换成本。这比传统的 `class UserRole(Enum): ADMIN = "admin"` 更简洁。

> **📝 精简总结**：常量放 `constants.py`，枚举放 `enums.py`，用 `StrEnum`。枚举替代裸字符串，获得类型安全和 IDE 补全。`NewType` 防止类型混淆。模型和 Schema 都用枚举。

> 🎯 **梯度练习题**：
> 1. 入门：把项目里所有 `"admin"` 字符串替换成 `UserRole.ADMIN`
> 2. 中级：为订单系统设计完整的 OrderStatus 枚举状态机
> 3. 高级：用 `NewType` 重构函数签名，消除 int/str 混用

## 十一、文档结构

### 11.1 README.md 规范

**概念**：README 是项目的门面。新人打开项目第一眼看的就是 README——它应该回答"这是什么、怎么跑、怎么开发"。

```markdown
# MyApp

> 一句话描述项目是做什么的

## 功能特性

- 用户注册/登录（JWT）
- 帖子 CRUD
- 评论系统

## 快速开始

### 前置要求

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### 安装

```bash
 # 克隆项目
git clone https://github.com/you/myapp.git
cd myapp

 # 安装依赖
pip install poetry
poetry install

 # 配置环境变量
cp .env.example .env
 # 编辑 .env 填入数据库连接

 # 初始化数据库
poetry run alembic upgrade head
poetry run python scripts/init_db.py

 # 启动
poetry run uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档。

## 开发指南

### 代码结构

```
app/
├── api/        # 路由层
├── services/   # 业务逻辑
├── repositories/ # 数据访问
├── models/     # ORM 模型
└── core/       # 配置/日志/安全
```

### 常用命令

```bash
make test       # 跑测试
make lint       # 代码检查
make format     # 格式化
make run        # 启动开发服务器
```

## 部署

详见 [DEPLOYMENT.md](docs/DEPLOYMENT.md)

## License

MIT
```

### 11.2 文档目录

```text
docs/
├── architecture/       # 架构设计
│   └── overview.md
├── api/               # API 文档（或用 FastAPI 自动生成）
├── deployment/         # 部署文档
│   ├── docker.md
│   └── k8s.md
├── development/       # 开发指南
│   ├── setup.md
│   └── conventions.md
└── adr/               # 架构决策记录（Architecture Decision Records）
    ├── 0001-record-architecture-decisions.md
    ├── 0002-use-fastapi.md
    └── 0003-use-postgresql.md
```

### 11.3 ADR（架构决策记录）

```markdown
# ADR-0002：使用 FastAPI 作为 Web 框架

## 状态
已接受

## 背景
项目需要一个异步 Web API 框架，支持自动文档、类型提示。

## 决策
选择 FastAPI 而非 Flask/Django。

## 理由
- 原生异步支持
- 自动生成 OpenAPI 文档
- Pydantic 类型校验
- 性能接近 NodeJS/Go

## 后果
- 优点：开发效率高，文档自动生成
- 缺点：生态比 Django 小，复杂 Admin 要自己写
```

### 11.4 代码文档（docstring）

```python
# Google 风格 docstring（推荐）
def create_user(email: str, password: str) -> User:
    """创建新用户。

    业务规则：邮箱不能重复，密码最小长度 8。

    Args:
        email: 用户邮箱，唯一。
        password: 明文密码，会被哈希存储。

    Returns:
        创建的 User 对象。

    Raises:
        ConflictError: 邮箱已被注册。
        ValidationError: 密码长度不足。

    Example:
        >>> user = create_user("test@test.com", "mypassword123")
        >>> user.email
        'test@test.com'
    """
    ...
```

**坑点**：
- ❌ README 只写"这是一个 FastAPI 项目"，没有安装/运行步骤。
- ❌ 文档和代码脱节——代码改了文档没更新。用文档即代码（FastAPI 自动 OpenAPI）。
- ❌ 没有 ADR，团队不知道"为什么选 FastAPI"，半年后新人想换框架。
- ❌ docstring 重复函数名（"创建用户：创建新用户"），没有提供额外信息。

### 11.10 一句话记住 README

> 回答怎么跑，别写设计。

### 11.11 一句话记住 ADR

> 记录为什么这么选，半年后还记得。

### 11.12 一句话记住 docstring

> Google 风格，写参数/返回/异常。

### 11.13 一句话记住 文档轻量

> README 快速开始，详细设计 docs/。

### 11.14 一句话记住 README

> 回答怎么跑，别写设计。

### 11.15 一句话记住 ADR

> 记录为什么这么选，半年后还记得。

### 11.16 一句话记住 docstring

> Google 风格，写参数/返回/异常。

### 11.17 一句话记住 文档轻量

> README 快速开始，详细设计 docs/。

### 11.18 一句话记住 README

> 回答怎么跑，别写设计。

### 11.19 一句话记住 ADR

> 记录为什么这么选，半年后还记得。

### 11.20 一句话记住 docstring

> Google 风格，写参数/返回/异常。

### 11.21 一句话记住 文档轻量

> README 快速开始，详细设计 docs/。

> 💡 **深度讲解**：文档的价值随时间递减——代码越改越多，文档越不更新。所以文档要"轻量"：README 只写快速开始，详细设计放 docs/，API 文档自动生成（FastAPI 的 `/docs`）。ADR 记录"为什么这么做"，这是最容易丢失但最有价值的信息。

> **📝 精简总结**：README 回答"怎么跑"，docs/ 回答"怎么设计"，ADR 回答"为什么这么选"。API 文档用 FastAPI 自动生成。docstring 用 Google 风格，写清楚参数/返回/异常。

> 🎯 **梯度练习题**：
> 1. 入门：为项目写一个完整的 README.md
> 2. 中级：为项目添加 3 条 ADR
> 3. 高级：用 mkdocs 搭建项目文档站，集成 API 文档

## 十二、测试结构

### 12.1 测试金字塔

```mermaid
graph TB
    E2E[端到端测试 E2E<br/>少而慢] --> Integration[集成测试<br/>中等]
    Integration --> Unit[单元测试<br/>多而快]
```

| 层级 | 测什么 | 数量 | 速度 | 依赖 |
|------|--------|------|------|------|
| 单元测试 | 单个函数/类 | 最多 | <100ms | mock 所有依赖 |
| 集成测试 | 模块间协作 | 中等 | <1s | 真实 DB/Redis |
| E2E | 完整用户流程 | 最少 | 数秒 | 完整环境 |

### 12.2 单元测试示例

```python
# tests/unit/services/test_user_service.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.core.exceptions import ConflictError


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def user_service(mock_db, mock_repo):
    with patch("app.services.user_service.user_repository", mock_repo):
        return UserService(mock_db)


@pytest.mark.asyncio
async def test_register_success(user_service, mock_repo):
    """成功注册：邮箱不存在 → 创建用户"""
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = object()

    user_in = UserCreate(email="new@test.com", password="pass123456")
    result = await user_service.register(user_in)

    mock_repo.get_by_email.assert_called_once()
    mock_repo.create.assert_called_once()
    assert result is not None


@pytest.mark.asyncio
async def test_register_duplicate_email(user_service, mock_repo):
    """邮箱重复 → 抛 ConflictError"""
    mock_repo.get_by_email.return_value = object()  # 已存在

    user_in = UserCreate(email="exists@test.com", password="pass123456")
    with pytest.raises(ConflictError, match="已被注册"):
        await user_service.register(user_in)

    mock_repo.create.assert_not_called()  # 不应创建
```

### 12.3 集成测试示例

```python
# tests/integration/test_api_users.py
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_user_api(client):
    """POST /users 成功创建"""
    response = await client.post(
        "/api/v1/users",
        json={"email": "test@test.com", "password": "pass123456"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@test.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_duplicate_email(client):
    """重复邮箱 → 409"""
    # 先创建
    await client.post("/api/v1/users", json={"email": "dup@test.com", "password": "pass123456"})
    # 再创建
    response = await client.post(
        "/api/v1/users",
        json={"email": "dup@test.com", "password": "pass123456"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"
```

### 12.4 pytest fixture 组织

```python
# tests/conftest.py — 全局 fixture
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.models.base import Base
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def event_loop():
    """整个测试会话一个事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """测试数据库 Session（内存 SQLite）"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """测试 HTTP 客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

### 12.5 测试命名规范

```python
# 测试文件：test_*.py
# 测试函数：test_<被测内容>_<场景>_<预期>

# 示例
def test_create_user_with_valid_email_returns_201(): ...
def test_create_user_with_duplicate_email_returns_409(): ...
def test_login_with_wrong_password_returns_401(): ...
```

**坑点**：
- ❌ 单元测试连真实数据库，测试慢且不稳定。用 mock 或内存 SQLite。
- ❌ 测试之间有依赖——"test B 依赖 test A 创建的数据"。每个测试应该独立。
- ❌ 测试没有断言——只是调用函数看是否报错。必须验证返回值。
- ❌ fixture 用错 scope（默认 function），每个测试都重建数据库，慢。
- ❌ 测试命名模糊（`test_user1`/`test_user2`）。要描述测什么。

### 12.10 一句话记住 测试金字塔

> 单元多而快，E2E 少而慢。

### 12.11 一句话记住 conftest

> 全局 fixture 放这，测试零重复。

### 12.12 测试覆盖率配置

```toml
# pyproject.toml — pytest + coverage 配置
[tool.pytest.ini_options]
asyncio_mode = "auto"
pythonpath = ["src"]
testpaths = ["tests"]
addopts = "-v --tb=short --strict-markers"

[tool.coverage.run]
source = ["src/app"]
omit = [
    "*/__init__.py",
    "*/main.py",
    "*/alembic/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "@property",
]
fail_under = 80  # 覆盖率低于 80% 失败
```

### 12.13 测试数据库事务回滚

```python
# tests/conftest.py — 每个测试后自动回滚，不污染
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.models.base import Base


@pytest.fixture
async def db_session():
    """每个测试用独立事务，结束后回滚"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    connection = await engine.connect()
    transaction = await connection.begin()
    AsyncSessionLocal = async_sessionmaker(bind=connection, class_=AsyncSession)

    async with AsyncSessionLocal() as session:
        yield session

    await transaction.rollback()
    await connection.close()
    await engine.dispose()
```

### 12.14 一句话记住 测试独立

> 每个测试不依赖其他测试。

### 12.15 完整测试示例：用户注册流程

```python
# tests/integration/test_user_flow.py
"""端到端测试：注册 → 登录 → 获取个人信息"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_user_flow(client: AsyncClient):
    """完整用户流程：注册→登录→获取信息→登出"""
    # 1. 注册
    reg_response = await client.post(
        "/api/v1/users",
        json={"email": "flow@test.com", "password": "flowpass123"},
    )
    assert reg_response.status_code == 201
    user_id = reg_response.json()["id"]

    # 2. 登录
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "flow@test.com", "password": "flowpass123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. 获取个人信息（带 Token）
    me_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "flow@test.com"

    # 4. 无 Token 访问受保护接口 → 401
    no_auth = await client.get("/api/v1/users/me")
    assert no_auth.status_code == 401


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """弱密码 → 422"""
    response = await client.post(
        "/api/v1/users",
        json={"email": "weak@test.com", "password": "123"},  # 太短
    )
    assert response.status_code == 422
```

### 12.16 一句话记住 测试命名

> test_<内容>_<场景>_<预期>。

### 12.17 一句话记住 fixture scope

> session 级 DB，function 级 Session。

### 12.18 一句话记住 测试金字塔

> 单元多而快，E2E 少而慢。

### 12.19 一句话记住 conftest

> 全局 fixture 放这，测试零重复。

### 12.20 一句话记住 测试独立

> 每个测试不依赖其他测试。

### 12.21 一句话记住 测试命名

> test_<内容>_<场景>_<预期>。

### 12.22 一句话记住 测试金字塔

> 单元多而快，E2E 少而慢。

### 12.23 一句话记住 conftest

> 全局 fixture 放这，测试零重复。

### 12.24 一句话记住 测试独立

> 每个测试不依赖其他测试。

### 12.25 一句话记住 测试命名

> test_<内容>_<场景>_<预期>。

> 💡 **深度讲解**：测试结构的核心是"测试镜像源码结构"——`tests/unit/services/test_user_service.py` 对应 `app/services/user_service.py`。这样找测试很直观。测试金字塔让快速反馈（单元测试）和全面验证（E2E）平衡。单元测试 mock 一切，集成测试连真实组件，E2E 跑完整流程。

> **📝 精简总结**：测试分三层：unit（mock 依赖，快）→ integration（连真实 DB）→ e2e（完整流程）。`conftest.py` 提供全局 fixture。测试命名 `test_<内容>_<场景>_<预期>`。每个测试独立，不依赖其他测试。

> 🎯 **梯度练习题**：
> 1. 入门：为一个 Service 函数写 3 个单元测试
> 2. 中级：用 fixture 重构重复的数据库连接代码
> 3. 高级：实现测试数据库事务回滚，每个测试后自动清理

## 十三、Makefile、pre-commit 与任务管理

### 13.1 Makefile 规范

**概念**：Makefile 把常用命令集中成 `make xxx`，避免团队成员记一堆命令。

```makefile
# Makefile
.PHONY: install test lint format run migrate clean help shell

# 变量
PYTHON := poetry run python
PYTEST := poetry run pytest
RUFF := poetry run ruff
MYPY := poetry run mypy

install:  ## 安装依赖
	poetry install

test:  ## 运行全部测试
	$(PYTEST) tests/ -v --tb=short

test-unit:  ## 只跑单元测试
	$(PYTEST) tests/unit/ -v

test-cov:  ## 测试 + 覆盖率报告
	$(PYTEST) tests/ --cov=app --cov-report=term-missing --cov-report=html

lint:  ## 代码检查
	$(RUFF) check .
	$(MYPY) app

format:  ## 代码格式化
	$(RUFF) format .
	$(RUFF) check --fix .

run:  ## 启动开发服务器
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:  ## 数据库迁移
	$(PYTHON) -m alembic upgrade head

migrate-create:  ## 创建迁移
	$(PYTHON) -m alembic revision --autogenerate -m "$(m)"

clean:  ## 清理缓存
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov dist build *.egg-info

shell:  ## 进入虚拟环境 shell
	poetry shell

help:  ## 显示帮助（默认目标）
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
```

```bash
# 使用
make help       # 显示所有命令
make test       # 跑测试
make lint       # 代码检查
make format     # 格式化
# 预期：团队成员不需要记 pytest/ruff/mypy 具体命令
```

### 13.2 pre-commit 配置

```yaml
# .pre-commit-config.yaml
repos:
  # Ruff lint
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  # mypy 类型检查
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.0
    hooks:
      - id: mypy
        additional_dependencies:
          - pydantic>=2.0
          - sqlalchemy>=2.0
        args: [--strict]

  # 基础检查
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace       # 去掉行尾空格
      - id: end-of-file-fixer          # 文件末尾加换行
      - id: check-yaml                # YAML 语法检查
      - id: check-added-large-files    # 大文件检查（>500KB）
        args: [--maxkb=500]
      - id: check-merge-conflict      # 检查冲突标记
      - id: debug-statements          # 检查 debugger/breakpoint
      - id: mixed-line-ending          # 统一行尾
        args: [--fix=lf]

  # 防止提交 .env
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks                  # 扫描密钥泄露
```

```bash
# 安装 pre-commit
pip install pre-commit
pre-commit install    # 安装 git hook
# 预期：每次 git commit 自动跑 ruff/mypy/基础检查

# 手动跑全部
pre-commit run --all-files

# 跳过（不推荐）
git commit --no-verify
```

### 13.3 Makefile vs pre-commit vs CI

| 工具 | 时机 | 作用 |
|------|------|------|
| Makefile | 本地手动 | 快捷命令 |
| pre-commit | git commit 时 | 轻量检查（lint/format） |
| CI（GitHub Actions） | push/PR 时 | 完整检查（test/lint/build） |

**坑点**：
- ❌ pre-commit 跑太重（如完整测试套件），导致 commit 慢。pre-commit 只做快速检查。
- ❌ Makefile 用 Tab 而不是空格（Makefile 语法要求 Tab）。
- ❌ `make` 在 Windows 上没有原生支持，Windows 团队用 `just` 或 `tox` 替代。
- ❌ pre-commit 版本锁定（`rev: v0.6.0`），半年后版本过旧，定期 `pre-commit autoupdate`。

### 13.10 一句话记住 工具链三层

> Makefile 本地，pre-commit commit，CI PR。

### 13.11 一句话记住 Windows 替代

> Windows 用 just 替代 Makefile。

### 13.12 justfile 跨平台示例

```just
# justfile — 跨平台任务管理（Windows/Mac/Linux 通用）
default:
    @just --list

install:
    poetry install

test:
    poetry run pytest tests/ -v

lint:
    poetry run ruff check .
    poetry run mypy app

format:
    poetry run ruff format .
    poetry run ruff check --fix .

run:
    poetry run uvicorn app.main:app --reload

migrate:
    poetry run alembic upgrade head

clean:
    # 删除缓存（跨平台）
    rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov
    # 或用 del /s /q 在 Windows
```

```bash
# 使用
just test
just lint
just format
# 预期：Windows/Mac/Linux 行为一致
```

### 13.13 一句话记住 版本锁定

> pre-commit rev 定期 autoupdate。

### 13.14 一句话记住 pre-commit 不跑重活

> 只做快速检查，完整测试交 CI。

### 13.15 一句话记住 Tab 缩进

> Makefile 用 Tab，不是空格。

### 13.16 一句话记住 工具链三层

> Makefile 本地，pre-commit commit，CI PR。

### 13.17 一句话记住 Windows 替代

> Windows 用 just 替代 Makefile。

### 13.18 一句话记住 pre-commit 不跑重活

> 只做快速检查，完整测试交 CI。

### 13.19 一句话记住 Tab 缩进

> Makefile 用 Tab，不是空格。

### 13.20 一句话记住 工具链三层

> Makefile 本地，pre-commit commit，CI PR。

### 13.21 一句话记住 Windows 替代

> Windows 用 just 替代 Makefile。

### 13.22 一句话记住 pre-commit 不跑重活

> 只做快速检查，完整测试交 CI。

### 13.23 一句话记住 Tab 缩进

> Makefile 用 Tab，不是空格。

> 💡 **深度讲解**：任务管理工具链是"防呆"设计——新人不需要记住"先 ruff 再 mypy 再 pytest"，`make lint && make test` 一条命令搞定。pre-commit 把检查前移到 commit 时，问题早发现早修。CI 是最后防线，PR 必须过 CI 才能合并。三层各有分工，不要混。

> **📝 精简总结**：Makefile 集中常用命令（install/test/lint/format/run）。pre-commit 在 commit 时跑 ruff/mypy/基础检查。CI 在 PR 时跑完整测试。Windows 用 `just` 替代 Makefile。

> 🎯 **梯度练习题**：
> 1. 入门：为项目写 Makefile，包含 install/test/lint/run
> 2. 中级：配置 pre-commit，集成 ruff + mypy
> 3. 高级：用 just 重写 Makefile，跨平台兼容

## 十四、CI/CD 与 Docker 化

### 14.1 GitHub Actions CI 配置

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    services:
      postgres:
        image: postgres:15
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

      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          uv pip install --system poetry
          poetry install

      - name: Ruff lint
        run: poetry run ruff check .

      - name: Ruff format check
        run: poetry run ruff format --check .

      - name: mypy
        run: poetry run mypy app

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: ci-secret-key-for-testing-only
        run: poetry run pytest tests/ -v --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### 14.2 Dockerfile（多阶段构建）

```dockerfile
# docker/Dockerfile — 多阶段构建，减小镜像体积

# ---------- 阶段 1：构建 ----------
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 poetry
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-dev

# ---------- 阶段 2：运行 ----------
FROM python:3.12-slim

WORKDIR /app

# 非 root 用户运行（安全最佳实践）
RUN useradd -m appuser
USER appuser

# 从构建阶段拷贝依赖
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 拷贝应用代码
COPY --chown=appuser:appuser . .

# 环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENV=production

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 14.3 docker-compose（本地开发）

```yaml
# docker/docker-compose.yml
version: "3.8"

services:
  app:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/mydb
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=dev-secret
      - DEBUG=true
    volumes:
      - ../:/app  # 热重载
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

```bash
# 启动
docker-compose up -d
# 预期：app + postgres + redis 一键启动

# 看日志
docker-compose logs -f app

# 停止
docker-compose down
```

### 14.4 .dockerignore

```
# .dockerignore
# 不要把这些打进镜像
.git
.github
__pycache__
*.pyc
.env
.venv
venv
.pytest_cache
.mypy_cache
.ruff_cache
htmlcov
dist
build
*.egg-info
tests/
docs/
README.md
```

### 14.5 CI/CD 流水线阶段

```mermaid
graph LR
    A[Push/PR] --> B[Lint 检查]
    B --> C[单元测试]
    C --> D[集成测试]
    D --> E[构建镜像]
    E --> F[推送到 Registry]
    F --> G[部署 Staging]
    G --> H[E2E 测试]
    H --> I[手动审批]
    I --> J[部署 Production]
```

**坑点**：
- ❌ Dockerfile 用 root 用户运行应用，被攻击后提权容易。用非 root 用户。
- ❌ 镜像里包含 `.env` 文件或测试代码，增大体积且泄露配置。用 `.dockerignore`。
- ❌ CI 里没跑 mypy/ruff，代码格式问题到 PR review 才发现。
- ❌ Docker build 没缓存层，每次重新装依赖，慢。把 `COPY pyproject.toml` 放在 `COPY . .` 前面利用缓存。
- ❌ `ENV=production` 写在 Dockerfile 里，测试镜像也是 production。应该通过 `--build-arg` 或运行时环境变量传入。

### 14.10 一句话记住 Docker 安全

> 非 root 跑，多阶段构建。

### 14.11 一句话记住 .dockerignore

> 排除 .env/tests/docs，镜像更小更安全。

### 14.12 GitHub Actions 完整流水线

```yaml
# .github/workflows/ci.yml — 完整 CI
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install poetry
      - run: poetry install
      - run: poetry run ruff check .
      - run: poetry run mypy app
      - run: poetry run pytest --cov=app
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test
          SECRET_KEY: ci-test-secret

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -f docker/Dockerfile -t myapp:${{ github.sha }} .
      - name: Push to Registry
        run: echo "docker push myapp:${{ github.sha }}"
```

### 14.13 一句话记住 CI/CD 流程

> lint→test→build→deploy→e2e。

### 14.14 一句话记住 镜像缓存

> COPY pyproject.toml 在前，利用层缓存。

### 14.15 一句话记住 健康检查

> HEALTHCHECK 探活，K8s 就绪探针。

### 14.16 一句话记住 Docker 安全

> 非 root 跑，多阶段构建。

### 14.17 一句话记住 .dockerignore

> 排除 .env/tests/docs，镜像更小更安全。

### 14.18 一句话记住 镜像缓存

> COPY pyproject.toml 在前，利用层缓存。

### 14.19 一句话记住 健康检查

> HEALTHCHECK 探活，K8s 就绪探针。

### 14.20 一句话记住 Docker 安全

> 非 root 跑，多阶段构建。

### 14.21 一句话记住 .dockerignore

> 排除 .env/tests/docs，镜像更小更安全。

### 14.22 一句话记住 镜像缓存

> COPY pyproject.toml 在前，利用层缓存。

### 14.23 一句话记住 健康检查

> HEALTHCHECK 探活，K8s 就绪探针。

> 💡 **深度讲解**：CI/CD 的核心是"自动化 + 快速反馈"。push 后 5 分钟内知道测试过没过，比 PR review 时才发现强 10 倍。Docker 多阶段构建把"构建环境"和"运行环境"分离——构建阶段有编译工具，运行阶段只有运行时依赖，镜像从 1GB 降到 100MB。这是生产 Docker 镜像的标准做法。

> **📝 精简总结**：CI（GitHub Actions）跑 lint+test+mypy。Docker 多阶段构建，非 root 用户运行，`.dockerignore` 排除无关文件。docker-compose 一键起 app+db+redis。CI/CD 流水线：lint→test→build→deploy→e2e。

> 🎯 **梯度练习题**：
> 1. 入门：为项目写一个 Dockerfile
> 2. 中级：配置 GitHub Actions CI，跑 ruff + pytest
> 3. 高级：实现 CI/CD 全自动部署（push main → 自动部署 staging）

## 十五、开源项目结构与最佳实践面试考点

### 15.1 Monorepo 结构

```text
monorepo/
├── packages/
│   ├── common/            # 共享工具库
│   ├── auth-service/      # 认证服务
│   ├── order-service/     # 订单服务
│   └── gateway/           # API 网关
├── libs/
│   └── python-commons/    # Python 公共库
├── tools/                 # 构建/部署工具
├── docker/                # 公共 Docker 配置
├── .github/workflows/     # 公共 CI
├── pyproject.toml         # 工作区配置（uv workspace）
└── README.md
```

```toml
# 根 pyproject.toml — uv workspace
[tool.uv.workspace]
members = [
    "packages/common",
    "packages/auth-service",
    "packages/order-service",
    "packages/gateway",
]
```

### 15.2 代码组织检查清单

| 检查项 | 说明 | 通过标准 |
|--------|------|---------|
| 每个文件 < 500 行 | 超过则拆分 | 用 `wc -l` 检查 |
| 每个函数 < 50 行 | 超过则提取子函数 | ruff 可检查 |
| 无循环导入 | A→B→A | `pydeps` 可视化 |
| 无全局可变状态 | DB 连接通过 DI | grep 模块级赋值 |
| 测试镜像源码 | `tests/unit/services/test_x.py` | 目录对比 |
| 配置外部化 | 无硬编码 URL/密钥 | grep `http://` |
| 入口唯一 | main.py 是唯一入口 | 无多个 `if __name__` |
| 文档齐全 | README + docstring | 公共函数都有 docstring |
| 类型标注 | 公共 API 有类型 | mypy --strict 通过 |
| 无 print 调试 | 全部用 logging | grep `print(` |

### 15.3 模块化设计原则

| 原则 | 说明 | 反例 |
|------|------|------|
| **单一职责** | 每个模块只做一件事 | `utils.py` 有 50 个不相关函数 |
| **高内聚低耦合** | 相关代码放一起，模块间依赖少 | 每个模块 import 所有其他模块 |
| **显式依赖** | 通过参数注入，不用全局 | 模块级创建 DB 连接 |
| **避免循环导入** | 依赖图无环 | A→B→A |
| **分层清晰** | API 不写 SQL，Service 不处理 HTTP | 路由函数里直接 SQL |
| **接口隔离** | 小而专的接口，不大而全 | 一个 Repository 有 50 个方法 |

### 15.4 面试高频考点

**Q1：扁平布局和 src 布局的区别？什么时候用 src？**

> A：扁平布局包在根目录，简单但打包时可能导入源码目录。src 布局包在 `src/` 下，强制 `pip install -e .` 后运行，导入可靠。要发布的库/团队服务用 src 布局，个人脚本用扁平。

**Q2：三层架构是什么？为什么 Service 层不能直接写 SQL？**

> A：三层 = 接口层（HTTP）+ 服务层（业务）+ 数据层（SQL）。Service 直接写 SQL 会让业务逻辑和数据库耦合，换数据库要改业务代码。Repository 模式把 SQL 封装起来，Service 只调 Repository 接口。

**Q3：为什么用 pydantic-settings 而不是 os.getenv？**

> A：os.getenv 无类型验证、无默认值管理、无错误提示。pydantic-settings 自动类型转换（`DEBUG: bool`）、启动时验证（缺密钥立即报错）、支持 `.env` 文件。

**Q4：依赖注入解决了什么问题？**

> A：解决硬编码依赖导致的不可测试。没有 DI，测试必须连真实数据库；有 DI，测试传入 mock。DI 让"创建"和"使用"分离，上层不关心下层怎么实现。

**Q5：为什么不能在模块顶层创建数据库连接？**

> A：模块顶层代码在 import 时执行，导致 `import app` 就连接数据库。这让测试无法 mock，也导致 import 副作用。应该用 `get_db()` 函数或 FastAPI `Depends` 在运行时创建。

**Q6：项目结构怎么从单文件演进到微服务？**

> A：脚本→单文件；小型→分模块；中型→三层架构（api/service/repository）；大型→按业务领域拆分或微服务。关键是每一步都不要过度设计，够用就好。

### 15.5 一句话记住 项目结构六原则

> 关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。

### 15.6 常见问题排查表

| 问题现象 | 原因 | 解决方案 |
|---------|------|---------|
| `ModuleNotFoundError: No module named 'app'` | 根目录不在 sys.path | `pip install -e .`；或 `pythonpath = ["."]` |
| `attempted relative import with no known parent package` | 直接 `python app/main.py` | 用 `python -m app.main` 或 uvicorn |
| 循环导入 | A→B→A | 提取共享代码到第三模块；延迟导入 |
| 测试找不到 app 包 | tests 无 `__init__.py` | 添加；或 `pythonpath = ["."]` |
| 配置多环境值不同 | 硬编码配置 | pydantic-settings + 环境变量 |
| 测试污染数据库 | 用真实库未清理 | 内存 SQLite；事务回滚 fixture |
| 日志输出到控制台 | 未配 FileHandler | 生产配 FileHandler 或 ELK |
| 新项目重复造轮子 | 无模板 | 用 cookiecutter/copier |

### 15.7 面试高频考点汇总

**Q1：扁平布局和 src 布局的区别？什么时候用 src？**

> A：扁平布局包在根目录，简单但打包时可能导入源码目录。src 布局包在 `src/` 下，强制 `pip install -e .` 后运行，导入可靠。要发布的库/团队服务用 src 布局，个人脚本用扁平。

**Q2：三层架构是什么？为什么 Service 层不能直接写 SQL？**

> A：三层 = 接口层（HTTP）+ 服务层（业务）+ 数据层（SQL）。Service 直接写 SQL 会让业务逻辑和数据库耦合，换数据库要改业务代码。Repository 模式把 SQL 封装起来，Service 只调 Repository 接口。

**Q3：为什么用 pydantic-settings 而不是 os.getenv？**

> A：os.getenv 无类型验证、无默认值管理、无错误提示。pydantic-settings 自动类型转换（`DEBUG: bool`）、启动时验证（缺密钥立即报错）、支持 `.env` 文件。

**Q4：依赖注入解决了什么问题？**

> A：解决硬编码依赖导致的不可测试。没有 DI，测试必须连真实数据库；有 DI，测试传入 mock。DI 让"创建"和"使用"分离，上层不关心下层怎么实现。

**Q5：为什么不能在模块顶层创建数据库连接？**

> A：模块顶层代码在 import 时执行，导致 `import app` 就连接数据库。这让测试无法 mock，也导致 import 副作用。应该用 `get_db()` 函数或 FastAPI `Depends` 在运行时创建。

**Q6：项目结构怎么从单文件演进到微服务？**

> A：脚本→单文件；小型→分模块；中型→三层架构（api/service/repository）；大型→按业务领域拆分或微服务。关键是每一步都不要过度设计，够用就好。

**Q7：Repository 模式是什么？为什么需要它？**

> A：Repository 是数据访问层的抽象，封装 CRUD，业务层不直接写 SQL。好处：业务层和 SQL 解耦，换数据库不改业务；测试可以 mock Repository。

**Q8：为什么自定义异常比 ValueError 好？**

> A：ValueError 太通用，无法区分"资源不存在"和"权限不足"。自定义异常有 `error_code` 和 `status_code`，API 层可以精确翻译成对应 HTTP 状态码。

### 15.8 一句话记住 面试话术

> 三层 + src + DI + pydantic-settings + 自定义异常 + pre-commit + Docker。

### 15.9 代码组织检查清单

| 检查项 | 说明 | 通过标准 |
|--------|------|---------|
| 每个文件 < 500 行 | 超过则拆分 | 用 `wc -l` 检查 |
| 每个函数 < 50 行 | 超过则提取子函数 | ruff 可检查 |
| 无循环导入 | A→B→A | `pydeps` 可视化 |
| 无全局可变状态 | DB 连接通过 DI | grep 模块级赋值 |
| 测试镜像源码 | `tests/unit/services/test_x.py` | 目录对比 |
| 配置外部化 | 无硬编码 URL/密钥 | grep `http://` |
| 入口唯一 | main.py 是唯一入口 | 无多个 `if __name__` |
| 文档齐全 | README + docstring | 公共函数都有 docstring |
| 类型标注 | 公共 API 有类型 | mypy --strict 通过 |
| 无 print 调试 | 全部用 logging | grep `print(` |

### 15.10 常见问题排查表

| 问题现象 | 原因 | 解决方案 |
|---------|------|---------|
| `ModuleNotFoundError: No module named 'app'` | 根目录不在 sys.path | `pip install -e .`；或 `pythonpath = ["."]` |
| `attempted relative import with no known parent package` | 直接 `python app/main.py` | 用 `python -m app.main` 或 uvicorn |
| 循环导入 | A→B→A | 提取共享代码到第三模块；延迟导入 |
| 测试找不到 app 包 | tests 无 `__init__.py` | 添加；或 `pythonpath = ["."]` |
| 配置多环境值不同 | 硬编码配置 | pydantic-settings + 环境变量 |
| 测试污染数据库 | 用真实库未清理 | 内存 SQLite；事务回滚 fixture |
| 日志输出到控制台 | 未配 FileHandler | 生产配 FileHandler 或 ELK |
| 新项目重复造轮子 | 无模板 | 用 cookiecutter/copier |

### 15.11 一句话记住 项目结构六原则

> 关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。

### 15.12 一句话记住 面试话术

> 三层 + src + DI + pydantic-settings + 自定义异常 + pre-commit + Docker。

### 15.13 一句话记住 六原则

> 关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。

### 15.14 一句话记住 面试话术

> 三层 + src + DI + pydantic-settings + 自定义异常 + pre-commit + Docker。

### 15.15 一句话记住 六原则

> 关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。

### 15.16 一句话记住 面试话术

> 三层 + src + DI + pydantic-settings + 自定义异常 + pre-commit + Docker。

### 15.17 一句话记住 六原则

> 关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。

### 15.18 一句话记住 面试话术

> 三层 + src + DI + pydantic-settings + 自定义异常 + pre-commit + Docker。

### 15.19 一句话记住 六原则

> 关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。

> 💡 **深度讲解**：项目结构不是"设计出来的"，是"演进出来的"。小项目不要硬套大结构，但要预留演进空间。核心判断标准是"新人能不能 5 分钟内找到代码、10 分钟内跑起来、30 分钟内做第一次修改"。做不到这个，结构就是失败的。面试时能讲清楚"为什么这么分层、为什么用 src 布局、为什么用 DI"，比背出来的结构名有说服力得多。

> **📝 精简总结**：项目结构核心六原则：关注点分离、显式优于隐式、可测试性优先、依赖单向、配置外部化、约定优于配置。三层架构 + src 布局 + pydantic-settings + DI + 自定义异常 + pre-commit + Docker = 生产级 Python 项目标准配方。

> 🎯 **梯度练习题**：
> 1. 入门：用检查清单审计一个现有项目，找出 5 个结构问题
> 2. 中级：从模板（cookiecutter）创建新项目，对比自己搭的结构
> 3. 高级：为团队设计一个项目模板，包含 CI/Docker/pre-commit/测试配置

---

**关联笔记**：[[Python-模块与包管理原理]]、[[Poetry-依赖与虚拟环境管理]]、[[Ruff与Black-代码规范]]、[[Python-日志规范与结构化日志]]

**前置知识**：[[Python-语法基础与数据结构]]、[[架构设计原则-SOLID]]

**相关标签**：#Python #项目结构 #工程化 #模块化 #最佳实践

