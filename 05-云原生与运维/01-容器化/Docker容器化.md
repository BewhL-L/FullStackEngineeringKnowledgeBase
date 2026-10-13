---
title: Docker容器化
tags: [Docker, 镜像, Dockerfile, DockerCompose, 云原生, 部署]
category: 云原生
created: 2026-08-29
updated: 2026-08-29
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[Linux 常用命令知识点系统梳理_优化版]]"]
aliases: [Docker容器化]
---

# 🐳 Docker 容器化

> Docker 是一个开源的容器化平台，通过将应用及其依赖打包到轻量级、可移植的容器中，实现"一次构建，到处运行"，是现代云原生应用部署的基石。

---

## 一、Docker 是什么

### 核心概念
Docker 是一个基于容器技术的应用打包和部署平台，核心思想是：
1. **镜像（Image）**：应用及其依赖的只读模板，是容器的基础
2. **容器（Container）**：镜像的运行实例，是隔离的进程空间
3. **仓库（Registry）**：存储和分发镜像的服务，如 Docker Hub

### 解决的问题
| 问题 | Docker 解决方案 |
|------|----------------|
| 环境不一致 | 容器包含完整运行环境，消除"在我机器上能跑"问题 |
| 部署复杂 | 镜像一次构建，到处运行，简化部署流程 |
| 资源利用率低 | 容器共享内核，轻量级，比虚拟机启动更快、资源占用更少 |
| 应用隔离 | 容器间进程、文件系统、网络隔离，避免应用间冲突 |
| 扩缩容困难 | 容器快速启动，配合编排工具实现弹性扩缩容 |
| 持续交付 | 镜像版本化，支持 CI/CD 流水线，实现持续集成和部署 |

```text
### Docker vs 虚拟机
```
| 维度 | Docker 容器 | 虚拟机（VM） |
|------|------------|-------------|
| 虚拟化级别 | 操作系统级虚拟化 | 硬件级虚拟化 |
| 内核 | 共享宿主机内核 | 独立客户机内核 |
| 启动速度 | 秒级（1-5秒） | 分钟级（30秒-几分钟） |
| 资源占用 | 轻量（MB级） | 重量（GB级） |
| 性能 | 接近原生 | 有虚拟化开销 |
| 隔离性 | 进程级隔离 | 完全隔离 |
| 适用场景 | 应用部署、微服务 | 完整操作系统、多租户 |

---

## 二、Docker 核心原理

### 容器化技术基础
Docker 容器本质上是 Linux 内核特性的组合：

```bash
Docker 容器
├── Namespace（命名空间）—— 进程、网络、挂载、UTS、IPC、PID 隔离
├── Cgroups（控制组）—— CPU、内存、磁盘 IO、网络带宽限制
├── UnionFS（联合文件系统）—— 镜像分层、可写层、Copy-on-Write
├── chroot（根文件系统切换）—— 文件系统隔离
└── Capabilities（能力）—— 细粒度权限控制
```

### 1. Namespace（命名空间）
Namespace 是 Linux 内核提供的进程隔离机制，Docker 使用以下 6 种 Namespace：

| Namespace | 隔离内容 | 说明 |
|-----------|---------|------|
| PID | 进程 ID | 容器内进程 ID 独立，PID 1 为容器主进程 |
| NET | 网络栈 | 容器有独立的网络设备、IP 地址、端口、路由表 |
| MNT | 挂载点 | 容器有独立的文件系统挂载视图 |
| UTS | 主机名和域名 | 容器可以有独立的主机名和域名 |
| IPC | 进程间通信 | 容器内 System V IPC 和 POSIX 消息队列独立 |
| USER | 用户和用户组 | 容器内用户 ID 和组 ID 独立，支持用户命名空间 |

### 2. Cgroups（控制组）
Cgroups 是 Linux 内核提供的资源限制和隔离机制：

| 子系统 | 功能 | 说明 |
|--------|------|------|
| cpu | CPU 限制 | 限制 CPU 使用比例、核数、优先级 |
| cpuacct | CPU 统计 | 统计 CPU 使用时间 |
| memory | 内存限制 | 限制内存使用量、Swap、OOM 行为 |
| blkio | 块设备 IO | 限制磁盘读写带宽、IOPS |
| devices | 设备访问 | 控制容器可以访问的设备 |
| net_cls | 网络分类 | 标记网络数据包，配合 tc 限制带宽 |
| pids | 进程数限制 | 限制容器内进程数量 |

### 3. UnionFS（联合文件系统）
UnionFS 是一种分层文件系统，支持将多个目录联合挂载：

```text
容器文件系统（可写层）
├── 容器层（可写，Copy-on-Write）
├── 镜像层 3（只读，如：应用代码）
├── 镜像层 2（只读，如：依赖库）
├── 镜像层 1（只读，如：基础操作系统）
└── bootfs（只读，引导文件系统）
```

**关键特性**：
- **分层存储**：镜像由多个只读层组成，层间共享，节省空间
- **Copy-on-Write（写时复制）**：容器修改文件时，将文件从只读层复制到可写层
- **增量更新**：更新镜像只需更新变化的层，加快构建和分发
- **层缓存**：构建时缓存未变化的层，加快构建速度

### 4. 容器运行时
Docker 容器运行时架构：

```bash
Docker CLI → Docker Daemon → containerd → runc → 容器进程
                ↓
            containerd-shim
                ↓
            runc（OCI 运行时）
                ↓
            Linux 内核（Namespace/Cgroups）
```

- **runc**：OCI 标准的容器运行时，负责创建和运行容器
- **containerd**：容器守护进程，管理容器生命周期、镜像、存储、网络
- **Docker Daemon**：Docker 守护进程，提供 API，管理镜像、容器、网络、卷

---

## 三、Docker 核心概念

### 1. 镜像（Image）
镜像是容器的只读模板，包含应用运行所需的一切：代码、运行时、库、环境变量、配置文件。

**镜像特点**：
- 只读：镜像一旦构建，不可修改
- 分层：由多个只读层组成，层间共享
- 版本化：通过标签（Tag）管理版本
- 可分发：通过仓库（Registry）分发和共享

**常用镜像操作**：
```bash
# 拉取镜像
docker pull nginx:latest

# 查看本地镜像
docker images

# 构建镜像
docker build -t myapp:1.0 .

# 给镜像打标签
docker tag myapp:1.0 myapp:latest

# 推送镜像到仓库
docker push myregistry/myapp:1.0

# 删除镜像
docker rmi myapp:1.0

# 查看镜像历史
docker history myapp:1.0

#  inspect 镜像详情
docker inspect myapp:1.0
```

### 2. 容器（Container）
容器是镜像的运行实例，是隔离的进程空间。

**容器特点**：
- 可写：容器有可写层，可以修改文件
- 隔离：进程、网络、文件系统隔离
- 轻量：共享内核，启动快，资源占用少
- 短暂：容器可以随时创建和销毁，数据应存在卷中

**常用容器操作**：
```bash
# 运行容器
docker run -d -p 8080:80 --name mynginx nginx:latest

# 查看运行中的容器
docker ps

# 查看所有容器（包括已停止）
docker ps -a

# 启动/停止/重启容器
docker start mynginx
docker stop mynginx
docker restart mynginx

# 进入容器
docker exec -it mynginx /bin/bash

# 查看容器日志
docker logs mynginx
docker logs -f mynginx  # 实时跟踪

# 查看容器资源使用
docker stats mynginx

# 查看容器详情
docker inspect mynginx

# 查看容器内进程
docker top mynginx

# 复制文件到/从容器
docker cp file.txt mynginx:/path/
docker cp mynginx:/path/file.txt ./

# 删除容器
docker rm mynginx
docker rm -f mynginx  # 强制删除运行中的容器

# 清理停止的容器
docker container prune
```

### 3. 仓库（Registry）
仓库是存储和分发镜像的服务。

**常见仓库**：
- **Docker Hub**：官方公共仓库，包含大量官方和社区镜像
- **Harbor**：开源企业级私有仓库，支持权限管理、安全扫描
- **阿里云 ACR**：阿里云容器镜像服务
- **腾讯云 TCR**：腾讯云容器镜像服务
- **GitHub GHCR**：GitHub Container Registry

**仓库操作**：
```bash
# 登录仓库
docker login myregistry.com

# 拉取镜像
docker pull myregistry.com/myapp:1.0

# 推送镜像
docker push myregistry.com/myapp:1.0

# 登出仓库
docker logout myregistry.com
```

### 4. 数据卷（Volume）
数据卷是 Docker 提供的持久化存储机制，用于保存容器产生的数据。

**数据卷类型**：
| 类型 | 说明 | 适用场景 |
|------|------|---------|
| 命名卷（Named Volume） | Docker 管理的卷，有名称 | 数据库数据、应用数据 |
| 绑定挂载（Bind Mount） | 挂载宿主机目录到容器 | 开发环境、配置文件 |
| tmpfs 挂载 | 挂载到内存，临时存储 | 敏感数据、临时文件 |

**数据卷操作**：
```bash
# 创建数据卷
docker volume create myvolume

# 查看数据卷
docker volume ls

# 查看数据卷详情
docker volume inspect myvolume

# 使用数据卷运行容器
docker run -d -v myvolume:/data --name myapp myapp:1.0

# 绑定挂载
docker run -d -v /host/path:/container/path --name myapp myapp:1.0

# 删除数据卷
docker volume rm myvolume

# 清理未使用的数据卷
docker volume prune
```

### 5. 网络（Network）
Docker 提供网络隔离和通信机制。

**网络驱动**：
| 驱动 | 说明 | 适用场景 |
|------|------|---------|
| bridge | 默认网络，容器间通过网桥通信 | 单主机容器通信 |
| host | 共享宿主机网络 | 高性能网络需求 |
| none | 无网络 | 安全隔离 |
| overlay | 多主机容器通信 | Swarm 集群、跨主机 |
| macvlan | 容器有独立 MAC 地址 |  legacy 应用、需要独立网络身份 |

**网络操作**：
```bash
# 查看网络
docker network ls

# 创建网络
docker network create mynetwork

# 查看网络详情
docker network inspect mynetwork

# 运行容器并连接网络
docker run -d --network mynetwork --name myapp myapp:1.0

# 连接容器到网络
docker network connect mynetwork myapp

# 断开容器网络
docker network disconnect mynetwork myapp

# 删除网络
docker network rm mynetwork

# 清理未使用网络
docker network prune
```

---

## 四、Dockerfile 最佳实践

### Dockerfile 基本结构
```dockerfile
# 基础镜像
FROM node:18-alpine

# 维护者信息
LABEL maintainer="dev@example.com"
LABEL version="1.0"
LABEL description="My App"

# 设置工作目录
WORKDIR /app

# 复制依赖文件（利用层缓存）
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制应用代码
COPY . .

# 构建应用
RUN npm run build

# 设置环境变量
ENV NODE_ENV=production
ENV PORT=3000

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# 创建非 root 用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# 启动命令
CMD ["node", "dist/main.js"]
```

### 最佳实践

**1. 选择合适的基础镜像**
```dockerfile
# 推荐：使用精简的 alpine 镜像
FROM node:18-alpine

# 推荐：使用特定版本，避免 latest
FROM python:3.11-slim

# 不推荐：使用 latest 标签
FROM node:latest

# 不推荐：使用完整操作系统镜像
FROM ubuntu:22.04
```

**2. 利用层缓存**
```dockerfile
# 正确：先复制依赖文件，再安装依赖，最后复制代码
COPY package*.json ./
RUN npm ci
COPY . .

# 错误：先复制所有代码，再安装依赖（每次代码变化都会重新安装依赖）
COPY . .
RUN npm ci
```

**3. 减少镜像层数**
```dockerfile
# 推荐：合并 RUN 指令，减少层数
RUN apt-get update && \
    apt-get install -y curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 不推荐：多个 RUN 指令，增加层数
RUN apt-get update
RUN apt-get install -y curl git
RUN apt-get clean
```

**4. 使用多阶段构建**
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
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
USER node
CMD ["node", "dist/main.js"]
```

**5. 以非 root 用户运行**
```dockerfile
# 创建非 root 用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 切换到非 root 用户
USER appuser
```

**6. 添加健康检查**
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1
```

**7. 清理缓存和临时文件**
```dockerfile
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN npm ci && npm cache clean --force
```

**8. 使用 .dockerignore**
```css
# .dockerignore
node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.env.local
dist
build
*.md
.DS_Store
```

### 常用指令详解
| 指令 | 说明 | 示例 |
|------|------|------|
| FROM | 指定基础镜像 | `FROM node:18-alpine` |
| LABEL | 添加元数据 | `LABEL version="1.0"` |
| RUN | 执行命令（构建时） | `RUN npm install` |
| CMD | 容器启动命令（可被覆盖） | `CMD ["node", "app.js"]` |
| ENTRYPOINT | 容器启动入口（不可被覆盖） | `ENTRYPOINT ["node"]` |
| COPY | 复制文件到镜像 | `COPY . .` |
| ADD | 复制文件（支持 URL 和自动解压） | `ADD app.tar.gz /app` |
| WORKDIR | 设置工作目录 | `WORKDIR /app` |
| ENV | 设置环境变量 | `ENV NODE_ENV=production` |
| ARG | 构建参数 | `ARG VERSION=1.0` |
| EXPOSE | 声明端口 | `EXPOSE 3000` |
| VOLUME | 声明数据卷 | `VOLUME ["/data"]` |
| USER | 设置运行用户 | `USER appuser` |
| HEALTHCHECK | 健康检查 | `HEALTHCHECK CMD curl ...` |
| SHELL | 设置默认 shell | `SHELL ["/bin/sh", "-c"]` |

---

## 五、Docker Compose

### 什么是 Docker Compose
```text
Docker Compose 是用于定义和运行多容器 Docker 应用的工具，通过 YAML 文件配置应用服务，一条命令即可启动所有服务。

### docker-compose.yml 示例
```
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://user:pass@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

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

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    command: redis-server --appendonly yes

volumes:
  pgdata:
  redisdata:

networks:
  default:
    name: myapp-network
```

### 常用命令
```bash
# 启动所有服务
docker-compose up -d

# 启动指定服务
docker-compose up -d web

# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs
docker-compose logs -f web

# 重新构建服务
docker-compose build
docker-compose up -d --build

# 进入服务容器
docker-compose exec web /bin/sh

# 重启服务
docker-compose restart web

# 暂停/恢复服务
docker-compose pause web
docker-compose unpause web

# 查看服务配置
docker-compose config

# 拉取最新镜像
docker-compose pull

# 缩放服务实例数
docker-compose up -d --scale web=3
```

### Compose 最佳实践
1. **使用环境变量**：敏感信息通过 `.env` 文件注入，不硬编码
2. **健康检查**：为关键服务配置健康检查，确保依赖就绪
3. **数据持久化**：数据库等有状态服务使用命名卷
4. **资源限制**：为服务配置 CPU 和内存限制
5. **网络隔离**：使用自定义网络，隔离不同应用
6. **重启策略**：配置合适的重启策略（`unless-stopped`）
7. **多环境配置**：使用 `docker-compose.override.yml` 管理环境差异

---

## 六、Docker 安全最佳实践

### 1. 镜像安全
- **使用官方或可信镜像**：优先使用 Docker Hub 官方镜像
- **定期更新基础镜像**：及时更新基础镜像，修复安全漏洞
- **扫描镜像漏洞**：使用 Trivy、Clair 等工具扫描镜像漏洞
- **最小化镜像**：使用精简基础镜像（alpine、slim），减少攻击面
- **不要在镜像中存储敏感信息**：密钥、密码通过环境变量或密钥管理服务注入

### 2. 容器安全
- **以非 root 用户运行**：使用 `USER` 指令切换到非 root 用户
- **只读文件系统**：使用 `--read-only` 挂载只读根文件系统
- **限制 capabilities**：使用 `--cap-drop=ALL` 移除所有 capabilities，按需添加
- **禁用特权模式**：避免使用 `--privileged`，除非绝对必要
- **限制资源**：使用 `--memory`、`--cpus` 限制容器资源使用
- **隔离网络**：使用自定义网络，避免使用 `--network=host`

### 3. 运行时安全
- **启用内容信任**：`export DOCKER_CONTENT_TRUST=1`，验证镜像签名
- **使用 seccomp/AppArmor**：限制容器系统调用和访问
- **定期更新 Docker**：及时更新 Docker 引擎，修复安全漏洞
- **监控容器行为**：使用 Falco 等工具监控容器异常行为
- **审计日志**：启用 Docker 审计日志，记录容器操作

---

## 七、Docker 性能优化

### 1. 镜像优化
- **多阶段构建**：构建阶段和运行阶段分离，减小最终镜像大小
- **精简基础镜像**：使用 alpine、distroless 等精简镜像
- **合并层**：合并 RUN 指令，减少镜像层数
- **清理缓存**：安装依赖后清理包管理器缓存
- **使用 .dockerignore**：排除不必要的文件，减小构建上下文

### 2. 构建优化
- **利用层缓存**：合理排序 Dockerfile 指令，利用构建缓存
- **并行构建**：使用 BuildKit 并行构建多阶段
- **使用构建缓存挂载**：`RUN --mount=type=cache` 缓存依赖下载
- **减小构建上下文**：使用 `.dockerignore` 排除大文件和无关文件

### 3. 运行时优化
- **资源限制**：合理设置 CPU 和内存限制，避免资源争抢
- **使用数据卷**：数据库等 IO 密集型应用使用数据卷，提升性能
- **网络优化**：使用自定义网络，避免端口映射开销
- **日志优化**：配置日志驱动和大小限制，避免日志占用过多磁盘
- **健康检查**：合理配置健康检查间隔和超时，避免频繁检查

---

## 八、常见问题与排查

### 1. 容器启动后立即退出
**原因**：容器主进程退出，或启动命令错误
**排查**：
```bash
# 查看容器日志
docker logs <container>

# 查看容器详情
docker inspect <container>

# 以前台模式运行，查看错误
docker run -it <image> /bin/sh
```

### 2. 端口映射不生效
**原因**：应用监听 127.0.0.1 而非 0.0.0.0，或端口被占用
**排查**：
```bash
# 查看端口映射
docker port <container>

# 查看容器网络
docker inspect <container> | grep -A 20 NetworkSettings

# 确保应用监听 0.0.0.0
# 修改应用配置，监听 0.0.0.0 而非 127.0.0.1
```

### 3. 镜像构建慢
**原因**：构建上下文大，或未利用层缓存
**排查**：
```bash
# 检查 .dockerignore 是否排除大文件
# 检查 Dockerfile 指令顺序，确保依赖文件先复制
# 使用 BuildKit 加速构建
DOCKER_BUILDKIT=1 docker build .
```

### 4. 容器间无法通信
**原因**：容器不在同一网络，或使用容器名而非服务名
**排查**：
```bash
# 查看容器网络
docker inspect <container> | grep -A 20 NetworkSettings

# 确保容器在同一网络
docker network connect <network> <container>

# 使用容器名或服务名通信，不要使用 localhost
```

### 5. 数据丢失
**原因**：数据未挂载到数据卷，容器删除后数据丢失
**排查**：
```bash
# 查看容器挂载
docker inspect <container> | grep -A 20 Mounts

# 确保数据目录挂载到数据卷或绑定挂载
docker run -v myvolume:/data <image>
```

---

## 🔗 关联笔记

**Docker 基础**
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
- [[Linux 常用命令知识点系统梳理_优化版]] — Linux 常用命令
- [[CI-CD持续集成与部署]] — CI/CD 流水线
- [[DevOps与云原生知识点完整整合大全_优化版]] — DevOps 与云原生完整知识体系

---

## 📖 学习路径建议

1. **入门**：理解 Docker 核心概念（镜像、容器、仓库），掌握常用命令，能够运行和管理容器
2. **进阶**：学习 Dockerfile 编写和最佳实践，掌握 Docker Compose 多容器编排，理解容器原理
3. **高级**：深入 Namespace/Cgroups/UnionFS 原理，掌握镜像优化和性能调优，学习容器安全
4. **专家**：研究容器运行时（containerd/runc），设计企业级容器平台，结合 Kubernetes 进行编排

---

## 💡 精简总结

Docker 是一个基于容器技术的应用打包和部署平台，通过镜像、容器、仓库三大核心概念，实现"一次构建，到处运行"。其底层依赖 Linux 内核的 Namespace（隔离）、Cgroups（资源限制）、UnionFS（分层文件系统）三大特性。Dockerfile 是构建镜像的声明式文件，遵循最佳实践可以构建出小、快、安全的镜像。Docker Compose 用于多容器应用编排，一条命令即可启动完整应用栈。Docker 是现代云原生应用部署的基石，与 Kubernetes 配合使用，可实现大规模容器编排和管理。

---

> **Docker 的本质不是虚拟化，而是将应用及其环境标准化封装，让部署变得简单、可重复、可移植。**

[[Home|🏠 返回首页]] · [[MOC-云原生与运维|☁️ 云原生与运维]] · [[学习路线总览|🗺️ 学习路线]]
