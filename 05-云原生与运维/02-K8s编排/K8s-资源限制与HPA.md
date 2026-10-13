---
title: K8s资源限制与HPA
tags: [Kubernetes, 资源限制, HPA, 自动扩缩容, 水平Pod自动伸缩, VPA, 资源管理, 枢纽笔记]
category: 云原生与运维
created: 2026-08-13
updated: 2026-08-28
difficulty: ⭐⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[K8s-核心概念与架构]]"]
aliases: [K8s-资源限制与HPA]
---

# 📈 K8s 资源限制与 HPA 自动扩缩容

> **文档说明**：系统讲解 Kubernetes 资源管理与自动扩缩容的完整知识体系，涵盖资源请求（Requests）与限制（Limits）、CPU/内存资源单位、QoS 等级（Guaranteed/Burstable/BestEffort）、LimitRange 与 ResourceQuota、HPA（水平 Pod 自动伸缩）原理与配置、HPA 算法（平均利用率/自定义指标/外部指标）、VPA（垂直 Pod 自动伸缩）、Cluster Autoscaler（节点自动伸缩）、KEDA 事件驱动扩缩容、扩缩容最佳实践、常见问题排查。
>
> **适用人群**：运维工程师、DevOps、后端开发者、SRE、Kubernetes 学习者
>
> **前置知识**：[[K8s-核心概念与架构]] · [[K8s-Pod与控制器]]

---

## 一、概述

### 1.1 为什么需要资源管理

Kubernetes 集群中，多个 Pod 共享节点的 CPU 和内存资源。如果不做资源限制，可能出现：

| 问题 | 说明 | 后果 |
|------|------|------|
| **资源争抢** | 某个 Pod 占用大量 CPU/内存，影响其他 Pod | 服务变慢、OOM 被杀 |
| **调度不合理** | 调度器不知道 Pod 需要多少资源，可能调度到资源不足的节点 | Pod 无法正常运行 |
| **OOM 频繁** | 内存无限制，Pod 内存泄漏导致节点内存耗尽 | 节点不可用、Pod 被驱逐 |
| **成本浪费** | 资源申请过多，实际使用率低 | 集群资源闲置、成本高 |
| **无法扩缩容** | 没有资源指标，无法判断何时扩容 | 流量高峰时服务崩溃 |

**资源管理的目标**：
- **稳定性**：保证每个 Pod 有足够资源，不被其他 Pod 影响
- **可预测性**：调度器根据资源请求合理调度
- **成本优化**：合理配置资源，避免浪费
- **弹性伸缩**：根据负载自动调整 Pod 数量和资源

### 1.2 K8s 资源管理体系

```mermaid
flowchart TB
    subgraph 资源配置["资源配置"]
        A[Pod 资源请求/限制<br/>Requests/Limits]
        B[LimitRange<br/>命名空间默认值]
        C[ResourceQuota<br/>命名空间配额]
    end
    
    subgraph 自动扩缩容["自动扩缩容"]
        D[HPA<br/>水平Pod自动伸缩]
        E[VPA<br/>垂直Pod自动伸缩]
        F[Cluster Autoscaler<br/>节点自动伸缩]
        G[KEDA<br/>事件驱动扩缩容]
    end
    
    资源配置 --> 自动扩缩容
    
    style 资源配置 fill:#667eea,color:#fff
    style 自动扩缩容 fill:#43e97b,color:#333
```

---

## 二、资源请求与限制

### 2.1 Requests vs Limits

每个容器可以配置 `resources.requests`（资源请求）和 `resources.limits`（资源限制）。

| 字段 | 说明 | 作用 |
|------|------|------|
| **requests.cpu** | 容器请求的 CPU 量 | 调度依据：调度器只考虑有足够可分配 CPU 的节点 |
| **requests.memory** | 容器请求的内存量 | 调度依据：调度器只考虑有足够可分配内存的节点 |
| **limits.cpu** | 容器 CPU 使用上限 | 运行时限制：超过会被节流（throttle），不会被杀 |
| **limits.memory** | 容器内存使用上限 | 运行时限制：超过会被 OOM Kill（杀死容器） |

**关键区别**：
- **Requests** 是「调度承诺」——K8s 保证容器至少能拿到这么多资源
- **Limits** 是「使用上限」——容器最多能用这么多，超过会被限制或杀死
- Requests ≤ Limits（CPU 可以 requests < limits，内存也可以）
- 不配置 requests 时，默认等于 limits
- 不配置 limits 时，容器可以使用节点全部资源（危险）

### 2.2 资源单位

**CPU 单位**：
| 单位 | 说明 | 换算 |
|------|------|------|
| **核（Core）** | 1 个物理核或虚拟核 | 1 = 1000m |
| **毫核（millicore/m）** | 千分之一个核 | 100m = 0.1 核 |
| **示例** | | |
| `1` | 1 个核 | = 1000m |
| `500m` | 0.5 个核 | = 半核 |
| `100m` | 0.1 个核 | = 10% 核 |
| `2` | 2 个核 | = 2000m |

> CPU 是可压缩资源（compressible）：超过 limits 会被节流（throttle），进程变慢但不会被杀。

**内存单位**：
| 单位 | 说明 | 换算 |
|------|------|------|
| **Ki** | 千比字节（Kibibyte） | 1Ki = 1024 字节 |
| **Mi** | 兆比字节（Mebibyte） | 1Mi = 1024Ki = 1048576 字节 |
| **Gi** | 吉比字节（Gibibyte） | 1Gi = 1024Mi |
| **K** | 千字节（Kilobyte） | 1K = 1000 字节 |
| **M** | 兆字节（Megabyte） | 1M = 1000K = 1000000 字节 |
| **G** | 吉字节（Gigabyte） | 1G = 1000M |

> 推荐使用 `Mi`/`Gi`（二进制），避免与 `M`/`G`（十进制）混淆。
> 内存是不可压缩资源（incompressible）：超过 limits 会被 OOM Kill（杀死容器）。

### 2.3 资源配置示例

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: app
    image: nginx:latest
    resources:
      requests:
        cpu: "100m"        # 请求 0.1 核
        memory: "128Mi"    # 请求 128MB 内存
      limits:
        cpu: "500m"        # 上限 0.5 核
        memory: "256Mi"    # 上限 256MB 内存
```

**不同场景的资源配置建议**：

| 场景 | CPU Requests | CPU Limits | Memory Requests | Memory Limits |
|------|-------------|-----------|----------------|--------------|
| **生产关键服务** | 500m-2 | 1-4 | 512Mi-2Gi | 1Gi-4Gi |
| **普通 Web 服务** | 100m-500m | 500m-2 | 128Mi-512Mi | 256Mi-1Gi |
| **后台任务/Worker** | 200m-1 | 1-4 | 256Mi-1Gi | 512Mi-2Gi |
| **数据库** | 1-4 | 2-8 | 2Gi-8Gi | 4Gi-16Gi |
| **缓存（Redis）** | 500m-2 | 1-4 | 1Gi-4Gi | 2Gi-8Gi |
| **开发/测试** | 50m-100m | 200m-500m | 64Mi-128Mi | 128Mi-256Mi |

> **配置原则**：① requests 基于实际平均负载设置（略高于平均） ② limits 基于峰值负载设置（略高于峰值） ③ 内存 limits 要谨慎，超过会 OOM Kill ④ CPU limits 可以宽松，超过只是节流 ⑤ 通过监控（metrics-server/Prometheus）观察实际使用，持续调整。

### 2.4 QoS 等级

Kubernetes 根据 Pod 的资源配置为其分配 QoS（Quality of Service）等级，决定 Pod 的调度和驱逐优先级。

| QoS 等级 | 条件 | 说明 | 驱逐优先级 |
|---------|------|------|-----------|
| **Guaranteed** | 每个容器都设置了 requests 和 limits，且 requests = limits（CPU 和内存都要） | 最高优先级，资源有保证 | 最后被驱逐 |
| **Burstable** | 至少一个容器设置了 requests 或 limits，但不满足 Guaranteed 条件 | 中等优先级，资源有最低保证 | 中间被驱逐 |
| **BestEffort** | 所有容器都没有设置 requests 和 limits | 最低优先级，资源无保证 | 最先被驱逐 |

```mermaid
flowchart LR
    A[Pod 资源配置] --> B{所有容器都有<br/>requests=limits?}
    B -->|是| C[Guaranteed<br/>最高优先级]
    B -->|否| D{至少一个容器有<br/>requests或limits?}
    D -->|是| E[Burstable<br/>中等优先级]
    D -->|否| F[BestEffort<br/>最低优先级]
    
    style C fill:#43e97b,color:#333
    style E fill:#feca57,color:#333
    style F fill:#ff6b6b,color:#fff
```

**QoS 示例**：
```yaml
# Guaranteed：requests = limits
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"

# Burstable：有 requests 但不等于 limits
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"

# BestEffort：没有 resources 配置
# （不写 resources 字段）
```

> **节点资源不足时的驱逐顺序**：BestEffort → Burstable（超出 requests 最多的先驱逐）→ Guaranteed（最后驱逐，且只有在超出 limits 或节点系统资源不足时才驱逐）。

---

## 三、LimitRange 与 ResourceQuota

### 3.1 LimitRange

LimitRange 为命名空间内的 Pod/容器设置默认资源请求和限制，避免每个容器都手动配置。

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: production
spec:
  limits:
  - type: Container
    default:                    # 默认 limits
      cpu: "500m"
      memory: "256Mi"
    defaultRequest:             # 默认 requests
      cpu: "100m"
      memory: "128Mi"
    max:                        # 最大 limits
      cpu: "2"
      memory: "2Gi"
    min:                        # 最小 requests
      cpu: "50m"
      memory: "64Mi"
    maxLimitRequestRatio:       # limits/requests 最大比值
      cpu: "4"
      memory: "2"
```

**LimitRange 的作用**：
- 未配置 resources 的容器自动应用默认值
- 防止容器申请过大或过小的资源
- 限制 limits/requests 比值，防止资源超卖

### 3.2 ResourceQuota

ResourceQuota 限制命名空间的总资源使用量，防止一个命名空间占用整个集群。

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: team-a
spec:
  hard:
    # 计算资源
    requests.cpu: "10"              # 总 CPU requests 不超过 10 核
    requests.memory: 20Gi           # 总内存 requests 不超过 20Gi
    limits.cpu: "20"                # 总 CPU limits 不超过 20 核
    limits.memory: 40Gi             # 总内存 limits 不超过 40Gi
    
    # 对象数量
    pods: "50"                       # 最多 50 个 Pod
    services: "10"                   # 最多 10 个 Service
    persistentvolumeclaims: "20"     # 最多 20 个 PVC
    configmaps: "20"                 # 最多 20 个 ConfigMap
    secrets: "20"                    # 最多 20 个 Secret
    
    # 存储资源
    requests.storage: 100Gi          # 总存储请求不超过 100Gi
```

**ResourceQuota 的作用**：
- 按团队/项目划分资源配额
- 防止资源滥用
- 多租户环境的资源隔离

---

## 四、HPA 水平 Pod 自动伸缩

### 4.1 HPA 原理

HPA（Horizontal Pod Autoscaler）根据 CPU/内存利用率或自定义指标，自动调整 Deployment/StatefulSet 的 Pod 副本数。

```mermaid
flowchart LR
    A[metrics-server<br/>采集资源指标] --> B[HPA Controller<br/>计算目标副本数]
    B --> C[调整 Deployment<br/>replicas 数量]
    C --> D[Pod 数量变化]
    D -->|流量增加| E[扩容 Pod]
    D -->|流量减少| F[缩容 Pod]
    
    style A fill:#667eea,color:#fff
    style B fill:#f093fb,color:#fff
    style C fill:#43e97b,color:#333
```

**HPA 工作流程**：
1. metrics-server 定期采集所有 Pod 的 CPU/内存使用率
2. HPA Controller 每隔 15 秒（默认）检查指标
3. 根据当前指标和目标指标，计算需要的副本数
4. 如果需要调整，修改 Deployment 的 replicas
5. Deployment 控制器创建或删除 Pod

**HPA 算法公式**：
```text
期望副本数 = ceil(当前副本数 × (当前指标 / 目标指标))

示例：
- 当前 3 个 Pod
- 当前 CPU 平均利用率 80%
- 目标 CPU 利用率 50%
- 期望副本数 = ceil(3 × (80% / 50%)) = ceil(3 × 1.6) = ceil(4.8) = 5 个 Pod
```

### 4.2 HPA 配置（CPU/内存指标）

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 3          # 最少 3 个 Pod
  maxReplicas: 20         # 最多 20 个 Pod
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60   # CPU 平均利用率目标 60%
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70   # 内存平均利用率目标 70%
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60    # 扩容前稳定 60 秒
      policies:
      - type: Percent
        value: 100                       # 每次最多扩容 100%（翻倍）
        periodSeconds: 60
      - type: Pods
        value: 4                         # 每次最多扩容 4 个
        periodSeconds: 60
      selectPolicy: Max                   # 取两个策略中的最大值
    scaleDown:
      stabilizationWindowSeconds: 300   # 缩容前稳定 300 秒（防止抖动）
      policies:
      - type: Percent
        value: 50                        # 每次最多缩容 50%
        periodSeconds: 60
      selectPolicy: Min
```

### 4.3 HPA 关键参数

| 参数 | 说明 | 默认值 | 建议 |
|------|------|--------|------|
| **minReplicas** | 最小副本数 | 1 | 根据最低负载设置，生产环境 ≥2 |
| **maxReplicas** | 最大副本数 | — | 根据集群资源和峰值负载设置 |
| **averageUtilization** | 目标利用率（基于 requests） | — | CPU 60-70%，内存 70-80% |
| **stabilizationWindowSeconds（扩容）** | 扩容前指标稳定窗口 | 0 | 30-60 秒，防止瞬时峰值导致频繁扩容 |
| **stabilizationWindowSeconds（缩容）** | 缩容前指标稳定窗口 | 300 | 300-600 秒，缩容要保守，防止抖动 |
| **scaleUp policies** | 扩容速率策略 | — | 每次最多扩容 100% 或 4 个 Pod |
| **scaleDown policies** | 缩容速率策略 | — | 每次最多缩容 50%，保守缩容 |

> **重要**：HPA 的 CPU/内存利用率是基于 `resources.requests` 计算的，不是基于 limits。所以必须配置 requests，否则 HPA 无法计算利用率。

### 4.4 自定义指标与外部指标

HPA v2 支持基于自定义指标（Custom Metrics）和外部指标（External Metrics）扩缩容。

**自定义指标**（Pod 级别的指标，如 QPS、请求延迟、队列长度）：
```yaml
metrics:
- type: Pods
  pods:
    metric:
      name: http_requests_per_second
    target:
      type: AverageValue
      averageValue: "100"   # 每个 Pod 平均 100 QPS
```

**外部指标**（非 Pod 级别的指标，如消息队列长度、SQS 队列深度）：
```yaml
metrics:
- type: External
  external:
    metric:
      name: rabbitmq_queue_messages
      selector:
        matchLabels:
          queue: orders
    target:
      type: AverageValue
      averageValue: "10"    # 每个 Pod 处理 10 条消息
```

> 自定义指标需要部署 Prometheus Adapter 或 Prometheus Metrics Adapter，将 Prometheus 指标暴露给 HPA。

### 4.5 HPA 常用命令

```bash
# 查看 HPA 列表
kubectl get hpa -A

# 查看 HPA 详情
kubectl describe hpa web-app-hpa -n production

# 查看 HPA 状态（实时）
kubectl get hpa web-app-hpa -n production -w

# 创建 HPA（命令行方式）
kubectl autoscale deployment web-app --cpu-percent=60 --min=3 --max=20 -n production

# 删除 HPA
kubectl delete hpa web-app-hpa -n production

# 查看 metrics-server 是否正常
kubectl top nodes
kubectl top pods -A

# 查看 HPA 事件（排查问题）
kubectl get events -n production --field-selector involvedObject.kind=HorizontalPodAutoscaler
```

---

## 五、VPA 垂直 Pod 自动伸缩

### 5.1 VPA 原理

VPA（Vertical Pod Autoscaler）根据 Pod 的历史资源使用情况，自动调整 Pod 的 resources.requests 和 limits。

**VPA vs HPA**：
| 维度 | HPA | VPA |
|------|-----|-----|
| **伸缩方向** | 水平（增加/减少 Pod 数量） | 垂直（增加/减少单个 Pod 资源） |
| **调整对象** | Deployment replicas | Pod resources.requests/limits |
| **适用场景** | 无状态服务、流量波动大 | 有状态服务、资源需求变化 |
| **是否重启 Pod** | 不重启（增减 Pod） | 需要重启（修改 resources） |
| **成熟度** | GA（稳定） | Beta（较稳定） |

> **注意**：HPA 和 VPA 不能同时基于 CPU/内存指标使用（会冲突），可以 HPA 基于自定义指标 + VPA 基于 CPU/内存。

### 5.2 VPA 配置

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-app-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: web-app
  updatePolicy:
    updateMode: "Auto"    # Auto=自动调整并重启, Off=只推荐不应用, Initial=只在创建时应用, Recreate=强制重启
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        cpu: "100m"
        memory: "128Mi"
      maxAllowed:
        cpu: "2"
        memory: "2Gi"
      controlledResources: ["cpu", "memory"]
```

**VPA 的四种模式**：
| 模式 | 说明 |
|------|------|
| **Off** | 只计算推荐值，不应用（用于观察和分析） |
| **Initial** | 只在 Pod 创建时应用推荐值，运行中不调整 |
| **Auto** | 自动调整 resources，必要时重启 Pod |
| **Recreate** | 与 Auto 类似，但会强制重启 Pod（即使 resources 变化小） |

---

## 六、Cluster Autoscaler 节点自动伸缩

### 6.1 原理

Cluster Autoscaler（CA）根据 Pod 调度状态自动调整集群节点数量：
- 有 Pod 因节点资源不足而 Pending（无法调度）→ 增加节点
- 节点资源利用率低且 Pod 可以调度到其他节点 → 减少节点

```mermaid
flowchart LR
    A[Pod Pending<br/>无法调度] --> B[Cluster Autoscaler]
    C[节点利用率低<br/>Pod可迁移] --> B
    B --> D{需要扩容?}
    D -->|是| E[调用云API<br/>增加节点]
    D -->|否| F{需要缩容?}
    F -->|是| G[驱逐Pod<br/>删除节点]
    F -->|否| H[保持不变]
    
    style B fill:#667eea,color:#fff
    style E fill:#43e97b,color:#333
    style G fill:#ff6b6b,color:#fff
```

### 6.2 配置要点

| 配置 | 说明 |
|------|------|
| **--nodes** | 节点组的最小/最大数量，如 `--nodes=3:10:worker-group` |
| **--scale-down-delay-after-add** | 扩容后多久才考虑缩容（默认 10 分钟） |
| **--scale-down-unneeded-time** | 节点空闲多久后才缩容（默认 10 分钟） |
| **--scale-down-utilization-threshold** | 节点利用率低于多少算空闲（默认 0.5） |
| **--expander** | 扩容时选择节点组的策略（random/most-pods/least-waste/price） |

> Cluster Autoscaler 需要云厂商支持（AWS EKS/GCP GKE/Azure AKS/阿里云 ACK），通过云 API 增减节点。本地集群可以用 KubeKey/k3s 等方案。

---

## 七、KEDA 事件驱动扩缩容

### 7.1 KEDA 简介

KEDA（Kubernetes Event-driven Autoscaling）是 HPA 的扩展，支持基于事件源（消息队列、数据库、定时任务等）的自动扩缩容。

**KEDA 支持的触发器**：
| 类型 | 触发器 |
|------|--------|
| **消息队列** | Kafka、RabbitMQ、Redis Streams、NATS、AWS SQS、Azure Service Bus |
| **数据库** | MySQL、PostgreSQL、MSSQL、MongoDB、Redis |
| **定时任务** | Cron |
| **监控** | Prometheus、Datadog、New Relic |
| **存储** | Azure Blob、AWS S3、Google Cloud Storage |
| **其他** | HTTP、GraphQL、Elasticsearch、Zookeeper |

### 7.2 KEDA 配置示例

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: rabbitmq-consumer-scaler
  namespace: production
spec:
  scaleTargetRef:
    name: order-consumer        # 目标 Deployment
  minReplicaCount: 0            # 可以缩到 0（无消息时不占资源）
  maxReplicaCount: 50           # 最多 50 个
  triggers:
  - type: rabbitmq
    metadata:
      host: amqp://user:pass@rabbitmq:5672/
      queueName: orders
      mode: QueueLength
      value: "10"               # 每个 Pod 处理 10 条消息
```

**KEDA 的优势**：
- 支持缩容到 0（无事件时不占资源，节省成本）
- 丰富的事件源支持（50+ 触发器）
- 基于 HPA 构建，稳定可靠
- 适合消息驱动的微服务、定时任务、事件处理

---

## 八、最佳实践

### 8.1 资源配置最佳实践

| 实践 | 说明 |
|------|------|
| **必须配置 requests** | HPA 基于 requests 计算利用率，调度器基于 requests 调度 |
| **生产环境配置 limits** | 防止资源泄漏影响其他 Pod，内存 limits 超过会 OOM Kill |
| **通过监控调整** | 用 Prometheus/Grafana 观察实际使用率，持续优化 requests/limits |
| **Guaranteed QoS** | 关键服务设置 requests = limits，获得最高优先级 |
| **LimitRange 默认值** | 为命名空间设置默认资源，防止遗漏配置 |
| **ResourceQuota 配额** | 按团队划分资源配额，防止资源滥用 |
| **内存 limits 谨慎** | 内存超过 limits 会 OOM Kill，建议 limits 比峰值高 20-30% |
| **CPU limits 可宽松** | CPU 超过 limits 只是节流，不会被杀，可以适当宽松 |

### 8.2 HPA 最佳实践

| 实践 | 说明 |
|------|------|
| **配置 minReplicas ≥ 2** | 生产环境至少 2 个 Pod，保证高可用 |
| **缩容窗口要长** | stabilizationWindowSeconds 300-600 秒，防止抖动 |
| **扩容窗口适中** | 30-60 秒，既能响应峰值，又不会因瞬时波动频繁扩容 |
| **maxReplicas 合理** | 根据集群资源和峰值负载设置，不要过大 |
| **基于 requests 的利用率** | 确保 requests 设置合理，否则利用率计算不准 |
| **自定义指标更精准** | CPU/内存是间接指标，用 QPS/延迟/队列长度更精准 |
| **预热（Warm-up）** | 扩容后 Pod 需要启动时间，考虑用 minReplicas 预留容量 |
| **配合 PDB** | 用 PodDisruptionBudget 保证缩容时服务可用 |
| **监控 HPA** | 监控 HPA 的当前副本数、目标值、当前值，及时发现异常 |

### 8.3 扩缩容组合策略

```mermaid
flowchart TB
    A[流量增加] --> B[HPA 扩容 Pod]
    B --> C{节点资源足够?}
    C -->|是| D[Pod 调度成功]
    C -->|否| E[Cluster Autoscaler<br/>扩容节点]
    E --> F[新节点加入集群]
    F --> D
    
    G[流量减少] --> H[HPA 缩容 Pod]
    H --> I{节点利用率低?}
    I -->|是| J[Cluster Autoscaler<br/>缩容节点]
    I -->|否| K[保持节点]
    
    style B fill:#43e97b,color:#333
    style E fill:#feca57,color:#333
    style H fill:#ff6b6b,color:#fff
    style J fill:#ff6b6b,color:#fff
```

**三层扩缩容体系**：
1. **HPA**：Pod 级别的水平伸缩（最快，秒级）
2. **VPA**：Pod 级别的垂直伸缩（较慢，需重启）
3. **Cluster Autoscaler**：节点级别的伸缩（最慢，分钟级）

> 三层配合：HPA 先响应流量变化调整 Pod 数，如果节点资源不足，Cluster Autoscaler 增加节点；流量减少时，HPA 先减少 Pod，节点空闲后 Cluster Autoscaler 减少节点。

---

## 九、常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **HPA 显示 unknown** | metrics-server 未部署或不正常 | 部署 metrics-server，`kubectl top pods` 验证 |
| **HPA 不扩容** | 指标未达到目标值 / targets 未就绪 / 指标采集延迟 | 检查 `kubectl describe hpa`，查看当前指标和目标 |
| **HPA 频繁扩缩容（抖动）** | 稳定窗口太短 / 指标波动大 | 增加 stabilizationWindowSeconds，扩容 60s 缩容 300s |
| **Pod 被 OOM Kill** | 内存 limits 设置过低 / 内存泄漏 | 增加 memory limits，排查内存泄漏 |
| **Pod CPU 被节流（throttle）** | CPU limits 设置过低 | 增加 CPU limits 或检查是否需要 limits |
| **Pod 一直 Pending** | 节点资源不足 / 亲和性约束 / 资源配额满 | `kubectl describe pod` 查看事件，检查节点资源和 ResourceQuota |
| **节点资源不足但不扩容** | Cluster Autoscaler 未配置 / 达到 maxNodes / 扩容延迟 | 检查 CA 配置和日志，确认节点组 maxNodes |
| **节点空闲但不缩容** | 有 PDB 保护 / 有本地存储 / 缩容窗口未到 | 检查 PDB、PVC、缩容配置 |
| **HPA 利用率计算异常** | requests 未设置 / 部分容器未设置 requests | 确保所有容器都设置了 requests |
| **VPA 和 HPA 冲突** | 同时基于 CPU/内存指标 | HPA 用自定义指标，VPA 用 CPU/内存，或只用一个 |
| **扩容后 Pod 启动慢** | 镜像大 / 启动慢 / 没有就绪探针 | 优化镜像，配置 readinessProbe，考虑预热 |

**排查命令**：
```bash
# 1. 检查 metrics-server
kubectl top nodes
kubectl top pods -A

# 2. 查看 HPA 详情
kubectl describe hpa <hpa-name> -n <namespace>

# 3. 查看 Pod 资源使用
kubectl top pod <pod-name> -n <namespace> --containers

# 4. 查看 Pod 资源配置
kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.containers[*].resources}'

# 5. 查看节点资源
kubectl describe node <node-name> | grep -A 10 "Allocated resources"

# 6. 查看 ResourceQuota
kubectl get resourcequota -n <namespace>
kubectl describe resourcequota <quota-name> -n <namespace>

# 7. 查看 LimitRange
kubectl get limitrange -n <namespace>
kubectl describe limitrange <lr-name> -n <namespace>

# 8. 查看驱逐事件
kubectl get events -n <namespace> --field-selector reason=OOMKilling
kubectl get events -n <namespace> --field-selector reason=Preempting
```

---

## 十、关联笔记

### K8s 核心
- [[K8s-核心概念与架构]] · [[K8s-Pod与控制器]] · [[K8s-故障排查手册]]
- [[K8s-网络模型]] · [[K8s-存储管理]]

### 云原生与运维
- [[Docker容器化]] · [[Prometheus监控体系]] · [[服务网格Istio]]
- [[CI-CD流水线]] · [[Linux性能调优]]

### 性能与架构
- [[高可用架构设计]] · [[性能优化方法论]] · [[微服务架构设计]]

### 导航
- [[MOC-云原生与运维]] · [[MOC-K8s编排]] · [[MOC-综合导航]] · [[Home]]

> 🔍 **知识点深度解析**
>
> **作用**：K8s 资源限制与 HPA 解决的是「集群资源高效利用与弹性伸缩」问题——通过 Requests/Limits 为每个 Pod 配置资源请求和上限，保证服务稳定性和可预测性；通过 HPA 根据负载自动调整 Pod 副本数，实现弹性伸缩，应对流量波动；通过 LimitRange/ResourceQuota 实现命名空间级别的资源管理和配额；通过 VPA/Cluster Autoscaler 实现垂直和节点级别的伸缩。目标是在保证服务稳定的前提下，最大化资源利用率，最小化成本。
>
> **底层原理**：K8s 资源管理的核心是「Requests 用于调度，Limits 用于运行时限制」。调度器（kube-scheduler）根据 Pod 的 requests.cpu 和 requests.memory 判断节点是否有足够可分配资源（节点可分配资源 = 节点总资源 - 系统预留 - 已分配 requests），只有可分配资源 ≥ Pod requests 的节点才会被选中。运行时，kubelet 通过 cgroups 限制容器资源：CPU 用 CFS（完全公平调度器）限制，超过 limits 会被节流（throttle）但不会被杀；内存用 memory cgroup 限制，超过 limits 会触发 OOM Killer 杀死容器。QoS 等级（Guaranteed/Burstable/BestEffort）由 requests 和 limits 的配置决定，影响节点资源不足时的驱逐顺序。HPA 的原理是「基于指标的反馈控制」：metrics-server 采集 Pod 的 CPU/内存使用率，HPA Controller 定期（默认 15s）计算期望副本数 = ceil(当前副本数 × 当前指标/目标指标)，然后调整 Deployment 的 replicas。HPA v2 还支持自定义指标（Prometheus Adapter）和外部指标（消息队列等）。扩缩容有稳定窗口（stabilizationWindow）防止抖动，扩容策略控制扩容速率，缩容策略控制缩容速率。
>
> **用法要点**：① 必须配置 requests（HPA 基于 requests 计算利用率，调度器基于 requests 调度） ② 生产环境配置 limits（内存 limits 超过会 OOM Kill，CPU 超过只是节流） ③ requests 基于平均负载设置（略高于平均），limits 基于峰值设置（略高于峰值） ④ 关键服务用 Guaranteed QoS（requests=limits），获得最高驱逐优先级 ⑤ HPA 配置：minReplicas≥2，maxReplicas 根据峰值设置，CPU 目标 60-70%，内存 70-80% ⑥ 缩容窗口要长（300-600s）防止抖动，扩容窗口适中（30-60s） ⑦ HPA 基于 CPU/内存时不能和 VPA 同时用（冲突），可以 HPA 用自定义指标 + VPA 用 CPU/内存 ⑧ 三层伸缩体系：HPA（Pod 水平，秒级）→ VPA（Pod 垂直，需重启）→ Cluster Autoscaler（节点，分钟级） ⑨ KEDA 支持事件驱动扩缩容和缩容到 0，适合消息驱动微服务 ⑩ 常见问题：HPA unknown（metrics-server 未部署）、OOM Kill（内存 limits 低）、CPU 节流（CPU limits 低）、频繁抖动（稳定窗口短）、Pod Pending（节点资源不足/配额满）。

> 💡 **深度讲解**：K8s 资源管理最容易踩的坑是「不理解 requests 和 limits 的区别」。requests 是「调度承诺」——K8s 保证容器至少能拿到这么多资源，调度器只看 requests 不看 limits；limits 是「使用上限」——容器最多能用这么多，超过会被限制。很多人以为配置了 limits 就安全了，但如果没配置 requests，调度器可能把 Pod 调度到已经超卖的节点（因为调度器不看 limits），导致运行时资源争抢。另一个关键点是「CPU 和内存的性质不同」：CPU 是可压缩资源，超过 limits 只是被节流（进程变慢），不会被杀；内存是不可压缩资源，超过 limits 会被 OOM Killer 直接杀死容器。所以内存 limits 要特别谨慎，建议比实际峰值高 20-30%，而 CPU limits 可以适当宽松。HPA 的目标利用率是基于 requests 计算的，不是基于 limits 或节点总资源——这是另一个常见误区。如果 requests 设置得太高（比如实际只用 100m 但 requests 设了 1000m），HPA 计算的利用率会很低（10%），永远不会触发扩容，导致流量高峰时服务崩溃。所以 requests 的设置要合理，基于实际平均负载，略高于平均值。HPA 的稳定窗口（stabilizationWindow）是防止抖动的关键：扩容前指标要持续超过目标一段时间才扩容，缩容前指标要持续低于目标一段时间才缩容。缩容窗口通常比扩容窗口长很多（扩容 60s，缩容 300s），因为缩容太激进可能导致服务不可用（Pod 删除后重建需要时间），而扩容太激进最多是浪费一些资源。三层扩缩容体系（HPA + VPA + Cluster Autoscaler）的配合也很重要：HPA 最快（秒级增减 Pod），VPA 较慢（需重启 Pod），Cluster Autoscaler 最慢（分钟级增减节点）。流量高峰时 HPA 先扩容 Pod，如果节点资源不足，Cluster Autoscaler 再扩容节点；流量下降时 HPA 先缩容 Pod，节点空闲后 Cluster Autoscaler 再缩容节点。这种分层设计保证了响应速度和成本效率的平衡。

> 📝 **精简总结**：K8s 资源管理 = Requests（调度承诺）+ Limits（使用上限）+ QoS（Guaranteed/Burstable/BestEffort）+ LimitRange（默认值）+ ResourceQuota（命名空间配额）。HPA = 基于 CPU/内存/自定义指标自动调整 Pod 副本数，公式：期望副本数=ceil(当前×当前指标/目标指标)。VPA = 自动调整 Pod 资源请求（需重启）。Cluster Autoscaler = 自动调整节点数。KEDA = 事件驱动扩缩容，支持缩容到 0。最佳实践：必须配 requests，生产配 limits，HPA min≥2，缩容窗口长（300s），三层伸缩配合。常见问题：HPA unknown（metrics-server）、OOM Kill（内存 limits 低）、抖动（稳定窗口短）、Pending（节点资源不足）。

> **学习路径建议**：先学习 [[K8s-核心概念与架构]] 掌握 K8s 基础 → 学习 [[K8s-Pod与控制器]] 理解 Pod 和 Deployment → 学习本文档掌握资源管理和自动扩缩容 → 学习 [[Prometheus监控体系]] 掌握监控和指标 → 学习 [[K8s-故障排查手册]] 掌握问题排查 → 在实践中配置和优化 HPA/资源限制。

---

> **K8s 资源管理的本质是「承诺与限制」——Requests 是对 Pod 的承诺（保证至少有这么多），Limits 是对 Pod 的限制（最多用这么多）。HPA 的本质是「反馈控制」——根据当前指标和目标指标的偏差，自动调整副本数。理解了这两个本质，你就能理解为什么 requests 决定调度、limits 决定运行时、HPA 基于 requests 计算、稳定窗口防止抖动。资源管理不是一次性配置，而是持续优化的过程——通过监控观察实际使用，不断调整 requests/limits/HPA 参数，在稳定性和成本之间找到最优平衡。**
