---
title: Python 部署运维知识点系统梳理
tags: [Python全栈, Python, 部署, 运维, Gunicorn, Docker, Nginx, 面试]
created: 2026-08-13
updated: 2026-08-13
---

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

## 2. WSGI 服务器

### 2.1 Gunicorn

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

## 3. ASGI 服务器

### 3.1 Uvicorn

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

| 维度 | WSGI | ASGI |
|------|------|------|
| 异步 | 不支持 | 原生支持 |
| 并发 | 多进程/线程 | 协程 + 多进程 |
| 长连接 | 不支持 | WebSocket/SSE |
| 性能 | 中 | 高（IO密集） |
| 框架 | Django/Flask | FastAPI/Django3+ |

---

## 4. 进程管理

### 4.1 Supervisor

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

## 6. Docker 容器化

### 6.1 Dockerfile

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

## 7. CI/CD

### 7.1 GitHub Actions 示例

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

## 8. 监控与日志

### 8.1 日志

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

## 8.4 健康检查

```python
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

## 9. 部署策略

### 9.1 蓝绿部署

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

```
实例1(v1) → 实例1(v2) → 实例2(v1) → 实例2(v2) → ...
逐个实例更新，期间 v1 和 v2 同时存在
```

优点：资源占用少
缺点：更新期间版本并存，需保证向后兼容；回滚慢

### 9.3 金丝雀发布（灰度发布）

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

| 算法 | 原理 | 适用场景 |
|------|------|----------|
| **轮询（Round Robin）** | 依次分配 | 服务器性能相近 |
| **加权轮询** | 按权重分配 | 服务器性能不同 |
| **最少连接** | 分配给连接数最少的 | 长连接场景 |
| **IP Hash** | 按客户端 IP 哈希 | 会话保持（不推荐，用 Redis 存 session） |
| **随机** | 随机分配 | 简单场景 |

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
