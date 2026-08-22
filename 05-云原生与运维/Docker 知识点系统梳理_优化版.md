---
title: Docker 知识点系统梳理
tags: [云原生, Docker, 容器, 面试]
created: 2026-08-13
updated: 2026-08-13
---

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。

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

> 🔍 **知识点深度解析**
>
> **作用**：Namespace 是 Linux 内核提供的隔离机制，让每个容器拥有独立的全局资源视图（独立的进程树、网络、挂载点等），是容器"看起来像一台独立机器"的根本原因。
>
> **原理**：内核通过 `clone()`、`unshare()`、`setns()` 系统调用创建并管理 Namespace；Docker 启动容器时为 PID、NET、IPC、MNT、UTS、USER 等维度分别建立独立 Namespace，容器内进程只能看到本 Namespace 内的资源，从而实现隔离。
>
> **用法要点**：① Namespace 只解决"看得见"的隔离，并不限制资源用量；② 6 类 Namespace 各自隔离不同维度，可单独或组合使用；③ USER Namespace 可把容器内 root 映射为宿主机普通用户，提升安全性；④ 容器共享宿主机内核，隔离性弱于虚拟机；⑤ 排障时常需进入对应 Namespace 查看真实网络栈/进程树。

### 2.2 Cgroups（控制组）— 资源限制

限制容器的 CPU、内存、磁盘 IO、网络带宽等资源使用。

> 🔍 **知识点深度解析**
>
> **作用**：Cgroups（Control Groups）限制、统计和隔离容器对 CPU、内存、IO、网络带宽等资源的使用，防止单容器耗尽宿主机资源、实现多容器公平调度。
>
> **原理**：内核以层级结构组织进程组，通过 cgroupfs（`/sys/fs/cgroup`）暴露接口；Docker 为每个容器创建 cgroup 并设置 limits，内核调度器据此强制限额（cgroup v1 按子系统、v2 统一层级）。
>
> **用法要点**：① 常与 Namespace 配合（隔离 + 限制）；② 可设置 cpu quota/period、memory limit、pids limit 等；③ 内存超限会触发 OOM Killer 杀死容器进程；④ `docker run` 用 `-m`/`--cpus` 指定限额；⑤ 较新内核默认启用 cgroup v2，资源模型更统一。

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


---
## 3. 常用命令

### 3.1 镜像命令

```bash

> 🔍 **知识点深度解析**
>
> **作用**：Docker 镜像命令涵盖拉取、查看、构建、删除和导出导入，是镜像生命周期管理的基础。
>
> **原理**：docker pull 拉取镜像（默认 Docker Hub，可指定 registry）；docker images 列出本地镜像；docker build -t name:tag . 根据 Dockerfile 构建；docker rmi 删除镜像（-f 强制）；docker tag 打标签；docker save/load 导出导入镜像为 tar 文件；docker history 查看镜像层历史。镜像由多层只读层组成，构建时利用层缓存加速。
>
> **用法要点**：① docker pull nginx:1.25 拉取指定版本，不写 tag 默认 latest  ② docker build -t myapp:v1 . 末尾的 . 是构建上下文  ③ docker rmi $(docker images -q) 批量删除  ④ docker save -o img.tar myapp:v1 导出，docker load -i 导入  ⑤ 面试常考：镜像分层原理、构建缓存、多阶段构建减小镜像

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

> 🔍 **知识点深度解析**
>
> **作用**：镜像命令用于获取、查看、构建、删除、共享镜像，是镜像生命周期管理的基础操作。
>
> **原理**：`docker pull` 从 Registry 按 digest/tag 拉取分层镜像并写入本地存储（overlay2）；`docker build` 读取 Dockerfile 逐指令生成镜像层；`save`/`load` 以 tar 形式离线迁移镜像。
>
> **用法要点**：① `pull` 优先用具体版本标签而非 `latest`，保证可重复构建；② `images` 查看本地镜像及大小，可加 `--filter` 过滤；③ `rmi` 删除前需先删除依赖容器；④ `build -t` 打标签、`-f` 指定非默认 Dockerfile；⑤ `push` 前需 `login` 并打全仓库名；⑥ `save`/`load` 适合内网离线分发。

### 3.2 容器命令

```bash

> 🔍 **知识点深度解析**
>
> **作用**：Docker 容器命令管理容器的启动、停止、进入、日志和生命周期。
>
> **原理**：docker run 启动容器（-d 后台、-p 端口映射、-v 挂载、--name 命名、-e 环境变量、--rm 退出自动删除）；docker ps 查看运行中容器（-a 含已停止）；docker stop/start/restart 控制容器；docker exec -it <id> bash 进入运行中容器；docker logs -f 查看日志；docker rm 删除容器（-f 强制删除运行中）；docker cp 在容器和宿主机间复制文件。
>
> **用法要点**：① docker run -d -p 8080:80 --name web nginx  ② docker exec -it <id> /bin/sh（Alpine 镜像用 sh 不是 bash）  ③ docker logs -f --tail 100 <id> 实时查看日志  ④ docker rm -f <id> 强制删除运行中的容器  ⑤ 面试常考：run 参数、exec vs attach、容器日志查看

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

> 🔍 **知识点深度解析**
>
> **作用**：容器命令负责容器的创建、启停、进入、日志查看与删除，是日常运维最常用的操作集合。
>
> **原理**：`docker run` 先按镜像创建可写层并启动进程（`-d` 后台、`-p` 端口映射、`-v` 挂载卷）；`exec` 在已有容器内新建进程（通过 nsenter 进入 Namespace）；`ps` 读取容器状态元数据，`logs` 读取容器 stdout/stderr。
>
> **用法要点**：① `run` 常用组合 `-d --name -p -v` 一次性定义运行参数；② `exec -it` 进入交互终端排障；③ `logs -f --tail` 实时跟踪日志；④ `stop` 发 SIGTERM 优雅停止，`rm -f` 强制删运行中的容器；⑤ `stats` 实时监控资源占用；⑥ 容器退出后默认停止，需 `--restart` 设置重启策略。

### 3.3 其他

```bash

> 🔍 **知识点深度解析**
>
> **作用**：Docker 其他常用命令包括系统清理、信息查看、网络和卷管理等运维操作。
>
> **原理**：docker system df 查看磁盘占用；docker system prune -a 清理无用镜像/容器/网络/卷（释放磁盘）；docker info 查看 Docker 系统信息；docker inspect <id> 查看容器/镜像详细配置（JSON）；docker stats 实时监控容器资源使用（CPU/内存/网络/IO）；docker events 查看实时事件流。
>
> **用法要点**：① docker system prune -a --volumes 彻底清理（谨慎）  ② docker inspect <id> | grep IPAddress 查容器 IP  ③ docker stats 实时资源监控，类似 top  ④ docker info 查看存储驱动、运行时等系统信息  ⑤ 面试常考：磁盘清理、inspect 用法、资源监控

# 查看 Docker 信息
docker info
docker version

# 清理无用资源
docker system prune -a  # 清理所有未使用的镜像、容器、网络
```

> 🔍 **知识点深度解析**
>
> **作用**：`info`/`version` 查看 Docker 引擎状态与版本，`system prune` 清理悬挂资源以释放磁盘空间。
>
> **原理**：`info` 读取 daemon 配置、存储驱动、运行时等运行时信息；`system prune` 扫描未被容器/镜像引用的悬挂层、网络、缓存并删除。
>
> **用法要点**：① `version` 区分 Client 与 Server（dockerd）版本，排障先看两者是否一致；② `info` 可确认存储驱动（overlay2）、Cgroup 版本等；③ `prune -a` 连未使用镜像一起删，操作前务必确认；④ 生产环境应定期清理避免磁盘写满；⑤ 可加 `--filter` 限定清理范围。

---


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

> 🔍 **知识点深度解析**
>
> **作用**：Dockerfile 指令定义镜像的构建步骤，决定最终镜像的内容、运行环境与启动行为。
>
> **原理**：每条指令（除 FROM/注释）生成一个只读镜像层并叠加；构建上下文（build context）被发送到 daemon，`COPY`/`ADD` 从中取文件；指令与上下文未变时命中缓存可跳过重建。
>
> **用法要点**：① `FROM` 必须首行，指定基础镜像；② `RUN` 在构建期执行并成层，宜用 `&&` 合并减少层数；③ `COPY` 优于 `ADD`（除非需自动解压 tar 或取 URL）；④ `ENV` 注入环境变量，`ARG` 仅构建期参数；⑤ `CMD` 可被 `run` 参数覆盖，`ENTRYPOINT` 不可；⑥ `EXPOSE` 仅声明端口，真正映射靠 `-p`。

### 4.2 示例

```dockerfile

> 🔍 **知识点深度解析**
>
> **作用**：Dockerfile 示例演示从基础镜像到应用镜像的完整构建流程，包含多阶段构建最佳实践。
>
> **原理**：典型 Java 应用 Dockerfile：FROM eclipse-temurin:17-jre 基础镜像；WORKDIR /app 设置工作目录；COPY target/*.jar app.jar 复制 JAR；EXPOSE 8080 声明端口；ENTRYPOINT ["java","-jar","app.jar"] 启动命令。多阶段构建：第一阶段 maven 构建，第二阶段只 COPY JAR 到 JRE 镜像，避免构建工具进入最终镜像。.dockerignore 排除 target/.git 等。
>
> **用法要点**：① 多阶段构建：builder 阶段编译，final 阶段只 COPY 产物  ② 用 JRE 而非 JDK 基础镜像减小体积  ③ ENTRYPOINT 用 exec 形式（JSON 数组），正确接收信号  ④ .dockerignore 排除无关文件，加速构建  ⑤ 面试常考：多阶段构建、CMD vs ENTRYTRYPOINT、镜像瘦身

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


---
## 5. 数据卷（Volume）

### 5.1 三种挂载方式

```bash

> 🔍 **知识点深度解析**
>
> **作用**：Docker 数据挂载有三种方式：volume（Docker 管理）、bind mount（宿主机路径）、tmpfs（内存）。
>
> **原理**：Volume：docker volume create 创建，存储在 /var/lib/docker/volumes/，Docker 管理生命周期，适合数据库数据持久化和容器间共享。Bind mount：-v /host/path:/container/path 直接挂载宿主机目录，适合开发时挂载源码和配置。Tmpfs：--tmpfs /path 挂载到内存，容器停止数据消失，适合敏感临时数据。
>
> **用法要点**：① Volume 最安全可移植，Docker 管理，适合生产数据持久化  ② Bind mount 直接映射宿主机路径，适合开发环境  ③ Tmpfs 数据在内存中，适合密码/密钥等敏感临时数据  ④ -v 和 --mount 都可挂载，--mount 语法更明确  ⑤ 面试常考：三种挂载区别、volume 位置、bind mount 风险

# 1. 匿名卷
docker run -v /data nginx

# 2. 具名卷（推荐，Docker 管理）
docker run -v myvolume:/data nginx

# 3. 绑定挂载（宿主机目录）
docker run -v /host/path:/container/path nginx
```

> 🔍 **知识点深度解析**
>
> **作用**：挂载让容器与宿主机/卷共享数据，实现持久化与跨容器数据共享，避免数据随容器删除而丢失。
>
> **原理**：匿名卷由 Docker 自动分配宿主机路径；具名卷由 Docker 在自有卷目录管理并命名；绑定挂载直接把宿主机目录映射到容器内路径；三者最终都是把宿主机某目录挂进容器文件系统。
>
> **用法要点**：① 匿名卷难管理，不推荐长久使用；② 具名卷由 Docker 统一生命周期管理，最常用；③ 绑定挂载方便开发热更新（代码同步）；④ `-v` 与 `--mount` 等价，`--mount` 语法更显式；⑤ 挂载只读可加 `:ro` 防误写；⑥ 多容器挂载同一卷即可交换数据。

### 5.2 数据卷特点

- 数据持久化，容器删除数据不丢失
- 可在多个容器间共享
- 支持数据卷容器、数据卷插件

> 🔍 **知识点深度解析**
>
> **作用**：数据卷提供独立于容器生命周期的持久化存储，是容器有状态服务（如数据库）的基石。
>
> **原理**：卷由 Docker 守护进程管理，存储于宿主机特定目录（`/var/lib/docker/volumes`），容器删除时卷默认保留；卷内容绕过容器可写层直接读写宿主文件系统，性能更好。
>
> **用法要点**：① 容器删除后卷数据不丢，需显式 `docker volume rm` 清理；② 多个容器可同时挂载同一卷实现共享；③ 数据库等状态服务应始终用卷；④ 备份卷可先停容器再打包卷目录；⑤ 可用卷插件对接 NFS/云存储；⑥ 早期"数据卷容器"模式已被自定义网络 + 卷取代。

---


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

> 🔍 **知识点深度解析**
>
> **作用**：网络模式决定容器如何接入网络，影响隔离性、性能与容器间通信方式。
>
> **原理**：`bridge` 模式创建 docker0 网桥，容器经 veth pair 接入并通过 NAT 出网；`host` 模式直接使用宿主机网络命名空间；`none` 无网络；`container` 模式共享另一容器的网络栈。
>
> **用法要点**：① `bridge` 默认且最通用，对外需 `-p` 端口映射；② `host` 省去 NAT、性能高但易端口冲突且降低隔离；③ `none` 用于离线计算/安全隔离；④ `container` 模式让多容器共享网络（如 sidecar）；⑤ 默认桥不支持容器名互访，跨容器通信应建自定义网络；⑥ 端口映射本质是 iptables/NFtables 规则。

### 6.2 自定义网络

```bash

> 🔍 **知识点深度解析**
>
> **作用**：Docker 自定义网络让容器间通过容器名互相访问，提供 DNS 解析和网络隔离。
>
> **原理**：docker network create mynet 创建 bridge 网络；docker run --network mynet 将容器加入网络。同一自定义网络中的容器可以通过容器名互相访问（Docker 内置 DNS 解析），而默认 bridge 网络只能通过 IP 访问。自定义网络支持 --subnet 指定子网、--driver 选择驱动（bridge/overlay/macvlan）。容器可连接多个网络。
>
> **用法要点**：① docker network create mynet 创建自定义 bridge 网络  ② 同一网络内容器名自动 DNS 解析，无需 --link  ③ docker network connect/disconnect 动态连接/断开网络  ④ overlay 网络用于 Swarm 多主机容器通信  ⑤ 面试常考：自定义网络 DNS、bridge vs overlay、容器间通信

# 创建网络
docker network create mynet

# 运行容器加入网络
docker run -d --name app --network mynet myapp
docker run -d --name db --network mynet mysql

# 容器间可用容器名通信（DNS 解析）
# app 容器内可 ping db
```

> 🔍 **知识点深度解析**
>
> **作用**：自定义网络（user-defined bridge）提供容器间自动 DNS 发现与更好的隔离，是编排多服务通信的推荐方式。
>
> **原理**：Docker 为自定义网络内置内嵌 DNS 服务器，容器以名称/别名互相解析；同一网络内容器间可直接用服务名通信，无需硬编码 IP。
>
> **用法要点**：① `network create` 创建，`run --network` 加入；② 同网容器可用容器名或 `--network-alias` 互访；③ 不同网络间默认隔离，需显式连接才互通；④ 比默认 bridge 多了 DNS 与自动隔离；⑤ Compose 默认会为每个项目建独立网络；⑥ 排障用 `docker network inspect` 看子网与连接。

---


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

> 🔍 **知识点深度解析**
>
> **作用**：`docker-compose.yml` 用声明式配置定义多容器应用的服务、网络与卷，一条命令即可整体启停。
>
> **原理**：Compose 读取 YAML，为每个 service 创建容器并接入统一网络；`depends_on` 控制启动顺序（仅顺序，不等待就绪），`volumes`/`services` 在顶层声明并在 service 中引用。
>
> **用法要点**：① `services` 下每个服务可指定 `build` 或 `image`；② `ports` 做主机端口映射，`environment` 注入环境变量；③ `depends_on` 只管启动先后，应用就绪需自身健康检查；④ `volumes` 挂宿主机路径或命名卷；⑤ 单个文件描述整个应用栈，便于版本管理；⑥ 变量可用 `${}` 从 `.env` 注入。

### 7.2 常用命令

```bash
docker-compose up -d          # 后台启动
docker-compose down           # 停止并删除
docker-compose logs -f web    # 查看服务日志
docker-compose exec web bash  # 进入服务容器
docker-compose build          # 重新构建
```

> 🔍 **知识点深度解析**
>
> **作用**：Compose 命令用于按配置整体构建、启动、停止、查看与进入多容器应用，简化多服务运维。
>
> **原理**：`up`/`down` 基于 YAML 创建/销毁容器、网络、卷；`logs`/`exec` 代理到对应 service 容器；`build` 重新执行各服务镜像构建。
>
> **用法要点**：① `up -d` 后台拉起整套服务；② `down` 停止并删容器网络（加 `-v` 连卷一起删，慎用）；③ `logs -f <服务>` 跟踪某服务日志；④ `exec` 进入指定服务容器排障；⑤ `build` 在代码变更后重建镜像；⑥ 可用 `-f` 指定非默认 compose 文件，生产可用 `deploy.replicas` 扩展副本。

---


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
