---
title: Docker容器化实战
tags: [Docker, 实战, 部署, Dockerfile, DockerCompose, 云原生]
category: 云原生
created: 2026-08-29
updated: 2026-08-29
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[Docker容器化]]"]
aliases: [Docker容器化实战]
---

# 🐳 Docker 容器化实战

> 从实际项目出发，系统讲解 Docker 容器化的完整实战流程，包括应用容器化、多容器编排、生产环境部署、性能优化、安全加固等核心技能，是从 Docker 入门到生产实战的必经之路。

---

## 一、容器化实战概述

### 什么是容器化实战
容器化实战是指将传统应用（单体或微服务）打包为 Docker 镜像，并以容器方式运行和管理的完整实践过程。

### 容器化的价值
| 价值 | 说明 |
|------|------|
| **环境一致性** | 开发、测试、生产环境完全一致，消除"在我机器上能跑"问题 |
| **快速部署** | 镜像一次构建，到处运行，部署时间从小时级降到秒级 |
| **资源利用率** | 容器共享内核，轻量级，相比虚拟机提升 3-5 倍资源利用率 |
| **弹性扩缩** | 配合编排工具，实现秒级弹性扩缩容，应对流量波动 |
| **持续交付** | 镜像版本化，支持 CI/CD 流水线，实现持续集成和持续部署 |
| **应用隔离** | 容器间进程、文件系统、网络隔离，避免应用间冲突 |

### 容器化适用场景
| 场景 | 说明 |
|------|------|
| Web 应用 | 前端、后端 API、微服务 |
| 数据处理 | 批处理、ETL、数据分析 |
| 定时任务 | Cron Job、异步任务、消息消费 |
| 开发环境 | 统一开发环境、一键启动 |
| CI/CD | 构建环境、测试环境、部署流水线 |
| AI 应用 | 模型服务、推理服务、AI Agent |

---

## 二、应用容器化完整流程

### 1. 容器化前准备
**分析应用依赖**
```text
应用类型：Web API / 前端 /  Worker / 定时任务
运行时：Node.js / Python / Java / Go
依赖：系统依赖、语言依赖、外部服务
端口：应用监听端口
数据：需要持久化的数据目录
配置：环境变量、配置文件
```

**选择基础镜像**
| 应用类型 | 推荐基础镜像 | 说明 |
|---------|-------------|------|
| Node.js | `node:18-alpine` | 轻量级，适合大多数 Node 应用 |
| Python | `python:3.11-slim` | 精简版，适合 Python 应用 |
| Java | `eclipse-temurin:17-jre-alpine` | Alpine 版 JRE，适合 Java 应用 |
| Go | `golang:1.21-alpine`（构建）+ `alpine:3.18`（运行） | 多阶段构建，最终镜像极小 |
| Nginx | `nginx:alpine` | 轻量级 Web 服务器 |

### 2. 编写 Dockerfile
**Node.js 应用示例**
```dockerfile
# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM node:18-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
EXPOSE 3000
USER node
CMD ["node", "dist/main.js"]
```

**Python 应用示例**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN adduser --disabled-password --gecos "" appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Java (Spring Boot) 应用示例**
```dockerfile
# 构建阶段
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

# 运行阶段
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
ENV JAVA_OPTS="-Xms512m -Xmx1024m"
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
USER 1001
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

**Go 应用示例（多阶段构建，最终镜像 < 20MB）**
```dockerfile
# 构建阶段
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o app .

# 运行阶段（使用 scratch 空镜像）
FROM scratch
COPY --from=builder /app/app /app
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
EXPOSE 8080
ENTRYPOINT ["/app"]
```

### 3. 构建和测试镜像
```bash
# 构建镜像
docker build -t myapp:1.0 .

# 查看镜像
docker images | grep myapp

# 运行容器测试
docker run -d -p 3000:3000 --name myapp-test myapp:1.0

# 查看容器状态
docker ps | grep myapp-test

# 查看日志
docker logs myapp-test

# 进入容器调试
docker exec -it myapp-test /bin/sh

# 测试应用
curl http://localhost:3000/health

# 停止并删除测试容器
docker rm -f myapp-test
```

### 4. 镜像优化
**优化策略**
| 策略 | 说明 | 效果 |
|------|------|------|
| 多阶段构建 | 构建阶段和运行阶段分离，最终镜像不含构建工具 | 减少 50-90% 镜像大小 |
| 精简基础镜像 | 使用 alpine、slim、distroless、scratch | 减少 50-80% 镜像大小 |
| 合并 RUN 指令 | 减少镜像层数，清理包管理器缓存 | 减少 10-30% 镜像大小 |
| 利用层缓存 | 合理排序 Dockerfile 指令，依赖文件先复制 | 加快构建速度 50-80% |
| .dockerignore | 排除 node_modules、.git、dist 等 | 减小构建上下文，加快构建 |
| 非 root 用户 | 以非 root 用户运行容器 | 提升安全性 |

**镜像大小对比示例**
| 镜像 | 大小 | 说明 |
|------|------|------|
| `node:18` + 直接复制 | ~1.2GB | 未优化 |
| `node:18-alpine` + 单阶段 | ~350MB | 使用 alpine |
| `node:18-alpine` + 多阶段 | ~200MB | 多阶段构建 |
| `node:18-alpine` + 多阶段 + 清理 | ~150MB | 优化依赖 |

---

## 三、多容器编排（Docker Compose）

### 典型应用栈示例
**Web 应用 + 数据库 + 缓存 + 消息队列**
```yaml
version: '3.8'

services:
  # Web 应用
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
      - REDIS_URL=redis://redis:6379
      - RABBITMQ_URL=amqp://user:pass@rabbitmq:5672
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
      rabbitmq:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL 数据库
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=myapp
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis 缓存
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redisdata:/data
    ports:
      - "6379:6379"

  # RabbitMQ 消息队列
  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    environment:
      - RABBITMQ_DEFAULT_USER=user
      - RABBITMQ_DEFAULT_PASS=pass
    volumes:
      - rabbitmqdata:/var/lib/rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_port_connectivity"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  pgdata:
  redisdata:
  rabbitmqdata:

networks:
  default:
    name: myapp-network
```

### 常用操作
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
docker-compose logs -f web

# 重启服务
docker-compose restart web

# 停止服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 停止并删除容器和数据卷
docker-compose down -v

# 重新构建并启动
docker-compose up -d --build

# 进入服务容器
docker-compose exec web /bin/sh

# 查看服务资源使用
docker-compose stats
```

### 环境变量管理
**.env 文件**
```env
# 应用配置
NODE_ENV=production
PORT=3000

# 数据库配置
POSTGRES_USER=user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=myapp

# Redis 配置
REDIS_PASSWORD=redis_password

# 标签
VERSION=1.0.0
```

**docker-compose.yml 中引用**
```yaml
services:
  web:
    image: myapp:${VERSION:-latest}
    environment:
      - NODE_ENV=${NODE_ENV}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```

---

## 四、生产环境部署

### 1. 镜像仓库管理
**推送镜像到仓库**
```bash
# 登录镜像仓库
docker login registry.example.com

# 给镜像打标签
docker tag myapp:1.0 registry.example.com/myapp:1.0
docker tag myapp:1.0 registry.example.com/myapp:latest

# 推送镜像
docker push registry.example.com/myapp:1.0
docker push registry.example.com/myapp:latest

# 拉取镜像
docker pull registry.example.com/myapp:1.0
```

**私有仓库部署（Harbor）**
```yaml
# docker-compose.yml
version: '3.8'
services:
  harbor:
    image: goharbor/harbor:v2.9.0
    ports:
      - "80:80"
      - "443:443"
    environment:
      - HARBOR_ADMIN_PASSWORD=admin123
    volumes:
      - harbor-data:/data
volumes:
  harbor-data:
```

### 2. 容器运行配置
**生产环境运行参数**
```bash
docker run -d \
  --name myapp \
  --restart=always \
  --memory=512m \
  --cpus=1.0 \
  --pids-limit=100 \
  --read-only \
  --tmpfs /tmp \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --security-opt=no-new-privileges \
  --health-cmd="curl -f http://localhost:3000/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  --health-start-period=40s \
  -p 3000:3000 \
  -e NODE_ENV=production \
  -e DATABASE_URL=postgresql://... \
  -v /data/logs:/app/logs \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  registry.example.com/myapp:1.0
```

### 3. 日志管理
**日志驱动配置**
```bash
# JSON 文件日志（默认）
docker run --log-driver=json-file --log-opt max-size=10m --log-opt max-file=3 myapp

# Syslog 日志
docker run --log-driver=syslog --log-opt syslog-address=tcp://syslog.example.com:514 myapp

# Fluentd 日志
docker run --log-driver=fluentd --log-opt fluentd-address=fluentd.example.com:24224 myapp

# 禁止日志
docker run --log-driver=none myapp
```

**日志收集架构**
```text
应用容器 → Docker 日志驱动 → Fluentd/Logstash → Elasticsearch → Kibana
```

### 4. 监控和告警
**容器监控**
```bash
# 查看容器资源使用
docker stats

# 查看容器详情
docker inspect myapp

# 查看容器进程
docker top myapp

# 查看容器端口
docker port myapp
```

**Prometheus + Grafana 监控**
```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
```

---

## 五、容器化常见问题与排查

### 1. 容器启动失败
**排查步骤**
```bash
# 1. 查看容器状态
docker ps -a | grep myapp

# 2. 查看容器日志
docker logs myapp
docker logs --tail 100 myapp

# 3. 查看容器详情
docker inspect myapp

# 4. 以前台模式运行，查看错误
docker run --rm -it myapp:1.0 /bin/sh

# 5. 检查端口占用
netstat -tlnp | grep 3000

# 6. 检查资源限制
docker stats myapp
```

**常见原因**
| 原因 | 解决方案 |
|------|---------|
| 端口被占用 | 更换端口或停止占用进程 |
| 配置文件缺失 | 检查配置文件挂载和路径 |
| 依赖服务未启动 | 检查 depends_on 和健康检查 |
| 权限不足 | 检查文件权限和用户设置 |
| 内存不足 | 增加内存限制或优化应用 |
| 镜像构建错误 | 重新构建镜像，检查 Dockerfile |

### 2. 应用无法访问
**排查步骤**
```bash
# 1. 检查容器是否运行
docker ps | grep myapp

# 2. 检查端口映射
docker port myapp

# 3. 检查容器内应用是否监听
docker exec myapp netstat -tlnp

# 4. 从容器内部测试
docker exec myapp curl http://localhost:3000/health

# 5. 从宿主机测试
curl http://localhost:3000/health

# 6. 检查防火墙
iptables -L -n | grep 3000
```

**常见原因**
| 原因 | 解决方案 |
|------|---------|
| 应用监听 127.0.0.1 | 修改为监听 0.0.0.0 |
| 端口未映射 | 检查 -p 参数 |
| 防火墙拦截 | 开放端口或配置防火墙规则 |
| 应用崩溃 | 查看日志，修复应用错误 |
| 健康检查失败 | 检查健康检查配置和端点 |

### 3. 数据丢失
**排查步骤**
```bash
# 1. 检查数据卷挂载
docker inspect myapp | grep -A 10 Mounts

# 2. 查看数据卷
docker volume ls
docker volume inspect myvolume

# 3. 进入容器检查数据
docker exec myapp ls -la /data

# 4. 检查宿主机挂载目录
ls -la /host/data
```

**常见原因**
| 原因 | 解决方案 |
|------|---------|
| 未挂载数据卷 | 使用 -v 或 volumes 挂载 |
| 挂载路径错误 | 检查容器内路径和宿主机路径 |
| 容器被删除 | 数据卷不会随容器删除，检查数据卷 |
| 权限问题 | 检查文件权限和用户设置 |
| 误操作删除 | 定期备份数据卷 |

### 4. 性能问题
**排查步骤**
```bash
# 1. 查看容器资源使用
docker stats

# 2. 查看容器内进程
docker top myapp

# 3. 查看容器详细资源
docker inspect myapp | grep -A 10 Memory
docker inspect myapp | grep -A 10 Cpu

# 4. 查看系统资源
free -h
df -h
top

# 5. 查看镜像大小
docker images | grep myapp
```

**常见原因**
| 原因 | 解决方案 |
|------|---------|
| 内存不足 | 增加内存限制或优化应用内存使用 |
| CPU 限制 | 增加 CPU 限制或优化应用性能 |
| 镜像过大 | 优化 Dockerfile，使用多阶段构建 |
| 日志过大 | 配置日志轮转和大小限制 |
| 磁盘 IO 瓶颈 | 使用高性能存储或优化数据库 |
| 网络延迟 | 检查网络配置，使用主机网络或优化网络 |

---

## 六、容器化最佳实践

### 1. Dockerfile 最佳实践
- ✅ 使用多阶段构建，减小最终镜像大小
- ✅ 使用精简基础镜像（alpine、slim、distroless）
- ✅ 合理排序指令，利用构建缓存（依赖文件先复制）
- ✅ 合并 RUN 指令，减少镜像层数
- ✅ 清理包管理器缓存和临时文件
- ✅ 使用 .dockerignore 排除不必要的文件
- ✅ 以非 root 用户运行容器
- ✅ 添加 HEALTHCHECK 健康检查
- ✅ 使用 EXPOSE 声明端口
- ✅ 使用 ENV 设置环境变量
- ✅ 使用 LABEL 添加元数据
- ❌ 不要在镜像中存储敏感信息（密码、密钥）
- ❌ 不要使用 latest 标签（生产环境使用具体版本）
- ❌ 不要在容器中运行多个进程（使用 supervisord 或拆分容器）
- ❌ 不要在容器中存储重要数据（使用数据卷）

### 2. 容器运行最佳实践
- ✅ 设置重启策略（`--restart=unless-stopped`）
- ✅ 设置资源限制（`--memory`、`--cpus`）
- ✅ 配置健康检查
- ✅ 配置日志驱动和轮转
- ✅ 使用只读文件系统（`--read-only`）
- ✅ 限制 capabilities（`--cap-drop=ALL`）
- ✅ 使用安全选项（`--security-opt=no-new-privileges`）
- ✅ 定期更新基础镜像和应用
- ✅ 监控容器资源和健康状态
- ✅ 备份重要数据卷

### 3. 安全最佳实践
- ✅ 使用官方或可信基础镜像
- ✅ 定期扫描镜像漏洞（Trivy、Clair）
- ✅ 以非 root 用户运行
- ✅ 限制 capabilities 和系统调用
- ✅ 使用只读文件系统
- ✅ 敏感信息通过环境变量或密钥管理服务注入
- ✅ 启用 Docker Content Trust（镜像签名验证）
- ✅ 定期更新 Docker 引擎和基础镜像
- ✅ 限制容器资源，防止拒绝服务攻击

### 4. CI/CD 最佳实践
- ✅ 代码提交触发自动构建
- ✅ 构建时运行单元测试和代码检查
- ✅ 扫描镜像漏洞
- ✅ 镜像标签使用 Git Commit SHA 或版本号
- ✅ 推送到镜像仓库
- ✅ 自动部署到测试环境
- ✅ 手动审批后部署到生产环境
- ✅ 支持快速回滚
- ✅ 保留构建日志和部署记录

---

## 七、容器化进阶主题

### 1. 多架构镜像构建
```bash
# 使用 buildx 构建多架构镜像
docker buildx create --name mybuilder --use
docker buildx inspect --bootstrap

# 构建支持 amd64 和 arm64 的镜像
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t registry.example.com/myapp:1.0 \
  --push .

# 查看镜像支持的架构
docker buildx imagetools inspect registry.example.com/myapp:1.0
```

### 2. 容器网络进阶
**网络模式**
| 模式 | 说明 | 适用场景 |
|------|------|---------|
| bridge | 默认网络，容器间通过网桥通信 | 单主机容器通信 |
| host | 共享宿主机网络 | 高性能网络需求 |
| none | 无网络 | 安全隔离 |
| overlay | 多主机容器通信 | Swarm 集群、跨主机 |
| macvlan | 容器有独立 MAC 地址 |  legacy 应用、需要独立网络身份 |

**自定义网络**
```bash
# 创建自定义网络
docker network create --driver bridge --subnet 172.20.0.0/16 mynetwork

# 运行容器并连接网络
docker run -d --network mynetwork --name myapp myapp:1.0

# 连接容器到网络
docker network connect mynetwork myapp

# 查看网络详情
docker network inspect mynetwork
```

### 3. 容器存储进阶
**存储驱动**
| 驱动 | 说明 | 适用场景 |
|------|------|---------|
| overlay2 | 默认存储驱动，性能好 | 大多数场景 |
| aufs | 早期存储驱动 | 旧系统兼容 |
| devicemapper | 块设备存储 | 高性能需求 |
| btrfs | Btrfs 文件系统 | 支持 CoW 的文件系统 |
| zfs | ZFS 文件系统 | 支持快照和克隆 |

**数据卷插件**
```bash
# 使用本地数据卷
docker volume create --driver local myvolume

# 使用 NFS 数据卷
docker volume create --driver local \
  --opt type=nfs \
  --opt o=addr=nfs.example.com,rw \
  --opt device=:/path/to/share \
  mynfsvolume

# 使用云存储数据卷（如 AWS EBS）
docker volume create --driver cloudstor:aws \
  --opt size=10 \
  myebsvolume
```

### 4. Docker 安全扫描
```bash
# 使用 Trivy 扫描镜像漏洞
trivy image myapp:1.0

# 扫描并生成报告
trivy image --format json --output report.json myapp:1.0

# 仅扫描高危漏洞
trivy image --severity HIGH,CRITICAL myapp:1.0

# 扫描 Dockerfile
trivy config Dockerfile

# 集成到 CI/CD
trivy image --exit-code 1 --severity CRITICAL myapp:1.0
```

---

## 🔗 关联笔记

**Docker 基础**
- [[Docker容器化]] — Docker 容器化完整指南
- [[Docker 知识点系统梳理_优化版]] — Docker 核心概念、常用命令、面试考点
- [[Docker命令速查表]] — Docker 高频命令速查
- [[Dockerfile最佳实践]] — Dockerfile 编写最佳实践

**Docker 进阶**
- [[Docker-核心原理与镜像优化]] — Docker 核心原理、Namespace/Cgroups、镜像优化
- [[Docker-Compose编排]] — Docker Compose 多容器编排
- [[多架构镜像构建-buildx]] — 多架构镜像构建、buildx、ARM64/AMD64
- [[容器安全与镜像扫描]] — 容器安全、镜像扫描、漏洞管理

**相关技术**
- [[Kubernetes 知识点系统梳理_优化版]] — Kubernetes 容器编排
- [[CI-CD持续集成与部署]] — CI/CD 流水线
- [[Prometheus监控体系]] — Prometheus 监控体系
- [[DevOps与云原生知识点完整整合大全_优化版]] — DevOps 与云原生完整知识体系

---

## 📖 学习路径建议

1. **入门**：掌握 Docker 基本概念和常用命令，能够构建和运行简单容器
2. **进阶**：学习 Dockerfile 编写和优化，掌握 Docker Compose 多容器编排
3. **高级**：深入 Docker 核心原理（Namespace/Cgroups/UnionFS），学习生产环境部署和运维
4. **专家**：研究容器安全、性能优化、多架构构建，设计企业级容器平台，结合 Kubernetes 进行编排

---

## 💡 精简总结

Docker 容器化实战是将应用打包为容器并在生产环境运行的完整实践过程。核心流程包括：容器化前准备（分析依赖、选择基础镜像）、编写 Dockerfile（多阶段构建、优化镜像大小）、构建和测试镜像、多容器编排（Docker Compose）、生产环境部署（镜像仓库、运行配置、日志管理、监控告警）。关键最佳实践包括：使用多阶段构建减小镜像大小、以非 root 用户运行、配置健康检查和资源限制、定期扫描镜像漏洞、使用数据卷持久化重要数据。常见问题包括容器启动失败、应用无法访问、数据丢失、性能问题，需要通过日志、inspect、exec 等工具逐步排查。容器化是云原生应用的基础，掌握容器化实战是从开发到运维的必备技能。

---

> **容器化的本质不是把应用装进盒子，而是让应用在任何环境中都能一致、可靠、高效地运行。**

[[Home|🏠 返回首页]] · [[MOC-云原生与运维|☁️ 云原生与运维]] · [[学习路线总览|🗺️ 学习路线]]
