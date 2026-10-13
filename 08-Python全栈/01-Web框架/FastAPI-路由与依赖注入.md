---
title: FastAPI 路由与依赖注入
tags: [Python, FastAPI, Web框架, 核心, 依赖注入, 路由]
category: Python全栈
created: 2026-08-13
updated: 2026-09-09
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[Python-语法基础与数据结构]]", "[[Python-异步编程asyncio]]", "[[Python-类型注解与mypy]]"]
aliases: [FastAPI路由与依赖注入, FastAPI DI, FastAPI路由, FastAPI依赖注入, FastAPI-高性能Web框架, FastAPI快速入门, FastAPI APIRouter]
---

# FastAPI 路由与依赖注入

> **📖 文档说明**
>
> 本文档是「从零基础新手到实战老手」三部曲的**核心进阶篇**，系统讲解 FastAPI 的两大基石：类型驱动的路由声明体系与依赖注入（Dependency Injection）系统。从第一个 Hello World 接口开始，逐步深入路径参数、查询参数、请求体、Header、Cookie、响应模型、HTTP 方法语义，再到 Depends 原理、依赖嵌套、作用域、yield 清理、数据库会话、认证授权、全局依赖、APIRouter 模块化与大型项目架构。全文配备 150+ 可运行代码示例、50+ 常见坑点、30+ 面试高频考点，学完即可独立构建生产级 FastAPI 服务。
>
> **👥 适用人群**
> - 零基础但有 Python 基础、想入门 FastAPI 的新手
> - 从 Flask/Django 迁移到 FastAPI 的全栈工程师
> - 需要构建高性能异步 API、微服务的后端开发者
> - 准备 FastAPI 相关面试的求职者
>
> **📚 前置知识**
> - [[Python-语法基础与数据结构]]
> - [[Python-异步编程asyncio]]
> - [[Python-类型注解与mypy]]
> - [[RESTfulAPI设计原则]]
>
> **🗺️ 学习路径**
> - 入门篇（第 1-5 章）：会用——能写出带参数校验和响应模型的接口
> - 进阶篇（第 6-9 章）：懂原理——理解依赖注入 DAG、作用域、yield 清理机制
> - 实战篇（第 10-12 章）：成专家——掌握大型项目路由架构、测试、性能优化与生产部署

---

## 一、FastAPI 概述与核心价值

### 1.1 FastAPI 是什么

#### 概念解释

**FastAPI 是一个基于 Starlette（ASGI 异步 Web 工具包）和 Pydantic（数据校验库）的现代、高性能 Python Web 框架。** 它的核心设计哲学是「类型注解驱动一切」——通过 Python 原生的类型注解自动完成请求参数解析、数据校验、序列化和 OpenAPI 文档生成，让开发者用最少的代码写出最健壮的 API。

> 🎯 面试高频：FastAPI 的两大技术底座是什么？答案是 Starlette（提供 ASGI 路由、中间件、请求/响应对象）和 Pydantic（提供数据校验、序列化、Schema 定义）。FastAPI 本身是在这两者之上的「类型注解胶水层」。

打个比方：如果把写 API 比作开餐厅，Flask 是让你自己买菜、切菜、炒菜、摆盘、上菜的夫妻店，每一步都要手动操作；而 FastAPI 是一个智能中央厨房——你只要在菜单（函数签名）上标注「这道菜要几分熟（类型注解）」，厨房自动完成备料（参数解析）、质检（Pydantic 校验）、烹饪（路由函数）、摆盘（响应序列化）和打印菜单（OpenAPI 文档），你只需要专注于「这道菜的味道」（业务逻辑）。

**核心价值**：FastAPI 将「参数解析 + 数据校验 + 文档生成」这三件每个 API 都要做的重复劳动完全自动化，同时原生支持异步，性能与 Node.js/Go 相当，开发效率却远超传统 Python 框架。

#### 原理说明：FastAPI 的技术栈分层

FastAPI 不是从零实现的 Web 框架，而是站在两个巨人肩膀上的「集成框架」：

```mermaid
graph TB
    subgraph 应用层
        A[你的路由函数<br/>async def create_item]
    end
    subgraph FastAPI层
        B[FastAPI 应用对象<br/>类型注解解析 / Depends 依赖注入 / response_model]
    end
    subgraph Starlette层
        C[Starlette<br/>ASGI 路由匹配 / 中间件 / Request / Response]
    end
    subgraph Pydantic层
        D[Pydantic v2<br/>数据校验 / 序列化 / Model 定义]
    end
    subgraph ASGI服务器层
        E[Uvicorn / Hypercorn<br/>ASGI 协议实现 / 事件循环]
    end
    A --> B
    B --> C
    B --> D
    C --> E
    E --> F[客户端 HTTP 请求]
```

**为什么这样设计？**

| 设计决策 | 原因 | 技术对比 |
|---------|------|---------|
| 基于 Starlette 而非自研 ASGI | Starlette 已实现高性能 ASGI 路由、中间件、WebSocket，重写是重复造轮子 | Flask 基于 Werkzeug（WSGI），Django 自研 WSGI 处理器 |
| 基于 Pydantic 而非自研校验 | Pydantic v2 核心用 Rust 编写，校验速度比纯 Python 快 10-50 倍，且生态成熟 | Marshmallow 需手动定义 Schema，DRF Serializer 与 Django ORM 强耦合 |
| 类型注解驱动而非装饰器配置 | Python 类型注解是语言原生特性，IDE 友好、mypy 可检查、无需额外学习 DSL | Flask-RESTX 需要 `@api.expect()` 装饰器，DRF 需单独写 Serializer 类 |
| 原生 async/await | ASGI 协议天然支持异步，无需 gevent/eventlet 猴子补丁 | Flask 异步需 `asyncio` + 额外 worker，Django 4.2 才部分支持异步视图 |

> 🎯 面试高频：FastAPI 为什么快？三个原因：① ASGI 异步架构，单进程可处理上万并发连接；② Pydantic v2 核心用 Rust（pydantic-core），校验极快；③ 路由匹配基于 Starlette 的前缀树（Trie），匹配复杂度 O(路径段数) 而非 O(路由数)。

#### 代码示例

**示例 1：Hello World——最小 FastAPI 应用**

```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="我的第一个 FastAPI 应用")

@app.get("/")
async def root():
    return {"message": "Hello World"}

# 运行：uvicorn main:app --reload
# 访问 http://localhost:8000/ → {"message":"Hello World"}
# 访问 http://localhost:8000/docs → 自动生成的 Swagger UI 文档
```

预期运行结果：启动后访问 `http://localhost:8000/` 返回 JSON `{"message":"Hello World"}`，访问 `/docs` 看到交互式 API 文档。

**示例 2：带类型注解的接口——自动参数解析与校验**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

# GET /items/5?q=phone → {"item_id":5,"q":"phone"}
# GET /items/abc → 422 错误：[{"loc":["path","item_id"],"msg":"Input should be a valid integer"}]
# GET /items/5 → {"item_id":5,"q":null}
```

预期运行结果：`item_id` 自动从路径提取并转为 int，`q` 自动从查询字符串提取；传非数字 `abc` 时自动返回 422 校验错误。

**示例 3：完整场景——带请求体校验的创建接口**

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Item(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="商品名称")
    price: float = Field(..., gt=0, description="价格必须大于0")
    is_offer: bool | None = Field(None, description="是否促销")

@app.post("/items/", status_code=201)
async def create_item(item: Item):
    return {"received": item.model_dump(), "id": 1}

# POST /items/ {"name":"iPhone","price":999.99} → 201
# POST /items/ {"name":"a","price":-10} → 422 校验失败
```

预期运行结果：Pydantic 自动校验请求体，字段不满足约束时返回 422 和详细错误位置；合法请求返回 201 Created。

#### 使用场景与最佳实践

**适用场景**：高并发 API 服务（AI 推理接口、实时数据推送、微服务网关）；需要自动生成 API 文档的团队；数据校验要求严格的金融、电商类接口；异步 IO 密集型应用。

**不适用场景**：需要 Django Admin 后台的内容管理系统；团队完全不熟悉类型注解的遗留项目；纯同步阻塞且并发量极低的内部小工具。

**最佳实践**：
1. 始终为路由函数参数添加类型注解，这是 FastAPI 一切自动化的基础
2. 使用 Pydantic Model 定义请求体和响应体，不要在函数内手动 `request.json()`
3. 生产环境用 `uvicorn` 或 `gunicorn + uvicorn worker` 启动，不要用 `--reload`
4. 始终声明 `response_model`，避免敏感字段（如密码哈希）泄露
5. 接口路径用名词复数（`/items/` 而非 `/item/`），符合 RESTful 规范

**性能建议**：路由函数中如果有阻塞 IO，要么改用异步版本，要么用 `def`（同步函数）让 FastAPI 自动放到线程池执行，不要在 `async def` 中调用阻塞代码。

#### 常见坑点

**坑点 1：在 async def 中调用阻塞代码导致性能骤降**

- 错误现象：压测时 QPS 极低，即使只有几个请求也响应缓慢
- 根本原因：`async def` 函数在事件循环中执行，内部调用同步阻塞操作会卡住整个事件循环
- 正确做法：改用异步库（httpx 替代 requests，asyncpg 替代 psycopg2），或将函数改为 `def`
- 预防措施：代码审查时检查 `async def` 函数内是否有阻塞调用

```python
# 错误：async def 中调用阻塞的 requests
@app.get("/bad")
async def bad():
    import requests
    result = requests.get("https://api.example.com/data")  # 阻塞！
    return result.json()

# 正确方案一：用异步 httpx
@app.get("/good-async")
async def good_async():
    import httpx
    async with httpx.AsyncClient() as client:
        result = await client.get("https://api.example.com/data")
    return result.json()

# 正确方案二：用同步 def，FastAPI 自动放线程池
@app.get("/good-sync")
def good_sync():
    import requests
    result = requests.get("https://api.example.com/data")
    return result.json()
```

**坑点 2：忘记安装 uvicorn 或用错启动命令**

- 错误现象：`uvicorn main:app` 报 `command not found`
- 根本原因：未安装 uvicorn，或启动参数 `main:app` 写错，或在错误目录启动
- 正确做法：`pip install uvicorn`，在 `main.py` 所在目录执行 `uvicorn main:app --reload`
- 预防措施：requirements.txt 固定 `uvicorn[standard]` 版本；用 `python -m uvicorn main:app`

---

### 1.2 FastAPI 与其他框架对比

#### 概念解释

**框架选型是技术决策的第一步。** FastAPI、Flask、Django、Tornado 是 Python 生态最主流的四个 Web 框架。FastAPI 的差异化优势在于「类型注解驱动 + 原生异步 + 自动文档」三位一体。

打个比方：选框架像选车——Django 是豪华 SUV（空间大、配置全、但重），Flask 是轻便自行车（灵活、轻量、但要自己装配件），Tornado 是赛车（快、但难驾驭），FastAPI 是特斯拉（又快又智能、自动驾驶辅助多）。

**核心价值**：理解各框架差异，能在项目启动时做出正确选型，避免架构错配。

#### 原理说明：四框架核心机制对比

```mermaid
graph LR
    subgraph WSGI框架
        F[Flask<br/>Werkzeug + Jinja2]
        D[Django<br/>自研 ORM + Admin]
    end
    subgraph ASGI框架
        T[Tornado<br/>自研异步 IO]
        FA[FastAPI<br/>Starlette + Pydantic]
    end
    WSGI框架 -->|同步阻塞| G[线程/进程模型]
    ASGI框架 -->|异步非阻塞| H[事件循环模型]
```

| 维度 | FastAPI | Flask | Django | Tornado |
|------|---------|-------|--------|---------|
| 协议 | ASGI（异步） | WSGI（同步） | WSGI（同步） | 自研异步 |
| 类型注解 | 核心驱动 | 不支持 | 不支持 | 不支持 |
| 数据校验 | Pydantic（自动） | 手动 / marshmallow | DRF Serializer | 手动 |
| 自动文档 | OpenAPI 内置 | 需 flask-restx | 需 drf-yasg | 无 |
| ORM | 任意（推荐 SQLAlchemy） | 任意 | Django ORM（强绑定） | 任意 |
| Admin 后台 | 无 | 无 | 内置（强大） | 无 |
| 异步 | 原生 async/await | 需 gevent | 4.2+ 部分支持 | 原生回调式 |
| 性能 | 极高（~Go 级别） | 中 | 中低 | 高 |
| 学习曲线 | 中（需懂类型注解） | 低 | 高（概念多） | 高（异步回调） |
| 典型场景 | 高并发 API、AI 服务 | 小工具、原型 | CMS、企业后台 | 长连接、WebSocket |

> 🎯 面试高频：FastAPI 和 Flask 的本质区别？① 协议层：FastAPI 是 ASGI，Flask 是 WSGI；② 编程模型：FastAPI 类型注解驱动，Flask 装饰器+手动解析；③ 性能：FastAPI 异步高并发，Flask 同步阻塞。

#### 代码示例

**示例 1：同一个接口在四个框架中的写法对比**

```python
# ===== FastAPI =====
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
class UserIn(BaseModel):
    name: str
    age: int

@app.post("/users/")
async def create_user(user: UserIn):
    return {"id": 1, **user.model_dump()}

# ===== Flask =====
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/users/", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or "name" not in data or "age" not in data:
        return jsonify({"error": "缺少字段"}), 400
    if not isinstance(data["age"], int):
        return jsonify({"error": "age 必须是整数"}), 400
    return jsonify({"id": 1, "name": data["name"], "age": data["age"]}), 201
```

预期运行结果：FastAPI 用 6 行完成参数校验+序列化，Flask 需要手动写 8 行校验逻辑。

**示例 2：FastAPI 异步并发优势演示**

```python
import asyncio
from fastapi import FastAPI

app = FastAPI()

@app.get("/slow/{seconds}")
async def slow_endpoint(seconds: float):
    await asyncio.sleep(seconds)
    return {"slept": seconds}

# 并发 100 个请求各 sleep 1 秒：总耗时约 1 秒（异步非阻塞）
# 同样的代码用 Flask + time.sleep：总耗时约 100 秒（同步阻塞）
```

预期运行结果：100 个并发请求几乎同时完成（约 1 秒）。

**示例 3：FastAPI 自动生成 OpenAPI 文档**

```python
from fastapi import FastAPI

app = FastAPI(
    title="电商 API",
    description="商品与订单管理接口",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.get("/products/{product_id}", summary="获取商品详情", response_description="商品信息")
async def get_product(product_id: int):
    """根据商品 ID 获取详情。- **product_id**: 商品唯一标识"""
    return {"id": product_id, "name": "示例商品"}

# 访问 /docs 看到带摘要、描述、参数说明的交互式文档
# 访问 /openapi.json 拿到标准 OpenAPI 3.1 JSON
```

预期运行结果：`/docs` 页面展示完整接口文档，可直接「Try it out」发请求。

#### 使用场景与最佳实践

**适用场景**：微服务架构中的 API 网关和业务服务；AI/ML 模型推理服务；前后端分离项目的后端 API；物联网设备数据接收接口。

**不适用场景**：服务器端渲染（SSR）的传统网站；需要内置 Admin、Auth、ORM 全家桶的快速后台；团队深度绑定 Django 生态的项目。

**最佳实践**：
1. 新项目优先选 FastAPI，除非明确需要 Django Admin 或服务端渲染
2. 从 Flask 迁移时，先把接口逐个改写为 FastAPI 路由，再逐步引入 Pydantic 和依赖注入
3. 不要为了「用 FastAPI」而在简单脚本中引入它
4. 对外 API 务必配置 title、description、version
5. 大型项目用 APIRouter 分模块，不要把所有路由写在一个 main.py 里

**性能建议**：IO 密集型用异步，CPU 密集型用同步 `def`（FastAPI 放线程池）或独立 Worker 进程。

#### 常见坑点

**坑点 1：认为 FastAPI 一定比 Flask 快，盲目迁移**

- 错误现象：迁移后性能没有提升，甚至更慢
- 根本原因：FastAPI 的性能优势来自异步非阻塞，如果路由函数内部仍是同步阻塞代码，异步框架也救不了
- 正确做法：迁移时同步改造数据库驱动为异步版，HTTP 客户端用 httpx
- 预防措施：迁移前做基准测试，确认瓶颈在 IO 而非 CPU

**坑点 2：在生产环境使用 --reload**

- 错误现象：生产环境服务偶尔重启、内存占用高
- 根本原因：`--reload` 是开发热重载功能，会监控文件变化并重启进程
- 正确做法：生产用 `uvicorn main:app --workers 4` 或 gunicorn + uvicorn worker
- 预防措施：CI/CD 中区分开发/生产配置，生产禁用 reload

---

### 1.3 FastAPI 请求处理全链路

#### 概念解释

**一个 HTTP 请求从进入 FastAPI 到返回响应，会经过一条清晰的处理流水线：ASGI 服务器接收 → 中间件链 → 路由匹配 → 参数解析与校验 → 依赖注入 → 路由函数执行 → 响应序列化 → 中间件响应链 → 返回客户端。** 理解这条流水线是调试和性能优化的基础。

打个比方：请求像一个去医院看病的病人——前台挂号（ASGI 服务器）→ 预检分诊（中间件）→ 科室匹配（路由匹配）→ 化验检查（参数校验）→ 专家会诊（依赖注入）→ 医生诊断（路由函数）→ 开药（响应序列化）→ 离院复查（中间件响应链）。

**核心价值**：掌握请求全链路后，遇到 422、500、响应字段缺失等问题时，能快速判断是哪个环节出了问题。

#### 原理说明：请求流水线详解

```mermaid
graph TB
    A[客户端 HTTP Request] --> B[ASGI Server<br/>Uvicorn]
    B --> C[中间件链外层<br/>ServerError / CORS / GZip]
    C --> D[自定义中间件<br/>日志 / 请求ID / 限流]
    D --> E[ExceptionMiddleware<br/>异常捕获]
    E --> F[Starlette Router<br/>路径匹配]
    F --> G{路径是否匹配?}
    G -->|否| H[404 Not Found]
    G -->|是| I[FastAPI 依赖解析器<br/>递归解析 Depends 链]
    I --> J[参数解析<br/>Path / Query / Body / Header]
    J --> K[Pydantic 校验]
    K -->|校验失败| L[422 Validation Error]
    K -->|校验通过| M[执行路由函数]
    M --> N[响应序列化<br/>response_model 过滤]
    N --> O[中间件响应链<br/>从内到外]
    O --> P[ASGI Server 发送 Response]
    P --> Q[客户端接收]
    style L fill:#ffcccc
    style H fill:#ffcccc
    style M fill:#ccffcc
```

**各环节职责与可干预点**：

| 环节 | 职责 | 开发者可干预方式 |
|------|------|----------------|
| ASGI Server | TCP 连接管理、HTTP 解析、事件循环 | 选择 uvicorn/hypercorn、配置 worker 数 |
| 中间件链 | 横切逻辑（日志、CORS、限流） | `app.add_middleware()` / `@app.middleware("http")` |
| 路由匹配 | URL 路径 → 路由函数 | `@app.get()` 等装饰器注册顺序 |
| 参数解析 | 从路径/查询/请求体提取参数 | 函数签名 + 类型注解 |
| Pydantic 校验 | 类型转换、约束检查 | `Field()`、自定义验证器 |
| 依赖注入 | 解析 Depends 链、注入依赖 | `Depends()`、`dependency_overrides` |
| 路由函数 | 业务逻辑 | 你写的代码 |
| 响应序列化 | 过滤字段、转换格式 | `response_model`、`response_model_exclude` |

> 🎯 面试高频：FastAPI 中 422 错误是在哪个环节产生的？答案是在 Pydantic 校验环节，发生在路由函数执行之前。所以路由函数内的代码不会执行，也无法在函数内捕获 422。

#### 代码示例

**示例 1：在各环节添加日志，观察请求流转**

```python
import time
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def log_pipeline(request: Request, call_next):
    print(f"[1-中间件-before] {request.method} {request.url.path}")
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    print(f"[6-中间件-after] 状态码={response.status_code} 耗时={duration:.1f}ms")
    return response

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    print(f"[4-路由函数] item_id={item_id}, q={q}")
    return {"item_id": item_id, "q": q}

# GET /items/5?q=test 控制台输出：
# [1-中间件-before] GET /items/5
# [4-路由函数] item_id=5, q=test
# [6-中间件-after] 状态码=200 耗时=1.2ms
```

预期运行结果：控制台按顺序打印中间件 before → 路由函数 → 中间件 after。

**示例 2：观察 422 校验失败时路由函数不执行**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    print("路由函数执行了！")  # 这行不会打印
    return {"item_id": item_id}

# GET /items/abc → 422 错误，控制台无输出
# 因为 Pydantic 校验在路由函数之前，失败直接返回 422
```

预期运行结果：访问 `/items/abc` 返回 422，控制台没有打印。

**示例 3：完整场景——带依赖的请求全链路追踪**

```python
from fastapi import FastAPI, Depends, Request
import time

app = FastAPI()

async def log_dependency(request: Request):
    start = time.time()
    print(f"[3-依赖-before] 路径={request.url.path}")
    yield
    print(f"[5-依赖-after] 耗时={(time.time()-start)*1000:.1f}ms")

@app.get("/test")
async def test_endpoint(request: Request, _: None = Depends(log_dependency)):
    print("[4-路由函数] 业务逻辑执行")
    return {"ok": True}

# GET /test 控制台输出：
# [3-依赖-before] 路径=/test
# [4-路由函数] 业务逻辑执行
# [5-依赖-after] 耗时=0.5ms
```

预期运行结果：依赖的 before 在路由函数之前执行，after 在路由函数之后执行。

#### 使用场景与最佳实践

**适用场景**：调试接口异常时定位问题环节；性能优化时分析各环节耗时分布；设计中间件和依赖时理解执行顺序。

**不适用场景**：简单接口开发不需要深入理解全链路。

**最佳实践**：
1. 调试时在中间件和依赖中加日志，快速定位请求卡在哪一步
2. 422 错误优先检查参数类型和约束
3. 404 错误检查路由路径和注册顺序
4. 500 错误检查路由函数内部异常和依赖异常
5. 响应字段缺失检查 response_model 是否过滤了字段

**性能建议**：用中间件记录各环节耗时，找到瓶颈。通常瓶颈在路由函数的数据库查询或外部调用，而非框架本身（框架开销通常 < 1ms）。

#### 常见坑点

**坑点 1：路由函数内修改了响应但客户端看不到**

- 错误现象：在路由函数中 `response.headers["X-Custom"] = "value"`，但客户端收不到
- 根本原因：如果路由函数返回 dict，FastAPI 会创建新的 JSONResponse，函数内对 response 参数的修改不影响最终响应
- 正确做法：直接返回 `JSONResponse(content=..., headers={...})`，或注入 `Response` 对象并修改
- 预防措施：需要自定义响应头时，明确返回 Response 子类或注入 Response 参数

```python
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI()

# 正确：注入 Response 对象并修改
@app.get("/with-header")
async def with_header(response: Response):
    response.headers["X-Custom"] = "hello"
    return {"message": "ok"}

# 正确：直接返回 JSONResponse
@app.get("/with-header2")
async def with_header2():
    return JSONResponse(content={"message": "ok"}, headers={"X-Custom": "hello"})
```

**坑点 2：请求体在中间件中被读取后路由函数拿不到**

- 错误现象：自定义中间件中调用了 `await request.body()`，路由函数中请求体为空
- 根本原因：ASGI 的 receive 协程是一次性的，body 被读取后流已消耗
- 正确做法：中间件中不要读取 body；如需记录请求体，重新封装 `request._receive`
- 预防措施：中间件中只读取 header 和 path，不读取 body

---

> 💡 **本章深度讲解**：本章建立了 FastAPI 的全局认知。FastAPI 的本质是「Starlette + Pydantic + 类型注解胶水」，它不是重新发明轮子，而是把两个优秀组件以类型注解为核心巧妙粘合。请求处理流水线是理解一切的地图——遇到任何问题，先想「这发生在流水线的哪个环节」。与 Flask/Django 的对比帮助你在选型时做出理性决策。
>
> 📝 **本章精简总结**：
> 1. FastAPI = Starlette（ASGI 路由/中间件）+ Pydantic（数据校验）+ 类型注解驱动
> 2. 核心优势：自动参数解析、自动数据校验、自动 OpenAPI 文档、原生异步高性能
> 3. 请求流水线：ASGI → 中间件 → 路由匹配 → 参数解析 → Pydantic 校验 → 依赖注入 → 路由函数 → 响应序列化
> 4. 422 错误发生在 Pydantic 校验环节，路由函数不会执行
> 5. 选型：API 服务选 FastAPI，CMS/Admin 选 Django，小工具选 Flask
> 6. async def 中不能有阻塞代码，否则卡住事件循环
> 7. 生产环境禁用 --reload，用多 worker 启动
> 8. 始终声明 response_model 防止敏感字段泄露

🎯 **梯度练习题**

**基础题⭐**
1. 写出一个最小的 FastAPI 应用，包含 GET `/hello/{name}` 接口，返回 `{"message": f"Hello {name}"}`。
2. FastAPI 的两大技术底座是什么？各自负责什么？
3. 为什么在 `async def` 路由函数中不能调用 `time.sleep()`？

**进阶题⭐⭐**
4. 请解释 FastAPI 请求处理流水线的 8 个环节，并说明 422 错误发生在哪个环节。
5. 对比 FastAPI 和 Flask 实现「POST /users/ 创建用户，name 非空、age 为正整数」接口的代码差异。

**实战题⭐⭐⭐**
6. 设计一个中间件，记录每个请求的「中间件 before → 路由函数开始 → 路由函数结束 → 中间件 after」四个时间点，计算各环节耗时。提示：中间件记录 before/after，依赖记录路由函数前后。

---

## 二、路由基础：路径参数与查询参数

### 2.1 路径参数（Path Parameters）

#### 概念解释

**路径参数是 URL 路径中可变的部分，用花括号 `{}` 包裹，用于标识资源的唯一标识或层级关系。** FastAPI 通过函数参数名与路径参数名匹配，结合类型注解自动完成提取和类型转换。

打个比方：路径参数像快递地址中的「房间号」——URL `/users/123/orders/456` 中，`123` 是用户 ID（哪个用户），`456` 是订单 ID（哪个订单），它们是地址中可变的部分，决定了请求定位到哪个具体资源。

**核心价值**：路径参数让 URL 具有自描述性（RESTful 风格），同时 FastAPI 自动类型转换和校验，无需手动 `int(request.args["id"])`。

#### 原理说明：路径参数的匹配与转换机制

```mermaid
graph LR
    A[URL: /items/42] --> B[Starlette 路由匹配<br/>提取 item_id="42"]
    B --> C[FastAPI 类型注解解析<br/>item_id: int]
    C --> D[Pydantic 校验<br/>"42" → 42]
    D --> E{校验通过?}
    E -->|是| F[路由函数接收 item_id=42]
    E -->|否| G[422 Validation Error]
```

**路径参数的类型转换规则**：

| 类型注解 | URL 中的值 | 转换结果 | 失败时 |
|---------|-----------|---------|--------|
| `int` | `42` | `42` | 422 |
| `float` | `3.14` | `3.14` | 422 |
| `str` | `hello` | `"hello"` | 永不失败（任何值都是 str） |
| `bool` | `true`/`1`/`on`/`yes` | `True` | 422 |
| `Enum` | 枚举值之一 | 枚举成员 | 422 |
| `uuid.UUID` | 合法 UUID | UUID 对象 | 422 |

> 🎯 面试高频：路径参数和查询参数的区别？路径参数是 URL 路径的一部分（`/items/42`），用于标识资源；查询参数在 `?` 之后（`/items?q=phone&page=1`），用于过滤、排序、分页。路径参数是必需的（没有就 404），查询参数通常可选。

#### 代码示例

**示例 1：基础路径参数**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id, "type": type(item_id).__name__}

# GET /items/42 → {"item_id":42,"type":"int"}
# GET /items/abc → 422: "Input should be a valid integer"
# GET /items/ → 404（路径不匹配，因为缺少 item_id）
```

预期运行结果：`item_id` 自动转为 int，传非数字返回 422。

**示例 2：带约束的路径参数（Path）**

```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(..., ge=1, le=10000, description="商品 ID，范围 1-10000")
):
    return {"item_id": item_id}

# GET /items/42 → 200 {"item_id":42}
# GET /items/0 → 422: "Input should be greater than or equal to 1"
# GET /items/99999 → 422: "Input should be less than or equal to 10000"
```

预期运行结果：`Path(...)` 中的 `ge`（大于等于）、`le`（小于等于）自动校验范围。

**示例 3：完整场景——多路径参数 + 枚举类型**

```python
from enum import Enum
from fastapi import FastAPI, Path

app = FastAPI()

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"

@app.get("/users/{user_id}/orders/{order_id}")
async def read_user_order(
    user_id: int = Path(..., ge=1, description="用户 ID"),
    order_id: int = Path(..., ge=1, description="订单 ID"),
):
    return {"user_id": user_id, "order_id": order_id}

@app.get("/orders/status/{status}")
async def read_orders_by_status(status: OrderStatus):
    return {"status": status.value, "status_name": status.name}

# GET /users/1/orders/99 → {"user_id":1,"order_id":99}
# GET /orders/status/paid → {"status":"paid","status_name":"paid"}
# GET /orders/status/invalid → 422（不在枚举中）
```

预期运行结果：多路径参数按名称匹配；枚举类型自动校验只能取预定义值。

#### 使用场景与最佳实践

**适用场景**：标识具体资源（`/users/{id}`）；层级关系（`/users/{uid}/orders/{oid}`）；资源操作（`/items/{id}/reviews`）。

**不适用场景**：可选的过滤条件（用查询参数）；大量参数（超过 3 个考虑查询参数或请求体）；敏感信息（不要把 token 放路径中，会被日志记录）。

**最佳实践**：
1. 路径参数用名词复数 + ID：`/users/{user_id}` 而非 `/user/{id}`
2. 始终添加类型注解和约束（`ge=1` 防止负数 ID）
3. 静态路径必须注册在参数路径之前（`/users/me` 在 `/users/{user_id}` 之前）
4. 多路径参数时确保名称唯一且语义清晰
5. 枚举类型路径参数用于有限状态集合（订单状态、分类等）

**性能建议**：路径参数匹配基于前缀树，复杂度 O(路径段数)，与路由数量无关。但避免过深的路径嵌套（超过 5 层），影响可读性和匹配效率。

#### 常见坑点

**坑点 1：静态路径和参数路径冲突**

- 错误现象：访问 `/users/me` 返回 422 或被匹配为 `user_id="me"`
- 根本原因：路由按注册顺序匹配，如果 `/users/{user_id}` 先注册，`/users/me` 会被匹配为参数路径
- 正确做法：将静态路径 `/users/me` 注册在参数路径 `/users/{user_id}` 之前
- 预防措施：团队约定静态路径始终写在参数路径前面；代码审查时检查路由顺序

```python
# 正确：静态路由先注册
@app.get("/users/me")
async def read_current_user():
    return {"user": "current"}

@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id}

# 错误：参数路由先注册，/users/me 会被匹配为 user_id="me" → 422
```

**坑点 2：路径参数包含斜杠导致 404**

- 错误现象：路径参数值中包含 `/`（如文件路径），访问返回 404
- 根本原因：URL 路径中 `/` 是路径分隔符，`/files/path/to/file.txt` 被解析为多层路径
- 正确做法：使用 `:path` 转换器让参数包含斜杠：`@app.get("/files/{file_path:path}")`
- 预防措施：需要传递路径类参数时，使用 `:path` 转换器或改用查询参数

```python
from fastapi import FastAPI

app = FastAPI()

# 使用 :path 转换器，参数可以包含斜杠
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

# GET /files/docs/guide/readme.md → {"file_path":"docs/guide/readme.md"}
```

---

### 2.2 查询参数（Query Parameters）

#### 概念解释

**查询参数是 URL 中 `?` 之后的键值对，用 `&` 分隔，用于传递可选的过滤、排序、分页等条件。** FastAPI 通过函数参数名与查询参数名匹配，结合类型注解和默认值自动解析。

打个比方：查询参数像点咖啡时的附加要求——「一杯拿铁（路径参数指定了资源），要大杯、少糖、加燕麦奶（查询参数指定了可选条件）」。路径参数决定「要什么」，查询参数决定「要什么样的」。

**核心价值**：查询参数让接口灵活支持多种查询条件，FastAPI 自动解析、类型转换、默认值处理和校验，无需手动 `request.args.get("q", default)`。

#### 原理说明：查询参数解析机制

```mermaid
graph TB
    A[URL: /items?q=phone&page=1&size=20] --> B[Starlette 解析 query_string]
    B --> C[FastAPI 匹配函数参数名]
    C --> D{参数有默认值?}
    D -->|是| E[可选参数，缺失用默认值]
    D -->|否| F{参数有 ... ?}
    F -->|是| G[必需参数，缺失返回 422]
    F -->|否| H[默认 None，可选]
    E --> I[Pydantic 类型转换与校验]
    G --> I
    H --> I
    I --> J[注入路由函数]
```

**查询参数的默认值规则**：

| 函数签名 | 是否必需 | 缺失时行为 |
|---------|---------|-----------|
| `q: str` | 必需 | 422 错误 |
| `q: str = "default"` | 可选 | 使用 `"default"` |
| `q: str \| None = None` | 可选 | 使用 `None` |
| `q: str = Query(...)` | 必需 | 422 错误 |
| `q: str = Query(None)` | 可选 | 使用 `None` |

> 🎯 面试高频：FastAPI 如何判断一个参数是查询参数还是路径参数？规则：① 参数名出现在路径 `{}` 中 → 路径参数；② 简单类型（int/str/float/bool）且不在路径中 → 查询参数；③ Pydantic Model → 请求体；④ Depends() → 依赖注入。

#### 代码示例

**示例 1：基础查询参数**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
async def list_items(q: str | None = None, page: int = 1, size: int = 20):
    return {"q": q, "page": page, "size": size}

# GET /items/ → {"q":null,"page":1,"size":20}
# GET /items/?q=phone → {"q":"phone","page":1,"size":20}
# GET /items/?q=phone&page=2&size=50 → {"q":"phone","page":2,"size":50}
# GET /items/?page=abc → 422: page 必须是整数
```

预期运行结果：有默认值的参数可选，自动使用默认值；类型不匹配返回 422。

**示例 2：带约束的查询参数（Query）**

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items/")
async def list_items(
    q: str | None = Query(None, min_length=2, max_length=50, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    category: str | None = Query(None, pattern="^[a-z-]+$", description="分类slug"),
):
    return {"q": q, "page": page, "size": size, "category": category}

# GET /items/?q=a → 422: q 长度至少2
# GET /items/?size=200 → 422: size 最大100
# GET /items/?category=Electronics → 422: 不匹配正则（大写字母）
```

预期运行结果：`Query()` 提供丰富的约束校验，包括长度、范围、正则模式。

**示例 3：完整场景——布尔参数 + 多值参数 + 别名**

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/products/")
async def list_products(
    in_stock: bool = False,
    tags: list[str] = Query([], description="按标签过滤，可传多个"),
    sort_by: str = Query("created_at", alias="sort-by", description="排序字段"),
):
    return {"in_stock": in_stock, "tags": tags, "sort_by": sort_by}

# GET /products/?in_stock=true → {"in_stock":true,...}
# GET /products/?in_stock=1 → {"in_stock":true,...}（1/on/yes/true 都解析为 True）
# GET /products/?tags=electronics&tags=phone → {"tags":["electronics","phone"]}
# GET /products/?sort-by=price → {"sort_by":"price"}（别名映射）
```

预期运行结果：布尔参数支持多种真值写法；`list[str]` 自动收集同名参数为列表；`alias` 支持 URL 中用连字符命名。

#### 使用场景与最佳实践

**适用场景**：分页（page/size）、搜索过滤（q/category/price_range）、排序（sort_by/order）、布尔开关（in_stock/is_published）。

**不适用场景**：大量参数（超过 5-6 个，考虑用请求体 POST）；敏感数据（token/密码不要放 URL，会被日志和浏览器历史记录）；复杂嵌套结构（查询参数是扁平的，不适合嵌套对象）。

**最佳实践**：
1. 分页参数用 `page`/`page_size` 或 `offset`/`limit`，始终设置 `le` 上限防止一次查太多
2. 搜索关键词用 `q`，设置 `min_length` 防止空搜索
3. 布尔参数命名用 `is_` 或 `has_` 前缀（`is_active`、`has_image`）
4. 多值参数用 `list[str]` 类型，支持 `?tags=a&tags=b`
5. URL 中用连字符命名时用 `alias` 映射到 Python 蛇形命名

**性能建议**：查询参数校验开销极小，但避免在查询参数中传递大段文本（URL 长度通常限制在 2048-8192 字节），大参数用 POST 请求体。

#### 常见坑点

**坑点 1：查询参数名与 Python 关键字冲突**

- 错误现象：想定义 `from` 查询参数（日期范围起点），但 `from` 是 Python 关键字，无法作为参数名
- 根本原因：Python 保留字不能作为变量名
- 正确做法：用 `alias` 映射，参数名用 `from_date`，URL 中用 `from`
- 预防措施：遇到关键字冲突时统一用 `alias` 方案

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/logs/")
async def get_logs(
    from_date: str = Query(..., alias="from", description="开始日期"),
    to_date: str = Query(..., alias="to", description="结束日期"),
):
    return {"from": from_date, "to": to_date}

# GET /logs/?from=2024-01-01&to=2024-12-31 → {"from":"2024-01-01","to":"2024-12-31"}
```

**坑点 2：可选参数未设默认值导致 422**

- 错误现象：定义 `q: str | None` 但没写 `= None`，不传 q 时返回 422
- 根本原因：`str | None` 只是类型注解，表示「可以是 str 或 None」，但没有默认值意味着参数是必需的
- 正确做法：可选参数必须显式写默认值 `q: str | None = None`
- 预防措施：团队约定所有可选参数必须带默认值；代码审查时检查

```python
from fastapi import FastAPI

app = FastAPI()

# 错误：q 是必需的，不传返回 422
@app.get("/bad")
async def bad(q: str | None):
    return {"q": q}

# 正确：q 可选，默认 None
@app.get("/good")
async def good(q: str | None = None):
    return {"q": q}
```

---

### 2.3 路径参数与查询参数的组合使用

#### 概念解释

**实际接口中路径参数和查询参数经常组合使用：路径参数标识「哪个资源」，查询参数指定「资源的哪些方面/如何返回」。** 例如 `GET /users/{user_id}/orders?status=paid&page=1` 中，`user_id` 是路径参数（哪个用户的订单），`status` 和 `page` 是查询参数（过滤已支付订单、第一页）。

打个比方：去图书馆借书——路径参数是「哪个书架、哪一层」（定位资源位置），查询参数是「只要中文书、按出版日期排序、只要近五年的」（筛选和排序条件）。

**核心价值**：组合使用让 URL 既具有 RESTful 的资源定位能力，又具有灵活的查询过滤能力，是生产级 API 的标准模式。

#### 原理说明：组合参数的解析优先级

```mermaid
graph TB
    A[请求: GET /users/123/orders?status=paid&page=1] --> B[路径匹配]
    B --> C[提取路径参数<br/>user_id=123]
    C --> D[解析查询字符串<br/>status=paid, page=1]
    D --> E[FastAPI 按函数签名匹配]
    E --> F[user_id: int → Path]
    E --> G[status: str → Query]
    E --> H[page: int → Query]
    F --> I[Pydantic 统一校验]
    G --> I
    H --> I
    I --> J[注入路由函数]
```

**参数来源推断规则（FastAPI 核心机制）**：

| 参数类型 | 推断来源 | 示例 |
|---------|---------|------|
| 路径中声明的参数名 | Path | `/users/{user_id}` → `user_id` |
| 简单类型（int/str/float/bool） | Query | `q: str \| None` |
| Pydantic Model | Body | `item: Item` |
| `Depends()` | 依赖注入 | `db: Session = Depends(get_db)` |
| `Header()` | 请求头 | `user_agent: str = Header(None)` |
| `Cookie()` | Cookie | `session_id: str = Cookie(None)` |

> 🎯 面试高频：FastAPI 如何自动推断参数来源？这是 FastAPI 最核心的设计之一。规则：路径中同名 → Path；简单类型 → Query；Pydantic Model → Body；Depends → 依赖。这个推断机制让开发者无需显式声明 `Path()`/`Query()`，除非需要额外约束。

#### 代码示例

**示例 1：路径参数 + 查询参数基础组合**

```python
from fastapi import FastAPI, Path, Query

app = FastAPI()

@app.get("/users/{user_id}/orders")
async def list_user_orders(
    user_id: int = Path(..., ge=1, description="用户 ID"),
    status: str | None = Query(None, description="订单状态过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    return {
        "user_id": user_id,
        "status": status,
        "pagination": {"page": page, "page_size": page_size},
    }

# GET /users/1/orders?status=paid&page=2 → 正常返回
# GET /users/abc/orders → 422（user_id 不是 int）
# GET /users/1/orders?page=0 → 422（page 必须 >= 1）
```

预期运行结果：路径参数和查询参数分别校验，互不干扰。

**示例 2：路径参数作为查询参数的默认值**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int,
    item_id: int,
    q: str | None = None,
    short: bool = False,
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "这是一个完整的商品描述"})
    return item

# GET /users/1/items/2?q=phone → 包含 description
# GET /users/1/items/2?short=true → 不包含 description
```

预期运行结果：路径参数必填，查询参数可选，布尔参数控制返回内容详略。

**示例 3：完整场景——电商商品列表接口**

```python
from fastapi import FastAPI, Path, Query
from enum import Enum

app = FastAPI()

class SortField(str, Enum):
    price = "price"
    created_at = "created_at"
    sales = "sales"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

@app.get("/categories/{category_id}/products")
async def list_products(
    category_id: int = Path(..., ge=1, description="分类 ID"),
    keyword: str | None = Query(None, min_length=1, max_length=100, description="搜索关键词"),
    min_price: float | None = Query(None, ge=0, description="最低价格"),
    max_price: float | None = Query(None, ge=0, description="最高价格"),
    in_stock: bool = Query(False, description="仅显示有货"),
    sort_by: SortField = Query(SortField.created_at, description="排序字段"),
    sort_order: SortOrder = Query(SortOrder.desc, description="排序方向"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """电商商品列表：按分类 + 多维度过滤 + 排序 + 分页"""
    return {
        "category_id": category_id,
        "filters": {
            "keyword": keyword, "min_price": min_price,
            "max_price": max_price, "in_stock": in_stock,
        },
        "sort": {"by": sort_by.value, "order": sort_order.value},
        "pagination": {"page": page, "page_size": page_size},
    }

# GET /categories/3/products?keyword=phone&min_price=1000&max_price=5000&in_stock=true&sort_by=price&page=1
# → 完整的过滤+排序+分页参数
```

预期运行结果：一个接口支持 9 个参数的组合查询，每个参数独立校验，OpenAPI 文档自动展示所有参数说明。

#### 使用场景与最佳实践

**适用场景**：资源子列表（用户的订单、分类下的商品）；带过滤的资源查询；批量操作中的资源定位。

**不适用场景**：参数超过 8 个（考虑 POST + 请求体）；参数间有复杂依赖关系（用 Pydantic Model 封装）。

**最佳实践**：
1. 路径参数用于资源标识，查询参数用于过滤/排序/分页，职责分明
2. 路径参数加 `ge=1` 约束，查询参数加上限约束
3. 分页参数统一命名（page/page_size 或 offset/limit），全项目保持一致
4. 枚举类型用于排序字段、状态等有限集合，避免任意字符串
5. 复杂查询条件（如价格区间）拆为 min_xxx/max_xxx 两个参数

**性能建议**：查询参数本身无性能开销，但参数对应的数据库查询需要建索引。常见过滤字段（status、category_id）和排序字段（created_at、price）应在数据库中建复合索引。

#### 常见坑点

**坑点 1：路径参数和查询参数同名导致混淆**

- 错误现象：定义了 `/items/{item_id}` 路径，同时函数中有 `item_id: int = Query(...)`，导致参数来源不确定
- 根本原因：FastAPI 优先匹配路径参数，同名查询参数会被忽略
- 正确做法：避免同名；如果确实需要，用不同的参数名（路径用 `item_id`，查询用 `id_filter`）
- 预防措施：代码审查时检查路径参数名和查询参数名是否冲突

**坑点 2：查询参数传空字符串 vs 不传的区别**

- 错误现象：`?q=` 和不传 `q` 行为不同，导致业务逻辑混乱
- 根本原因：`?q=` 传入空字符串 `""`，不传则使用默认值 `None`，两者在 Python 中是不同的值
- 正确做法：在业务逻辑中区分 `if q is None`（未传）和 `if q == ""`（传了空值），或用 `Query(None)` 并在逻辑中统一处理
- 预防措施：接口文档中明确说明空字符串和不传的区别；前端约定不传而非传空字符串

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/search")
async def search(q: str | None = Query(None, min_length=1)):
    if q is None:
        return {"message": "未传搜索词，返回全部"}
    return {"message": f"搜索: {q}"}

# GET /search → {"message":"未传搜索词，返回全部"}
# GET /search?q= → 422（min_length=1，空字符串不合法）
# GET /search?q=phone → {"message":"搜索: phone"}
```

---

> 💡 **本章深度讲解**：路径参数和查询参数是 FastAPI 路由的基础。路径参数标识资源（URL 路径中的可变部分），查询参数过滤资源（? 后的键值对）。FastAPI 通过类型注解自动推断参数来源、完成类型转换和校验，这是「类型注解驱动」的第一个体现。核心要记住三点：① 静态路径必须注册在参数路径之前；② 可选参数必须显式设默认值；③ 路径参数和查询参数职责分明——路径定资源，查询定条件。
>
> 📝 **本章精简总结**：
> 1. 路径参数用 `{}` 包裹，类型注解自动转换，Path() 添加约束
> 2. 查询参数在 ? 之后，有默认值则可选，无默认值则必需
> 3. 参数来源推断：路径同名 → Path，简单类型 → Query，Pydantic → Body，Depends → 依赖
> 4. 静态路径必须注册在参数路径之前，否则 /users/me 被匹配为 user_id
> 5. 可选参数必须写 `= None`，仅 `str | None` 不够
> 6. 布尔参数支持 true/1/on/yes 多种真值写法
> 7. list[str] 自动收集同名查询参数为列表
> 8. 路径参数含斜杠时用 `:path` 转换器

🎯 **梯度练习题**

**基础题⭐**
1. 写一个接口 `GET /books/{book_id}`，book_id 为 int 且 >= 1，返回 `{"book_id": book_id}`。
2. 写一个接口 `GET /search`，有可选查询参数 `q`（str，默认 None）和 `limit`（int，默认 10，最大 100）。
3. 为什么静态路径 `/users/me` 必须注册在 `/users/{user_id}` 之前？

**进阶题⭐⭐**
4. 解释 FastAPI 自动推断参数来源的规则，并说明 `item: Item`（Pydantic Model）为什么被推断为请求体而非查询参数。
5. 设计一个文章列表接口 `GET /categories/{cat_id}/articles`，支持：状态过滤（draft/published）、关键词搜索、按浏览量/发布时间排序、分页。写出完整函数签名。

**实战题⭐⭐⭐**
6. 实现一个完整的电商商品搜索接口，路径参数 `category_id`，查询参数包括 keyword、min_price、max_price、in_stock、tags（多值）、sort_by、sort_order、page、page_size。要求每个参数都有合理的约束和默认值，并在函数中模拟返回过滤后的结果（含总数、当前页、总页数）。

---

## 三、请求体、Header、Cookie 与表单文件

### 3.1 请求体（Request Body）与 Pydantic Model

#### 概念解释

**请求体是客户端发送到服务器的数据载荷，通常是 JSON 格式，用于创建或更新资源。** FastAPI 通过将 Pydantic Model 声明为函数参数，自动完成 JSON 解析、类型转换、数据校验和 OpenAPI Schema 生成。

打个比方：请求体像快递包裹里的物品——URL 和 Header 是快递单（地址、寄件人信息），请求体是包裹里实际的商品（商品名称、价格、描述等详细数据）。Pydantic Model 是「验货清单」，自动检查包裹里的东西是否齐全、规格是否正确。

**核心价值**：Pydantic Model 将请求体的定义、校验、文档三合一，开发者只需定义一次 Schema，即可同时获得运行时校验和 API 文档，无需手动 `request.get_json()` + 逐字段校验。

#### 原理说明：请求体解析与校验流程

```mermaid
graph TB
    A[POST /items/ JSON Body] --> B[Starlette 读取请求体<br/>await request.body()]
    B --> C[JSON 解析<br/>json.loads]
    C --> D[FastAPI 匹配 Pydantic Model]
    D --> E[Pydantic v2 校验<br/>Rust 核心 pydantic-core]
    E --> F{校验通过?}
    F -->|是| G[创建 Model 实例<br/>注入路由函数]
    F -->|否| H[422 Validation Error<br/>含字段级错误信息]
    G --> I[路由函数接收 item: Item]
```

**Pydantic Model 常用字段约束**：

| 约束 | 说明 | 示例 |
|------|------|------|
| `...` | 必填（Ellipsis） | `name: str = Field(...)` |
| `min_length` / `max_length` | 字符串长度范围 | `name: str = Field(..., min_length=2, max_length=100)` |
| `gt` / `ge` / `lt` / `le` | 数值大小约束 | `price: float = Field(..., gt=0)` |
| `pattern` | 正则匹配 | `email: str = Field(..., pattern=r"^.+@.+$")` |
| `default` | 默认值 | `is_active: bool = Field(default=True)` |
| `description` | 字段说明（用于文档） | `Field(..., description="用户邮箱")` |
| `examples` | 示例值（用于文档） | `Field(..., examples=["john@example.com"])` |

> 🎯 面试高频：Pydantic v1 和 v2 的主要区别？① v2 核心用 Rust 重写（pydantic-core），性能提升 10-50 倍；② `Config` 类改为 `model_config` 字典；③ `from_orm=True` 改为 `from_attributes=True`；④ `.dict()` 改为 `.model_dump()`，`.json()` 改为 `.model_dump_json()`；⑤ 验证器从 `@validator` 改为 `@field_validator`。

#### 代码示例

**示例 1：基础请求体**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None

@app.post("/items/")
async def create_item(item: Item):
    return {"name": item.name, "price": item.price, "is_offer": item.is_offer}

# POST /items/ {"name":"iPhone","price":999.99} → 200
# POST /items/ {"name":"iPhone"} → 422: price 字段缺失
# POST /items/ {"name":"iPhone","price":"not_a_number"} → 422: price 类型错误
```

预期运行结果：Pydantic 自动解析 JSON 并校验，缺失字段或类型错误返回 422。

**示例 2：带约束和嵌套 Model 的请求体**

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr

app = FastAPI()

class Address(BaseModel):
    street: str = Field(..., min_length=2, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    zip_code: str = Field(..., pattern=r"^\d{6}$", description="6位邮编")

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=8, max_length=128, description="密码至少8位")
    full_name: str | None = Field(None, max_length=100)
    age: int | None = Field(None, ge=0, le=150)
    address: Address | None = None

@app.post("/users/", status_code=201)
async def create_user(user: UserCreate):
    return {"id": 1, "email": user.email, "address": user.address}

# POST /users/ {"email":"a@b.com","password":"12345678","address":{"street":"路","city":"北京","zip_code":"100000"}}
# → 201 创建成功
# POST /users/ {"email":"invalid","password":"123"} → 422: email 格式错误 + password 太短
```

预期运行结果：嵌套 Model 递归校验，EmailStr 自动验证邮箱格式，所有约束同时检查。

**示例 3：完整场景——请求体 + 路径参数 + 查询参数组合**

```python
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field

app = FastAPI()

class ItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    price: float | None = Field(None, gt=0)
    description: str | None = Field(None, max_length=1000)

@app.put("/items/{item_id}")
async def update_item(
    item_id: int = Path(..., ge=1),
    item: ItemUpdate,
    partial: bool = Query(False, description="是否部分更新"),
):
    """更新商品：路径参数定位资源，请求体携带更新数据，查询参数控制更新模式"""
    update_data = item.model_dump(exclude_unset=True)  # 只包含客户端传了的字段
    return {"item_id": item_id, "updated_fields": list(update_data.keys()), "partial": partial}

# PUT /items/42?partial=true {"name":"新名字"}
# → {"item_id":42,"updated_fields":["name"],"partial":true}
# PUT /items/42 {"price":-10} → 422: price 必须 > 0
```

预期运行结果：`exclude_unset=True` 只序列化客户端显式传入的字段，实现 PATCH 语义的部分更新。

#### 使用场景与最佳实践

**适用场景**：创建资源（POST）、全量更新（PUT）、部分更新（PATCH）、复杂查询条件（POST search）、批量操作。

**不适用场景**：简单的资源获取（用 GET + 查询参数）；小量数据传递（用查询参数）；文件上传（用 Form/File）。

**最佳实践**：
1. 为创建和更新分别定义不同的 Model（UserCreate / UserUpdate），更新用 `| None` 支持部分更新
2. 始终用 `Field()` 添加约束和 description，让 OpenAPI 文档专业可用
3. 敏感字段（password）只在请求 Model 中出现，不要在响应 Model 中出现
4. 用 `model_dump(exclude_unset=True)` 区分「未传」和「传了 None」
5. 嵌套 Model 用于复杂结构（地址、配置等），但避免过深嵌套（超过 3 层影响可读性）

**性能建议**：Pydantic v2 校验极快，但超大请求体（>1MB）的 JSON 解析仍有开销。对大请求体设置 `Body(..., media_type="application/json")` 并考虑请求体大小限制中间件。

#### 常见坑点

**坑点 1：请求体中传了未定义的字段被忽略**

- 错误现象：客户端传了 `extra_field`，但服务端不报错也不处理，调试困难
- 根本原因：Pydantic 默认忽略未定义的字段（`extra="ignore"`）
- 正确做法：在 Model Config 中设置 `extra="forbid"` 禁止额外字段，或 `extra="allow"` 允许并保留
- 预防措施：对外 API 建议 `extra="forbid"`，帮助客户端发现拼写错误的字段名

```python
from pydantic import BaseModel, ConfigDict

class StrictItem(BaseModel):
    model_config = ConfigDict(extra="forbid")  # 禁止额外字段
    name: str
    price: float

# POST {"name":"iPhone","price":999,"extra":"oops"} → 422: 额外字段不允许
```

**坑点 2：更新接口中 None 和未传无法区分**

- 错误现象：PATCH 接口中客户端想把某个字段设为 None，但服务端无法区分「设为 None」和「没传这个字段」
- 根本原因：默认 `model_dump()` 会把所有 None 字段都包含，无法区分
- 正确做法：用 `model_dump(exclude_unset=True)` 只包含客户端显式设置的字段；字段类型用 `X | None`
- 预防措施：所有 PATCH/部分更新接口统一使用 `exclude_unset=True`

```python
from pydantic import BaseModel

class UserUpdate(BaseModel):
    name: str | None = None
    age: int | None = None

# 客户端传 {"name": None}
user = UserUpdate(name=None)
user.model_dump()              # {"name": None, "age": None} — 无法区分
user.model_dump(exclude_unset=True)  # {"name": None} — 只包含传了的字段
```

---

### 3.2 Header 参数

#### 概念解释

**Header 参数是 HTTP 请求头中的键值对，用于传递元数据如认证 Token、内容类型、用户代理、请求 ID 等。** FastAPI 通过 `Header()` 函数声明 Header 参数，自动从请求头中提取并转换。

打个比方：Header 像信件的信封——上面写着寄件人地址（Origin）、信件类型（Content-Type）、紧急程度（X-Priority）、追踪编号（X-Request-ID）等元信息。信封上的信息不影响信件内容（请求体），但影响信件如何被处理和路由。

**核心价值**：Header 参数让认证、内容协商、链路追踪等横切关注点可以声明式注入，无需在每个函数中手动 `request.headers.get("Authorization")`。

#### 原理说明：Header 参数解析机制

```mermaid
graph LR
    A[请求头: Authorization: Bearer xxx<br/>User-Agent: Mozilla/5.0<br/>X-Request-ID: abc123] --> B[Starlette Request.headers]
    B --> C[FastAPI Header() 匹配]
    C --> D[自动下划线转连字符<br/>user_agent → User-Agent]
    D --> E[类型转换与校验]
    E --> F[注入路由函数]
```

**Header 参数的特殊规则**：

| 规则 | 说明 | 示例 |
|------|------|------|
| 下划线自动转连字符 | `user_agent` → `User-Agent` | `user_agent: str = Header(None)` |
| 禁用转换 | `convert_underscores=False` | `user_agent: str = Header(None, convert_underscores=False)` |
| 多值 Header | `list[str]` 收集同名 Header | `x_trace_id: list[str] = Header([])` |
| 不区分大小写 | HTTP Header 名不区分大小写 | `Authorization` 和 `authorization` 相同 |

> 🎯 面试高频：FastAPI 中 Header 参数为什么默认把下划线转为连字符？因为 HTTP Header 规范中使用连字符（`User-Agent`），而 Python 变量名不能用连字符，所以 FastAPI 自动将 `user_agent` 转换为 `User-Agent` 来匹配请求头。如果需要匹配带下划线的 Header（不规范但存在），设置 `convert_underscores=False`。

#### 代码示例

**示例 1：基础 Header 参数**

```python
from fastapi import FastAPI, Header

app = FastAPI()

@app.get("/headers/")
async def read_headers(
    user_agent: str | None = Header(None),
    x_request_id: str | None = Header(None),
    accept_language: str | None = Header(None),
):
    return {
        "user_agent": user_agent,
        "x_request_id": x_request_id,
        "accept_language": accept_language,
    }

# curl -H "User-Agent: MyApp/1.0" -H "X-Request-ID: abc123" http://localhost:8000/headers/
# → {"user_agent":"MyApp/1.0","x_request_id":"abc123","accept_language":null}
```

预期运行结果：`user_agent` 自动匹配 `User-Agent` Header，`x_request_id` 匹配 `X-Request-ID`。

**示例 2：认证 Header 与多值 Header**

```python
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

@app.get("/protected")
async def protected(
    authorization: str = Header(..., description="Bearer Token"),
    x_forwarded_for: list[str] = Header([], description="代理链"),
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")
    token = authorization.split(" ")[1]
    return {"token": token[:10] + "...", "proxy_chain": x_forwarded_for}

# curl -H "Authorization: Bearer my-secret-token" -H "X-Forwarded-For: 1.1.1.1" -H "X-Forwarded-For: 2.2.2.2" http://localhost:8000/protected
# → {"token":"my-secret...","proxy_chain":["1.1.1.1","2.2.2.2"]}
```

预期运行结果：`authorization` 为必需 Header，缺失返回 422；`x_forwarded_for` 为列表，收集所有同名 Header。

**示例 3：完整场景——基于 Header 的国际化与版本控制**

```python
from fastapi import FastAPI, Header, HTTPException
from enum import Enum

app = FastAPI()

class Language(str, Enum):
    zh_cn = "zh-CN"
    en_us = "en-US"
    ja_jp = "ja-JP"

SUPPORTED_VERSIONS = {"v1", "v2"}

@app.get("/api/content")
async def get_content(
    accept_language: Language = Header(Language.zh_cn, description="语言偏好"),
    x_api_version: str = Header("v1", description="API 版本"),
):
    """基于 Header 的内容协商：语言国际化 + API 版本控制"""
    if x_api_version not in SUPPORTED_VERSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的 API 版本: {x_api_version}")

    messages = {
        Language.zh_cn: {"v1": "欢迎使用 v1 接口", "v2": "欢迎使用 v2 接口（新版）"},
        Language.en_us: {"v1": "Welcome to v1 API", "v2": "Welcome to v2 API (new)"},
        Language.ja_jp: {"v1": "v1 APIへようこそ", "v2": "v2 APIへようこそ（新）"},
    }
    return {
        "language": accept_language.value,
        "version": x_api_version,
        "message": messages[accept_language][x_api_version],
    }

# curl -H "Accept-Language: en-US" -H "X-API-Version: v2" http://localhost:8000/api/content
# → {"language":"en-US","version":"v2","message":"Welcome to v2 API (new)"}
```

预期运行结果：通过 Header 实现语言切换和 API 版本控制，无需修改 URL 路径。

#### 使用场景与最佳实践

**适用场景**：认证授权（Authorization）、内容协商（Accept/Accept-Language）、链路追踪（X-Request-ID/X-Trace-ID）、API 版本控制（X-API-Version）、幂等性控制（Idempotency-Key）、缓存控制（If-None-Match/If-Modified-Since）。

**不适用场景**：业务数据（用请求体）、大量参数（Header 总大小通常限制 8KB）、敏感信息长期存储（用 Cookie 或 Authorization）。

**最佳实践**：
1. 认证 Token 用 `Authorization: Bearer <token>` 标准格式
2. 自定义 Header 用 `X-` 前缀（虽然 RFC 6648 不推荐，但行业惯例仍广泛使用）
3. 请求 ID 用 `X-Request-ID`，在微服务间透传实现链路追踪
4. 多值 Header 用 `list[str]` 类型
5. 必需 Header 用 `Header(...)`，可选 Header 用 `Header(None)` 或 `Header(default)`

**性能建议**：Header 解析开销极小，但避免在 Header 中传递大段数据（如 JWT Token 超过 4KB 可能被部分代理截断）。

#### 常见坑点

**坑点 1：Header 名大小写和下划线转换问题**

- 错误现象：定义 `x_custom_header: str = Header(None)`，但客户端发的是 `X-Custom-Header`，取不到值
- 根本原因：默认 `convert_underscores=True`，`x_custom_header` 会被转为 `x-custom-header`（全小写），HTTP Header 不区分大小写所以应该能匹配；但如果客户端发的 Header 名本身带下划线，需要禁用转换
- 正确做法：理解自动转换规则，需要匹配带下划线的 Header 时设 `convert_underscores=False`
- 预防措施：统一使用连字符命名自定义 Header，避免下划线

```python
from fastapi import FastAPI, Header

app = FastAPI()

# 默认：x_custom_header → 匹配 X-Custom-Header
@app.get("/default")
async def default(x_custom_header: str = Header(None)):
    return {"value": x_custom_header}

# 禁用转换：精确匹配 X_Custom_Header（带下划线）
@app.get("/raw")
async def raw(x_custom_header: str = Header(None, convert_underscores=False)):
    return {"value": x_custom_header}
```

**坑点 2：在路由函数中同时注入 Request 和 Header 参数导致重复**

- 错误现象：既注入了 `request: Request` 又声明了 `authorization: str = Header(...)`，代码冗余
- 根本原因：两者都能获取 Header，但 `Header()` 更声明式且自动校验
- 正确做法：需要单个 Header 用 `Header()`，需要访问所有 Header 或请求元数据时才注入 `Request`
- 预防措施：优先用 `Header()` 声明式注入，避免手动 `request.headers.get()`

---

### 3.3 Cookie 参数

#### 概念解释

**Cookie 是服务器通过 Set-Cookie 响应头设置、浏览器自动在后续请求中携带的小型数据片段，用于会话管理、用户偏好、跟踪等。** FastAPI 通过 `Cookie()` 函数声明 Cookie 参数，自动从请求 Cookie 中提取。

打个比方：Cookie 像游乐园的手环——入园时工作人员给你戴上手环（Set-Cookie），之后每个游乐项目（后续请求）你都不需要再买票，工作人员扫一下手环（自动携带 Cookie）就知道你已付费。手环上可以记录你的身份、VIP 等级、入场时间等信息。

**核心价值**：Cookie 参数让会话管理声明式化，无需手动解析 `Cookie` 请求头字符串，FastAPI 自动提取命名 Cookie 的值。

#### 原理说明：Cookie 工作流程

```mermaid
sequenceDiagram
    participant C as 客户端（浏览器）
    participant S as FastAPI 服务器
    C->>S: POST /login（用户名密码）
    S->>S: 验证通过，生成 session_id
    S-->>C: 200 + Set-Cookie: session_id=abc123; HttpOnly; Secure; Path=/
    C->>S: GET /profile（自动携带 Cookie: session_id=abc123）
    S->>S: Cookie() 提取 session_id
    S-->>C: 200 用户资料
```

**Cookie 的安全属性**：

| 属性 | 说明 | 安全建议 |
|------|------|---------|
| `HttpOnly` | 禁止 JavaScript 访问，防 XSS 窃取 | 会话 Cookie 必须设置 |
| `Secure` | 仅在 HTTPS 下传输 | 生产环境必须设置 |
| `SameSite` | 控制跨站请求是否携带，防 CSRF | 设为 `Lax` 或 `Strict` |
| `Max-Age`/`Expires` | 过期时间 | 会话 Cookie 不设（浏览器关闭即失效） |
| `Path` | Cookie 生效路径 | 设为 `/` 或具体路径 |
| `Domain` | Cookie 生效域名 | 设为当前域名，避免过宽 |

> 🎯 面试高频：Cookie 和 Session 的区别？Cookie 是客户端存储机制（数据存在浏览器，每次请求自动携带），Session 是服务端存储机制（数据存在服务器，Cookie 中只存 session_id）。FastAPI 中可以用 Cookie 存 session_id，服务端用 Redis/数据库查 Session 数据，也可以用 JWT 把数据存在客户端（无状态）。

#### 代码示例

**示例 1：读取 Cookie**

```python
from fastapi import FastAPI, Cookie

app = FastAPI()

@app.get("/items/")
async def read_items(session_id: str | None = Cookie(None)):
    return {"session_id": session_id}

# curl --cookie "session_id=abc123" http://localhost:8000/items/
# → {"session_id":"abc123"}
# curl http://localhost:8000/items/ → {"session_id":null}
```

预期运行结果：`Cookie()` 自动从请求 Cookie 中提取 `session_id` 的值。

**示例 2：设置和读取 Cookie（登录会话）**

```python
from fastapi import FastAPI, Cookie, Response
from pydantic import BaseModel
import uuid

app = FastAPI()

# 模拟会话存储（生产用 Redis）
sessions: dict[str, dict] = {}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(login: LoginRequest, response: Response):
    # 验证用户（简化示例）
    if login.username == "admin" and login.password == "password":
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"username": login.username, "role": "admin"}
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600,
            path="/",
        )
        return {"message": "登录成功"}
    return {"message": "用户名或密码错误"}

@app.get("/profile")
async def profile(session_id: str | None = Cookie(None)):
    if not session_id or session_id not in sessions:
        return {"message": "未登录"}
    return {"user": sessions[session_id]}

@app.post("/logout")
async def logout(response: Response, session_id: str | None = Cookie(None)):
    if session_id:
        sessions.pop(session_id, None)
    response.delete_cookie("session_id")
    return {"message": "已退出登录"}
```

预期运行结果：登录成功后设置 HttpOnly+Secure 的 Cookie，后续请求自动携带，`/profile` 识别用户身份，登出时删除 Cookie。

**示例 3：完整场景——基于 Cookie 的用户偏好与 A/B 测试**

```python
from fastapi import FastAPI, Cookie, Response
from pydantic import BaseModel
import random

app = FastAPI()

class ThemePreference(BaseModel):
    theme: str = "light"
    language: str = "zh-CN"
    timezone: str = "Asia/Shanghai"

@app.get("/preferences")
async def get_preferences(
    preferences: str | None = Cookie(None, description="用户偏好 Cookie"),
):
    """读取用户偏好 Cookie，不存在则返回默认值"""
    if preferences:
        import json
        try:
            return json.loads(preferences)
        except json.JSONDecodeError:
            pass
    return ThemePreference().model_dump()

@app.post("/preferences")
async def set_preferences(
    prefs: ThemePreference,
    response: Response,
):
    """设置用户偏好 Cookie，用于 A/B 测试分组"""
    import json
    response.set_cookie(
        key="preferences",
        value=json.dumps(prefs.model_dump()),
        httponly=False,  # 前端需要读取主题
        secure=True,
        samesite="lax",
        max_age=86400 * 30,  # 30 天
    )
    # A/B 测试分组
    group = "A" if random.random() < 0.5 else "B"
    response.set_cookie(key="ab_group", value=group, httponly=True, secure=True, max_age=86400 * 30)
    return {"preferences": prefs.model_dump(), "ab_group": group}

@app.get("/experiment")
async def get_experiment(ab_group: str | None = Cookie(None)):
    """根据 A/B 分组返回不同版本的内容"""
    if ab_group == "A":
        return {"version": "A", "layout": "经典版", "button_color": "blue"}
    elif ab_group == "B":
        return {"version": "B", "layout": "新版", "button_color": "green"}
    return {"version": "default", "layout": "默认版"}
```

预期运行结果：用户偏好存在 Cookie 中（前端可读，用于主题切换），A/B 分组存在 HttpOnly Cookie 中（前端不可篡改），实验接口根据分组返回不同内容。

#### 使用场景与最佳实践

**适用场景**：会话管理（登录状态）、用户偏好（主题、语言）、A/B 测试分组、购物车（未登录用户）、跟踪分析（匿名用户 ID）。

**不适用场景**：大量数据（Cookie 通常限制 4KB）、敏感数据（即使 HttpOnly 也可能被 CSRF 利用）、跨域共享（Cookie 受同源策略限制）。

**最佳实践**：
1. 会话 Cookie 必须设置 `HttpOnly=True`、`Secure=True`、`SameSite="Lax"`
2. Cookie 中只存标识符（session_id），实际数据存服务端（Redis）
3. 敏感操作（转账、改密码）需额外 CSRF Token，不能仅依赖 Cookie
4. 设置合理的 `max_age`，会话 Cookie 不设过期时间（浏览器关闭失效）
5. 生产环境 `Secure=True`，开发环境可设 False（但注意本地用 http）

**性能建议**：Cookie 在每个请求中自动携带，避免存储大量数据。每个域名 Cookie 总数通常限制 50 个，总大小 4KB。

#### 常见坑点

**坑点 1：Cookie 在跨域请求中不携带**

- 错误现象：前后端分离项目中，登录后设置了 Cookie，但后续跨域请求不携带 Cookie
- 根本原因：CORS 跨域请求默认不携带 Cookie，需要前端 `fetch` 设置 `credentials: 'include'`，后端 CORS 配置 `allow_credentials=True` 且 `allow_origins` 不能是 `*`
- 正确做法：前端 `fetch(url, {credentials: 'include'})`，后端 `CORSMiddleware(allow_origins=["https://app.example.com"], allow_credentials=True)`
- 预防措施：前后端分离项目一开始就配置好 CORS + Cookie 携带

**坑点 2：set_cookie 后路由函数返回 dict 导致 Cookie 不生效**

- 错误现象：调用了 `response.set_cookie()`，但浏览器没有收到 Cookie
- 根本原因：如果路由函数返回 dict，FastAPI 创建新的 JSONResponse，而你修改的是注入的 `response` 对象——但 FastAPI 会使用注入的 response 对象，所以应该生效。常见原因是 `response` 参数名不对或返回了自定义 Response 覆盖了
- 正确做法：确保注入 `response: Response` 参数，调用 `set_cookie` 后返回 dict（FastAPI 会复用这个 response 对象）
- 预防措施：设置 Cookie 后检查响应头中是否有 `Set-Cookie`

```python
from fastapi import FastAPI, Response

app = FastAPI()

# 正确：注入 Response 并设置 Cookie，返回 dict
@app.post("/login")
async def login(response: Response):
    response.set_cookie(key="session", value="abc", httponly=True)
    return {"message": "ok"}  # FastAPI 会复用 response 对象，Cookie 生效

# 正确：直接返回 Response 子类
from fastapi.responses import JSONResponse
@app.post("/login2")
async def login2():
    resp = JSONResponse(content={"message": "ok"})
    resp.set_cookie(key="session", value="abc", httponly=True)
    return resp
```

---

### 3.4 表单数据与文件上传

#### 概念解释

**表单数据（Form）是 `application/x-www-form-urlencoded` 或 `multipart/form-data` 格式的请求体，用于传统表单提交和文件上传。** FastAPI 通过 `Form()` 和 `File()` / `UploadFile` 声明式处理表单字段和文件。

打个比方：表单数据像填写纸质申请表——每个字段（姓名、邮箱）是一个 Form 字段，附上的照片/文件是 File 字段。`multipart/form-data` 是「带附件的申请表」，可以同时包含文字和文件；`application/x-www-form-urlencoded` 是「纯文字申请表」，只能传文字。

**核心价值**：FastAPI 让文件上传和表单处理与 JSON 请求体一样声明式，`UploadFile` 提供异步文件操作和自动临时文件存储，避免大文件内存溢出。

#### 原理说明：表单与文件处理机制

```mermaid
graph TB
    A[multipart/form-data 请求] --> B[Starlette 解析 multipart]
    B --> C[普通表单字段 → Form()]
    B --> D[文件字段 → UploadFile]
    D --> E[SpooledTemporaryFile<br/>小文件内存 / 大文件磁盘]
    E --> F[异步 read / write / seek]
    C --> G[注入路由函数]
    F --> G
```

**Form vs File vs JSON 请求体对比**：

| 特性 | Form() | File() / UploadFile | Pydantic Body |
|------|--------|---------------------|---------------|
| Content-Type | x-www-form-urlencoded | multipart/form-data | application/json |
| 用途 | 表单字段 | 文件上传 | JSON 数据 |
| 类型 | str/int 等简单类型 | bytes / UploadFile | Pydantic Model |
| 异步 | 否 | 是（UploadFile） | 否（解析时） |
| 大文件 | 不适用 | 支持（流式） | 不适用 |

> 🎯 面试高频：`bytes` 和 `UploadFile` 接收文件的区别？`bytes` 会把整个文件加载到内存，适合小文件（< 1MB）；`UploadFile` 使用 SpooledTemporaryFile，小文件在内存、大文件自动写磁盘，支持异步操作和 `file.filename`/`file.content_type` 元数据，适合大文件和生产环境。

#### 代码示例

**示例 1：基础表单提交**

```python
from fastapi import FastAPI, Form

app = FastAPI()

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username, "password_length": len(password)}

# curl -X POST -d "username=admin&password=secret123" http://localhost:8000/login/
# → {"username":"admin","password_length":9}
# Content-Type: application/x-www-form-urlencoded
```

预期运行结果：`Form()` 从表单数据中提取字段，`...` 表示必填。

**示例 2：单文件上传（UploadFile）**

```python
from fastapi import FastAPI, File, UploadFile
from pathlib import Path

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(..., description="上传文件")):
    """上传文件并保存到本地，返回文件信息"""
    # 读取文件内容（异步）
    content = await file.read()
    # 保存到磁盘
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        f.write(content)
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "saved_to": str(file_path),
    }

# curl -X POST -F "file=@photo.jpg" http://localhost:8000/upload/
# → {"filename":"photo.jpg","content_type":"image/jpeg","size":123456,...}
```

预期运行结果：`UploadFile` 提供文件名、内容类型、异步读取方法，文件保存到本地。

**示例 3：完整场景——多文件上传 + 表单字段 + 文件校验**

```python
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from pathlib import Path
import aiofiles

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "application/pdf"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/gallery/")
async def upload_gallery(
    title: str = Form(..., min_length=1, max_length=100, description="相册标题"),
    description: str = Form("", max_length=500),
    files: list[UploadFile] = File(..., description="多张图片，最多9张"),
):
    """多文件上传：表单字段 + 文件列表 + 类型/大小校验 + 异步保存"""
    if len(files) > 9:
        raise HTTPException(status_code=400, detail="最多上传9张图片")

    saved_files = []
    for file in files:
        # 校验类型
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.content_type}")

        # 读取并校验大小
        content = await file.read()
        if len(content) > MAX_SIZE:
            raise HTTPException(status_code=400, detail=f"文件过大: {file.filename}")

        # 异步保存
        safe_name = f"{title}_{file.filename}"
        file_path = UPLOAD_DIR / safe_name
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        saved_files.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "path": str(file_path),
        })
        await file.close()

    return {"title": title, "description": description, "uploaded": saved_files, "count": len(saved_files)}

# curl -X POST -F "title=旅行照片" -F "description=三亚之旅" -F "files=@1.jpg" -F "files=@2.jpg" http://localhost:8000/gallery/
# → 上传多张图片，返回每张的保存信息
```

预期运行结果：支持多文件上传、表单字段、类型校验、大小限制、异步保存，返回完整上传报告。

#### 使用场景与最佳实践

**适用场景**：用户头像/图片上传、文档/PDF 上传、传统 HTML 表单提交、批量文件导入、大文件分片上传。

**不适用场景**：纯 JSON 数据交互（用 Pydantic Body）、小配置项传递（用查询参数）、二进制流下载（用 StreamingResponse）。

**最佳实践**：
1. 生产环境始终用 `UploadFile` 而非 `bytes`，避免大文件内存溢出
2. 校验文件类型（`content_type`）和大小，不要信任客户端声明的类型
3. 文件名要做安全处理（防止路径穿越攻击），不要直接用 `file.filename` 拼接路径
4. 大文件用分片上传（前端切片 + 后端合并），避免单次请求超时
5. 上传文件存储到对象存储（S3/OSS）而非本地磁盘，便于扩展和备份

**性能建议**：`UploadFile` 默认阈值 1MB（超过写磁盘），可通过 `UploadFile(..., max_size=...)` 调整。高并发上传场景使用对象存储直传（前端直接传 S3，后端只签名），减轻服务器压力。

#### 常见坑点

**坑点 1：文件上传时忘记安装 python-multipart**

- 错误现象：使用 `Form()` 或 `File()` 时报 `AssertionError: The python-multipart package must be installed to use form data`
- 根本原因：FastAPI 解析 multipart/form-data 依赖 `python-multipart` 库，但它不是 FastAPI 的强制依赖
- 正确做法：`pip install python-multipart`
- 预防措施：requirements.txt 中包含 `python-multipart`，只要项目有表单/文件上传就必须安装

**坑点 2：文件名字符串导致路径穿越攻击**

- 错误现象：用户上传文件名为 `../../etc/passwd`，文件被写入系统目录
- 根本原因：直接用 `file.filename` 拼接保存路径，攻击者构造恶意文件名穿越目录
- 正确做法：用 `Path(file.filename).name` 只取文件名部分，或生成随机文件名（UUID + 原扩展名）
- 预防措施：始终对文件名做 sanitize，生产环境用随机文件名

```python
from pathlib import Path
import uuid

# 安全：只取文件名部分，去除路径
safe_filename = Path(file.filename).name

# 更安全：生成随机文件名，保留扩展名
ext = Path(file.filename).suffix
safe_filename = f"{uuid.uuid4()}{ext}"

file_path = UPLOAD_DIR / safe_filename
```

---

> 💡 **本章深度讲解**：请求体、Header、Cookie、表单文件是 FastAPI 接收客户端数据的四种方式。请求体（Pydantic Model）用于结构化 JSON 数据，是最常用的方式；Header 用于元数据和认证；Cookie 用于会话和偏好；表单文件用于传统表单和文件上传。核心要记住：① Pydantic Model 是请求体的标准方式，自动校验+文档；② Header 自动下划线转连字符；③ Cookie 必须设置 HttpOnly+Secure+SameSite 安全属性；④ 文件上传用 UploadFile 而非 bytes，校验类型和大小，文件名做安全处理。
>
> 📝 **本章精简总结**：
> 1. 请求体用 Pydantic Model，自动 JSON 解析+校验+文档，Field() 添加约束
> 2. Pydantic v2 用 model_dump() 替代 .dict()，from_attributes 替代 from_orm
> 3. 更新接口用 model_dump(exclude_unset=True) 区分未传和传了 None
> 4. Header 参数自动下划线转连字符，多值用 list[str]
> 5. Cookie 用 Cookie() 读取，response.set_cookie() 设置，必须 HttpOnly+Secure
> 6. 表单/文件上传需安装 python-multipart
> 7. 文件上传用 UploadFile（异步+临时文件），不用 bytes（全量内存）
> 8. 上传文件名必须做安全处理，防止路径穿越攻击

🎯 **梯度练习题**

**基础题⭐**
1. 定义一个 Pydantic Model `Product`，包含 name（str，2-100字符）、price（float，>0）、stock（int，>=0）、description（可选 str）。
2. 写一个接口读取 `User-Agent` 和 `X-Request-ID` 两个 Header 并返回。
3. 文件上传时 `bytes` 和 `UploadFile` 有什么区别？生产环境应该用哪个？

**进阶题⭐⭐**
4. 解释 Pydantic v2 中 `model_dump()` 和 `model_dump(exclude_unset=True)` 的区别，在 PATCH 接口中为什么必须用后者？
5. 实现一个登录接口：POST /login 接收 username/password 表单，验证成功后设置 HttpOnly+Secure 的 session_id Cookie，GET /profile 读取 Cookie 返回用户信息，POST /logout 删除 Cookie。

**实战题⭐⭐⭐**
6. 实现一个完整的文件上传接口：支持多文件上传（最多 5 个）、每个文件类型校验（仅图片）、大小限制（5MB）、文件名安全处理、异步保存到本地、返回每个文件的 URL。同时实现 GET /files/{filename} 下载接口。

---

## 四、HTTP 方法语义与路径操作装饰器

### 4.1 HTTP 方法语义与 RESTful 设计

#### 概念解释

**HTTP 方法（GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS）是对资源操作语义的标准化表达，每个方法有明确的幂等性、安全性和用途约定。** FastAPI 通过 `@app.get()`、`@app.post()` 等装饰器将路由函数绑定到特定 HTTP 方法。

打个比方：HTTP 方法像图书馆的操作指令——GET 是「查一下这本书的信息」（只读、不改变），POST 是「新增一本书」（创建），PUT 是「把这本书替换成另一本」（全量替换），PATCH 是「修改这本书的部分信息」（部分更新），DELETE 是「把这本书下架」（删除）。每个指令有明确的预期效果。

**核心价值**：遵循 HTTP 方法语义让 API 具有自描述性和可预测性，客户端和缓存服务器（CDN）可以基于方法语义做缓存、重试等优化。

#### 原理说明：HTTP 方法特性对比

```mermaid
graph LR
    subgraph 安全方法（只读）
        GET[GET<br/>查询资源]
        HEAD[HEAD<br/>查询响应头]
        OPTIONS[OPTIONS<br/>查询支持的方法]
    end
    subgraph 幂等方法
        PUT[PUT<br/>全量替换]
        DELETE[DELETE<br/>删除资源]
    end
    subgraph 非幂等方法
        POST[POST<br/>创建资源]
        PATCH[PATCH<br/>部分更新]
    end
    GET -->|可缓存| C[CDN/浏览器缓存]
    POST -->|不可缓存| N[每次执行]
```

| 方法 | 用途 | 安全 | 幂等 | 可缓存 | 请求体 | 典型状态码 |
|------|------|------|------|--------|--------|-----------|
| GET | 查询资源 | ✅ | ✅ | ✅ | 无 | 200 |
| POST | 创建资源 | ❌ | ❌ | ❌ | 有 | 201 |
| PUT | 全量替换 | ❌ | ✅ | ❌ | 有 | 200/204 |
| PATCH | 部分更新 | ❌ | ❌ | ❌ | 有 | 200 |
| DELETE | 删除资源 | ❌ | ✅ | ❌ | 无 | 200/204 |
| HEAD | 查询响应头 | ✅ | ✅ | ✅ | 无 | 200 |
| OPTIONS | 查询支持方法 | ✅ | ✅ | ❌ | 无 | 200 |

> 🎯 面试高频：PUT 和 PATCH 的区别？PUT 是全量替换——客户端发送完整的资源表示，服务器用它完全替换现有资源（未传的字段会被设为默认值/删除）；PATCH 是部分更新——客户端只发送需要修改的字段，未传的字段保持不变。PUT 是幂等的（多次执行结果相同），PATCH 不一定幂等（如 `{ "count": count + 1 }` 多次执行结果不同）。

#### 代码示例

**示例 1：标准 CRUD 接口设计**

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=2)
    price: float = Field(..., gt=0)

class ItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=2)
    price: float | None = Field(None, gt=0)

# 内存数据库
items_db: dict[int, dict] = {}
next_id = 1

@app.get("/items/", summary="获取商品列表")
async def list_items():
    """GET: 查询所有商品（安全、幂等、可缓存）"""
    return list(items_db.values())

@app.post("/items/", status_code=status.HTTP_201_CREATED, summary="创建商品")
async def create_item(item: ItemCreate):
    """POST: 创建新商品（非安全、非幂等）"""
    global next_id
    new_item = {"id": next_id, **item.model_dump()}
    items_db[next_id] = new_item
    next_id += 1
    return new_item

@app.get("/items/{item_id}", summary="获取单个商品")
async def get_item(item_id: int):
    """GET: 查询单个商品"""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="商品不存在")
    return items_db[item_id]

@app.put("/items/{item_id}", summary="全量替换商品")
async def replace_item(item_id: int, item: ItemCreate):
    """PUT: 全量替换（幂等）"""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="商品不存在")
    items_db[item_id] = {"id": item_id, **item.model_dump()}
    return items_db[item_id]

@app.patch("/items/{item_id}", summary="部分更新商品")
async def update_item(item_id: int, item: ItemUpdate):
    """PATCH: 部分更新（非幂等）"""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="商品不存在")
    update_data = item.model_dump(exclude_unset=True)
    items_db[item_id].update(update_data)
    return items_db[item_id]

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除商品")
async def delete_item(item_id: int):
    """DELETE: 删除商品（幂等）"""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="商品不存在")
    del items_db[item_id]
    # 204 No Content：删除成功不返回响应体
```

预期运行结果：完整的 CRUD 接口，每个方法语义正确，POST 返回 201，DELETE 返回 204。

**示例 2：幂等性演示——PUT vs POST**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

counter = {"value": 0}
resources: dict[int, dict] = {}

class Resource(BaseModel):
    name: str

# POST：非幂等，每次调用创建新资源
@app.post("/resources/")
async def create_resource(resource: Resource):
    counter["value"] += 1
    new_id = counter["value"]
    resources[new_id] = {"id": new_id, **resource.model_dump()}
    return resources[new_id]
# 调用 3 次 → 创建 3 个资源，id 分别为 1,2,3

# PUT：幂等，多次调用结果相同
@app.put("/resources/{resource_id}")
async def replace_resource(resource_id: int, resource: Resource):
    resources[resource_id] = {"id": resource_id, **resource.model_dump()}
    return resources[resource_id]
# 对 /resources/1 调用 3 次 → 资源 1 被替换 3 次，最终状态相同
```

预期运行结果：POST 每次创建新资源（非幂等），PUT 对同一 ID 多次调用结果相同（幂等）。

**示例 3：完整场景——订单接口的方法语义设计**

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from enum import Enum

app = FastAPI()

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    cancelled = "cancelled"

class OrderCreate(BaseModel):
    product_id: int = Field(..., ge=1)
    quantity: int = Field(..., ge=1, le=100)
    address: str = Field(..., min_length=5)

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

orders_db: dict[int, dict] = {}
order_seq = 0

@app.post("/orders/", status_code=201, summary="创建订单")
async def create_order(order: OrderCreate):
    """POST 创建订单：每次调用生成新订单号"""
    global order_seq
    order_seq += 1
    new_order = {
        "id": order_seq,
        **order.model_dump(),
        "status": OrderStatus.pending.value,
    }
    orders_db[order_seq] = new_order
    return new_order

@app.get("/orders/{order_id}", summary="查询订单")
async def get_order(order_id: int):
    """GET 查询订单：只读，可缓存"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="订单不存在")
    return orders_db[order_id]

@app.patch("/orders/{order_id}/status", summary="更新订单状态")
async def update_order_status(order_id: int, update: OrderStatusUpdate):
    """PATCH 更新订单状态：部分修改，状态机校验"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="订单不存在")
    order = orders_db[order_id]
    # 状态机校验：已取消的订单不能再修改
    if order["status"] == OrderStatus.cancelled.value:
        raise HTTPException(status_code=400, detail="已取消的订单不能修改状态")
    order["status"] = update.status.value
    return order

@app.delete("/orders/{order_id}", status_code=204, summary="取消订单")
async def cancel_order(order_id: int):
    """DELETE 取消订单：幂等，重复取消不报错"""
    if order_id in orders_db:
        orders_db[order_id]["status"] = OrderStatus.cancelled.value
    # 即使订单不存在也返回 204（幂等删除），或返回 404（严格模式）
```

预期运行结果：订单接口遵循方法语义——POST 创建、GET 查询、PATCH 状态更新（含状态机校验）、DELETE 取消（幂等）。

#### 使用场景与最佳实践

**适用场景**：所有 RESTful API 设计；资源的 CRUD 操作；需要 CDN 缓存的查询接口；需要重试安全的操作（幂等方法）。

**不适用场景**：复杂的 RPC 风格操作（如「批量导入」「触发计算」），可用 POST + 动作路径（`/imports/`、`/jobs/`）；需要事务的多步骤操作。

**最佳实践**：
1. 路径用名词复数（`/items/`、`/orders/`），不用动词（`/getItems`、`/createOrder`）
2. GET 不修改数据，POST 创建，PUT 全量替换，PATCH 部分更新，DELETE 删除
3. POST 成功返回 201 + Location 响应头指向新资源 URL
4. DELETE 成功返回 204 No Content
5. 幂等操作（PUT/DELETE）重复调用不应报错或产生副作用
6. 查询接口用 GET，操作接口用 POST（即使是「查询」但需要复杂请求体时可用 POST /search）

**性能建议**：GET 接口添加合适的 Cache-Control 响应头，利用 CDN 和浏览器缓存。POST/PUT/PATCH/DELETE 不可缓存，避免在这些接口中做只读查询。

#### 常见坑点

**坑点 1：用 GET 做修改操作**

- 错误现象：用 `@app.get("/delete-item/{id}")` 实现删除，导致搜索引擎爬虫或浏览器预加载误删数据
- 根本原因：GET 是安全方法，爬虫、CDN、浏览器会主动请求 GET 链接，且 GET 请求可被缓存和重试
- 正确做法：删除用 DELETE，修改用 PUT/PATCH，创建用 POST
- 预防措施：代码审查时检查所有 GET 接口是否有副作用（修改数据库、发邮件等）

**坑点 2：POST 和 PUT 的使用场景混淆**

- 错误现象：所有写操作都用 POST，包括更新和删除
- 根本原因：不理解 HTTP 方法语义，或图省事只用 POST
- 正确做法：创建用 POST，全量更新用 PUT，部分更新用 PATCH，删除用 DELETE
- 预防措施：团队制定 API 设计规范，代码审查时检查方法使用是否正确

---

### 4.2 路径操作装饰器的高级参数

#### 概念解释

**路径操作装饰器（`@app.get()`、`@app.post()` 等）除了路径和方法，还支持丰富的参数来控制响应状态码、标签、摘要、描述、弃用标记、响应模型等。** 这些参数让接口文档更专业、响应行为更可控。

打个比方：路径操作装饰器的参数像商品的标签和说明书——`tags` 是分类标签（在文档中分组），`summary` 是商品标题，`description` 是详细说明，`status_code` 是承诺的交付状态，`deprecated=True` 是「清仓处理，即将下架」的标记。

**核心价值**：善用装饰器参数可以让 OpenAPI 文档自动变得专业完整，同时精确控制接口的响应行为，无需额外代码。

#### 原理说明：装饰器参数的作用机制

```mermaid
graph TB
    A[@app.get(path, **kwargs)] --> B[FastAPI 注册路由]
    B --> C[path → 路由匹配]
    B --> D[status_code → 默认响应状态码]
    B --> E[response_model → 响应序列化过滤]
    B --> F[tags/summary/description → OpenAPI 文档]
    B --> G[dependencies → 路由级依赖]
    B --> H[deprecated → 文档标记弃用]
    B --> I[responses → 自定义响应文档]
```

**常用装饰器参数一览**：

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `path` | str | 路由路径 | `"/items/{item_id}"` |
| `status_code` | int | 默认响应状态码 | `201` |
| `response_model` | Type | 响应模型（过滤字段） | `UserResponse` |
| `tags` | list[str] | 文档分组标签 | `["用户管理"]` |
| `summary` | str | 接口简短摘要 | `"创建用户"` |
| `description` | str | 接口详细描述 | `"创建新用户，邮箱唯一"` |
| `deprecated` | bool | 是否标记弃用 | `True` |
| `dependencies` | list[Depends] | 路由级依赖 | `[Depends(verify_token)]` |
| `responses` | dict | 自定义响应文档 | `{404: {"model": Error}}` |
| `response_model_exclude` | set | 响应排除字段 | `{"password"}` |
| `response_model_include` | set | 响应包含字段 | `{"id", "name"}` |

> 🎯 面试高频：`response_model` 的作用是什么？① 过滤输出字段（防止敏感字段如 password 泄露）；② 自动序列化（ORM 对象 → JSON）；③ 生成 OpenAPI 响应 Schema；④ 类型校验响应数据。即使路由函数返回 ORM 对象，只要设置了 `response_model` 且 Model 配置 `from_attributes=True`，就能自动转换。

#### 代码示例

**示例 1：文档相关参数**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str | None = None

@app.post(
    "/users/",
    response_model=UserResponse,
    status_code=201,
    tags=["用户管理"],
    summary="创建新用户",
    description="创建一个新用户账户。邮箱必须唯一，密码至少8位。创建成功后返回用户信息（不含密码）。",
    responses={
        409: {"description": "邮箱已被注册"},
        422: {"description": "参数校验失败"},
    },
)
async def create_user(email: str, password: str, full_name: str | None = None):
    """创建用户"""
    return {"id": 1, "email": email, "full_name": full_name, "password": "hashed_xxx"}
    # 注意：password 会被 response_model 过滤掉，不会返回给客户端
```

预期运行结果：OpenAPI 文档中该接口有完整的摘要、描述、分组、响应状态码说明；响应体自动过滤 password 字段。

**示例 2：弃用接口与响应模型过滤**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserV1(BaseModel):
    id: int
    name: str

class UserV2(BaseModel):
    id: int
    email: str
    full_name: str | None = None

@app.get(
    "/v1/users/{user_id}",
    response_model=UserV1,
    tags=["用户管理"],
    summary="【已弃用】获取用户信息 v1",
    deprecated=True,
)
async def get_user_v1(user_id: int):
    """旧版接口，已弃用，请使用 /v2/users/{user_id}"""
    return {"id": user_id, "name": "张三", "email": "zhangsan@example.com", "password": "secret"}

@app.get(
    "/v2/users/{user_id}",
    response_model=UserV2,
    response_model_exclude={"email"},  # 也可以动态排除
    tags=["用户管理"],
    summary="获取用户信息 v2",
)
async def get_user_v2(user_id: int):
    """新版接口，返回更完整的用户信息"""
    return {"id": user_id, "email": "zhangsan@example.com", "full_name": "张三", "password": "secret"}
```

预期运行结果：v1 接口在文档中显示为弃用（删除线样式），v2 接口排除 email 字段，两个接口都自动过滤 password。

**示例 3：完整场景——路由级依赖与自定义响应**

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel

app = FastAPI()

async def verify_api_key(x_api_key: str = Header(...)):
    """路由级依赖：验证 API Key"""
    if x_api_key != "secret-key-123":
        raise HTTPException(status_code=401, detail="无效的 API Key")

class ErrorResponse(BaseModel):
    error: str
    code: int

class ItemResponse(BaseModel):
    id: int
    name: str

@app.get(
    "/secure/items/{item_id}",
    response_model=ItemResponse,
    tags=["安全接口"],
    summary="获取受保护的商品信息",
    dependencies=[Depends(verify_api_key)],  # 路由级依赖，不需要在函数参数中声明
    responses={
        200: {"model": ItemResponse, "description": "成功返回商品信息"},
        401: {"model": ErrorResponse, "description": "API Key 无效"},
        404: {"model": ErrorResponse, "description": "商品不存在"},
    },
)
async def get_secure_item(item_id: int):
    """需要 API Key 才能访问的接口"""
    if item_id == 0:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {"id": item_id, "name": "受保护的商品", "secret": "内部数据"}  # secret 被过滤
```

预期运行结果：`dependencies` 参数声明的依赖会在路由函数执行前自动运行，无需在函数签名中声明；`responses` 参数为不同状态码提供文档说明。

#### 使用场景与最佳实践

**适用场景**：所有生产级 API；需要专业 OpenAPI 文档的对外接口；需要统一响应过滤的接口；需要标记弃用的旧版接口。

**不适用场景**：内部临时接口（可简化）；纯函数式测试路由。

**最佳实践**：
1. 每个接口都设置 `tags`、`summary`，让文档清晰分组
2. 始终设置 `response_model`，防止敏感字段泄露
3. 创建接口设置 `status_code=201`，删除接口设置 `status_code=204`
4. 旧版接口用 `deprecated=True` 标记，并在 description 中说明替代接口
5. 用 `dependencies` 声明路由级依赖（如认证），保持函数签名干净
6. 用 `responses` 文档化错误响应，帮助前端处理各种情况

**性能建议**：`response_model` 会做一次序列化和校验，对超大响应（>100KB）有轻微开销。如果性能敏感且确定数据格式正确，可用 `response_model_by_alias=False` 减少处理，或直接返回 `JSONResponse` 跳过模型校验。

#### 常见坑点

**坑点 1：response_model 过滤了字段但返回 ORM 对象时报错**

- 错误现象：设置了 `response_model=UserResponse`，路由函数返回 SQLAlchemy ORM 对象，报 `ValueError: "object" input not supported`
- 根本原因：Pydantic 默认只能从 dict 构建 Model，不能直接从 ORM 对象读取属性
- 正确做法：在 Pydantic Model 中设置 `model_config = ConfigDict(from_attributes=True)`（Pydantic v2）
- 预防措施：所有用于响应 ORM 对象的 Model 都配置 `from_attributes=True`

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 对象读取
    id: int
    email: str
```

**坑点 2：status_code 设置后路由函数内 raise HTTPException 被覆盖**

- 错误现象：设置了 `status_code=201`，但函数内 `raise HTTPException(status_code=400)` 仍然返回 400（正常），但有时混淆了默认状态码和异常状态码
- 根本原因：`status_code` 是「成功时的默认状态码」，`raise HTTPException` 的状态码优先级更高
- 正确做法：理解 `status_code` 只在函数正常返回时生效，异常时用 HTTPException 的状态码
- 预防措施：不要在函数内手动修改 `response.status_code` 来覆盖成功状态码，用 `status_code` 参数声明

---

> 💡 **本章深度讲解**：HTTP 方法语义是 RESTful API 的基础。GET（查询、安全幂等）、POST（创建、非幂等）、PUT（全量替换、幂等）、PATCH（部分更新、非幂等）、DELETE（删除、幂等）各有明确语义。路径操作装饰器的参数（status_code、response_model、tags、summary、deprecated、dependencies、responses）让接口既专业又可控。核心原则：路径用名词复数，方法表达操作语义，响应模型过滤敏感字段，文档参数让 OpenAPI 自动完整。
>
> 📝 **本章精简总结**：
> 1. GET 查询（安全/幂等/可缓存）、POST 创建（非幂等）、PUT 全量替换（幂等）、PATCH 部分更新、DELETE 删除（幂等）
> 2. PUT 和 PATCH 的区别：PUT 全量替换，PATCH 部分更新
> 3. 路径用名词复数（/items/），不用动词（/getItems）
> 4. POST 成功返回 201，DELETE 成功返回 204
> 5. response_model 过滤敏感字段+自动序列化+生成文档
> 6. 装饰器参数：tags 分组、summary 摘要、description 描述、deprecated 弃用
> 7. dependencies 参数声明路由级依赖，函数签名保持干净
> 8. ORM 对象作为响应需设置 from_attributes=True

🎯 **梯度练习题**

**基础题⭐**
1. 写出标准 CRUD 的五个接口方法和路径（以 /items/ 资源为例）。
2. PUT 和 PATCH 有什么区别？哪个是幂等的？
3. response_model 的三个主要作用是什么？

**进阶题⭐⭐**
4. 解释为什么不能用 GET 请求做修改操作？如果用了会有什么风险？
5. 设计一个「文章点赞」接口：POST /articles/{id}/like（点赞，非幂等）和 DELETE /articles/{id}/like（取消点赞，幂等）。说明为什么点赞用 POST 而非 PUT。

**实战题⭐⭐⭐**
6. 实现一个完整的用户管理模块接口，包含：创建用户（POST，201）、用户列表（GET，分页）、用户详情（GET）、全量更新（PUT）、部分更新（PATCH）、删除（DELETE，204）。每个接口都有 response_model、tags、summary、responses 文档。UserResponse 需过滤 password 字段，支持从 ORM 对象序列化。

---

## 五、响应模型、状态码与响应类型

### 5.1 响应模型（response_model）

#### 概念解释

**响应模型是通过 `response_model` 参数声明的 Pydantic Model，用于控制路由函数返回数据的序列化、字段过滤和类型校验。** 它是 FastAPI 中防止敏感数据泄露、保证响应格式一致性的核心机制。

打个比方：响应模型像餐厅的出餐标准——不管后厨（路由函数）做出来的菜有多少配料（返回的 dict/ORM 对象有多少字段），出餐时必须按照菜单（response_model）上的标准摆盘，多余的配料（敏感字段如 password）不上桌，缺少的配料（必填字段）会被检查出来。

**核心价值**：响应模型实现「输入输出分离」——请求 Model 可以包含密码等写入字段，响应 Model 只暴露安全字段，从机制上防止敏感数据泄露，同时自动生成 OpenAPI 响应 Schema。

#### 原理说明：响应模型序列化流程

```mermaid
graph TB
    A[路由函数返回<br/>dict / ORM 对象 / Model] --> B[FastAPI 检测 response_model]
    B --> C{Pydantic v2 构建}
    C -->|dict| D[model_validate(dict)]
    C -->|ORM对象| E[model_validate(obj)<br/>需 from_attributes=True]
    C -->|Model实例| F[直接使用]
    D --> G[字段过滤<br/>include/exclude]
    E --> G
    F --> G
    G --> H[序列化输出<br/>model_dump(mode=json)]
    H --> I[JSONResponse]
```

**响应模型的过滤选项**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `response_model` | 响应模型类 | `UserResponse` |
| `response_model_include` | 只包含指定字段 | `{"id", "name"}` |
| `response_model_exclude` | 排除指定字段 | `{"password"}` |
| `response_model_by_alias` | 是否按别名序列化 | `False` |
| `response_model_exclude_unset` | 排除未设置的字段 | `True` |
| `response_model_exclude_defaults` | 排除默认值字段 | `True` |
| `response_model_exclude_none` | 排除 None 字段 | `True` |

> 🎯 面试高频：为什么 response_model 能过滤敏感字段？因为 FastAPI 会用 `response_model` 重新构建一个 Pydantic Model 实例，Model 中未定义的字段会被丢弃。即使路由函数返回的 dict 包含 `password`、`hashed_password` 等字段，只要响应 Model 中没有这些字段，它们就不会出现在最终 JSON 中。这是「白名单」机制而非「黑名单」——只输出 Model 中定义的字段。

#### 代码示例

**示例 1：基础响应模型过滤敏感字段**

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict

app = FastAPI()

class UserCreate(BaseModel):
    email: str
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str | None = None
    # 注意：没有 password 字段！

@app.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    # 模拟数据库存储，返回包含密码的完整对象
    return {
        "id": 1,
        "email": user.email,
        "full_name": None,
        "password": "hashed_" + user.password,  # 敏感字段
        "secret_key": "internal-secret",        # 内部字段
    }

# POST /users/ {"email":"a@b.com","password":"password123"}
# 响应：{"id":1,"email":"a@b.com","full_name":null}
# password 和 secret_key 被自动过滤，不会返回给客户端
```

预期运行结果：响应体只包含 `UserResponse` 中定义的字段，password 和 secret_key 被过滤。

**示例 2：动态 include/exclude 字段**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str | None = None
    stock: int
    created_at: str

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    return {
        "id": item_id, "name": "iPhone", "price": 999.99,
        "description": "最新款", "stock": 100, "created_at": "2024-01-01",
    }

# 也可以在装饰器中动态过滤
@app.get(
    "/items/{item_id}/brief",
    response_model=ItemResponse,
    response_model_include={"id", "name", "price"},  # 只返回这三个字段
)
async def get_item_brief(item_id: int):
    return await get_item(item_id)

@app.get(
    "/items/{item_id}/public",
    response_model=ItemResponse,
    response_model_exclude={"stock", "created_at"},  # 排除内部字段
)
async def get_item_public(item_id: int):
    return await get_item(item_id)

# GET /items/1/brief → {"id":1,"name":"iPhone","price":999.99}
# GET /items/1/public → {"id":1,"name":"iPhone","price":999.99,"description":"最新款"}
```

预期运行结果：同一数据通过不同的 include/exclude 返回不同详略程度的响应。

**示例 3：完整场景——统一响应包装模型**

```python
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar

app = FastAPI()

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    """统一响应包装：code + message + data"""
    code: int = 0
    message: str = "success"
    data: T | None = None

class UserData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str | None = None

class PaginatedData(BaseModel, Generic[T]):
    """分页数据包装"""
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

@app.get("/users/{user_id}", response_model=ApiResponse[UserData])
async def get_user(user_id: int):
    """单个用户：统一包装 + 用户数据"""
    user = {"id": user_id, "email": "a@b.com", "full_name": "张三", "password": "secret"}
    return ApiResponse(data=UserData.model_validate(user))

@app.get("/users/", response_model=ApiResponse[PaginatedData[UserData]])
async def list_users(page: int = 1, page_size: int = 20):
    """用户列表：统一包装 + 分页数据"""
    users = [
        {"id": 1, "email": "a@b.com", "full_name": "张三", "password": "x"},
        {"id": 2, "email": "c@d.com", "full_name": "李四", "password": "y"},
    ]
    paginated = PaginatedData[UserData](
        items=[UserData.model_validate(u) for u in users],
        total=2, page=page, page_size=page_size, total_pages=1,
    )
    return ApiResponse(data=paginated)

# GET /users/1 → {"code":0,"message":"success","data":{"id":1,"email":"a@b.com","full_name":"张三"}}
# GET /users/ → {"code":0,"message":"success","data":{"items":[...],"total":2,...}}
```

预期运行结果：通过泛型 `Generic[T]` 实现统一响应包装，OpenAPI 文档自动生成嵌套的 Schema，所有接口响应格式一致。

#### 使用场景与最佳实践

**适用场景**：所有对外 API；包含敏感字段的用户/订单接口；需要统一响应格式的项目；需要不同详略程度响应的接口。

**不适用场景**：内部调试接口（可直接返回 dict）；流式响应（StreamingResponse 不经过 response_model）；文件下载（Response 直接返回二进制）。

**最佳实践**：
1. 始终为每个接口声明 `response_model`，这是防止敏感字段泄露的第一道防线
2. 请求 Model 和响应 Model 分开定义（UserCreate / UserResponse），不要复用
3. 响应 Model 配置 `from_attributes=True`，支持直接返回 ORM 对象
4. 用泛型 `ApiResponse[T]` 统一响应格式，code/message/data 结构
5. 不同详略程度用 `response_model_include/exclude`，不要定义多个几乎相同的 Model
6. 分页响应用专门的 PaginatedData 模型，包含 total/page/total_pages

**性能建议**：response_model 序列化有开销（构建 Model + 校验 + dump）。对性能极敏感的大响应接口，可直接返回 `JSONResponse(content=...)` 跳过模型层，但需自行保证数据安全。

#### 常见坑点

**坑点 1：response_model 未生效，敏感字段仍返回**

- 错误现象：设置了 `response_model=UserResponse`，但响应中仍包含 password 字段
- 根本原因：① 路由函数直接返回了 `JSONResponse`（绕过 response_model 处理）；② response_model 拼写错误；③ 返回的是已经序列化的 JSON 字符串
- 正确做法：路由函数返回 dict 或 ORM 对象，不要手动返回 JSONResponse（除非需要自定义 header）
- 预防措施：代码审查时检查返回类型，需要自定义 header 时注入 Response 参数而非返回 JSONResponse

**坑点 2：ORM 对象返回时报 from_attributes 错误**

- 错误现象：`response_model=UserResponse`，返回 SQLAlchemy 对象时报 `PydanticSerializationError`
- 根本原因：Pydantic v2 默认不支持从任意对象读取属性，需配置 `from_attributes=True`
- 正确做法：在 Model 中设置 `model_config = ConfigDict(from_attributes=True)`
- 预防措施：项目中所有响应 Model 基类统一配置 from_attributes

```python
from pydantic import BaseModel, ConfigDict

class ORMModel(BaseModel):
    """所有响应 Model 的基类，统一配置 from_attributes"""
    model_config = ConfigDict(from_attributes=True)

class UserResponse(ORMModel):
    id: int
    email: str
```

---

### 5.2 HTTP 状态码与自定义响应

#### 概念解释

**HTTP 状态码是服务器对请求的响应状态标识，分为 1xx（信息）、2xx（成功）、3xx（重定向）、4xx（客户端错误）、5xx（服务器错误）五类。** FastAPI 通过 `status_code` 参数设置成功状态码，通过 `HTTPException` 设置错误状态码，通过 `Response` 子类实现自定义响应。

打个比方：HTTP 状态码像快递的物流状态——200 是「已签收」，201 是「已发货（新创建）」，301 是「地址已变更，请转发」，404 是「收件人不存在」，500 是「快递员出了意外」。客户端根据状态码决定下一步操作（重试、提示错误、跳转等）。

**核心价值**：正确使用状态码让 API 行为可预测，客户端和监控系统可以基于状态码做自动化处理（重试 5xx、告警 5xx、缓存 200 等）。

#### 原理说明：状态码分类与 FastAPI 处理

```mermaid
graph LR
    subgraph 2xx 成功
        200[200 OK<br/>GET/PUT/PATCH]
        201[201 Created<br/>POST]
        204[204 No Content<br/>DELETE]
    end
    subgraph 3xx 重定向
        301[301 永久重定向]
        302[302 临时重定向]
    end
    subgraph 4xx 客户端错误
        400[400 Bad Request]
        401[401 未认证]
        403[403 无权限]
        404[404 不存在]
        422[422 校验失败]
        429[429 限流]
    end
    subgraph 5xx 服务器错误
        500[500 内部错误]
        502[502 网关错误]
        503[503 服务不可用]
    end
```

**FastAPI 内置 Response 类型**：

| Response 类型 | Content-Type | 用途 |
|--------------|-------------|------|
| `Response` | text/plain | 自定义原始响应 |
| `JSONResponse` | application/json | JSON 响应（默认） |
| `HTMLResponse` | text/html | HTML 页面 |
| `PlainTextResponse` | text/plain | 纯文本 |
| `RedirectResponse` | - | 重定向 |
| `StreamingResponse` | 流式 | 大文件/视频/SSE |
| `FileResponse` | 自动检测 | 文件下载 |

> 🎯 面试高频：FastAPI 中 422 和 400 的区别？400 Bad Request 是通用的客户端错误（请求格式正确但语义有误，如业务规则不满足）；422 Unprocessable Entity 是 FastAPI/Pydantic 专用的参数校验错误（请求格式正确但字段校验失败，如类型不对、约束不满足）。422 的响应体包含详细的字段级错误信息（loc/msg/type）。

#### 代码示例

**示例 1：正确使用状态码**

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class ItemCreate(BaseModel):
    name: str

items = {}

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """创建成功返回 201"""
    new_id = len(items) + 1
    items[new_id] = {"id": new_id, "name": item.name}
    return items[new_id]

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    """查询成功返回 200，不存在返回 404"""
    if item_id not in items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"商品 {item_id} 不存在",
        )
    return items[item_id]

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """删除成功返回 204（无响应体）"""
    if item_id not in items:
        raise HTTPException(status_code=404, detail="商品不存在")
    del items[item_id]
    # 不需要 return，204 自动不返回 body
```

预期运行结果：POST 返回 201，GET 成功返回 200/失败 404，DELETE 返回 204。

**示例 2：自定义响应类型**

```python
from fastapi import FastAPI
from fastapi.responses import (
    HTMLResponse, PlainTextResponse, RedirectResponse, FileResponse
)

app = FastAPI()

@app.get("/html", response_class=HTMLResponse)
async def get_html():
    """返回 HTML 页面"""
    return """
    <html><body><h1>Hello FastAPI</h1><p>这是一个 HTML 响应</p></body></html>
    """

@app.get("/text", response_class=PlainTextResponse)
async def get_text():
    """返回纯文本"""
    return "这是纯文本响应，不是 JSON"

@app.get("/redirect")
async def redirect():
    """重定向到外部 URL"""
    return RedirectResponse(url="https://fastapi.tiangolo.com")

@app.get("/download")
async def download_file():
    """文件下载"""
    return FileResponse(
        path="data/report.pdf",
        filename="年度报告.pdf",  # 浏览器下载时的文件名
        media_type="application/pdf",
    )

# GET /html → 浏览器渲染 HTML 页面
# GET /text → Content-Type: text/plain
# GET /redirect → 307 跳转到 fastapi.tiangolo.com
# GET /download → 浏览器下载 PDF 文件
```

预期运行结果：不同 Response 类型设置不同的 Content-Type 和行为。

**示例 3：完整场景——流式响应（SSE + 大文件）**

```python
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

@app.get("/stream/sse")
async def sse_stream():
    """Server-Sent Events 流式响应：AI 对话场景"""
    async def event_generator():
        messages = ["你", "好", "，", "我", "是", "AI", "助", "手"]
        for char in messages:
            yield f"data: {json.dumps({'char': char})}\n\n"
            await asyncio.sleep(0.1)  # 模拟逐字输出
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        },
    )

@app.get("/download/large")
async def download_large_file():
    """大文件流式下载：避免加载到内存"""
    def file_generator():
        with open("large_file.iso", "rb") as f:
            while chunk := f.read(1024 * 1024):  # 每次读 1MB
                yield chunk

    return StreamingResponse(
        file_generator(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=large_file.iso"},
    )

# GET /stream/sse → 客户端逐字接收 AI 回复
# GET /download/large → 流式下载大文件，内存占用恒定
```

预期运行结果：SSE 流式推送逐字输出，大文件流式下载不占内存。

#### 使用场景与最佳实践

**适用场景**：所有 API 接口；需要自定义 Content-Type 的接口；文件下载；AI 流式输出；服务器推送事件。

**不适用场景**：简单 JSON 响应（用默认即可）。

**最佳实践**：
1. 创建用 201，删除用 204，查询/更新用 200
2. 认证失败用 401（含 WWW-Authenticate header），权限不足用 403
3. 参数校验失败 FastAPI 自动返回 422，业务错误用 400
4. 限流用 429 + Retry-After header
5. 大文件用 StreamingResponse/FileResponse，不要读入内存
6. AI 流式输出用 SSE（text/event-stream），设置 no-cache 和 no-buffering

**性能建议**：StreamingResponse 的生成器如果是同步函数，FastAPI 会放到线程池执行，避免阻塞事件循环。异步生成器（async def + yield）直接在事件循环中执行，性能更好。

#### 常见坑点

**坑点 1：204 No Content 时返回了响应体**

- 错误现象：设置了 `status_code=204`，但函数返回了 dict，客户端收到空响应或报错
- 根本原因：204 规范要求无响应体，FastAPI 会忽略返回值
- 正确做法：204 接口不要 return 任何内容，或 return None
- 预防措施：删除接口统一用 204 且不返回 body；需要返回删除信息时用 200

**坑点 2：StreamingResponse 中使用同步生成器阻塞事件循环**

- 错误现象：流式响应时其他请求被阻塞
- 根本原因：同步生成器（`def gen(): yield`）在事件循环线程中执行，阻塞操作卡住整个循环
- 正确做法：用异步生成器（`async def gen(): yield`），或将阻塞 IO 放到线程池
- 预防措施：StreamingResponse 的生成器优先用 async def

---

## 六、依赖注入核心原理

### 6.1 依赖注入的概念与价值

#### 概念解释

**依赖注入（Dependency Injection, DI）是一种设计模式，将对象所依赖的资源（数据库会话、当前用户、配置、缓存客户端等）从外部注入，而非在对象内部自行创建。** FastAPI 通过 `Depends()` 函数声明式地声明依赖，框架自动解析、创建并注入。

打个比方：依赖注入像餐厅的食材配送系统——厨师（路由函数）不需要自己去菜市场买菜（创建数据库连接），只要在菜单上写「需要：新鲜牛肉（get_db 依赖）」，后厨（FastAPI DI 系统）自动把食材备好送到厨房。厨师专注做菜（业务逻辑），食材的采购、质检、回收（依赖的创建、校验、清理）由系统统一管理。

**核心价值**：依赖注入实现「控制反转」——业务代码不直接依赖具体实现，而是依赖抽象接口，使得代码可测试（替换依赖为 Mock）、可复用（同一依赖多处注入）、可维护（修改依赖实现不影响业务代码）。

#### 原理说明：FastAPI 依赖注入的 DAG 解析机制

```mermaid
graph TD
    A[路由函数 create_order] --> B[get_current_user<br/>Depends]
    A --> C[get_db<br/>Depends]
    B --> D[get_db<br/>共享缓存 ✓]
    B --> E[verify_token<br/>Depends]
    C --> D
    E --> F[get_settings<br/>Depends]
    style D fill:#90EE90
```

FastAPI 的依赖注入是一个**有向无环图（DAG）解析器**，执行流程：

1. **递归解析**：从路由函数的参数开始，递归解析每个 `Depends()` 的依赖函数及其参数
2. **拓扑排序**：将依赖图按依赖关系排序，确保被依赖的先执行
3. **请求级缓存**：同一请求中相同依赖函数只执行一次，结果缓存复用（上图绿色节点 get_db 被两个依赖同时需要，但只执行一次）
4. **注入结果**：将依赖返回值注入到路由函数和上层依赖的参数中
5. **清理执行**：生成器依赖（yield）在请求结束后执行清理逻辑

| 特性 | 说明 |
|------|------|
| 依赖类型 | 普通函数、异步函数、生成器函数、类、类的 `__call__` |
| 缓存范围 | 默认请求级（同一请求相同依赖只执行一次） |
| 嵌套深度 | 无限制（依赖的依赖的依赖...） |
| 循环依赖 | 不支持（DAG，循环会报错） |
| 覆盖 | `app.dependency_overrides[dep] = mock_dep` 用于测试 |

> 🎯 面试高频：FastAPI 依赖注入和 Flask 的 `g` 对象有什么区别？① FastAPI DI 是声明式的（函数签名声明依赖），Flask g 是命令式的（手动 `g.db = ...`）；② FastAPI DI 自动解析依赖链和缓存，Flask g 需要手动管理；③ FastAPI DI 支持生成器清理（yield），Flask g 需要 `teardown_appcontext`；④ FastAPI DI 可通过 dependency_overrides 测试替换，Flask g 需要 mock 全局对象。

#### 代码示例

**示例 1：最简单的依赖注入**

```python
from fastapi import FastAPI, Depends

app = FastAPI()

async def get_query_params(q: str | None = None, page: int = 1):
    """依赖函数：解析并返回查询参数"""
    return {"q": q, "page": page}

@app.get("/search/")
async def search(params: dict = Depends(get_query_params)):
    """路由函数声明依赖，FastAPI 自动执行 get_query_params 并注入结果"""
    return {"search_params": params, "results": []}

# GET /search/?q=python&page=2 → {"search_params":{"q":"python","page":2},"results":[]}
```

预期运行结果：`Depends(get_query_params)` 自动执行依赖函数，将返回值注入 `params` 参数。

**示例 2：依赖的依赖（嵌套依赖）**

```python
from fastapi import FastAPI, Depends, HTTPException

app = FastAPI()

def get_settings():
    """最底层依赖：返回配置"""
    return {"api_key": "secret-123", "debug": False}

def verify_api_key(settings: dict = Depends(get_settings)):
    """中层依赖：依赖 get_settings，验证 API Key"""
    # 实际场景中从 Header 读取 key 并与 settings 比较
    return settings["api_key"]

def get_current_user(api_key: str = Depends(verify_api_key)):
    """上层依赖：依赖 verify_api_key，返回当前用户"""
    return {"id": 1, "name": "张三", "api_key": api_key}

@app.get("/profile")
async def profile(user: dict = Depends(get_current_user)):
    """路由函数：依赖 get_current_user"""
    return user

# 依赖链：profile → get_current_user → verify_api_key → get_settings
# FastAPI 自动按顺序执行：get_settings → verify_api_key → get_current_user → profile
```

预期运行结果：FastAPI 自动解析三层嵌套依赖，按拓扑顺序执行，最终注入用户对象。

**示例 3：完整场景——类依赖与可调用对象依赖**

```python
from fastapi import FastAPI, Depends, Query

app = FastAPI()

class Pagination:
    """类依赖：封装分页参数，可复用"""
    def __init__(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

    def dict(self):
        return {"page": self.page, "page_size": self.page_size, "offset": self.offset}

class KeywordFilter:
    """可调用对象依赖：__call__ 方法作为依赖函数"""
    def __init__(self, default_keyword: str = ""):
        self.default_keyword = default_keyword

    async def __call__(self, q: str | None = Query(None, min_length=1)):
        return q or self.default_keyword

# 使用类依赖
@app.get("/items/")
async def list_items(pagination: Pagination = Depends()):
    """Depends() 不传参数时，自动使用参数类型 Pagination 作为依赖"""
    return {"pagination": pagination.dict(), "items": []}

# 使用可调用对象依赖
keyword_filter = KeywordFilter(default_keyword="全部")

@app.get("/search/")
async def search(keyword: str = Depends(keyword_filter)):
    return {"keyword": keyword, "results": []}

# GET /items/?page=2&page_size=50 → {"pagination":{"page":2,"page_size":50,"offset":50},...}
# GET /search/?q=fastapi → {"keyword":"fastapi",...}
# GET /search/ → {"keyword":"全部",...}
```

预期运行结果：类依赖通过 `__init__` 参数自动解析查询参数，可调用对象依赖通过 `__call__` 方法执行，两种方式都实现依赖的复用和参数封装。

#### 使用场景与最佳实践

**适用场景**：数据库会话管理；当前用户认证授权；配置注入；分页/过滤参数封装；缓存客户端；外部服务客户端（HTTP、Redis、MQ）；横切关注点（日志、审计、限流）。

**不适用场景**：纯计算逻辑（直接写函数即可）；只有一个地方使用的简单逻辑（无需抽象为依赖）；需要在请求间共享状态的资源（用应用级单例而非请求级依赖）。

**最佳实践**：
1. 依赖函数命名用 `get_xxx` 前缀（`get_db`、`get_current_user`）
2. 数据库会话用生成器依赖（yield），自动管理事务和连接
3. 认证依赖链分层设计：`get_current_user` → `get_current_active_user` → `get_current_superuser`
4. 通用参数（分页、过滤）封装为类依赖，避免每个接口重复声明
5. 依赖保持单一职责，一个依赖只做一件事
6. 测试时用 `dependency_overrides` 替换依赖为 Mock/内存实现

**性能建议**：依赖在请求级缓存，同一请求中重复注入不重复执行。但跨请求不缓存，数据库连接池等资源应在应用启动时创建（单例），依赖只负责从池中获取会话。

#### 常见坑点

**坑点 1：依赖函数中使用了请求级资源但被 lru_cache 装饰**

- 错误现象：`@lru_cache` 装饰的依赖函数返回的数据库会话在多个请求间共享，导致数据错乱
- 根本原因：`lru_cache` 是进程级缓存，会把第一次请求的 db 会话缓存下来，后续请求复用同一个已关闭的会话
- 正确做法：不要用 `lru_cache` 装饰请求级依赖（如 get_db）；配置等不可变对象才用 `lru_cache`
- 预防措施：代码审查时检查 `@lru_cache` 是否装饰了请求级依赖

```python
from functools import lru_cache
from fastapi import Depends

# 错误：get_db 被 lru_cache，会话在请求间共享
@lru_cache
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 正确：get_db 不缓存，每次请求创建新会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 正确：配置对象可以用 lru_cache（不可变、应用级）
@lru_cache
def get_settings():
    return Settings()
```

**坑点 2：Depends() 不传参数时类型推断错误**

- 错误现象：`pagination: Pagination = Depends()` 时报错或不执行依赖
- 根本原因：`Depends()` 不传参数时，FastAPI 使用参数的类型注解作为依赖。如果类型注解是 `Pagination`（类），FastAPI 会实例化它；但如果注解是 `dict` 或其他非可调用类型，会失败
- 正确做法：类依赖用 `Depends()` 配合类型注解 `Pagination`；函数依赖显式传 `Depends(get_pagination)`
- 预防措施：统一风格——函数依赖显式传函数名，类依赖用 `Depends()` + 类型注解

---

### 6.2 函数依赖与类依赖

#### 概念解释

**FastAPI 支持两种主要的依赖形式：函数依赖（普通函数/异步函数/生成器函数）和类依赖（类的 `__init__` 或 `__call__` 方法）。** 函数依赖适合无状态的逻辑（获取数据库会话、验证 Token），类依赖适合有状态的参数封装（分页、过滤器）。

打个比方：函数依赖像一次性工具——每次用的时候拿出来（执行函数），用完就扔（返回值注入后函数本身不保留状态）；类依赖像多功能工具箱——初始化时配置好参数（`__init__`），之后可以反复使用不同的工具方法（`.dict()`、`.apply()`）。

**核心价值**：两种依赖形式覆盖不同场景——函数依赖轻量灵活，类依赖可封装状态和方法，开发者可以根据需求选择最合适的形式。

#### 原理说明：函数依赖 vs 类依赖执行机制

```mermaid
graph TB
    subgraph 函数依赖
        A[Depends(get_db)] --> B[执行 get_db()]
        B --> C[返回值注入]
    end
    subgraph 类依赖
        D[Depends(Pagination)<br/>或 pagination: Pagination = Depends()] --> E[调用 Pagination(__init__参数)]
        E --> F[实例注入]
        F --> G[可调用实例方法<br/>pagination.dict()]
    end
    subgraph 可调用对象依赖
        H[Depends(filter_instance)] --> I[调用 filter_instance.__call__(参数)]
        I --> J[返回值注入]
    end
```

**四种依赖形式对比**：

| 形式 | 语法 | 状态 | 典型用途 |
|------|------|------|---------|
| 普通函数 | `Depends(get_db)` | 无 | 数据库会话、配置 |
| 异步函数 | `Depends(aget_db)` | 无 | 异步数据库会话 |
| 生成器函数 | `Depends(get_db)` + yield | 无 | 资源管理（事务/连接） |
| 类（__init__） | `Depends(Pagination)` | 有 | 参数封装（分页/过滤） |
| 可调用对象 | `Depends(instance)` | 有 | 可配置的过滤器 |

> 🎯 面试高频：FastAPI 中类依赖 `Depends(Pagination)` 和 `pagination: Pagination = Depends()` 有什么区别？两者效果相同——FastAPI 看到 `Depends()` 无参数时，会从参数类型注解 `Pagination` 推断依赖类，然后调用 `Pagination(...)` 创建实例。显式 `Depends(Pagination)` 更清晰，隐式 `Depends()` 更简洁。注意：类依赖的 `__init__` 参数会被 FastAPI 当作请求参数解析（Path/Query/Body 等）。

#### 代码示例

**示例 1：函数依赖的四种形式**

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# 1. 普通函数依赖
def get_sync_db():
    return {"connection": "sync-db"}

# 2. 异步函数依赖
async def get_async_db():
    return {"connection": "async-db"}

# 3. 生成器函数依赖（带清理）
def get_db_with_cleanup():
    db = {"connection": "db", "opened": True}
    print("依赖：打开数据库连接")
    try:
        yield db
    finally:
        db["opened"] = False
        print("依赖：关闭数据库连接")

# 4. 异步生成器依赖
async def get_async_db_with_cleanup():
    db = {"connection": "async-db", "opened": True}
    print("依赖：打开异步数据库连接")
    try:
        yield db
    finally:
        db["opened"] = False
        print("依赖：关闭异步数据库连接")

@app.get("/sync")
async def sync_endpoint(db: dict = Depends(get_sync_db)):
    return db

@app.get("/async")
async def async_endpoint(db: dict = Depends(get_async_db)):
    return db

@app.get("/cleanup")
async def cleanup_endpoint(db: dict = Depends(get_db_with_cleanup)):
    return db
# 控制台输出：
# 依赖：打开数据库连接
# （路由函数执行）
# 依赖：关闭数据库连接
```

预期运行结果：生成器依赖在请求前执行 yield 前代码，请求后执行 yield 后代码，实现资源自动清理。

**示例 2：类依赖封装分页参数**

```python
from fastapi import FastAPI, Depends, Query

app = FastAPI()

class PaginationParams:
    """分页参数类依赖：自动解析 page/page_size，计算 offset"""
    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        sort_by: str = Query("created_at", description="排序字段"),
        sort_order: str = Query("desc", description="排序方向"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
        self.sort_by = sort_by
        self.sort_order = sort_order

    @property
    def order_by(self):
        """生成 ORDER BY 子句"""
        return f"{self.sort_by} {self.sort_order.upper()}"

    def dict(self):
        return {
            "page": self.page,
            "page_size": self.page_size,
            "offset": self.offset,
            "order_by": self.order_by,
        }

@app.get("/users/")
async def list_users(pagination: PaginationParams = Depends()):
    """用户列表：使用分页类依赖"""
    return {"pagination": pagination.dict(), "users": []}

@app.get("/orders/")
async def list_orders(pagination: PaginationParams = Depends()):
    """订单列表：复用同一个分页类依赖"""
    return {"pagination": pagination.dict(), "orders": []}

# GET /users/?page=2&page_size=50&sort_by=name&sort_order=asc
# → {"pagination":{"page":2,"page_size":50,"offset":50,"order_by":"name ASC"},...}
```

预期运行结果：`PaginationParams` 类的 `__init__` 参数自动解析为查询参数，实例注入后可调用方法和属性。

**示例 3：完整场景——可配置的可调用对象依赖**

```python
from fastapi import FastAPI, Depends, Query, HTTPException

app = FastAPI()

class RoleChecker:
    """可调用对象依赖：检查用户角色，可配置允许的角色"""
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, role: str = Query(..., description="用户角色（模拟）")):
        if role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail=f"需要角色: {self.allowed_roles}")
        return role

# 创建不同角色的检查器实例
admin_checker = RoleChecker(["admin"])
editor_checker = RoleChecker(["admin", "editor"])
viewer_checker = RoleChecker(["admin", "editor", "viewer"])

@app.get("/admin/dashboard")
async def admin_dashboard(role: str = Depends(admin_checker)):
    return {"message": "管理员仪表盘", "role": role}

@app.get("/editor/articles")
async def editor_articles(role: str = Depends(editor_checker)):
    return {"message": "编辑文章管理", "role": role}

@app.get("/public/content")
async def public_content(role: str = Depends(viewer_checker)):
    return {"message": "公开内容", "role": role}

# GET /admin/dashboard?role=admin → 200
# GET /admin/dashboard?role=viewer → 403 需要角色: ['admin']
# GET /editor/articles?role=editor → 200
```

预期运行结果：同一个 `RoleChecker` 类通过不同的初始化参数创建不同的依赖实例，实现灵活的角色权限控制。

#### 使用场景与最佳实践

**适用场景**：函数依赖——数据库会话、认证、配置、外部客户端；类依赖——分页参数、过滤条件、复杂查询参数；可调用对象依赖——可配置的权限检查、可参数化的验证器。

**不适用场景**：极简单一参数（直接声明在函数中即可）；需要跨请求状态（用应用级单例）。

**最佳实践**：
1. 无状态逻辑用函数依赖，有状态参数封装用类依赖
2. 类依赖的 `__init__` 参数用 `Query()`/`Path()` 等声明约束
3. 可调用对象依赖适合「同一逻辑不同配置」的场景（角色检查、阈值验证）
4. 依赖函数名用动词（get/verify/extract），类依赖名用名词（Pagination/Filter）
5. 类依赖提供 `dict()` 或 `model_dump()` 方法，方便序列化和日志

**性能建议**：类依赖每次请求都会实例化，如果 `__init__` 中有重计算，考虑用 `@lru_cache` 装饰类的 `__call__` 方法（仅适用于无状态配置）。函数依赖的请求级缓存已足够高效。

#### 常见坑点

**坑点 1：类依赖的 __init__ 中有默认参数但未用 Query 声明**

- 错误现象：`Pagination` 类中 `page: int = 1`，但 FastAPI 不把它当作查询参数，而是当作 Python 默认值
- 根本原因：类依赖的 `__init__` 参数需要用 `Query()`/`Path()` 等显式声明，FastAPI 才能识别为请求参数；普通默认值只是 Python 默认值
- 正确做法：`page: int = Query(1, ge=1)` 显式声明
- 预防措施：类依赖的所有 `__init__` 参数都用 FastAPI 的参数函数声明

**坑点 2：可调用对象依赖的实例在模块级创建导致配置不可变**

- 错误现象：`checker = RoleChecker(["admin"])` 在模块级创建，测试时无法修改 allowed_roles
- 根本原因：模块级单例在 import 时创建，测试中修改会影响其他测试
- 正确做法：测试时用 `dependency_overrides` 替换整个依赖，或在函数内创建实例
- 预防措施：可配置依赖在测试中统一用 override 替换，不要直接修改实例属性

---

### 6.3 依赖注入与测试（dependency_overrides）

#### 概念解释

**`app.dependency_overrides` 是 FastAPI 提供的依赖覆盖机制，允许在测试中用 Mock 或内存实现替换真实依赖，实现业务逻辑与外部资源的隔离测试。** 这是依赖注入模式最大的价值之一——可测试性。

打个比方：依赖覆盖像电影拍摄中的替身——正常拍摄时用真演员（真实数据库依赖），但拍危险镜头或需要特定效果时用替身（Mock 依赖）。演员的角色（依赖接口）不变，只是扮演者（实现）换了，剧情（业务逻辑）照常推进。

**核心价值**：通过依赖覆盖，单元测试可以不依赖真实数据库、外部 API、认证服务，测试速度快、结果稳定、可重复，是 CI/CD 中自动化测试的基础。

#### 原理说明：依赖覆盖的执行机制

```mermaid
graph TB
    A[测试请求] --> B[FastAPI 依赖解析]
    B --> C{依赖在<br/>dependency_overrides 中?}
    C -->|是| D[执行覆盖函数<br/>Mock / 内存实现]
    C -->|否| E[执行原始依赖<br/>真实数据库 / 外部API]
    D --> F[注入路由函数]
    E --> F
    F --> G[执行业务逻辑]
    G --> H[断言结果]
```

**依赖覆盖的关键 API**：

| API | 说明 |
|-----|------|
| `app.dependency_overrides[get_db] = override_get_db` | 覆盖单个依赖 |
| `app.dependency_overrides.clear()` | 清除所有覆盖 |
| `app.dependency_overrides.pop(get_db, None)` | 清除单个覆盖 |

> 🎯 面试高频：FastAPI 测试中如何 mock 数据库？用 `app.dependency_overrides[get_db] = override_get_db`，其中 `override_get_db` 返回内存数据库（如 SQLite :memory:）或 Mock 对象。测试结束后调用 `app.dependency_overrides.clear()` 恢复真实依赖。这比 monkeypatch 更优雅，因为它只替换依赖注入点，不影响其他代码。

#### 代码示例

**示例 1：用内存数据库覆盖真实数据库**

```python
# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    db = SessionLocal()  # 真实 PostgreSQL
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return user
```

```python
# test_users.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db, Base

# 测试用内存 SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """覆盖依赖：返回测试数据库会话"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# 注册覆盖
app.dependency_overrides[get_db] = override_get_db

# 创建测试表
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_get_user():
    # 先创建测试用户
    db = TestingSessionLocal()
    db.add(User(email="test@example.com", hashed_password="hash"))
    db.commit()
    db.close()

    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def teardown_module(module):
    """测试结束后清除覆盖"""
    app.dependency_overrides.clear()
```

预期运行结果：测试使用内存 SQLite 而非真实 PostgreSQL，测试速度快且不污染生产数据。

**示例 2：Mock 外部 API 依赖**

```python
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

app = FastAPI()

class WeatherService:
    async def get_weather(self, city: str) -> dict:
        # 真实场景：调用外部天气 API
        return {"city": city, "temp": 25, "source": "real-api"}

def get_weather_service():
    return WeatherService()

@app.get("/weather/{city}")
async def weather(city: str, service: WeatherService = Depends(get_weather_service)):
    result = await service.get_weather(city)
    return result

# ===== 测试 =====
class MockWeatherService:
    """Mock 天气服务：返回固定数据，不调用外部 API"""
    async def get_weather(self, city: str) -> dict:
        return {"city": city, "temp": 20, "source": "mock"}

def override_get_weather_service():
    return MockWeatherService()

app.dependency_overrides[get_weather_service] = override_get_weather_service
client = TestClient(app)

def test_weather():
    response = client.get("/weather/北京")
    assert response.status_code == 200
    assert response.json()["temp"] == 20
    assert response.json()["source"] == "mock"
```

预期运行结果：测试中天气服务被替换为 Mock，返回固定数据，测试不依赖外部 API 可用性。

**示例 3：完整场景——pytest fixture 管理依赖覆盖**

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db, Base

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """每个测试函数独立的数据库会话"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """测试客户端：覆盖 get_db 依赖，使用测试数据库"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()  # 每个测试后清除覆盖

# test_users.py
def test_create_user(client):
    response = client.post("/users/", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_get_user_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == 404
```

预期运行结果：每个测试函数有独立的数据库（创建表→测试→删表），依赖覆盖在 fixture 中自动注册和清除，测试之间完全隔离。

#### 使用场景与最佳实践

**适用场景**：单元测试和集成测试；CI/CD 自动化测试；需要隔离外部依赖的测试；模拟异常场景（如数据库不可用）。

**不适用场景**：端到端测试（应使用真实依赖）；性能测试（Mock 数据不反映真实性能）。

**最佳实践**：
1. 用 pytest fixture 管理依赖覆盖的注册和清除，确保测试隔离
2. 数据库测试用 SQLite 内存库或测试专用数据库，不要用生产库
3. 外部 API 用 Mock 替换，测试不依赖网络
4. 每个测试后调用 `dependency_overrides.clear()`，防止覆盖泄漏到其他测试
5. 覆盖函数的签名必须与原依赖一致（包括 yield 生成器）
6. 用 `TestClient`（基于 httpx）发送测试请求，支持异步路由

**性能建议**：数据库测试用 `scope="function"` 的 fixture 每次重建表，虽然慢但隔离好；大量测试时可用 `scope="module"` + 事务回滚提升速度。

#### 常见坑点

**坑点 1：依赖覆盖未清除导致测试间污染**

- 错误现象：第一个测试的 Mock 依赖影响了第二个测试，导致测试结果不稳定
- 根本原因：`dependency_overrides` 是应用级全局字典，测试后未清除
- 正确做法：在 pytest fixture 的 teardown 中调用 `app.dependency_overrides.clear()`
- 预防措施：统一用 fixture 管理覆盖，不要在测试函数中手动设置覆盖

**坑点 2：覆盖生成器依赖时忘记用 yield**

- 错误现象：覆盖 `get_db`（生成器依赖）时用了普通函数 `return db`，导致请求结束后数据库连接不关闭
- 根本原因：FastAPI 根据原依赖的类型决定清理逻辑，如果原依赖是生成器，覆盖也必须是生成器
- 正确做法：覆盖函数也用 `yield`，保持与原依赖相同的形式
- 预防措施：覆盖依赖时复制原依赖的函数签名和形式（def/async def/yield）

---

> 💡 **本章深度讲解**：依赖注入是 FastAPI 最核心的设计之一。它本质是一个 DAG 解析器——递归解析依赖链、拓扑排序执行、请求级缓存结果、生成器自动清理。函数依赖适合无状态逻辑，类依赖适合参数封装，可调用对象依赖适合可配置逻辑。`dependency_overrides` 让测试可以隔离外部依赖，是可测试性的关键。理解依赖注入的价值在于：业务代码只依赖抽象，不依赖具体实现，从而实现高内聚低耦合。
>
> 📝 **本章精简总结**：
> 1. 依赖注入 = 控制反转，Depends() 声明式注入，框架自动解析创建
> 2. FastAPI DI 是 DAG 解析器：递归解析→拓扑排序→请求级缓存→注入→清理
> 3. 同一请求中相同依赖只执行一次（请求级缓存）
> 4. 函数依赖（get_db）、类依赖（Pagination）、可调用对象依赖（RoleChecker）
> 5. 生成器依赖用 yield 分隔 before/after，适合资源管理
> 6. dependency_overrides 用于测试替换依赖为 Mock/内存实现
> 7. 测试后必须 clear() 覆盖，防止测试间污染
> 8. 不要用 lru_cache 装饰请求级依赖（如 get_db）

🎯 **梯度练习题**

**基础题⭐**
1. 写一个简单的依赖函数 `get_current_user`，返回模拟用户 `{"id": 1, "name": "张三"}`，并在路由函数中注入。
2. 函数依赖和类依赖分别适合什么场景？
3. dependency_overrides 的作用是什么？测试结束后为什么要 clear()？

**进阶题⭐⭐**
4. 解释 FastAPI 依赖注入的 DAG 解析机制，为什么同一请求中相同依赖只执行一次？
5. 实现一个分页类依赖 `Pagination`，包含 page（>=1）、page_size（1-100）、sort_by、sort_order，提供 offset 属性和 dict() 方法。在两个不同接口中复用它。

**实战题⭐⭐⭐**
6. 实现一个完整的认证依赖链：`get_settings`（配置）→ `verify_token`（验证 JWT）→ `get_current_user`（查用户）→ `get_current_active_user`（检查激活）→ `get_current_superuser`（检查管理员）。然后写测试用 dependency_overrides 替换 `get_current_user` 为 Mock 用户，测试需要管理员权限的接口。

---

## 七、依赖嵌套、作用域与 yield 清理

### 7.1 依赖嵌套与 DAG 解析

#### 概念解释

**依赖嵌套是指一个依赖函数本身又声明了其他依赖，形成依赖的依赖（子依赖），FastAPI 自动递归解析整个依赖图。** 这使得复杂的认证链、资源管理链可以分层设计，每层只关注自己的职责。

打个比方：依赖嵌套像公司的审批流程——员工请假（路由函数）需要部门经理审批（get_current_user 依赖），部门经理需要 HR 验证员工身份（verify_token 依赖），HR 需要查询公司配置（get_settings 依赖）。每层只做自己的事，FastAPI 自动按从底层到顶层的顺序执行。

**核心价值**：依赖嵌套实现关注点分离——认证、授权、数据库、配置各成一层，修改某一层不影响其他层，且每层可独立测试和复用。

#### 原理说明：DAG 拓扑排序执行

```mermaid
graph TD
    A[路由函数] --> B[get_current_active_user]
    A --> C[get_db]
    B --> D[get_current_user]
    D --> E[verify_token]
    D --> C
    E --> F[get_settings]
    C --> G[get_engine]
    F --> H[get_config]
    G --> H
    style H fill:#90EE90
    style C fill:#90EE90
```

执行顺序（拓扑排序）：
1. `get_config`（最底层，无依赖）
2. `get_settings`（依赖 get_config）、`get_engine`（依赖 get_config）
3. `verify_token`（依赖 get_settings）、`get_db`（依赖 get_engine）
4. `get_current_user`（依赖 verify_token + get_db）
5. `get_current_active_user`（依赖 get_current_user）
6. 路由函数（依赖 get_current_active_user + get_db）

注意：`get_db` 被 `get_current_user` 和路由函数同时依赖，但只执行一次（请求级缓存，绿色节点）。

> 🎯 面试高频：FastAPI 如何处理循环依赖？FastAPI 的依赖图是 DAG（有向无环图），如果存在循环依赖（A 依赖 B，B 依赖 A），FastAPI 会在启动时检测到并抛出 `RecursionError` 或无限递归。设计依赖时应避免循环，通过引入中间层或事件驱动解耦。

#### 代码示例

**示例 1：三层嵌套认证链**

```python
from fastapi import FastAPI, Depends, HTTPException, status

app = FastAPI()

def get_settings():
    """第1层：配置"""
    return {"secret_key": "my-secret", "token_expire": 3600}

def verify_token(
    token: str = "mock-token-abc",
    settings: dict = Depends(get_settings),
):
    """第2层：验证 Token（依赖配置）"""
    if not token or token != "valid-token":
        raise HTTPException(status_code=401, detail="Token 无效")
    return {"user_id": 1, "token": token}

def get_current_user(
    token_data: dict = Depends(verify_token),
):
    """第3层：获取当前用户（依赖 Token 验证）"""
    # 实际场景：用 user_id 查数据库
    return {"id": token_data["user_id"], "name": "张三", "is_active": True}

def get_current_active_user(
    current_user: dict = Depends(get_current_user),
):
    """第4层：检查用户是否激活（依赖当前用户）"""
    if not current_user["is_active"]:
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user

@app.get("/profile")
async def profile(user: dict = Depends(get_current_active_user)):
    """路由函数：依赖第4层"""
    return user

# 依赖链：profile → get_current_active_user → get_current_user → verify_token → get_settings
# FastAPI 自动从最底层 get_settings 开始执行
```

预期运行结果：FastAPI 自动按依赖关系从底层到顶层执行，最终注入激活用户。

**示例 2：共享依赖的缓存验证**

```python
from fastapi import FastAPI, Depends

app = FastAPI()

execution_count = {"get_db": 0}

def get_db():
    """被多个依赖共享的数据库会话"""
    execution_count["get_db"] += 1
    print(f"get_db 执行了第 {execution_count['get_db']} 次")
    return {"session": "db-session"}

def get_current_user(db: dict = Depends(get_db)):
    """依赖 get_db"""
    return {"id": 1, "db": db}

def get_audit_log(db: dict = Depends(get_db)):
    """也依赖 get_db"""
    return {"action": "login", "db": db}

@app.get("/test-shared")
async def test_shared(
    user: dict = Depends(get_current_user),
    audit: dict = Depends(get_audit_log),
):
    """两个上层依赖都需要 get_db，但 get_db 只执行一次"""
    return {"user": user, "audit": audit, "db_executions": execution_count["get_db"]}

# GET /test-shared 控制台输出：
# get_db 执行了第 1 次
# 响应中 db_executions = 1（不是 2！）
```

预期运行结果：`get_db` 虽然被两个依赖同时需要，但在同一请求中只执行一次，证明请求级缓存生效。

**示例 3：完整场景——电商订单的复杂依赖链**

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 依赖链：get_settings → get_db → get_current_user → get_current_buyer → create_order
def get_settings():
    return {"max_order_amount": 10000, "tax_rate": 0.13}

def get_db(settings: dict = Depends(get_settings)):
    return {"connection": "postgres", "settings": settings}

def get_current_user(db: dict = Depends(get_db)):
    return {"id": 1, "name": "张三", "balance": 5000, "role": "buyer"}

def get_current_buyer(user: dict = Depends(get_current_user)):
    if user["role"] != "buyer":
        raise HTTPException(status_code=403, detail="只有买家可以下单")
    return user

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float

@app.post("/orders/")
async def create_order(
    items: list[OrderItem],
    buyer: dict = Depends(get_current_buyer),
    db: dict = Depends(get_db),
    settings: dict = Depends(get_settings),
):
    """创建订单：依赖买家身份、数据库、配置"""
    total = sum(item.price * item.quantity for item in items)
    if total > settings["max_order_amount"]:
        raise HTTPException(status_code=400, detail=f"订单金额超过上限 {settings['max_order_amount']}")
    if total > buyer["balance"]:
        raise HTTPException(status_code=400, detail="余额不足")
    tax = total * settings["tax_rate"]
    return {
        "order_id": 1001,
        "buyer": buyer["name"],
        "items": [i.model_dump() for i in items],
        "total": total,
        "tax": tax,
        "final_amount": total + tax,
    }

# POST /orders/ items=[{"product_id":1,"quantity":2,"price":100}]
# → {"order_id":1001,"buyer":"张三","total":200,"tax":26.0,"final_amount":226.0}
```

预期运行结果：复杂依赖链自动解析，业务逻辑专注于订单计算，认证、数据库、配置都通过依赖注入获得。

#### 使用场景与最佳实践

**适用场景**：多层认证授权链；资源管理链（配置→连接池→会话）；复杂业务流程（权限→校验→操作）；微服务中的共享依赖。

**不适用场景**：简单接口（1-2 个依赖即可，无需嵌套）；性能极敏感的接口（嵌套层级过深增加解析开销，虽然很小）。

**最佳实践**：
1. 依赖嵌套层级控制在 3-4 层以内，过深影响可读性
2. 每层依赖只做一件事（验证 Token / 查用户 / 检查权限）
3. 共享依赖（如 get_db）放在依赖链的底层，让多个上层依赖复用
4. 依赖命名体现层级：get_current_user → get_current_active_user → get_current_superuser
5. 用 Mermaid 图画出复杂依赖链，帮助团队理解

**性能建议**：依赖解析开销极小（微秒级），但依赖函数中的数据库查询和外部调用是性能瓶颈。对高频调用的依赖（如 get_current_user）考虑缓存用户信息到 Redis。

#### 常见坑点

**坑点 1：循环依赖导致启动失败**

- 错误现象：应用启动时报 `RecursionError` 或无限递归
- 根本原因：A 依赖 B，B 又依赖 A，形成循环
- 正确做法：重构依赖，提取公共部分到第三个依赖 C，让 A 和 B 都依赖 C
- 预防措施：设计依赖时画 DAG 图，确保无环；代码审查时检查依赖方向

**坑点 2：依赖函数中 raise HTTPException 后清理逻辑不执行**

- 错误现象：生成器依赖中 `yield` 前 raise 了异常，`yield` 后的清理代码不执行
- 根本原因：异常在 yield 之前抛出，生成器没有进入 try 块的 finally
- 正确做法：将资源获取放在 try 之前，yield 在 try 中，清理在 finally 中
- 预防措施：生成器依赖的标准模式：获取资源 → try → yield → finally 清理

---

### 7.2 依赖的作用域与生命周期

#### 概念解释

**依赖的作用域决定了依赖实例的生命周期和共享范围。** FastAPI 支持三种作用域：请求级（默认，每次请求创建）、应用级（单例，全局共享）、生成器级（请求前后执行清理）。

打个比方：作用域像工具的使用范围——请求级依赖是一次性手套（每个客户用一副，用完即弃），应用级依赖是餐厅的烤箱（买一次，所有厨师共用多年），生成器依赖是租借的道具（开场前领取，散场后归还）。

**核心价值**：正确选择作用域既能保证资源隔离（请求级数据库会话避免数据错乱），又能避免重复创建（应用级配置对象节省开销），还能自动清理（生成器依赖释放资源）。

#### 原理说明：三种作用域对比

```mermaid
graph TB
    subgraph 请求级
        R1[请求1 get_db → 会话A]
        R2[请求2 get_db → 会话B]
        R3[请求3 get_db → 会话C]
    end
    subgraph 应用级
        A1[get_settings → 单例配置对象]
        R1 --> A1
        R2 --> A1
        R3 --> A1
    end
    subgraph 生成器级
        G1[get_db: 打开会话 → yield → 关闭会话]
    end
```

| 作用域 | 语法 | 生命周期 | 典型用途 | 线程安全 |
|--------|------|---------|---------|---------|
| 请求级 | `Depends(get_db)` | 每次请求创建，请求结束销毁 | 数据库会话、当前用户 | ✅ 天然隔离 |
| 应用级 | `@lru_cache` / 单例 | 应用启动创建，全局共享 | 配置、连接池、引擎 | ⚠️ 需保证无状态 |
| 生成器级 | `yield` | 请求前创建，请求后清理 | 数据库事务、文件句柄 | ✅ 请求隔离 |

> 🎯 面试高频：FastAPI 依赖的默认作用域是什么？请求级。同一请求中相同依赖只执行一次并缓存结果，但不同请求之间不共享。如果需要应用级单例，用 `@lru_cache` 装饰依赖函数（仅适用于无状态的配置等），或在模块级创建实例。数据库会话必须是请求级，不能用 lru_cache，否则多个请求共享同一个会话导致数据错乱。

#### 代码示例

**示例 1：请求级 vs 应用级依赖对比**

```python
from fastapi import FastAPI, Depends
from functools import lru_cache

app = FastAPI()

request_count = {"value": 0}

# 请求级依赖：每次请求都执行
def get_request_id():
    request_count["value"] += 1
    return f"req-{request_count['value']}"

# 应用级依赖：用 lru_cache 缓存，只执行一次
@lru_cache
def get_app_config():
    print("get_app_config 执行了（只执行一次）")
    return {"app_name": "MyApp", "version": "1.0.0"}

@app.get("/test-scope")
async def test_scope(
    req_id: str = Depends(get_request_id),
    config: dict = Depends(get_app_config),
):
    return {"request_id": req_id, "config": config}

# 第1次请求：request_id=req-1，控制台打印 "get_app_config 执行了"
# 第2次请求：request_id=req-2，控制台无打印（app_config 已缓存）
# 第3次请求：request_id=req-3，控制台无打印
```

预期运行结果：请求级依赖每次执行，应用级依赖只执行一次。

**示例 2：生成器依赖的生命周期**

```python
from fastapi import FastAPI, Depends

app = FastAPI()

class DatabaseSession:
    def __init__(self):
        self.opened = False
        self.committed = False
        self.rolled_back = False

    def open(self):
        self.opened = True
        print("  [依赖] 打开数据库会话")

    def commit(self):
        self.committed = True
        print("  [依赖] 提交事务")

    def rollback(self):
        self.rolled_back = True
        print("  [依赖] 回滚事务")

    def close(self):
        self.opened = False
        print("  [依赖] 关闭数据库会话")

def get_db():
    """生成器依赖：完整的事务管理生命周期"""
    db = DatabaseSession()
    db.open()
    try:
        yield db
        db.commit()       # 路由函数正常返回后提交
    except Exception:
        db.rollback()     # 路由函数抛异常时回滚
        raise             # 重新抛出异常，让 FastAPI 处理
    finally:
        db.close()        # 无论成功失败都关闭

@app.get("/success")
async def success_endpoint(db: DatabaseSession = Depends(get_db)):
    print("[路由] 执行业务逻辑（成功）")
    return {"status": "ok"}
# 控制台：
#   [依赖] 打开数据库会话
# [路由] 执行业务逻辑（成功）
#   [依赖] 提交事务
#   [依赖] 关闭数据库会话

@app.get("/failure")
async def failure_endpoint(db: DatabaseSession = Depends(get_db)):
    print("[路由] 执行业务逻辑（失败）")
    raise ValueError("模拟错误")
# 控制台：
#   [依赖] 打开数据库会话
# [路由] 执行业务逻辑（失败）
#   [依赖] 回滚事务
#   [依赖] 关闭数据库会话
# 客户端收到 500 错误
```

预期运行结果：生成器依赖在成功时提交事务，失败时回滚，无论如何都关闭会话。

**示例 3：完整场景——异步生成器依赖 + 应用级引擎**

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from functools import lru_cache

app = FastAPI()

@lru_cache
def get_engine():
    """应用级：数据库引擎（单例，包含连接池）"""
    return create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

@lru_cache
def get_session_factory(engine=Depends(get_engine)):
    """应用级：会话工厂（单例）"""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db(session_factory=Depends(get_session_factory)):
    """请求级：异步数据库会话（每次请求创建，自动事务管理）"""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """使用异步数据库会话"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user

# 引擎和会话工厂是应用级单例（启动时创建一次）
# 每个请求创建新的 AsyncSession（请求级隔离）
# 请求结束自动 commit/rollback/close
```

预期运行结果：应用级单例（引擎、连接池）避免重复创建，请求级会话保证数据隔离，异步生成器自动管理事务。

#### 使用场景与最佳实践

**适用场景**：请求级——数据库会话、当前用户、事务；应用级——配置、数据库引擎、连接池、缓存客户端；生成器级——任何需要清理的资源（文件句柄、网络连接、锁）。

**不适用场景**：需要在请求间共享可变状态（用 Redis 等外部存储，不要用依赖）。

**最佳实践**：
1. 数据库会话用请求级生成器依赖，自动管理事务
2. 配置对象用 `@lru_cache` 应用级单例
3. 数据库引擎/连接池在应用启动时创建（应用级），不要每次请求创建
4. 生成器依赖的标准模式：获取资源 → try → yield → except 回滚 → finally 关闭
5. 应用级依赖必须是无状态或线程安全的，不要在其中存储请求数据

**性能建议**：应用级单例避免重复创建昂贵资源（数据库引擎、Redis 连接池）。请求级依赖保证隔离性。两者结合是最佳实践——昂贵资源应用级，会话/事务请求级。

#### 常见坑点

**坑点 1：用 lru_cache 装饰请求级依赖导致数据错乱**

- 错误现象：多个请求共享同一个数据库会话，出现数据交叉污染
- 根本原因：`@lru_cache` 是进程级缓存，将请求级依赖变成了应用级
- 正确做法：只有无状态的配置类依赖才能用 `@lru_cache`，数据库会话等请求级资源绝对不能
- 预防措施：代码审查时检查 `@lru_cache` 装饰的依赖是否有状态

**坑点 2：生成器依赖中 yield 后修改了响应但不生效**

- 错误现象：在生成器依赖的 yield 之后修改 `response.headers`，但客户端看不到
- 根本原因：yield 之后响应已经发送给客户端，无法再修改
- 正确做法：需要修改响应的逻辑放在 yield 之前（通过 request.state 传递数据），或用中间件
- 预防措施：理解生成器依赖的执行时机——yield 前是请求阶段，yield 后是清理阶段（响应已发送）

---

### 7.3 yield 依赖的清理机制与异常传播

#### 概念解释

**yield 依赖是 FastAPI 中实现资源清理的核心机制，通过生成器函数的 `yield` 关键字将依赖分为「请求前」和「请求后」两个阶段。** yield 之前的代码在路由函数执行前运行（获取资源），yield 之后的代码在路由函数执行后运行（清理资源）。

打个比方：yield 依赖像餐厅的餐桌服务——客人入座前（yield 前）服务员摆好餐具（打开数据库会话），客人用餐时（yield 出的资源）使用餐具，客人离开后（yield 后）服务员收拾餐具（关闭会话、提交事务）。如果客人打翻了盘子（路由函数抛异常），服务员需要特别处理（回滚事务）。

**核心价值**：yield 依赖将资源的获取和清理封装在同一个函数中，确保资源总是被正确释放，即使路由函数抛出异常也不会泄漏。

#### 原理说明：yield 依赖的执行与异常传播

```mermaid
sequenceDiagram
    participant DI as FastAPI DI
    participant Dep as get_db 生成器
    participant Route as 路由函数
    DI->>Dep: 调用 get_db()
    Dep->>Dep: 打开会话（yield 前）
    Dep-->>DI: yield db
    DI->>Route: 注入 db，执行路由函数
    alt 路由函数正常返回
        Route-->>DI: 返回结果
        DI->>Dep: 恢复生成器（yield 后）
        Dep->>Dep: commit() + close()
    else 路由函数抛出异常
        Route-->>DI: raise Exception
        DI->>Dep: throw() 注入异常到生成器
        Dep->>Dep: rollback()（except 块）
        Dep->>Dep: close()（finally 块）
        Dep-->>DI: 重新 raise
        DI-->>客户端: 500 错误
    end
```

**yield 依赖的异常传播规则**：

| 场景 | yield 后行为 | 异常处理 |
|------|-------------|---------|
| 路由函数正常返回 | 执行 yield 后代码 | 无异常 |
| 路由函数抛异常 | 异常被 throw 到生成器的 yield 行 | except 块捕获，finally 清理 |
| yield 前抛异常 | yield 后代码不执行 | 需在 yield 前用 try/except |
| yield 后代码抛异常 | 覆盖原始异常（需注意） | 建议 yield 后只做清理，不抛新异常 |

> 🎯 面试高频：FastAPI 中 yield 依赖和普通依赖的区别？普通依赖只执行一次返回值，没有清理阶段；yield 依赖在 yield 后还有清理代码，适合资源管理。yield 依赖中如果路由函数抛异常，异常会被注入到生成器的 yield 行，可以用 try/except 捕获并回滚，finally 确保清理。这是 FastAPI 实现数据库事务自动管理的核心机制。

#### 代码示例

**示例 1：yield 依赖的标准事务管理模式**

```python
from fastapi import FastAPI, Depends, HTTPException

app = FastAPI()

class MockDB:
    def __init__(self):
        self.data = {}
        self.committed = False
        self.rolled_back = False

def get_db():
    db = MockDB()
    print("[依赖] 创建会话")
    try:
        yield db
        print("[依赖] 提交事务")
        db.committed = True
    except Exception as e:
        print(f"[依赖] 回滚事务: {e}")
        db.rolled_back = True
        raise  # 必须重新抛出，否则异常被吞掉
    finally:
        print("[依赖] 关闭会话")

@app.post("/users/")
async def create_user(name: str, db: MockDB = Depends(get_db)):
    print(f"[路由] 创建用户: {name}")
    db.data["name"] = name
    return {"id": 1, "name": name}

@app.get("/error")
async def error_endpoint(db: MockDB = Depends(get_db)):
    print("[路由] 模拟错误")
    raise HTTPException(status_code=400, detail="故意报错")

# POST /users/?name=张三 控制台：
# [依赖] 创建会话
# [路由] 创建用户: 张三
# [依赖] 提交事务
# [依赖] 关闭会话

# GET /error 控制台：
# [依赖] 创建会话
# [路由] 模拟错误
# [依赖] 回滚事务: 故意报错
# [依赖] 关闭会话
```

预期运行结果：正常请求提交事务，异常请求回滚事务，两种情况都关闭会话。

**示例 2：多个 yield 依赖的执行顺序（洋葱模型）**

```python
from fastapi import FastAPI, Depends

app = FastAPI()

def dep_a():
    print("A: before")
    yield "A"
    print("A: after")

def dep_b(a: str = Depends(dep_a)):
    print(f"B: before (got {a})")
    yield "B"
    print("B: after")

def dep_c(b: str = Depends(dep_b)):
    print(f"C: before (got {b})")
    yield "C"
    print("C: after")

@app.get("/onion")
async def onion_endpoint(c: str = Depends(dep_c)):
    print(f"路由函数: got {c}")
    return {"result": c}

# 控制台输出（洋葱模型：before 从外到内，after 从内到外）：
# A: before
# B: before (got A)
# C: before (got B)
# 路由函数: got C
# C: after
# B: after
# A: after
```

预期运行结果：多个 yield 依赖形成洋葱模型——before 从最外层到最内层执行，after 从最内层到最外层执行。

**示例 3：完整场景——异步 yield 依赖 + 上下文管理器**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
import aioredis

app = FastAPI()

# 应用级 Redis 连接池（启动时创建）
redis_pool = None

@app.on_event("startup")
async def startup():
    global redis_pool
    redis_pool = aioredis.from_url("redis://localhost", decode_responses=True)

@app.on_event("shutdown")
async def shutdown():
    await redis_pool.close()

async def get_redis():
    """请求级：从连接池获取连接，使用后自动归还"""
    async with redis_pool.client() as conn:
        print("[依赖] 获取 Redis 连接")
        try:
            yield conn
            print("[依赖] Redis 操作成功")
        except Exception as e:
            print(f"[依赖] Redis 操作失败: {e}")
            raise
        finally:
            print("[依赖] 归还 Redis 连接")

@app.get("/cache/{key}")
async def get_cache(key: str, redis=Depends(get_redis)):
    value = await redis.get(key)
    if not value:
        await redis.set(key, "default-value", ex=3600)
        value = "default-value"
    return {"key": key, "value": value}

# GET /cache/user:1
# [依赖] 获取 Redis 连接
# [依赖] Redis 操作成功
# [依赖] 归还 Redis 连接
```

预期运行结果：异步 yield 依赖管理 Redis 连接，从连接池获取、使用、自动归还，异常时正确传播。

#### 使用场景与最佳实践

**适用场景**：数据库会话和事务管理；文件句柄管理；网络连接（Redis、MQ）；锁的获取和释放；临时资源创建和清理。

**不适用场景**：纯计算无资源的依赖（用普通函数即可）；需要修改响应的逻辑（用中间件）。

**最佳实践**：
1. yield 依赖的标准模式：获取资源 → try → yield → except 回滚 → finally 关闭
2. except 块中必须 `raise` 重新抛出异常，否则异常被吞掉客户端收到 200
3. yield 后只做清理操作（commit/rollback/close），不要抛新异常
4. 多个 yield 依赖形成洋葱模型，理解执行顺序
5. 异步资源用 `async def` + `yield`，同步资源用 `def` + `yield`

**性能建议**：yield 依赖的清理代码在响应发送后执行（FastAPI 会先发送响应再执行清理），所以清理操作不会增加响应延迟。但如果清理操作很慢（如大事务提交），会占用 worker 线程，影响后续请求。

#### 常见坑点

**坑点 1：except 块中忘记 raise 导致异常被吞**

- 错误现象：路由函数抛出异常，但客户端收到 200 成功响应
- 根本原因：生成器依赖的 except 块捕获了异常但没有重新 raise
- 正确做法：except 块中处理完（如回滚）后必须 `raise`
- 预防措施：团队约定 yield 依赖的 except 块必须以 `raise` 结尾

```python
# 错误：异常被吞掉
def get_db_bad():
    db = Session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        # 忘记 raise！异常被吞，客户端收到 200

# 正确：重新抛出
def get_db_good():
    db = Session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise  # 必须重新抛出
    finally:
        db.close()
```

**坑点 2：yield 后修改响应不生效**

- 错误现象：在 yield 后设置 `response.headers["X-Custom"] = "value"`，客户端收不到
- 根本原因：yield 后响应已经发送，无法修改
- 正确做法：需要修改响应的逻辑放在 yield 前，通过 `request.state` 传递数据给中间件，或直接用中间件
- 预防措施：理解 yield 依赖的 after 阶段是「响应已发送后的清理」，不是「响应发送前的处理」

---

## 八、数据库会话与认证授权依赖

### 8.1 数据库会话依赖

#### 概念解释

**数据库会话依赖是 FastAPI 项目中最常用的依赖，通过生成器函数管理数据库会话的创建、事务提交/回滚和连接关闭。** 它将数据库资源管理从业务代码中完全抽离，业务函数只需声明 `db: Session = Depends(get_db)` 即可获得会话。

打个比方：数据库会话依赖像银行的柜台窗口——每个客户（请求）来了，银行给一个专属柜台（数据库会话），客户办完业务（路由函数），银行自动结账（提交事务）或抹账（回滚），然后关闭窗口（释放连接）。客户不需要关心窗口怎么开、怎么关，只需要在窗口前办业务。

**核心价值**：数据库会话依赖实现「每个请求一个会话」的最佳实践，自动管理事务边界，防止连接泄漏，业务代码专注于数据操作。

#### 原理说明：数据库会话依赖的完整生命周期

```mermaid
stateDiagram-v2
    [*] --> 创建会话: 请求进入
    创建会话 --> 执行业务: yield db
    执行业务 --> 提交事务: 正常返回
    执行业务 --> 回滚事务: 抛出异常
    提交事务 --> 关闭会话
    回滚事务 --> 关闭会话
    关闭会话 --> [*]: 请求结束
```

**同步 vs 异步数据库会话对比**：

| 维度 | 同步（SQLAlchemy ORM） | 异步（SQLAlchemy asyncio） |
|------|----------------------|--------------------------|
| 驱动 | psycopg2 / pymysql | asyncpg / aiomysql |
| 函数 | `def get_db()` | `async def get_db()` |
| 会话 | `Session` | `AsyncSession` |
| 查询 | `db.query(User).all()` | `await db.execute(select(User))` |
| 提交 | `db.commit()` | `await db.commit()` |
| 性能 | 线程池执行 | 原生异步，高并发 |

> 🎯 面试高频：FastAPI 中为什么数据库会话要用生成器依赖（yield）？三个原因：① 自动事务管理——正常提交、异常回滚；② 连接自动关闭——finally 确保连接归还连接池，防止泄漏；③ 请求级隔离——每个请求独立会话，避免多请求共享会话导致的数据错乱。如果用普通函数 return db，会话永远不会关闭，连接池很快耗尽。

#### 代码示例

**示例 1：同步数据库会话依赖（SQLAlchemy）**

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "postgresql://user:pass@localhost/mydb"
engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=40)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """同步数据库会话依赖：标准事务管理模式"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
```

预期运行结果：每个请求获得独立会话，正常提交、异常回滚、自动关闭。

**示例 2：异步数据库会话依赖（SQLAlchemy asyncio）**

```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/mydb"
engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=40, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    """异步数据库会话依赖"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# main.py
from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
```

预期运行结果：异步会话支持 `await`，高并发下不阻塞事件循环。

**示例 3：完整场景——多数据库会话依赖（读写分离）**

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

app = FastAPI()

# 主库（写）
write_engine = create_async_engine("postgresql+asyncpg://user:pass@master/db")
WriteSession = async_sessionmaker(write_engine, class_=AsyncSession)

# 从库（读）
read_engine = create_async_engine("postgresql+asyncpg://user:pass@slave/db")
ReadSession = async_sessionmaker(read_engine, class_=AsyncSession)

async def get_write_db():
    """写库会话依赖"""
    async with WriteSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_read_db():
    """读库会话依赖（只读，不需要事务）"""
    async with ReadSession() as session:
        yield session

@app.get("/articles/{article_id}")
async def get_article(article_id: int, read_db: AsyncSession = Depends(get_read_db)):
    """读操作：走从库"""
    result = await read_db.execute(select(Article).where(Article.id == article_id))
    return result.scalar_one_or_none()

@app.post("/articles/")
async def create_article(article: ArticleCreate, write_db: AsyncSession = Depends(get_write_db)):
    """写操作：走主库"""
    db_article = Article(**article.model_dump())
    write_db.add(db_article)
    await write_db.flush()
    return db_article
```

预期运行结果：读操作走从库（负载均衡），写操作走主库（数据一致性），两个依赖独立管理各自的会话和事务。

#### 使用场景与最佳实践

**适用场景**：所有需要数据库操作的接口；读写分离架构；多数据源场景；事务管理。

**不适用场景**：纯内存计算接口；使用 NoSQL（MongoDB）时用对应的异步客户端依赖。

**最佳实践**：
1. 数据库引擎（engine）是应用级单例，包含连接池，不要每次请求创建
2. 会话（session）是请求级，通过生成器依赖创建和销毁
3. 异步项目用 asyncpg + SQLAlchemy asyncio，同步项目用 psycopg2
4. 连接池配置 `pool_size`（通常 20）和 `max_overflow`（通常 40）
5. `expire_on_commit=False` 避免提交后访问属性触发额外查询
6. 读写分离时定义多个会话依赖（get_read_db / get_write_db）

**性能建议**：异步数据库驱动（asyncpg）比同步驱动（psycopg2）在高并发下吞吐量高 3-5 倍。新项目优先用异步。连接池大小 = CPU 核数 × 2 + 磁盘数（经验公式），避免过大导致数据库连接数耗尽。

#### 常见坑点

**坑点 1：同步数据库驱动在 async def 中阻塞事件循环**

- 错误现象：使用 psycopg2 + SQLAlchemy 同步会话，但路由函数是 `async def`，高并发下性能极差
- 根本原因：同步数据库操作阻塞事件循环，其他请求无法处理
- 正确做法：要么用异步驱动（asyncpg + AsyncSession），要么把路由函数改为 `def`（FastAPI 自动放线程池）
- 预防措施：项目启动时确定同步/异步技术栈，不要混用

**坑点 2：忘记关闭会话导致连接池耗尽**

- 错误现象：运行一段时间后报 `QueuePool limit of size 20 overflow 40 reached, connection timed out`
- 根本原因：数据库会话没有正确关闭，连接泄漏
- 正确做法：用生成器依赖 + finally 关闭，或用 `async with session_factory() as session` 上下文管理器
- 预防措施：所有数据库会话必须通过依赖注入获取，不要在函数内手动创建

---

### 8.2 认证授权依赖链

#### 概念解释

**认证授权依赖链是通过多层嵌套依赖实现的身份验证和权限控制体系。** 典型链路：`get_current_user`（验证 Token 并获取用户）→ `get_current_active_user`（检查是否激活）→ `get_current_superuser`（检查是否管理员），每层依赖在前一层基础上增加权限检查。

打个比方：认证授权链像机场安检——第一道检查身份证和登机牌（验证 Token），第二道检查是否在禁飞名单（用户是否激活），第三道检查是否有 VIP 通道权限（是否管理员）。每道关卡只做自己的检查，通过后进入下一道，最终到达登机口（路由函数）。

**核心价值**：分层认证授权实现「最小权限原则」——不同接口需要不同权限级别，通过依赖不同层级的依赖来精确控制，代码复用且易于维护。

#### 原理说明：OAuth2 + JWT 认证流程

```mermaid
sequenceDiagram
    participant C as 客户端
    participant S as FastAPI 服务器
    participant DB as 数据库
    C->>S: POST /login {username, password}
    S->>DB: 查询用户
    DB-->>S: 用户信息（含密码哈希）
    S->>S: 验证密码（bcrypt）
    S-->>C: 200 {access_token: "jwt...", token_type: "bearer"}
    C->>S: GET /profile Authorization: Bearer jwt...
    S->>S: OAuth2PasswordBearer 提取 Token
    S->>S: JWT 解码（验证签名+过期）
    S->>DB: 根据 user_id 查询用户
    DB-->>S: 用户对象
    S->>S: 检查 is_active / is_superuser
    S-->>C: 200 用户资料
```

**认证依赖链的层级设计**：

| 层级 | 依赖函数 | 职责 | 失败状态码 |
|------|---------|------|-----------|
| 1 | `oauth2_scheme` | 从 Header 提取 Bearer Token | 401（未认证） |
| 2 | `get_current_user` | 解码 JWT、查询用户 | 401（Token 无效） |
| 3 | `get_current_active_user` | 检查用户是否激活 | 400（已禁用） |
| 4 | `get_current_superuser` | 检查是否管理员 | 403（权限不足） |

> 🎯 面试高频：FastAPI 中 OAuth2PasswordBearer 的作用？它是一个依赖，从请求头 `Authorization: Bearer <token>` 中提取 Token 字符串。如果请求头中没有 Authorization 或格式不对，自动返回 401。它本身不验证 Token，只是提取，验证逻辑在 `get_current_user` 中完成。`tokenUrl` 参数用于 Swagger UI 的「Authorize」按钮，告诉文档去哪里获取 Token。

#### 代码示例

**示例 1：JWT 认证依赖链基础实现**

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

app = FastAPI()

# 配置
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 方案：从 Authorization Header 提取 Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# 模拟用户数据库
fake_users_db = {
    "alice": {"username": "alice", "password": "secret123", "is_active": True, "is_superuser": False},
    "admin": {"username": "admin", "password": "admin123", "is_active": True, "is_superuser": True},
}

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode({"sub": subject, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """第2层：解码 JWT，获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """第3层：检查用户是否激活"""
    if not current_user["is_active"]:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user

async def get_current_superuser(current_user: dict = Depends(get_current_user)):
    """第4层：检查是否管理员"""
    if not current_user["is_superuser"]:
        raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
    return current_user

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """登录接口：返回 JWT Token"""
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    access_token = create_access_token(subject=user["username"])
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_my_profile(current_user: dict = Depends(get_current_active_user)):
    """需要登录的接口"""
    return current_user

@app.get("/admin/users")
async def list_all_users(_: dict = Depends(get_current_superuser)):
    """需要管理员权限的接口"""
    return list(fake_users_db.values())
```

预期运行结果：登录获取 JWT，携带 Token 访问 `/users/me` 返回当前用户，访问 `/admin/users` 需要管理员权限。

**示例 2：基于角色的权限控制（RBAC）**

```python
from fastapi import FastAPI, Depends, HTTPException
from enum import Enum

app = FastAPI()

class Role(str, Enum):
    USER = "user"
    EDITOR = "editor"
    ADMIN = "admin"

# 模拟当前用户（实际从 JWT 解析）
async def get_current_user():
    return {"id": 1, "username": "alice", "roles": [Role.USER, Role.EDITOR]}

class RoleChecker:
    """可调用对象依赖：检查用户是否拥有指定角色"""
    def __init__(self, required_roles: list[Role]):
        self.required_roles = required_roles

    async def __call__(self, current_user: dict = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])
        if not any(role in user_roles for role in self.required_roles):
            raise HTTPException(
                status_code=403,
                detail=f"需要角色: {[r.value for r in self.required_roles]}",
            )
        return current_user

# 创建不同角色的检查器
require_user = RoleChecker([Role.USER])
require_editor = RoleChecker([Role.EDITOR, Role.ADMIN])
require_admin = RoleChecker([Role.ADMIN])

@app.get("/articles/")
async def list_articles(_: dict = Depends(require_user)):
    return {"articles": []}

@app.post("/articles/")
async def create_article(_: dict = Depends(require_editor)):
    return {"message": "文章已创建"}

@app.delete("/articles/{article_id}")
async def delete_article(_: dict = Depends(require_admin)):
    return {"message": "文章已删除"}
```

预期运行结果：通过可调用对象依赖实现灵活的 RBAC，不同接口要求不同角色。

**示例 3：完整场景——API Key + JWT 双认证模式**

```python
from fastapi import FastAPI, Depends, Header, HTTPException
from jose import jwt, JWTError

app = FastAPI()

API_KEYS = {"service-a-key-123": "service-a", "service-b-key-456": "service-b"}
SECRET_KEY = "jwt-secret"

async def verify_api_key(x_api_key: str = Header(None)):
    """API Key 认证：服务间调用"""
    if x_api_key and x_api_key in API_KEYS:
        return {"type": "api_key", "service": API_KEYS[x_api_key]}
    return None

async def verify_jwt(authorization: str = Header(None)):
    """JWT 认证：用户端调用"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"type": "jwt", "user_id": payload.get("sub")}
    except JWTError:
        return None

async def get_current_principal(
    api_key_principal: dict | None = Depends(verify_api_key),
    jwt_principal: dict | None = Depends(verify_jwt),
):
    """双认证：支持 API Key 或 JWT，至少一种有效"""
    if api_key_principal:
        return api_key_principal
    if jwt_principal:
        return jwt_principal
    raise HTTPException(status_code=401, detail="需要 API Key 或 JWT 认证")

@app.get("/api/data")
async def get_data(principal: dict = Depends(get_current_principal)):
    """支持 API Key 和 JWT 两种认证方式的接口"""
    return {"principal": principal, "data": "敏感数据"}
```

预期运行结果：接口同时支持服务间 API Key 认证和用户端 JWT 认证，两种方式都能通过。

#### 使用场景与最佳实践

**适用场景**：用户登录认证（JWT/OAuth2）；API 密钥认证（服务间调用）；角色权限控制（RBAC）；多因素认证；微服务网关认证。

**不适用场景**：完全公开的接口（不需要认证）；内部测试环境（可临时禁用认证）。

**最佳实践**：
1. 密码用 bcrypt/argon2 哈希存储，不要明文存储
2. JWT 设置合理的过期时间（15-30 分钟），用 Refresh Token 机制续期
3. 认证依赖链分层设计，每层只做一个检查
4. 401（未认证）和 403（已认证但无权限）区分使用
5. 生产环境 SECRET_KEY 从环境变量读取，不要硬编码
6. 用 `OAuth2PasswordBearer` 的 `tokenUrl` 让 Swagger UI 支持一键认证
7. 管理员接口用 `get_current_superuser` 依赖，不要在函数内手动检查角色

**性能建议**：`get_current_user` 每次请求都查数据库，高频接口可将用户信息缓存到 Redis（TTL = Token 过期时间），减少数据库压力。但要注意缓存一致性——用户信息变更时清除缓存。

#### 常见坑点

**坑点 1：JWT 不设置过期时间导致 Token 永久有效**

- 错误现象：用户修改密码后，旧 Token 仍然有效
- 根本原因：JWT 是无状态的，一旦签发无法撤销，不设置过期时间意味着永久有效
- 正确做法：设置 `exp` 过期时间（15-30 分钟），配合 Refresh Token 机制；需要撤销时维护 Token 黑名单（Redis）
- 预防措施：JWT 必须包含 `exp` 字段，生产环境 Token 过期时间不超过 1 小时

**坑点 2：在路由函数中手动检查权限而非使用依赖**

- 错误现象：每个需要管理员权限的函数都写 `if not user.is_superuser: raise 403`，代码重复
- 根本原因：没有利用依赖注入的分层授权机制
- 正确做法：定义 `get_current_superuser` 依赖，需要管理员的接口声明 `_: User = Depends(get_current_superuser)`
- 预防措施：团队约定所有权限检查通过依赖实现，不要在业务函数中写权限判断

---

## 九、全局依赖、路由依赖与依赖覆盖

### 9.1 全局依赖与路由级依赖

#### 概念解释

**全局依赖是在应用级别（`app = FastAPI(dependencies=[...])`）或路由级别（`APIRouter(dependencies=[...])` / `@app.get(dependencies=[...])`）声明的依赖，对范围内所有接口自动生效，无需在每个函数参数中声明。** 这使得认证、日志、限流等横切关注点可以统一应用。

打个比方：全局依赖像大楼的门禁系统——安装在大楼入口（应用级），所有进入大楼的人都要刷卡（认证），不需要每个办公室再装一个门禁。路由级依赖像楼层门禁——只有进入特定楼层（某组路由）才需要额外刷卡。

**核心价值**：全局/路由级依赖避免在每个接口重复声明相同依赖，实现横切关注点的统一管理，修改时只需改一处。

#### 原理说明：三级依赖的作用范围

```mermaid
graph TB
    subgraph 应用级全局依赖
        A[app = FastAPI(dependencies=[Depends(verify_api_key)])]
    end
    subgraph 路由级依赖
        B[router = APIRouter(dependencies=[Depends(rate_limit)])]
    end
    subgraph 接口级依赖
        C[@app.get(dependencies=[Depends(audit_log)])]
    end
    A -->|所有接口| D[请求]
    B -->|该 router 所有接口| D
    C -->|该接口| D
    D --> E[路由函数]
```

**三级依赖对比**：

| 级别 | 声明方式 | 作用范围 | 典型用途 |
|------|---------|---------|---------|
| 应用级 | `FastAPI(dependencies=[...])` | 所有接口 | 全局认证、API Key、请求 ID |
| 路由级 | `APIRouter(dependencies=[...])` | 该 router 下所有接口 | 模块级认证、限流 |
| 接口级 | `@app.get(dependencies=[...])` | 单个接口 | 特定权限、审计日志 |

> 🎯 面试高频：全局依赖和接口参数中声明的依赖有什么区别？全局依赖通过 `dependencies=[Depends(...)]` 声明，依赖的返回值不会注入到路由函数（只是执行副作用），适合认证、日志等不需要返回值的场景。函数参数中声明的依赖（`db: Session = Depends(get_db)`）会将返回值注入函数，适合需要使用依赖结果的场景。两者可以同时使用，全局依赖先执行。

#### 代码示例

**示例 1：应用级全局依赖（API Key 认证）**

```python
from fastapi import FastAPI, Depends, Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    """全局依赖：所有接口都需要 API Key"""
    if x_api_key != "secret-key":
        raise HTTPException(status_code=401, detail="无效的 API Key")

# 应用级：所有接口都执行 verify_api_key
app = FastAPI(dependencies=[Depends(verify_api_key)])

@app.get("/public/data")
async def public_data():
    """自动应用全局 API Key 认证"""
    return {"data": "公开数据"}

@app.get("/secure/data")
async def secure_data():
    """同样自动应用全局认证"""
    return {"data": "安全数据"}

# 所有接口都需要 X-API-Key: secret-key 请求头
# 不需要在每个函数中声明依赖
```

预期运行结果：所有接口自动要求 API Key，无需逐个声明。

**示例 2：路由级依赖（模块认证）**

```python
from fastapi import FastAPI, APIRouter, Depends, HTTPException

app = FastAPI()

async def verify_user_token(authorization: str = Header(None)):
    """用户认证依赖"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="需要登录")
    return {"user_id": 1}

async def verify_admin_token(authorization: str = Header(None)):
    """管理员认证依赖"""
    if authorization != "Bearer admin-token":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return {"user_id": 1, "role": "admin"}

# 公开路由：无认证
public_router = APIRouter(prefix="/public")
@public_router.get("/health")
async def health():
    return {"status": "ok"}

# 用户路由：需要用户认证
user_router = APIRouter(prefix="/users", dependencies=[Depends(verify_user_token)])
@user_router.get("/profile")
async def profile():
    return {"message": "用户资料"}

# 管理员路由：需要管理员认证
admin_router = APIRouter(prefix="/admin", dependencies=[Depends(verify_admin_token)])
@admin_router.get("/dashboard")
async def dashboard():
    return {"message": "管理员仪表盘"}

app.include_router(public_router)
app.include_router(user_router)
app.include_router(admin_router)

# /public/health → 无需认证
# /users/profile → 需要 Bearer Token
# /admin/dashboard → 需要管理员 Token
```

预期运行结果：不同 router 应用不同的认证依赖，实现模块级权限隔离。

**示例 3：完整场景——多级依赖组合（全局 + 路由 + 接口）**

```python
from fastapi import FastAPI, APIRouter, Depends, Header, HTTPException, Request
import time

app = FastAPI()

# 1. 应用级：请求计时（所有接口）
async def add_request_time(request: Request):
    request.state.start_time = time.time()
    yield
    duration = (time.time() - request.state.start_time) * 1000
    print(f"请求耗时: {duration:.1f}ms")

app = FastAPI(dependencies=[Depends(add_request_time)])

# 2. 路由级：API 版本检查（/api/v1 下所有接口）
async def check_api_version(x_api_version: str = Header("v1")):
    if x_api_version not in ("v1", "v2"):
        raise HTTPException(status_code=400, detail="不支持的 API 版本")

v1_router = APIRouter(prefix="/api/v1", dependencies=[Depends(check_api_version)])

# 3. 接口级：审计日志（特定接口）
async def audit_log(request: Request):
    print(f"[审计] {request.method} {request.url.path}")

@v1_router.get("/users/{user_id}", dependencies=[Depends(audit_log)])
async def get_user(user_id: int):
    """同时应用：全局计时 + 路由级版本检查 + 接口级审计日志"""
    return {"id": user_id}

@v1_router.get("/items/")
async def list_items():
    """只应用：全局计时 + 路由级版本检查"""
    return {"items": []}

app.include_router(v1_router)
```

预期运行结果：`/api/v1/users/1` 同时执行三级依赖，`/api/v1/items/` 执行前两级依赖。

#### 使用场景与最佳实践

**适用场景**：应用级——全局认证、API Key、请求 ID、计时；路由级——模块认证、版本检查、限流；接口级——特定权限、审计日志、幂等性检查。

**不适用场景**：需要使用依赖返回值的场景（必须在函数参数中声明）；只有个别接口需要的依赖（直接在接口声明即可）。

**最佳实践**：
1. 全局依赖只做副作用（认证、日志、计时），不依赖返回值
2. 需要使用返回值的依赖（db、current_user）在函数参数中声明
3. 路由级依赖用于模块级横切关注点，避免每个接口重复声明
4. 三级依赖可以组合使用，执行顺序：应用级 → 路由级 → 接口级 → 函数参数
5. 公开接口（健康检查、Webhook）可以通过单独的 router 排除全局依赖

**性能建议**：全局依赖对每个请求都执行，确保其逻辑轻量（< 1ms）。不要在全局依赖中做数据库查询或外部调用，否则所有接口都受影响。

#### 常见坑点

**坑点 1：全局依赖中需要返回值但无法注入函数**

- 错误现象：在 `dependencies=[Depends(get_current_user)]` 中声明了认证依赖，但路由函数中拿不到 user 对象
- 根本原因：`dependencies` 列表中的依赖只执行副作用，返回值不注入函数
- 正确做法：需要返回值时在函数参数中声明 `current_user: User = Depends(get_current_user)`，全局依赖只做验证不返回
- 预防措施：理解 `dependencies` 参数和函数参数依赖的区别

**坑点 2：健康检查接口被全局认证拦截导致监控失败**

- 错误现象：K8s 健康检查 `/health` 返回 401，Pod 被标记为不健康
- 根本原因：全局 API Key 认证应用到了所有接口，包括健康检查
- 正确做法：将健康检查放在独立的 router 中，不包含全局认证；或在全局依赖中排除特定路径
- 预防措施：设计全局依赖时考虑排除健康检查、metrics、Webhook 等公开端点

---

### 9.2 依赖覆盖与高级用法

#### 概念解释

**依赖覆盖（dependency_overrides）是 FastAPI 提供的测试机制，允许在运行时替换任意依赖的实现。** 除了测试，还可以用于多环境配置、A/B 测试、特性开关等场景。

打个比方：依赖覆盖像戏剧的替补演员——正式演出用 A 角（真实依赖），但排练或特定场次时用 B 角（Mock 依赖）。角色（依赖接口）不变，只是扮演者（实现）换了，剧情照常推进。

**核心价值**：依赖覆盖让代码与外部资源解耦，测试可以快速、稳定、可重复地运行，是持续集成和自动化测试的基础。

#### 原理说明：依赖覆盖的查找机制

```mermaid
graph TB
    A[请求进入] --> B[FastAPI 解析依赖]
    B --> C{依赖在<br/>overrides 中?}
    C -->|是| D[执行覆盖函数]
    C -->|否| E[执行原始依赖]
    D --> F[注入结果]
    E --> F
    F --> G[路由函数执行]
```

**依赖覆盖的高级用法**：

| 用法 | 说明 | 示例 |
|------|------|------|
| 测试 Mock | 替换数据库/外部 API | `override_get_db` 返回内存库 |
| 多环境 | 开发/测试/生产用不同实现 | 开发用 SQLite，生产用 PostgreSQL |
| 特性开关 | 根据配置启用/禁用功能 | `override_get_cache` 切换 Redis/内存 |
| A/B 测试 | 不同用户用不同实现 | 根据用户 ID 选择依赖实现 |

> 🎯 面试高频：dependency_overrides 的原理是什么？FastAPI 在解析依赖时，会先检查 `app.dependency_overrides` 字典中是否有该依赖的 key。如果有，就用对应的覆盖函数替代原始依赖执行。覆盖函数的签名必须与原依赖一致（包括 yield）。这是一个简单但强大的字典查找机制，不需要复杂的 IoC 容器。

#### 代码示例

**示例 1：测试中的依赖覆盖**

```python
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

app = FastAPI()

def get_db():
    """真实依赖：PostgreSQL"""
    print("使用真实数据库")
    yield {"db": "postgres"}

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: dict = Depends(get_db)):
    return {"id": user_id, "db": db}

# ===== 测试 =====
def override_get_db():
    """覆盖依赖：内存数据库"""
    print("使用测试数据库")
    yield {"db": "sqlite-memory"}

# 注册覆盖
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
response = client.get("/users/1")
# 控制台打印 "使用测试数据库"（不是真实数据库）
assert response.status_code == 200
assert response.json()["db"] == "sqlite-memory"

# 清除覆盖
app.dependency_overrides.clear()
```

预期运行结果：测试中使用覆盖的内存数据库，不连接真实 PostgreSQL。

**示例 2：基于环境的依赖切换**

```python
import os
from fastapi import FastAPI, Depends

app = FastAPI()

class EmailService:
    async def send(self, to: str, subject: str, body: str):
        raise NotImplementedError

class SMTPEmailService(EmailService):
    """生产环境：真实 SMTP 发送"""
    async def send(self, to, subject, body):
        print(f"[SMTP] 发送邮件给 {to}: {subject}")
        # 实际调用 SMTP 服务器

class ConsoleEmailService(EmailService):
    """开发环境：打印到控制台"""
    async def send(self, to, subject, body):
        print(f"[Console] 邮件给 {to}: {subject}\n{body}")

def get_email_service() -> EmailService:
    """根据环境返回不同实现"""
    if os.getenv("ENV") == "production":
        return SMTPEmailService()
    return ConsoleEmailService()

@app.post("/send-email")
async def send_email(to: str, service: EmailService = Depends(get_email_service)):
    await service.send(to, "测试邮件", "这是一封测试邮件")
    return {"sent": True}

# 开发环境：ENV 未设置 → ConsoleEmailService（打印到控制台）
# 生产环境：ENV=production → SMTPEmailService（真实发送）
```

预期运行结果：同一接口在不同环境使用不同的邮件服务实现，无需修改业务代码。

**示例 3：完整场景——依赖覆盖 + pytest fixture + 异步测试**

```python
# conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from main import app, get_db, Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@pytest_asyncio.fixture(scope="function")
async def async_client():
    """异步测试客户端：覆盖数据库依赖"""
    # 创建测试表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # 清理
    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# test_users.py
import pytest

@pytest.mark.asyncio
async def test_create_user(async_client):
    response = await async_client.post(
        "/users/",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_get_user_not_found(async_client):
    response = await async_client.get("/users/999")
    assert response.status_code == 404
```

预期运行结果：每个测试函数有独立的内存数据库，异步测试客户端自动覆盖依赖，测试间完全隔离。

#### 使用场景与最佳实践

**适用场景**：单元测试和集成测试；多环境配置切换；特性开关；A/B 测试；演示环境（用 Mock 数据）。

**不适用场景**：生产环境动态切换（应通过配置而非 overrides）；需要频繁切换的场景（overrides 是全局的，并发切换有风险）。

**最佳实践**：
1. 测试中用 pytest fixture 管理覆盖的注册和清除
2. 覆盖函数签名必须与原依赖一致（包括 yield/async）
3. 每个测试后 `clear()` 覆盖，防止泄漏
4. 多环境用依赖函数内部判断环境，而非生产环境用 overrides
5. 异步测试用 `httpx.AsyncClient + ASGITransport`，不要用 `TestClient`（同步）

**性能建议**：测试数据库用 SQLite 内存库（`:memory:`）速度最快，但注意 SQLite 和 PostgreSQL 的 SQL 方言差异。重要项目建议用测试专用 PostgreSQL（Docker 容器）保证一致性。

#### 常见坑点

**坑点 1：覆盖异步依赖时用了同步函数**

- 错误现象：覆盖 `async def get_db()` 时用了 `def override_get_db()`，报类型错误或行为异常
- 根本原因：覆盖函数的异步性必须与原依赖一致
- 正确做法：原依赖是 `async def`，覆盖也必须是 `async def`；原依赖有 yield，覆盖也必须有 yield
- 预防措施：复制原依赖的函数签名，只修改内部实现

**坑点 2：dependency_overrides 在多线程测试中互相干扰**

- 错误现象：并行运行测试时，一个测试的覆盖影响了另一个测试
- 根本原因：`dependency_overrides` 是应用级全局字典，多线程并发修改不安全
- 正确做法：测试串行运行（pytest 默认），或每个测试用独立的 app 实例
- 预防措施：不要在测试中并行修改 `dependency_overrides`；CI 中 pytest 不加 `-n` 并行参数

---

## 十、APIRouter 与路由模块化

### 10.1 APIRouter 基础

#### 概念解释

**APIRouter 是 FastAPI 提供的路由组织工具，允许将相关接口分组到独立的模块中，再通过 `app.include_router()` 注册到主应用。** 它是大型项目路由模块化的核心机制，避免所有路由写在一个 `main.py` 中。

打个比方：APIRouter 像图书馆的楼层索引——把所有书（接口）按类别分到不同楼层（users 模块、orders 模块、items 模块），每个楼层有自己的编号规则（prefix）和标识（tags），读者（客户端）通过大楼总索引（main.py）找到对应楼层。

**核心价值**：APIRouter 实现路由的模块化组织，每个模块独立维护，代码结构清晰，团队协作时避免冲突，支持前缀、标签、依赖等批量配置。

#### 原理说明：APIRouter 的注册与匹配机制

```mermaid
graph TB
    A[main.py<br/>FastAPI app] --> B[include_router(users.router)]
    A --> C[include_router(orders.router)]
    A --> D[include_router(items.router)]
    B --> E[users.py<br/>APIRouter(prefix=/users)]
    C --> F[orders.py<br/>APIRouter(prefix=/orders)]
    D --> G[items.py<br/>APIRouter(prefix=/items)]
    E --> H[GET /users/<br/>GET /users/{id}]
    F --> I[POST /orders/<br/>GET /orders/{id}]
    G --> J[GET /items/<br/>POST /items/]
```

**APIRouter 常用参数**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `prefix` | 路由前缀 | `"/users"` |
| `tags` | 文档分组标签 | `["用户管理"]` |
| `dependencies` | 路由级依赖 | `[Depends(verify_token)]` |
| `responses` | 通用响应文档 | `{404: {"description": "Not Found"}}` |
| `default_response_class` | 默认响应类型 | `JSONResponse` |
| `callbacks` | 回调路由（OpenAPI） | 用于 Webhook 文档 |

> 🎯 面试高频：APIRouter 和 Flask Blueprint 的区别？① APIRouter 支持依赖注入（dependencies 参数），Blueprint 不支持；② APIRouter 的 prefix 在 include_router 时可再次叠加，Blueprint 的 url_prefix 注册时指定；③ APIRouter 自动生成 OpenAPI 文档分组（tags），Blueprint 需要手动配置；④ APIRouter 支持异步路由，Blueprint 是同步 WSGI。

#### 代码示例

**示例 1：基础 APIRouter 用法**

```python
# app/routers/users.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["用户管理"])

class UserCreate(BaseModel):
    email: str
    password: str

@router.get("/", summary="获取用户列表")
async def list_users():
    return {"users": []}

@router.post("/", status_code=201, summary="创建用户")
async def create_user(user: UserCreate):
    return {"id": 1, "email": user.email}

@router.get("/{user_id}", summary="获取用户详情")
async def get_user(user_id: int):
    if user_id == 0:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"id": user_id, "email": "user@example.com"}
```

```python
# app/main.py
from fastapi import FastAPI
from app.routers import users, items, orders

app = FastAPI(title="电商 API")

# 注册路由模块
app.include_router(users.router)
app.include_router(items.router)
app.include_router(orders.router)

@app.get("/health", tags=["系统"])
async def health():
    return {"status": "ok"}
```

预期运行结果：用户相关接口在 `/users/` 路径下，文档中按「用户管理」分组。

**示例 2：APIRouter 带依赖和响应配置**

```python
# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException

async def verify_admin(authorization: str = Header(None)):
    if authorization != "Bearer admin-token":
        raise HTTPException(status_code=403, detail="需要管理员权限")

# 路由级依赖：该 router 下所有接口都需要管理员认证
router = APIRouter(
    prefix="/admin",
    tags=["管理员"],
    dependencies=[Depends(verify_admin)],
    responses={403: {"description": "权限不足"}},
)

@router.get("/dashboard")
async def dashboard():
    return {"stats": "管理员仪表盘数据"}

@router.get("/users/")
async def manage_users():
    return {"users": "所有用户列表"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    return {"deleted": user_id}
# 所有 /admin/* 接口自动需要管理员认证
# 文档中所有接口都标注 403 响应
```

预期运行结果：`/admin/*` 下所有接口自动应用管理员认证，无需逐个声明。

**示例 3：完整场景——多版本 API 路由组织**

```python
# app/routers/v1/users.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/users/")
async def list_users_v1():
    return {"version": "v1", "users": [{"id": 1, "name": "张三"}]}

# app/routers/v2/users.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/users/")
async def list_users_v2():
    return {"version": "v2", "data": {"items": [{"id": 1, "name": "张三", "email": "a@b.com"}]}}

# app/main.py
from fastapi import FastAPI
from app.routers.v1 import users as users_v1
from app.routers.v2 import users as users_v2

app = FastAPI(title="多版本 API")

# v1 版本
app.include_router(users_v1.router, prefix="/api/v1", tags=["v1-用户"])
# v2 版本
app.include_router(users_v2.router, prefix="/api/v2", tags=["v2-用户"])

# GET /api/v1/users/ → v1 格式
# GET /api/v2/users/ → v2 格式
```

预期运行结果：通过 prefix 实现 API 版本控制，同一资源的不同版本可以独立演进。

#### 使用场景与最佳实践

**适用场景**：中大型项目（接口超过 20 个）；团队协作（多人开发不同模块）；多版本 API；微服务模块化。

**不适用场景**：小型项目（< 10 个接口，一个 main.py 即可）；原型验证（快速迭代不需要模块化）。

**最佳实践**：
1. 按业务领域划分 router（users、orders、items），不要按技术类型划分
2. 每个 router 文件不超过 300 行，超过则进一步拆分
3. router 的 prefix 在定义时设置（`APIRouter(prefix="/users")`），include_router 时可叠加版本前缀
4. 用 tags 让 OpenAPI 文档按模块分组
5. 路由级依赖用于模块认证（如 admin router 全部需要管理员）
6. `__init__.py` 中统一导出 router，方便 main.py 导入

**性能建议**：APIRouter 的路由匹配在应用启动时完成，运行时无额外开销。include_router 的数量不影响请求性能（Starlette 前缀树匹配）。

#### 常见坑点

**坑点 1：prefix 重复导致路径错误**

- 错误现象：`APIRouter(prefix="/users")` 定义了前缀，include_router 时又加了 `prefix="/api"`，但接口内又写了 `/users/`，导致路径变成 `/api/users/users/`
- 根本原因：prefix 重复叠加
- 正确做法：router 内的路径不要包含 prefix（写 `@router.get("/")` 而非 `@router.get("/users/")`）
- 预防措施：团队约定 router 内路径相对 prefix，不要重复前缀

```python
# 错误：prefix 和路径重复
router = APIRouter(prefix="/users")
@router.get("/users/")  # 实际路径 /users/users/
async def bad():
    pass

# 正确：路径相对 prefix
router = APIRouter(prefix="/users")
@router.get("/")  # 实际路径 /users/
async def good():
    pass
```

**坑点 2：不同 router 中有相同路径导致覆盖**

- 错误现象：两个 router 都注册了 `GET /`，后注册的覆盖了先注册的
- 根本原因：FastAPI 按注册顺序匹配，相同路径后注册的不可达
- 正确做法：确保每个 router 有唯一 prefix，或检查路径冲突
- 预防措施：启动时检查路由表（`app.routes`），CI 中加路由冲突检测

---

### 10.2 大型项目路由架构

#### 概念解释

**大型 FastAPI 项目需要清晰的目录结构和路由组织策略，将路由、模型、依赖、服务分层管理。** 典型架构采用「分层架构 + 领域驱动」，路由层只处理 HTTP 请求/响应，业务逻辑在 service 层，数据访问在 repository 层。

打个比方：大型项目架构像连锁餐厅的组织——前台（路由层）负责接待顾客和上菜（HTTP 请求/响应），后厨（service 层）负责烹饪（业务逻辑），采购仓库（repository 层）负责食材存储（数据访问），食材标准（models/schemas）统一规范。各层职责分明，顾客不需要知道菜怎么做的，厨师不需要关心食材从哪买的。

**核心价值**：清晰的架构让大型项目可维护、可测试、可扩展，团队协作高效，新人上手快。

#### 原理说明：分层架构与依赖方向

```mermaid
graph TB
    subgraph 表现层
        A[API 路由层<br/>routers/]
    end
    subgraph 业务层
        B[服务层<br/>services/]
    end
    subgraph 数据层
        C[仓储层<br/>repositories/]
        D[模型层<br/>models/ + schemas/]
    end
    subgraph 基础设施
        E[数据库<br/>database.py]
        F[依赖注入<br/>dependencies.py]
        G[配置<br/>config.py]
    end
    A --> B
    B --> C
    C --> E
    A --> D
    B --> D
    A --> F
    F --> E
    F --> G
```

**推荐的项目目录结构**：

```
my_fastapi_project/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 应用入口
│   ├── config.py                # 配置管理（pydantic-settings）
│   ├── database.py              # 数据库连接与会话依赖
│   ├── dependencies.py          # 通用依赖（get_db, get_current_user）
│   ├── api/                     # API 路由层
│   │   ├── __init__.py
│   │   ├── deps.py              # API 层专用依赖
│   │   └── v1/                  # API v1 版本
│   │       ├── __init__.py
│   │       ├── users.py         # 用户路由
│   │       ├── orders.py        # 订单路由
│   │       └── items.py         # 商品路由
│   ├── core/                    # 核心组件
│   │   ├── __init__.py
│   │   ├── security.py          # JWT/密码哈希
│   │   └── exceptions.py        # 自定义异常
│   ├── models/                  # SQLAlchemy ORM 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── order.py
│   ├── schemas/                 # Pydantic Schema
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── order.py
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── order_service.py
│   ├── repositories/            # 数据访问层
│   │   ├── __init__.py
│   │   ├── base.py              # 通用 CRUD 基类
│   │   ├── user_repo.py
│   │   └── order_repo.py
│   └── tests/                   # 测试
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_users.py
│       └── test_orders.py
├── alembic/                     # 数据库迁移
├── requirements.txt
├── .env
└── README.md
```

> 🎯 面试高频：FastAPI 大型项目的推荐架构？分层架构：路由层（routers）处理 HTTP，服务层（services）处理业务逻辑，仓储层（repositories）处理数据访问，模型层（models/schemas）定义数据结构。依赖方向：路由 → 服务 → 仓储 → 数据库，上层依赖下层，下层不依赖上层。路由层不写业务逻辑，服务层不直接操作 HTTP。

#### 代码示例

**示例 1：分层架构的完整代码（用户模块）**

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class UserUpdate(BaseModel):
    full_name: str | None = None
    password: str | None = Field(None, min_length=8)

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    created_at: datetime
```

```python
# app/repositories/user_repo.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class UserRepository:
    """数据访问层：只做数据库操作，不包含业务逻辑"""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
```

```python
# app/services/user_service.py
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.core.exceptions import UserNotFoundError, EmailAlreadyExistsError

class UserService:
    """业务逻辑层：处理业务规则，不直接操作 HTTP"""
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, user_in: UserCreate):
        # 业务规则：邮箱唯一
        existing = await self.repo.get_by_email(user_in.email)
        if existing:
            raise EmailAlreadyExistsError(user_in.email)
        # 业务规则：密码哈希
        user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
        )
        return await self.repo.create(user)

    async def get_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user
```

```python
# app/api/v1/users.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/users", tags=["用户管理"])

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """依赖注入：创建 UserService（注入 Repository）"""
    return UserService(UserRepository(db))

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    service: UserService = Depends(get_user_service),
):
    """路由层：只处理 HTTP 请求/响应，业务逻辑委托给 Service"""
    return await service.create_user(user_in)

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user=Depends(get_current_active_user)):
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    return await service.get_user(user_id)
```

预期运行结果：分层架构中，路由层只做 HTTP 处理，服务层处理业务逻辑，仓储层处理数据访问，各层独立可测试。

**示例 2：通用 CRUD 仓储基类**

```python
# app/repositories/base.py
from typing import Generic, TypeVar, Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """通用 CRUD 仓储基类，所有具体仓储继承它"""
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: int) -> ModelType | None:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        obj = self.model(**obj_in.model_dump())
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, id: int, obj_in: UpdateSchemaType) -> ModelType | None:
        obj = await self.get(id)
        if not obj:
            return None
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(obj, field, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: int) -> bool:
        obj = await self.get(id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.flush()
        return True
```

```python
# app/repositories/item_repo.py
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate
from app.repositories.base import BaseRepository

class ItemRepository(BaseRepository[Item, ItemCreate, ItemUpdate]):
    """商品仓储：继承通用 CRUD，可添加商品特定查询"""
    def __init__(self, db):
        super().__init__(Item, db)

    async def get_by_category(self, category_id: int) -> list[Item]:
        from sqlalchemy import select
        result = await self.db.execute(
            select(Item).where(Item.category_id == category_id)
        )
        return list(result.scalars().all())
```

预期运行结果：通用基类提供标准 CRUD，具体仓储继承后自动获得，只需添加特定查询方法。

**示例 3：完整场景——API 版本管理与路由聚合**

```python
# app/api/v1/__init__.py
from fastapi import APIRouter
from app.api.v1 import users, orders, items

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(orders.router)
api_router.include_router(items.router)

# app/api/v2/__init__.py
from fastapi import APIRouter
from app.api.v2 import users as users_v2, analytics

api_router = APIRouter()
api_router.include_router(users_v2.router)
api_router.include_router(analytics.router)

# app/main.py
from fastapi import FastAPI
from app.api.v1 import api_router as v1_router
from app.api.v2 import api_router as v2_router

app = FastAPI(title="电商平台 API", version="2.0.0")

# 统一注册版本路由
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")

@app.get("/health", tags=["系统"])
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}
```

预期运行结果：通过 `__init__.py` 聚合路由，main.py 只需两行 include_router，新增模块只需在对应版本的 `__init__.py` 中添加。

#### 使用场景与最佳实践

**适用场景**：中大型项目（50+ 接口）；团队协作开发；需要长期维护的生产系统；多版本 API。

**不适用场景**：小型工具项目；快速原型验证；个人学习项目。

**最佳实践**：
1. 严格分层：路由层不写业务逻辑，服务层不操作 HTTP，仓储层不包含业务规则
2. 依赖注入贯穿各层：路由注入 Service，Service 注入 Repository，Repository 注入 Session
3. 用泛型基类（BaseRepository）减少重复 CRUD 代码
4. API 版本通过目录结构（v1/v2）+ prefix 管理
5. `__init__.py` 聚合 router，main.py 保持简洁
6. 每个模块（users/orders）有独立的 router、service、repository、schema
7. 测试按模块组织，与源码结构对应

**性能建议**：分层架构的性能开销可以忽略（函数调用级）。真正的性能瓶颈在数据库查询和外部调用。仓储层注意使用 `selectinload`/`joinedload` 避免 N+1 查询，服务层注意批量操作而非循环单条。

#### 常见坑点

**坑点 1：路由层写业务逻辑导致无法测试**

- 错误现象：路由函数中直接写数据库查询、业务判断、密码哈希，单元测试必须启动整个应用
- 根本原因：没有分层，业务逻辑与 HTTP 耦合
- 正确做法：业务逻辑抽到 Service 层，Service 不依赖 HTTP，可独立单元测试
- 预防措施：代码审查时检查路由函数是否超过 20 行，超过则考虑抽 Service

**坑点 2：循环导入（router 导入 service，service 导入 router）**

- 错误现象：启动时报 `ImportError: cannot import name 'X' from partially initialized module`
- 根本原因：分层不清晰，下层依赖了上层
- 正确做法：严格遵守依赖方向（路由→服务→仓储→数据库），下层不导入上层
- 预防措施：用类型注解（`from __future__ import annotations`）延迟解析，或重构依赖方向

---

## 十一、性能优化、测试与生产部署

### 11.1 性能优化

#### 概念解释

**FastAPI 性能优化是通过异步编程、连接池、缓存、响应优化等手段提升 API 吞吐量和降低延迟的实践。** FastAPI 本身已经很快，性能瓶颈通常在数据库查询、外部调用和序列化，而非框架本身。

打个比方：性能优化像交通治理——FastAPI 是一条宽阔的高速公路（框架本身不堵），但收费站（数据库查询）、红绿灯（外部 API 调用）、车辆载重（响应体大小）会造成拥堵。优化就是修 ETC 通道（连接池）、修立交桥（异步并发）、减轻车辆载重（响应压缩）。

**核心价值**：性能优化让相同硬件资源支撑更多用户，降低延迟提升用户体验，节省云服务器成本。

#### 原理说明：性能瓶颈定位与优化手段

```mermaid
graph LR
    A[请求延迟] --> B[网络传输]
    A --> C[框架处理]
    A --> D[数据库查询]
    A --> E[外部调用]
    A --> F[序列化]
    B --> G[GZip压缩 / CDN]
    C --> H[异步路由 / 减少中间件]
    D --> I[连接池 / 索引 / 缓存]
    E --> J[异步HTTP / 并发请求]
    F --> K[response_model / 减少字段]
```

**性能优化手段清单**：

| 优化手段 | 说明 | 预期收益 |
|---------|------|---------|
| 异步数据库驱动 | asyncpg 替代 psycopg2 | 高并发吞吐量 3-5 倍 |
| 连接池 | pool_size=20, max_overflow=40 | 避免频繁创建连接 |
| response_model | 限制输出字段 | 大字段场景减少 50%+ 体积 |
| Redis 缓存 | 缓存热点数据 | 热点查询延迟从 50ms → 1ms |
| GZip 中间件 | 压缩响应体 | 减少 60-80% 网络传输 |
| 异步并发 | asyncio.gather 并发调用 | 多个外部调用总延迟=最大者而非总和 |
| 数据库索引 | 常用查询字段建索引 | 查询速度 10-100 倍 |
| 批量操作 | 批量 insert/update | 减少数据库往返 |

> 🎯 面试高频：FastAPI 性能优化的关键点？① 用异步驱动（asyncpg/httpx）避免阻塞事件循环；② 数据库连接池合理配置；③ 热点数据用 Redis 缓存；④ response_model 过滤不必要字段；⑤ 多个独立 IO 操作用 asyncio.gather 并发；⑥ 数据库建合适索引；⑦ GZip 压缩大响应；⑧ 生产用多 worker（gunicorn + uvicorn）。

#### 代码示例

**示例 1：异步并发调用多个外部 API**

```python
import asyncio
import httpx
from fastapi import FastAPI

app = FastAPI()

@app.get("/dashboard")
async def dashboard():
    """并发调用三个外部 API，总延迟 = 最大者而非三者之和"""
    async with httpx.AsyncClient() as client:
        # 三个调用并发执行
        user_task = client.get("https://api.example.com/users/1")
        orders_task = client.get("https://api.example.com/orders?user_id=1")
        products_task = client.get("https://api.example.com/products?featured=true")

        # 等待所有完成
        user_resp, orders_resp, products_resp = await asyncio.gather(
            user_task, orders_task, products_task
        )

    return {
        "user": user_resp.json(),
        "orders": orders_resp.json(),
        "products": products_resp.json(),
    }
# 串行：100ms + 200ms + 150ms = 450ms
# 并发：max(100, 200, 150) = 200ms
```

预期运行结果：三个外部 API 并发调用，总延迟从 450ms 降到 200ms。

**示例 2：Redis 缓存热点数据**

```python
from fastapi import FastAPI, Depends
import redis
import json

app = FastAPI()

# 应用级 Redis 连接池
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_product_from_db(product_id: int) -> dict:
    """模拟数据库查询（耗时 50ms）"""
    return {"id": product_id, "name": "iPhone 15", "price": 9999, "stock": 100}

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """先查缓存，未命中再查数据库并回写缓存"""
    cache_key = f"product:{product_id}"

    # 1. 查 Redis 缓存
    cached = redis_client.get(cache_key)
    if cached:
        return {"source": "cache", "data": json.loads(cached)}

    # 2. 缓存未命中，查数据库
    product = get_product_from_db(product_id)

    # 3. 回写缓存，TTL 10 分钟
    redis_client.setex(cache_key, 600, json.dumps(product))

    return {"source": "database", "data": product}

# 第一次请求：source=database，延迟 ~50ms
# 第二次请求：source=cache，延迟 ~1ms
```

预期运行结果：热点商品数据缓存到 Redis，后续请求从缓存读取，延迟从 50ms 降到 1ms。

**示例 3：完整场景——数据库连接池 + 索引 + 批量操作**

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, text
from fastapi import FastAPI, Depends

# 连接池优化：pool_size + max_overflow + pool_pre_ping
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,           # 常驻连接数
    max_overflow=40,        # 峰值额外连接数
    pool_pre_ping=True,     # 连接前 ping 检查，避免使用断开的连接
    pool_recycle=3600,      # 1 小时回收连接，避免数据库超时断开
    echo=False,
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

app = FastAPI()

@app.post("/users/batch")
async def batch_create_users(users: list[dict], db: AsyncSession = Depends(get_db)):
    """批量插入：一次 SQL 插入多行，避免循环单条插入"""
    # 批量插入（SQLAlchemy 2.0 风格）
    await db.execute(
        text("INSERT INTO users (email, name) VALUES (:email, :name)"),
        [{"email": u["email"], "name": u["name"]} for u in users],
    )
    return {"created": len(users)}

@app.get("/users/")
async def list_users(
    page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_db)
):
    """分页查询：确保 email 和 created_at 有索引"""
    offset = (page - 1) * page_size
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(offset).limit(page_size)
    )
    return list(result.scalars().all())

# 数据库索引建议（Alembic 迁移）：
# CREATE INDEX idx_users_email ON users(email);
# CREATE INDEX idx_users_created_at ON users(created_at DESC);
# CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
```

预期运行结果：连接池避免频繁创建连接，批量插入减少数据库往返，索引加速查询和排序。

#### 使用场景与最佳实践

**适用场景**：生产环境高并发服务；响应延迟要求 < 100ms 的接口；QPS > 100 的热点接口；云服务器成本敏感的项目。

**不适用场景**：内部工具（QPS < 10）；原型验证；CPU 密集型任务（优化框架无用，需用多进程/队列）。

**最佳实践**：
1. 先压测定位瓶颈，再优化——不要过早优化
2. 异步项目全程用异步库（asyncpg、httpx、aioredis），不要混用同步库
3. 数据库连接池配置 `pool_pre_ping=True` 避免使用断开的连接
4. 热点数据用 Redis 缓存，设置合理 TTL
5. 多个独立 IO 操作用 `asyncio.gather` 并发
6. 数据库查询字段建索引，避免 `SELECT *`
7. 大响应用 GZip 压缩，`response_model` 过滤字段
8. 生产用 `gunicorn -k uvicorn.workers.UvicornWorker -w 2*CPU+1`

**性能建议**：用 `py-spy` 或 `cProfile` 做 CPU 分析，用 `starlette-prometheus` 做请求延迟监控。优化前先建立性能基线（QPS、P50/P95/P99 延迟），优化后对比验证。

#### 常见坑点

**坑点 1：在 async def 中使用同步数据库驱动**

- 错误现象：高并发下 QPS 上不去，事件循环被阻塞
- 根本原因：同步数据库操作（psycopg2）在 async def 中阻塞事件循环
- 正确做法：用异步驱动（asyncpg + SQLAlchemy asyncio），或路由函数用 `def`
- 预防措施：项目初始化时确定全异步技术栈，CI 中检查 async def 内是否有同步调用

**坑点 2：N+1 查询问题**

- 错误现象：列表接口查询 20 条记录，但发出了 21 条 SQL（1 条查列表 + 20 条查关联）
- 根本原因：循环中访问关联对象触发懒加载
- 正确做法：用 `selectinload` 或 `joinedload` 预加载关联数据
- 预防措施：开启 SQLAlchemy 日志（echo=True）在开发环境检查 SQL 数量

```python
from sqlalchemy.orm import selectinload

# 错误：N+1 查询
result = await db.execute(select(User))
users = result.scalars().all()
for user in users:
    print(user.orders)  # 每个 user 触发一次查询

# 正确：预加载关联
result = await db.execute(
    select(User).options(selectinload(User.orders))
)
users = result.scalars().all()
for user in users:
    print(user.orders)  # 已预加载，不触发额外查询
```

---

### 11.2 测试策略

#### 概念解释

**FastAPI 测试包括单元测试（测试 Service/Repository）、集成测试（测试 API 端点）和端到端测试（测试完整流程）。** FastAPI 提供 `TestClient`（同步）和 `httpx.AsyncClient + ASGITransport`（异步）两种测试客户端，配合 `dependency_overrides` 实现隔离测试。

打个比方：测试像质检流程——单元测试是检查每个零件（Service 函数）是否合格，集成测试是检查组装后的机器（API 端点）是否正常工作，端到端测试是检查整条生产线（用户注册→下单→支付）是否顺畅。依赖覆盖是「模拟测试环境」，用假零件（Mock）替代真实零件，测试不受外部资源影响。

**核心价值**：完善的测试保证代码质量，让重构和功能添加有安全网，CI/CD 自动化测试确保每次部署不引入回归。

#### 原理说明：测试金字塔与 FastAPI 测试工具

```mermaid
graph TB
    subgraph 端到端测试
        E2E[E2E Tests<br/>完整用户流程<br/>少量、慢]
    end
    subgraph 集成测试
        IT[Integration Tests<br/>API 端点测试<br/>中等数量]
    end
    subgraph 单元测试
        UT[Unit Tests<br/>Service/Repository<br/>大量、快]
    end
    UT --> IT --> E2E
    style UT fill:#90EE90
    style IT fill:#ffeb99
    style E2E fill:#ffcccc
```

**FastAPI 测试工具对比**：

| 工具 | 类型 | 异步支持 | 适用场景 |
|------|------|---------|---------|
| `TestClient` | 同步 | 内部处理异步路由 | 简单集成测试 |
| `httpx.AsyncClient + ASGITransport` | 异步 | 原生异步 | 异步测试、需要 async 断言 |
| `pytest-asyncio` | 测试框架 | 异步测试标记 | 运行 async test 函数 |
| `dependency_overrides` | 依赖替换 | - | 隔离外部依赖 |

> 🎯 面试高频：FastAPI 中 TestClient 和 httpx.AsyncClient 的区别？TestClient 是基于 requests 的同步客户端，内部会运行异步路由（通过 anyio），适合简单测试；httpx.AsyncClient + ASGITransport 是原生异步客户端，测试函数本身是 async，适合需要异步断言或复杂异步逻辑的测试。两者都能测试异步路由，新项目推荐用 httpx.AsyncClient。

#### 代码示例

**示例 1：TestClient 基础集成测试**

```python
# test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "iPhone", "price": 999.99},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "iPhone"
    assert data["price"] == 999.99

def test_validation_error():
    response = client.post(
        "/items/",
        json={"name": "a", "price": -10},  # name 太短、price 负数
    )
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert len(errors) == 2  # 两个字段错误
```

预期运行结果：TestClient 发送请求，断言状态码和响应体，校验错误返回 422。

**示例 2：异步测试 + 依赖覆盖**

```python
# conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from main import app, get_db, Base

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DB_URL)
TestingSession = async_sessionmaker(engine, expire_on_commit=False)

@pytest_asyncio.fixture(scope="function")
async def async_client():
    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestingSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# test_users.py
import pytest

@pytest.mark.asyncio
async def test_create_user(async_client):
    response = await async_client.post(
        "/users/",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_duplicate_email(async_client):
    # 先创建一个用户
    await async_client.post("/users/", json={"email": "dup@example.com", "password": "pass1234"})
    # 再创建相同邮箱
    response = await async_client.post("/users/", json={"email": "dup@example.com", "password": "pass1234"})
    assert response.status_code == 409
```

预期运行结果：每个测试有独立内存数据库，异步客户端发送请求，依赖覆盖隔离真实数据库。

**示例 3：完整场景——Service 层单元测试**

```python
# test_user_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.user_service import UserService
from app.core.exceptions import EmailAlreadyExistsError

@pytest.fixture
def mock_repo():
    """Mock Repository，不连接数据库"""
    repo = MagicMock()
    repo.get_by_email = AsyncMock(return_value=None)
    repo.create = AsyncMock(return_value=MagicMock(id=1, email="test@example.com"))
    return repo

@pytest.fixture
def user_service(mock_repo):
    return UserService(mock_repo)

@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_repo):
    from app.schemas.user import UserCreate
    user_in = UserCreate(email="test@example.com", password="password123")

    result = await user_service.create_user(user_in)

    # 验证调用了 repo.create
    mock_repo.create.assert_called_once()
    assert result.email == "test@example.com"

@pytest.mark.asyncio
async def test_create_user_duplicate_email(user_service, mock_repo):
    """邮箱已存在时抛出异常"""
    from app.schemas.user import UserCreate
    # Mock：邮箱已存在
    mock_repo.get_by_email = AsyncMock(return_value=MagicMock(email="existing@example.com"))

    user_in = UserCreate(email="existing@example.com", password="password123")

    with pytest.raises(EmailAlreadyExistsError):
        await user_service.create_user(user_in)

    # 验证没有调用 create
    mock_repo.create.assert_not_called()
```

预期运行结果：Service 层单元测试用 Mock Repository，不连接数据库，测试速度极快（毫秒级），专注于业务逻辑验证。

#### 使用场景与最佳实践

**适用场景**：所有生产级项目；CI/CD 自动化测试；重构前建立测试安全网；团队协作防止回归。

**不适用场景**：一次性脚本；原型验证（但建议养成写测试习惯）。

**最佳实践**：
1. 测试金字塔：大量单元测试（Service）+ 中等集成测试（API）+ 少量 E2E
2. 每个测试独立：用 fixture 管理数据库和依赖覆盖，测试间不共享状态
3. 测试命名清晰：`test_<功能>_<场景>_<预期结果>`
4. 用 `dependency_overrides` 隔离外部依赖，测试不连真实数据库/外部 API
5. 异步测试用 `httpx.AsyncClient + ASGITransport`，不用 `TestClient`
6. 测试覆盖正常路径、边界条件、异常场景
7. CI 中运行测试 + 覆盖率检查（pytest --cov）

**性能建议**：单元测试用 Mock 不连数据库，速度极快（< 10ms/个）。集成测试用 SQLite 内存库，比真实 PostgreSQL 快 10 倍。大量测试时用 `pytest-xdist` 并行运行（注意 dependency_overrides 全局问题）。

#### 常见坑点

**坑点 1：测试间依赖覆盖未清除导致污染**

- 错误现象：单独运行测试通过，一起运行时部分测试失败
- 根本原因：前一个测试的 `dependency_overrides` 影响了后一个测试
- 正确做法：在 fixture 的 teardown 中 `app.dependency_overrides.clear()`
- 预防措施：统一用 fixture 管理覆盖，不要在测试函数中手动设置

**坑点 2：TestClient 测试异步路由时事件循环冲突**

- 错误现象：使用 `TestClient` 测试含异步数据库的路由时报 `RuntimeError: There is no current event loop`
- 根本原因：TestClient 内部管理事件循环，与测试中的异步代码冲突
- 正确做法：异步项目用 `httpx.AsyncClient + ASGITransport`，不用 TestClient
- 预防措施：新项目统一用 httpx 异步测试客户端

---

### 11.3 生产部署配置

#### 概念解释

**生产部署是将 FastAPI 应用部署到服务器的完整配置，包括 ASGI 服务器选择、Worker 进程数、Gunicorn 配置、环境变量、日志、监控等。** 正确的生产配置保证应用稳定、高效、可观测。

打个比方：生产部署像餐厅开业——开发环境是后厨试菜（单厨师、随意），生产环境是正式营业（多个厨师=Worker、领班=Gunicorn、点餐系统=日志、卫生检查=监控）。每个环节都要标准化配置，才能应对高峰期的客流。

**核心价值**：生产级配置让应用在高并发下稳定运行，故障可快速定位，资源利用最大化。

#### 原理说明：生产部署架构

```mermaid
graph TB
    C[客户端] --> N[Nginx 反向代理<br/>SSL终止 / 负载均衡 / 静态文件]
    N --> G[Gunicorn<br/>管理 Worker 进程]
    G --> W1[Uvicorn Worker 1]
    G --> W2[Uvicorn Worker 2]
    G --> W3[Uvicorn Worker N]
    W1 --> DB[(PostgreSQL)]
    W2 --> DB
    W3 --> DB
    W1 --> R[(Redis 缓存)]
    W2 --> R
    W3 --> R
```

**生产部署关键配置**：

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| Worker 数 | `2 * CPU核数 + 1` | Gunicorn 进程数 |
| Worker 类 | `uvicorn.workers.UvicornWorker` | ASGI Worker |
| 超时 | 30s | 请求超时 |
| keepalive | 5s | 保持连接 |
| 日志 | info + 结构化 JSON | 可观测性 |
| 环境变量 | 从 .env / 配置中心读取 | 不硬编码密钥 |
| 健康检查 | `/health` 端点 | K8s liveness/readiness |

> 🎯 面试高频：FastAPI 生产环境为什么用 Gunicorn + Uvicorn 而不是直接 Uvicorn？① Gunicorn 是进程管理器，负责启动/监控/重启 Worker 进程，Uvicorn 是 ASGI 服务器处理请求；② Gunicorn 管理多进程（多核利用），Uvicorn 单进程是单线程异步；③ Gunicorn 支持优雅重启（graceful restart），Worker 崩溃自动重启；④ 直接 `uvicorn --workers N` 也可以多进程，但 Gunicorn 更成熟稳定，支持更多配置。

#### 代码示例

**示例 1：Gunicorn 配置文件**

```python
# gunicorn_config.py
import multiprocessing

# 绑定地址
bind = "0.0.0.0:8000"

# Worker 进程数：CPU核数 * 2 + 1
workers = multiprocessing.cpu_count() * 2 + 1

# ASGI Worker 类（必须用 UvicornWorker）
worker_class = "uvicorn.workers.UvicornWorker"

# 每个 Worker 的最大并发连接数
worker_connections = 1000

# 请求超时（秒）
timeout = 30

# 优雅重启超时
graceful_timeout = 30

# 保持连接秒数
keepalive = 5

# 最大请求数（防止内存泄漏，超过后重启 Worker）
max_requests = 1000
max_requests_jitter = 50

# 日志
accesslog = "-"  # stdout
errorlog = "-"
loglevel = "info"

# 进程名
proc_name = "fastapi-app"

# 预加载应用（减少内存占用，但注意数据库连接在 fork 前创建的问题）
preload_app = True
```

```bash
# 启动命令
gunicorn app.main:app -c gunicorn_config.py

# 或直接用 uvicorn 多 worker（简单场景）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

预期运行结果：Gunicorn 启动多个 Uvicorn Worker，利用多核 CPU，Worker 崩溃自动重启。

**示例 2：Docker 部署**

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 非 root 用户运行
RUN useradd -m appuser
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# 启动命令
CMD ["gunicorn", "app.main:app", "-c", "gunicorn_config.py"]
```

```yaml
# docker-compose.yml
version: "3.8"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    restart: always

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

预期运行结果：Docker Compose 一键启动 API + PostgreSQL + Redis，环境变量注入，数据持久化。

**示例 3：完整场景——生产环境 main.py 配置**

```python
# app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.config import get_settings
from app.api.v1 import api_router
from app.core.logging import setup_logging

settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化资源，关闭时清理"""
    # 启动
    logger.info(f"启动 {settings.APP_NAME} v{settings.VERSION}")
    # 初始化数据库连接池、Redis 等
    yield
    # 关闭
    logger.info("关闭应用，清理资源")
    # 关闭数据库连接池、Redis 连接

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,  # 生产关闭文档
    redoc_url=None,
    lifespan=lifespan,
)

# 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查端点：K8s liveness/readiness probe"""
    return {"status": "healthy", "version": settings.VERSION}

@app.get("/ready", tags=["系统"])
async def readiness_check():
    """就绪检查：验证数据库和 Redis 连接"""
    # 检查数据库连接
    # 检查 Redis 连接
    return {"status": "ready"}
```

预期运行结果：生产环境关闭 API 文档，配置 CORS 白名单，GZip 压缩，生命周期管理资源，健康检查和就绪检查分离。

#### 使用场景与最佳实践

**适用场景**：所有生产环境部署；云服务器（阿里云/腾讯云/AWS）；容器化部署（Docker/K8s）；Serverless（需调整为 ASGI handler）。

**不适用场景**：本地开发（用 `uvicorn --reload`）。

**最佳实践**：
1. 生产用 Gunicorn + UvicornWorker，Worker 数 = 2×CPU+1
2. 用 Nginx 做反向代理：SSL 终止、静态文件、负载均衡
3. 环境变量从配置中心或 .env 读取，密钥不硬编码
4. 生产关闭 `/docs`（`docs_url=None`）
5. 配置 `/health`（liveness）和 `/ready`（readiness）两个端点
6. 结构化 JSON 日志，包含 request_id、耗时、状态码
7. Docker 用非 root 用户运行，多阶段构建减小镜像
8. `max_requests` 配置防止内存泄漏（Worker 处理 N 个请求后重启）

**性能建议**：Worker 数不是越多越好——过多 Worker 会增加内存和上下文切换开销。`2×CPU+1` 是经验值，IO 密集型可适当增加，CPU 密集型减少。压测找到最佳 Worker 数。

#### 常见坑点

**坑点 1：preload_app=True 导致数据库连接在 fork 前创建**

- 错误现象：Gunicorn `preload_app=True` 时，多个 Worker 共享同一个数据库连接，导致连接冲突
- 根本原因：preload 模式下应用在 fork 前加载，数据库引擎/连接池在主进程创建，fork 后子进程继承但连接不可共享
- 正确做法：数据库引擎在 lifespan 中创建（Worker 启动后），或 `preload_app=False`
- 预防措施：理解 preload 的含义，数据库连接必须在 Worker 进程内创建

**坑点 2：生产环境开启 debug=True**

- 错误现象：生产环境报错时返回完整堆栈 traceback，泄露代码结构和敏感信息
- 根本原因：`FastAPI(debug=True)` 或环境变量 DEBUG=True
- 正确做法：生产 `debug=False`，注册全局异常处理器返回通用错误消息
- 预防措施：配置从环境变量读取，生产环境设置 DEBUG=False，CI 中检查

---

> 💡 **本章深度讲解**：性能优化、测试和生产部署是 FastAPI 从「能跑」到「生产可用」的关键三步。性能优化的核心是「不要阻塞事件循环」——全程异步、连接池、缓存、并发。测试的核心是「隔离」——dependency_overrides 替换外部依赖，pytest fixture 管理状态。生产部署的核心是「稳定」——Gunicorn 多 Worker、Nginx 反向代理、健康检查、结构化日志。这三章的知识让你从「会写接口」进阶到「能运维生产系统」。
>
> 📝 **本章精简总结**：
> 1. 性能优化：异步驱动、连接池、Redis 缓存、asyncio.gather 并发、response_model 过滤、GZip 压缩
> 2. 测试金字塔：大量单元测试（Service/Mock）+ 中等集成测试（API）+ 少量 E2E
> 3. 异步测试用 httpx.AsyncClient + ASGITransport，不用 TestClient
> 4. 测试后必须 clear dependency_overrides，防止测试间污染
> 5. 生产用 Gunicorn + UvicornWorker，Worker 数 = 2×CPU+1
> 6. 生产关闭 /docs 文档，debug=False
> 7. 配置 /health（liveness）和 /ready（readiness）端点
> 8. Nginx 反向代理：SSL 终止、负载均衡、静态文件

🎯 **梯度练习题**

**基础题⭐**
1. 写出 Gunicorn 配置文件的关键参数（bind、workers、worker_class、timeout）。
2. 异步测试中用什么客户端？为什么不用 TestClient？
3. 性能优化中 `asyncio.gather` 的作用是什么？举一个使用场景。

**进阶题⭐⭐**
4. 解释数据库 N+1 查询问题，以及如何用 selectinload 解决。
5. 设计一个完整的测试 fixture：每个测试有独立的内存 SQLite 数据库，自动覆盖 get_db 依赖，测试后清除覆盖和删除表。

**实战题⭐⭐⭐**
6. 实现一个生产级 FastAPI 应用的完整部署配置，包括：① gunicorn_config.py（多 Worker、超时、日志）；② Dockerfile（多阶段构建、非 root 用户、健康检查）；③ docker-compose.yml（API + PostgreSQL + Redis）；④ main.py（lifespan 管理资源、生产关闭文档、CORS 白名单、健康检查）。

---

## 🔗 关联笔记

- [[FastAPI-中间件与异常处理]]
- [[FastAPI-WebSocket实时通信]]
- [[FastAPI-封装LLM流式接口]]
- [[Python-异步编程asyncio]]
- [[Python-类型注解与mypy]]
- [[SQLAlchemy-ORM核心与查询]]
- [[RESTfulAPI设计原则]]
- [[Django-ORM与Admin体系]]
- [[Flask-轻量服务架构]]

## 📖 前置知识

- [[Python-语法基础与数据结构]]
- [[Python-异步编程asyncio]]
- [[Python-类型注解与mypy]]

## 🏷️ 相关标签

#Python #FastAPI #Web框架 #依赖注入 #路由 #异步

---

[[Home|🏠 返回首页]] · [[MOC-Python全栈|📚 返回分类]]
