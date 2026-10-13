---
title: Prometheus监控体系
tags: [Prometheus, 可观测性, Grafana, 云原生, DevOps]
category: 云原生
created: 2026-08-29
updated: 2026-08-29
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[Docker容器化]]"]
aliases: [Prometheus监控体系]
---

# 📊 Prometheus 监控体系

> Prometheus 是云原生时代的事实标准监控系统，通过多维数据模型、强大的 PromQL 查询语言、高效的时序数据库和灵活的告警机制，为容器化应用和微服务架构提供完整的可观测性解决方案。

---

## 一、Prometheus 概述

### 什么是 Prometheus
Prometheus 是一个开源的系统监控和告警工具包，最初由 SoundCloud 开发，2016 年加入 CNCF（云原生计算基金会），是继 Kubernetes 之后第二个毕业的 CNCF 项目。

### 核心特性
| 特性 | 说明 |
|------|------|
| **多维数据模型** | 时序数据由指标名和键值对（标签）标识，支持灵活的维度组合 |
| **PromQL 查询语言** | 强大的查询语言，支持聚合、切片、预测、关联等复杂操作 |
| **拉取模型** | 通过 HTTP 拉取指标，目标端只需暴露 /metrics 端点 |
| **无依赖存储** | 自带时序数据库，无需外部存储，单机即可工作 |
| **服务发现** | 支持静态配置、DNS、Kubernetes、Consul 等多种服务发现方式 |
| **告警管理** | 灵活的告警规则，支持分组、抑制、静默、路由等高级功能 |
| **可视化集成** | 与 Grafana 深度集成，提供丰富的图表和仪表盘 |
| **客户端库** | 支持 Go、Java、Python、Ruby 等多种语言的客户端库 |
| **高可用** | 支持联邦集群和高可用部署，水平扩展 |

### Prometheus 架构
```text
                        ┌─────────────┐
                        │  Pushgateway │
                        └──────┬──────┘
                               │ 推送
                               ▼
┌─────────────┐    拉取    ┌─────────────┐    告警    ┌─────────────┐
│  目标服务    │ ──────────► │  Prometheus  │ ─────────► │ Alertmanager │
│ (Exporters)  │            │   Server     │            └──────┬──────┘
└─────────────┘            └──────┬──────┘                   │
                                    │ 存储                        │ 通知
                                    ▼                             ▼
                            ┌─────────────┐              ┌─────────────┐
                            │  TSDB 存储   │              │  邮件/钉钉   │
                            └─────────────┘              │  Slack/Webhook│
                                                           └─────────────┘
                                    │
                                    │ 查询
                                    ▼
                            ┌─────────────┐
                            │   Grafana    │
                            └─────────────┘
```

### 核心组件
| 组件 | 说明 |
|------|------|
| **Prometheus Server** | 核心组件，负责抓取、存储、查询指标 |
| **Exporters** | 指标暴露器，将第三方系统指标转换为 Prometheus 格式 |
| **Pushgateway** | 推送网关，支持短生命周期任务推送指标 |
| **Alertmanager** | 告警管理器，处理告警的分组、抑制、静默、通知 |
| **Client Libraries** | 客户端库，用于在应用代码中埋点指标 |
| **Grafana** | 可视化平台（非 Prometheus 组件，但通常配合使用） |

---

## 二、Prometheus 数据模型

### 时序数据
Prometheus 中所有数据都是时序数据（Time Series），由以下部分组成：

```text
<metric name>{<label name>=<label value>, ...} <timestamp> <value>
```

**示例**
```text
http_requests_total{method="GET",path="/api/users",status="200"} 1620000000 1024
```

### 指标类型
Prometheus 有四种核心指标类型：

| 类型 | 说明 | 示例 | 适用场景 |
|------|------|------|---------|
| **Counter** | 计数器，只增不减（可重置为0） | `http_requests_total` | 请求数、错误数、任务完成数 |
| **Gauge** | 仪表盘，可增可减 | `memory_usage_bytes` | 内存使用、CPU 使用率、队列长度 |
| **Histogram** | 直方图，统计数据分布 | `http_request_duration_seconds` | 请求延迟、响应大小 |
| **Summary** | 摘要，统计分位数 | `http_request_duration_seconds` | 请求延迟、响应大小（客户端计算分位数） |

**Counter 示例**
```go
// 定义 Counter
var httpRequestsTotal = prometheus.NewCounterVec(
    prometheus.CounterOpts{
        Name: "http_requests_total",
        Help: "Total number of HTTP requests",
    },
    []string{"method", "path", "status"},
)

// 增加计数
httpRequestsTotal.WithLabelValues("GET", "/api/users", "200").Inc()
```

**Gauge 示例**
```go
// 定义 Gauge
var memoryUsageBytes = prometheus.NewGauge(
    prometheus.GaugeOpts{
        Name: "memory_usage_bytes",
        Help: "Current memory usage in bytes",
    },
)

// 设置值
memoryUsageBytes.Set(1024 * 1024 * 256)
```

**Histogram 示例**
```go
// 定义 Histogram
var httpRequestDuration = prometheus.NewHistogramVec(
    prometheus.HistogramOpts{
        Name:    "http_request_duration_seconds",
        Help:    "HTTP request duration in seconds",
        Buckets: prometheus.DefBuckets, // 默认桶：0.005, 0.01, 0.025, ..., 10
    },
    []string{"method", "path"},
)

// 观察值
httpRequestDuration.WithLabelValues("GET", "/api/users").Observe(0.123)
```

### 标签（Labels）
标签是 Prometheus 多维数据模型的核心，通过键值对标识时序数据的维度。

**标签命名规范**
- 使用小写字母、数字、下划线
- 以字母开头
- `__` 开头的标签为内部保留标签
- 标签值可以包含任意 Unicode 字符

**常用标签**
| 标签 | 说明 | 示例 |
|------|------|------|
| `method` | HTTP 方法 | GET, POST, PUT, DELETE |
| `path` | 请求路径 | /api/users, /api/orders |
| `status` | HTTP 状态码 | 200, 404, 500 |
| `instance` | 实例地址 | 192.168.1.1:8080 |
| `job` | 任务名称 | api-server, worker |
| `namespace` | K8s 命名空间 | production, staging |
| `pod` | K8s Pod 名称 | api-server-7d9f8b6c5d-x2k4j |

**标签最佳实践**
- ✅ 标签基数不宜过大（如 user_id、request_id 不适合作为标签）
- ✅ 使用标签区分不同维度（环境、区域、版本等）
- ✅ 保持标签名和值的一致性
- ❌ 不要在标签中存储高频变化的值
- ❌ 不要使用过多标签（建议不超过 10 个）

---

## 三、PromQL 查询语言

### 基本查询
**查询最新值**
```promql
# 查询所有实例的 CPU 使用率
node_cpu_usage_percent

# 按标签过滤
node_cpu_usage_percent{instance="server1:9100"}

# 正则匹配
node_cpu_usage_percent{instance=~"server[1-3]:.*"}

# 排除匹配
node_cpu_usage_percent{instance!~"server[1-3]:.*"}
```

**查询历史值**
```promql
# 查询 5 分钟前的值
node_cpu_usage_percent offset 5m

# 查询时间范围（区间向量）
node_cpu_usage_percent[5m]

# 查询 1 小时前的 5 分钟区间
node_cpu_usage_percent[5m] offset 1h
```

### 常用函数
**聚合函数**
| 函数 | 说明 | 示例 |
|------|------|------|
| `sum` | 求和 | `sum(http_requests_total)` |
| `avg` | 平均值 | `avg(node_cpu_usage_percent)` |
| `min` | 最小值 | `min(node_memory_available_bytes)` |
| `max` | 最大值 | `max(node_memory_usage_bytes)` |
| `count` | 计数 | `count(up == 0)` |
| `stddev` | 标准差 | `stddev(node_cpu_usage_percent)` |
| `stdvar` | 标准方差 | `stdvar(node_cpu_usage_percent)` |
| `topk` | 前 K 个 | `topk(5, node_cpu_usage_percent)` |
| `bottomk` | 后 K 个 | `bottomk(5, node_memory_available_bytes)` |
| `quantile` | 分位数 | `quantile(0.95, http_request_duration_seconds)` |

**聚合示例**
```promql
# 按 job 分组求和
sum by (job) (http_requests_total)

# 按 method 和 path 分组求平均
avg by (method, path) (http_request_duration_seconds_sum)

# 排除 instance 标签
sum without (instance) (node_cpu_usage_percent)

# 统计每个 job 的实例数
count by (job) (up)

# CPU 使用率最高的 5 个实例
topk(5, node_cpu_usage_percent)
```

**计算函数**
| 函数 | 说明 | 示例 |
|------|------|------|
| `rate` | 每秒增长率（区间向量） | `rate(http_requests_total[5m])` |
| `irate` | 瞬时增长率（基于最后两个点） | `irate(http_requests_total[5m])` |
| `increase` | 增长量 | `increase(http_requests_total[1h])` |
| `delta` | 变化量（Gauge） | `delta(node_memory_usage_bytes[1h])` |
| `deriv` | 导数（Gauge） | `deriv(node_memory_usage_bytes[1h])` |
| `predict_linear` | 线性预测 | `predict_linear(node_memory_usage_bytes[1h], 3600)` |
| `histogram_quantile` | 直方图分位数 | `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` |

**计算示例**
```promql
# HTTP 请求 QPS
rate(http_requests_total[5m])

# 按 method 和 path 分组的 QPS
sum by (method, path) (rate(http_requests_total[5m]))

# HTTP 请求 P95 延迟
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))

# 错误率
sum by (path) (rate(http_requests_total{status=~"5.."}[5m])) 
/ 
sum by (path) (rate(http_requests_total[5m]))

# 预测 1 小时后内存是否会满（>90%）
predict_linear(node_memory_usage_bytes[1h], 3600) / node_memory_total_bytes > 0.9
```

### 运算符
**算术运算符**
```promql
# 加法
node_memory_usage_bytes + node_memory_available_bytes

# 除法（计算使用率）
node_memory_usage_bytes / node_memory_total_bytes * 100

# 乘法
rate(http_requests_total[5m]) * 60
```

**比较运算符**
```promql
# CPU 使用率大于 80%
node_cpu_usage_percent > 80

# 等于 0（服务宕机）
up == 0

# 不等于
node_cpu_usage_percent != 100
```

**逻辑运算符**
```promql
# 与（and）
node_cpu_usage_percent > 80 and node_memory_usage_percent > 80

# 或（or）
node_cpu_usage_percent > 90 or node_memory_usage_percent > 90

# 非（unless）
node_cpu_usage_percent > 80 unless maintenance_mode == 1
```

---

## 四、Prometheus 配置与部署

### 基础配置
**prometheus.yml**
```yaml
# 全局配置
global:
  scrape_interval: 15s          # 抓取间隔
  evaluation_interval: 15s      # 规则评估间隔
  scrape_timeout: 10s           # 抓取超时
  external_labels:              # 外部标签
    monitor: 'production-monitor'
    environment: 'production'

# 规则文件
rule_files:
  - "rules/*.yml"

# Alertmanager 配置
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# 抓取配置
scrape_configs:
  # Prometheus 自身监控
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter（主机监控）
  - job_name: 'node-exporter'
    static_configs:
      - targets:
          - 'server1:9100'
          - 'server2:9100'
          - 'server3:9100'

  # 应用监控（通过服务发现）
  - job_name: 'api-server'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets:
          - 'api-server1:8080'
          - 'api-server2:8080'

  # Kubernetes 服务发现
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
```

```text
### Docker Compose 部署
```
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.48.0
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./rules:/etc/prometheus/rules
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:v0.26.0
    container_name: alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager-data:/alertmanager
    restart: unless-stopped

  grafana:
    image: grafana/grafana:10.2.0
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:v1.7.0
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped

volumes:
  prometheus-data:
  alertmanager-data:
  grafana-data:
```

### 常用 Exporters
| Exporter | 说明 | 端口 |
|----------|------|------|
| **node_exporter** | 主机硬件和操作系统指标 | 9100 |
| **blackbox_exporter** | 黑盒监控（HTTP/TCP/ICMP/DNS） | 9115 |
| **mysqld_exporter** | MySQL 数据库指标 | 9104 |
| **redis_exporter** | Redis 指标 | 9121 |
| **postgres_exporter** | PostgreSQL 指标 | 9187 |
| **mongodb_exporter** | MongoDB 指标 | 9216 |
| **nginx_exporter** | Nginx 指标 | 9113 |
| **kafka_exporter** | Kafka 指标 | 9308 |
| **elasticsearch_exporter** | Elasticsearch 指标 | 9114 |
| **rabbitmq_exporter** | RabbitMQ 指标 | 9419 |
| **cadvisor** | 容器资源指标 | 8080 |
| **kube-state-metrics** | Kubernetes 状态指标 | 8080 |

---

## 五、告警配置（Alertmanager）

### 告警规则
**rules/alerts.yml**
```yaml
groups:
  - name: node-alerts
    rules:
      # 主机宕机
      - alert: NodeDown
        expr: up{job="node-exporter"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "主机 {{ $labels.instance }} 宕机"
          description: "主机 {{ $labels.instance }} 已经宕机超过 1 分钟"

      # CPU 使用率过高
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "主机 {{ $labels.instance }} CPU 使用率过高"
          description: "主机 {{ $labels.instance }} CPU 使用率超过 80%，当前值 {{ $value }}%"

      # 内存使用率过高
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "主机 {{ $labels.instance }} 内存使用率过高"
          description: "主机 {{ $labels.instance }} 内存使用率超过 85%，当前值 {{ $value }}%"

      # 磁盘使用率过高
      - alert: HighDiskUsage
        expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "主机 {{ $labels.instance }} 磁盘 {{ $labels.mountpoint }} 使用率过高"
          description: "磁盘使用率超过 85%，当前值 {{ $value }}%"

  - name: app-alerts
    rules:
      # 服务不可用
      - alert: ServiceDown
        expr: up{job="api-server"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "服务 {{ $labels.job }} 不可用"
          description: "服务 {{ $labels.job }} 实例 {{ $labels.instance }} 已经不可用超过 1 分钟"

      # HTTP 5xx 错误率过高
      - alert: HighErrorRate
        expr: sum by (path) (rate(http_requests_total{status=~"5.."}[5m])) / sum by (path) (rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "接口 {{ $labels.path }} 错误率过高"
          description: "接口 {{ $labels.path }} 5xx 错误率超过 5%，当前值 {{ $value }}%"

      # HTTP P95 延迟过高
      - alert: HighLatency
        expr: histogram_quantile(0.95, sum by (le, path) (rate(http_request_duration_seconds_bucket[5m]))) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "接口 {{ $labels.path }} P95 延迟过高"
          description: "接口 {{ $labels.path }} P95 延迟超过 1 秒，当前值 {{ $value }}s"
```

### Alertmanager 配置
**alertmanager.yml**
```yaml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alertmanager@example.com'
  smtp_auth_username: 'alertmanager@example.com'
  smtp_auth_password: 'password'

# 告警模板
templates:
  - '/etc/alertmanager/templates/*.tmpl'

# 路由树
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s          # 组内第一条告警等待时间
  group_interval: 5m        # 组内后续告警间隔
  repeat_interval: 4h       # 重复告警间隔
  receiver: 'default'       # 默认接收者
  routes:
    # 严重告警发送到值班电话
    - matchers:
        - severity = critical
      receiver: 'oncall'
      group_wait: 10s
      repeat_interval: 1h

    # 警告告警发送到邮件
    - matchers:
        - severity = warning
      receiver: 'email'

# 接收者
receivers:
  - name: 'default'
    email_configs:
      - to: 'devops@example.com'
        send_resolved: true

  - name: 'oncall'
    email_configs:
      - to: 'oncall@example.com'
        send_resolved: true
    webhook_configs:
      - url: 'https://oapi.dingtalk.com/robot/send?access_token=xxx'
        send_resolved: true

  - name: 'email'
    email_configs:
      - to: 'dev@example.com'
        send_resolved: true

# 抑制规则
inhibit_rules:
  # 服务宕机时抑制该服务的其他告警
  - source_matchers:
      - alertname = ServiceDown
    target_matchers:
      - severity = warning
    equal: ['job', 'instance']

  # 主机宕机时抑制该主机的所有告警
  - source_matchers:
      - alertname = NodeDown
    target_matchers:
      - severity =~ "warning|critical"
    equal: ['instance']
```

---

## 六、Grafana 可视化

### Grafana 配置
**provisioning/datasources/prometheus.yml**
```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

### 常用仪表盘
| 仪表盘 | 说明 | Grafana ID |
|--------|------|-----------|
| **Node Exporter Full** | 主机资源监控（CPU、内存、磁盘、网络） | 1860 |
| **Docker Monitoring** | 容器资源监控 | 893 |
| **Kubernetes Cluster** | K8s 集群监控 | 7249 |
| **MySQL Overview** | MySQL 数据库监控 | 7362 |
| **Redis Overview** | Redis 监控 | 763 |
| **Nginx** | Nginx 监控 | 12708 |
| **JVM (Micrometer)** | Java 应用 JVM 监控 | 4701 |
| **Spring Boot** | Spring Boot 应用监控 | 12900 |
| **Prometheus Stats** | Prometheus 自身监控 | 2 |
| **Alertmanager** | Alertmanager 监控 | 9578 |

### 常用面板查询
**CPU 使用率**
```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**内存使用率**
```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

**磁盘使用率**
```promql
(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100
```

**网络流量**
```promql
# 入站流量
rate(node_network_receive_bytes_total{device!~"lo|docker.*"}[5m]) * 8

# 出站流量
rate(node_network_transmit_bytes_total{device!~"lo|docker.*"}[5m]) * 8
```

**HTTP QPS**
```promql
sum by (method, path) (rate(http_requests_total[5m]))
```

**HTTP 错误率**
```promql
sum by (path) (rate(http_requests_total{status=~"5.."}[5m])) 
/ 
sum by (path) (rate(http_requests_total[5m])) * 100
```

**HTTP P95 延迟**
```promql
histogram_quantile(0.95, sum by (le, path) (rate(http_request_duration_seconds_bucket[5m])))
```

---

## 七、Prometheus 最佳实践

### 1. 指标命名规范
- ✅ 使用 `_` 分隔单词，全小写
- ✅ 使用后缀表示单位：`_seconds`、`_bytes`、`_total`
- ✅ Counter 类型使用 `_total` 后缀
- ✅ 指标名前缀表示命名空间：`http_`、`node_`、`process_`
- ❌ 不要使用 `_count`、`_sum` 作为后缀（Histogram/Summary 自动生成）
- ❌ 不要在指标名中包含单位（应使用后缀）
- ❌ 不要使用大写字母和连字符

**示例**
```css
# 好的命名
http_requests_total
http_request_duration_seconds
node_memory_usage_bytes
process_cpu_seconds_total

# 不好的命名
HttpRequests（大写）
http-requests（连字符）
requestCount（驼峰、无单位）
memory_usage（无单位）
```

### 2. 标签使用规范
- ✅ 标签基数不宜过大（避免 user_id、request_id）
- ✅ 使用标签区分维度：环境、区域、版本、方法等
- ✅ 保持标签名和值的一致性
- ✅ 使用 `instance` 标签标识实例
- ❌ 不要在标签中存储高频变化的值
- ❌ 不要使用过多标签（建议不超过 10 个）
- ❌ 不要使用 `le`、`quantile` 作为自定义标签（保留标签）

### 3. 抓取配置最佳实践
- ✅ 合理设置抓取间隔（15s-1m）
- ✅ 使用服务发现，避免静态配置
- ✅ 使用 relabel 过滤和重命名标签
- ✅ 设置合理的抓取超时
- ✅ 为高基数指标设置抓取间隔更长
- ❌ 不要抓取不需要的指标（使用 metric_relabel 过滤）
- ❌ 不要设置过短的抓取间隔（增加存储和计算压力）

### 4. 存储和性能优化
- ✅ 合理设置数据保留时间（默认 15 天，可根据需求调整）
- ✅ 使用 TSDB 压缩和降采样（Prometheus 2.x 自动压缩）
- ✅ 高基数指标使用 recording rules 预聚合
- ✅ 使用联邦集群水平扩展
- ✅ 定期清理不再需要的时间序列
- ❌ 不要存储过高基数的指标（如 user_id）
- ❌ 不要设置过长的保留时间（增加存储成本）

### 5. 告警最佳实践
- ✅ 告警要有明确的可操作性
- ✅ 设置合理的 `for` 持续时间，避免抖动
- ✅ 使用分级告警（warning/critical）
- ✅ 使用抑制规则减少告警风暴
- ✅ 定期审查和优化告警规则
- ❌ 不要设置过多告警（告警疲劳）
- ❌ 不要设置过敏感的阈值（频繁触发）
- ❌ 不要只告警不处理（建立告警响应流程）

---

## 八、常见问题与排查

### 1. 指标抓取失败
**排查步骤**
```bash
# 1. 检查目标状态
curl http://prometheus:9090/api/v1/targets

# 2. 检查目标是否可访问
curl http://target:9100/metrics

# 3. 检查网络连通性
telnet target 9100
ping target

# 4. 检查防火墙
iptables -L -n | grep 9100

# 5. 检查 Prometheus 日志
docker logs prometheus
```

**常见原因**
| 原因 | 解决方案 |
|------|---------|
| 目标服务未启动 | 启动目标服务或 Exporter |
| 端口未开放 | 开放端口或检查防火墙 |
| 网络不通 | 检查网络配置和路由 |
| 抓取路径错误 | 检查 metrics_path 配置 |
| 认证失败 | 检查 basic_auth 或 bearer_token 配置 |
| TLS 证书问题 | 检查 scheme 和 tls_config |

### 2. 查询无数据
**排查步骤**
```promql
# 1. 检查指标是否存在
http_requests_total

# 2. 检查标签是否正确
http_requests_total{job="api-server"}

# 3. 检查时间范围
http_requests_total[5m]

# 4. 检查目标状态
up{job="api-server"}
```

**常见原因**
| 原因 | 解决方案 |
|------|---------|
| 指标名错误 | 检查指标名拼写 |
| 标签不匹配 | 检查标签名和值 |
| 时间范围不对 | 调整时间范围 |
| 目标未抓取 | 检查目标状态和抓取配置 |
| 数据已过期 | 检查数据保留时间 |

### 3. 告警未触发
**排查步骤**
```promql
# 1. 检查告警规则表达式
expr: up == 0

# 2. 在 Prometheus 中执行表达式
up == 0

# 3. 检查规则状态
curl http://prometheus:9090/api/v1/rules

# 4. 检查告警状态
curl http://prometheus:9090/api/v1/alerts

# 5. 检查 Alertmanager 状态
curl http://alertmanager:9093/api/v2/alerts
```

**常见原因**
| 原因 | 解决方案 |
|------|---------|
| 表达式错误 | 检查 PromQL 表达式语法 |
| 阈值设置过高 | 调整阈值 |
| for 持续时间未到 | 等待持续时间或调整 |
| 规则未加载 | 检查 rule_files 配置和语法 |
| Alertmanager 未配置 | 检查 alerting 配置 |
| 告警被抑制 | 检查 inhibit_rules 配置 |

### 4. 存储压力大
**排查步骤**
```bash
# 1. 查看存储大小
du -sh /prometheus

# 2. 查看时间序列数量
curl http://prometheus:9090/api/v1/status/tsdb

# 3. 查看高基数指标
topk(10, count by (__name__) ({__name__=~".+"}))

# 4. 查看 Prometheus 资源使用
docker stats prometheus
```

**常见原因和解决方案**
| 原因 | 解决方案 |
|------|---------|
| 高基数指标 | 减少标签基数或使用 recording rules 预聚合 |
| 抓取间隔过短 | 增加抓取间隔 |
| 保留时间过长 | 缩短数据保留时间 |
| 指标过多 | 使用 metric_relabel 过滤不需要的指标 |
| 单机性能不足 | 使用联邦集群或远程存储 |

---

## 🔗 关联笔记

**监控可观测**
- [[APM应用性能监控-SkyWalking]] — SkyWalking APM 应用性能监控
- [[ELK-日志聚合]] — ELK 日志聚合
- [[Jaeger-分布式链路追踪]] — Jaeger 分布式链路追踪
- [[Sentry错误监控与追踪]] — Sentry 错误监控
- [[告警体系设计]] — 告警体系设计

**云原生运维**
- [[Docker容器化]] — Docker 容器化
- [[Docker容器化实战]] — Docker 容器化实战
- [[Kubernetes 知识点系统梳理_优化版]] — Kubernetes 容器编排
- [[CI-CD持续集成与部署]] — CI/CD 流水线
- [[DevOps与云原生知识点完整整合大全_优化版]] — DevOps 与云原生完整知识体系

---

## 📖 学习路径建议

1. **入门**：理解 Prometheus 核心概念，安装部署，配置基本抓取和 Grafana 可视化
2. **进阶**：学习 PromQL 查询语言，配置告警规则和 Alertmanager，集成常用 Exporters
3. **高级**：深入 Prometheus 架构和 TSDB 原理，学习服务发现、relabel、联邦集群，性能优化
4. **专家**：设计企业级监控体系，高可用部署，长期存储，与 AIOps 结合，监控即代码

---

## 💡 精简总结

Prometheus 是云原生时代的事实标准监控系统，通过多维数据模型（指标名+标签）、强大的 PromQL 查询语言、高效的时序数据库和灵活的告警机制，为容器化应用和微服务架构提供完整的可观测性解决方案。核心组件包括 Prometheus Server（抓取存储查询）、Exporters（指标暴露）、Alertmanager（告警管理）、Pushgateway（推送网关）。四种核心指标类型：Counter（计数器）、Gauge（仪表盘）、Histogram（直方图）、Summary（摘要）。PromQL 支持聚合（sum/avg/topk）、计算（rate/increase/histogram_quantile）、预测（predict_linear）等复杂操作。最佳实践包括：合理的指标命名和标签使用、适当的抓取间隔、分级告警和抑制规则、存储优化和高可用部署。Prometheus 与 Grafana 深度集成，提供丰富的可视化仪表盘，是现代运维和 SRE 必备的监控工具。

---

> **监控的本质不是收集数据，而是在问题发生前发现异常，在问题发生时快速定位，在问题解决后防止复发。**

[[Home|🏠 返回首页]] · [[MOC-云原生与运维|☁️ 云原生与运维]] · [[学习路线总览|🗺️ 学习路线]]
