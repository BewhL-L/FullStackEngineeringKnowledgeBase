---
title: Docker命令速查表
tags: [速查表, Docker, 云原生, DevOps]
category: 云原生
created: 2026-08-27
updated: 2026-08-27
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 重要
pre: []
aliases: [Docker命令速查表]
---

# Docker命令速查表

> **文档说明**：Docker常用命令速查表，覆盖镜像、容器、网络、数据卷、Dockerfile、Compose。
>
> **适用人群**：开发者、运维工程师
>
> **前置知识**：容器基本概念

---

## 一、镜像操作

```bash
# 查看镜像
docker images                    # 列出本地镜像
docker images -a                 # 包含中间层
docker images --digests          # 显示摘要

# 搜索/拉取
docker search nginx              # 搜索镜像
docker pull nginx                # 拉取最新版
docker pull nginx:1.25           # 拉取指定版本
docker pull nginx@sha256:xxx     # 按摘要拉取

# 构建镜像
docker build -t myapp:1.0 .      # 构建并打标签
docker build -f Dockerfile.dev . # 指定Dockerfile
docker build --no-cache .        # 不使用缓存
docker build --build-arg KEY=val .  # 传递构建参数
docker build -t app --platform linux/amd64 .  # 跨平台构建

# 标签
docker tag source:tag target:tag # 打标签
docker tag image_id myrepo/app:1.0

# 推送
docker login                     # 登录仓库
docker push myrepo/app:1.0       # 推送镜像

# 删除
docker rmi image-id              # 删除镜像
docker rmi -f image-id           # 强制删除
docker image prune               # 删除悬空镜像
docker image prune -a            # 删除所有未使用镜像

# 导出/导入
docker save -o app.tar myapp:1.0 # 导出镜像到文件
docker load -i app.tar           # 从文件导入镜像

# 查看详情
docker inspect image-id          # 镜像详细信息
docker history image-id          # 镜像构建历史
```

---

## 二、容器操作

```bash
# 运行容器
docker run nginx                          # 运行（前台）
docker run -d nginx                       # 后台运行
docker run --name mynginx nginx           # 指定名称
docker run -p 8080:80 nginx               # 端口映射 主机:容器
docker run -p 8080:80 -p 8443:443 nginx   # 多端口
docker run -v /host:/container nginx      # 挂载卷
docker run -e ENV=prod nginx              # 环境变量
docker run --rm nginx                     # 停止后自动删除
docker run -it ubuntu bash                # 交互式进入
docker run --network mynet nginx          # 指定网络
docker run --restart=always nginx         # 自动重启

# 查看容器
docker ps                         # 运行中的容器
docker ps -a                      # 所有容器
docker ps -q                      # 只显示ID

# 启动/停止/重启
docker start container-id         # 启动
docker stop container-id          # 停止（优雅）
docker kill container-id          # 强制停止
docker restart container-id       # 重启

# 删除
docker rm container-id            # 删除容器
docker rm -f container-id         # 强制删除（运行中也删）
docker container prune            # 删除所有停止的容器

# 进入容器
docker exec -it container-id bash # 进入运行中容器
docker exec container-id cmd      # 执行命令
docker attach container-id        # 附加到容器

# 查看信息
docker logs container-id          # 查看日志
docker logs -f container-id       # 实时跟踪
docker logs --tail 100 cid        # 最后100行
docker inspect container-id       # 详细信息
docker stats                     # 资源使用统计
docker top container-id           # 容器内进程
docker port container-id          # 端口映射

# 复制文件
docker cp file.txt cid:/path/     # 主机→容器
docker cp cid:/path/file.txt ./   # 容器→主机

# 暂停/恢复
docker pause container-id         # 暂停
docker unpause container-id       # 恢复
```

---

## 三、数据卷

```bash
# 管理卷
docker volume create myvol        # 创建卷
docker volume ls                  # 列出卷
docker volume inspect myvol       # 查看详情
docker volume rm myvol            # 删除卷
docker volume prune               # 删除未使用卷

# 使用卷
docker run -v myvol:/data nginx   # 命名卷
docker run -v /host/path:/data nginx  # 绑定挂载
docker run -v /host/path:/data:ro nginx  # 只读挂载
```

---

## 四、网络

```bash
# 网络管理
docker network ls                 # 列出网络
docker network create mynet       # 创建网络
docker network create --driver bridge --subnet 172.20.0.0/16 mynet
docker network inspect mynet      # 查看详情
docker network rm mynet           # 删除网络
docker network prune             # 删除未使用网络

# 容器网络
docker network connect mynet cid  # 连接网络
docker network disconnect mynet cid # 断开网络

# 网络类型
# bridge   默认，容器间通过bridge通信
# host     共享主机网络
# none     无网络
# overlay  多主机集群网络
```

---

## 五、Dockerfile

```dockerfile
# 基础镜像
FROM node:18-alpine

# 元数据
LABEL maintainer="name@example.com"
LABEL version="1.0"

# 工作目录
WORKDIR /app

# 环境变量
ENV NODE_ENV=production
ENV PORT=3000

# 构建参数
ARG BUILD_VERSION=latest

# 复制文件（优先复制依赖文件，利用缓存）
COPY package*.json ./
RUN npm ci --only=production

# 复制源码
COPY . .

# 构建
RUN npm run build

# 暴露端口（只是声明，需-p映射）
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:3000/health || exit 1

# 切换用户（非root运行）
RUN addgroup -S app && adduser -S app -G app
USER app

# 启动命令（exec形式，推荐）
CMD ["node", "server.js"]

# 入口点（容器启动时执行，CMD作为参数）
ENTRYPOINT ["docker-entrypoint.sh"]
```

### 多阶段构建

```dockerfile
# 构建阶段
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段（只包含运行时）
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### 镜像优化要点

- 使用alpine/slim基础镜像
- 多阶段构建，运行阶段不含编译工具
- 合并RUN指令，减少层数
- 利用构建缓存（依赖文件先复制）
- 清理包管理器缓存：`rm -rf /var/lib/apt/lists/*`
- 使用非root用户运行
- 添加.dockerignore排除无关文件

---

## 六、Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DB_HOST=db
    depends_on:
      db:
        condition: service_healthy
    restart: always
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  pgdata:

networks:
  default:
    name: myapp-net
```

```bash
# Compose命令
docker compose up -d              # 启动（后台）
docker compose up --build         # 构建并启动
docker compose down               # 停止并删除
docker compose down -v            # 同时删除卷
docker compose ps                 # 查看状态
docker compose logs -f            # 查看日志
docker compose logs web -f        # 查看指定服务
docker compose exec web bash      # 进入服务
docker compose restart web        # 重启服务
docker compose pull               # 拉取最新镜像
docker compose config             # 验证并显示配置
```

---

## 七、系统与清理

```bash
# 系统信息
docker info                      # Docker系统信息
docker version                   # 版本信息

# 资源清理
docker system df                 # 磁盘使用
docker system prune              # 清理停止容器+悬空镜像+未使用网络
docker system prune -a           # 清理所有未使用镜像
docker system prune -a --volumes # 同时清理卷

# 一键清理所有
docker stop $(docker ps -aq)     # 停止所有容器
docker rm $(docker ps -aq)       # 删除所有容器
docker rmi $(docker images -q)   # 删除所有镜像
```

---

## 八、常见问题排查

```bash
# 容器启动失败
docker logs container-id         # 查看日志
docker inspect container-id      # 查看配置

# 进入已停止的容器调试
docker commit cid debug-image    # 提交为镜像
docker run -it --entrypoint sh debug-image

# 查看镜像层大小
docker history image-id --no-trunc

# 清理悬空镜像
docker image prune -f
```

---

## 关联文档

- [[Docker-核心原理与镜像优化]] — Docker深度原理
- [[Dockerfile最佳实践]] — Dockerfile优化
- [[Docker-Compose编排]] — Compose详解
- [[K8s-核心概念与架构]] — Kubernetes进阶
- [[Linux命令速查表]] — Linux命令

---

> 💡 **使用建议**：日常高频：run/ps/logs/exec/build/compose。镜像优化是进阶重点：多阶段构建、alpine基础镜像、缓存利用、非root运行。生产环境务必设置restart策略和healthcheck。
