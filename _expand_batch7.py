# -*- coding: utf-8 -*-
"""第七批：补充前次会话遗漏的知识点深度解析（Java AI/AIGC、分布式锁、微服务组件、Docker、Nginx、HTTP、Git、Python 全栈）"""
import os, sys
from collections import defaultdict

ENGINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "01-前端开发")
sys.path.insert(0, ENGINE_DIR)
from engine import expand

BASE = os.path.dirname(os.path.abspath(__file__))

# 每个文件的 content_map
file_maps = {}

# ============ 02-后端开发 ============
file_maps[r"02-后端开发\Java AI Agent开发知识点系统梳理_优化版.md"] = {
    "### 2.2 快速开始": (
        "Spring AI 快速集成：引入 starter、配置 API Key、注入 ChatClient 即可调用大模型。",
        "添加 spring-ai-openai-spring-boot-starter 依赖，在 application.yml 配置 spring.ai.openai.api-key 和 base-url。注入 ChatClient.Builder 构建 ChatClient，调用 .prompt().user(\"问题\").call().content() 获得响应。Spring Boot 自动配置根据 classpath 和配置属性创建 ChatModel/ChatClient Bean。",
        ["引入 spring-ai-bom 管理版本，starter 自动装配", "application.yml 配置 api-key/base-url/chat.options.model", "ChatClient 是核心入口，支持 prompt/user/system/call/stream", "call() 同步返回，stream() 返回 Flux 流式响应", "面试常考：Spring AI 自动配置原理、ChatClient 用法"]
    ),
    "### 2.3 Function Calling（工具调用）": (
        "Function Calling 让 LLM 能调用 Java 方法获取外部数据或执行操作，是 Agent 工具能力的基础。",
        "定义 @Bean Function<Request, Response> 并在 ChatClient 中通过 .functions(\"beanName\") 注册。LLM 返回工具调用请求（函数名+JSON 参数），Spring AI 自动调用对应 Java 方法，将结果序列化为 JSON 回传 LLM，LLM 再生成最终回答。支持多轮工具调用和函数回调。",
        ["@Bean 实现 Function<I,O> 接口，方法名即函数名", "@JsonPropertyDescription 描述参数，帮助 LLM 理解", ".functions(\"beanName\") 注册到 ChatClient", "Spring AI 自动处理 JSON 序列化和方法调用", "面试常考：Function Calling 流程、参数描述、多工具调用"]
    ),
}

file_maps[r"02-后端开发\Java AIGC应用开发知识点系统梳理_优化版.md"] = {
    "## 7.6 内容水印与溯源": (
        "AIGC 内容水印在生成内容中嵌入不可见标记，用于溯源和鉴别 AI 生成内容。",
        "文本水印：在生成时调整特定 token 的选择概率（如 Green List 方案），检测时统计这些 token 出现频率判断是否 AI 生成。图片水印：扩散模型在潜空间嵌入信号，或在 DCT 频域添加不可见标记。音频水印：在频谱中嵌入编码。溯源通过提取水印追踪生成模型和时间。国内《生成式 AI 服务管理暂行办法》要求对 AI 生成内容添加标识。",
        ["文本水印：Green/Red List token 选择偏置，不影响可读性", "图片水印：扩散模型 latent space 嵌入或频域水印", "法规要求：AI 生成内容必须显式+隐式标识", "水印鲁棒性：抗裁剪/压缩/编辑，仍可检测", "面试常考：水印原理、合规要求、检测方法"]
    ),
    "## 7.7 AIGC 版权合规要点": (
        "AIGC 版权涉及训练数据合法性、生成内容归属和侵权风险，是企业应用必须关注的合规问题。",
        "训练数据：受版权保护的作品用于训练是否构成侵权尚无定论（合理使用 vs 侵权），国内要求训练数据来源合法。生成内容：AI 生成内容的著作权归属存争议（中国法院有案例认定人类智力投入部分可受保护）。侵权风险：生成内容与已有作品实质性相似可能侵权。合规措施：使用授权数据训练、加入侵权检测、用户协议明确权利归属、保留生成记录。",
        ["训练数据需合法来源，避免爬取受版权保护内容", "生成内容著作权：人类有智力投入才可能受保护", "侵权检测：比对生成内容与已有作品相似度", "用户协议明确生成内容权利归属和责任", "面试常考：AIGC 版权争议、训练数据合规、内容归属"]
    ),
}

# ============ 04-分布式与中间件 ============
file_maps[r"04-分布式与中间件\分布式锁知识点系统梳理_优化版.md"] = {
    "### 2.1 基础实现（SETNX）": (
        "Redis SETNX 是最基础的分布式锁实现，利用 key 不存在时才设置成功的原子操作保证互斥。",
        "SET key value NX EX 30：NX 保证 key 不存在时才设置（互斥），EX 设置过期时间（防死锁）。value 必须是唯一标识（UUID+线程ID），释放锁时用 Lua 脚本先判断 value 再删除（避免误删他人锁）。SETNX 缺陷：不可重入、锁续期需手动、主从切换可能丢锁（RedLock 争议）。",
        ["SET key value NX EX seconds 原子加锁，不用 SETNX+EXPIRE 两条命令", "value 用 UUID 唯一标识，释放时 Lua 脚本比对后删除", "过期时间需大于业务执行时间，或用看门狗自动续期", "Redisson 封装了可重入锁、看门狗、联锁等高级特性", "面试常考：SETNX 原子性、value 唯一标识、Lua 释放、锁续期"]
    ),
}

file_maps[r"04-分布式与中间件\微服务核心组件知识点系统梳理_优化版.md"] = {
    "### 2.1 Nacos（推荐）": (
        "Nacos 是 Spring Cloud Alibaba 首选注册中心，同时支持服务发现和配置管理，兼容 AP/CP。",
        "服务注册：微服务启动时 Nacos Client 注册实例（IP/端口/元数据），心跳 5s 续约，15s 不健康 30s 摘除。临时实例用 Distro（AP），持久实例用 Raft（CP）。消费者本地缓存服务列表，10s 轮询更新。Spring Cloud LoadBalancer 做客户端负载均衡。相比 Eureka，Nacos 支持配置中心、更活跃的社区和 K8s 集成。",
        ["spring-cloud-starter-alibaba-nacos-discovery 引入", "临时实例 AP（Distro），持久实例 CP（Raft）", "心跳续约+本地缓存，Nacos 宕机仍可消费", "Nacos 同时是配置中心，一组件两用", "面试常考：Nacos vs Eureka、AP/CP、心跳机制"]
    ),
    "### 3.1 Nacos Config": (
        "Nacos Config 提供分布式配置管理，支持配置热更新、环境隔离和灰度发布。",
        "bootstrap.yml 配置 Nacos 地址和 namespace/group/dataId。应用启动时从 Nacos 拉取配置，长轮询监听变更（默认 30s），配置变更后推送通知。@RefreshScope 标注的 Bean 在配置变更时自动刷新。多环境用 namespace 隔离（dev/prod），group 区分项目，dataId 对应应用名+profile+扩展名。",
        ["spring-cloud-starter-alibaba-nacos-config 引入", "bootstrap.yml 配置 server-addr/namespace/group/file-extension", "@RefreshScope + @Value 实现配置热更新", "长轮询（Long Polling）30s 监听变更，近实时推送", "面试常考：配置热更新原理、namespace/group/dataId、长轮询"]
    ),
}

# ============ 05-云原生与运维 ============
file_maps[r"05-云原生与运维\Docker 知识点系统梳理_优化版.md"] = {
    "### 3.1 镜像命令": (
        "Docker 镜像命令涵盖拉取、查看、构建、删除和导出导入，是镜像生命周期管理的基础。",
        "docker pull 拉取镜像（默认 Docker Hub，可指定 registry）；docker images 列出本地镜像；docker build -t name:tag . 根据 Dockerfile 构建；docker rmi 删除镜像（-f 强制）；docker tag 打标签；docker save/load 导出导入镜像为 tar 文件；docker history 查看镜像层历史。镜像由多层只读层组成，构建时利用层缓存加速。",
        ["docker pull nginx:1.25 拉取指定版本，不写 tag 默认 latest", "docker build -t myapp:v1 . 末尾的 . 是构建上下文", "docker rmi $(docker images -q) 批量删除", "docker save -o img.tar myapp:v1 导出，docker load -i 导入", "面试常考：镜像分层原理、构建缓存、多阶段构建减小镜像"]
    ),
    "### 3.2 容器命令": (
        "Docker 容器命令管理容器的启动、停止、进入、日志和生命周期。",
        "docker run 启动容器（-d 后台、-p 端口映射、-v 挂载、--name 命名、-e 环境变量、--rm 退出自动删除）；docker ps 查看运行中容器（-a 含已停止）；docker stop/start/restart 控制容器；docker exec -it <id> bash 进入运行中容器；docker logs -f 查看日志；docker rm 删除容器（-f 强制删除运行中）；docker cp 在容器和宿主机间复制文件。",
        ["docker run -d -p 8080:80 --name web nginx", "docker exec -it <id> /bin/sh（Alpine 镜像用 sh 不是 bash）", "docker logs -f --tail 100 <id> 实时查看日志", "docker rm -f <id> 强制删除运行中的容器", "面试常考：run 参数、exec vs attach、容器日志查看"]
    ),
    "### 3.3 其他": (
        "Docker 其他常用命令包括系统清理、信息查看、网络和卷管理等运维操作。",
        "docker system df 查看磁盘占用；docker system prune -a 清理无用镜像/容器/网络/卷（释放磁盘）；docker info 查看 Docker 系统信息；docker inspect <id> 查看容器/镜像详细配置（JSON）；docker stats 实时监控容器资源使用（CPU/内存/网络/IO）；docker events 查看实时事件流。",
        ["docker system prune -a --volumes 彻底清理（谨慎）", "docker inspect <id> | grep IPAddress 查容器 IP", "docker stats 实时资源监控，类似 top", "docker info 查看存储驱动、运行时等系统信息", "面试常考：磁盘清理、inspect 用法、资源监控"]
    ),
    "### 4.2 示例": (
        "Dockerfile 示例演示从基础镜像到应用镜像的完整构建流程，包含多阶段构建最佳实践。",
        "典型 Java 应用 Dockerfile：FROM eclipse-temurin:17-jre 基础镜像；WORKDIR /app 设置工作目录；COPY target/*.jar app.jar 复制 JAR；EXPOSE 8080 声明端口；ENTRYPOINT [\"java\",\"-jar\",\"app.jar\"] 启动命令。多阶段构建：第一阶段 maven 构建，第二阶段只 COPY JAR 到 JRE 镜像，避免构建工具进入最终镜像。.dockerignore 排除 target/.git 等。",
        ["多阶段构建：builder 阶段编译，final 阶段只 COPY 产物", "用 JRE 而非 JDK 基础镜像减小体积", "ENTRYPOINT 用 exec 形式（JSON 数组），正确接收信号", ".dockerignore 排除无关文件，加速构建", "面试常考：多阶段构建、CMD vs ENTRYTRYPOINT、镜像瘦身"]
    ),
    "### 5.1 三种挂载方式": (
        "Docker 数据挂载有三种方式：volume（Docker 管理）、bind mount（宿主机路径）、tmpfs（内存）。",
        "Volume：docker volume create 创建，存储在 /var/lib/docker/volumes/，Docker 管理生命周期，适合数据库数据持久化和容器间共享。Bind mount：-v /host/path:/container/path 直接挂载宿主机目录，适合开发时挂载源码和配置。Tmpfs：--tmpfs /path 挂载到内存，容器停止数据消失，适合敏感临时数据。",
        ["Volume 最安全可移植，Docker 管理，适合生产数据持久化", "Bind mount 直接映射宿主机路径，适合开发环境", "Tmpfs 数据在内存中，适合密码/密钥等敏感临时数据", "-v 和 --mount 都可挂载，--mount 语法更明确", "面试常考：三种挂载区别、volume 位置、bind mount 风险"]
    ),
    "### 6.2 自定义网络": (
        "Docker 自定义网络让容器间通过容器名互相访问，提供 DNS 解析和网络隔离。",
        "docker network create mynet 创建 bridge 网络；docker run --network mynet 将容器加入网络。同一自定义网络中的容器可以通过容器名互相访问（Docker 内置 DNS 解析），而默认 bridge 网络只能通过 IP 访问。自定义网络支持 --subnet 指定子网、--driver 选择驱动（bridge/overlay/macvlan）。容器可连接多个网络。",
        ["docker network create mynet 创建自定义 bridge 网络", "同一网络内容器名自动 DNS 解析，无需 --link", "docker network connect/disconnect 动态连接/断开网络", "overlay 网络用于 Swarm 多主机容器通信", "面试常考：自定义网络 DNS、bridge vs overlay、容器间通信"]
    ),
}

file_maps[r"05-云原生与运维\Nginx 知识点系统梳理_优化版.md"] = {
    "### 7.1 请求限流（limit_req）": (
        "Nginx limit_req 基于漏桶算法限制请求速率，防止突发流量压垮后端服务。",
        "limit_req_zone 定义限流区域（key=二进制IP、zone名称、共享内存大小、rate 速率）。limit_req zone=name burst=N nodelay 在 location 中启用：rate 限制平均速率（如 10r/s），burst 允许突发请求数排队，nodelay 突发请求立即处理不延迟。超出 burst 的请求返回 503。还可用 limit_conn 限制并发连接数。",
        ["limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s 在 http 块定义", "limit_req zone=api burst=20 nodelay 在 location 启用", "burst 是排队容量，nodelay 让突发请求立即处理", "limit_conn 限制并发连接数，limit_req 限制速率", "面试常考：漏桶算法、burst/nodelay、503 处理"]
    ),
}

# ============ 06-计算机基础 ============
file_maps[r"06-计算机基础\HTTP 协议深度解析_优化版.md"] = {
    "### 4.2 响应结构": (
        "HTTP 响应由状态行、响应头、空行和响应体四部分组成，状态行包含版本、状态码和原因短语。",
        "状态行：HTTP/1.1 200 OK（版本+状态码+原因短语）。响应头：Content-Type/Content-Length/Set-Cookie/Cache-Control 等。空行（\\r\\n）分隔头部和主体。响应体：HTML/JSON/图片等资源。状态码分类：1xx 信息、2xx 成功、3xx 重定向、4xx 客户端错误、5xx 服务端错误。",
        ["状态行：HTTP版本 + 状态码 + 原因短语", "2xx 成功（200/201/204），3xx 重定向（301/302/304）", "4xx 客户端错误（400/401/403/404），5xx 服务端错误（500/502/503）", "响应头和响应体之间用空行分隔", "面试常考：状态码含义、301 vs 302、401 vs 403"]
    ),
    "### 5.3 响应 Header": (
        "HTTP 响应头控制缓存、内容类型、跨域、Cookie 和安全策略，是服务端指令的传递载体。",
        "Content-Type：响应体 MIME 类型（application/json; charset=utf-8）。Cache-Control：缓存策略（max-age/no-cache/no-store）。Set-Cookie：下发 Cookie（含 HttpOnly/Secure/SameSite）。Access-Control-Allow-Origin：CORS 跨域允许。Content-Encoding：压缩编码（gzip/br）。Strict-Transport-Security：强制 HTTPS。X-Content-Type-Options：nosniff 防 MIME 嗅探。",
        ["Content-Type 指定媒体类型和字符集", "Cache-Control: max-age=31536000 强缓存，no-cache 协商缓存", "Set-Cookie 加 HttpOnly/Secure/SameSite 防 XSS/CSRF", "CORS 相关：Allow-Origin/Allow-Methods/Allow-Headers", "面试常考：缓存头、安全头、CORS 头、Content-Type"]
    ),
    "### 9.3 简单请求 vs 预检请求": (
        "CORS 将请求分为简单请求和预检请求，预检请求用 OPTIONS 方法询问服务端是否允许实际请求。",
        "简单请求需同时满足：方法为 GET/POST/HEAD；Content-Type 仅限 application/x-www-form-urlencoded/multipart/form-data/text/plain；无自定义头。简单请求直接发送，服务端返回 Access-Control-Allow-Origin 即可。不满足条件的请求（如 application/json、PUT/DELETE、自定义头）先发 OPTIONS 预检请求，服务端返回允许的方法/头/有效期，预检通过后才发实际请求。",
        ["简单请求：GET/POST/HEAD + 三种 Content-Type + 无自定义头", "预检请求：OPTIONS 方法，询问 Access-Control-Request-Method/Headers", "预检通过后才发实际请求，增加一次 RTT", "Access-Control-Max-Age 缓存预检结果，减少 OPTIONS 请求", "面试常考：简单请求条件、预检流程、OPTIONS 优化"]
    ),
}

# ============ 07-通用工具 ============
file_maps[r"07-通用工具\Git 版本控制知识点系统梳理_优化版.md"] = {
    "### 3.1 基础操作": (
        "Git 基础操作覆盖工作区→暂存区→本地仓库→远程仓库的完整提交流程。",
        "git init 初始化仓库；git clone 克隆远程仓库。git add 将工作区修改加入暂存区（git add . 添加所有）。git commit -m \"message\" 将暂存区提交到本地仓库。git push 将本地提交推送到远程。git pull = git fetch + git merge，拉取远程更新并合并。git status 查看工作区状态，git diff 查看修改内容。",
        ["工作区→暂存区（add）→本地仓库（commit）→远程（push）", "git add -p 交互式暂存，可只暂存部分修改", "git commit --amend 修改最后一次提交（未 push 时）", "git push -u origin main 首次推送并设置上游分支", "面试常考：三个区域、add/commit/push 流程、pull vs fetch"]
    ),
    "### 3.2 撤销操作": (
        "Git 撤销操作针对工作区、暂存区和提交历史分别提供不同命令，需注意已推送提交的安全撤销。",
        "工作区撤销：git checkout -- <file> 或 git restore <file> 丢弃工作区修改。暂存区撤销：git reset HEAD <file> 或 git restore --staged <file> 取消暂存。修改最后提交：git commit --amend（未 push）。回退提交：git reset --soft/mixed/hard（未 push）；已 push 用 git revert 创建反向提交（安全，不改写历史）。",
        ["git restore <file> 丢弃工作区修改（不可恢复）", "git restore --staged <file> 取消暂存，保留工作区修改", "git reset --hard 彻底回退（慎用，会丢失修改）", "已推送的提交用 git revert，不用 reset --force", "面试常考：reset 三种模式、revert vs reset、amend"]
    ),
    "### 5.3 冲突解决": (
        "Git 合并冲突发生在两个分支修改同一文件同一位置时，需手动编辑解决后标记完成。",
        "git merge/rebase 时冲突，Git 在文件中标记 <<<<<<< HEAD（当前分支）、=======、>>>>>>> branch（合入分支）。手动编辑保留正确内容，删除冲突标记，git add 标记已解决，git commit（merge）或 git rebase --continue（rebase）完成。工具：VSCode/IDEA 内置冲突解决器可视化三窗格合并。预防：频繁拉取主分支、小颗粒提交、沟通避免改同一文件。",
        ["冲突标记：<<<<<<< HEAD / ======= / >>>>>>> branch", "手动编辑后 git add + git commit 完成 merge", "rebase 冲突：git add 后 git rebase --continue", "git mergetool 启动可视化合并工具", "面试常考：冲突原因、解决流程、merge vs rebase 冲突处理"]
    ),
    "### 9.1 .gitignore": (
        ".gitignore 指定不需要纳入版本控制的文件模式，避免构建产物、密钥和 IDE 文件进入仓库。",
        "在仓库根目录创建 .gitignore，每行一个模式：精确文件名（.env）、通配符（*.log、target/、node_modules/）、取反（!important.log）。全局忽略：git config --global core.excludesfile ~/.gitignore_global。注意：已被跟踪的文件不会因 .gitignore 而忽略，需先 git rm --cached <file> 移除跟踪。",
        ["target/、node_modules/、__pycache__/ 忽略构建产物", ".env、*.key 忽略密钥和配置文件", "*.log、*.tmp 忽略临时文件", "已跟踪文件需 git rm --cached 后 .gitignore 才生效", "面试常考：.gitignore 语法、已跟踪文件忽略、全局忽略"]
    ),
}

# ============ 08-Python全栈 ============
file_maps[r"08-Python全栈\Python Web开发框架知识点系统梳理_优化版.md"] = {
    "### 2.5 Admin 后台": (
        "Django Admin 是内置的后台管理系统，自动根据模型生成 CRUD 界面，极少代码即可管理数据。",
        "创建超级用户 python manage.py createsuperuser，在 admin.py 中 admin.site.register(Model) 注册模型即可管理。ModelAdmin 自定义列表显示（list_display）、搜索（search_fields）、过滤（list_filter）、分页（list_per_page）、只读字段（readonly_fields）、内联编辑（inlines）。Admin 的权限体系基于 User/Group/Permission，可控制模型级和对象级访问。",
        ["admin.site.register(Model, ModelAdmin) 注册并自定义", "list_display 控制列表列，search_fields 搜索，list_filter 过滤", "inlines 实现关联模型在同一页面编辑", "createsuperuser 创建管理员，权限基于 Group 分配", "面试常考：Admin 定制、权限控制、ModelAdmin 常用配置"]
    ),
    "### 4.5.3 认证与权限": (
        "DRF 认证与权限分离：认证确定用户身份，权限决定是否允许操作，支持多种认证方案和权限类。",
        "认证类：SessionAuthentication（浏览器）、TokenAuthentication（Token 头）、JWTAuthentication（djangorestframework-simplejwt）、BasicAuthentication。权限类：IsAuthenticated（已登录）、IsAdminUser（管理员）、IsAuthenticatedOrReadOnly（认证可写/匿名只读）、DjangoModelPermissions（Django 模型权限）。自定义权限继承 BasePermission 重写 has_permission/has_object_permission。",
        ["认证（Authentication）识别身份，权限（Permission）决定访问", "JWT 用 djangorestframework-simplejwt，access/refresh token", "全局默认在 DEFAULT_AUTHENTICATION_CLASSES 配置", "视图级用 permission_classes = [IsAuthenticated] 覆盖", "面试常考：认证 vs 权限、JWT 流程、自定义权限"]
    ),
    "## 4.7 WebSocket 实时通信": (
        "Python Web 框架通过 Channels（Django）、Flask-SocketIO、FastAPI WebSocket 支持实时双向通信。",
        "Django Channels 替换 WSGI 为 ASGI，通过 channel layer（Redis）实现跨进程消息传递，消费者（Consumer）处理 WebSocket 连接。Flask-SocketIO 基于 python-socketio，支持房间和命名空间。FastAPI 原生支持 WebSocket（from fastapi import WebSocket），async def 处理收发。生产部署用 Daphne/Uvicorn（ASGI 服务器）。",
        ["Django Channels：ASGI + channel layer（Redis）+ Consumer", "FastAPI 原生 WebSocket：async def ws(websocket: WebSocket)", "Flask-SocketIO：@socketio.on + room 广播", "ASGI 服务器（Daphne/Uvicorn）替代 WSGI 支持长连接", "面试常考：ASGI vs WSGI、Channels 架构、WebSocket 鉴权"]
    ),
    "## 4.8 认证授权体系": (
        "Python Web 认证体系涵盖 Session/Cookie、Token/JWT、OAuth2 和 RBAC 权限模型。",
        "Session 认证：服务端存 Session，Cookie 带 sessionid，Django/Flask 原生支持。Token 认证：无状态，Authorization: Bearer <token>，适合前后端分离和 API。JWT：Header.Payload.Signature，Payload 含用户信息和过期时间，签名防篡改。OAuth2：第三方登录授权码模式。RBAC：用户-角色-权限三级模型，Django Auth 内置 Group/Permission。",
        ["Session 有状态适合 Web，JWT 无状态适合 API/微服务", "JWT 三部分：Header.Payload.Signature，Payload 不加密勿存敏感信息", "OAuth2 授权码模式用于第三方登录", "RBAC：用户→角色→权限，Django auth 内置支持", "面试常考：Session vs JWT、JWT 结构、OAuth2 流程、RBAC"]
    ),
    "## 4.9 其他 Web 框架": (
        "Python 生态还有 Tornado（异步）、Sanic（高性能异步）、Starlette（ASGI 工具包）、Bottle（单文件）等框架。",
        "Tornado：Facebook 开源，自带异步 IOLoop 和 WebSocket，适合长轮询/长连接，但生态较小。Sanic：类 Flask API + async/await，高性能 ASGI 框架，支持 WebSocket。Starlette：FastAPI 的底层框架，轻量 ASGI 工具包，可独立使用。Bottle：单文件微框架，适合小型工具。选型：FastAPI（新项目 API 首选）、Django（全栈/管理后台）、Flask（轻量灵活）。",
        ["Tornado：异步+WebSocket，适合长连接场景", "Sanic：Flask 风格 + async，高性能", "Starlette：FastAPI 底层，轻量 ASGI 工具包", "选型：FastAPI（API）、Django（全栈）、Flask（轻量）", "面试常考：框架对比、ASGI 框架、选型依据"]
    ),
}

file_maps[r"08-Python全栈\Python中间件与异步任务知识点系统梳理_优化版.md"] = {
    "### 2.4 Worker 启动": (
        "Celery Worker 是执行任务的进程，启动参数控制并发数、队列、日志和自动重载。",
        "celery -A proj worker --loglevel=info 启动 Worker。-c/--concurrency 并发数（默认 CPU 核数，prefork 模式）；-Q 指定监听的队列；--autoscale=max,min 自动伸缩；-n 设置节点名；--logfile 指定日志文件。生产环境用 systemd/supervisor 管理 Worker 进程，多队列时启动多个 Worker 分别消费不同队列实现任务隔离。",
        ["celery -A proj worker -l info 启动，-A 指定 Celery 实例", "-c 4 设置 prefork 并发数，-P gevent 用协程池", "-Q queue1,queue2 指定监听队列", "--autoscale=10,3 自动伸缩 3-10 进程", "面试常考：Worker 启动参数、并发模式、多队列隔离"]
    ),
    "## 2.5 Celery 高级原语（任务编排）": (
        "Celery 原语（chain/group/chord/chain）实现任务编排，支持串行、并行、分组和回调。",
        "chain：任务串行执行，前一个结果作为后一个参数（chain(task1.s(), task2.s())()）。group：任务并行执行，返回 GroupResult（group(task.s(i) for i in range(10))()）。chord：group 执行完后执行回调（chord(header)(callback)），类似 MapReduce。chunks：大批量任务分块。这些原语可组合成复杂工作流，结果通过 ResultBackend 持久化。",
        ["chain 串行：A→B→C，前一个返回值传给后一个", "group 并行：多个任务同时执行，收集所有结果", "chord = group + callback，并行完成后执行汇总", "原语可嵌套组合成复杂 DAG 工作流", "面试常考：chain/group/chord 区别、工作流编排、结果获取"]
    ),
    "### 2.6 任务优先级与路由": (
        "Celery 任务路由将不同任务分发到不同队列，配合 Worker 实现优先级和资源隔离。",
        "task_routes 配置任务到队列的映射（如 task.add → queue:high-priority）。任务优先级：RabbitMQ/Redis 支持队列优先级（x-max-priority），apply_async(priority=0-9) 设置任务优先级。多队列架构：high/default/low 三级队列，分别启动 Worker，high 队列分配更多并发。定时任务和实时任务分到不同队列避免互相影响。",
        ["task_routes 将任务路由到指定队列", "RabbitMQ 支持 priority，Redis 优先级支持有限", "多队列+多 Worker 实现资源隔离和优先级", "apply_async(queue='high', priority=9) 指定队列和优先级", "面试常考：任务路由配置、优先级实现、多队列架构"]
    ),
    "## 4.5 APScheduler（独立定时任务）": (
        "APScheduler 是 Python 独立定时任务库，支持 cron/间隔/日期触发器，可嵌入应用或独立运行。",
        "四大组件：Scheduler（调度器：BackgroundScheduler/BlockingScheduler）、Trigger（触发器：CronTrigger/IntervalTrigger/DateTrigger）、JobStore（任务存储：内存/SQLAlchemy/MongoDB）、Executor（执行器：线程池/进程池）。@scheduler.scheduled_job('cron', hour=2) 添加任务。支持任务持久化（重启不丢失）、错过任务补偿（misfire_grace_time）和最大并发实例控制。",
        ["BackgroundScheduler 后台运行，BlockingScheduler 阻塞主线程", "CronTrigger 类似 Linux cron，IntervalTrigger 固定间隔", "JobStore 持久化到数据库，重启后任务不丢失", "misfire_grace_time 处理错过的任务，coalesce 合并错过的执行", "面试常考：APScheduler 组件、触发器类型、与 Celery Beat 区别"]
    ),
    "## 4.6 asyncio 事件循环原理": (
        "asyncio 事件循环是单线程协作式并发核心，通过 IO 多路复用和回调调度实现高并发。",
        "事件循环（Event Loop）不断从就绪队列取出任务执行，遇到 await（协程挂起点）时将控制权交还循环，去执行其他就绪任务。底层用 selector（epoll/kqueue/IOCP）监听 IO 事件，IO 就绪后唤醒对应协程。协程在单线程内切换，无锁但不能有阻塞调用（time.sleep 会阻塞整个循环）。async/await 是语法糖，协程对象由事件循环驱动。",
        ["单线程+IO多路复用（epoll），协作式调度", "await 是挂起点，遇到 await 交还控制权给事件循环", "阻塞调用（requests/time.sleep）会卡住整个循环，用 aiohttp/asyncio.sleep", "asyncio.gather 并发执行多个协程", "面试常考：事件循环原理、协程 vs 线程、await 机制、selector"]
    ),
}

file_maps[r"08-Python全栈\Python全栈前端集成知识点系统梳理_优化版.md"] = {
    "## 6.1 WebSocket 实时通信": (
        "Python 后端通过 WebSocket 实现服务端主动推送，适用于聊天、通知、实时数据和协同编辑。",
        "FastAPI 原生 WebSocket：async def ws_endpoint(websocket: WebSocket)，await websocket.accept()/receive_text()/send_text()。Django Channels 用 Consumer 处理连接，channel layer（Redis）支持跨进程广播。Flask-SocketIO 用 @socketio.on。生产需 ASGI 服务器（Uvicorn/Daphne），Nginx 配置 Upgrade/Connection 头支持 WebSocket 代理。",
        ["FastAPI 原生 WebSocket，Django Channels（ASGI）", "Redis channel layer 实现跨进程广播和房间", "Nginx 需配置 proxy_set_header Upgrade $http_upgrade", "WebSocket 鉴权：连接时 token 校验（query 参数或子协议）", "面试常考：WebSocket vs SSE、ASGI 部署、广播实现"]
    ),
    "## 6.2 文件上传与下载": (
        "Python Web 文件上传处理 multipart/form-data，下载通过 FileResponse/Streaming 实现大文件流式传输。",
        "FastAPI：UploadFile 接收上传文件（await file.read() 读取，file.file 是 SpooledTemporaryFile 假脱机到磁盘）。Django：request.FILES 获取文件，FileSystemStorage 保存。下载：FastAPI FileResponse（支持断点续传）或 StreamingResponse（流式生成）。大文件上传用分片上传，下载用 StreamingResponse 分块读取避免内存溢出。",
        ["FastAPI UploadFile 自动假脱机到磁盘，不占内存", "Django request.FILES['file'] 获取上传文件", "FileResponse 自动处理 Content-Length 和断点续传", "StreamingResponse 分块流式传输大文件/动态生成内容", "面试常考：大文件上传、流式下载、断点续传、内存控制"]
    ),
    "## 6.3 国际化（i18n）": (
        "Python Web 国际化通过 gettext 提取翻译字符串，配合中间件根据用户语言切换 locale。",
        "Django：USE_I18N=True，{% trans \"text\" %} 或 gettext_lazy 标记字符串，django-admin makemessages -l zh_Hans 生成 .po 文件，compilemessages 编译为 .mo。FastAPI：使用 babel 库，gettext 标记，babel extract/init/compile 流程。语言检测：Accept-Language 头、URL 前缀（/zh/、/en/）或 Cookie。",
        ["gettext_lazy 延迟翻译（模型/表单定义时用），gettext 即时翻译", "makemessages 提取 .po，compilemessages 编译 .mo", "LocaleMiddleware 根据 Accept-Language/URL 切换语言", "FastAPI 用 Babel 库，中间件设置 locale", "面试常考：i18n 流程、gettext、.po/.mo、语言检测"]
    ),
    "## 6.4 SEO 优化": (
        "Python Web SEO 包括 SSR/模板渲染、sitemap、robots.txt、结构化数据和元标签优化。",
        "Django/Flask/Jinja2 服务端渲染（SSR）对搜索引擎友好（SPA 需 prerender 或 SSR）。sitemap.xml：Django 自带 sitemaps 框架，FastAPI 动态生成。robots.txt 控制爬取范围。语义化 HTML、meta description/og 标签、结构化数据（JSON-LD）提升搜索展现。URL 设计语义化（/articles/python-asyncio 而非 /article?id=1）。",
        ["服务端渲染（Jinja2/Django Template）比 SPA 更利于 SEO", "sitemap.xml 动态生成，robots.txt 控制爬取", "meta description/og 标签、JSON-LD 结构化数据", "语义化 URL 和面包屑导航", "面试常考：SSR vs CSR for SEO、sitemap、meta 标签"]
    ),
    "## 6.5 SSE（Server-Sent Events）": (
        "SSE 是服务端单向推送协议，基于 HTTP，比 WebSocket 轻量，适合通知/日志流/AI 流式输出。",
        "SSE 使用 text/event-stream Content-Type，服务端持续发送 data: 内容\\n\\n 格式的事件。浏览器用 EventSource API 接收（自动重连）。FastAPI 返回 StreamingResponse 生成器，media_type='text/event-stream'。相比 WebSocket：SSE 单向（服务端→客户端）、基于 HTTP 无需特殊协议、自动重连、支持自定义事件类型。LLM 流式输出（打字机效果）是典型场景。",
        ["Content-Type: text/event-stream，data: 消息\\n\\n 格式", "EventSource 浏览器 API，自动重连，比 WebSocket 简单", "FastAPI StreamingResponse + 生成器实现", "单向推送，适合通知/日志/AI 流式响应", "面试常考：SSE vs WebSocket、event-stream、自动重连"]
    ),
}

file_maps[r"08-Python全栈\Python安全防护知识点系统梳理_优化版.md"] = {
    "### 3.3 代码注入": (
        "代码注入通过 eval/exec/pickle 等危险函数执行恶意代码，Python 中需严格避免执行用户可控输入。",
        "eval/exec 执行用户输入可直接执行任意代码（eval(\"__import__('os').system('rm -rf /')\")）。pickle/yaml.load 反序列化恶意数据可执行任意代码（__reduce__ 魔术方法）。模板注入（SSTI）：Jinja2 render_template_string(user_input) 可执行 {{ config }} 或 {{ ''.__class__.__mro__ }}。防护：禁用 eval/exec、用 ast.literal_eval 替代 eval、yaml.safe_load、模板用 render_template 而非字符串拼接、沙箱隔离。",
        ["禁用 eval/exec 处理用户输入，用 ast.literal_eval 替代", "pickle/yaml.load 可执行任意代码，用 yaml.safe_load", "Jinja2 SSTI：render_template_string 拼接用户输入可 RCE", "subprocess 用列表参数不用 shell=True，避免命令注入", "面试常考：eval 危险、pickle 反序列化、SSTI、防护措施"]
    ),
    "## 8.1 SSRF（服务端请求伪造）": (
        "SSRF 让服务端请求攻击者指定的 URL，可访问内网服务、云元数据或本地文件，造成内网穿透。",
        "应用根据用户输入发起 HTTP 请求（如 URL 预览、Webhook、图片下载），攻击者传入 http://169.254.169.254/latest/meta-data/（云元数据）、http://localhost:6379（内网 Redis）、file:///etc/passwd。防护：URL 白名单（只允许指定域名）、禁止内网 IP（10./172.16-31./192.168./127./169.254.）、禁止 file/gopher 协议、DNS 重绑定防护（解析后校验 IP）、最小权限网络策略。",
        ["风险：访问云元数据（窃取密钥）、内网服务、本地文件", "白名单限制目标域名，禁止内网 IP 段", "禁用 file://、gopher:// 等非 HTTP 协议", "DNS 重绑定：先解析 DNS 再校验 IP，连接前再校验", "面试常考：SSRF 原理、云元数据攻击、防护措施"]
    ),
    "## 8.2 不安全的反序列化": (
        "不安全的反序列化（pickle/marshal/shelve）可导致远程代码执行，是 Python 特有的高危漏洞。",
        "pickle.loads 反序列化时调用对象的 __reduce__ 方法，攻击者构造恶意 pickle 数据即可执行任意系统命令。PyYAML 的 yaml.load 同样危险（!!python/object/apply:os.system）。shelve 基于 pickle。JSON 反序列化安全（只解析数据）。防护：永远不要反序列化不可信数据、用 JSON 替代 pickle、必须用 pickle 时用 hmac 签名验证、yaml.safe_load。",
        ["pickle.loads 不可信数据 = RCE（__reduce__ 执行任意命令）", "yaml.load 同样危险，必须用 yaml.safe_load", "JSON 反序列化安全，跨语言数据交换用 JSON", "必须用 pickle 时用 hmac 签名确保数据未被篡改", "面试常考：pickle RCE、__reduce__、安全替代方案"]
    ),
    "## 8.3 依赖漏洞扫描": (
        "依赖漏洞扫描检查第三方库的已知 CVE，是供应链安全的基础实践。",
        "工具：pip-audit（PyPA 官方，扫描 requirements.txt 已知漏洞）、safety（免费数据库）、Dependabot/Renovate（GitHub 自动 PR 更新）、Snyk（商业，多语言）。CI 中集成 pip-audit 阻断高危漏洞。定期更新依赖（pip install --upgrade），关注 PyPA 安全公告。最小化依赖：不用的库不安装，减少攻击面。",
        ["pip-audit -r requirements.txt 扫描已知漏洞", "safety check 另一个免费扫描工具", "Dependabot/Renovate 自动提交依赖更新 PR", "CI 集成扫描，高危漏洞阻断构建", "面试常考：供应链安全、pip-audit、依赖更新策略"]
    ),
    "## 8.4 速率限制与防暴力破解": (
        "速率限制限制单位时间内请求次数，防止暴力破解、撞库和 CC 攻击。",
        "slowapi（FastAPI，基于 limits 库）：@limiter.limit(\"5/minute\") 装饰器。Django：django-ratelimit。Flask：Flask-Limiter。策略：固定窗口（简单但有临界问题）、滑动窗口（更平滑）、令牌桶（允许突发）。登录接口额外限制：同 IP 5次/分钟、同账号锁定/验证码、失败计数。Redis 实现分布式限流（INCR + EXPIRE 或令牌桶 Lua 脚本）。",
        ["slowapi（FastAPI）/django-ratelimit/Flask-Limiter", "登录接口：IP+账号双维度限流，失败锁定+验证码", "Redis INCR+EXPIRE 实现固定窗口，Lua 脚本保证原子性", "滑动窗口/令牌桶比固定窗口更精确", "面试常考：限流算法、登录防爆破、Redis 限流实现"]
    ),
    "## 8.5 目录遍历与路径安全": (
        "目录遍历通过 ../ 或绝对路径访问未授权文件，文件操作必须校验和规范化路径。",
        "用户传入文件名（如 ?file=../../etc/passwd），服务端直接 open 拼接路径导致读取任意文件。防护：os.path.realpath 规范化路径后校验是否在允许目录内（os.path.commonpath）；用白名单限定可访问文件；Flask send_from_directory 内置安全检查；Django FileResponse 不允许路径穿越；禁止用户直接控制文件路径。",
        ["风险：?file=../../../etc/passwd 读取系统文件", "os.path.realpath 规范化后校验是否在 BASE_DIR 内", "send_from_directory / FileResponse 内置路径安全检查", "白名单限定可访问文件，不用用户输入直接拼接路径", "面试常考：目录遍历原理、路径规范化、防护方法"]
    ),
    "## 8.6 JWT 安全细节": (
        "JWT 安全涉及密钥管理、算法选择、Token 存储和撤销机制，配置不当可导致认证绕过。",
        "风险：none 算法绕过（服务端未校验算法）、弱密钥（HS256 密钥可暴力破解）、Payload 未加密（Base64 可解码，勿存敏感信息）、Token 无法撤销（JWT 无状态，需黑名单/短有效期）。安全实践：强制 RS256/ES256 非对称算法、强密钥（≥256bit）、短 access token + refresh token、HTTPS 传输、HttpOnly Cookie 存储防 XSS、敏感操作重新认证。",
        ["禁用 none 算法，用 RS256/ES256 非对称签名", "Payload 是 Base64 不是加密，不能存密码/身份证", "短 access token（15min）+ refresh token，黑名单撤销", "Token 存 HttpOnly Cookie 防 XSS，不用 localStorage", "面试常考：JWT 安全风险、算法选择、撤销机制、存储方式"]
    ),
}

file_maps[r"08-Python全栈\Python性能优化知识点系统梳理_优化版.md"] = {
    "## 4.4 GIL 深度解析": (
        "GIL（全局解释器锁）是 CPython 的互斥锁，同一时刻只允许一个线程执行 Python 字节码，影响多线程 CPU 并行。",
        "GIL 存在原因：CPython 内存管理（引用计数）非线程安全，GIL 简化实现。影响：IO 密集型多线程有效（IO 等待时释放 GIL）；CPU 密集型多线程无法利用多核（甚至因锁竞争更慢），需用多进程（multiprocessing）或 C 扩展（NumPy/Cython 释放 GIL）。Python 3.2+ GIL 机制改进（时间片+竞争切换），但根本限制仍在。PEP 703（3.13 实验性 no-GIL）正在推进。",
        ["GIL 保证同一时刻只有一个线程执行 Python 字节码", "IO 密集型多线程有效（等待时释放 GIL）", "CPU 密集型用 multiprocessing 或 C 扩展绕过 GIL", "Python 3.13 实验性 free-threading（no-GIL，PEP 703）", "面试常考：GIL 原因、对多线程影响、绕过方法、PEP 703"]
    ),
    "## 4.5 协程 vs 线程 vs 进程深度对比": (
        "协程/线程/进程在并发模型、开销、GIL 影响和适用场景上各有不同，需按任务类型选择。",
        "进程：独立内存空间，开销最大（MB 级），真正并行（绕过 GIL），适合 CPU 密集。线程：共享内存，开销中等（KB 级栈），受 GIL 限制无法 CPU 并行，适合 IO 密集（阻塞 IO 释放 GIL）。协程：单线程内用户态切换，开销极小（KB 级），协作式调度，需 async/await 和异步库，适合高并发 IO（万级连接）。选型：CPU 密集→多进程，IO 密集→协程（高并发）或线程（简单）。",
        ["进程：独立内存，真并行，CPU 密集型，开销大", "线程：共享内存，受 GIL 限制，IO 密集型，中等开销", "协程：单线程协作式，超高并发 IO，需异步库，开销最小", "协程不能有阻塞调用，否则卡住整个事件循环", "面试常考：三者对比、GIL 影响、选型依据、切换开销"]
    ),
    "## 6.5 内存泄漏排查": (
        "Python 内存泄漏多由全局容器无限增长、循环引用、未关闭资源和 C 扩展泄漏导致，需用工具定位。",
        "常见原因：全局 list/dict/cache 无限追加（未设上限/LRU）；闭包/信号引用导致对象无法回收；未关闭的文件/连接/线程；C 扩展（numpy/pandas）内存未释放。排查工具：tracemalloc（标准库，对比快照定位分配位置）、memory_profiler（逐行内存）、objgraph（查找引用链）、pympler（对象统计）。修复：用 weakref、LRU cache 设上限、上下文管理器确保关闭、定期 gc.collect()。",
        ["tracemalloc 对比快照定位内存分配位置", "objgraph.show_backrefs 查找阻止回收的引用链", "全局缓存用 lru_cache(maxsize=N) 或 cachetools 设上限", "weakref 避免循环引用和长生命周期引用", "面试常考：泄漏原因、tracemalloc、引用链分析、修复方法"]
    ),
}

file_maps[r"08-Python全栈\Python接口设计与文档知识点系统梳理_优化版.md"] = {
    "## 7.3 API 限流（速率限制）": (
        "API 限流保护服务不被滥用，常用固定窗口、滑动窗口、令牌桶和漏桶算法，网关层统一实施。",
        "固定窗口：简单但窗口边界可能 2x 突发。滑动窗口：更精确，Redis ZSET 实现。令牌桶：固定速率生成令牌，请求消耗令牌，允许突发流量（适合 API）。漏桶：固定速率处理，平滑流量。实现：Redis + Lua（INCR/EXPIRE 固定窗口，ZSET 滑动窗口）；网关层（Nginx limit_req、Kong、Cloudflare）统一限流。响应头：X-RateLimit-Limit/Remaining/Reset。",
        ["令牌桶允许突发，漏桶平滑输出，API 常用令牌桶", "Redis + Lua 原子操作实现分布式限流", "网关层（Nginx/Kong）统一限流，比应用层更高效", "返回 429 Too Many Requests + Retry-After 头", "面试常考：限流算法对比、Redis 实现、429 响应"]
    ),
    "## 7.4 接口幂等性": (
        "幂等性保证同一请求执行一次和多次效果相同，是分布式系统重试和消息消费的安全基础。",
        "GET/PUT/DELETE 天然幂等，POST 不幂等。实现方案：① 唯一请求 ID（客户端生成 Request-Id，服务端去重表/Redis SETNX）② 数据库唯一索引（防重复插入）③ 状态机（只允许特定状态转换，重复请求被拒绝）④ 乐观锁（version 字段，UPDATE ... WHERE version=N）⑤ Token 令牌（先获取 token，提交时消耗）。支付/订单等关键接口必须幂等。",
        ["GET/PUT/DELETE 幂等，POST 需额外保证", "唯一请求 ID + Redis SETNX 去重，最常用方案", "数据库唯一索引/乐观锁 version 防重复写", "状态机限制重复操作（如已支付不能再支付）", "面试常考：幂等方案、唯一 ID、乐观锁、支付幂等"]
    ),
    "## 7.5 Webhook 设计": (
        "Webhook 是服务端主动回调客户端 HTTP 接口的事件通知机制，需处理签名验证、重试和幂等。",
        "客户端注册回调 URL，事件发生时服务端 POST JSON 到该 URL。关键设计：① 签名验证（HMAC-SHA256 签名请求体，X-Signature 头）② 重试机制（失败指数退避重试，5xx/超时重试，4xx 不重试）③ 幂等（Event-Id 去重）④ 超时设置（短超时 5-10s）⑤ 异步发送（不阻塞主流程）⑥ 事件版本化。",
        ["HMAC-SHA256 签名请求体，客户端验证防伪造", "失败指数退避重试（1s/2s/4s/8s/16s），最多 5 次", "Event-Id 幂等去重，客户端返回 2xx 确认", "异步发送+超时控制，不阻塞业务主流程", "面试常考：Webhook 签名、重试策略、幂等、异步"]
    ),
    "## 7.6 OAuth2 授权流程": (
        "OAuth2 授权码模式是第三方登录的标准流程，用户在授权服务器同意后，应用获取 access_token 访问资源。",
        "流程：① 用户点击第三方登录，重定向到授权服务器（client_id/redirect_uri/scope/state）② 用户登录并同意授权 ③ 授权服务器重定向回 redirect_uri?code=xxx ④ 后端用 code+client_secret 换取 access_token（POST /token）⑤ 用 access_token 调用 API 获取用户信息。state 参数防 CSRF。PKCE（code_challenge）增强公共客户端安全。",
        ["授权码模式：code 换 token，client_secret 只在后端使用", "state 参数随机字符串防 CSRF，回调时校验", "PKCE：code_verifier/code_challenge 增强移动端/SPA 安全", "access_token 短期，refresh_token 长期续期", "面试常考：授权码流程、state 作用、PKCE、token 安全"]
    ),
    "## 7.7 接口签名验证": (
        "接口签名通过 HMAC/非对称加密验证请求完整性和身份，防止篡改和重放，常用于开放 API。",
        "签名过程：将请求参数（path/query/body/timestamp/nonce）按规则拼接，用 AppSecret 做 HMAC-SHA256 生成签名，放入 Authorization/X-Signature 头。服务端用相同算法验签。防重放：timestamp（5分钟有效期）+ nonce（随机串，Redis 去重）。密钥管理：AppKey 标识身份，AppSecret 保密；更安全用 RSA 非对称签名（私钥签公钥验）。",
        ["参数排序拼接 + AppSecret HMAC-SHA256 生成签名", "timestamp 有效期 + nonce 防重放攻击", "AppKey 标识身份，AppSecret 保密不传输", "RSA 非对称签名比 HMAC 更安全（无需共享密钥）", "面试常考：签名算法、防重放、HMAC vs RSA、密钥管理"]
    ),
    "## 7.8 API 网关": (
        "API 网关是微服务统一入口，负责路由转发、认证鉴权、限流熔断、日志监控和协议转换。",
        "网关位于客户端和微服务之间，所有请求经过网关。核心功能：路由（按 path/host 转发到后端服务）、认证（JWT/API Key 统一校验）、限流熔断（令牌桶+熔断降级）、日志监控（请求日志/指标/trace）、协议转换（HTTP→gRPC）、灰度发布（按权重/Header 路由）。Python 生态：FastAPI 自写网关、Kong（Nginx+Lua）、APISIX、Traefik、Spring Cloud Gateway。",
        ["统一入口：路由+认证+限流+日志+熔断，横切关注点集中", "Kong/APISIX/Traefik 是成熟网关，Nginx-based 高性能", "网关认证后将用户信息传给后端（X-User-Id 头）", "灰度发布：网关按权重/Header 分流到不同版本", "面试常考：网关职责、认证下沉、限流熔断、选型对比"]
    ),
}

file_maps[r"08-Python全栈\Python数据库与缓存知识点系统梳理_优化版.md"] = {
    "### 2.4 关系查询与 N+1 优化": (
        "ORM 关系查询的 N+1 问题：1 条查询获取列表 + N 条查询访问关联对象，用预加载优化为 2 条查询。",
        "Django：QuerySet 惰性求值，访问外键/多对多时每次触发查询（N+1）。select_related（外键/一对一，JOIN 查询）、prefetch_related（多对多/反向外键，IN 查询+Python 拼接）。SQLAlchemy：joinedload（JOIN）、selectinload（IN 查询）、subqueryload（子查询）。async 版本用 selectinload 避免 joinedload 的笛卡尔积。",
        ["N+1：1 条查列表 + N 条查关联，列表页性能杀手", "Django select_related（FK/OneToOne JOIN）、prefetch_related（M2M IN）", "SQLAlchemy joinedload（JOIN）、selectinload（IN，async 友好）", "Django Debug Toolbar/SQLAlchemy echo 检测 N+1", "面试常考：N+1 原因、select_related vs prefetch_related、joinedload vs selectinload"]
    ),
    "### 4.5.2 SQLAlchemy 事务管理": (
        "SQLAlchemy 事务通过 Session 管理，自动 begin/commit/rollback，支持嵌套事务和保存点。",
        "Session 首次操作时自动开启事务，session.commit() 提交，session.rollback() 回滚。with session.begin() 上下文管理器自动提交/回滚。嵌套事务用 session.begin_nested()（SAVEPOINT）。async 版本 AsyncSession 用 async with session.begin()。声明式事务：FastAPI Depends 注入 Session，请求结束自动 commit/rollback。",
        ["Session 是事务边界，自动 begin，commit/rollback 结束", "with session.begin() 自动提交异常回滚", "begin_nested() 创建 SAVEPOINT 支持部分回滚", "AsyncSession: async with session.begin()", "面试常考：Session 生命周期、自动事务、SAVEPOINT、声明式事务"]
    ),
    "## 5.4 分库分表策略": (
        "分库分表解决单库单表数据量过大问题，分为垂直拆分（按业务/字段）和水平拆分（按行）。",
        "垂直分库：按业务拆库（用户库/订单库/商品库），微服务天然如此。垂直分表：冷热字段分离（大字段拆到扩展表）。水平分表：按分片键（user_id/order_id）将数据分散到多表多库，分片算法：取模（均匀但扩容难）、范围（按时间/ID 区间，易热点）、一致性哈希（扩容迁移少）。中间件：ShardingSphere（Java）、Vitess、Python 用 sqlalchemy-sharding 或应用层路由。",
        ["垂直拆分：按业务/字段，水平拆分：按行分片", "分片键选择：高基数、查询高频、避免跨片 JOIN", "取模均匀但扩容需数据迁移，一致性哈希迁移少", "跨片查询/分布式事务/全局唯一 ID 是主要挑战", "面试常考：垂直 vs 水平、分片算法、扩容迁移、分布式 ID"]
    ),
    "## 5.5 MongoDB（PyMongo）": (
        "MongoDB 是文档型 NoSQL，PyMongo/Motor 是 Python 驱动，适合半结构化数据和快速迭代场景。",
        "PyMongo 同步驱动：MongoClient 连接，db.col.insert_one/find/update_one/delete_one。Motor 异步驱动（AsyncIO）：AsyncIOMotorClient，await 操作。文档是 BSON（二进制 JSON），支持嵌套文档和数组。索引：create_index（单字段/复合/文本/地理）。聚合管道：$match/$group/$sort/$lookup（JOIN）。适合：日志/内容管理/物联网/原型快速迭代；不适合：多文档事务要求高、复杂 JOIN。",
        ["PyMongo 同步，Motor 异步（asyncio）", "文档 BSON 支持嵌套，schema 灵活适合半结构化数据", "聚合管道 $lookup 实现类 JOIN，$group 分组统计", "索引优化和关系型类似：explain() 分析查询计划", "面试常考：MongoDB vs RDBMS、聚合管道、索引、适用场景"]
    ),
    "## 5.6 Memcached": (
        "Memcached 是纯内存键值缓存，简单高效，适合小数据量缓存和 Session 存储。",
        "Memcached 多线程架构（比 Redis 单线程在多核下吞吐更高），数据只在内存（重启丢失），LRU 淘汰。数据结构只有 String（value 最大 1MB），不支持持久化/主从/集群（客户端一致性哈希分片）。Python 客户端：pymemcache、python-memcached。与 Redis 对比：Memcached 更简单、多核多线程吞吐高；Redis 数据结构丰富、持久化、主从复制、功能更全面。",
        ["纯内存、多线程、多核高吞吐，简单 KV 缓存", "只支持 String，value ≤1MB，无持久化，重启丢失", "客户端一致性哈希实现分布式，无服务端集群", "Redis 功能更丰富，Memcached 在纯 KV 场景性能更优", "面试常考：Memcached vs Redis、多线程模型、一致性哈希"]
    ),
}

file_maps[r"08-Python全栈\Python测试工程知识点系统梳理_优化版.md"] = {
    "## 8.1 契约测试（Contract Testing）": (
        "契约测试验证服务间 API 契约（请求/响应格式）是否一致，分消费者驱动和提供者驱动两种。",
        "消费者驱动契约（CDC）：消费者定义期望的请求/响应格式（契约），提供者验证自己满足所有消费者的契约。工具：Pact（Python 用 pact-python），消费者生成 pact 文件（JSON），提供者回放验证。解决微服务集成问题：不用启动所有服务即可验证接口兼容性，提供者修改接口时能立即发现破坏了哪个消费者。",
        ["消费者驱动契约（CDC）：消费者定义期望，提供者验证", "Pact 是主流工具，pact 文件是 JSON 格式契约", "不需要启动所有服务，独立验证接口兼容性", "契约测试在 E2E 测试和单元测试之间，速度快", "面试常考：契约测试概念、CDC、Pact 流程、与 E2E 区别"]
    ),
    "## 8.2 测试数据管理": (
        "测试数据管理包括数据准备、隔离、清理和工厂模式，确保测试可重复、独立、并行安全。",
        "工厂模式：factory_boy（Python 版 FactoryBot）定义模型工厂，Faker 生成随机数据，TestFixture 复用。数据隔离：每个测试用事务包裹（pytest-django 的 db fixture，测试后回滚）或独立测试数据库。数据清理：事务回滚（最快）、TRUNCATE（较慢）、删除。避免硬编码测试数据，用工厂+Faker 动态生成。敏感数据脱敏后用于测试。",
        ["factory_boy + Faker 生成测试数据，不硬编码", "事务回滚隔离测试数据（pytest-django db fixture）", "测试间数据独立，不依赖执行顺序", "pytest fixtures 作用域：function/class/module/session", "面试常考：工厂模式、数据隔离、fixture 作用域、并行测试"]
    ),
    "## 8.3 突变测试（Mutation Testing）": (
        "突变测试通过故意修改代码（突变体）检验测试套件的有效性，是评估测试质量的高级手段。",
        "工具（如 mutmut/cosmic-ray）自动对代码做小修改：将 > 改为 >=、+ 改为 -、True 改为 False、删除语句等（突变体），然后运行测试。如果测试失败，突变体被'杀死'（测试有效）；如果测试通过，突变体'存活'（测试覆盖不足）。突变分数 = 被杀死突变体/总突变体。缺点：计算开销大（每个突变体都要跑一遍测试），适合关键模块。",
        ["突变体：故意修改代码（>→>=、+→-、True→False）", "测试能检测到突变=杀死，检测不到=存活（测试不足）", "突变分数衡量测试套件的缺陷检测能力", "计算开销大，适合核心模块，不常用但能发现无效测试", "面试常考：突变测试原理、突变体、突变分数、与覆盖率区别"]
    ),
    "## 8.4 测试报告与并行测试": (
        "测试报告可视化测试结果，并行测试加速执行，是 CI/CD 中测试环节的效率保障。",
        "测试报告：pytest-html 生成 HTML 报告、pytest-cov 覆盖率报告、allure-pytest 生成 Allure 精美报告（趋势/分类/附件）、junit-xml 供 CI 解析。并行测试：pytest-xdist（-n auto 按 CPU 核数并行）、pytest-parallel。注意：并行测试需数据隔离（独立数据库/事务）、测试间无依赖、随机端口。CI 中并行+分片（--shard）进一步加速。",
        ["Allure 报告：趋势图/分类/附件，比 pytest-html 更专业", "pytest-cov 生成覆盖率报告（终端/HTML/XML）", "pytest-xdist -n auto 多核并行，要求测试独立", "并行测试需独立数据库/事务隔离，避免数据竞争", "面试常考：测试报告工具、并行测试条件、覆盖率分析"]
    ),
    "## 8.5 测试金字塔与策略": (
        "测试金字塔指导测试分层比例：大量单元测试、适量集成测试、少量 E2E 测试，平衡速度和信心。",
        "金字塔底层：单元测试（70%，快，隔离，测函数/类）；中层：集成测试（20%，测模块间交互/数据库/API）；顶层：E2E 测试（10%，慢，测完整用户流程）。反模式：冰淇淋金字塔（大量 E2E，慢且脆弱）。测试策略：核心逻辑单元测试覆盖、API 层集成测试、关键路径 E2E 冒烟测试。新代码先写测试（TDD），bug 修复先写复现测试。",
        ["单元测试多（快）、集成测试中、E2E 少（慢），70/20/10", "冰淇淋反模式：E2E 过多导致慢且不稳定", "单元测试 mock 外部依赖，集成测试用真实数据库", "E2E 只覆盖关键路径（登录/支付/下单），作为冒烟测试", "面试常考：测试金字塔、分层比例、反模式、测试策略"]
    ),
}

file_maps[r"08-Python全栈\Python语言基础与进阶知识点系统梳理_优化版.md"] = {
    "### 2.3 字符串操作": (
        "Python 字符串是不可变 Unicode 序列，常用操作包括格式化、分割拼接、查找替换和编码处理。",
        "格式化：f-string（f\"{name}\"，3.6+，最推荐）、str.format()、% 旧式。分割拼接：split/rsplit/partition、join（高效拼接，避免 + 循环）。查找替换：find/index（找不到 index 抛异常）、replace、strip/lstrip/rstrip。判断：startswith/endswith、isalpha/isdigit/isalnum。编码：encode('utf-8') 转 bytes，decode('utf-8') 转 str。不可变性：每次修改创建新字符串。",
        ["f-string 最推荐：f\"{name=}\" 支持表达式和 = 调试", "join 拼接比 + 高效（+ 每次创建新对象）", "str 不可变，encode→bytes，decode→str", "splitlines() 按行分割，partition 返回三元组", "面试常考：f-string、字符串不可变、编码、join vs +"]
    ),
    "### 3.2 函数": (
        "Python 函数是一等对象，支持默认参数、可变参数、关键字参数、闭包和装饰器。",
        "参数类型：位置参数、默认参数（必须在非默认后）、*args（可变位置参数，元组）、**kwargs（可变关键字参数，字典）、keyword-only 参数（* 之后）。默认参数用不可变对象（None），避免可变默认参数陷阱（def f(a=[]) 共享同一列表）。函数是一等公民：可赋值、传参、返回。lambda 匿名函数（单表达式）。",
        ["*args 收集位置参数为元组，**kwargs 收集关键字参数为字典", "默认参数用 None 而非 []/{}, 可变默认参数在定义时创建一次", "keyword-only 参数在 * 之后，必须用关键字传递", "lambda 只能单表达式，不支持语句", "面试常考：*args/**kwargs、可变默认参数陷阱、一等函数"]
    ),
    "## 5.5 正则表达式": (
        "Python re 模块提供正则匹配、搜索、替换和分割，用于文本提取和格式验证。",
        "re.match（从开头匹配）、re.search（搜索任意位置）、re.findall（返回所有匹配列表）、re.finditer（返回迭代器）、re.sub（替换）、re.split（按模式分割）。模式：r'' 原始字符串避免转义；\\d 数字、\\w 单词字符、\\s 空白、+ 一次或多次、* 零次或多次、? 零次或一次、{n,m} 次数、() 分组、[] 字符集、^/$ 开头结尾。编译正则 re.compile 复用提升性能。",
        ["match 从开头，search 任意位置，findall 返回所有匹配", "r'' 原始字符串避免反斜杠转义问题", "() 分组提取，group(1)/groups() 获取分组内容", "re.compile 预编译，频繁使用时提升性能", "面试常考：match vs search、贪婪 vs 非贪婪、分组、常用模式"]
    ),
    "### 5.6.3 依赖锁定": (
        "依赖锁定确保所有环境安装相同版本的依赖，避免'在我机器上能跑'问题。",
        "pip freeze > requirements.txt 生成精确版本（==），但包含间接依赖。pip-tools：requirements.in 写直接依赖，pip-compile 生成锁定文件（含间接依赖和 hash）。Poetry/PDM：pyproject.toml + poetry.lock，现代标准，自动管理虚拟环境和锁文件。锁文件提交到 Git，部署时 pip install -r requirements.txt 或 poetry install --no-dev 安装锁定版本。",
        ["pip freeze 包含所有依赖（含间接），pip-tools 更可控", "Poetry/PDM：pyproject.toml + lock 文件，现代标准", "锁文件提交 Git，确保开发/测试/生产版本一致", "pip install --require-hashes 验证包完整性", "面试常考：依赖锁定原因、requirements.txt vs Poetry、可复现构建"]
    ),
    "## 5.7 日志系统（logging）": (
        "Python logging 模块提供分级日志、多处理器、格式化和配置化日志管理。",
        "五大组件：Logger（记录器，按名称层级）、Handler（处理器：StreamHandler/FileHandler/RotatingFileHandler）、Filter（过滤器）、Formatter（格式化器）、LogRecord（日志记录）。级别：DEBUG<INFO<WARNING<ERROR<CRITICAL。最佳实践：模块级 logger = logging.getLogger(__name__)，配置 dictConfig/fileConfig，生产用 JSON 格式便于 ELK 采集，按大小/时间轮转日志，异常用 logger.exception() 自动带堆栈。",
        ["getLogger(__name__) 模块级 logger，按名称层级传播", "级别：DEBUG/INFO/WARNING/ERROR/CRITICAL", "RotatingFileHandler/TimedRotatingFileHandler 轮转日志", "生产用 JSON 格式 + ELK/Loki 采集，logger.exception 记录堆栈", "面试常考：logging 组件、日志级别、配置方式、轮转、异常日志"]
    ),
}

file_maps[r"08-Python全栈\Python部署运维知识点系统梳理_优化版.md"] = {
    "## 6.3 环境变量与配置管理": (
        "环境变量是 12-Factor App 推荐的配置方式，将配置与代码分离，不同环境使用不同变量。",
        "python-dotenv 从 .env 文件加载环境变量（开发用，.env 不提交 Git）。os.environ.get('KEY', 'default') 读取。Pydantic BaseSettings（FastAPI）自动从环境变量/ .env 读取并类型校验。配置分层：默认值→配置文件→环境变量→命令行参数（后者覆盖前者）。敏感配置（密钥/数据库密码）只通过环境变量注入，不写入代码和配置文件。生产用 K8s Secret/ConfigMap 或 Vault 管理。",
        ["python-dotenv 加载 .env（开发），.env 加入 .gitignore", "Pydantic BaseSettings 自动读取环境变量+类型校验", "12-Factor：配置存环境变量，代码不含环境差异", "敏感信息用 K8s Secret/Vault，不写代码和 .env", "面试常考：12-Factor 配置、dotenv、BaseSettings、密钥管理"]
    ),
    "## 8.3 日志收集架构": (
        "生产日志收集架构将分散的日志集中存储和分析，典型方案为 ELK/EFK 或 Loki 栈。",
        "ELK：Elasticsearch（存储索引）+ Logstash/Fluentd（采集处理）+ Kibana（可视化）。EFK：Fluentd 替代 Logstash（K8s 常用）。Loki：Grafana Loki 轻量级，只索引标签不索引全文，成本低，配合 Promtail 采集。日志规范：JSON 结构化输出（level/time/service/trace_id/message），stdout 输出（容器标准），Sidecar/DaemonSet 采集。链路追踪：trace_id 贯穿日志便于关联。",
        ["ELK：Elasticsearch+Logstash+Kibana，功能强大但资源消耗大", "Loki+Promtail+Grafana：轻量低成本，只索引标签", "JSON 结构化日志到 stdout，容器标准做法", "trace_id 贯穿日志，关联同一请求的所有日志", "面试常考：ELK vs Loki、结构化日志、日志采集、trace_id"]
    ),
    "## 8.4 健康检查": (
        "健康检查让负载均衡器和编排系统判断服务是否正常，分存活探针和就绪探针。",
        "存活检查（liveness）：服务是否运行，失败则重启容器（K8s livenessProbe）。就绪检查（readiness）：服务是否可接收流量，失败则从负载均衡摘除但不重启（K8s readinessProbe）。启动检查（startup）：慢启动应用保护。FastAPI /health 端点：检查数据库/Redis/外部依赖连通性。K8s 探针：httpGet/tcpSocket/exec，initialDelaySeconds/periodSeconds/failureThreshold 配置。",
        ["liveness 失败重启，readiness 失败摘流量不重启", "健康检查端点检查依赖（DB/Redis）连通性，不只返回 200", "K8s 探针：httpGet/tcpSocket/exec，配置延迟和阈值", "启动探针保护慢启动应用，避免被 liveness 误杀", "面试常考：liveness vs readiness、健康检查端点、K8s 探针配置"]
    ),
}


def run():
    for fpath, cmap in file_maps.items():
        full_path = os.path.join(BASE, fpath)
        lines, added = expand(full_path, cmap, False, False, "")
        print(f"  {os.path.basename(fpath)}: {lines} lines, {added} blocks added")


if __name__ == "__main__":
    run()
