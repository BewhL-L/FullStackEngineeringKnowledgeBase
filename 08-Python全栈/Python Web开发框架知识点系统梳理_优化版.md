---
title: Python Web 开发框架知识点系统梳理
tags: [Python全栈, Python, Web框架, Django, Flask, FastAPI, 面试]
created: 2026-08-13
updated: 2026-08-13
---

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


# Python Web 开发框架知识点系统梳理（优化版）

> **文档说明**：系统梳理 Python 三大主流 Web 框架——Django、Flask、FastAPI 的核心概念、架构、使用方式与选型对比。

---

## 1. 概述

Python Web 框架生态丰富，三大主流框架各有定位：

| 框架 | 定位 | 特点 | 适用场景 |
|------|------|------|----------|
| **Django** | 全栈重量级 | 自带 ORM/Admin/Auth/表单，"电池齐全" | 中大型项目、CMS、后台管理 |
| **Flask** | 轻量级微框架 | 核心精简，扩展丰富，灵活度高 | 小型项目、API、微服务、原型 |
| **FastAPI** | 现代异步框架 | 基于 Pydantic + Starlette，自动文档，高性能 | API 服务、异步场景、微服务 |

---


---
## 2. Django

### 2.1 核心架构（MTV）

> 🔍 **知识点深度解析**
>
> **作用**：Django 采用 MTV（Model-Template-View）架构将数据处理、展示与业务逻辑解耦，使团队可以分层开发、独立维护。
>
> **原理**：请求经 URLconf 路由到 View（业务逻辑层），View 操作 Model（ORM 读写数据库）并选择 Template 渲染；MTV 是 MVC 的变体——Django 的 View 实际对应 MVC 的 Controller，Template 对应 MVC 的 View。
>
> **用法要点**：① Model 用 ORM 描述数据结构与表关系 ② View 处理请求并返回响应（FBV 函数或 CBV 类） ③ Template 负责 HTML 渲染与展示 ④ URLconf 将 URL 映射到对应 View ⑤ 面试常考 MTV 与 MVC 的对应关系


```
Model（模型）→ 数据层（ORM）
Template（模板）→ 表现层
View（视图）→ 业务逻辑层
URLconf → URL 路由
```

### 2.2 项目结构

> 🔍 **知识点深度解析**
>
> **作用**：规范的项目结构区分全局配置与功能应用，是多人协作与长期可维护的基础。
>
> **原理**：Django 项目（project）包含全局配置（settings/urls/wsgi），应用（app）是独立功能模块（models/views/urls/admin 等），通过 INSTALLED_APPS 注册；manage.py 是命令行统一入口。
>
> **用法要点**：① 一个 project 可包含多个 app ② settings.py 集中配置数据库/中间件/模板等 ③ urls.py 分根路由与应用路由两级 ④ migrations 保存数据库变更历史 ⑤ 新增功能优先建独立 app 而非堆在单一模块


```
project/
├── manage.py          # 命令行工具
├── project/           # 项目配置
│   ├── settings.py    # 配置
│   ├── urls.py        # 根路由
│   └── wsgi.py/asgi.py
└── app/               # 应用
    ├── models.py      # 数据模型
    ├── views.py       # 视图
    ├── urls.py        # 应用路由
    ├── admin.py       # 后台管理
    ├── forms.py       # 表单
    └── migrations/    # 数据库迁移
```

### 2.3 ORM（核心）

> 🔍 **知识点深度解析**
>
> **作用**：ORM 让开发者用 Python 类和对象操作数据库，避免手写 SQL，显著提升开发效率与代码可移植性。
>
> **原理**：模型类映射到数据表、字段映射到列；QuerySet 是惰性序列，只有在迭代/切片/求值（list、len、bool）时才真正执行 SQL；select_related 用 SQL JOIN 预取一对一/多对一，prefetch_related 用额外查询+Python 关联解决多对多/反向外键的 N+1 问题。
>
> **用法要点**：① 用 select_related/prefetch_related 消除 N+1 ② values()/values_list() 返回轻量字典/元组 ③ 大数据量用 iterator() 防止内存溢出 ④ filter/get/exclude/order_by 为高频 API ⑤ 联表查询优先预加载关联对象


```python
# models.py
from django.db import models
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey("Author", on_delete=models.CASCADE)
    
    class Meta:
        db_table = "article"
        ordering = ["-created_at"]

# 查询
Article.objects.all()                    # 全部
Article.objects.filter(title__contains="Python")  # 过滤
Article.objects.get(id=1)                # 单条
Article.objects.order_by("-created_at")[:10]  # 排序+分页
Article.objects.select_related("author") # 联表查询（一对一/多对一）
Article.objects.prefetch_related("tags") # 预取（多对多/一对多）
```

### 2.4 视图与路由

> 🔍 **知识点深度解析**
>
> **作用**：视图处理请求并返回响应，路由将 URL 映射到底层视图函数或类，是 Web 框架的入口枢纽。
>
> **原理**：FBV 是普通函数接收 request 返回 response；CBV 继承 View 并通过 as_view() 分发 get/post 等方法；urls.py 的 path()/re_path() 用转换器（<int:pk>）提取路径参数。
>
> **用法要点**：① 用 @app/path 装饰器或 path() 绑定 URL 与方法 ② request.args/get_json() 取参 ③ jsonify 返回 JSON ④ 生产禁用 debug（代码泄露/任意执行风险） ⑤ 生产用 gunicorn/uwsgi 启动


```python
# views.py（FBV 函数视图）
from django.http import JsonResponse
def article_list(request):
    articles = Article.objects.all().values("id", "title")
    return JsonResponse(list(articles), safe=False)

# views.py（CBV 类视图）
from django.views.generic import ListView
class ArticleListView(ListView):
    model = Article
    template_name = "article_list.html"

# urls.py
from django.urls import path
urlpatterns = [
    path("articles/", article_list, name="article_list"),
    path("articles/<int:pk>/", ArticleDetailView.as_view()),
]
```

### 2.5 Admin 后台

```python

> 🔍 **知识点深度解析**
>
> **作用**：Django Admin 是内置的后台管理系统，自动根据模型生成 CRUD 界面，极少代码即可管理数据。
>
> **原理**：创建超级用户 python manage.py createsuperuser，在 admin.py 中 admin.site.register(Model) 注册模型即可管理。ModelAdmin 自定义列表显示（list_display）、搜索（search_fields）、过滤（list_filter）、分页（list_per_page）、只读字段（readonly_fields）、内联编辑（inlines）。Admin 的权限体系基于 User/Group/Permission，可控制模型级和对象级访问。
>
> **用法要点**：① admin.site.register(Model, ModelAdmin) 注册并自定义  ② list_display 控制列表列，search_fields 搜索，list_filter 过滤  ③ inlines 实现关联模型在同一页面编辑  ④ createsuperuser 创建管理员，权限基于 Group 分配  ⑤ 面试常考：Admin 定制、权限控制、ModelAdmin 常用配置

# admin.py
from django.contrib import admin
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title",)
    date_hierarchy = "created_at"
```

> 🔍 **知识点深度解析**
>
> **作用**：Django 是 Python 最成熟的全栈框架，理解其 ORM 和 MTV 架构是关键。
>
> **原理**：Django ORM 将 Python 类映射为数据库表，查询集（QuerySet）是惰性的——只有迭代/切片/调用时才执行 SQL。`select_related` 用 JOIN 一次查询（适合 ForeignKey/OneToOne），`pre_related` 用两次查询+Python 关联（适合 ManyToMany/反向 ForeignKey），解决 N+1 查询问题。Django 的 MTV 中 View 实际是 Controller，Template 是 View，命名与传统 MVC 不同。中间件（Middleware）是请求/响应的钩子链，可做认证、日志、跨域等。
>
> **用法要点**：① 避免在循环中执行查询（N+1），用 select_related/prefetch_related；② `values()`/`values_list()` 返回字典/元组，比模型实例轻量；③ 大数据量用 `iterator()` 避免内存溢出；④ 面试常考：ORM 查询、N+1 优化、QuerySet 惰性、中间件、MTV 架构、Django vs Flask。

---


---
## 3. Flask

### 3.1 核心特点

> 🔍 **知识点深度解析**
>
> **作用**：理解 Flask 的定位（轻量微框架）有助于在合适场景选型并设计合理架构。
>
> **原理**：Flask 核心只提供路由与请求处理，WSGI 层基于 Werkzeug，模板基于 Jinja2，其余功能靠第三方扩展；所谓“微”指核心小而非能力弱。
>
> **用法要点**：① 微框架=核心精简，功能靠扩展 ② 基于 Werkzeug（WSGI）+ Jinja2（模板） ③ 适合小型项目/API/微服务/原型 ④ 灵活度高但需自己组装组件 ⑤ 与 Django 最大区别是“内置电池” vs “按需扩展”


- 微框架：核心只包含路由 + 请求处理
- WSGI 基于 Werkzeug，模板基于 Jinja2
- 通过扩展添加功能（Flask-SQLAlchemy、Flask-Login 等）

### 3.2 基本使用

> 🔍 **知识点深度解析**
>
> **作用**：掌握 Flask 最小应用写法与路由装饰器是入门与写 API 的关键。
>
> **原理**：Flask(__name__) 创建应用，@app.route 注册路由并绑定视图函数；请求对象 request 提供参数/表单/JSON；jsonify 将 dict 序列化为 JSON 响应；app.run(debug=True) 仅用于开发。
>
> **用法要点**：① 用 @app.route 装饰器绑定 URL 与方法 ② request 提供参数/表单/JSON 访问 ③ jsonify 返回标准 JSON 响应 ④ 生产环境禁用 debug 模式 ⑤ 生产使用 gunicorn/uwsgi 启动


```python
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/api/articles", methods=["GET"])
def article_list():
    articles = Article.query.all()
    return jsonify([{"id": a.id, "title": a.title} for a in articles])

@app.route("/api/articles/<int:article_id>", methods=["GET"])
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    return jsonify({"id": article.id, "title": article.title})

if __name__ == "__main__":
    app.run(debug=True)
```

### 3.3 蓝图（Blueprint）

> 🔍 **知识点深度解析**
>
> **作用**：蓝图将路由与视图分组模块化，便于大型项目拆分、复用与测试。
>
> **原理**：Blueprint 在子模块中定义路由，再 register_blueprint 挂载到 app；可设 url_prefix 统一前缀；配合应用工厂模式可创建多个 app 实例（测试/多环境）。
>
> **用法要点**：① 用 Blueprint 拆分模块路由 ② url_prefix 统一模块前缀 ③ 配合工厂模式支持多实例 ④ 蓝图间可嵌套组合 ⑤ 适合中大型 Flask 项目组织


```python
# article/routes.py
from flask import Blueprint
article_bp = Blueprint("article", __name__, url_prefix="/api/articles")

@article_bp.route("/")
def list_articles():
    return jsonify(...)

# app.py
from article.routes import article_bp
app.register_blueprint(article_bp)
```

### 3.4 常用扩展

| 扩展 | 功能 |
|------|------|
| Flask-SQLAlchemy | ORM |
| Flask-Migrate | 数据库迁移 |
| Flask-Login | 用户认证 |
| Flask-WTF | 表单 + CSRF |
| Flask-Caching | 缓存 |
| Flask-CORS | 跨域 |
| Flask-JWT-Extended | JWT 认证 |
| Flask-RESTful / Flask-RESTX | REST API 框架 |

> 🔍 **知识点深度解析**
>
> **作用**：Flask 是轻量灵活的代表，适合需要精细控制的项目。
>
> **原理**：Flask 核心基于 Werkzeug（WSGI 工具库）和 Jinja2（模板引擎）。请求上下文（request）和应用上下文（current_app）通过 LocalStack 实现线程隔离——每个线程有独立的上下文，所以可以全局导入 request 而不会线程冲突。蓝图（Blueprint）将路由分组，实现模块化。Flask 的扩展通过 `init_app(app)` 模式支持应用工厂（Application Factory），便于创建多个 app 实例（测试/多环境）。
>
> **用法要点**：① 生产环境用 `gunicorn` 或 `uwsgi`，不要用 `app.run()`；② 用应用工厂模式 + 蓝图组织大型项目；③ 面试常考：Flask 上下文、WSGI、蓝图、与 Django 区别、扩展机制。

---


---
## 4. FastAPI

### 4.1 核心特点

> 🔍 **知识点深度解析**
>
> **作用**：明确 FastAPI 的差异化优势（异步+类型+自动文档）是选型与面试重点。
>
> **原理**：基于 Starlette（ASGI）提供原生 async，Pydantic 做数据校验/序列化，类型提示驱动参数解析与文档生成；性能接近 Node/Go。
>
> **用法要点**：① ASGI 异步、并发能力高 ② Pydantic 类型校验与序列化 ③ 自动生成 Swagger/ReDoc 文档 ④ 类型提示即接口文档 ⑤ 适合高性能 API 与异步场景


- 基于 Starlette（ASGI 异步）+ Pydantic（数据校验）
- 自动生成 OpenAPI/Swagger 文档
- 原生 async/await 支持
- 类型提示驱动，IDE 友好
- 性能接近 Node/Go

### 4.2 基本使用

> 🔍 **知识点深度解析**
>
> **作用**：掌握 FastAPI 路由、Pydantic 模型与响应模型是开发 API 的基础。
>
> **原理**：用 @app.get/post 装饰器声明路径操作，函数参数按类型区分路径/查询/请求体；Pydantic 模型定义入参与出参，response_model 控制返回字段；async def 支持异步处理。
>
> **用法要点**：① 用 Pydantic 模型定义请求/响应 ② response_model 过滤返回字段 ③ 路径/查询/请求体由类型自动解析 ④ 异步函数用 async def ⑤ HTTPException 返回标准错误


```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Article API", version="1.0")

class ArticleCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = None

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    
    class Config:
        from_attributes = True  # 支持 ORM 模型

@app.get("/api/articles", response_model=List[ArticleResponse])
async def list_articles(tag: Optional[str] = None):
    """获取文章列表"""
    articles = await get_articles(tag)
    return articles

@app.post("/api/articles", response_model=ArticleResponse, status_code=201)
async def create_article(article: ArticleCreate):
    """创建文章"""
    new_article = await create_article(article)
    return new_article

@app.get("/api/articles/{article_id}")
async def get_article(article_id: int):
    article = await get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
```

### 4.3 依赖注入

> 🔍 **知识点深度解析**
>
> **作用**：依赖注入实现可复用、可测试的共享逻辑（数据库会话、鉴权、公共参数）。
>
> **原理**：Depends 声明依赖，FastAPI 在调用路径操作前解析依赖树并注入；依赖可嵌套，yield 形式的依赖能自动管理资源（如 db 会话关闭）。
>
> **用法要点**：① Depends 注入依赖对象 ② 用 yield 管理资源生命周期 ③ 依赖可嵌套复用 ④ 常用于数据库会话与鉴权 ⑤ 同一依赖默认每次请求计算一次（可缓存）


```python
from fastapi import Depends
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/articles")
async def list_articles(db: AsyncSession = Depends(get_db)):
    return db.query(Article).all()
```

### 4.4 自动文档

- Swagger UI：`/docs`
- ReDoc：`/redoc`
- OpenAPI JSON：`/openapi.json`

> 🔍 **知识点深度解析**
>
> **作用**：FastAPI 是现代 Python API 框架的首选，高性能 + 自动文档 + 类型安全。
>
> **原理**：FastAPI 基于 ASGI（异步服务器网关接口），支持 async/await，比 WSGI（Django/Flask）并发性能高。Pydantic v2 用 Rust 实现数据校验和序列化，速度极快。类型提示不是装饰——FastAPI 通过类型提示自动做请求参数解析、数据校验、响应序列化和 OpenAPI 文档生成。依赖注入系统（Depends）实现可复用的依赖（数据库会话、认证用户），支持嵌套依赖。路径操作函数的参数按位置/类型自动解析：路径参数、查询参数、请求体。
>
> **用法要点**：① 用 Pydantic 模型定义请求/响应，不要直接返回 ORM 对象；② 异步函数中不要调用阻塞 IO（用 async 库或 `run_in_threadpool`）；③ 生产用 `uvicorn` 或 `gunicorn + uvicorn worker`；④ 面试常考：FastAPI 原理、ASGI vs WSGI、Pydantic、依赖注入、与 Flask/Django 对比、性能优势。

---

## 4.5 Django REST Framework（DRF）

DRF 是 Django 生态中最流行的 REST API 框架，提供序列化、视图集、路由、权限、过滤、分页等完整能力。

### 4.5.1 序列化器（Serializer）

> 🔍 **知识点深度解析**
>
> **作用**：DRF 的 Serializer 负责复杂数据与 JSON 的双向转换与校验，是 API 数据层核心。
>
> **原理**：Serializer 将模型实例/QuerySet 序列化为 JSON，也能将输入反序列化为校验后的数据；ModelSerializer 按模型自动生成字段；SerializerMethodField 自定义只读字段；validate_<field> 做字段级校验。
>
> **用法要点**：① ModelSerializer 自动生成字段 ② SerializerMethodField 自定义只读字段 ③ validate_xxx 自定义字段校验 ④ read_only/write_only 控制字段方向 ⑤ 注意嵌套序列化器的 N+1 与性能


```python
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = ["id", "title", "content", "author_name", "comment_count", "created_at"]
        read_only_fields = ["id", "created_at"]
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("标题至少5个字符")
        return value
```

### 4.5.2 视图集与路由

> 🔍 **知识点深度解析**
>
> **作用**：ViewSet+Router 把 CRUD 操作与 URL 自动绑定，显著减少样板代码。
>
> **原理**：ViewSet 将 list/retrieve/create/update/destroy 等动作封装为一个类；DefaultRouter 根据 ViewSet 自动生成 RESTful 路由；@action 添加自定义动作，detail=True 操作单条资源。
>
> **用法要点**：① ViewSet 聚合 CRUD 动作 ② Router 自动生成 URL ③ @action 添加自定义动作 ④ 权限/过滤/分页在 ViewSet 统一配置 ⑤ 相比 APIView 更简洁


```python
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "title"]
    
    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """自定义动作：发布文章"""
        article = self.get_object()
        article.status = "published"
        article.save()
        return Response({"status": "published"})

# 路由自动生成 CRUD
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r"articles", ArticleViewSet)
urlpatterns = [path("api/", include(router.urls))]
```

### 4.5.3 认证与权限

```python

> 🔍 **知识点深度解析**
>
> **作用**：DRF 认证与权限分离：认证确定用户身份，权限决定是否允许操作，支持多种认证方案和权限类。
>
> **原理**：认证类：SessionAuthentication（浏览器）、TokenAuthentication（Token 头）、JWTAuthentication（djangorestframework-simplejwt）、BasicAuthentication。权限类：IsAuthenticated（已登录）、IsAdminUser（管理员）、IsAuthenticatedOrReadOnly（认证可写/匿名只读）、DjangoModelPermissions（Django 模型权限）。自定义权限继承 BasePermission 重写 has_permission/has_object_permission。
>
> **用法要点**：① 认证（Authentication）识别身份，权限（Permission）决定访问  ② JWT 用 djangorestframework-simplejwt，access/refresh token  ③ 全局默认在 DEFAULT_AUTHENTICATION_CLASSES 配置  ④ 视图级用 permission_classes = [IsAuthenticated] 覆盖  ⑤ 面试常考：认证 vs 权限、JWT 流程、自定义权限

# 全局配置
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "1000/day"},
}
```

> 🔍 **知识点深度解析**
>
> **作用**：DRF 是 Django 构建 REST API 的事实标准，理解序列化和视图集是高效开发的关键。
>
> **原理**：Serializer 负责数据校验和序列化（Python 对象 ↔ JSON），`ModelSerializer` 基于模型自动生成字段和校验。ViewSet 将 CRUD 操作封装为一个类，配合 Router 自动生成 URL 路由（list/create/retrieve/update/partial_update/destroy）。权限（Permission）控制访问级别，认证（Authentication）验证用户身份，限流（Throttle）控制请求频率。`@action` 装饰器添加自定义动作，`detail=True` 表示操作单条资源。
>
> **用法要点**：① 用 `select_related/prefetch_related` 在 queryset 中预加载，避免序列化时 N+1；② 嵌套序列化器注意性能，大数据量用 `SerializerMethodField` 或单独接口；③ 面试常考：Serializer 原理、ViewSet vs APIView、权限与认证区别、限流、分页。

---

## 4.6 中间件机制

中间件是请求/响应的钩子链，在请求到达视图前和响应返回后执行。

### 三框架中间件对比

> 🔍 **知识点深度解析**
>
> **作用**：中间件统一在请求/响应前后插入横切逻辑（日志、鉴权、CORS、限流），是框架的重要扩展点。
>
> **原理**：Django 中间件是含 __call__/process_* 的类，按 MIDDLEWARE 顺序形成处理链；Flask 用 before/after_request 钩子；FastAPI 用 @app.middleware 装饰器（基于 Starlette），三种机制本质都是“请求→视图→响应”的钩子。
>
> **用法要点**：① 中间件作用于请求前与响应后 ② Django 用类+列表顺序控制 ③ Flask 用 before/after_request 钩子 ④ FastAPI 用装饰器声明 ⑤ 常见用途：日志、CORS、鉴权、限流、计时


```python
# Django 中间件
class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        # 请求前
        start = time.time()
        response = self.get_response(request)
        # 响应后
        print(f"耗时: {time.time()-start:.3f}s")
        return response

# Flask 钩子
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    print(f"耗时: {time.time()-request.start_time:.3f}s")
    return response

# FastAPI 中间件（基于 Starlette）
@app.middleware("http")
async def add_process_time(request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response
```

**常见中间件用途**：认证、日志、跨域（CORS）、限流、请求计时、安全头、异常处理。

---

## 4.7 WebSocket 实时通信

```python

> 🔍 **知识点深度解析**
>
> **作用**：Python Web 框架通过 Channels（Django）、Flask-SocketIO、FastAPI WebSocket 支持实时双向通信。
>
> **原理**：Django Channels 替换 WSGI 为 ASGI，通过 channel layer（Redis）实现跨进程消息传递，消费者（Consumer）处理 WebSocket 连接。Flask-SocketIO 基于 python-socketio，支持房间和命名空间。FastAPI 原生支持 WebSocket（from fastapi import WebSocket），async def 处理收发。生产部署用 Daphne/Uvicorn（ASGI 服务器）。
>
> **用法要点**：① Django Channels：ASGI + channel layer（Redis）+ Consumer  ② FastAPI 原生 WebSocket：async def ws(websocket: WebSocket)  ③ Flask-SocketIO：@socketio.on + room 广播  ④ ASGI 服务器（Daphne/Uvicorn）替代 WSGI 支持长连接  ⑤ 面试常考：ASGI vs WSGI、Channels 架构、WebSocket 鉴权

# FastAPI WebSocket
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"收到: {data}")
    except WebSocketDisconnect:
        print(f"客户端 {client_id} 断开")

# Django Channels（需配置 ASGI）
# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("chat", self.channel_name)
        await self.accept()
    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send("chat", {"type": "chat_message", "message": data["message"]})
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))
```

---

## 4.8 认证授权体系

| 方案 | 特点 | 适用场景 |
|------|------|----------|
| **Session 认证** | 服务端存储 session，Cookie 传递 session_id | 传统 Web、同域应用 |
| **JWT** | 无状态，Token 包含用户信息，Header 传递 | SPA、前后端分离、微服务 |
| **OAuth2** | 第三方授权（微信/Google/GitHub 登录） | 社交登录、开放平台 |
| **API Key** | 简单密钥，放在 Header 或 Query | 服务间调用、开放 API |
| **Token 刷新** | Access Token（短期）+ Refresh Token（长期） | 安全要求高的应用 |

```python

> 🔍 **知识点深度解析**
>
> **作用**：Python Web 认证体系涵盖 Session/Cookie、Token/JWT、OAuth2 和 RBAC 权限模型。
>
> **原理**：Session 认证：服务端存 Session，Cookie 带 sessionid，Django/Flask 原生支持。Token 认证：无状态，Authorization: Bearer <token>，适合前后端分离和 API。JWT：Header.Payload.Signature，Payload 含用户信息和过期时间，签名防篡改。OAuth2：第三方登录授权码模式。RBAC：用户-角色-权限三级模型，Django Auth 内置 Group/Permission。
>
> **用法要点**：① Session 有状态适合 Web，JWT 无状态适合 API/微服务  ② JWT 三部分：Header.Payload.Signature，Payload 不加密勿存敏感信息  ③ OAuth2 授权码模式用于第三方登录  ④ RBAC：用户→角色→权限，Django auth 内置支持  ⑤ 面试常考：Session vs JWT、JWT 结构、OAuth2 流程、RBAC

# JWT 认证流程
# 1. 用户登录 → 验证密码 → 生成 Access Token + Refresh Token
# 2. 前端存储 Token（localStorage/内存）
# 3. 请求时 Header: Authorization: Bearer <access_token>
# 4. Access Token 过期 → 用 Refresh Token 换取新的 Access Token
# 5. 登出 → 前端删除 Token（服务端可加入黑名单）
```

---

## 4.9 其他 Web 框架

| 框架 | 特点 | 适用场景 |
|------|------|----------|
| **Tornado** | 异步非阻塞，长连接友好 | 高并发实时应用 |
| **Sanic** | 异步，类 Flask API，性能高 | 高性能 API |
| **Quart** | Flask 的异步版本（ASGI） | Flask 项目迁移异步 |
| **Starlette** | 轻量 ASGI 框架，FastAPI 底层 | 高性能底层框架 |
| **Bottle** | 单文件微框架，极简 | 微型服务/原型 |

---


> 🔍 **知识点深度解析**
>
> **作用**：Python 生态还有 Tornado（异步）、Sanic（高性能异步）、Starlette（ASGI 工具包）、Bottle（单文件）等框架。
>
> **原理**：Tornado：Facebook 开源，自带异步 IOLoop 和 WebSocket，适合长轮询/长连接，但生态较小。Sanic：类 Flask API + async/await，高性能 ASGI 框架，支持 WebSocket。Starlette：FastAPI 的底层框架，轻量 ASGI 工具包，可独立使用。Bottle：单文件微框架，适合小型工具。选型：FastAPI（新项目 API 首选）、Django（全栈/管理后台）、Flask（轻量灵活）。
>
> **用法要点**：① Tornado：异步+WebSocket，适合长连接场景  ② Sanic：Flask 风格 + async，高性能  ③ Starlette：FastAPI 底层，轻量 ASGI 工具包  ④ 选型：FastAPI（API）、Django（全栈）、Flask（轻量）  ⑤ 面试常考：框架对比、ASGI 框架、选型依据


---
## 5. 框架选型对比

| 维度 | Django | Flask | FastAPI |
|------|--------|-------|---------|
| 架构 | 全栈 MTV | 微框架 + 扩展 | ASGI 异步 |
| ORM | 内置（强大） | 需扩展（SQLAlchemy） | 需扩展（SQLAlchemy/SQLModel） |
| 异步 | 3.0+ 支持 ASGI | 不原生支持 | 原生 async |
| 自动文档 | 无（需 drf-yasg） | 无（需 flask-restx） | 内置 Swagger/ReDoc |
| 数据校验 | forms/serializers | 需扩展 | Pydantic 内置 |
| 后台管理 | 内置 Admin | 需扩展 | 无 |
| 学习曲线 | 较陡（概念多） | 平缓 | 平缓（需懂 async） |
| 性能 | 中 | 中 | 高 |
| 生态成熟度 | 最高 | 高 | 快速增长 |

**选型建议**：
- 快速开发后台/CMS → Django
- 小型项目/灵活架构 → Flask
- API 服务/高性能/异步 → FastAPI

---


---
## 6. 面试高频考点

1. **Django ORM**：QuerySet 惰性、N+1 优化、select_related vs prefetch_related
2. **Django 中间件**：请求/响应钩子、执行顺序
3. **Flask 上下文**：request/current_app 线程隔离原理
4. **Flask 蓝图**：模块化路由、应用工厂
5. **FastAPI 原理**：ASGI、Pydantic、类型提示驱动
6. **WSGI vs ASGI**：同步 vs 异步、并发模型
7. **框架对比**：Django/Flask/FastAPI 选型
8. **RESTful API 设计**：见接口设计文档
9. **数据库迁移**：Django migrations / Alembic
10. **认证授权**：Session/JWT/OAuth2 实现
11. **DRF**：Serializer、ViewSet、Router、权限与限流
12. **WebSocket**：FastAPI WebSocket、Django Channels
13. **中间件**：三框架实现对比、常见用途
14. **表单验证**：Django Forms、Pydantic、WTForms
15. **信号机制**：Django Signals 解耦

---


---
## 📝 精简总结

- Django：全栈重量级，ORM/Admin/Auth 开箱即用，适合中大型项目
- Flask：轻量微框架，灵活度高，扩展丰富，适合小型项目和微服务
- FastAPI：现代异步框架，Pydantic 校验 + 自动文档 + 高性能，API 首选
- DRF：Django REST API 事实标准，Serializer+ViewSet+Router+权限+限流
- 中间件：请求/响应钩子链，三框架各有实现（Django类/Flask钩子/FastAPI装饰器）
- WebSocket：FastAPI 原生支持，Django 用 Channels（ASGI）
- 认证授权：Session（传统Web）、JWT（前后端分离）、OAuth2（第三方登录）、API Key（服务间）
- 其他框架：Tornado（异步长连接）、Sanic（高性能）、Quart（Flask异步版）
- ORM：Django 内置强大，Flask/FastAPI 用 SQLAlchemy
- 异步：FastAPI 原生支持，Django 3.0+ 支持 ASGI，Flask 不原生
- 选型：后台用 Django，灵活用 Flask，API 用 FastAPI

---

[[08-Python全栈/MOC-Python全栈|← 返回 Python 全栈 MOC]] | [[Home|🏠 返回首页]]
