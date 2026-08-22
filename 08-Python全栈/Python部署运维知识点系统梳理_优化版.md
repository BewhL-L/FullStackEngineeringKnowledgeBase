---
title: Python 部署运维知识点系统梳理
tags: [Python全栈, Python, 部署, 运维, Gunicorn, Docker, Nginx, 面试]
created: 2026-08-13
updated: 2026-08-13
---

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


# Python 部署运维知识点系统梳理（优化版）

> **文档说明**：系统梳理 Python Web 应用的部署与运维，涵盖 WSGI/ASGI 服务器、进程管理、Nginx 反向代理、Docker 容器化、CI/CD、监控等。

---

## 1. 概述

Python Web 应用部署的典型架构：

```
客户端 → Nginx（反向代理/静态资源/负载均衡）
         → WSGI/ASGI 服务器（Gunicorn/Uvicorn）
         → Python 应用（Django/Flask/FastAPI）
         → 数据库/缓存
```

**关键组件**：
- **WSGI 服务器**：Gunicorn、uWSGI（同步，Django/Flask）
- **ASGI 服务器**：Uvicorn、Hypercorn（异步，FastAPI/Django3+）
- **进程管理**：Supervisor、systemd
- **反向代理**：Nginx
- **容器化**：Docker + Docker Compose
- **CI/CD**：GitHub Actions、GitLab CI、Jenkins

---


---
## 2. WSGI 服务器

### 2.1 Gunicorn

> 🔍 **知识点深度解析**
>
> **作用**：Gunicorn 是成熟的 WSGI 服务器，是部署 Django/Flask 的常用选择。
>
> **原理**：多 worker 预派生模型，主进程管理 worker；配合同步/异步 worker 类与 Nginx 反代；不支持原生 ASGI 需配 uvicorn worker。
>
> **用法要点**：① 预派生多 worker ② 主进程管理 ③ 配 Nginx 反代 ④ 同步/异步 worker ⑤ 原生不支持 ASGI


```bash
# 安装
pip install gunicorn

# 启动 Django
gunicorn myproject.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class gevent \
  --timeout 30 \
  --access-logfile access.log \
  --error-logfile error.log

# 配置文件 gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4  # 通常 = CPU核心数 * 2 + 1
worker_class = "gevent"  # 异步worker，IO密集推荐
timeout = 30
keepalive = 5
```

### 2.2 uWSGI

> 🔍 **知识点深度解析**
>
> **作用**：uWSGI 功能全面、配置强大的 WSGI 服务器，适合复杂部署。
>
> **原理**：支持多种协议、进程/线程混合模型与丰富调优；配置体系庞大，常与 Nginx 通过 socket 通信。
>
> **用法要点**：① 功能全面可深度调优 ② 进程/线程混合 ③ 协议多样 ④ 配置复杂 ⑤ 常配 Nginx socket


```ini
# uwsgi.ini
[uwsgi]
module = myproject.wsgi:application
http-socket = 0.0.0.0:8000
processes = 4
threads = 2
master = true
vacuum = true
die-on-term = true
```

### 2.3 Worker 类型选择

| Worker 类型 | 并发模型 | 适用场景 |
|-------------|----------|----------|
| sync | 多进程同步 | CPU 密集 |
| gevent | 协程（猴子补丁） | IO 密集 |
| eventlet | 协程 | IO 密集 |
| gthread | 多线程 | 混合 |

> 🔍 **知识点深度解析**
>
> **作用**：WSGI 服务器是 Python 应用与 Web 服务器之间的桥梁。
>
> **原理**：WSGI（Web Server Gateway Interface）是 Python Web 的标准接口协议，定义了应用端（可调用对象）和服务器端的交互方式。Gunicorn 用 pre-fork 模型：master 进程启动后 fork 出多个 worker 进程，每个 worker 独立处理请求。worker 数量公式：`CPU核心数 * 2 + 1`，但 IO 密集型可适当增加。gevent worker 通过猴子补丁（monkey patch）将标准库的阻塞 IO 替换为非阻塞，实现协程级并发，适合 IO 密集场景。Gunicorn 不支持静态文件，需要 Nginx 处理。
>
> **用法要点**：① worker 数不是越多越好，过多会导致上下文切换开销；② 长连接/流式响应用异步 worker；③ 用 `--max-requests` 防止内存泄漏（worker 处理一定请求后重启）；④ 面试常考：WSGI 原理、Gunicorn worker 模型、worker 数计算、gevent 原理。

---


---
## 3. ASGI 服务器

### 3.1 Uvicorn

> 🔍 **知识点深度解析**
>
> **作用**：Uvicorn 是轻量高性能 ASGI 服务器，是运行 FastAPI 的首选。
>
> **原理**：基于 uvloop 与 httptools，支持 HTTP/1.1 与 WebSocket；常作为 Gunicorn 的 uvicorn worker 以获得进程管理。
>
> **用法要点**：① ASGI 服务器 ② uvloop 高性能 ③ 支持 WebSocket ④ 常配 Gunicorn worker ⑤ 运行 FastAPI/Starlette


```bash
# 启动 FastAPI
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info

# 生产环境用 Gunicorn 管理 Uvicorn worker
gunicorn main:app \
  -k uvicorn.workers.UvicornWorker \
  -w 4 \
  -b 0.0.0.0:8000
```

### 3.2 ASGI vs WSGI

> 🔍 **知识点深度解析**
>
> **作用**：理解 ASGI 与 WSGI 差异是选型异步栈与评估并发能力的基础。
>
> **原理**：WSGI 同步、一连接一线程；ASGI 异步、单进程处理多并发连接，支持 WebSocket/HTTP2；ASGI 向后兼容 WSGI 应用。
>
> **用法要点**：① WSGI 同步模型 ② ASGI 异步并发 ③ ASGI 支持 WebSocket ④ ASGI 兼容 WSGI ⑤ 按是否需要异步选型


| 维度 | WSGI | ASGI |
|------|------|------|
| 异步 | 不支持 | 原生支持 |
| 并发 | 多进程/线程 | 协程 + 多进程 |
| 长连接 | 不支持 | WebSocket/SSE |
| 性能 | 中 | 高（IO密集） |
| 框架 | Django/Flask | FastAPI/Django3+ |

---


---
## 4. 进程管理

### 4.1 Supervisor

> 🔍 **知识点深度解析**
>
> **作用**：Supervisor 用纯 Python 管理进程，简化后台服务守护与自启。
>
> **原理**：通过配置文件定义要守护的进程，自动重启崩溃进程、集中日志；适合无 systemd 的环境（如容器/旧系统）。
>
> **用法要点**：① 纯 Python 进程管理 ② 崩溃自动重启 ③ 集中日志 ④ 配置简单 ⑤ 适合容器/无 systemd


```ini
# /etc/supervisor/conf.d/myapp.conf
[program:myapp]
command=/path/to/venv/bin/gunicorn myproject.wsgi -c gunicorn.conf.py
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/myapp/err.log
stdout_logfile=/var/log/myapp/out.log
environment=DJANGO_SETTINGS_MODULE="myproject.settings.prod"
```

```bash
supervisorctl reread
supervisorctl update
supervisorctl status
supervisorctl restart myapp
```

### 4.2 systemd

> 🔍 **知识点深度解析**
>
> **作用**：systemd 是 Linux 主流初始化系统，适合生产服务化管理。
>
> **原理**：用 unit 文件定义服务、依赖与重启策略，支持开机自启、日志接入 journald；是服务器部署的标准方式。
>
> **用法要点**：① 系统级服务管理 ② 开机自启 ③ 重启策略可配 ④ journald 日志 ⑤ 生产标准方式


```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Python App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/gunicorn myproject.wsgi -c gunicorn.conf.py
Restart=always
RestartSec=5
Environment=DJANGO_SETTINGS_MODULE=myproject.settings.prod

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable myapp
systemctl start myapp
systemctl status myapp
```

---


---
## 5. Nginx 反向代理

```nginx
server {
    listen 80;
    server_name example.com;
    
    # 静态资源（Django collectstatic）
    location /static/ {
        alias /path/to/project/static/;
        expires 30d;
    }
    
    # 媒体文件
    location /media/ {
        alias /path/to/project/media/;
    }
    
    # 动态请求转发到 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }
}
```

---


---
## 6. Docker 容器化

### 6.1 Dockerfile

> 🔍 **知识点深度解析**
>
> **作用**：Dockerfile 定义应用镜像构建，是容器化部署的起点。
>
> **原理**：用基础镜像、依赖安装、代码拷贝、暴露端口与启动命令；多用多阶段构建减小体积、缓存依赖层加速构建。
>
> **用法要点**：① 基础镜像选型 ② 多阶段构建瘦身 ③ 依赖层缓存 ④ 非 root 运行 ⑤ 明确 CMD/ENTRYPOINT


```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 依赖缓存优化
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 收集静态文件（Django）
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "myproject.wsgi:application", "-c", "gunicorn.conf.py"]
```

### 6.2 Docker Compose

> 🔍 **知识点深度解析**
>
> **作用**：Docker Compose 用声明式配置编排多容器应用，简化本地与中小部署。
>
> **原理**：docker-compose.yml 定义服务、网络、卷与依赖；一条命令拉起 Web+DB+Cache 整套环境，便于开发与环境一致。
>
> **用法要点**：① 声明式多服务 ② 一键拉起整套 ③ 共享网络与卷 ④ 服务依赖编排 ⑤ 适合开发/中小部署


```yaml
version: "3.8"
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: always

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - web

volumes:
  pgdata:
```

---

## 6.3 环境变量与配置管理

```python

> 🔍 **知识点深度解析**
>
> **作用**：环境变量是 12-Factor App 推荐的配置方式，将配置与代码分离，不同环境使用不同变量。
>
> **原理**：python-dotenv 从 .env 文件加载环境变量（开发用，.env 不提交 Git）。os.environ.get('KEY', 'default') 读取。Pydantic BaseSettings（FastAPI）自动从环境变量/ .env 读取并类型校验。配置分层：默认值→配置文件→环境变量→命令行参数（后者覆盖前者）。敏感配置（密钥/数据库密码）只通过环境变量注入，不写入代码和配置文件。生产用 K8s Secret/ConfigMap 或 Vault 管理。
>
> **用法要点**：① python-dotenv 加载 .env（开发），.env 加入 .gitignore  ② Pydantic BaseSettings 自动读取环境变量+类型校验  ③ 12-Factor：配置存环境变量，代码不含环境差异  ④ 敏感信息用 K8s Secret/Vault，不写代码和 .env  ⑤ 面试常考：12-Factor 配置、dotenv、BaseSettings、密钥管理

# python-dotenv
from dotenv import load_dotenv
import os
load_dotenv()  # 加载 .env 文件
DATABASE_URL = os.getenv("DATABASE_URL")

# pydantic-settings（推荐，类型安全）
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    debug: bool = False
    api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**.env 文件示例**：
```env
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0
DEBUG=False
API_KEY=secret-key-here
```

**配置管理原则**：
- 代码与配置分离，不同环境用不同 .env
- 敏感信息（密钥/密码）不提交到 Git（.gitignore 排除 .env）
- 生产环境用系统环境变量或密钥管理服务（AWS Secrets Manager/Vault）
- 配置按环境分层：base → dev → test → prod

---


---
## 7. CI/CD

### 7.1 GitHub Actions 示例

> 🔍 **知识点深度解析**
>
> **作用**：CI/CD 自动化构建测试部署，保障质量与交付速度。
>
> **原理**：用 workflow YAML 定义触发条件与 job（lint/test/build/deploy）；矩阵测试多版本，部署步骤结合密钥与 SSH/Docker。
>
> **用法要点**：① YAML 定义流水线 ② 触发条件灵活 ③ 矩阵测多版本 ④ 测试门禁 ⑤ 部署结合密钥


```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest
      - name: Build & Push Docker
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker push registry.example.com/myapp:${{ github.sha }}
      - name: Deploy to Server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.HOST }}
          username: deploy
          key: ${{ secrets.SSH_KEY }}
          script: |
            docker pull registry.example.com/myapp:${{ github.sha }}
            docker-compose up -d
```

---


---
## 8. 监控与日志

### 8.1 日志

> 🔍 **知识点深度解析**
>
> **作用**：规范日志是线上问题排查与可观测性的基础。
>
> **原理**：用 logging 模块分级（DEBUG/INFO/WARNING/ERROR）、结构化输出（JSON）、附带上下文；避免打印敏感信息、控制级别。
>
> **用法要点**：① logging 分级 ② 结构化便于检索 ③ 附上下文 ④ 不记敏感信息 ⑤ 按环境调级别


```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("/var/log/myapp/app.log"),
        logging.StreamHandler()
    ]
)
```

### 8.2 监控工具

> 🔍 **知识点深度解析**
>
> **作用**：监控与指标帮助实时掌握系统健康并及时发现异常。
>
> **原理**：Prometheus 拉取指标、Grafana 展示、Sentry 收集错误；关注 QPS/延迟/错误率/资源使用率并设置告警。
>
> **用法要点**：① Prometheus 指标 ② Grafana 可视化 ③ Sentry 错误追踪 ④ 关注黄金指标 ⑤ 配置告警


- **Prometheus + Grafana**：指标监控
- **ELK / Loki**：日志聚合
- **Sentry**：错误追踪
- **Flower**：Celery 监控
- **healthcheck**：健康检查端点

---

## 8.3 日志收集架构

```
应用 → 结构化日志（JSON）→ Filebeat/Fluentd → Elasticsearch/Loki → Kibana/Grafana
```

**结构化日志（JSON 格式）**：
```python
import logging, json
class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        })
```

---


> 🔍 **知识点深度解析**
>
> **作用**：生产日志收集架构将分散的日志集中存储和分析，典型方案为 ELK/EFK 或 Loki 栈。
>
> **原理**：ELK：Elasticsearch（存储索引）+ Logstash/Fluentd（采集处理）+ Kibana（可视化）。EFK：Fluentd 替代 Logstash（K8s 常用）。Loki：Grafana Loki 轻量级，只索引标签不索引全文，成本低，配合 Promtail 采集。日志规范：JSON 结构化输出（level/time/service/trace_id/message），stdout 输出（容器标准），Sidecar/DaemonSet 采集。链路追踪：trace_id 贯穿日志便于关联。
>
> **用法要点**：① ELK：Elasticsearch+Logstash+Kibana，功能强大但资源消耗大  ② Loki+Promtail+Grafana：轻量低成本，只索引标签  ③ JSON 结构化日志到 stdout，容器标准做法  ④ trace_id 贯穿日志，关联同一请求的所有日志  ⑤ 面试常考：ELK vs Loki、结构化日志、日志采集、trace_id

## 8.4 健康检查

```python

> 🔍 **知识点深度解析**
>
> **作用**：健康检查让负载均衡器和编排系统判断服务是否正常，分存活探针和就绪探针。
>
> **原理**：存活检查（liveness）：服务是否运行，失败则重启容器（K8s livenessProbe）。就绪检查（readiness）：服务是否可接收流量，失败则从负载均衡摘除但不重启（K8s readinessProbe）。启动检查（startup）：慢启动应用保护。FastAPI /health 端点：检查数据库/Redis/外部依赖连通性。K8s 探针：httpGet/tcpSocket/exec，initialDelaySeconds/periodSeconds/failureThreshold 配置。
>
> **用法要点**：① liveness 失败重启，readiness 失败摘流量不重启  ② 健康检查端点检查依赖（DB/Redis）连通性，不只返回 200  ③ K8s 探针：httpGet/tcpSocket/exec，配置延迟和阈值  ④ 启动探针保护慢启动应用，避免被 liveness 误杀  ⑤ 面试常考：liveness vs readiness、健康检查端点、K8s 探针配置

# FastAPI 健康检查端点
@app.get("/health")
async def health_check():
    # 检查数据库连接
    try:
        await db.execute("SELECT 1")
        db_ok = True
    except Exception:
        db_ok = False
    # 检查 Redis
    try:
        await redis.ping()
        redis_ok = True
    except Exception:
        redis_ok = False
    status = "healthy" if (db_ok and redis_ok) else "unhealthy"
    return {"status": status, "database": db_ok, "redis": redis_ok}
```

**健康检查类型**：
- **Liveness（存活）**：进程是否在运行，失败则重启
- **Readiness（就绪）**：是否能接收流量，失败则从负载均衡摘除
- **Startup（启动）**：启动是否完成，避免慢启动应用被误杀

---


---
## 9. 部署策略

### 9.1 蓝绿部署

> 🔍 **知识点深度解析**
>
> **作用**：蓝绿部署用两套环境切换实现零停机发布与快速回滚。
>
> **原理**：同时运行蓝（旧）绿（新）两套，流量从蓝切到绿；出问题立刻切回蓝，风险低但需双倍资源。
>
> **用法要点**：① 双环境切换 ② 零停机发布 ③ 秒级回滚 ④ 需双倍资源 ⑤ 切换前充分验证


```
蓝环境（v1，当前生产）← 流量
绿环境（v2，新版本）← 无流量

部署步骤：
1. 在绿环境部署 v2
2. 测试绿环境
3. 切换流量到绿环境（DNS/Nginx/负载均衡）
4. 蓝环境保留作为回滚
5. 验证稳定后，蓝环境可更新为下次部署
```

优点：零停机、回滚快（切回蓝环境）
缺点：需要双倍资源

### 9.2 滚动更新

> 🔍 **知识点深度解析**
>
> **作用**：滚动更新逐步替换实例，在资源节约与可用间取得平衡。
>
> **原理**：按批次逐个用新版本替换旧实例，始终保持部分容量在线；需就绪探针防止流量打到未就绪实例。
>
> **用法要点**：① 分批替换实例 ② 始终保持可用 ③ 资源占用低 ④ 需健康检查 ⑤ 回滚较慢


```
实例1(v1) → 实例1(v2) → 实例2(v1) → 实例2(v2) → ...
逐个实例更新，期间 v1 和 v2 同时存在
```

优点：资源占用少
缺点：更新期间版本并存，需保证向后兼容；回滚慢

### 9.3 金丝雀发布（灰度发布）

> 🔍 **知识点深度解析**
>
> **作用**：金丝雀发布先把新版本放少量流量，验证无碍再全量。
>
> **原理**：按权重将小部分请求路由到新版本，观察指标；异常则回退，降低故障爆炸半径，适合高风险变更。
>
> **用法要点**：① 小流量验证 ② 降低故障半径 ③ 按指标决策 ④ 需精细路由 ⑤ 适合高风险变更


```
100% 流量
  ├── 95% → v1（旧版本）
  └── 5%  → v2（新版本，金丝雀）

逐步增加 v2 流量：5% → 20% → 50% → 100%
监控 v2 指标，异常则立即回滚
```

优点：风险可控，影响范围小
缺点：需要流量控制能力（Nginx/网关/K8s）

### 9.4 负载均衡算法

> 🔍 **知识点深度解析**
>
> **作用**：负载均衡算法决定请求如何分发，影响性能与可用性。
>
> **原理**：轮询、加权轮询、最少连接、IP 哈希（会话保持）、一致性哈希等；按后端异构与服务特点选择。
>
> **用法要点**：① 轮询/加权轮询 ② 最少连接 ③ IP 哈希保会话 ④ 一致性哈希减抖动 ⑤ 按后端特点选型


| 算法 | 原理 | 适用场景 |
|------|------|----------|
| **轮询（Round Robin）** | 依次分配 | 服务器性能相近 |
| **加权轮询** | 按权重分配 | 服务器性能不同 |
| **最少连接** | 分配给连接数最少的 | 长连接场景 |
| **IP Hash** | 按客户端 IP 哈希 | 会话保持（不推荐，用 Redis 存 session） |
| **随机** | 随机分配 | 简单场景 |

---


---
## 10. 面试高频考点

1. **WSGI 原理**：接口协议、Gunicorn pre-fork 模型
2. **Gunicorn 配置**：worker 数计算、worker 类型选择
3. **WSGI vs ASGI**：同步 vs 异步、适用场景
4. **Nginx 作用**：反向代理、负载均衡、静态资源
5. **Supervisor/systemd**：进程守护、自动重启
6. **Docker 部署**：Dockerfile 优化、多阶段构建
7. **CI/CD 流程**：自动化测试、构建、部署
8. **零停机部署**：蓝绿部署、滚动更新、金丝雀发布
9. **环境变量管理**：配置分离、密钥管理、pydantic-settings
10. **日志与监控**：结构化日志、Sentry、Prometheus、ELK/Loki
11. **健康检查**：Liveness/Readiness/Startup 区别
12. **负载均衡算法**：轮询/加权/最少连接/IP Hash
13. **服务发现**：Consul/Eureka/K8s Service
14. **配置中心**：Nacos/Apollo/Vault
15. **Docker 多阶段构建**：减小镜像体积

---


---
## 📝 精简总结

- 部署架构：Nginx → Gunicorn/Uvicorn → Python App → DB/Redis
- WSGI：Gunicorn（pre-fork多进程），worker数=CPU*2+1，IO密集用gevent
- ASGI：Uvicorn（异步协程），适合 FastAPI/长连接
- 进程管理：Supervisor 或 systemd，保证服务自动重启
- Nginx：反向代理 + 静态资源 + 负载均衡 + HTTPS
- Docker：容器化部署，Docker Compose 编排多服务，多阶段构建减小镜像
- 环境变量：python-dotenv/pydantic-settings，配置与代码分离，密钥不入库
- CI/CD：GitHub Actions 自动化测试构建部署
- 部署策略：蓝绿（零停机/双倍资源）、滚动（省资源/兼容）、金丝雀（灰度/风险可控）
- 健康检查：Liveness（存活重启）、Readiness（就绪摘流量）、Startup（启动保护）
- 负载均衡：轮询/加权轮询/最少连接/IP Hash
- 日志：结构化 JSON 日志，ELK/Loki 收集，Filebeat/Fluentd 采集
- 监控：Sentry 错误追踪 + Prometheus/Grafana 指标 + Flower(Celery)
- 服务发现：Consul/Eureka/K8s Service，配置中心：Nacos/Apollo/Vault

---

[[08-Python全栈/MOC-Python全栈|← 返回 Python 全栈 MOC]] | [[Home|🏠 返回首页]]
