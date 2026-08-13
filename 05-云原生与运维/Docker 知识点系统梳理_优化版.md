---
title: Docker 知识点系统梳理
tags: [云原生, Docker, 容器, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# Docker 知识点系统梳理（优化版）

> **文档说明**：系统梳理 Docker 核心知识，涵盖容器原理、镜像、容器、Dockerfile、数据卷、网络、Compose、多阶段构建等内容。

---

## 1. 概述

Docker 是开源的**容器化平台**，将应用及其依赖打包到轻量级、可移植的容器中，实现"一次构建，到处运行"。

**容器 vs 虚拟机**：

| 特性 | 容器（Docker） | 虚拟机（VM） |
|------|----------------|--------------|
| 虚拟化级别 | 操作系统级 | 硬件级 |
| 启动速度 | 秒级 | 分钟级 |
| 资源占用 | MB 级 | GB 级 |
| 性能 | 接近原生 | 有损耗 |
| 隔离性 | 进程级隔离 | 完全隔离 |
| 内核 | 共享宿主机内核 | 独立内核 |

**核心组件**：
- **镜像（Image）**：只读模板，包含应用和依赖
- **容器（Container）**：镜像的运行实例
- **仓库（Registry）**：存储镜像（Docker Hub、阿里云镜像仓库）

---

## 2. 容器核心原理

Docker 容器基于 Linux 内核的三大技术：

### 2.1 Namespace（命名空间）— 隔离

| Namespace | 隔离内容 |
|-----------|----------|
| PID | 进程 ID |
| NET | 网络栈 |
| IPC | 进程间通信 |
| MNT | 文件系统挂载点 |
| UTS | 主机名和域名 |
| USER | 用户和用户组 |

### 2.2 Cgroups（控制组）— 资源限制

限制容器的 CPU、内存、磁盘 IO、网络带宽等资源使用。

### 2.3 UnionFS（联合文件系统）— 镜像分层

镜像由多层只读层组成，容器启动时在最上层加可写层。

> 🔍 **知识点深度解析**
>
> **作用**：理解容器原理才能理解 Docker 为什么轻量、隔离性如何。
>
> **原理**：容器不是虚拟机，没有自己的内核，而是通过 Namespace 实现系统资源的隔离（每个容器看到独立的进程、网络、文件系统），通过 Cgroups 限制资源使用（防止一个容器占满宿主机资源）。镜像用 UnionFS 分层存储，每层只读，修改文件时复制到可写层（Copy-on-Write），所以多个容器可共享同一镜像的只读层，节省空间。容器本质是宿主机上的一个进程，通过上述技术实现了隔离和限制。
>
> **用法要点**：① 容器共享宿主机内核，所以 Linux 容器不能在 Windows 上原生运行（需要 WSL2 或虚拟机）；② 容器内进程在宿主机上可见（ps aux 能看到）；③ 面试常考：容器原理、Namespace/Cgroups、容器 vs 虚拟机、镜像分层。

---

## 3. 常用命令

### 3.1 镜像命令

```bash
# 拉取镜像
docker pull nginx:latest

# 查看本地镜像
docker images

# 删除镜像
docker rmi nginx:latest

# 构建镜像
docker build -t myapp:1.0 .

# 推送镜像
docker push myregistry.com/myapp:1.0

# 镜像导出/导入
docker save -o myapp.tar myapp:1.0
docker load -i myapp.tar
```

### 3.2 容器命令

```bash
# 运行容器
docker run -d --name mynginx -p 8080:80 -v /data:/usr/share/nginx/html nginx

# 查看容器
docker ps          # 运行中
docker ps -a       # 所有

# 停止/启动/重启
docker stop mynginx
docker start mynginx
docker restart mynginx

# 进入容器
docker exec -it mynginx /bin/bash

# 查看日志
docker logs -f --tail 100 mynginx

# 删除容器
docker rm mynginx
docker rm -f mynginx  # 强制删除运行中的容器

# 查看容器资源使用
docker stats
```

### 3.3 其他

```bash
# 查看 Docker 信息
docker info
docker version

# 清理无用资源
docker system prune -a  # 清理所有未使用的镜像、容器、网络
```

---

## 4. Dockerfile

### 4.1 常用指令

| 指令 | 说明 |
|------|------|
| `FROM` | 基础镜像（必须第一条） |
| `WORKDIR` | 工作目录 |
| `COPY` | 复制文件（推荐，比 ADD 简单） |
| `ADD` | 复制文件（支持 URL、自动解压 tar） |
| `RUN` | 构建时执行命令（创建新层） |
| `ENV` | 设置环境变量 |
| `EXPOSE` | 声明端口 |
| `CMD` | 容器启动时执行（可被覆盖） |
| `ENTRYPOINT` | 容器启动时执行（不可被覆盖，CMD 作为参数） |
| `VOLUME` | 声明数据卷 |
| `ARG` | 构建参数 |

### 4.2 示例

```dockerfile
# 多阶段构建：第一阶段构建
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 第二阶段：只保留构建产物
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

> 🔍 **知识点深度解析**
>
> **作用**：Dockerfile 是构建镜像的脚本，优化 Dockerfile 能减小镜像体积、提升构建速度。
>
> **原理**：Dockerfile 每条指令创建一个镜像层，层会缓存——如果指令和上下文没变，直接用缓存。所以变化频率低的指令放前面（依赖安装），变化频率高的放后面（代码复制），最大化利用缓存。多阶段构建用多个 FROM，最终镜像只保留最后一个阶段的内容，构建工具（node、maven）不会进入最终镜像，大幅减小体积。CMD 和 ENTRYPOINT 区别：CMD 可被 docker run 后的参数覆盖，ENTRYPOINT 不会（CMD 的内容作为参数传给 ENTRYPOINT）。
>
> **用法要点**：① 用 Alpine 基础镜像减小体积；② 多阶段构建分离编译和运行环境；③ 合并 RUN 指令减少层数（用 && 连接）；④ .dockerignore 排除不需要的文件（node_modules、.git）；⑤ 面试常考：Dockerfile 指令、CMD vs ENTRYPOINT、多阶段构建、镜像优化。

---

## 5. 数据卷（Volume）

### 5.1 三种挂载方式

```bash
# 1. 匿名卷
docker run -v /data nginx

# 2. 具名卷（推荐，Docker 管理）
docker run -v myvolume:/data nginx

# 3. 绑定挂载（宿主机目录）
docker run -v /host/path:/container/path nginx
```

### 5.2 数据卷特点

- 数据持久化，容器删除数据不丢失
- 可在多个容器间共享
- 支持数据卷容器、数据卷插件

---

## 6. 网络

### 6.1 网络模式

| 模式 | 说明 |
|------|------|
| `bridge` | 默认，容器连接到 docker0 网桥，通过 NAT 访问外网 |
| `host` | 共享宿主机网络，性能好但端口冲突 |
| `none` | 无网络 |
| `container` | 共享其他容器的网络 |
| 自定义网络 | 推荐，容器间可用容器名 DNS 解析 |

### 6.2 自定义网络

```bash
# 创建网络
docker network create mynet

# 运行容器加入网络
docker run -d --name app --network mynet myapp
docker run -d --name db --network mynet mysql

# 容器间可用容器名通信（DNS 解析）
# app 容器内可 ping db
```

---

## 7. Docker Compose

### 7.1 docker-compose.yml 示例

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8080:80"
    depends_on:
      - db
    environment:
      - DB_HOST=db
    volumes:
      - ./html:/usr/share/nginx/html

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: mydb
    volumes:
      - dbdata:/var/lib/mysql

volumes:
  dbdata:
```

### 7.2 常用命令

```bash
docker-compose up -d          # 后台启动
docker-compose down           # 停止并删除
docker-compose logs -f web    # 查看服务日志
docker-compose exec web bash  # 进入服务容器
docker-compose build          # 重新构建
```

---

## 8. 镜像优化

1. **用 Alpine 基础镜像**：比 Debian 小很多
2. **多阶段构建**：构建工具不进入最终镜像
3. **合并 RUN 指令**：减少层数，`apt-get install && rm -rf /var/lib/apt/lists/*`
4. **.dockerignore**：排除 node_modules、.git 等
5. **用 COPY 代替 ADD**：ADD 会自动解压 tar，可能意外
6. **非 root 用户运行**：安全最佳实践
7. **具体版本标签**：不要用 latest，不可重复构建

---

## 9. 面试高频考点

1. **容器原理**：Namespace、Cgroups、UnionFS
2. **容器 vs 虚拟机**：区别、优缺点
3. **Dockerfile**：常用指令、CMD vs ENTRYPOINT
4. **多阶段构建**：原理、优势
5. **镜像分层**：Copy-on-Write、层缓存
6. **数据卷**：三种方式、持久化
7. **网络模式**：bridge、host、自定义网络
8. **镜像优化**：减小体积的方法
9. **Docker Compose**：编排多容器应用
10. **容器安全**：非 root、只读文件系统、资源限制

---

## 📝 精简总结

- Docker 容器 = Namespace（隔离）+ Cgroups（限制）+ UnionFS（分层）
- 镜像是只读模板，容器是镜像的运行实例（加可写层）
- Dockerfile 构建镜像，多阶段构建减小体积
- 数据卷实现持久化，具名卷推荐
- 自定义网络支持容器名 DNS 通信
- Docker Compose 编排多容器应用
- 优化：Alpine 基础、多阶段、合并 RUN、.dockerignore

---

[[05-云原生与运维/MOC-云原生与运维|← 返回云原生 MOC]] | [[Home|🏠 返回首页]]
