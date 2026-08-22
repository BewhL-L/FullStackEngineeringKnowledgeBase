---
title: Kubernetes 知识点系统梳理
tags: [云原生, Kubernetes, K8s, 容器, 运维]
created: 2026-08-12
updated: 2026-08-12
---

# Kubernetes 知识点系统梳理（优化版）

> **文档说明**：本文档参照《Java知识点完整整合大全》排版风格，系统梳理 Kubernetes（K8s）容器编排技术栈。包含概述、核心特性、常用用法、注意事项四大模块，辅以动态可视化解析图、深度讲解与精简总结。**优化版**在原有内容基础上，为每个知识点补充了作用、原理、用法的深度解析，并新增了知识点图解。

---

## 1. 概述

Kubernetes（简称 K8s）是 Google 开源的容器编排平台，用于自动化部署、扩展和管理容器化应用。它是云原生时代的操作系统，已成为容器编排的事实标准。

**核心定位**：
- 容器编排：自动化部署、调度、管理容器
- 服务发现与负载均衡：内置 Service、DNS、Ingress
- 自动扩缩容：根据 CPU/内存/自定义指标自动伸缩
- 自愈能力：容器故障自动重启、节点故障重新调度
- 滚动更新与回滚：零停机发布，一键回滚

**核心概念**：

| 概念 | 说明 |
|------|------|
| Cluster | 集群，由 Master 和 Node 组成 |
| Pod | 最小调度单位，一个或多个容器的组合 |
| Service | 服务，为 Pod 提供稳定访问入口 |
| Volume | 存储卷，解决容器数据持久化 |
| Namespace | 命名空间，资源隔离 |
| Label/Selector | 标签/选择器，资源关联机制 |

---


---
## 2. 核心特性

<div style="background:linear-gradient(135deg,#a8edea,#fed6e3);border-radius:16px;padding:24px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#1a1a2e;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes k8sPulse{0%,100%{transform:scale(1);opacity:.9}50%{transform:scale(1.04);opacity:1}}.k8s-master{background:rgba(255,255,255,.6);border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:12px;margin-bottom:10px;text-align:center;animation:k8sPulse 2.5s ease-in-out infinite}.k8s-node{display:inline-block;width:30%;vertical-align:top;margin:0 1%;background:rgba(255,255,255,.5);border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:10px;font-size:10px;text-align:center;animation:k8sPulse 2.5s ease-in-out infinite}.k8s-node:nth-child(2){animation-delay:.5s}.k8s-node:nth-child(3){animation-delay:1s}.k8s-comp{font-size:10px;margin:2px 0}.k8s-icon{font-size:18px}</style>
<div style="text-align:center;font-size:16px;font-weight:700;margin-bottom:16px;padding-bottom:12px;border-bottom:1.5px solid rgba(0,0,0,.1);letter-spacing:1px">Kubernetes 集群架构</div>
<div class="k8s-master">
<div style="font-size:14px;font-weight:700;margin-bottom:6px">🎛️ Master（控制平面）</div>
<div class="k8s-comp">API Server · etcd · Scheduler · Controller Manager</div>
</div>
<div style="text-align:center;font-size:12px;font-weight:700;margin:8px 0">⬇️ 管理 ⬇️</div>
<div style="text-align:center">
<div class="k8s-node"><div class="k8s-icon">🖥️</div><div style="font-weight:700">Node 1</div><div class="k8s-comp">kubelet · kube-proxy</div><div class="k8s-comp">Pod · Pod · Pod</div></div>
<div class="k8s-node"><div class="k8s-icon">🖥️</div><div style="font-weight:700">Node 2</div><div class="k8s-comp">kubelet · kube-proxy</div><div class="k8s-comp">Pod · Pod · Pod</div></div>
<div class="k8s-node"><div class="k8s-icon">🖥️</div><div style="font-weight:700">Node 3</div><div class="k8s-comp">kubelet · kube-proxy</div><div class="k8s-comp">Pod · Pod · Pod</div></div>
</div>
</div>

### 2.1 集群架构

**Master（控制平面）**：
- API Server：集群入口，所有操作通过它，RESTful API，负责认证授权
- etcd：分布式键值存储，保存集群所有状态（配置、状态、元数据）
- Scheduler：调度 Pod 到合适的 Node（资源、亲和性、污点容忍）
- Controller Manager：控制器集合（Node/Deployment/Service/Endpoint 控制器）

**Node（工作节点）**：
- kubelet：管理本节点 Pod 生命周期（创建/监控/重启）
- kube-proxy：网络代理，实现 Service 负载均衡（iptables/IPVS）
- 容器运行时：Docker/containerd，运行容器

> 🔍 **知识点深度解析**
>
> **作用**：K8s 集群架构采用 Master-Worker 模式，Master 负责管理和调度，Node 负责运行容器。理解各组件职责是排查 K8s 问题的基础。
>
> **原理**：API Server 是唯一与 etcd 交互的组件，其他组件通过 API Server 读写状态（声明式 API）。etcd 用 Raft 协议保证一致性（奇数节点，3或5个）。Scheduler 监听未调度的 Pod，通过过滤（Predicate）和打分（Priority）选择最优 Node。Controller Manager 是"控制循环"：监听资源状态，对比期望状态和实际状态，执行操作使实际状态趋近期望（如 Deployment 控制器保证副本数）。kubelet 通过 PodSpec 创建容器，定期上报 Pod 状态。kube-proxy 监听 Service/Endpoint，配置 iptables/IPVS 规则实现负载均衡。
>
> **用法要点**：① Master 节点高可用：API Server 多实例+负载均衡，etcd 3节点集群；② 生产环境 Master 不运行业务 Pod（用污点 NoSchedule）；③ Node 节点资源预留：system-reserved + kube-reserved，防止容器占满资源；④ 容器运行时：K8s 1.24+ 移除 dockershim，用 containerd 或 CRI-O；⑤ kube-proxy 模式：IPVS 比 iptables 性能好（大规模 Service）；⑥ etcd 是集群的"大脑"，必须备份（etcdctl snapshot save）。

### 2.2 Pod 与容器

**Pod**：K8s 最小调度单位，一个 Pod 包含一个或多个容器，共享网络（同一 IP）和存储（Volume）。

**Pod 生命周期**：Pending → Running → Succeeded/Failed。容器状态：Waiting → Running → Terminated。

**重启策略**：Always（默认，总是重启）、OnFailure（失败才重启）、Never（不重启）。

**静态 Pod**：由 kubelet 直接管理（不通过 API Server），用于部署 Master 组件（kubeadm 方式）。

> 🔍 **知识点深度解析**
>
> **作用**：Pod 是 K8s 的最小部署单元，将一个或多个容器组合在一起，共享网络和存储。多容器 Pod 用于"边车模式"（Sidecar）：主容器+辅助容器（日志收集、配置同步、代理）。
>
> **原理**：Pod 内容器共享 Infra 容器（pause）的网络命名空间和 IPC，所以可以用 localhost 互相访问，共享 Volume。Pod 的 IP 是 Pod IP，容器共享。kubelet 根据 PodSpec 创建容器：先创建 pause 容器（持有网络命名空间），再创建业务容器。Pod 状态由 kubelet 上报，API Server 存储到 etcd。健康检查：livenessProbe（存活，失败则重启容器）、readinessProbe（就绪，失败则从 Service Endpoint 移除）、startupProbe（启动，慢启动应用保护）。
>
> **用法要点**：① 一个 Pod 通常一个容器，多容器用于 Sidecar（日志/代理/配置）；② 必须配置 livenessProbe 和 readinessProbe（健康检查是自愈的基础）；③ 资源限制：resources.requests（调度依据）+ limits（上限，超过 OOMKill）；④ 重启策略 Always 适合长期运行服务，OnFailure/Never 适合 Job；⑤ 不要直接管理 Pod（用 Deployment/StatefulSet）；⑥ 优雅终止：terminationGracePeriodSeconds（默认30秒），容器收到 SIGTERM 后清理。

### 2.3 工作负载（Workload）

**Deployment**：无状态应用，管理 ReplicaSet，支持滚动更新、回滚、扩缩容。

**StatefulSet**：有状态应用，稳定的网络标识（Pod名有序）、稳定的存储、有序部署/伸缩。

**DaemonSet**：每个 Node 运行一个 Pod（日志收集、监控 Agent）。

**Job/CronJob**：一次性任务/定时任务。

> 🔍 **知识点深度解析**
>
> **作用**：工作负载是 Pod 的管理者，不同类型适合不同场景。Deployment 管理无状态服务（最常用），StatefulSet 管理有状态服务（数据库、缓存），DaemonSet 管理节点级 Agent，Job 管理批处理任务。
>
> **原理**：Deployment 通过管理 ReplicaSet 实现滚动更新：创建新 ReplicaSet（新版本），逐步增加新 Pod 副本数，同时减少旧 ReplicaSet 副本数，直到新副本达到期望值。回滚就是切换到旧 ReplicaSet。StatefulSet 为每个 Pod 提供稳定标识（pod-name-0, pod-name-1），DNS 解析到固定 Pod，存储用 VolumeClaimTemplate 为每个 Pod 创建独立 PVC。DaemonSet 控制器确保每个（或匹配的）Node 运行一个 Pod，Node 加入时自动调度。Job 创建 Pod 运行直到成功完成（completions 次），CronJob 按 Cron 表达式定时创建 Job。
>
> **用法要点**：① 无状态服务用 Deployment（Web/API/微服务）；② 有状态服务用 StatefulSet（MySQL/Redis/Kafka/Etcd），配合 Headless Service；③ 节点级 Agent 用 DaemonSet（Filebeat/Node Exporter/fluentd）；④ 批处理用 Job，定时任务用 CronJob；⑤ Deployment 滚动更新策略：maxSurge（最多超出多少）+ maxUnavailable（最多不可用多少）；⑥ 回滚：kubectl rollout undo deployment/name；⑦ StatefulSet 扩容是有序的（0→1→2），缩容是逆序（2→1→0）。

### 2.4 Service 与 Ingress

**Service**：为一组 Pod 提供稳定访问入口（Pod IP 会变，Service IP 不变），基于 Label Selector 关联 Pod。

**Service 类型**：
- ClusterIP（默认）：集群内部访问
- NodePort：每个 Node 开放端口，外部可访问
- LoadBalancer：云服务商负载均衡器
- ExternalName：CNAME 别名

**Ingress**：HTTP/HTTPS 路由入口，基于域名/路径路由到不同 Service，支持 TLS 终止、限流。

> 🔍 **知识点深度解析**
>
> **作用**：Service 解决 Pod IP 不稳定的问题（Pod 重建 IP 会变），提供稳定的虚拟 IP（ClusterIP）和负载均衡。Ingress 是七层路由（HTTP/HTTPS），基于域名/路径分发到不同 Service，是集群对外的统一入口（替代多个 NodePort/LoadBalancer）。
>
> **原理**：Service 由 kube-proxy 实现：监听 Service 和 Endpoint 变化，配置 iptables/IPVS 规则。访问 Service IP:Port 时，iptables 规则 DNAT 到后端 Pod IP（随机/轮询选择）。Endpoint 由 Endpoint Controller 根据 Service 的 Selector 动态维护（Pod 增删时更新）。Ingress 由 Ingress Controller（如 Nginx Ingress Controller）实现：监听 Ingress 资源，生成 Nginx 配置，reload Nginx。外部流量→LoadBalancer/NodePort→Ingress Controller→按域名/路径路由→Service→Pod。
>
> **用法要点**：① 集群内部服务间调用用 Service（ClusterIP）；② 对外暴露 HTTP 服务用 Ingress（推荐），不要用 NodePort（端口管理混乱）；③ Ingress Controller 需单独部署（Nginx/Traefik/HAProxy）；④ TLS 证书用 cert-manager 自动签发（Let's Encrypt）；⑤ Service 会话保持：sessionAffinity=ClientIP；⑥ Headless Service（clusterIP: None）用于 StatefulSet（DNS 直接解析到 Pod IP）；⑦ 不要用 Service 做长连接负载均衡（iptables 随机，不感知连接状态）。

### 2.5 存储（Volume/PV/PVC/StorageClass）

**Volume**：Pod 内共享存储，容器重启数据不丢，但 Pod 删除则丢失（emptyDir）。

**PV（PersistentVolume）**：集群级存储资源，由管理员创建或动态供给。

**PVC（PersistentVolumeClaim）**：用户对存储的请求（大小、访问模式），绑定到 PV。

**StorageClass**：动态存储供给定义，指定 provisioner 和参数，PVC 引用后自动创建 PV。

**访问模式**：ReadWriteOnce（单节点读写）、ReadOnlyMany（多节点只读）、ReadWriteMany（多节点读写）。

> 🔍 **知识点深度解析**
>
> **作用**：K8s 存储抽象解决了容器数据持久化问题。PV/PVC 分离了存储提供者和使用者（管理员提供 PV，用户声明 PVC），StorageClass 实现动态供给（无需手动创建 PV）。
>
> **原理**：Volume 是 Pod 内的目录，emptyDir 随 Pod 创建/删除，hostPath 挂载 Node 目录。PV 是集群资源，有独立于 Pod 的生命周期。PVC 绑定 PV 后，Pod 通过 volumeMounts 挂载到容器。动态供给：PVC 指定 storageClassName，StorageClass 的 provisioner（如 csi-provisioner）调用存储 API 创建卷，自动创建 PV 并绑定。CSI（容器存储接口）是标准，各存储厂商实现 CSI Driver（Ceph/NFS/AWS EBS/阿里云盘）。
>
> **用法要点**：① 生产用 PVC + StorageClass 动态供给（不要手动创建 PV）；② 数据库用 ReadWriteOnce（RWO），共享文件用 ReadWriteMany（RWX，NFS/CephFS）；③ PV 回收策略：Retain（保留，默认生产用）、Delete（删除，测试用）；④ StatefulSet 用 volumeClaimTemplates 为每个 Pod 创建独立 PVC；⑤ 备份：Velero 或存储快照；⑥ 不要用 hostPath（绑定到特定 Node，Pod 调度受限）；⑦ 存储性能：SSD 类用于数据库，HDD 类用于日志/归档。

### 2.6 配置管理（ConfigMap/Secret）

**ConfigMap**：存储非敏感配置（key-value），挂载为文件或环境变量。

**Secret**：存储敏感信息（密码、Token、证书），Base64 编码，挂载为临时文件（tmpfs，不落盘）。

**使用方式**：
- 环境变量：valueFrom.configMapKeyRef / secretKeyRef
- 卷挂载：volumes + volumeMounts（ConfigMap 变更自动更新）

> 🔍 **知识点深度解析**
>
> **作用**：ConfigMap/Secret 将配置从镜像中分离，实现"一次构建，多环境部署"。ConfigMap 存普通配置，Secret 存敏感信息。配置变更无需重新构建镜像。
>
> **原理**：ConfigMap/Secret 是 K8s API 资源，存储在 etcd。作为环境变量注入时，kubelet 在容器启动时读取并设置，容器运行中不会更新（需重启 Pod）。作为 Volume 挂载时，kubelet 定期检查更新，通过符号链接原子替换（ConfigMap 更新后约60秒内容器内文件更新）。Secret 数据 Base64 编码（不是加密），挂载时用 tmpfs（内存文件系统，不写入 Node 磁盘）。etcd 加密（EncryptionConfiguration）可保护静态 Secret。
>
> **用法要点**：① 非敏感配置用 ConfigMap，敏感信息用 Secret（密码/Token/证书）；② Secret 不是加密（Base64），生产需开启 etcd 加密或用外部密钥管理（Vault/Sealed Secrets）；③ 配置热更新：Volume 挂载自动更新，环境变量需重启 Pod；④ 应用需支持配置热加载（如 watch 文件变化），否则挂载更新了但应用不生效；⑤ 大配置不要用 ConfigMap（限制 1MB），用文件挂载或外部配置中心（Nacos/Apollo）；⑥ Secret 作为环境变量可能泄露（进程环境、日志打印），推荐 Volume 挂载；⑦ 不要把 Secret 提交到 Git（用 Sealed Secrets 或 External Secrets）。

### 2.7 调度与亲和性

**调度过程**：Scheduler 过滤（Predicate）不满足条件的 Node → 打分（Priority）选择最高分 Node。

**影响调度的因素**：
- 资源请求（requests）：Node 剩余资源≥requests
- 节点选择器（nodeSelector）：指定 Label 的 Node
- 亲和性（Affinity）：节点亲和性、Pod 亲和/反亲和
- 污点与容忍（Taint/Toleration）：Node 排斥 Pod，Pod 可容忍
- 拓扑分布约束（TopologySpreadConstraints）：跨故障域均匀分布

> 🔍 **知识点深度解析**
>
> **作用**：调度决定 Pod 运行在哪个 Node，影响性能（本地存储）、高可用（跨节点分布）、资源利用。亲和性/反亲和性实现高级调度策略（如同一服务 Pod 分散到不同节点，关联服务 Pod 靠近部署）。
>
> **原理**：Scheduler 调度分两步：① 过滤（Predicate）：排除不满足条件的 Node（资源不足、端口冲突、污点不容忍、亲和性不满足）；② 打分（Priority）：对剩余 Node 打分（资源均衡、亲和性匹配、镜像已存在等），选最高分。节点亲和性（nodeAffinity）：硬约束（requiredDuringSchedulingIgnoredDuringExecution）必须满足，软约束（preferred）尽量满足。Pod 反亲和性（podAntiAffinity）：同一服务 Pod 调度到不同 Node（高可用）。污点（Taint）：Node 标记，默认排斥 Pod，Pod 加 Toleration 才能调度（如 Master 节点的 NoSchedule 污点）。
>
> **用法要点**：① 高可用：Pod 反亲和性（topologyKey: kubernetes.io/hostname），同一服务 Pod 分散到不同 Node；② 关联服务靠近：Pod 亲和性（减少网络延迟）；③ 专用节点：节点污点+Pod 容忍（如 GPU 节点、大数据节点）；④ 资源 requests 必须设置（调度依据，不设则可能调度到资源不足的 Node）；⑤ 拓扑分布约束（TopologySpreadConstraints）比反亲和性更灵活（跨可用区/机架均匀分布）；⑥ 不要用 nodeSelector（功能有限），用节点亲和性；⑦ 调度失败排查：kubectl describe pod 看 Events（FailedScheduling 原因）。

---


---
## 3. 常用用法

### 3.1 Deployment 部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  labels:
    app: order-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
      - name: order-service
        image: registry.example.com/order-service:v1.0.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 1000m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
```

> 🔍 **知识点深度解析**
>
> **作用**：Deployment 是无状态服务的标准部署方式，管理副本数、滚动更新、健康检查、资源限制。是 K8s 最常用的资源。
>
> **原理**：Deployment 控制器监听 Deployment 资源，创建/更新 ReplicaSet。滚动更新时，创建新 ReplicaSet（新镜像），按 maxSurge/maxUnavailable 逐步替换旧 Pod。maxSurge=1 表示最多多1个 Pod，maxUnavailable=0 表示滚动期间所有 Pod 都可用（零停机）。健康检查：livenessProbe 失败 kubelet 重启容器，readinessProbe 失败从 Service Endpoint 移除（不接收流量）。资源 requests 用于调度，limits 用于限制（超过 CPU 被节流，超过内存被 OOMKill）。
>
> **用法要点**：① 必须设置 resources.requests 和 limits（防止资源争抢和 OOM）；② 必须设置 livenessProbe 和 readinessProbe（自愈和零停机更新的基础）；③ 滚动更新 maxUnavailable=0 + maxSurge=1 实现零停机；④ 镜像标签不要用 latest（无法回滚，每次都拉取），用版本号（v1.0.0）或 Git commit；⑤ 部署命令：kubectl apply -f deployment.yaml；⑥ 查看状态：kubectl rollout status deployment/order-service；⑦ 回滚：kubectl rollout undo deployment/order-service --to-revision=1。

### 3.2 Service 配置

```yaml
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  selector:
    app: order-service
  ports:
  - port: 80          # Service 端口
    targetPort: 8080  # Pod 端口
    protocol: TCP
  type: ClusterIP
---

> 🔍 **知识点深度解析**
>
> **作用**：Service 为一组 Pod 提供稳定的访问入口和负载均衡，解决 Pod IP 动态变化的问题。
>
> **原理**：Service 通过 label selector 选中后端 Pod，Endpoints Controller 监控 Pod 变化更新 Endpoints 对象。kube-proxy 在每个节点上配置 iptables/ipvs 规则，将发往 ClusterIP 的流量负载均衡到后端 Pod。Service 类型：ClusterIP（集群内部）、NodePort（节点端口暴露）、LoadBalancer（云负载均衡器）、ExternalName（DNS CNAME）。
>
> **用法要点**：① ClusterIP 默认类型，集群内部访问；NodePort 通过 <NodeIP>:<NodePort> 暴露  ② kube-proxy iptables 模式（随机）、ipvs 模式（多种算法，性能好）  ③ Service 和 Pod 通过 label selector 关联，Endpoints 自动维护  ④ Headless Service（clusterIP: None）直接返回 Pod IP 用于 StatefulSet  ⑤ 面试常考：Service 类型、kube-proxy 原理、Endpoints、ClusterIP 不可 Ping

# 对外暴露（NodePort，不推荐生产用）
apiVersion: v1
kind: Service
metadata:
  name: order-service-nodeport
spec:
  selector:
    app: order-service
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080  # 30000-32767
  type: NodePort
```

> 🔍 **知识点深度解析**
>
> **作用**：Service 为 Pod 提供稳定访问入口和负载均衡。ClusterIP 用于集群内部服务间调用，NodePort/LoadBalancer 用于外部访问。
>
> **原理**：Service 通过 Label Selector 关联 Pod，Endpoint Controller 自动维护 Endpoint 列表（Pod IP+Port）。kube-proxy 监听 Service/Endpoint，配置 iptables/IPVS 规则：访问 Service ClusterIP:Port 时，DNAT 到后端 Pod（随机选择，iptables 模式；轮询/最少连接，IPVS 模式）。ClusterIP 是虚拟 IP（iptables 规则，不是真实网卡 IP），只在集群内可达。NodePort 在每个 Node 上开放端口，外部访问 NodeIP:NodePort → kube-proxy → Service → Pod。
>
> **用法要点**：① 服务间调用用 Service 名（K8s DNS：service-name.namespace.svc.cluster.local）；② targetPort 可以是端口号或名称（推荐名称，解耦）；③ 生产环境对外用 Ingress，不要用 NodePort（端口有限、不安全）；④ 会话保持：sessionAffinity: ClientIP（同一客户端 IP 路由到同一 Pod）；⑤ Headless Service（clusterIP: None）用于 StatefulSet（DNS A 记录直接返回 Pod IP）；⑥ 多端口 Service：ports 数组配置多个；⑦ Service 不感知 Pod 健康状态（靠 readinessProbe 从 Endpoint 移除不健康 Pod）。

### 3.3 Ingress 配置

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/limit-rps: "100"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /orders
        pathType: Prefix
        backend:
          service:
            name: order-service
            port:
              number: 80
      - path: /users
        pathType: Prefix
        backend:
          service:
            name: user-service
            port:
              number: 80
```

> 🔍 **知识点深度解析**
>
> **作用**：Ingress 是集群七层（HTTP/HTTPS）路由入口，基于域名/路径分发到不同 Service。支持 TLS 终止、限流、重写、鉴权，替代多个 LoadBalancer。
>
> **原理**：Ingress 资源本身只是配置，实际由 Ingress Controller（如 Nginx Ingress Controller）实现。Controller 监听 Ingress/Service/Endpoint 变化，生成 Nginx 配置（server/location/upstream），reload Nginx。外部流量→云负载均衡（或 NodePort）→Ingress Controller Pod（Nginx）→按域名/路径路由→后端 Service→Pod。TLS 终止在 Ingress Controller 完成（证书存在 Secret 中），后端是 HTTP。
>
> **用法要点**：① 必须先部署 Ingress Controller（Nginx/Traefik），Ingress 才生效；② ingressClassName 指定 Controller（K8s 1.18+）；③ TLS 证书用 cert-manager 自动管理（Let's Encrypt 免费证书）；④ 常用注解：rewrite-target（路径重写）、ssl-redirect（强制 HTTPS）、limit-rps（限流）、proxy-body-size（上传大小）；⑤ 生产用域名路由（不同服务不同域名或路径）；⑥ 灰度发布：canary 注解（nginx.ingress.kubernetes.io/canary: "true"）按比例分流；⑦ Ingress 只支持 HTTP/HTTPS，TCP/UDP 用 Service NodePort/LoadBalancer。

### 3.4 ConfigMap 与 Secret

```yaml

> 🔍 **知识点深度解析**
>
> **作用**：ConfigMap 存储非敏感配置，Secret 存储敏感信息（密码、密钥、证书），实现配置与镜像解耦。
>
> **原理**：ConfigMap 以键值对或文件形式存储配置，可通过环境变量、命令行参数或 Volume 挂载到 Pod。Secret 类似但数据用 base64 编码（注意不是加密），可配置 etcd 加密静态存储和 RBAC 限制访问。两者更新后，挂载的 Volume 文件会自动更新（环境变量方式不会热更新）。
>
> **用法要点**：① ConfigMap 挂载为 Volume 时文件更新自动生效，环境变量方式不更新  ② Secret base64 编码非加密，生产环境需启用 etcd 加密 + RBAC  ③ Secret 类型：Opaque（通用）、dockerconfigjson（镜像仓库）、tls（证书）  ④ 配置与镜像分离，同一镜像不同环境用不同 ConfigMap  ⑤ 面试常考：ConfigMap vs Secret、热更新、Secret 安全性、配置注入方式

# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  application.yml: |
    server:
      port: 8080
    spring:
      datasource:
        url: jdbc:mysql://mysql:3306/app
  LOG_LEVEL: INFO
---
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  DB_PASSWORD: cGFzc3dvcmQ=  # base64 编码
  API_KEY: YWJjZGVmZ2g=
---
# Pod 中使用
spec:
  containers:
  - name: app
    image: app:v1
    env:
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: LOG_LEVEL
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: DB_PASSWORD
    volumeMounts:
    - name: config-volume
      mountPath: /config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

> 🔍 **知识点深度解析**
>
> **作用**：ConfigMap/Secret 实现配置与代码分离，环境变量注入简单配置，Volume 挂载配置文件（支持热更新）。Secret 管理敏感信息。
>
> **原理**：环境变量注入：kubelet 在容器启动时从 ConfigMap/Secret 读取值，设置为容器环境变量。Volume 挂载：ConfigMap 每个 key 成为一个文件，挂载到指定目录；Secret 挂载用 tmpfs（内存文件系统，Node 重启丢失，Pod 重建时重新挂载）。ConfigMap 更新后，Volume 挂载的文件会自动更新（kubelet 同步，约60秒延迟），但环境变量不会更新（需重启 Pod）。
>
> **用法要点**：① 配置文件用 Volume 挂载（支持热更新），简单 key-value 用环境变量；② Secret 用 Volume 挂载（比环境变量安全，环境变量可能被日志/进程泄露）；③ ConfigMap 变更后，Volume 挂载自动更新，但应用需支持热加载（如 Spring Cloud @RefreshScope 或 watch 文件）；④ 敏感配置不要写在 ConfigMap，用 Secret；⑤ Secret 不是加密（Base64），生产用 Sealed Secrets/Vault 或开启 etcd 加密；⑥ 大配置文件（>1MB）不要用 ConfigMap，用外部存储或 initContainer 下载；⑦ 多环境配置：不同 Namespace 用不同 ConfigMap，或用 Kustomize/Helm 管理。

### 3.5 持久化存储

```yaml

> 🔍 **知识点深度解析**
>
> **作用**：PV/PVC/StorageClass 提供持久化存储抽象，使 Pod 重建后数据不丢失。
>
> **原理**：PV（PersistentVolume）是集群级存储资源（NFS、Ceph、云盘），PVC（PersistentVolumeClaim）是用户对存储的请求（大小、访问模式），StorageClass 动态创建 PV 无需管理员预先分配。PVC 绑定 PV 后挂载到 Pod。访问模式：RWO（单节点读写）、ROX（多节点只读）、RWX（多节点读写）。StatefulSet 使用 volumeClaimTemplates 为每个 Pod 创建独立 PVC。
>
> **用法要点**：① PV 是集群资源，PVC 是命名空间资源，通过 accessModes/storageClassName 绑定  ② StorageClass + provisioner 实现动态供给（自动创建 PV）  ③ RWO 单节点读写、RWX 多节点读写（NFS/CephFS）  ④ StatefulSet volumeClaimTemplates 每个 Pod 独立 PVC，有序绑定  ⑤ 面试常考：PV/PVC 绑定流程、StorageClass 动态供给、StatefulSet 存储、访问模式

# StorageClass（动态供给）
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  fsType: ext4
reclaimPolicy: Retain
allowVolumeExpansion: true
---
# PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-data
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: fast-ssd
---
# Pod 中使用
spec:
  containers:
  - name: mysql
    image: mysql:8.0
    volumeMounts:
    - name: mysql-data
      mountPath: /var/lib/mysql
  volumes:
  - name: mysql-data
    persistentVolumeClaim:
      claimName: mysql-data
```

> 🔍 **知识点深度解析**
>
> **作用**：PVC + StorageClass 实现动态存储供给，用户只需声明需要多少存储，K8s 自动创建 PV 并挂载。是有状态应用（数据库）的基础。
>
> **原理**：PVC 创建后，PersistentVolumeController 寻找匹配的 PV（或通过 StorageClass 动态创建）。动态供给：provisioner 调用云存储 API 创建卷（如 AWS EBS），创建 PV 对象，绑定到 PVC。Pod 挂载 PVC 时，kubelet 调用 CSI Driver 将卷挂载到 Node（Attach/Detach + Mount/Unmount）。allowVolumeExpansion=true 支持扩容（修改 PVC storage 字段，自动扩容 PV 和文件系统）。
>
> **用法要点**：① 生产用 StorageClass 动态供给，不要手动创建 PV；② reclaimPolicy: Retain（删除 PVC 后保留数据，生产推荐）；③ 数据库用 ReadWriteOnce（RWO）+ SSD StorageClass；④ 共享存储（多 Pod 读写）用 ReadWriteMany（RWX），需要 NFS/CephFS/GlusterFS；⑤ StatefulSet 用 volumeClaimTemplates（每个 Pod 独立 PVC）；⑥ 扩容：修改 PVC spec.resources.requests.storage（需 allowVolumeExpansion）；⑦ 备份：Velero 或存储快照（CSI VolumeSnapshot）；⑧ 不要用 emptyDir 存重要数据（Pod 删除即丢失）。

### 3.6 资源限制与 HPA

```yaml

> 🔍 **知识点深度解析**
>
> **作用**：通过 resources.requests/limits 分配计算资源，HPA 根据 CPU/内存/自定义指标自动伸缩副本数。
>
> **原理**：requests 是调度依据（K8s 保证节点有足够资源），limits 是上限（cgroups 限制，CPU 超 limit 被限流，内存超 limit 被 OOM Kill）。HPA 周期性（默认 15s）从 Metrics Server 获取指标，计算期望副本数 = ceil(当前副本数 × 当前指标/目标指标)，调整 Deployment replicas。支持 CPU/内存和自定义指标（Prometheus Adapter）。
>
> **用法要点**：① requests 用于调度，limits 用于运行时限制（cgroups）  ② CPU 可压缩（超 limit 限流），内存不可压缩（超 limit OOM Kill）  ③ HPA 公式：desiredReplicas = ceil(currentReplicas * currentMetric / desiredMetric)  ④ 需要 Metrics Server 或 Prometheus Adapter 提供指标  ⑤ 面试常考：requests vs limits、HPA 算法、OOM Kill、VPA 与 HPA 区别

# HPA（自动扩缩容）
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
    scaleDown:
      stabilizationWindowSeconds: 300
```

> 🔍 **知识点深度解析**
>
> **作用**：HPA（Horizontal Pod Autoscaler）根据 CPU/内存/自定义指标自动扩缩容 Pod 副本数，应对流量波动，节省资源。是云原生弹性伸缩的核心。
>
> **原理**：HPA 控制器定期（默认15秒）从 Metrics Server 获取 Pod 资源使用率，计算期望副本数：desiredReplicas = ceil[currentReplicas * (currentMetric / desiredMetric)]。如当前3个 Pod，CPU 使用率90%，目标70%，则 desired=ceil(3*90/70)=4。扩容立即执行，缩容有稳定窗口（stabilizationWindowSeconds，防止抖动）。自定义指标（如 QPS、队列长度）需要 Prometheus Adapter 或自定义 Metrics API。
>
> **用法要点**：① 必须设置 resources.requests（HPA 计算使用率的基准）；② 必须部署 Metrics Server（HPA 依赖它获取指标）；③ CPU 扩容快（几秒），内存扩容慢（需启动 JVM 等），内存指标不适合做快速扩缩；④ 自定义指标（QPS/队列长度）比 CPU 更准确（CPU 高不一定是业务压力）；⑤ 缩容窗口设长一些（300秒），防止频繁缩容；⑥ 最大副本数要合理（防止无限扩容打垮下游）；⑦ VPA（垂直扩缩容）调整 Pod 资源请求，与 HPA 不要同时用（冲突）。

### 3.7 健康检查与优雅停机

```yaml
spec:
  containers:
  - name: app
    image: app:v1
    ports:
    - containerPort: 8080
    livenessProbe:
      httpGet:
        path: /actuator/health/liveness
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 3
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /actuator/health/readiness
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 3
    startupProbe:
      httpGet:
        path: /actuator/health
        port: 8080
      failureThreshold: 30
      periodSeconds: 10
    lifecycle:
      preStop:
        exec:
          command: ["sh", "-c", "sleep 15"]
  terminationGracePeriodSeconds: 60
```

> 🔍 **知识点深度解析**
>
> **作用**：健康检查保证只有健康的 Pod 接收流量（readiness），不健康的 Pod 自动重启（liveness）。优雅停机保证 Pod 删除时正在处理的请求不中断。是零停机发布和高可用的基础。
>
> **原理**：livenessProbe：kubelet 定期检查，连续失败（failureThreshold）则重启容器。readinessProbe：失败则从 Service Endpoint 移除（不接收新流量），成功则加回。startupProbe：慢启动应用保护，启动成功后才启用 liveness/readiness（防止启动慢被误杀）。优雅停机：Pod 删除时，① 从 Endpoint 移除（停止接收新流量）；② 发送 SIGTERM 给容器；③ 等待 preStop hook 执行或 terminationGracePeriodSeconds 超时；④ 发送 SIGKILL 强制终止。preStop sleep 是为了等待负载均衡器/Ingress 感知到 Pod 已移除（避免还有请求进来）。
>
> **用法要点**：① 必须配置 livenessProbe 和 readinessProbe；② 慢启动应用（JVM 启动30秒+）用 startupProbe 保护；③ readinessProbe 失败从 Endpoint 移除，但容器不重启（与 liveness 区别）；④ 优雅停机：preStop sleep 10-30秒（等待 Ingress/Service 更新）+ 应用处理完在途请求；⑤ terminationGracePeriodSeconds 要大于 preStop 时间+应用处理时间；⑥ Spring Boot 优雅停机：server.shutdown=graceful + spring.lifecycle.timeout-per-shutdown-phase=30s；⑦ 健康检查端点要轻量（不要查数据库，否则数据库慢会导致 Pod 被误杀）。

### 3.8 常用 kubectl 命令

```bash

> 🔍 **知识点深度解析**
>
> **作用**：kubectl 是 K8s 命令行工具，覆盖资源查看、编辑、扩缩容、日志和调试操作。
>
> **原理**：常用命令：kubectl get pods/services/deployments 查看资源（-o wide 显示 IP/节点，-w 监听变化）；kubectl describe 查看事件详情（排查调度失败）；kubectl logs 查看容器日志（-f 跟踪，--previous 看上一个崩溃容器）；kubectl exec 进入容器；kubectl scale 扩缩容；kubectl rollout status/undo 管理发布；kubectl apply -f 声明式更新。
>
> **用法要点**：① kubectl get pods -A 查看所有命名空间 Pod  ② kubectl describe pod <name> 查看事件排障  ③ kubectl logs -f <pod> 实时日志，--previous 崩溃前日志  ④ kubectl exec -it <pod> -- bash 进入容器  ⑤ 面试常考：kubectl 常用命令、Pod 排障流程、日志查看

# 资源查看
kubectl get pods -n namespace                    # 列出 Pod
kubectl get pods -o wide                         # 显示 Node/IP
kubectl get deployments,svc,ingress              # 多种资源
kubectl describe pod <pod-name>                  # 详细信息（Events 排查）
kubectl logs <pod-name> -f                       # 查看日志（-f 跟随）
kubectl logs <pod-name> --previous               # 查看上一个容器日志（崩溃后）

# 部署与管理
kubectl apply -f deployment.yaml                 # 应用配置
kubectl delete -f deployment.yaml                # 删除
kubectl scale deployment <name> --replicas=5     # 扩缩容
kubectl rollout status deployment/<name>         # 滚动更新状态
kubectl rollout undo deployment/<name>           # 回滚
kubectl rollout history deployment/<name>        # 历史版本

# 调试
kubectl exec -it <pod-name> -- /bin/sh           # 进入容器
kubectl port-forward svc/<name> 8080:80          # 端口转发（本地调试）
kubectl top pods                                 # 资源使用（需 Metrics Server）
kubectl get events --sort-by='.lastTimestamp'    # 事件（排查问题）
kubectl explain deployment.spec                  # 资源文档
```

> 🔍 **知识点深度解析**
>
> **作用**：kubectl 是 K8s 命令行工具，用于管理集群资源。掌握常用命令是 K8s 开发和运维的基础。describe 和 logs 是排查问题最常用的命令。
>
> **原理**：kubectl 通过 REST API 与 API Server 通信，kubectl get 是 LIST 操作，describe 是 GET+聚合相关资源（Events/Endpoint），logs 是通过 kubelet API 获取容器日志（API Server 代理到 kubelet）。apply 是声明式配置（对比当前状态和配置，执行更新），create 是命令式（直接创建）。rollout 系列命令操作 Deployment 的滚动更新状态（存在 annotations 中）。
>
> **用法要点**：① 排查问题第一步：kubectl describe pod 看 Events（Pending/ImagePullBackOff/CrashLoopBackOff 原因）；② 容器崩溃：kubectl logs --previous 看上一次日志；③ 进入容器调试：kubectl exec -it（生产容器可能没有 shell，用临时容器 kubectl debug）；④ 本地调试服务：kubectl port-forward（本地端口转发到集群 Service）；⑤ 资源使用：kubectl top pods/nodes（需 Metrics Server）；⑥ 批量操作：kubectl get pods -l app=xxx -o name | xargs kubectl delete；⑦ 配置文件用 apply（声明式，可重复执行），不要用 create（命令式，重复执行报错）。

---


---
## 4. 注意事项

1. **资源限制必须设置**：requests（调度依据）和 limits（上限）。不设 requests 可能调度到资源不足节点，不设 limits 可能占满节点资源导致其他 Pod OOM。

2. **健康检查必须配置**：livenessProbe（自愈）+ readinessProbe（零停机）。慢启动应用加 startupProbe。没有健康检查，Pod 死了不重启、不健康还接收流量。

3. **镜像不要用 latest**：latest 标签无法回滚、每次部署都拉取（不确定版本）。用版本号（v1.0.0）或 Git commit SHA。

4. **优雅停机**：preStop hook + terminationGracePeriodSeconds + 应用优雅处理 SIGTERM。否则滚动更新时在途请求会中断。

5. **Secret 不是加密**：Base64 编码不是加密。生产环境开启 etcd 静态加密，或用 Sealed Secrets/Vault 管理敏感信息。

6. **不要直接管理 Pod**：用 Deployment/StatefulSet/DaemonSet。直接创建的 Pod 不会被自愈（节点故障不重新调度）。

7. **有状态服务用 StatefulSet**：数据库、缓存、消息队列用 StatefulSet（稳定标识+稳定存储），不要用 Deployment（Pod 重建标识会变）。

8. **HPA 依赖 Metrics Server**：HPA 需要 Metrics Server 获取指标，必须部署。自定义指标需要 Prometheus Adapter。

9. **Ingress Controller 单独部署**：Ingress 资源只是配置，需要 Ingress Controller（Nginx/Traefik）才生效。生产用 Ingress 对外暴露，不要用 NodePort。

10. **etcd 备份**：etcd 存了集群所有状态，丢失=集群重建。定期备份（etcdctl snapshot save），测试恢复流程。

11. **节点资源预留**：配置 system-reserved 和 kube-reserved，防止容器占满 CPU/内存导致节点不稳定（系统进程 OOM）。

12. **日志与监控**：集群级日志收集（EFK/Loki）、监控（Prometheus+Grafana）、告警（Alertmanager）。没有监控等于盲飞。

---

> 💡 **深度讲解**：Kubernetes 是云原生时代的操作系统，核心是声明式 API 和控制循环。Master 组件（API Server/etcd/Scheduler/Controller Manager）管理集群，Node 组件（kubelet/kube-proxy/容器运行时）运行容器。Pod 是最小调度单位，多容器共享网络和存储（Sidecar 模式）。工作负载分 Deployment（无状态）、StatefulSet（有状态）、DaemonSet（节点级）、Job（批处理）。Service 提供稳定访问入口和负载均衡（kube-proxy 实现），Ingress 是七层路由入口。存储用 PV/PVC/StorageClass 动态供给，配置用 ConfigMap/Secret。调度通过过滤+打分选择 Node，亲和性/反亲和性/污点实现高级策略。HPA 根据指标自动扩缩容。健康检查（liveness/readiness/startup）和优雅停机是高可用的基础。理解了这些概念，就能正确部署和管理容器化应用，也能在遇到 Pod 调度失败、CrashLoopBackOff、服务不通等问题时快速定位。
>
> **📝 精简总结**：K8s 架构=Master(API Server/etcd/Scheduler/Controller)+Node(kubelet/kube-proxy/运行时)；Pod=最小调度单位(共享网络存储)；工作负载=Deployment(无状态)/StatefulSet(有状态)/DaemonSet(节点级)/Job；Service=稳定入口+负载均衡，Ingress=七层路由；存储=PV/PVC/StorageClass动态供给；配置=ConfigMap(普通)/Secret(敏感)；调度=过滤+打分+亲和性/污点；HPA=自动扩缩容；必须=资源限制+健康检查+优雅停机+镜像版本号。

---

> 📋 **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 知识点深度解析」模块（作用+原理+用法要点），原有内联图已统一风格化美化（圆角、阴影、渐变、动画）。所有原有内容完整保留，未做任何修改。
