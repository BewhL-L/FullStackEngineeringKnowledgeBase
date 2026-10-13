---
title: Poetry 依赖与虚拟环境管理
category: 测试与工程化
tags: [Python, Poetry, 依赖管理, 虚拟环境, 包管理, pyproject.toml]
priority: P1
status: completed
created: 2026-09-10
updated: 2026-09-10
version: 2.0
author: BewhY_L
pre: ["[[Python-模块与包管理原理]]", "[[Python-项目结构最佳实践]]"]
description: 系统讲解 Poetry 依赖管理与虚拟环境工具的完整用法，涵盖 pyproject.toml、依赖分组、锁文件机制、构建发布、Docker/CI 集成
---

# Poetry 依赖与虚拟环境管理

> **文档定位**：本文档是 Python 依赖管理工具 Poetry 的完整实战指南，覆盖从安装初始化到 pyproject.toml 配置、依赖管理、虚拟环境、依赖分组、构建发布、Docker/CI 集成、私有仓库配置的全部核心场景。
>
> **适用人群**：Python 开发者、需要管理项目依赖的全栈工程师、从 pip/venv 迁移到 Poetry 的团队
>
> **前置知识**：[[Python-模块与包管理原理]]、[[Python-项目结构最佳实践]]、基础命令行操作

---

## 一、Python 依赖管理痛点与 Poetry 概述

### 1.1 传统依赖管理的痛点

在 Python 生态中，依赖管理长期是一个令人头疼的问题。传统方式 `pip + requirements.txt + venv` 存在多个结构性缺陷：

```mermaid
graph LR
    subgraph 传统痛点
        A[pip freeze<br/>包含所有依赖] --> B[无法区分直接/间接依赖]
        B --> C[版本冲突<br/>A要requests>=2.0<br/>B要requests<2.0]
        C --> D[无锁文件<br/>pip install 结果不确定]
        D --> E["在我机器上能跑<br/>IWorksOnMyMachine"]
    end
```

| 痛点 | 传统方式的问题 | 实际影响 |
|------|---------------|---------|
| **直接/间接依赖混淆** | `pip freeze > requirements.txt` 冻结所有包 | 无法知道哪些是直接依赖，更新时不敢删 |
| **版本冲突** | pip 不做依赖解析 | 安装时随机选版本，可能冲突 |
| **无锁文件** | requirements.txt 不包含传递依赖 | 每次 install 结果可能不同 |
| **开发/生产依赖混合** | requirements-dev.txt 手动维护 | 容易把开发工具部署到生产 |
| **虚拟环境手动管理** | 手动 `python -m venv` + activate | 每个项目不同的激活方式，容易混乱 |
| **打包发布繁琐** | setup.py + MANIFEST.in + twine | 配置复杂，容易出错 |
| **元数据分散** | setup.py, requirements.txt, README | 项目信息散落在多个文件 |

### 1.2 Poetry 是什么

**Poetry** 是 Python 的依赖管理和打包工具，它将以下工具的功能统一到一个命令中：

- `pip` — 包安装
- `venv` / `virtualenv` — 虚拟环境
- `setup.py` / `setuptools` — 包构建
- `requirements.txt` — 依赖声明
- `twine` — PyPI 发布

**生活化比喻**：如果 pip 像是去杂货店自己买菜（每个工具单独买，自己配比例），Poetry 就像一个专业厨师——你告诉他要做什么菜（声明直接依赖），他自动去市场选最好的食材（解析传递依赖），并记住完整的菜谱（lock 文件），确保每次做出来的味道一样。

### 1.3 Poetry 核心架构

```mermaid
graph TB
    subgraph 输入
        A[pyproject.toml<br/>声明直接依赖]
    end

    subgraph Poetry 核心
        B[依赖解析器<br/>PubGrub算法求解]
        C[虚拟环境管理<br/>venv 创建/激活]
        D[锁文件生成<br/>poetry.lock]
        E[构建系统<br/>wheel/sdist]
        F[发布系统<br/>PyPI upload]
    end

    subgraph 输出
        G[poetry.lock<br/>锁定所有依赖版本+哈希]
        H[.venv/<br/>项目虚拟环境]
        I[dist/*.whl<br/>分发包]
        J[PyPI<br/>公开仓库]
    end

    A --> B
    B --> D
    D --> G
    B --> C
    C --> H
    A --> E
    E --> I
    I --> F
    F --> J
```

### 1.4 核心概念速览

| 概念 | 说明 | 类比 |
|------|------|------|
| `pyproject.toml` | 项目配置文件（PEP 621），声明依赖和元数据 | 项目的"身份证" |
| `poetry.lock` | 锁文件，记录所有依赖的精确版本和哈希 | 完整的"购物清单" |
| 依赖解析器 | 自动求解所有直接和传递依赖的兼容版本 | 自动配菜单的厨师 |
| 虚拟环境隔离 | 每个项目独立的 Python 环境 | 每个项目独立的厨房 |
| 依赖组 | 分组管理依赖（dev/prod/test/docs） | 食材分类存放 |
| 版本约束 | `^` `~` `>=` 等符号声明版本范围 | 食材的"新鲜度要求" |

> ✅ 最佳实践：`poetry.lock` 必须提交到 Git（应用项目），但库项目（开源包）通常不提交 lock 文件。这是应用和库的关键区别——应用追求可复现，库追求兼容性。

### 1.5 与其他工具的核心差异

```python
# 传统方式（多个工具配合）
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install fastapi uvicorn

# 3. 冻结依赖
pip freeze > requirements.txt

# 4. 打包发布
python setup.py bdist_wheel
twine upload dist/*

# Poetry 方式（一个工具搞定）
# 1. 初始化项目
poetry new my-project

# 2. 添加依赖
poetry add fastapi uvicorn

# 3. 构建发布
poetry build
poetry publish
```

### 1.6 适合使用 Poetry 的场景

```python
# 适合 Poetry 的场景：
# 1. Web API 项目（FastAPI/Django/Flask）
# 2. CLI 工具开发
# 3. 开源库发布到 PyPI
# 4. 团队协作的中大型项目
# 5. 需要打包发布的项目

# 不太需要 Poetry 的场景：
# 1. 一次性脚本（直接 pip install 即可）
# 2. 数据科学项目（用 conda 更合适）
# 3. Jupyter Notebook 环境
# 4. 极简项目（只依赖标准库）
```

### 1.7 Poetry 的局限性

```python
# Poetry 的局限性：
# 1. 不支持非 Python 依赖（需要 conda）
# 2. 依赖解析有时较慢（复杂依赖图）
# 3. 学习曲线（需要理解版本约束语法）
# 4. 比 pip 重（多了虚拟环境管理等功能）
# 5. Windows 上偶尔有路径问题
```

---

> 💡 **本章深度讲解**：理解 Poetry 之前，先理解它要解决的问题。Python 依赖管理的痛点本质上是"声明依赖"和"锁定版本"之间的鸿沟。Poetry 通过统一的 `pyproject.toml` + `poetry.lock` 架构，将声明和锁定分离——pyproject.toml 声明"我需要什么"，poetry.lock 锁定"我实际用了什么"。这个分离使得团队协作、CI 构建和生产部署都能获得一致的环境。
>
> **📝 精简总结**：
> - 核心概念：pyproject.toml、poetry.lock、依赖解析器、虚拟环境
> - 关键原理：声明依赖与锁定版本分离；PubGrub 算法求解版本冲突
> - 常用操作：`poetry new`；`poetry add`；`poetry install`
> - 最佳实践：lock 文件提交 Git；区分应用和库项目
> - 常见坑点：pip freeze 包含间接依赖；无锁文件导致不可复现
> - 面试高频：pyproject.toml vs requirements.txt；lock 文件的作用

### 🎯 梯度练习题

**基础题（⭐）**
1. Poetry 统一了哪些传统工具的功能？
   - 答案：pip + venv + setup.py + requirements.txt + twine。
2. `poetry.lock` 应该提交到 Git 吗？
   - 答案：应用项目应该提交；库项目通常不提交。

**进阶题（⭐⭐）**
1. 为什么 `pip freeze > requirements.txt` 不是好的依赖管理方式？
   - 思考方向：包含间接依赖；无法区分直接依赖；无版本约束语义。
2. pyproject.toml 和 poetry.lock 的职责分别是什么？
   - 思考方向：前者声明直接依赖（我需要什么），后者锁定所有依赖版本（我实际用了什么）。

**实战题（⭐⭐⭐）**
- **背景**：团队有一个老项目用 `pip install` + `requirements.txt`。
- **需求**：迁移到 Poetry。
- **要求**：① 初始化 pyproject.toml；② 从 requirements.txt 导入依赖；③ 生成 lock 文件；④ 验证项目能正常运行。
- **验收标准**：`poetry install` 成功；`poetry run python main.py` 正常。
- **提示**：用 `poetry init` 交互式初始化，然后逐行 `poetry add`。

---

## 二、Poetry 安装与项目初始化

### 2.1 安装 Poetry

```bash
# 官方推荐方式：安装脚本（自动隔离 Poetry 自身）
curl -sSL https://install.python-poetry.org | python3 -

# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# 验证安装
poetry --version
# 预期输出：Poetry (version 1.8.0)

# 使用 pip 安装（不推荐，可能污染全局环境）
pip install poetry
```

### 2.2 配置 Poetry

```bash
# 查看当前所有配置
poetry config --list

# 推荐配置：在项目目录内创建 .venv
poetry config virtualenvs.in-project true
# 这样 .venv 会在项目目录中，IDE 可以自动识别

# 配置缓存目录
poetry config cache-dir ~/.cache/pypoetry

# 配置并行安装数
poetry config installer.max-workers 10

# 查看单个配置
poetry config virtualenvs.in-project
```

```bash
# 配置国内镜像源（加速下载）
poetry source add --priority=primary tsinghua https://pypi.tuna.tsinghua.edu.cn/simple

# 查看已配置的源
poetry source list

# 移除源
poetry source remove tsinghua
```

### 2.3 创建新项目

```bash
# 创建新项目（标准结构）
poetry new my-project

# 项目结构：
# my-project/
# ├── pyproject.toml       # 项目配置
# ├── README.md
# ├── my_project/          # 源代码包
# │   ├── __init__.py
# │   └── main.py
# └── tests/
#     ├── __init__.py
#     └── test_my_project.py
```

```bash
# 在现有目录中初始化
cd existing-project
poetry init
# 交互式提问：项目名、版本、依赖等
# 生成 pyproject.toml
```

### 2.4 项目结构详解

```bash
my-project/
├── pyproject.toml       # 核心配置：依赖、元数据、构建系统
├── poetry.lock          # 锁文件（提交 Git）
├── README.md
├── .venv/               # 虚拟环境（不提交 Git）
├── .gitignore           # 忽略 .venv/ 和 __pycache__/
├── my_project/          # 源代码包
│   ├── __init__.py
│   ├── main.py
│   └── utils/
└── tests/                # 测试
    ├── __init__.py
    ├── conftest.py
    └── test_main.py
```

```gitignore
# .gitignore
.venv/
__pycache__/
*.pyc
*.pyo
dist/
build/
*.egg-info/
.pytest_cache/
.mypy_cache/
htmlcov/
.coverage
```

### 2.5 第一个 Poetry 项目

```bash
# 1. 创建项目
poetry new my-cli-tool
cd my-cli-tool

# 2. 添加依赖
poetry add requests
poetry add click

# 3. 添加开发依赖
poetry add --group dev pytest pytest-cov ruff mypy

# 4. 安装所有依赖（生成 .venv 和 poetry.lock）
poetry install

# 5. 运行项目
poetry run python my_cli_tool/main.py

# 6. 激活虚拟环境
poetry shell
# 现在你在虚拟环境的 shell 中
# 输入 exit 退出
```

### 2.6 Poetry 自动补全

```bash
# Bash 补全
poetry completions bash >> ~/.bash_completion.d/poetry.bash-completion

# Zsh 补全
poetry completions zsh > ~/.zsh/completion/_poetry

# Fish 补全
poetry completions fish > ~/.config/fish/completions/poetry.fish
```

> ❌ 常见坑点：安装 Poetry 后如果 `poetry` 命令找不到，需要将 Poetry 的 bin 目录添加到 PATH。默认安装位置是 `~/.local/bin`（Linux/Mac）或 `%APPDATA%\Python\Scripts`（Windows）。安装脚本末尾会提示你添加 PATH 的命令。

---

> 💡 **本章深度讲解**：Poetry 的安装和初始化是建立项目工程化的第一步。`virtualenvs.in-project true` 是最重要的配置——它让虚拟环境就在项目目录中，IDE 自动识别，删除项目时自动清理。`poetry new` 生成的标准结构是所有 Python 项目的良好起点。掌握这些基础操作后，后续的依赖管理和构建发布都是在这个基础上展开。
>
> **📝 精简总结**：
> - 核心概念：pyproject.toml、.venv、poetry.lock、virtualenvs.in-project
> - 关键原理：官方安装器隔离 Poetry 自身；项目级 .venv 便于 IDE 识别
> - 常用操作：`poetry new`；`poetry init`；`poetry install`；`poetry shell`
> - 最佳实践：设置 virtualenvs.in-project true；配置国内镜像源
> - 常见坑点：poetry 命令找不到（PATH 未配置）；.venv 未在项目内
> - 面试高频：poetry new vs poetry init；为什么 lock 文件要提交

### 🎯 梯度练习题

**基础题（⭐）**
1. `poetry new` 和 `poetry init` 的区别是什么？
   - 答案：new 创建新项目目录；init 在现有目录中初始化。
2. 为什么推荐 `virtualenvs.in-project true`？
   - 答案：.venv 在项目目录中，IDE 自动识别，删除项目时自动清理。

**进阶题（⭐⭐）**
1. 为什么官方推荐用安装脚本而非 pip install poetry？
   - 思考方向：隔离 Poetry 自身的依赖；避免与项目依赖冲突；自动管理升级。
2. 如何配置国内镜像源加速下载？
   - 思考方向：`poetry source add --priority=primary 源名 URL`。

**实战题（⭐⭐⭐）**
- **背景**：你要为一个新的 Python CLI 工具项目搭建工程化环境。
- **需求**：从零开始初始化 Poetry 项目。
- **要求**：① 创建项目；② 配置 .venv 在项目内；③ 添加 click 作为生产依赖；④ 添加 pytest 作为开发依赖；⑤ 配置国内镜像源。
- **验收标准**：`poetry install` 成功；`poetry show` 显示依赖树。
- **提示**：注意区分 `poetry add` 和 `poetry add --group dev`。

---

## 三、pyproject.toml 详解

### 3.1 pyproject.toml 结构总览

`pyproject.toml` 是 PEP 621 定义的 Python 项目标准配置文件，Poetry 使用它管理项目元数据和依赖：

```toml
# pyproject.toml 完整结构示例

# 项目元数据
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "一个示例项目"
authors = ["Your Name <you@example.com>"]
readme = "README.md"
license = "MIT"
homepage = "https://github.com/yourname/my-project"
repository = "https://github.com/yourname/my-project.git"
documentation = "https://my-project.readthedocs.io"
keywords = ["example", "demo"]
packages = [{ include = "my_project" }]

# 生产依赖
[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.100.0"
uvicorn = { version = "^0.23", extras = ["standard"] }
sqlalchemy = { version = "^2.0", extras = ["asyncio"] }
pydantic = "^2.0"

# 开发依赖组
[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
pytest-asyncio = "^0.21"
pytest-cov = "^4.1"
ruff = "^0.1"
mypy = "^1.5"

# 文档依赖组
[tool.poetry.group.docs.dependencies]
mkdocs = "^1.5"
mkdocs-material = "^9.2"

# 脚本入口
[tool.poetry.scripts]
start = "my_project.main:main"
test = "my_project.scripts:run_tests"

# 构建系统
[build-system]
requires = ["poetry-core>=1.6.0"]
build-backend = "poetry.core.masonry.api"
```

### 3.2 项目元数据详解

```toml
[tool.poetry]
# 名称：小写字母+数字+连字符
name = "my-awesome-project"

# 版本：语义化版本（SemVer）
version = "1.2.3"

# 描述：一句话描述项目
description = "一个示例项目"

# 作者列表
authors = [
    "Alice <alice@example.com>",
    "Bob <bob@example.com>",
]

# 许可证：SPDX 标识符
license = "MIT"

# README 文件
readme = "README.md"

# 包发现：指定哪些目录作为包
packages = [
    { include = "my_project" },
    { include = "my_project_extra" },
]

# 默认 Poetry 会自动发现与项目名同名的包（下划线替代连字符）
# 对于 my-project，自动发现 my_project/
```

### 3.3 依赖声明语法

```toml
[tool.poetry.dependencies]
# 基本形式：包名 = "版本约束"
requests = "^2.31.0"

# 完整形式：字典语法，支持 extras 和 markers
sqlalchemy = { version = "^2.0", extras = ["asyncio"] }

# Python 版本约束（必须声明）
python = "^3.10"

# 可选依赖
redis = { version = "^5.0", optional = true }

# 平台特定依赖
psycopg2-binary = { version = "^2.9", markers = "sys_platform != 'win32'" }

# Git 依赖
django = { git = "https://github.com/django/django.git", rev = "stable/5.0.x" }

# 路径依赖（本地开发）
my-utils = { path = "../my-utils", develop = true }

# URL 依赖
private-lib = { url = "https://example.com/private-lib-1.0.0.tar.gz" }
```

### 3.4 版本约束语法详解

| 约束 | 含义 | 示例 | 匹配范围 |
|------|------|------|---------|
| `^1.2.3` | 兼容更新（不改变最左非零位） | `^1.2.3` | `>=1.2.3, <2.0.0` |
| `^0.2.3` | 0.x 版本特殊处理 | `^0.2.3` | `>=0.2.3, <0.3.0` |
| `~1.2.3` | 小版本锁定 | `~1.2.3` | `>=1.2.3, <1.3.0` |
| `>=1.2.3` | 大于等于 | `>=1.2.3` | `1.2.3` 及以上 |
| `>=1.2 <2.0` | 范围 | - | `1.2` 到 `2.0` 之间 |
| `==1.2.3` | 精确版本 | `==1.2.3` | 仅 `1.2.3` |
| `~=1.2` | 兼容发布 | `~=1.2` | `>=1.2, <2.0` |
| `*` | 任意版本 | `*` | 所有版本 |

```toml
# 版本约束实战示例
requests = "^2.31.0"      # 接受 2.31.x 到 2.999.x，不接受 3.0
django = "^5.0"           # 接受 5.x，不接受 6.0
flask = "~3.0"            # 接受 3.0.x，不接受 3.1
pytest = "^7.4"           # 接受 7.4.x 到 7.999.x
numpy = ">=1.24,<2.0"    # 明确范围
```

> 🎯 面试高频：`^` 和 `~` 版本约束的区别？——`^` 允许次版本和补丁版本更新（不改变最左非零位），`~` 只允许补丁版本更新（不改变次版本）。例如 `^1.2.3` 允许 `1.3.0`，但 `~1.2.3` 不允许。生产依赖推荐用 `^`，库依赖推荐用 `~` 或更严格。

### 3.5 scripts 命令定义

```toml
[tool.poetry.scripts]
# 命令名 = "模块路径:函数名"
start = "my_project.main:main"
dev = "my_project.scripts:run_dev"
lint = "my_project.scripts:lint"
test = "my_project.scripts:run_tests"
```

```python
# my_project/scripts.py
def run_dev():
    import subprocess
    subprocess.run(["uvicorn", "my_project.main:app", "--reload"])

def lint():
    import subprocess
    subprocess.run(["ruff", "check", "."])

def run_tests():
    import subprocess
    subprocess.run(["pytest", "-v"])
```

```bash
# 运行定义的脚本
poetry run start
poetry run lint
poetry run test
```

### 3.6 完整 pyproject.toml 实战模板

```toml
# pyproject.toml - 生产级 FastAPI 项目完整配置示例

[tool.poetry]
name = "user-api"
version = "1.2.0"
description = "用户管理 API 服务"
authors = ["Dev Team <dev@company.com>"]
readme = "README.md"
license = "Proprietary"
homepage = "https://git.company.com/api/user-api"
repository = "https://git.company.com/api/user-api.git"
keywords = ["api", "user", "fastapi"]

[tool.poetry.dependencies]
python = "^3.12"
fastapi = { version = "^0.104.0", extras = ["standard"] }
uvicorn = { version = "^0.24.0", extras = ["standard"] }
sqlalchemy = { version = "^2.0.23", extras = ["asyncio"] }
asyncpg = "^0.29.0"
pydantic = { version = "^2.5.2", extras = ["email"] }
alembic = "^1.12.1"
redis = { version = "^5.0.1", optional = true }
python-jose = { version = "^3.3.0", extras = ["cryptography"] }
passlib = { version = "^1.7.4", extras = ["bcrypt"] }

[tool.poetry.extras]
redis = ["redis>=5.0.0"]

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
pytest-mock = "^3.12.0"
httpx = "^0.25.2"
ruff = "^0.1.6"
mypy = "^1.7.1"
pre-commit = "^3.6.0"
ipython = "^8.18.1"
pip-audit = "^2.7.3"

[tool.poetry.group.docs.dependencies]
mkdocs = "^1.5.3"
mkdocs-material = "^9.5.3"

[tool.poetry.scripts]
start = "user_api.main:main"
dev = "user_api.scripts:run_dev"
test = "user_api.scripts:run_tests"
lint = "user_api.scripts:run_lint"

# 工具配置（统一在 pyproject.toml）
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --tb=short"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true

[tool.coverage.run]
source = ["user_api"]
branch = true

[build-system]
requires = ["poetry-core>=1.7.0"]
build-backend = "poetry.core.masonry.api"
```

### 3.7 包发现与自定义包路径

```toml
# 默认：Poetry 自动发现与项目名同名的包（连字符转下划线）
# my-project -> my_project/

# 自定义包路径
[tool.poetry]
packages = [
    { include = "my_project" },          # 单个包
    { include = "my_package_*" },        # 通配符
    { include = "libs/utils" },          # 子目录
]

# 如果你的包不在标准位置
packages = [{ include = "src/my_project" }]
```

```bash
# 验证包发现是否正确
poetry build
# 查看 dist/ 中的 wheel 是否包含正确的包
python -m zipfile -l dist/*.whl
```

---

> 💡 **本章深度讲解**：pyproject.toml 是 Poetry 的核心——它统一了项目元数据、依赖声明、构建配置和工具配置。理解版本约束符号（`^` `~` `>=`）是依赖管理的基础：太严格会错过安全补丁，太宽松可能引入不兼容变更。scripts 定义让项目有标准的入口命令。这个文件就是项目的"操作系统"——所有工具都读取它。
>
> **📝 精简总结**：
> - 核心概念：pyproject.toml、版本约束、extras、scripts
> - 关键原理：^ 锁定最左非零位；~ 锁定次版本；extras 可选依赖
> - 常用操作：`poetry add pkg`；`[tool.poetry.scripts]`
> - 最佳实践：用 ^ 约束生产依赖；scripts 定义常用命令
> - 常见坑点：0.x 版本的 ^ 行为不同；忘记声明 python 版本
> - 面试高频：^ vs ~ 版本约束；extras 的作用

### 🎯 梯度练习题

**基础题（⭐）**
1. `^1.2.3` 和 `~1.2.3` 分别匹配什么版本范围？
   - 答案：`^1.2.3` → `>=1.2.3, <2.0.0`；`~1.2.3` → `>=1.2.3, <1.3.0`。
2. pyproject.toml 中 `python = "^3.10"` 是什么意思？
   - 答案：需要 Python 3.10 到 4.0 之间的版本。

**进阶题（⭐⭐）**
1. 为什么 `^0.2.3` 的行为和 `^1.2.3` 不同？
   - 思考方向：0.x 版本 API 不稳定；Poetry 将 0.x 的 ^ 锁定到次版本。
2. `extras` 的作用是什么？
   - 思考方向：可选功能依赖；`sqlalchemy[asyncio]` 按需安装。

**实战题（⭐⭐⭐）**
- **背景**：你要创建一个 FastAPI 项目的 pyproject.toml。
- **需求**：配置完整的项目。
- **要求**：① 生产依赖：fastapi、uvicorn、sqlalchemy[asyncio]；② 开发依赖：pytest、ruff、mypy；③ 脚本：start 和 test；④ Python 版本 >=3.10。
- **验收标准**：`poetry install` 成功；`poetry run start` 可运行。
- **提示**：注意 `extras` 的字典语法。

---

## 四、依赖管理：添加、更新、删除与锁定

### 4.1 添加依赖

```bash
# 添加生产依赖（默认加入 [tool.poetry.dependencies]）
poetry add requests
poetry add "fastapi>=0.100.0"
poetry add "django@^5.0"

# 带 extras 的依赖
poetry add "sqlalchemy[asyncio]"

# 添加开发依赖
poetry add --group dev pytest pytest-cov ruff

# 添加测试依赖（单独的 group）
poetry add --group test pytest-asyncio

# 添加可选依赖
poetry add --optional redis

# 从特定源安装
poetry add --source my-private-repo private-package

# 从 Git 安装
poetry add git+https://github.com/django/django.git#stable/5.0.x

# 从本地路径安装
poetry add ./local-package
```

### 4.2 查看依赖

```bash
# 列出所有已安装依赖
poetry show

# 依赖树（查看依赖的依赖）
poetry show --tree

# 输出示例：
# fastapi 0.100.0 FastAPI framework
# ├── pydantic 2.0.0 Data validation
# └── starlette 0.27.0 ASGI framework
#
# uvicorn 0.23.0 Lightning server
# └── click 8.1.0 Composable CLI

# 查看单个包的详细信息
poetry show fastapi

# 查看可更新的包
poetry show --outdated

# 输出示例：
# fastapi (0.100.0)
#   latest: 0.104.0
#   status: outdated
```

### 4.3 更新依赖

```bash
# 更新所有依赖到最新兼容版本（更新 lock 文件）
poetry update

# 更新指定依赖
poetry update fastapi

# 更新多个依赖
poetry update fastapi uvicorn

# 预览更新（不实际执行）
poetry update --dry-run

# 只更新 lock 文件，不安装
poetry lock --no-update
```

> ❌ 常见坑点：`poetry update` 和 `poetry install` 的区别——`install` 读取 lock 文件安装精确版本；`update` 重新解析依赖并更新 lock 文件。日常开发用 `install`，定期升级用 `update`。不要在 CI 中用 `poetry update`，因为它可能引入新版本导致意外失败。

### 4.4 移除依赖

```bash
# 移除生产依赖
poetry remove requests

# 移除开发依赖
poetry remove --group dev pytest

# 移除后自动更新 pyproject.toml 和 lock 文件
```

### 4.5 导出 requirements.txt

```bash
# 导出为 requirements.txt（兼容旧工具）
poetry export -f requirements.txt -o requirements.txt

# 只导出生产依赖
poetry export -f requirements.txt --without dev -o requirements-prod.txt

# 导出时包含哈希（可复现）
poetry export -f requirements.txt --without-hashes -o requirements.txt

# 导出到标准输出
poetry export -f requirements.txt
```

### 4.6 锁文件机制

`poetry.lock` 记录了所有依赖（包括传递依赖）的精确版本和哈希值：

```toml
# poetry.lock 片段示例
[[package]]
name = "fastapi"
version = "0.100.0"
description = "FastAPI framework"
optional = false
python-versions = ">=3.7"

[[package.dependencies]]
name = "pydantic"
version = "2.0.0"

[[package.files]]
file = "fastapi-0.100.0-py3-none-any.whl"
hash = "sha256:abc123..."
```

**锁文件的关键规则**：

```bash
# poetry.lock 必须提交到 Git（应用项目）
git add poetry.lock
git commit -m "Update dependencies"

# poetry install 读取 lock 文件安装精确版本
# 不更新任何版本，确保环境一致
poetry install

# poetry add / update 会更新 lock 文件
# 新增或升级依赖时自动更新
```

### 4.7 冲突解决

```bash
# 版本冲突时的错误示例：
# SolverProblemError
# Because my-project depends on fastapi (^0.100.0)
# and starlette (^0.30.0), fastapi>=0.100.0 depends on starlette (>=0.27,<0.28.0)
# So my-project cannot be resolved.

# 解决方法1：放宽约束
poetry add "starlette>=0.27.0,<0.28.0"

# 解决方法2：查看依赖树找到冲突源
poetry show --tree

# 解决方法3：强制锁定传递依赖
# 在 pyproject.toml 中添加
# [tool.poetry.dependencies]
# starlette = "0.27.0"  # 强制版本

# 解决方法4：清除缓存重试
poetry cache clear --all pypi
poetry lock
```

### 4.8 依赖锁定与安全审计

```bash
# 安装安全扫描工具
poetry add --group dev pip-audit

# 扫描已知漏洞
poetry run pip-audit
# 输出示例：
# Name       Version  ID             Fix Versions
# ---------- -------- -------------- ------------
# requests   2.28.0   PYSEC-2023-1   2.31.0
# pillow     9.5.0    PYSEC-2023-10  10.0.1

# 输出 JSON（CI 集成）
poetry run pip-audit --format json

# 自动修复（升级有漏洞的包）
poetry run pip-audit --fix
```

```bash
# 依赖许可检查
poetry add --group dev pip-licenses

# 查看所有依赖的许可证
poetry run pip-licenses

# 输出示例：
# Name    Version    License
# ------- ---------- -------
# fastapi 0.100.0    MIT
# pydantic 2.0.0     MIT
# pytest   7.4.0     MIT
```

### 4.9 依赖更新策略

```python
# 推荐的依赖更新节奏：
#
# 每周：
#   - poetry show --outdated  # 查看可更新
#
# 每月：
#   - poetry update          # 更新所有兼容版本
#   - 运行测试确保无问题
#   - 提交新的 lock 文件
#
# 每季度：
#   - 审查依赖树（poetry show --tree）
#   - 移除未使用的依赖
#   - 检查安全漏洞（pip-audit）
#
# 大版本升级（如 Django 4→5）：
#   - 在单独分支进行
#   - 仔细阅读 CHANGELOG
#   - 逐步修复兼容性问题
#   - 充分测试后合并
```

### 4.10 导出各种格式

```bash
# 导出 requirements.txt（带哈希）
poetry export -f requirements.txt -o requirements.txt --without-hashes

# 导出仅生产依赖
poetry export -f requirements.txt --without dev,test -o requirements-prod.txt

# 导出 conda 格式（配合 conda 使用）
# Poetry 本身不直接支持 conda，需要手动转换

# 导出到 pip-tools 格式
# 不需要，Poetry 直接管理
```

---

> 💡 **本章深度讲解**：依赖管理的核心是"声明"和"锁定"的分离。pyproject.toml 声明你需要什么范围的版本，poetry.lock 锁定你实际安装了什么版本。`add`/`remove`/`update` 修改声明并重新解析；`install` 严格按照 lock 文件安装。冲突时先用 `poetry show --tree` 找到依赖链，再调整版本约束。理解这个工作流后，依赖管理就变得可预测了。
>
> **📝 精简总结**：
> - 核心概念：add/remove/update/install、lock 文件、冲突解析
> - 关键原理：install 读 lock；update 重新解析；lock 包含哈希
> - 常用操作：`poetry add pkg`；`poetry show --tree`；`poetry update pkg`
> - 最佳实践：CI 用 install 不用 update；定期 update 获取安全补丁
> - 常见坑点：CI 用 update 导致不可预测；冲突时不知道怎么排查
> - 面试高频：install vs update；lock 文件的作用；冲突解决流程

### 🎯 梯度练习题

**基础题（⭐）**
1. `poetry install` 和 `poetry update` 的区别？
   - 答案：install 读 lock 文件精确安装；update 重新解析并更新 lock。
2. 如何查看依赖树？
   - 答案：`poetry show --tree`。

**进阶题（⭐⭐）**
1. 为什么 CI 中应该用 `poetry install` 而不是 `poetry update`？
   - 思考方向：可复现性；update 可能引入新版本导致意外失败。
2. 遇到 SolverProblemError 时如何排查？
   - 思考方向：`poetry show --tree` 找冲突链；调整版本约束；清除缓存。

**实战题（⭐⭐⭐）**
- **背景**：你的项目依赖 A 需要 requests>=2.0，依赖 B 需要 requests<2.0。
- **需求**：解决版本冲突。
- **要求**：① 用 `poetry show --tree` 找到冲突来源；② 决定升级哪个依赖；③ 验证解决方案。
- **验收标准**：`poetry install` 成功；所有依赖兼容。
- **提示**：可能需要升级 B 到支持 requests>=2.0 的版本。

---

## 五、虚拟环境管理

### 5.1 Poetry 虚拟环境工作原理

Poetry 自动为每个项目管理虚拟环境，不需要手动创建和激活：

```mermaid
graph LR
    A[poetry install] --> B{虚拟环境存在?}
    B -->|否| C[自动创建 .venv]
    B -->|是| D[使用现有 .venv]
    C --> E[安装依赖]
    D --> E
    E --> F[完成]
```

### 5.2 虚拟环境基本操作

```bash
# 安装依赖（自动创建/使用虚拟环境）
poetry install

# 查看虚拟环境信息
poetry env info

# 输出示例：
# Virtualenv
# Python: 3.12.0
# Path: /home/user/projects/my-project/.venv
# Executable: /home/user/projects/my-project/.venv/bin/python
# Valid: True

# 查看虚拟环境路径
poetry env info --path

# 列出所有虚拟环境
poetry env list

# 在虚拟环境中执行命令
poetry run python main.py
poetry run pytest
poetry run uvicorn my_project.main:app --reload
```

### 5.3 激活虚拟环境

```bash
# 进入虚拟环境的子 shell
poetry shell

# 现在你在虚拟环境中，可以直接运行命令
python main.py
pytest
exit  # 退出子 shell

# 或者用 poetry run（不进入 shell）
poetry run python main.py
```

### 5.4 指定 Python 版本

```bash
# 查看 Poetry 检测到的 Python 版本
poetry env info

# 指定使用哪个 Python 创建虚拟环境
poetry env use python3.12
poetry env use /usr/bin/python3.11
poetry env use 3.10  # Poetry 会自动查找

# 删除虚拟环境
poetry env remove python3.10

# 删除所有虚拟环境
poetry env remove --all
```

### 5.5 虚拟环境配置

```bash
# 在项目目录内创建 .venv（推荐）
poetry config virtualenvs.in-project true

# 不创建虚拟环境（直接安装到系统 Python）
# 仅在 Docker 中使用
poetry config virtualenvs.create false

# 虚拟环境创建位置（默认）
# ~/.cache/pypoetry/virtualenvs/
# 或 ~/Library/Caches/pypoetry/virtualenvs/ (macOS)
```

```toml
# 也可以在项目中配置（pyproject.toml）
# 但更推荐用 poetry config 全局设置
```

### 5.6 常见虚拟环境问题

```python
# 问题：IDE 找不到虚拟环境
# 解决：poetry config virtualenvs.in-project true
# 然后删除旧的虚拟环境重新创建
poetry env remove --all
poetry install

# 问题：poetry run python 版本不对
# 解决：查看 pyproject.toml 中的 python 约束
# [tool.poetry.dependencies]
# python = "^3.10"  # 需要 3.10+
poetry env use python3.12
poetry install

# 问题：磁盘空间不足
# 原因：多个项目的虚拟环境累积
# 解决：清理不用的虚拟环境
poetry env list  # 查看所有
# 删除不用的项目后清理
rm -rf ~/.cache/pypoetry/virtualenvs/
```

### 5.7 多 Python 版本共存

```bash
# 场景：项目需要同时测试 Python 3.10 和 3.12

# 1. 创建 Python 3.10 虚拟环境
poetry env use python3.10
poetry install
# 运行测试
poetry run pytest

# 2. 切换到 Python 3.12
poetry env use python3.12
poetry install
# 运行测试
poetry run pytest

# 3. 查看所有环境
poetry env list
# my-project-py3.10
# my-project-py3.12
```

```python
# pyproject.toml 中声明 Python 版本范围
[tool.poetry.dependencies]
# 允许 3.10 到 4.0
python = "^3.10"

# 或者更严格
python = ">=3.10,<3.13"
```

### 5.8 在 CI 中管理虚拟环境

```bash
# GitHub Actions 中 Poetry 自动创建虚拟环境
# 不需要手动管理
# setup-python 安装 Python 后，poetry install 自动创建 .venv

# 缓存虚拟环境（加速 CI）
# GitHub Actions:
#   - uses: actions/setup-python@v5
#     with:
#       python-version: "3.12"
#       cache: 'poetry'  # 自动缓存
```

### 5.9 虚拟环境磁盘管理

```bash
# 查看 Poetry 占用的磁盘空间
du -sh ~/.cache/pypoetry/

# 查看所有虚拟环境
poetry env list --full-path

# 清理不用的虚拟环境
# 列出所有
poetry env list
# 删除指定
poetry env remove my-project-py3.9

# 清理 Poetry 缓存
poetry cache clear --all pypi

# 只清理下载缓存（不删除已安装的包）
poetry cache list
```

### 5.10 虚拟环境与 IDE 集成

```json
# VSCode settings.json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.terminal.activateEnvironment": true
}
```

```bash
# PyCharm
# Settings -> Project -> Python Interpreter
# 选择 .venv/bin/python 或 .venv\Scripts\python.exe
```

```bash
# 如果 IDE 找不到虚拟环境
# 1. 确认 virtualenvs.in-project true
poetry config virtualenvs.in-project true

# 2. 重新创建虚拟环境
poetry env remove --all
poetry install

# 3. 在 IDE 中手动选择 .venv 中的 Python
```

### 5.11 虚拟环境与系统 Python 的关系

```python
# Poetry 虚拟环境的工作原理：
# 1. Poetry 找到系统 Python 解释器
# 2. 在 .venv/ 中创建虚拟环境（软链接或复制）
# 3. pip 安装的包都安装到 .venv/lib/.../site-packages/
# 4. poetry run 在 .venv 的上下文中执行命令

# 与系统 Python 的隔离：
# - .venv 中的包不影响系统 Python
# - 系统 Python 的包不影响 .venv
# - 标准库（os, sys 等）共享

# 查看虚拟环境中的包
poetry run pip list

# 查看系统 Python 的包（不应该混用）
pip list
```

### 5.12 虚拟环境迁移

```bash
# 迁移项目到新机器

# 1. 复制项目文件（不包括 .venv/）
scp -r my-project/ user@new-machine:~/

# 2. 在新机器上安装 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 3. 进入项目目录
cd my-project

# 4. 安装依赖（从 poetry.lock 安装）
poetry install

# 注意：不需要复制 .venv/，因为它是机器特定的
# poetry install 会根据 lock 文件重建
```

> ✅ 最佳实践：始终设置 `virtualenvs.in-project true`。这样 .venv 在项目目录中，VSCode/PyCharm 自动识别，不需要手动配置 Python 解释器路径。

---

> 💡 **本章深度讲解**：Poetry 的虚拟环境管理是它最受欢迎的特性之一——你再也不需要手动 `python -m venv` 和 `source activate`。Poetry 自动根据项目的 Python 版本约束选择合适的解释器，自动创建和管理 .venv。`poetry run` 让你在不激活虚拟环境的情况下执行命令。这大大简化了多项目开发的工作流。
>
> **📝 精简总结**：
> - 核心概念：.venv、poetry shell、poetry run、env use
> - 关键原理：自动创建虚拟环境；按 python 约束选择解释器
> - 常用操作：`poetry shell`；`poetry run cmd`；`poetry env use 3.12`
> - 最佳实践：virtualenvs.in-project true；一个项目一个虚拟环境
> - 常见坑点：IDE 找不到 .venv；Python 版本不匹配
> - 面试高频：poetry run vs poetry shell；virtualenvs.in-project

### 🎯 梯度练习题

**基础题（⭐）**
1. `poetry shell` 和 `poetry run` 的区别？
   - 答案：shell 进入虚拟环境子 shell；run 在虚拟环境中执行单条命令。
2. 如何指定 Python 版本创建虚拟环境？
   - 答案：`poetry env use python3.12`。

**进阶题（⭐⭐）**
1. 为什么 Docker 中要设置 `virtualenvs.create false`？
   - 思考方向：Docker 容器内不需要虚拟环境；直接安装到系统 Python 更简单。
2. `virtualenvs.in-project true` 的好处是什么？
   - 思考方向：IDE 自动识别；删除项目时自动清理；团队一致性。

**实战题（⭐⭐⭐）**
- **背景**：你的项目需要同时支持 Python 3.10 和 3.12。
- **需求**：配置多版本虚拟环境。
- **要求**：① 创建 Python 3.10 的虚拟环境；② 安装依赖；③ 创建 Python 3.12 的虚拟环境；④ 验证两个版本都能运行。
- **验收标准**：`poetry env list` 显示两个环境；都能运行测试。
- **提示**：用 `poetry env use` 切换。

---

## 六、依赖组与版本约束语义

### 6.1 依赖组概念

依赖组（Dependency Groups）是 Poetry 1.2+ 的核心特性，允许将依赖按用途分组：

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
ruff = "^0.1"
mypy = "^1.5"

[tool.poetry.group.test.dependencies]
pytest-asyncio = "^0.21"
pytest-cov = "^4.1"
factory-boy = "^3.3"

[tool.poetry.group.docs.dependencies]
mkdocs = "^1.5"
mkdocs-material = "^9.2"

[tool.poetry.group.lint.dependencies]
ruff = "^0.1"
mypy = "^1.5"
pre-commit = "^3.5"
```

### 6.2 依赖组操作

```bash
# 添加到指定组
poetry add --group dev pytest
poetry add --group docs mkdocs

# 安装时排除某个组
poetry install --without dev

# 只安装某个组
poetry install --only docs

# 安装多个组
poetry install --with dev,test

# 生产环境安装（排除所有开发组）
poetry install --without dev,test,docs
```

### 6.3 可选依赖组

```toml
# 可选组：用户可以选择安装
[tool.poetry.group.redis]
optional = true

[tool.poetry.group.redis.dependencies]
redis = "^5.0"
```

```bash
# 安装时包含可选组
poetry install --with redis

# 用户安装你的包时选择 extras
pip install my-package[redis]
```

### 6.4 版本约束语义深入

```toml
# 语义化版本（SemVer）：MAJOR.MINOR.PATCH
# 1.4.2
#  │ │ └─ PATCH：向后兼容的 bug 修复
#  │ └─── MINOR：向后兼容的新功能
#  └───── MAJOR：不兼容的 API 变更

# ^ 符号详解
^1.2.3   # 允许 MINOR 和 PATCH 更新：>=1.2.3, <2.0.0
^0.2.3   # 0.x 特殊处理：只允许 PATCH 更新：>=0.2.3, <0.3.0
^0.0.3   # 0.0.x：只允许精确版本：>=0.0.3, <0.0.4

# ~ 符号详解
~1.2.3   # 只允许 PATCH 更新：>=1.2.3, <1.3.0
~1.2     # 等价于 ~1.2.0：>=1.2, <1.3
~1       # 等价于 ~1.0：>=1.0, <2.0
```

```python
# 版本约束选择指南
# 生产依赖（你控制升级）：
fastapi = "^0.100.0"   # 允许兼容更新

# 库依赖（你发布的包）：
requests = "^2.31.0"  # 宽松约束，让用户有灵活性

# 工具链（需要精确版本）：
ruff = "0.1.9"         # 精确版本，避免 lint 规则变化
black = "23.7.0"       # 精确版本，格式化规则稳定
```

### 6.5 约束传递依赖

```toml
# 如果传递依赖有问题，可以在 pyproject.toml 中强制约束
[tool.poetry.dependencies]
# 你的直接依赖
fastapi = "^0.100.0"

# 强制约束传递依赖（即使你不直接使用它）
starlette = "0.27.0"  # 锁定 starlette 版本
# 这样 Poetry 解析时会选择满足 fastapi 要求且 starlette=0.27.0 的方案
```

### 6.6 平台特定依赖

```toml
[tool.poetry.dependencies]
python = "^3.10"

# 仅在 Linux 上安装
pywatchman = { version = "^4.0", markers = "sys_platform == 'linux'" }

# 仅在 Windows 上安装
pywin32 = { version = "^306", markers = "sys_platform == 'win32'" }

# Python 版本特定依赖
dataclasses = { version = "^0.8", markers = "python_version < '3.7'" }

# 操作系统特定依赖
psycopg2-binary = { version = "^2.9", markers = "platform_system != 'Windows'" }
```

### 6.7 extras 可选功能

```toml
[tool.poetry]
name = "data-toolkit"

[tool.poetry.dependencies]
python = "^3.10"
pandas = "^2.0"
# 可选依赖
redis = { version = "^5.0", optional = true }
sqlalchemy = { version = "^2.0", optional = true }

[tool.poetry.extras]
redis = ["redis>=5.0"]
database = ["sqlalchemy>=2.0"]
all = ["redis>=5.0", "sqlalchemy>=2.0"]
```

```bash
# 用户安装时选择 extras
pip install data-toolkit              # 只装核心依赖
pip install data-toolkit[redis]       # 加 redis
pip install data-toolkit[database]    # 加 sqlalchemy
pip install data-toolkit[all]        # 全部
```

### 6.8 版本约束实战案例

```python
# 场景：一个 Web API 项目的依赖策略

# 核心框架（用 ^，允许兼容更新）
fastapi = "^0.104.0"
pydantic = "^2.5.2"

# 数据库驱动（用 ^，允许补丁更新）
sqlalchemy = { version = "^2.0.23", extras = ["asyncio"] }
asyncpg = "^0.29.0"

# 工具链（精确版本，避免规则变化）
ruff = "0.1.6"          # Lint 规则每个版本可能变
black = "23.12.1"       # 格式化规则稳定
mypy = "1.7.1"          # 类型检查严格性稳定

# 测试框架（用 ^）
pytest = "^7.4.3"

# 为什么这样选择？
# - 框架类包：^ 允许安全更新（bug 修复、性能优化）
# - 工具链包：精确版本（避免 lint/format 规则变化导致 CI 失败）
# - 测试框架：^ 允许新特性
```

> ✅ 最佳实践：工具链类依赖（ruff/black/mypy）用精确版本，因为这些工具的规则每个版本可能变化，^ 约束可能导致 CI 突然失败。框架和库依赖用 ^ 约束，允许安全更新。

### 6.9 Python 版本约束策略

```toml
# Python 版本约束的选择

# 保守策略（库项目）
python = ">=3.9,<4.0"  # 支持多个版本

# 平衡策略（推荐）
python = "^3.10"       # 3.10 到 4.0

# 激进策略（新应用）
python = ">=3.12"     # 只用最新版

# 精确策略（Docker 部署）
python = "3.12"       # 固定版本
```

```python
# Python 版本约束的影响：
# 1. 太宽（>=3.9）：需要测试多个版本，CI 时间长
# 2. 太严（==3.12）：限制用户选择
# 3. 平衡（^3.10）：推荐，覆盖主流版本
# 4. Docker 部署可以更严格，因为容器控制 Python 版本
```

### 6.10 语义化版本（SemVer）详解

```python
# SemVer 格式：MAJOR.MINOR.PATCH
# 1.4.2
#  │ │ └─ PATCH：向后兼容的 bug 修复
#  │ └─── MINOR：向后兼容的新功能
#  └───── MAJOR：不兼容的 API 变更

# 示例演进：
# 1.0.0 -> 1.0.1  # 修复 bug
# 1.0.0 -> 1.1.0  # 新增功能
# 1.0.0 -> 2.0.0  # 不兼容变更

# 预发布版本：
# 1.0.0a0    # alpha（内部测试）
# 1.0.0b1    # beta（公开测试）
# 1.0.0rc1   # release candidate（候选发布）
# 1.0.0      # 正式版
```

> 🎯 面试高频：什么是语义化版本？为什么重要？——SemVer 用 MAJOR.MINOR.PATCH 三个数字表示版本。MAJOR 不兼容变更，MINOR 向后兼容新功能，PATCH 向后兼容 bug 修复。遵循 SemVer 让用户知道升级的风险——^1.2.3 允许 MINOR 和 PATCH 更新，风险可控。

> ❌ 常见坑点：不要随意锁定传递依赖版本。只有在传递依赖有安全漏洞或已知 bug 时才强制锁定。随意锁定会阻碍正常的更新升级，可能导致依赖解析变慢或冲突。

---

> 💡 **本章深度讲解**：依赖组让项目依赖有了组织结构——开发、测试、文档、生产各有各的依赖。生产部署时 `--without dev` 确保不安装不必要的工具。版本约束符号的选择反映了你的风险偏好：`^` 允许更多更新（更容易获得安全补丁），`~` 更保守（更少意外）。理解 SemVer 和约束符号后，你可以精确控制依赖的升级节奏。
>
> **📝 精简总结**：
> - 核心概念：依赖组、SemVer、^/~ 约束、传递依赖锁定
> - 关键原理：组分组管理；--without/--only 控制安装；0.x 版本特殊处理
> - 常用操作：`poetry add --group dev`；`poetry install --without dev`
> - 最佳实践：生产用 ^；工具链精确版本；只在必要时锁定传递依赖
> - 常见坑点：0.x 版本 ^ 的行为；过度锁定传递依赖
> - 面试高频：^ vs ~；依赖组；SemVer 语义

### 🎯 梯度练习题

**基础题（⭐）**
1. 如何只安装生产依赖（不安装 dev 组）？
   - 答案：`poetry install --without dev`。
2. `^1.2.3` 允许更新到哪个版本？
   - 答案：允许 1.2.3 到 2.0.0（不含 2.0.0）。

**进阶题（⭐⭐）**
1. 为什么 0.x 版本的 `^` 行为不同？
   - 思考方向：0.x 版本 API 不稳定；SemVer 规范；Poetry 的特殊处理。
2. 什么时候应该锁定传递依赖？
   - 思考方向：安全漏洞；已知 bug；兼容性问题。不要随意锁定。

**实战题（⭐⭐⭐）**
- **背景**：你需要配置一个团队项目的依赖组。
- **需求**：分组管理依赖。
- **要求**：① dev 组：pytest、ruff、mypy；② docs 组：mkdocs；③ 生产依赖：fastapi、sqlalchemy；④ 生产部署时排除 dev 和 docs。
- **验收标准**：`poetry install --without dev,docs` 只安装生产依赖。
- **提示**：用 `[tool.poetry.group.xxx.dependencies]` 语法。

---

## 七、项目构建与发布

### 7.1 构建分发包

```bash
# 构建 wheel 和 sdist（源码分发包）
poetry build

# 输出：
# Building my-project (0.1.0)
#   - Building sdist
#   - Built my_project-0.1.0.tar.gz
#   - Building wheel
#   - Built my_project-0.1.0-py3-none-any.whl
```

```bash
# 只构建 wheel（推荐，更快安装）
poetry build --format wheel

# 只构建 sdist
poetry build --format sdist

# 查看构建产物
ls dist/
# my_project-0.1.0-py3-none-any.whl
# my_project-0.1.0.tar.gz
```

### 7.2 发布到 PyPI

```bash
# 发布到官方 PyPI（需要 PyPI 账号和 token）
poetry publish

# 发布并同时构建
poetry publish --build

# 配置 PyPI token
poetry config pypi-token.pypi pypi-xxxxxxxxxxxx

# 发布到测试 PyPI
poetry publish --repository testpypi
```

### 7.3 发布到私有仓库

```bash
# 添加私有源
poetry source add --priority=primary my-private-repo https://pypi.example.com/simple/

# 配置认证 token
poetry config pypi-token.my-private-repo xxxxxxxx

# 发布到私有仓库
poetry publish --repository my-private-repo

# 或在 pyproject.toml 中配置
# [tool.poetry]
# ...
```

### 7.4 版本号管理

```bash
# 查看当前版本
poetry version
# 输出：my-project 0.1.0

# 递增补丁版本（0.1.0 → 0.1.1）
poetry version patch

# 递增次版本（0.1.0 → 0.2.0）
poetry version minor

# 递增主版本（0.1.0 → 1.0.0）
poetry version major

# 预发布版本
poetry version prerelease
# 1.0.0 → 1.0.1a0

# 直接设置版本
poetry version 2.0.0
```

### 7.5 .gitignore 和发布检查清单

```gitignore
# .gitignore
.venv/
__pycache__/
*.pyc
dist/
build/
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage
```

```bash
# 发布前检查清单
# 1. 更新版本号
poetry version minor

# 2. 更新 changelog
# 手动编辑 CHANGELOG.md

# 3. 运行测试
poetry run pytest

# 4. 运行 lint
poetry run ruff check .
poetry run mypy my_project

# 5. 构建
poetry build

# 6. 发布
poetry publish
```

### 7.6 预发布版本

```bash
# 预发布版本（alpha/beta/rc）
poetry version prerelease
# 1.0.0 -> 1.0.1a0

# 指定预发布标签
poetry version prerelease --preview
# 1.0.0 -> 1.1.0a0

# 版本号格式：
# 1.0.0a0     # alpha
# 1.0.0b1     # beta
# 1.0.0rc1    # release candidate
# 1.0.0       # 正式版
```

### 7.7 自定义构建

```toml
# pyproject.toml - 自定义构建配置
[tool.poetry]
# 指定要包含的文件
include = [
    "my_project/py.typed",      # 类型标记
    "my_project/data/*.json",    # 数据文件
]

# 排除文件
exclude = [
    "my_project/tests/",
    "my_project/*.pyi",
]
```

```bash
# 构建后检查包内容
tar tzf dist/my_project-0.1.0.tar.gz
# 确认包含所有必要文件，排除测试和文档
```

---

> 💡 **本章深度讲解**：构建和发布是将代码变成可分发包的最后一步。`poetry build` 自动生成 wheel 和 sdist，`poetry publish` 自动上传到 PyPI。版本号管理遵循 SemVer——patch 是 bug 修复，minor 是新功能，major 是 breaking change。在生产项目中，发布流程应该自动化（CI 触发），手动发布容易遗漏步骤。
>
> **📝 精简总结**：
> - 核心概念：wheel/sdist、PyPI 发布、SemVer 版本递增
> - 关键原理：build 生成分发包；publish 上传到仓库
> - 常用操作：`poetry build`；`poetry publish`；`poetry version minor`
> - 最佳实践：发布前运行测试和 lint；CI 自动化发布
> - 常见坑点：忘记配置 PyPI token；版本号不规范
> - 面试高频：wheel vs sdist；SemVer 版本管理

### 🎯 梯度练习题

**基础题（⭐）**
1. `poetry build` 生成哪两种格式？
   - 答案：wheel（.whl）和 sdist（.tar.gz）。
2. `poetry version minor` 做了什么？
   - 答案：次版本+1，补丁归零（0.1.0 → 0.2.0）。

**进阶题（⭐⭐）**
1. wheel 和 sdist 的区别？
   - 思考方向：wheel 是预编译的分发包，安装快；sdist 是源码包，需要在安装时构建。
2. 为什么发布前要运行所有测试？
   - 思考方向：发布后修复需要新版本；PyPI 上的包无法修改（只能覆盖或新版本）。

**实战题（⭐⭐⭐）**
- **背景**：你要发布一个开源 Python 包到 PyPI。
- **需求**：完成完整的发布流程。
- **要求**：① 更新版本号；② 运行测试；③ 构建分发包；④ 发布到 PyPI Test。
- **验收标准**：PyPI Test 上能下载到你的包；`pip install --index-url https://test.pypi.org/simple/ your-package` 成功。
- **提示**：先在 TestPyPI 测试，再发布到正式 PyPI。

---

## 八、与 pip / conda / pipenv 对比

### 8.1 Poetry vs pip + requirements.txt

| 维度 | pip + requirements.txt | Poetry |
|------|----------------------|--------|
| 依赖声明 | requirements.txt（平铺） | pyproject.toml（结构化） |
| 依赖锁定 | pip freeze（包含间接依赖） | poetry.lock（精确+哈希） |
| 依赖解析 | pip（简单解析） | 内置解析器（PubGrub） |
| 虚拟环境 | 手动 venv + activate | 自动管理 |
| 开发依赖 | 手动 requirements-dev.txt | 依赖组自动分离 |
| 打包发布 | setup.py + twine | 内置 build + publish |
| 元数据 | 分散在 setup.py 等 | pyproject.toml 集中 |
| 可复现性 | 低（无 lock） | 高（lock + 哈希） |

### 8.2 Poetry vs conda

| 维度 | conda | Poetry |
|------|-------|--------|
| 语言 | 跨语言（Python/R/C++） | 仅 Python |
| 包源 | Anaconda Repository | PyPI |
| 环境管理 | 强大（跨语言） | 仅 Python 包 |
| Python 版本 | 可安装 Python 本身 | 使用系统 Python |
| 适合场景 | 数据科学、科学计算 | Web 开发、API、CLI |
| 包数量 | 较少（~8000） | 极多（~50万+） |
| 速度 | 较慢（求解器复杂） | 较快（PubGrub） |

### 8.3 Poetry vs pipenv

| 维度 | pipenv | Poetry |
|------|--------|--------|
| 配置文件 | Pipfile + Pipfile.lock | pyproject.toml + poetry.lock |
| 虚拟环境 | 内置管理 | 内置管理 |
| 打包发布 | 不支持 | 内置支持 |
| 依赖解析 | 较慢（曾有性能问题） | 快（自定义解析器） |
| 维护活跃度 | 低（基本停滞） | 高（活跃开发） |
| 社区采纳 | 下降 | 上升（事实标准） |
| 推荐度 | 不推荐新项目 | 强烈推荐 |

### 8.4 迁移指南

```bash
# 从 requirements.txt 迁移到 Poetry
# 1. 初始化 Poetry 项目
poetry init

# 2. 逐行添加依赖
poetry add fastapi uvicorn sqlalchemy

# 3. 添加开发依赖
poetry add --group dev pytest pytest-cov

# 4. 删除旧文件
rm requirements.txt requirements-dev.txt
rm -rf venv/

# 5. 用 Poetry 安装
poetry install
```

```bash
# 从 Pipenv 迁移到 Poetry
# 1. 从 Pipfile 读取依赖
cat Pipfile

# 2. 初始化 Poetry
poetry init

# 3. 手动添加 Pipfile 中的依赖
poetry add fastapi uvicorn

# 4. 删除 Pipfile 和 Pipfile.lock
rm Pipfile Pipfile.lock

# 5. 安装
poetry install
```

### 8.5 pip-tools 方案对比

| 维度 | pip-tools | Poetry |
|------|-----------|--------|
| 声明文件 | requirements.in | pyproject.toml |
| 锁文件 | requirements.txt | poetry.lock |
| 虚拟环境 | 需手动 venv | 内置管理 |
| 打包发布 | 需 setuptools | 内置 |
| 依赖解析 | pip 解析 | PubGrub 解析 |
| 学习曲线 | 较陡 | 中等 |
| 适合场景 | 简单项目 | 中大型项目 |

```bash
# pip-tools 工作流
# 1. 写 requirements.in
echo "fastapi" > requirements.in
echo "uvicorn" >> requirements.in

# 2. 编译（生成锁定的 requirements.txt）
pip-compile requirements.in

# 3. 安装
pip-sync requirements.txt
```

### 8.6 uv — 新一代 Python 包管理器

```bash
# uv 是用 Rust 写的新一代 Python 包管理器
# 速度比 Poetry 快 10-100 倍

# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# uv 兼容 pyproject.toml 和 Poetry 的配置
uv add fastapi
uv remove pytest
uv sync

# uv 安装快的原因：
# 1. 用 Rust 写，原生性能
# 2. 全局缓存（跨项目共享包）
# 3. 并行下载和安装
```

| 维度 | Poetry | uv |
|------|--------|-----|
| 语言 | Python | Rust |
| 速度 | 中等 | 极快 |
| 配置文件 | pyproject.toml | pyproject.toml（兼容） |
| 成熟度 | 高 | 快速发展中 |
| 推荐 | 稳定项目 | 新项目/追求速度 |

> ✅ 最佳实践：新项目可以考虑 uv 作为包管理器（兼容 Poetry 配置），但生产环境建议用成熟稳定的 Poetry。uv 正在快速发展，API 可能变化。

---

> 💡 **本章深度讲解**：工具选择不是非此即彼。对于纯 Python Web 项目，Poetry 是最佳选择；对于数据科学项目，conda 仍然不可替代（因为需要非 Python 依赖如 CUDA、MKL）。pip 本身在很多场景仍然够用（简单脚本、Docker 容器内）。理解各工具的适用场景比记住命令更重要。
>
> **📝 精简总结**：
> - 核心概念：pip/conda/pipenv vs Poetry 的定位差异
> - 关键原理：Poetry 统一管理；conda 跨语言；pip 最简
> - 常用操作：迁移时 `poetry init` + 逐行 add
> - 最佳实践：Web 项目用 Poetry；数据科学用 conda；简单脚本用 pip
> - 常见坑点：盲目用 Poetry 替代 conda（数据科学场景不适合）
> - 面试高频：Poetry vs pip；conda vs Poetry；工具选择依据

### 🎯 梯度练习题

**基础题（⭐）**
1. Poetry 和 conda 的主要区别？
   - 答案：Poetry 仅 Python；conda 跨语言，可安装 Python 本身。
2. 为什么新项目不推荐用 pipenv？
   - 答案：维护停滞；Poetry 功能更全面且活跃开发。

**进阶题（⭐⭐）**
1. 数据科学项目为什么用 conda 而不是 Poetry？
   - 思考方向：需要非 Python 依赖（CUDA、MKL、C 库）；Poetry 只能管理 Python 包。
2. 什么场景下 pip 就够了？
   - 思考方向：简单脚本；Docker 容器内；不需要打包发布。

**实战题（⭐⭐⭐）**
- **背景**：你的团队有混合项目——Web API 用 pip+requirements.txt，数据处理用 conda。
- **需求**：统一工具链。
- **要求**：① Web API 迁移到 Poetry；② 数据项目保留 conda；③ 制定团队规范文档。
- **验收标准**：Web 项目用 Poetry；数据项目用 conda；规范清晰。
- **提示**：不是所有项目都要用 Poetry。

---

## 九、私有仓库与多项目工作区

### 9.1 私有仓库配置

```bash
# 添加私有 PyPI 源
poetry source add --priority=primary my-company-pypi https://pypi.company.com/simple/

# 配置认证
poetry config pypi-token.my-company-pypi <your-token>

# 从私有源安装包
poetry add internal-package
```

```toml
# pyproject.toml 中的源配置
[[tool.poetry.source]]
name = "my-company-pypi"
url = "https://pypi.company.com/simple/"
priority = "primary"  # primary | secondary | explicit
```

### 9.2 源优先级

| 优先级 | 说明 | 用途 |
|--------|------|------|
| `primary` | 与 PyPI 同等地位，一起搜索 | 私有+公共包混合 |
| `secondary` | 只在 primary 找不到时搜索 | 私有包补充 |
| `explicit` | 只在显式指定时使用 | 非常私有的包 |

```bash
# 只从显式源安装
poetry add --source my-company-pypi internal-package
```

### 9.3 多项目工作区（Monorepo）

```bash
# Monorepo 结构
my-monorepo/
├── pyproject.toml          # 根项目配置
├── packages/
│   ├── package-a/
│   │   ├── pyproject.toml
│   │   └── package_a/
│   └── package-b/
│       ├── pyproject.toml
│       └── package_b/
└── services/
    └── api/
        ├── pyproject.toml
        └── api/
```

```toml
# packages/package-a/pyproject.toml
[tool.poetry]
name = "package-a"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.10"
package-b = { path = "../package-b" }
```

```bash
# 在 monorepo 中安装本地包
poetry add ./packages/package-a
poetry add --editable ./packages/package-a  # 开发模式
```

### 9.4 Git 依赖

```bash
# 从 Git 安装
poetry add git+https://github.com/user/repo.git

# 指定分支
poetry add git+https://github.com/user/repo.git#develop

# 指定标签
poetry add git+https://github.com/user/repo.git#v1.0.0

# 指定 commit
poetry add git+https://github.com/user/repo.git#abc123def

# SSH 方式
poetry add git+ssh://git@github.com/user/repo.git
```

### 9.5 路径依赖（本地开发）

```toml
# pyproject.toml
[tool.poetry.dependencies]
# 本地路径依赖（开发时修改立即生效）
my-utils = { path = "../my-utils", develop = true }

# 非开发模式（复制安装）
other-pkg = { path = "../other-pkg" }
```

> ✅ 最佳实践：Monorepo 中用 `develop = true` 路径依赖，这样修改本地包代码后不需要重新安装，Poetry 直接引用源目录。

### 9.6 企业级私有仓库方案

```bash
# 方案1：devpi（自建 PyPI 代理）
# devpi 缓存公共包 + 存储私有包

# 安装 devpi
pip install devpi-server devpi-client

# 启动服务器
devpi-server --start --host 0.0.0.0 --port 3141

# 配置 Poetry 使用 devpi
poetry source add --priority=primary devpi http://localhost:3141/root/pypi/+simple/
```

```bash
# 方案2：Artifactory / Nexus（企业级）
# 配置 Poetry 使用 Artifactory
poetry source add --priority=primary company-artifactory \
    https://artifactory.company.com/api/pypi/pypi/simple/

# 配置认证
poetry config http-basic.company-artifactory username password
```

```bash
# 方案3：Git 依赖（最简单的私有分发）
# 不需要私有仓库，直接从 Git 安装
poetry add git+ssh://git@git.company.com/lib/utils.git#v1.0.0
```

### 9.7 多项目工作区实战

```bash
# Monorepo 完整结构
my-monorepo/
├── pyproject.toml          # 根项目
├── poetry.lock
├── packages/
│   ├── core/               # 核心库
│   │   ├── pyproject.toml
│   │   └── core/
│   └── utils/              # 工具库
│       ├── pyproject.toml
│       └── utils/
└── services/
    └── api/                # API 服务
        ├── pyproject.toml
        └── api/
```

```toml
# services/api/pyproject.toml
[tool.poetry]
name = "api-service"

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.104.0"
core = { path = "../../packages/core" }
utils = { path = "../../packages/utils" }
```

```bash
# 在 API 服务目录中安装
cd services/api
poetry install
# Poetry 会自动安装 core 和 utils 本地包
```

---

> 💡 **本章深度讲解**：私有仓库和多项目工作区是企业级 Python 开发的常见需求。大型公司通常有自己的 PyPI 镜像/代理（如 devpi、Artifactory），Poetry 可以无缝接入。Monorepo 中多个包互相依赖时，路径依赖和 Git 依赖让本地开发和 CI 部署都能正常工作。
>
> **📝 精简总结**：
> - 核心概念：私有源、源优先级、Monorepo、路径依赖
> - 关键原理：primary/secondary/explicit 源搜索策略；develop 模式直接引用
> - 常用操作：`poetry source add`；`poetry add ./local-pkg`
> - 最佳实践：develop 模式用于本地开发；explicit 源用于私有包
> - 常见坑点：认证 token 未配置；源优先级不当导致下载慢
> - 面试高频：源优先级；路径依赖 vs Git 依赖

### 🎯 梯度练习题

**基础题（⭐）**
1. 如何从私有仓库安装包？
   - 答案：先 `poetry source add` 添加源，然后 `poetry add`。
2. `develop = true` 的路径依赖有什么好处？
   - 答案：修改本地包代码后不需要重新安装，直接生效。

**进阶题（⭐⭐）**
1. primary、secondary、explicit 源优先级的区别？
   - 思考方向：primary 与 PyPI 一起搜索；secondary 补充；explicit 显式指定。
2. 什么时候用 Git 依赖而不是路径依赖？
   - 思考方向：跨项目跨机器；CI 环境；路径依赖只适合本地。

**实战题（⭐⭐⭐）**
- **背景**：公司有一个私有 PyPI 服务器，地址 https://pypi.internal.company.com。
- **需求**：配置项目使用私有源。
- **要求**：① 添加私有源；② 配置认证；③ 安装一个内部包；④ 确保公共包仍从 PyPI 下载。
- **验收标准**：内部包从私有源安装；公共包从 PyPI 安装。
- **提示**：用 primary 优先级，私有源和 PyPI 一起搜索。

---

## 十、与 Docker 集成

### 10.1 Dockerfile 最佳实践

```dockerfile
# Dockerfile - 多阶段构建，利用缓存优化
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装 Poetry
RUN pip install --no-cache-dir poetry==1.8.0

# 在 Docker 中不创建虚拟环境
RUN poetry config virtualenvs.create false

# 先复制依赖文件（利用 Docker 层缓存）
COPY pyproject.toml poetry.lock ./

# 只安装生产依赖（不安装 dev 组）
RUN poetry install --no-root --without dev --no-interaction

# 复制源码
COPY . .

# 安装项目本身
RUN poetry install --without dev --no-interaction

# 运行阶段
FROM python:3.12-slim

WORKDIR /app

# 从 builder 复制已安装的包
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# 运行应用
CMD ["uvicorn", "my_project.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 10.2 Docker 缓存优化

```dockerfile
# ❌ 不好的做法：每次 COPY . 都会让缓存失效
COPY . .
RUN poetry install

# ✅ 好的做法：先复制依赖文件，利用层缓存
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev --no-interaction
COPY . .
```

### 10.3 Docker Compose 集成

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data/

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

### 10.4 开发环境 Docker

```dockerfile
# Dockerfile.dev - 开发环境（包含 dev 依赖）
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.0
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction

COPY . .

# 开发模式：uvicorn --reload
CMD ["uvicorn", "my_project.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
```

### 10.5 Docker 多阶段构建完整示例

```dockerfile
# Dockerfile - 生产环境最佳实践

# ====== 构建阶段 ======
FROM python:3.12-slim AS builder

WORKDIR /app

# 系统依赖（构建时需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
RUN pip install --no-cache-dir poetry==1.8.0

# Docker 中不创建虚拟环境
RUN poetry config virtualenvs.create false

# 先复制依赖文件（层缓存）
COPY pyproject.toml poetry.lock ./

# 只安装生产依赖
RUN poetry install --no-root --without dev --no-interaction --no-ansi

# 复制源码并安装项目
COPY . .
RUN poetry install --without dev --no-interaction --no-ansi

# ====== 运行阶段 ======
FROM python:3.12-slim

WORKDIR /app

# 只复制必要的文件
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app/my_project /app/my_project
COPY --from=builder /app/README.md /app/

# 非 root 用户运行
RUN useradd -m appuser
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# 启动命令
CMD ["uvicorn", "my_project.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 10.6 .dockerignore 优化

```
# .dockerignore
.venv/
__pycache__/
*.pyc
.git/
.github/
tests/
docs/
htmlcov/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.DS_Store
*.md
!README.md
```

> ✅ 最佳实践：.dockerignore 排除不必要的文件，减小构建上下文大小。特别是 `.venv/` 和 `.git/` 目录很大，排除后构建速度显著提升。

### 10.7 Docker Compose 完整开发栈

```yaml
# docker-compose.yml - 完整开发环境
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/app
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=true
    volumes:
      - .:/app  # 源码挂载，支持 --reload
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 10.8 生产部署检查清单

```bash
# 生产部署前检查清单

# 1. 确认生产依赖
grep -A 100 '\[tool.poetry.dependencies\]' pyproject.toml | head -20

# 2. 确认没有开发依赖
poetry install --without dev --dry-run

# 3. 安全审计
poetry run pip-audit

# 4. 构建 Docker 镜像
docker build -t my-app:latest .

# 5. 测试镜像
docker run --rm -p 8000:8000 my-app:latest

# 6. 推送镜像
docker tag my-app:latest registry.company.com/my-app:latest
docker push registry.company.com/my-app:latest
```

### 10.9 Docker 中 Poetry 常见问题

```dockerfile
# 问题1：poetry install 后找不到命令
# 原因：virtualenvs.create false 但路径问题
# 解决：确保 PATH 正确
ENV PATH="/app/.venv/bin:$PATH"

# 问题2：poetry install 很慢
# 原因：每次 COPY . 后重新安装
# 解决：先 COPY 依赖文件
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev
COPY . .

# 问题3：pip 版本太旧
# 解决：先升级 pip
RUN pip install --upgrade pip

# 问题4：系统依赖缺失
# 某些 Python 包需要系统库（如 psycopg2 需要 libpq）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*
```

### 10.11 Docker 镜像大小优化

```dockerfile
# 基础镜像选择
# python:3.12-slim  ~150MB（推荐）
# python:3.12      ~1GB（不推荐用于生产）
# gcr.io/distroless/python3.12 ~50MB（最小化）

# 优化技巧：
# 1. 用 slim 基础镜像
FROM python:3.12-slim

# 2. 多阶段构建
# builder 阶段有 gcc 等构建工具
# 运行阶段只有运行时依赖

# 3. 清理 apt 缓存
RUN apt-get update && apt-get install -y xxx \
    && rm -rf /var/lib/apt/lists/*

# 4. 不安装推荐包
RUN apt-get install -y --no-install-recommends xxx

# 5. 用 .dockerignore 排除无关文件
```

```dockerfile
# distroless 最终镜像（无 shell，最安全）
FROM gcr.io/distroless/python3-debian12:nonroot
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app/my_project /app/my_project
WORKDIR /app
CMD ["python", "-m", "my_project.main"]
```

### 10.12 Docker 与 Poetry 版本对齐

```dockerfile
# Docker 中固定 Poetry 版本
# 确保本地和 CI 用相同版本

FROM python:3.12-slim

# 固定 Poetry 版本
RUN pip install --no-cache-dir poetry==1.8.0

# 验证
RUN poetry --version

# 这样确保：
# 1. 解析器版本一致
# 2. lock 文件格式一致
# 3. 行为一致
```

```bash
# 本地固定 Poetry 版本
# 用官方安装脚本时指定版本
curl -sSL https://install.python-poetry.org | python3 - --version 1.8.0
```

### 10.13 Docker Compose 生产配置

```yaml
# docker-compose.prod.yml - 生产环境
version: '3.8'

services:
  api:
    image: registry.company.com/my-app:latest
    restart: always
    ports:
      - "80:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/prod
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=info
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    restart: always
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: prod

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data

volumes:
  postgres_prod_data:
  redis_data:
```

> ❌ 常见坑点：Docker 中 Poetry 安装慢——通常是因为每次 COPY . 后重新安装所有依赖。正确做法是先 COPY pyproject.toml + poetry.lock，运行 install，再 COPY . 源码。这样只要依赖不变，Docker 层缓存就命中。

---

> 💡 **本章深度讲解**：Docker + Poetry 是 Python 后端服务的标准部署方案。关键优化点是利用 Docker 层缓存——先安装依赖，再复制源码，这样代码变更不会触发依赖重新安装。多阶段构建进一步减小最终镜像体积，只保留运行时需要的包。开发环境用独立的 Dockerfile，包含 dev 依赖和 --reload 模式。
>
> **📝 精简总结**：
> - 核心概念：多阶段构建、层缓存、virtualenvs.create false
> - 关键原理：先 COPY 依赖文件再 COPY 源码；builder 阶段安装，运行阶段复制
> - 常用操作：`poetry install --without dev --no-root`
> - 最佳实践：多阶段构建；利用层缓存；开发/生产用不同 Dockerfile
> - 常见坑点：COPY . 在 install 之前导致缓存失效
> - 面试高频：Docker 层缓存优化；virtualenvs.create false 的原因

### 🎯 梯度练习题

**基础题（⭐）**
1. Docker 中为什么 `virtualenvs.create false`？
   - 答案：容器内不需要虚拟环境，直接安装到系统 Python。
2. 如何利用 Docker 层缓存加速构建？
   - 答案：先 COPY pyproject.toml + poetry.lock，再 RUN poetry install，最后 COPY .。

**进阶题（⭐⭐）**
1. 为什么用多阶段构建？
   - 思考方向：减小最终镜像体积；builder 阶段有构建工具，运行阶段只有运行时。
2. `--no-root` 参数的作用？
   - 思考方向：不安装项目本身，只安装依赖。

**实战题（⭐⭐⭐）**
- **背景**：你的 FastAPI 项目需要 Docker 化部署。
- **需求**：编写生产级 Dockerfile。
- **要求**：① 多阶段构建；② 只安装生产依赖；③ 层缓存优化；④ 最终镜像 <200MB。
- **验收标准**：`docker build` 成功；`docker run` 启动服务；二次构建利用缓存。
- **提示**：用 `python:3.12-slim` 作为基础镜像。

---

## 十一、与 CI/CD 集成

### 11.1 GitHub Actions 基础

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Poetry
        run: pip install poetry==1.8.0

      - name: Install dependencies
        run: poetry install --no-interaction

      - name: Lint
        run: poetry run ruff check .

      - name: Type check
        run: poetry run mypy my_project

      - name: Test
        run: poetry run pytest --cov=my_project -v
```

### 11.2 多 Python 版本测试

```yaml
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
      - run: pip install poetry
      - run: poetry install --no-interaction
      - run: poetry run pytest -v
```

### 11.3 缓存优化

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: 'poetry'  # 自动缓存 Poetry 虚拟环境
          cache-dependency-path: poetry.lock

      - run: pip install poetry==1.8.0
      - run: poetry install --no-interaction
      - run: poetry run pytest -v
```

### 11.4 发布工作流

```yaml
# .github/workflows/release.yml
name: Release

on:
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Poetry
        run: pip install poetry==1.8.0

      - name: Build and publish
        env:
          POETRY_PYPI_TOKEN_PYPI: ${{ secrets.PYPI_TOKEN }}
        run: |
          poetry install --no-interaction
          poetry publish --build
```

### 11.5 GitLab CI

```yaml
# .gitlab-ci.yml
image: python:3.12

stages:
  - test
  - deploy

before_script:
  - pip install poetry==1.8.0
  - poetry config virtualenvs.create false
  - poetry install --no-interaction

test:
  stage: test
  script:
    - poetry run pytest -v
    - poetry run ruff check .

deploy:
  stage: deploy
  only:
    - main
  script:
    - poetry publish --build
```

### 11.6 完整的 GitHub Actions 工作流

```yaml
# .github/workflows/ci.yml - 完整 CI/CD 管道
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  POETRY_VERSION: "1.8.0"
  PYTHON_VERSION: "3.12"

jobs:
  # 代码质量检查
  lint-and-typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'poetry'

      - name: Install Poetry
        run: pip install poetry==${{ env.POETRY_VERSION }}

      - name: Install dependencies
        run: poetry install --no-interaction

      - name: Ruff lint
        run: poetry run ruff check .

      - name: Ruff format check
        run: poetry run ruff format --check .

      - name: Mypy type check
        run: poetry run mypy my_project --strict

  # 单元测试（多版本）
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
          cache: 'poetry'
          cache-dependency-path: poetry.lock

      - name: Install Poetry
        run: pip install poetry==${{ env.POETRY_VERSION }}

      - name: Install dependencies
        run: poetry install --no-interaction

      - name: Run tests
        run: poetry run pytest --cov=my_project --cov-report=xml -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  # 集成测试（需要数据库）
  integration-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'poetry'

      - run: pip install poetry==${{ env.POETRY_VERSION }}
      - run: poetry install --no-interaction

      - name: Integration tests
        run: poetry run pytest -m integration -v
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test

  # 发布（main 分支）
  publish:
    needs: [lint-and-typecheck, test, integration-test]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - run: pip install poetry==${{ env.POETRY_VERSION }}

      - name: Publish to PyPI
        env:
          POETRY_PYPI_TOKEN_PYPI: ${{ secrets.PYPI_TOKEN }}
        run: poetry publish --build
```

### 11.7 pre-commit 集成

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, types-requests]
```

```bash
# 安装 pre-commit
poetry add --group dev pre-commit
pre-commit install

# 手动运行所有钩子
pre-commit run --all-files

# 只检查暂存的文件
pre-commit run
```

### 11.8 缓存策略详解

```yaml
# GitHub Actions 中 Poetry 缓存详解
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # setup-python 自动缓存 Poetry 虚拟环境
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: 'poetry'
          cache-dependency-path: poetry.lock

      # 安装 Poetry
      - run: pip install poetry==1.8.0

      # 安装依赖（命中缓存时秒级完成）
      - run: poetry install --no-interaction

      # 运行测试
      - run: poetry run pytest -v
```

```python
# 缓存工作原理：
# 1. setup-python 读取 poetry.lock 的哈希
# 2. 如果哈希不变，从缓存恢复 .venv
# 3. 如果哈希变化（依赖更新），重新安装
# 4. 安装完成后自动保存新的缓存

# 缓存位置：
# Linux: ~/.cache/pypoetry/virtualenvs/
# macOS: ~/Library/Caches/pypoetry/virtualenvs/
```

### 11.9 发布自动化

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - "v*"  # 推送 v1.0.0 标签时触发

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: 'poetry'

      - run: pip install poetry==1.8.0
      - run: poetry install --no-interaction

      # 运行所有测试
      - run: poetry run pytest -v

      # 构建并发布
      - name: Publish to PyPI
        env:
          POETRY_PYPI_TOKEN_PYPI: ${{ secrets.PYPI_TOKEN }}
        run: poetry publish --build

      # 创建 GitHub Release
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
```

```bash
# 手动发布流程
# 1. 更新版本
poetry version minor

# 2. 提交版本变更
git add pyproject.toml
git commit -m "Bump version to 1.1.0"

# 3. 打标签
git tag v1.1.0

# 4. 推送标签（触发 CI 发布）
git push origin v1.1.0
```

### 11.10 多环境配置

```yaml
# .github/workflows/ci.yml
# 多环境部署策略

jobs:
  # 开发环境（每次 push）
  dev-deploy:
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: 'poetry'
      - run: pip install poetry==1.8.0
      - run: poetry install --no-interaction
      - name: Deploy to dev
        run: ./scripts/deploy-dev.sh
        env:
          ENV: development

  # 生产环境（打标签）
  prod-deploy:
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: 'poetry'
      - run: pip install poetry==1.8.0
      - run: poetry install --no-interaction --without dev
      - name: Deploy to production
        run: ./scripts/deploy-prod.sh
        env:
          ENV: production
```

### 11.11 CI 性能优化

```yaml
# 优化前：每次 CI 都安装所有依赖（5分钟）
- run: poetry install --no-interaction

# 优化后：缓存 + 并行（1分钟）
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
    cache: 'poetry'
    cache-dependency-path: poetry.lock
- run: poetry install --no-interaction

# 进一步优化：只安装需要的组
- run: poetry install --no-root --without docs --no-interaction

# 使用 GitHub Actions 的服务容器
# 数据库等服务用 services 定义，不用在 CI 中安装
```

### 11.12 CI 故障排查

```yaml
# CI 失败时的排查步骤

# 1. 查看 CI 日志
# GitHub Actions -> Failed job -> 查看日志

# 2. 本地复现
# 克隆仓库到干净目录
git clone <repo> /tmp/ci-debug
cd /tmp/ci-debug

# 安装 Poetry
pip install poetry==1.8.0

# 安装依赖
poetry install --no-interaction

# 运行失败的命令
poetry run pytest -v

# 3. 常见原因：
# - Python 版本不匹配
# - Poetry 版本不一致
# - 缓存问题（清除重试）
# - 网络问题（依赖下载失败）
# - 环境变量缺失
```

### 11.13 CI 安全扫描

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 1'  # 每周一扫描
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: 'poetry'

      - run: pip install poetry==1.8.0
      - run: poetry install --no-interaction

      - name: Pip audit (dependency vulnerabilities)
        run: poetry run pip-audit

      - name: Bandit (security lint)
        run: poetry run bandit -r my_project/

      - name: Safety check
        run: poetry run safety check
```

---

> 💡 **本章深度讲解**：CI/CD 集成让 Poetry 的依赖管理价值最大化——lock 文件确保 CI 环境和开发环境完全一致。缓存 Poetry 虚拟环境可以大幅加速 CI 执行。发布工作流自动构建和上传包，减少手动操作。多 Python 版本矩阵测试确保包的兼容性。
>
> **📝 精简总结**：
> - 核心概念：GitHub Actions、矩阵测试、缓存、自动发布
> - 关键原理：lock 文件确保 CI 一致性；cache 加速；token 认证
> - 常用操作：`poetry install --no-interaction`；`poetry publish --build`
> - 最佳实践：缓存 Poetry 环境；多版本测试；自动发布
> - 常见坑点：未设置 POETRY_PYPI_TOKEN_PYPI；缓存未配置
> - 面试高频：CI 中 Poetry 工作流；缓存策略；自动化发布

### 🎯 梯度练习题

**基础题（⭐）**
1. CI 中为什么用 `poetry install` 而不是 `poetry update`？
   - 答案：install 读 lock 文件确保一致；update 重新解析可能引入新版本。
2. 如何在 GitHub Actions 中缓存 Poetry 环境？
   - 答案：`setup-python` 的 `cache: 'poetry'` 选项。

**进阶题（⭐⭐）**
1. 为什么 CI 中用 `--no-interaction`？
   - 思考方向：CI 环境没有交互终端；防止命令等待输入。
2. 如何自动发布到 PyPI？
   - 思考方向：release 事件触发；POETRY_PYPI_TOKEN_PYPI 环境变量。

**实战题（⭐⭐⭐）**
- **背景**：你的项目需要 CI 跑 lint + type check + test。
- **需求**：编写完整的 CI 工作流。
- **要求**：① 三个 job 并行；② 多 Python 版本测试；③ 覆盖率上传；④ main 分支自动发布。
- **验收标准**：PR 触发 CI；main 合并后自动发布。
- **提示**：用 GitHub Actions matrix 和 needs。

---

## 十二、常见问题与故障排查

### 12.1 常见问题速查表

| 问题现象 | 原因 | 解决方案 |
|---------|------|---------|
| `poetry install` 很慢 | 默认 PyPI 源在国外 | 配置国内镜像源 |
| `SolverProblemError` 版本冲突 | 依赖要求不兼容版本 | `poetry show --tree` 找冲突；调整约束 |
| `command not found: poetry` | PATH 未配置 | 将 Poetry bin 目录加入 PATH |
| 虚拟环境找不到包 | 安装到了错误的 Python | `poetry env list` 查看；`poetry env use` 指定 |
| `poetry.lock` Git 冲突 | 多人同时改依赖 | `poetry lock --no-update` 重新生成 |
| Docker 构建慢 | 每次重新安装依赖 | 先 COPY pyproject.toml + lock |
| `poetry run` 找不到命令 | scripts 未定义 | 在 `[tool.poetry.scripts]` 中定义 |
| 开发依赖部署到生产 | 忘了 `--without dev` | 生产用 `poetry install --without dev` |
| 私有包安装失败 | 私有源未配置/认证失败 | `poetry source add` + `poetry config pypi-token` |
| Poetry 版本不一致 | 团队用不同版本 | CI 中固定 Poetry 版本 |
| 依赖解析卡住 | 依赖图复杂 | 缩小版本约束；升级 Poetry；清除缓存 |
| `KeyError: 'foo'` | 私有源认证问题 | 检查 token 配置 |
| 安装后 import 失败 | 包未安装到虚拟环境 | `poetry install` 确保项目本身安装 |
| `--root` 相关错误 | pyproject.toml 不在当前目录 | 在项目根目录运行 Poetry |

### 12.2 故障排查流程

```bash
# 1. 检查 Poetry 版本
poetry --version

# 2. 检查配置
poetry config --list

# 3. 检查虚拟环境
poetry env info
poetry env list

# 4. 检查依赖状态
poetry show
poetry show --tree
poetry show --outdated

# 5. 清除缓存重试
poetry cache clear --all pypi
poetry lock --no-update
poetry install

# 6. 调试模式
poetry -vvv install  # 详细输出
```

### 12.3 依赖解析慢的解决

```bash
# 问题：poetry install 卡住很久

# 解决1：缩小版本约束范围
# 不要用 * 或 >=0
# 用 ^x.y.z 明确范围

# 解决2：清除缓存
poetry cache clear --all pypi

# 解决3：升级 Poetry
pip install --upgrade poetry

# 解决4：并行安装
poetry config installer.max-workers 10

# 解决5：使用 --no-cache 临时跳过缓存
poetry install --no-cache
```

### 12.4 lock 文件冲突处理

```bash
# 场景：多人同时修改 pyproject.toml，poetry.lock 产生 Git 冲突

# 解决1：接受 pyproject.toml 的合并结果，重新生成 lock
git checkout --theirs pyproject.toml
poetry lock --no-update
git add poetry.lock

# 解决2：接受某一方的 lock，然后 install
git checkout --theirs poetry.lock
poetry install

# 解决3：删除 lock 重新生成（最后手段）
rm poetry.lock
poetry lock
```

### 12.5 网络问题排查

```bash
# 问题：poetry install 下载超时

# 解决1：配置国内镜像源
poetry source add --priority=primary tsinghua https://pypi.tuna.tsinghua.edu.cn/simple

# 解决2：使用阿里云镜像
poetry source add --priority=primary aliyun https://mirrors.aliyun.com/pypi/simple/

# 解决3：设置超时
poetry config installer.timeout 60

# 解决4：使用代理
export HTTP_PROXY=http://proxy:8080
export HTTPS_PROXY=http://proxy:8080
poetry install
```

### 12.6 Python 版本问题

```bash
# 问题：当前 Python 版本不满足 pyproject.toml 中的约束

# 错误示例：
# The currently activated Python version 3.9.7 is not supported by the project
# (^3.10).

# 解决1：安装更高版本 Python
# 使用 pyenv 或 conda 安装 Python 3.12
pyenv install 3.12
poetry env use $(pyenv which python3.12)

# 解决2：放宽 pyproject.toml 中的约束
# [tool.poetry.dependencies]
# python = ">=3.9"  # 放宽到 3.9+

# 解决3：用 conda 管理 Python 版本
conda create -n my-project python=3.12
conda activate my-project
poetry env use python
```

### 12.7 安装失败排查

```bash
# 问题：poetry install 失败

# 1. 查看详细错误
poetry -vvv install  # 详细输出

# 2. 清除缓存
poetry cache clear --all pypi

# 3. 删除虚拟环境重新创建
poetry env remove --all
rm -f poetry.lock
poetry install

# 4. 检查网络
curl -I https://pypi.org/simple/

# 5. 检查磁盘空间
df -h  # Linux/Mac
# 确保有足够空间安装包

# 6. 检查 pip 版本
pip install --upgrade pip
```

### 12.8 常见错误信息速查

| 错误信息 | 含义 | 解决 |
|---------|------|------|
| `SolverProblemError` | 依赖冲突 | 查看依赖树，调整版本约束 |
| `NoCompatiblePythonVersionFound` | Python 版本不满足 | 安装正确版本或放宽约束 |
| `PackageNotFound` | 包不存在 | 检查包名拼写；检查源配置 |
| `InvalidVersion` | 版本号格式错误 | 检查 pyproject.toml 中的版本字符串 |
| `HTTP 401` | 认证失败 | 配置私有源 token |
| `HTTP 403` | 权限不足 | 检查 token 权限 |
| `LockFileNotFresh` | lock 文件过期 | 运行 `poetry lock` |
| `CurrentPythonVersionIncompatible` | Python 版本不匹配 | `poetry env use` 切换 |
| `FailedToOpenFile` | 文件权限 | 检查文件权限和磁盘空间 |

### 12.9 性能问题排查

```bash
# 问题：poetry install 很慢

# 1. 查看详细日志
poetry -vvv install 2>&1 | head -50

# 2. 检查网络
time curl -I https://pypi.org/simple/

# 3. 配置国内镜像
poetry source add --priority=primary tsinghua https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 并行安装
poetry config installer.max-workers 10

# 5. 检查缓存
poetry cache list

# 6. 清除缓存重新安装
poetry cache clear --all pypi
poetry install
```

### 12.10 版本升级指南

```bash
# 升级 Poetry 自身

# 官方安装方式安装的 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# pip 安装的 Poetry
pip install --upgrade poetry

# 查看版本
poetry --version

# 从 1.x 升级到 2.x（注意 breaking changes）
# 1. 阅读迁移指南
# 2. 在测试环境验证
# 3. 更新 CI 中的 Poetry 版本
# 4. 重新生成 lock 文件
```

### 12.11 数据迁移与备份

```bash
# 备份当前环境
poetry export -f requirements.txt -o backup-requirements.txt

# 导出完整依赖树
poetry show --tree > dependency-tree.txt

# 备份 pyproject.toml
cp pyproject.toml pyproject.toml.backup

# 恢复
# 1. 从备份恢复 pyproject.toml
cp pyproject.toml.backup pyproject.toml

# 2. 删除旧 lock
rm -f poetry.lock

# 3. 重新安装
poetry install
```

### 12.12 常见场景排查指南

```bash
# 场景1：新克隆项目，poetry install 失败
# 步骤：
# 1. 检查 Python 版本
python3 --version
# 2. 检查 pyproject.toml 中的 python 约束
grep python pyproject.toml
# 3. 如果版本不匹配，安装正确版本
# 4. 清除缓存
poetry cache clear --all pypi
# 5. 重新安装
rm -rf .venv poetry.lock
poetry install

# 场景2：poetry update 后测试失败
# 步骤：
# 1. 查看更新了什么
git diff poetry.lock
# 2. 查看新版本的 CHANGELOG
# 3. 回滚到上一个版本
git checkout HEAD~1 poetry.lock pyproject.toml
poetry install
# 4. 逐个升级找到问题包
poetry update problem-package

# 场景3：CI 通过但本地失败
# 步骤：
# 1. 检查 Python 版本是否一致
python3 --version
# 2. 检查 Poetry 版本是否一致
poetry --version
# 3. 删除本地 .venv 重新安装
poetry env remove --all
poetry install
# 4. 检查环境变量
env | grep -i python
```

### 12.13 Poetry 升级常见问题

```bash
# 从 Poetry 1.x 升级到 2.x

# 1. 备份
cp pyproject.toml pyproject.toml.bak
cp poetry.lock poetry.lock.bak

# 2. 升级 Poetry
pip install --upgrade poetry

# 3. 检查版本
poetry --version

# 4. 验证配置
poetry check

# 5. 重新生成 lock
rm poetry.lock
poetry lock

# 6. 安装
poetry install

# 注意事项：
# - Poetry 2.x 有一些 breaking changes
# - 依赖组语法可能变化
# - 建议先在测试环境验证
```

### 12.14 Windows 特殊问题

```powershell
# Windows 上 Poetry 的常见问题

# 1. poetry 命令找不到
# 将 %APPDATA%\Python\Scripts 加入 PATH

# 2. 路径太长
# Windows 默认路径长度限制 260 字符
# 解决：启用长路径支持
# 注册表: HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled = 1

# 3. 权限问题
# 不要用管理员运行 poetry
# 普通用户即可

# 4. Git Bash 兼容性
# poetry shell 在 Git Bash 中可能有问题
# 用 poetry run 替代
```

### 12.15 macOS 特殊问题

```bash
# macOS 上 Poetry 的常见问题

# 1. 安装路径
# 默认安装在 ~/Library/Application Support/pypoetry/
# 确保 ~/.local/bin 在 PATH 中

# 2. Python 版本管理
# 推荐用 pyenv 管理 Python 版本
pyenv install 3.12
poetry env use $(pyenv which python3.12)

# 3. Homebrew 冲突
# 如果用 brew 安装 Python，可能与 pyenv 冲突
# 统一用 pyenv 管理

# 4. 磁盘空间
# Poetry 缓存在 ~/Library/Caches/pypoetry/
# 定期清理：poetry cache clear --all pypi
```

### 12.16 Linux 特殊问题

```bash
# Linux 上 Poetry 的常见问题

# 1. PEP 668 externally-managed-environment
# 某些 Linux 发行版（如 Ubuntu 24.04）禁止直接 pip install
# 解决：用 pipx 安装 Poetry
pipx install poetry

# 2. 权限问题
# 不要用 sudo 运行 poetry
# 普通用户即可，.venv 在项目目录

# 3. 系统 Python 版本太旧
# 用 deadsnakes PPA 安装新版本
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.12 python3.12-venv
```

### 12.17 依赖树分析技巧

```bash
# 查看完整依赖树
poetry show --tree

# 只看某个包的依赖
poetry show fastapi --tree

# 查看依赖来源（谁依赖了它）
poetry show --why starlette
# 输出：fastapi depends on starlette

# 查看间接依赖
poetry show --tree | grep -E "^\s+\w"

# 统计依赖数量
poetry show | wc -l

# 查看最大的包
poetry show --tree | sort -r | head -20
```

### 12.18 依赖冲突分析实战

```bash
# 示例冲突场景：
# my-project 需要 django>=4.0
# my-project 需要 django-cors-headers==3.7.0
# django-cors-headers==3.7.0 要求 django<4.0

# 排查步骤：
# 1. 查看依赖树
poetry show --tree
# 找到冲突的两个包

# 2. 查看包详情
poetry show django-cors-headers
# 看它要求的 Django 版本

# 3. 解决方案：
# a. 升级 django-cors-headers 到支持 Django 4 的版本
poetry add "django-cors-headers>=4.0"

# b. 或降低 Django 版本
poetry add "django>=3.2,<4.0"

# c. 或锁定冲突的传递依赖
# 在 pyproject.toml 中添加
# django = "3.2.0"
```

### 12.19 常见错误代码速查

| 错误代码 | 含义 | 解决 |
|---------|------|------|
| `SolverProblemError` | 依赖解析失败 | 查看依赖树，调整约束 |
| `PackageNotFound` | 包不存在 | 检查包名拼写 |
| `InvalidVersion` | 版本号格式错误 | 检查版本字符串 |
| `NoCompatiblePythonVersion` | Python 版本不满足 | 安装正确版本 |
| `LockFileCorrupted` | lock 文件损坏 | 删除 lock 重新生成 |
| `CacheError` | 缓存损坏 | `poetry cache clear --all pypi` |
| `HTTPError` | 网络错误 | 检查网络/代理 |
| `AuthenticationError` | 认证失败 | 检查 token 配置 |
| `PermissionError` | 文件权限 | 检查目录权限 |
| `VirtualenvNotFound` | 虚拟环境不存在 | `poetry install` 创建 |

### 12.20 依赖更新检查清单

```bash
# 定期依赖更新检查清单

# 1. 查看可更新的包
poetry show --outdated

# 2. 安全扫描
poetry run pip-audit

# 3. 测试更新
poetry update --dry-run  # 预览
poetry update            # 实际更新

# 4. 运行测试
poetry run pytest -v

# 5. 运行 lint
poetry run ruff check .
poetry run mypy my_project

# 6. 提交
git add pyproject.toml poetry.lock
git commit -m "Update dependencies"

# 7. 监控生产环境
# 观察更新后是否有异常
```

### 12.21 团队协作中的依赖管理

```markdown
# 团队依赖管理规范

## 添加新依赖的流程
1. 在 PR 中说明为什么需要这个包
2. 说明替代方案和选择理由
3. 评估许可证兼容性
4. 评估维护活跃度
5. 说明版本约束选择（^ 还是 ==）
6. Code Review 确认

## 更新依赖的流程
1. 每月一次批量更新
2. 在独立分支进行
3. 运行完整测试套件
4. 观察一周后合并
5. 重大版本升级需要单独评审

## 禁止事项
- 禁止未经评审添加新依赖
- 禁止在 CI 中用 poetry update
- 禁止提交时忘记 poetry.lock
- 禁止将开发依赖加入生产组
```

### 12.22 从 pip-tools 迁移到 Poetry

```bash
# pip-tools 项目迁移到 Poetry

# 1. 读取 requirements.in 中的依赖
cat requirements.in

# 2. 初始化 Poetry
poetry init

# 3. 逐行添加生产依赖
poetry add fastapi uvicorn sqlalchemy

# 4. 添加开发依赖
poetry add --group dev pytest ruff

# 5. 删除旧文件
rm requirements.in requirements.txt requirements-dev.txt

# 6. 生成新 lock 文件
poetry lock

# 7. 验证
poetry install
poetry show --tree
```

### 12.23 常见问题快速诊断表

| 症状 | 第一步检查 | 第二步 | 第三步 |
|------|-----------|--------|--------|
| install 失败 | `poetry --version` | 清除缓存 | 删除 lock 重建 |
| 冲突错误 | `poetry show --tree` | 调整约束 | 锁定传递依赖 |
| 找不到包 | `poetry env info` | `poetry run pip list` | 重新 install |
| 版本不匹配 | `python3 --version` | `poetry env use` | 重新 install |
| CI 失败 | 本地复现 | 检查版本一致性 | 检查环境变量 |
| Docker 慢 | 层缓存 | 先 COPY 依赖 | 用 slim 镜像 |

---

> 💡 **本章深度讲解**：故障排查是 Poetry 日常使用中最常遇到的问题。核心思路是"二分法"——先确定是环境问题还是代码问题，再逐步缩小范围。`poetry show --tree` 和 `poetry -vvv` 是最有用的两个排查工具。记住：大多数问题都可以通过"清缓存、删 lock、重新安装"解决。
>
> **📝 精简总结**：
> - 核心概念：SolverProblemError、lock 冲突、缓存清理
> - 关键原理：依赖树定位冲突；lock 重新生成；环境一致性
> - 常用操作：`poetry show --tree`；`poetry cache clear`；`poetry lock --no-update`
> - 最佳实践：固定 Poetry 版本；CI 用 install 不用 update
> - 常见坑点：CI 版本不一致；lock 冲突不会解
> - 面试高频：冲突排查流程；lock 文件冲突处理

---

> 💡 **本章深度讲解**：依赖管理的大多数问题都可以通过"看日志 + 查依赖树 + 清缓存"三步解决。`poetry show --tree` 是最有用的排查工具——它显示完整的依赖链，让你看到哪个包在要求哪个版本。lock 文件冲突是团队协作中的常见问题，`poetry lock --no-update` 是标准解法。
>
> **📝 精简总结**：
> - 核心概念：SolverProblemError、lock 冲突、缓存清理
> - 关键原理：依赖树定位冲突；lock 重新生成；缓存清除
> - 常用操作：`poetry show --tree`；`poetry cache clear`；`poetry lock --no-update`
> - 最佳实践：定期清缓存；固定 Poetry 版本；缩小版本约束
> - 常见坑点：CI 中 Poetry 版本不一致；lock 冲突不知道怎么解
> - 面试高频：SolverProblemError 排查；lock 文件冲突处理

### 🎯 梯度练习题

**基础题（⭐）**
1. 遇到 SolverProblemError 第一步做什么？
   - 答案：`poetry show --tree` 查看依赖树找到冲突来源。
2. poetry.lock 的 Git 冲突怎么处理？
   - 答案：`poetry lock --no-update` 重新生成。

**进阶题（⭐⭐）**
1. 为什么依赖解析会变慢？
   - 思考方向：依赖图复杂；版本约束宽松；缓存被污染。
2. 为什么团队要固定 Poetry 版本？
   - 思考方向：不同版本的解析器行为不同；lock 文件格式可能不同。

**实战题（⭐⭐⭐）**
- **背景**：CI 中 `poetry install` 偶尔失败，但本地正常。
- **需求**：排查 CI 环境差异。
- **要求**：① 检查 Python 版本；② 检查 Poetry 版本；③ 检查 lock 文件是否一致；④ 检查网络/镜像源。
- **验收标准**：CI 稳定通过；找到根因并修复。
- **提示**：CI 中固定 Poetry 版本；用 `poetry install --no-root` 减少变量。

---

## 十三、最佳实践与常见坑点

### 13.1 依赖管理最佳实践

| 实践 | 说明 | 示例 |
|------|------|------|
| **提交 poetry.lock** | 确保所有环境一致 | Git 提交 lock 文件 |
| **使用 ^ 版本约束** | 允许兼容更新 | `fastapi = "^0.100.0"` |
| **分离 dev/prod 依赖** | 生产不装开发工具 | `[tool.poetry.group.dev.dependencies]` |
| **定期更新依赖** | 获取安全补丁 | `poetry update` 每月一次 |
| **最小化依赖** | 移除未使用的包 | `poetry show --tree` 审查 |
| **用 extras** | 可选功能按需安装 | `sqlalchemy[asyncio]` |
| **锁定间接依赖** | 安全漏洞时强制版本 | `starlette = "0.27.0"` |

### 13.2 项目结构最佳实践

```bash
my-project/
├── pyproject.toml       # ✅ 唯一的配置入口
├── poetry.lock          # ✅ 提交 Git
├── README.md
├── .venv/               # ❌ 不提交 Git
├── .gitignore
├── src/                 # 或 my_project/
│   ├── __init__.py
│   ├── main.py
│   └── utils/
└── tests/
    ├── conftest.py
    └── test_main.py
```

### 13.3 常见坑点汇总

| 坑点 | 现象 | 原因 | 解决方案 |
|------|------|------|---------|
| lock 不提交 | 团队成员环境不一致 | poetry.lock 在 .gitignore | 从 .gitignore 移除 poetry.lock |
| 过度宽松约束 | `pkg = "*"` 导致不可预测更新 | 图省事 | 用 `^` 约束明确范围 |
| 开发依赖进生产 | 生产装了 pytest 等工具 | 忘了 --without dev | 生产用 `--without dev,test,docs` |
| 随意锁定间接依赖 | 依赖更新困难 | 过度保护 | 只在必要时锁定 |
| 不更新依赖 | 安全漏洞累积 | 怕出问题 | 每月 `poetry update` + CI 测试 |
| poetry 命令找不到 | PATH 未配置 | 安装后未重启终端 | 将 ~/.local/bin 加入 PATH |
| 缓存污染 | 解析结果不一致 | 旧缓存 | `poetry cache clear --all pypi` |
| 多版本混乱 | 不同成员用不同 Poetry | 未固定版本 | CI 中固定 Poetry 版本 |
| 忘记 .venv | 在全局 Python 安装 | 未设置 in-project | `poetry config virtualenvs.in-project true` |
| Docker 缓存失效 | 每次重新安装依赖 | COPY . 在 install 之前 | 先 COPY 依赖文件 |
| 无版本约束说明 | 不知道为什么锁某个版本 | 随意锁定 | 添加注释说明原因 |
| CI 中用 update | CI 结果不确定 | 图省事 | CI 用 install，不用 update |
| Python 版本不匹配 | 虚拟环境用了错误 Python | pyproject.toml 约束不对 | `poetry env use python3.12` |
| 私有包认证失败 | token 未配置或过期 | 环境变量缺失 | `poetry config pypi-token` |
| 磁盘空间不足 | .venv 累积 | 多项目未清理 | 定期清理不用的虚拟环境 |

### 13.4 团队协作规范

```markdown
# 团队 Poetry 规范（TEAM_POETRY_GUIDE.md）

## 必须遵守
1. 所有项目使用 Poetry 管理依赖
2. poetry.lock 必须提交到 Git
3. 生产环境用 `poetry install --without dev`
4. CI 中固定 Poetry 版本（1.8.x）
5. 新依赖必须通过 code review 添加

## 推荐做法
1. 生产依赖用 ^ 约束
2. 工具链依赖（ruff/mypy）用精确版本
3. 定期（每月）运行 `poetry update`
4. 用 `poetry show --outdated` 检查可更新
5. 安全漏洞用 `pip-audit` 扫描

## 禁止
1. 禁止在 CI 中用 `poetry update`
2. 禁止随意锁定传递依赖
3. 禁止在 .gitignore 中排除 poetry.lock
4. 禁止使用 `pip install` 直接安装到项目环境
```

### 13.5 依赖审查清单

```bash
# 每次添加新依赖时检查：
# 1. 是否真的需要？能否自己实现？
# 2. 包的维护状态？最近有更新吗？
# 3. 许可证是否兼容？
# 4. 安全记录？有没有已知漏洞？
# 5. 依赖数量？会不会引入很多传递依赖？
# 6. 性能影响？启动时间？内存占用？

# 审查工具
poetry show --tree          # 查看依赖树
poetry show <package>       # 查看包详情
poetry run pip-audit        # 安全扫描
poetry run pip-licenses     # 许可证检查
```

### 13.6 性能优化

```bash
# 1. 并行安装
poetry config installer.max-workers 10

# 2. 全局缓存（减少重复下载）
poetry config cache-dir ~/.cache/pypoetry

# 3. 使用国内镜像
poetry source add --priority=primary tsinghua https://pypi.tuna.tsinghua.edu.cn/simple

# 4. CI 中缓存虚拟环境
# GitHub Actions:
#   cache: 'poetry'

# 5. 最小化依赖
# 定期审查 poetry show --tree，移除未使用的包
```

### 13.7 安全最佳实践

```bash
# 1. 定期安全扫描
poetry add --group dev pip-audit
poetry run pip-audit

# 2. 最小权限原则
# 生产环境只安装必要的包
poetry install --without dev,docs

# 3. 锁定依赖版本
# 不要用 * 或 >=0
# 用 ^ 或精确版本

# 4. 验证包哈希
# poetry.lock 自动记录哈希
# 安装时自动验证（防止供应链攻击）

# 5. 使用私有镜像
# 企业内网通过私有镜像代理
# 不直接连接公共 PyPI
```

### 13.8 可维护性最佳实践

```toml
# pyproject.toml 中添加注释说明依赖原因
[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.104.0"       # Web 框架
sqlalchemy = "^2.0"         # ORM
# starlette 锁定：修复 CVE-2023-xxx
starlette = "0.27.0"
```

```python
# 依赖更新记录（CHANGELOG.md）
## [1.2.0] - 2026-09-10
### Changed
- Upgraded fastapi from 0.100 to 0.104
- Upgraded pydantic from 2.0 to 2.5

### Fixed
- Locked starlette to 0.27.0 (security fix)
```

### 13.9 常见 anti-pattern

```python
# ❌ Anti-pattern 1：requirements.txt 和 pyproject.toml 并存
# 问题：两个文件可能不同步
# 解决：只用 pyproject.toml，删除 requirements.txt

# ❌ Anti-pattern 2：所有依赖用 *
fastapi = "*"
# 问题：不可预测的更新
# 解决：用 ^ 约束

# ❌ Anti-pattern 3：开发依赖和生产依赖混在一起
[tool.poetry.dependencies]
pytest = "^7.4"  # 不应该在这里
# 解决：用 [tool.poetry.group.dev.dependencies]

# ❌ Anti-pattern 4：poetry.lock 不提交 Git
# 问题：团队成员环境不一致
# 解决：提交 poetry.lock

# ❌ Anti-pattern 5：CI 中用 poetry update
# 问题：CI 结果不确定
# 解决：CI 用 poetry install
```

### 13.10 依赖迁移策略

```bash
# 从一个库迁移到另一个库的步骤
# 例如：从 requests 迁移到 httpx

# 1. 安装新库
poetry add httpx

# 2. 逐个模块迁移
# 修改 import 和调用

# 3. 运行测试确保无问题
poetry run pytest

# 4. 移除旧库
poetry remove requests

# 5. 提交
git add pyproject.toml poetry.lock
git commit -m "Migrate from requests to httpx"
```

### 13.11 版本升级检查清单

```bash
# 大版本升级检查清单（如 Django 4→5）

# 1. 阅读官方迁移指南
# 2. 查看 deprecated features
# 3. 创建升级分支
git checkout -b upgrade/django-5

# 4. 升级
poetry add "django@^5.0"

# 5. 运行测试
poetry run pytest

# 6. 修复兼容性问题
# 7. 代码审查
# 8. 合并
```

### 13.12 依赖卫生检查

```bash
# 定期运行的检查命令

# 1. 查看过时依赖
poetry show --outdated

# 2. 安全扫描
poetry run pip-audit

# 3. 许可证检查
poetry run pip-licenses

# 4. 依赖树审查
poetry show --tree | wc -l  # 依赖数量
poetry show --tree | grep "^\w"  # 直接依赖

# 5. 检查未使用的依赖
# 用 pyflake 或 vulture
poetry run vulture my_project
```

### 13.13 文档与资源

```markdown
# 推荐学习资源

## 官方文档
- Poetry 官方文档：https://python-poetry.org/docs/
- PEP 621：https://peps.python.org/pep-0621/
- SemVer：https://semver.org/

## 博客文章
- "Why you should use Poetry"
- "Migrating from requirements.txt to Poetry"
- "Poetry best practices"

## 视频教程
- "Python Poetry Tutorial for Beginners"
- "Poetry Deep Dive"

## 社区
- Poetry GitHub Discussions
- Python Discord #packaging 频道
```

### 13.14 快速参考卡片

```
常用命令：
  poetry new <name>      # 新项目
  poetry init             # 初始化现有项目
  poetry install          # 安装所有依赖
  poetry add <pkg>        # 添加生产依赖
  poetry add --group dev <pkg>  # 添加开发依赖
  poetry remove <pkg>     # 移除依赖
  poetry update            # 更新所有依赖
  poetry show --tree       # 依赖树
  poetry shell             # 激活虚拟环境
  poetry run <cmd>         # 在虚拟环境中执行
  poetry build             # 构建分发包
  poetry publish           # 发布到 PyPI

关键配置：
  virtualenvs.in-project = true  # .venv 在项目内
  python = "^3.12"              # Python 版本约束
  [tool.poetry.group.dev.dependencies]  # 开发依赖组

版本约束：
  ^1.2.3  # >=1.2.3, <2.0.0
  ~1.2.3  # >=1.2.3, <1.3.0
  ==1.2.3 # 精确版本
```

### 与其他工具的对比速查

| 功能 | Poetry | pip+venv | conda | pip-tools |
|------|--------|----------|-------|-----------|
| 依赖声明 | pyproject.toml | requirements.txt | environment.yml | requirements.in |
| 锁文件 | poetry.lock | 无 | environment.lock | requirements.txt |
| 虚拟环境 | 内置 | 手动 | 内置 | 手动 |
| 打包发布 | 内置 | setup.py | 无 | 无 |
| 依赖解析 | PubGrub | pip | conda solver | pip |
| 学习曲线 | 中 | 低 | 中 | 高 |
| 推荐 | 强烈推荐 | 不推荐新项目 | 数据科学 | 可替代 |

### 版本约束决策速查

| 场景 | 推荐约束 | 示例 |
|------|---------|------|
| 生产框架依赖 | ^ | fastapi = "^0.104" |
| 工具链依赖 | == | ruff = "0.1.6" |
| 库项目依赖 | ~ | requests = "~2.31" |
| 安全补丁需要 | >= | urllib3 = ">=2.0.7" |
| 完全锁定 | == | numpy = "1.26.2" |
| 宽松允许 | * | devtools = "*" |

### Docker 部署速查

```dockerfile
# 最小化 Dockerfile
FROM python:3.12-slim
RUN pip install poetry==1.8.0
RUN poetry config virtualenvs.create false
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev --no-interaction
COPY . .
CMD ["uvicorn", "my_project.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 13.4 面试高频考点汇总

> 🎯 **面试考点 1**：poetry.lock 应该提交到 Git 吗？
> 应用项目应该提交（确保环境一致）；库项目通常不提交（让用户选择兼容版本）。

> 🎯 **面试考点 2**：`^` 和 `~` 版本约束的区别？
> `^` 允许次版本和补丁更新（不改变最左非零位）；`~` 只允许补丁更新。

> 🎯 **面试考点 3**：poetry install 和 poetry update 的区别？
> install 读 lock 文件精确安装；update 重新解析依赖并更新 lock。

> 🎯 **面试考点 4**：如何解决依赖冲突？
> `poetry show --tree` 找冲突源；调整版本约束；必要时锁定传递依赖。

> 🎯 **面试考点 5**：Docker 中 Poetry 的最佳实践？
> 多阶段构建；virtualenvs.create false；先 COPY 依赖文件利用层缓存；--without dev。

> 🎯 **面试考点 6**：pyproject.toml 相比 requirements.txt 的优势？
> 结构化；区分直接/间接依赖；版本约束语义；集中管理元数据；依赖分组。

> 🎯 **面试考点 7**：什么是依赖组？如何使用？
> 按用途分组管理依赖（dev/test/docs/prod）；`poetry install --without dev` 排除。

> 🎯 **面试考点 8**：如何从 requirements.txt 迁移到 Poetry？
> `poetry init` 初始化；逐行 `poetry add`；删除旧文件；`poetry install`。

> 🎯 **面试考点 9**：Poetry 的依赖解析器用什么算法？
> PubGrub 算法，类似 PubGrub 版本求解器，高效求解依赖图。

> 🎯 **面试考点 10**：为什么 CI 中要固定 Poetry 版本？
> 不同版本的解析器可能产生不同的 lock 结果；确保一致性。

### 13.5 进阶学习资源

- [Poetry 官方文档](https://python-poetry.org/docs/) — 最权威参考
- [PEP 621 — pyproject.toml](https://peps.python.org/pep-0621/) — 标准定义
- [Semantic Versioning](https://semver.org/) — 语义化版本规范
- 《Python Packaging User Guide》— Python 打包官方指南

---

> 💡 **本章深度讲解**：最佳实践和坑点是从实际项目中总结的经验。核心原则是"可复现"——lock 文件提交 Git、CI 用 install 不用 update、固定 Poetry 版本。另一个原则是"最小化"——只安装需要的依赖，生产环境排除开发工具。掌握这些原则后，依赖管理从"玄学"变成可预测的工程实践。
>
> **📝 精简总结**：
> - 核心概念：可复现性、最小依赖、语义化版本
> - 关键原理：lock 文件锁定；依赖分组；层缓存
> - 常用操作：`poetry show --tree`；`poetry update`；`--without dev`
> - 最佳实践：提交 lock；生产排除 dev；定期更新
> - 常见坑点：lock 不提交；开发依赖进生产；Docker 缓存失效
> - 面试高频：lock 文件；^/~ 约束；install vs update

### 🎯 梯度练习题

**基础题（⭐）**
1. 生产环境为什么要用 `--without dev`？
   - 答案：不安装开发工具（pytest/ruff 等），减小镜像体积。
2. 为什么要定期 `poetry update`？
   - 答案：获取安全补丁和 bug 修复。

**进阶题（⭐⭐）**
1. 为什么不应该随意锁定间接依赖版本？
   - 思考方向：阻碍正常更新；可能导致解析变慢；安全漏洞修复时需要升级。
2. 应用项目和库项目在 lock 文件策略上有什么区别？
   - 思考方向：应用追求可复现（提交 lock）；库追求兼容性（不提交 lock）。

**实战题（⭐⭐⭐）**
- **背景**：你的项目 6 个月没更新依赖，现在有大量安全漏洞。
- **需求**：安全地更新所有依赖。
- **要求**：① `poetry update` 更新；② 运行所有测试；③ 检查 breaking changes；④ 分批提交（不要一次全改）。
- **验收标准**：所有测试通过；没有 breaking change；依赖是最新兼容版本。
- **提示**：先小范围更新（一次一个包），再全量更新。

---

## 附录：Poetry 速查表

### 常用命令

```bash
# 项目管理
poetry new my-project        # 创建新项目
poetry init                  # 初始化现有项目
poetry install               # 安装所有依赖
poetry update                # 更新所有依赖
poetry build                 # 构建分发包
poetry publish               # 发布到 PyPI

# 依赖管理
poetry add fastapi           # 添加生产依赖
poetry add --group dev pytest  # 添加开发依赖
poetry remove fastapi       # 移除依赖
poetry show                  # 列出依赖
poetry show --tree           # 依赖树
poetry show --outdated      # 可更新的包

# 虚拟环境
poetry shell                 # 激活虚拟环境
poetry run python main.py    # 在虚拟环境中执行
poetry env info              # 虚拟环境信息
poetry env use python3.12    # 指定 Python 版本
poetry env list              # 列出所有虚拟环境
poetry env remove python3.12 # 删除虚拟环境

# 配置
poetry config --list        # 查看配置
poetry config virtualenvs.in-project true  # .venv 在项目内
poetry source add name url   # 添加源
poetry version               # 查看/设置版本
```

### pyproject.toml 模板

```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = ""
authors = ["Your Name <you@example.com>"]
readme = "README.md"
license = "MIT"

[tool.poetry.dependencies]
python = "^3.10"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
ruff = "^0.1"
mypy = "^1.5"

[build-system]
requires = ["poetry-core>=1.6.0"]
build-backend = "poetry.core.masonry.api"
```

### 版本约束速查

| 约束 | 含义 | 示例 | 匹配 |
|------|------|------|------|
| `^1.2.3` | 兼容更新 | `^1.2.3` | `>=1.2.3,<2.0.0` |
| `~1.2.3` | 小版本锁定 | `~1.2.3` | `>=1.2.3,<1.3.0` |
| `>=1.2.3` | 大于等于 | `>=1.2.3` | `1.2.3+` |
| `==1.2.3` | 精确 | `==1.2.3` | `1.2.3` |
| `*` | 任意 | `*` | 所有 |

### 依赖组速查

| 组 | 用途 | 安装命令 |
|----|------|---------|
| 默认（prod） | 生产依赖 | 总是安装 |
| dev | 开发工具 | `poetry install --without dev` 排除 |
| test | 测试框架 | `poetry install --only test` |
| docs | 文档生成 | `poetry install --without docs` |

### Docker 速查

```dockerfile
# 关键三行
RUN pip install poetry==1.8.0
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --without dev --no-interaction
```

### CI 速查

```yaml
# 关键步骤
- run: pip install poetry==1.8.0
- run: poetry install --no-interaction
- run: poetry run pytest -v
```

### 故障排查速查

```bash
# 1. 查看版本
poetry --version

# 2. 查看配置
poetry config --list

# 3. 查看虚拟环境
poetry env info

# 4. 查看依赖树
poetry show --tree

# 5. 清除缓存
poetry cache clear --all pypi

# 6. 详细输出
poetry -vvv install
```

### 常用环境变量

```bash
# 指定 Poetry 版本
POETRY_VERSION=1.8.0

# PyPI Token（发布用）
POETRY_PYPI_TOKEN_PYPI=your-token

# 私有源 Token
POETRY_HTTP_BASIC_MY_REPO_USERNAME=user
POETRY_HTTP_BASIC_MY_REPO_PASSWORD=pass

# 非交互模式
POETRY_NO_INTERACTION=1
```

### 完整项目初始化脚本

```bash
# 一键初始化新项目
#!/bin/bash
set -e

PROJECT_NAME=$1
if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: $0 <project-name>"
    exit 1
fi

# 1. 创建项目
poetry new "$PROJECT_NAME"
cd "$PROJECT_NAME"

# 2. 配置 .venv 在项目内
poetry config virtualenvs.in-project true

# 3. 添加生产依赖
poetry add fastapi "uvicorn[standard]" sqlalchemy asyncpg pydantic

# 4. 添加开发依赖
poetry add --group dev pytest pytest-asyncio pytest-cov ruff mypy pre-commit

# 5. 初始化 git
git init
cat > .gitignore << 'EOF'
.venv/
__pycache__/
*.pyc
dist/
build/
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/
EOF

# 6. 安装
poetry install

echo "✅ Project $PROJECT_NAME created successfully!"
echo "Run 'cd $PROJECT_NAME && poetry shell' to start coding"
```

### 工作流速查

```mermaid
graph LR
    A[修改代码] --> B[poetry run 测试]
    B --> C[添加新依赖?]
    C -->|是| D[poetry add pkg]
    D --> E[poetry install]
    C -->|否| F[git commit]
    E --> F
    F --> G[CI 自动运行]
    G --> H{通过?}
    H -->|是| I[合并/发布]
    H -->|否| A
```

### 依赖生命周期

```mermaid
graph TD
    A[发现需求] --> B[poetry add pkg]
    B --> C[pyproject.toml 更新]
    C --> D[依赖解析]
    D --> E[poetry.lock 更新]
    E --> F[.venv 安装]
    F --> G[使用]
    G --> H[定期 poetry update]
    H --> I[安全扫描]
    I --> J[清理未使用依赖]
    J --> G
```

### 版本约束决策树

```mermaid
graph TD
    A[选择版本约束] --> B{是工具链?}
    B -->|是| C[精确版本 ==x.y.z]
    B -->|否| D{是库项目?}
    D -->|是| E[~x.y.z 宽松]
    D -->|否| F{是应用项目?}
    F -->|是| G[^x.y.z 平衡]
    F -->|否| H[>=x.y 最宽松]
```

### 团队协作流程

```mermaid
sequenceDiagram
    participant Dev as 开发者
    participant Git as Git
    participant CI as CI/CD
    participant Prod as 生产环境

    Dev->>Git: poetry add new-pkg
    Dev->>Git: commit pyproject.toml + poetry.lock
    Git->>CI: 触发 CI
    CI->>CI: poetry install
    CI->>CI: poetry run pytest
    CI-->>Git: 通过/失败
    Git->>Prod: 部署
    Prod->>Prod: poetry install --without dev
```

### 常见问题决策树

```mermaid
graph TD
    A[遇到 Poetry 问题] --> B{是安装失败?}
    B -->|是| C{网络问题?}
    C -->|是| D[配置国内镜像]
    C -->|否| E[清除缓存重试]
    B -->|否| F{是依赖冲突?}
    F -->|是| G[poetry show --tree]
    G --> H[调整版本约束]
    B -->|否| I{是运行时问题?}
    I -->|是| J[poetry env info]
    J --> K[检查 Python 版本]
```

---

**🔗 关联笔记**

- [[Python-项目结构最佳实践]] — Python 项目结构与工程化规范
- [[Pytest-测试驱动开发]] — Python 测试框架
- [[Python-类型注解与mypy]] — 静态类型检查

**📖 前置知识**

- [[Python-模块与包管理原理]]
- [[Python-项目结构最佳实践]]

**🏷️ 相关标签**

#Python #Poetry #依赖管理 #虚拟环境 #包管理

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]
