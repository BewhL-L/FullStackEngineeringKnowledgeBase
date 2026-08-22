---
title: Nginx 知识点系统梳理
tags: [运维, Nginx, 反向代理, 负载均衡, 面试]
created: 2026-08-13
updated: 2026-08-13
---

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。

# Nginx 知识点系统梳理（优化版）

> **文档说明**：系统梳理 Nginx 核心知识，涵盖反向代理、负载均衡、静态资源、HTTPS、限流、配置优化等内容。

---

## 1. 概述

Nginx 是高性能的**HTTP 和反向代理服务器**，以高并发、低资源消耗著称，常用于 Web 服务器、反向代理、负载均衡、静态资源服务。

**核心特性**：
- 事件驱动、异步非阻塞（epoll），支持高并发
- 模块化设计，可扩展
- 反向代理、负载均衡
- 静态资源服务、Gzip 压缩
- HTTPS、HTTP/2、HTTP/3 支持
- 限流、缓存、访问控制

**正向代理 vs 反向代理**：
- **正向代理**：代理客户端，访问目标服务器（如 VPN）
- **反向代理**：代理服务器，客户端不知道真实服务器（如 Nginx 转发到后端应用）

---


---
## 2. 配置文件结构

```nginx
# 全局块
user nginx;
worker_processes auto;        # 工作进程数，建议等于 CPU 核数
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

# events 块
events {
    worker_connections 10240; # 每个工作进程最大连接数
    use epoll;                # 事件模型，Linux 用 epoll
    multi_accept on;          # 一次接受多个连接
}

# http 块
http {
    include       mime.types;
    default_type  application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile        on;       # 高效文件传输
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout 65;     # 长连接超时
    gzip on;                  # 开启压缩

    # 上游服务器（负载均衡）
    upstream backend {
        server 192.168.1.10:8080 weight=1;
        server 192.168.1.11:8080 weight=2;
        server 192.168.1.12:8080 backup; # 备份服务器
    }

    # server 块（虚拟主机）
    server {
        listen 80;
        server_name example.com;

        # location 块
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：理解 Nginx 配置结构是正确配置的基础。
>
> **原理**：Nginx 采用多进程模型：master 进程管理配置和 worker 进程，worker 进程处理请求（每个 worker 单线程，通过 epoll 异步非阻塞处理大量连接）。配置文件分四层：全局块（进程、日志）、events（连接处理）、http（HTTP 全局配置）、server（虚拟主机）、location（URL 匹配）。location 匹配优先级：精确匹配 `=` > 前缀匹配 `^~` > 正则匹配 `~`/`~*` > 普通前缀匹配 > 默认 `/`。
>
> **用法要点**：① worker_processes 设为 auto 或 CPU 核数；② worker_connections 调大（10240+）支持高并发；③ 用 include 拆分配置文件（conf.d/*.conf）；④ nginx -t 测试配置，nginx -s reload 热重载（不中断服务）；⑤ 面试常考：配置结构、location 匹配优先级、进程模型、epoll。

---


---
## 3. 反向代理

```nginx
location /api/ {
    proxy_pass http://backend;
    
    # 传递真实客户端信息
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # 超时设置
    proxy_connect_timeout 10s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
    
    # 缓冲
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
}
```

**注意**：`proxy_pass` 末尾带 `/` 会替换 location 前缀，不带则追加。
- `location /api/` + `proxy_pass http://backend/` → `/api/users` → `http://backend/users`
- `location /api/` + `proxy_pass http://backend` → `/api/users` → `http://backend/api/users`

---


---
## 4. 负载均衡

### 4.1 策略

| 策略 | 说明 |
|------|------|
| `round-robin` | 默认，轮询 |
| `weight` | 加权轮询 |
| `ip_hash` | 按客户端 IP 哈希，同一客户端到同一后端（会话保持） |
| `least_conn` | 最少连接数 |
| `fair` | 响应时间（需第三方模块） |
| `url_hash` | 按 URL 哈希（需第三方模块） |

> 🔍 **知识点深度解析**
>
> **作用**：负载均衡策略决定请求如何分发到 upstream 中的多个后端服务器，直接影响吞吐、可用性与会话一致性。
>
> **原理**：Nginx 在 upstream 块中按策略选择后端：round-robin 默认轮询；weight 加权轮询按权重比例分配（权重越大越多）；ip_hash 对客户端 IP 做哈希，使同一客户端固定落到同一后端（会话保持）；least_conn 选当前连接数最少的节点（适合处理时长差异大的场景）；fair/url_hash 需第三方模块。
>
> **用法要点**：① 生产用 weight 加权轮询，性能好的节点权重调大；② 会话保持优先用 Redis 共享 session，而非依赖 ip_hash（IP 变化或经代理后失效）；③ 配合 max_fails/fail_timeout 做被动健康检查，自动剔除异常节点；④ backup 标记备用节点，仅当其他均不可用时启用；⑤ least_conn 适合长连接/耗时差异大的服务；⑥ 加 keepalive 复用后端长连接，降低握手开销。

### 4.2 配置

```nginx
upstream backend {
    # weight 权重，max_fails 失败次数，fail_timeout 失败超时
    server 192.168.1.10:8080 weight=3 max_fails=3 fail_timeout=30s;
    server 192.168.1.11:8080 weight=1 max_fails=3 fail_timeout=30s;
    server 192.168.1.12:8080 backup;  # 备份，其他都挂了才用
    keepalive 32;  # 长连接数
}
```

> 🔍 **知识点深度解析**
>
> **作用**：负载均衡将请求分发到多个后端服务器，提升吞吐量和可用性。
>
> **原理**：Nginx 反向代理时根据 upstream 配置的策略选择后端服务器。加权轮询按 weight 比例分配（weight 越大分配越多）。ip_hash 用客户端 IP 前三位做哈希，保证同一客户端总是到同一后端（解决 session 问题，但 IP 变化或代理后失效）。least_conn 选择当前连接数最少的服务器，适合请求处理时间差异大的场景。健康检查：max_fails 次失败后，在 fail_timeout 内不再分配请求到该服务器。
>
> **用法要点**：① 生产用 weight 加权轮询，性能好的服务器 weight 大；② 会话保持优先用 Redis 共享 session，不要依赖 ip_hash；③ 配置健康检查（max_fails + fail_timeout）自动剔除故障节点；④ keepalive 配置长连接，减少 TCP 握手开销；⑤ 面试常考：负载均衡策略、ip_hash 原理、健康检查、会话保持方案。

---


---
## 5. 静态资源服务

```nginx
server {
    listen 80;
    server_name static.example.com;
    root /var/www/static;

    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 30d;          # 缓存 30 天
        add_header Cache-Control "public, immutable";
        access_log off;       # 静态资源不记日志
    }

    location / {
        try_files $uri $uri/ /index.html;  # SPA 前端路由
    }
}
```

**Gzip 压缩**：
```nginx
gzip on;
gzip_min_length 1k;
gzip_comp_level 5;
gzip_types text/plain text/css application/json application/javascript text/xml;
gzip_vary on;
```

---


---
## 6. HTTPS 配置

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate     /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        root /usr/share/nginx/html;
    }
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

---


---
## 7. 限流

### 7.1 请求限流（limit_req）

```nginx

> 🔍 **知识点深度解析**
>
> **作用**：Nginx limit_req 基于漏桶算法限制请求速率，防止突发流量压垮后端服务。
>
> **原理**：limit_req_zone 定义限流区域（key=二进制IP、zone名称、共享内存大小、rate 速率）。limit_req zone=name burst=N nodelay 在 location 中启用：rate 限制平均速率（如 10r/s），burst 允许突发请求数排队，nodelay 突发请求立即处理不延迟。超出 burst 的请求返回 503。还可用 limit_conn 限制并发连接数。
>
> **用法要点**：① limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s 在 http 块定义  ② limit_req zone=api burst=20 nodelay 在 location 启用  ③ burst 是排队容量，nodelay 让突发请求立即处理  ④ limit_conn 限制并发连接数，limit_req 限制速率  ⑤ 面试常考：漏桶算法、burst/nodelay、503 处理

# 定义限流区域：10r/s 每秒 10 个请求
limit_req_zone $binary_remote_addr zone=req_limit:10m rate=10r/s;

server {
    location /api/ {
        # burst 允许突发 20 个，nodelay 不延迟直接处理
        limit_req zone=req_limit burst=20 nodelay;
        proxy_pass http://backend;
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：limit_req 对请求速率做限流（漏桶算法），保护后端不被突发流量冲垮，常用于防刷、防爬虫、防 DDoS。
>
> **原理**：通过 limit_req_zone 在共享内存中定义限流区（key 通常为 $binary_remote_addr 即客户端 IP，rate 设定平均速率如 10r/s）；limit_req 在 location 中引用该区，burst 设置桶容量（允许突发的请求数），nodelay 表示突发请求不排队直接处理，超出 burst+rate 的请求直接返回 503。
>
> **用法要点**：① rate 用 r/s 或 r/m，按业务承受能力设定；② burst + nodelay 平滑正常突发，避免误伤；③ 超量返回 503，可用 error_page 自定义限流页；④ 限流 key 用 $binary_remote_addr（二进制省内存）；⑤ 多 location 可共用一个 zone；⑥ 过于严格的速率会让正常用户频繁 503，需结合监控调参。

### 7.2 连接限流（limit_conn）

```nginx
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

server {
    location /download/ {
        limit_conn conn_limit 10;  # 每个 IP 最多 10 个连接
    }
}
```

> 🔍 **知识点深度解析**
>
> **作用**：限流保护后端服务不被突发流量冲垮，防爬虫、防 DDoS。
>
> **原理**：limit_req 用漏桶算法，rate 设定平均速率（10r/s = 每 100ms 一个请求），burst 设置桶容量（允许突发的请求数），nodelay 表示突发请求不排队直接处理（超过 burst+rate 的请求直接 503）。limit_conn 限制并发连接数。$binary_remote_addr 是客户端 IP 的二进制形式（比字符串省空间），zone 定义共享内存区域（10m 可存约 16 万个 IP 状态）。
>
> **用法要点**：① rate 用 r/s 或 r/m；② burst + nodelay 应对正常突发流量；③ 限流返回 503，可自定义错误页；④ 面试常考：限流算法（漏桶/令牌桶）、limit_req 配置、burst 作用。

---


---
## 8. 动静分离

```nginx
server {
    listen 80;
    server_name example.com;

    # 静态资源由 Nginx 处理
    location ~* \.(html|css|js|jpg|png|gif)$ {
        root /var/www/static;
        expires 7d;
    }

    # 动态请求转发到后端
    location /api/ {
        proxy_pass http://backend;
    }

    # 上传目录
    location /upload/ {
        alias /data/upload/;
    }
}
```

---


---
## 9. 性能优化

1. **worker_processes auto**：等于 CPU 核数
2. **worker_connections 10240+**：增大连接数
3. **sendfile on + tcp_nopush on**：高效静态文件传输
4. **keepalive_timeout**：合理设置长连接（65s）
5. **gzip 压缩**：减少传输体积
6. **静态资源缓存**：expires + Cache-Control
7. **upstream keepalive**：后端长连接复用
8. **合理的 worker_rlimit_nofile**：文件描述符限制
9. **开启 HTTP/2**：多路复用
10. **separate 日志**：access_log 异步写入

---


---
## 10. 面试高频考点

1. **Nginx 进程模型**：master + worker、epoll 异步非阻塞
2. **反向代理**：配置、proxy_pass 路径问题
3. **负载均衡**：策略、ip_hash、健康检查
4. **location 匹配**：优先级、正则
5. **HTTPS**：配置、TLS 版本
6. **限流**：limit_req、漏桶算法、burst
7. **动静分离**：静态资源 + 反向代理
8. **性能优化**：并发配置、压缩、缓存
9. **正向 vs 反向代理**：区别
10. **502/504 错误**：原因排查（后端挂了/超时）

---


---
## 📝 精简总结

- Nginx 是高性能反向代理/Web 服务器，epoll 异步非阻塞
- 配置分四层：全局 → events → http → server → location
- 反向代理用 proxy_pass，注意路径末尾 / 的区别
- 负载均衡策略：轮询、加权、ip_hash、least_conn
- 静态资源服务 + 缓存 + Gzip，动静分离提升性能
- HTTPS 用 443 端口 + SSL 证书，HTTP 重定向
- 限流用 limit_req（漏桶）+ burst 应对突发
- 优化：多 worker、大连接数、长连接、压缩、缓存

---

[[05-云原生与运维/MOC-云原生与运维|← 返回云原生 MOC]] | [[Home|🏠 返回首页]]
