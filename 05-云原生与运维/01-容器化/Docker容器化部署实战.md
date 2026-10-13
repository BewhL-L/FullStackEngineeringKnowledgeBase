---
title: Docker容器化部署实战
tags: [Docker, 容器化, 部署, Dockerfile, DockerCompose, 生产环境]
category: 云原生与运维
created: 2026-09-07
updated: 2026-09-07
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 重要
pre: ["[[Docker-核心原理与镜像优化]]", "[[Docker-Compose编排]]"]
aliases: [Docker部署, 容器化部署, Docker生产部署]
---

# Docker容器化部署实战

> Docker容器化部署是现代应用交付的标准方式。本文从Dockerfile编写、多阶段构建、镜像优化、Compose编排到生产环境部署，提供完整的实战指南。
>
> **核心目标**：镜像体积小、构建速度快、运行安全、部署可复现。

---

## 一、概述：Docker部署体系

### 1.1 容器化部署优势

| 维度 | 传统部署 | Docker容器化 |
|------|---------|-------------|
| 环境一致性 | 开发/测试/生产环境不一致 | 镜像即环境，处处一致 |
| 部署速度 | 手动配置，耗时小时级 | 秒级启动，自动化部署 |
| 资源利用率 | 虚拟机开销大（GB级） | 容器轻量（MB级），密度高 |
| 弹性伸缩 | 手动扩缩，响应慢 | 配合编排平台自动伸缩 |
| 版本管理 | 无版本，回滚困难 | 镜像版本化，一键回滚 |
| 隔离性 | 进程混部，互相影响 | 命名空间+cgroups隔离 |

### 1.2 部署架构

```text
代码提交 → CI/CD流水线
    ↓
1. 构建Docker镜像（Dockerfile + 多阶段构建）
    ↓
2. 推送镜像仓库（Harbor/Docker Hub/云仓库）
    ↓
3. 部署到目标环境
    ├── 开发/测试：docker-compose up
    ├── 预发/生产：Kubernetes / Docker Swarm
    └── 单机：docker run / docker-compose
    ↓
4. 健康检查 + 日志采集 + 监控告警
```

---

## 二、底层原理：镜像分层与构建缓存

### 2.1 镜像分层原理

```text
Docker镜像 = 只读层（Layer）的堆叠

示例（从下到上）：
┌─────────────────────────┐
│  Layer 6: CMD启动命令    │  ← 最上层，可写（容器层）
├─────────────────────────┤
│  Layer 5: 应用代码       │  ← COPY . /app
├─────────────────────────┤
│  Layer 4: 依赖安装       │  ← npm install / pip install
├─────────────────────────┤
│  Layer 3: 工作目录设置   │  ← WORKDIR /app
├─────────────────────────┤
│  Layer 2: 环境变量       │  ← ENV NODE_ENV=production
├─────────────────────────┤
│  Layer 1: 基础镜像       │  ← FROM node:20-alpine
└─────────────────────────┘

关键：每一层只记录与上一层的差异，层可缓存、可复用
```

### 2.2 构建缓存机制

Docker按指令顺序构建，每条指令生成一层。如果指令和上下文未变，直接使用缓存。

**缓存失效顺序**：某一层缓存失效 → 后续所有层缓存全部失效。

**优化原则**：将变化频率低的指令放在前面（基础镜像、依赖安装），变化频率高的放在后面（代码拷贝）。

---

## 三、实操：生产级Dockerfile

### 3.1 Node.js多阶段构建

```dockerfile
# ===== 构建阶段 =====
FROM node:20-alpine AS builder
WORKDIR /app

# 先拷贝依赖文件（利用缓存）
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# 再拷贝源码（变化频繁，放在依赖之后）
COPY . .
RUN npm run build

# ===== 运行阶段 =====
FROM node:20-alpine AS runner
WORKDIR /app

# 安全：创建非root用户
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

# 从构建阶段拷贝必要文件
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

# 环境变量
ENV NODE_ENV=production
ENV PORT=3000

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# 切换非root用户
USER nextjs

# 启动命令（exec形式，确保信号传递）
CMD ["node", "server.js"]
```

### 3.2 Python多阶段构建

```dockerfile
# ===== 构建阶段 =====
FROM python:3.12-slim AS builder
WORKDIR /app

# 安装编译依赖（仅构建阶段需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===== 运行阶段 =====
FROM python:3.12-slim AS runner
WORKDIR /app

# 只拷贝虚拟环境（不含编译工具）
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 运行时依赖（如需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN useradd -m -u 1001 appuser
COPY --chown=appuser:appuser . .
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### 3.3 Java多阶段构建

```dockerfile
# ===== 构建阶段 =====
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app

# 先拷贝pom（缓存依赖）
COPY pom.xml .
RUN mvn dependency:go-offline -B

# 再拷贝源码
COPY src ./src
RUN mvn clean package -DskipTests -B

# ===== 运行阶段（JRE精简） =====
FROM eclipse-temurin:17-jre-alpine AS runner
WORKDIR /app

# 只拷贝jar包
COPY --from=builder /app/target/*.jar app.jar

# JVM参数优化
ENV JAVA_OPTS="-XX:+UseG1GC -XX:MaxRAMPercentage=75.0 -XX:+HeapDumpOnOutOfMemoryError"

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -qO- http://localhost:8080/actuator/health || exit 1

USER 1001
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

### 3.4 .dockerignore

```css
# 版本控制
.git
.gitignore

# 依赖目录
node_modules
vendor
__pycache__
*.pyc
.venv

# 构建产物
dist
build
target
*.log

# IDE
.idea
.vscode
*.swp

# 环境文件
.env
.env.local
.env.*.local

# 文档
README.md
docs

# 测试
tests
coverage
*.test.js
```

### 3.5 docker-compose生产配置

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    image: myapp:${VERSION:-latest}
    build:
      context: .
      dockerfile: Dockerfile
    container_name: myapp
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env.production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - app-network

  nginx:
    image: nginx:1.25-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - app
    networks:
      - app-network

volumes:
  pg_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

---

## 四、常见问题与排查

### 4.1 镜像体积优化

| 优化手段 | 效果 | 示例 |
|---------|------|------|
| 使用alpine基础镜像 | 减少50%+ | node:20-alpine vs node:20 |
| 多阶段构建 | 减少编译依赖 | builder阶段编译，runner阶段只拷贝产物 |
| 合并RUN指令 | 减少层数 | RUN apt update && apt install -y ... && rm -rf /var/lib/apt/lists/* |
| .dockerignore | 排除无关文件 | 排除node_modules、.git等 |
| 清理包管理器缓存 | 减少缓存层 | npm cache clean、pip install --no-cache-dir |
| 使用distroless镜像 | 最小运行时 | gcr.io/distroless/nodejs |

### 4.2 容器启动失败排查

```bash
# 1. 查看容器日志
docker logs <container_id> --tail 100

# 2. 查看容器状态和退出码
docker ps -a | grep <container_name>
docker inspect <container_id> --format='{{.State.ExitCode}} {{.State.Error}}'

# 3. 进入容器调试（如果容器能启动）
docker exec -it <container_id> /bin/sh

# 4. 覆盖入口命令调试
docker run --rm -it --entrypoint /bin/sh myapp:latest

# 5. 检查端口占用
docker port <container_id>
netstat -tlnp | grep <port>

# 6. 检查资源限制
docker stats <container_id>
```

### 4.3 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `exec format error` | 架构不匹配（arm64镜像跑在amd64） | 构建时指定--platform=linux/amd64 |
| `no space left on device` | 磁盘满 | docker system prune -a清理 |
| `connection refused` | 应用未监听0.0.0.0 | 应用绑定0.0.0.0而非127.0.0.1 |
| `OOMKilled` | 内存超限 | 增加memory limit或优化应用内存 |
| `permission denied` | 文件权限问题 | COPY --chown或RUN chmod |

---

## 五、进阶与最佳实践

### 5.1 镜像安全扫描

```bash
# 使用Trivy扫描镜像漏洞
trivy image myapp:latest

# CI中集成
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest
```

### 5.2 生产环境检查清单

- [ ] 使用固定标签，不使用latest
- [ ] 多阶段构建，镜像体积最小化
- [ ] 非root用户运行
- [ ] 只读文件系统（read_only: true）
- [ ] 健康检查配置
- [ ] 资源限制（CPU/内存）
- [ ] 日志轮转配置
- [ ] 重启策略（unless-stopped）
- [ ] 敏感信息通过环境变量/Secret注入，不硬编码
- [ ] 镜像漏洞扫描
- [ ] .dockerignore配置
- [ ] 基础镜像定期更新

### 5.3 CI/CD集成

```yaml
# GitHub Actions示例
- name: Build and Push
  run: |
    docker build -t myapp:${{ github.sha }} .
    docker tag myapp:${{ github.sha }} myapp:latest
    docker push myapp:${{ github.sha }}
    docker push myapp:latest

- name: Deploy
  run: |
    ssh user@server "docker pull myapp:${{ github.sha }} && docker-compose up -d"
```

---

## 关联笔记

- [[Docker-核心原理与镜像优化]] — Docker核心原理
- [[Docker-Compose编排]] — Compose编排
- [[Dockerfile最佳实践]] — Dockerfile最佳实践
- [[Kubernetes入门与实践]] — K8s编排
- [[CI-CD流水线设计]] — CI/CD流水线
