# -*- coding: utf-8 -*-
"""第三批扩展：云原生 + 计算机基础"""
import os, sys
ENGINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "01-前端开发")
sys.path.insert(0, ENGINE_DIR)
from engine import expand

BASE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# Kubernetes
# ============================================================
k8s = {
    "### 3.1 Deployment 部署": (
        "Deployment 管理无状态应用的副本集，支持声明式更新、回滚和弹性伸缩，是 K8s 最常用的工作负载。",
        "Deployment 创建 ReplicaSet，ReplicaSet 维护指定数量的 Pod。更新时 Deployment 创建新 ReplicaSet 并按 maxSurge/maxUnavailable 策略滚动升级（逐步创建新 Pod、终止旧 Pod）。回滚通过 revision 历史恢复到旧 ReplicaSet。Deployment 通过 label selector 关联 Pod，修改 spec.template 触发滚动更新。",
        ["kubectl create deployment / apply -f deployment.yaml", "滚动更新策略：maxSurge（超出副本数上限）、maxUnavailable（不可用上限）", "kubectl rollout status/undo/history 管理发布和回滚", "replicas 指定副本数，HPA 可自动伸缩", "面试常考：Deployment vs StatefulSet、滚动更新原理、回滚机制、ReplicaSet 作用"]
    ),
    "### 3.2 Service 配置": (
        "Service 为一组 Pod 提供稳定的访问入口和负载均衡，解决 Pod IP 动态变化的问题。",
        "Service 通过 label selector 选中后端 Pod，Endpoints Controller 监控 Pod 变化更新 Endpoints 对象。kube-proxy 在每个节点上配置 iptables/ipvs 规则，将发往 ClusterIP 的流量负载均衡到后端 Pod。Service 类型：ClusterIP（集群内部）、NodePort（节点端口暴露）、LoadBalancer（云负载均衡器）、ExternalName（DNS CNAME）。",
        ["ClusterIP 默认类型，集群内部访问；NodePort 通过 <NodeIP>:<NodePort> 暴露", "kube-proxy iptables 模式（随机）、ipvs 模式（多种算法，性能好）", "Service 和 Pod 通过 label selector 关联，Endpoints 自动维护", "Headless Service（clusterIP: None）直接返回 Pod IP 用于 StatefulSet", "面试常考：Service 类型、kube-proxy 原理、Endpoints、ClusterIP 不可 Ping"]
    ),
    "### 3.3 Ingress 配置": (
        "Ingress 管理集群外部到内部 Service 的 HTTP/HTTPS 路由，提供域名、路径、TLS 等七层转发能力。",
        "Ingress 只是路由规则定义，需要 Ingress Controller（如 Nginx Ingress Controller、Traefik）实际执行：Controller 监听 Ingress 资源变化，动态生成 Nginx 配置并 reload。Ingress 支持基于 Host 的虚拟主机、基于 Path 的路由、TLS 终止、注解配置（rewrite、限流、认证）。",
        ["Ingress Controller 必须单独部署（Nginx/Traefik/HAProxy）", "基于 Host 和 Path 路由到不同 Service", "TLS 终止：spec.tls 配置证书 Secret", "注解 annotations 实现 rewrite、限流、CORS、认证等高级功能", "面试常考：Ingress vs Service、Ingress Controller 原理、Nginx 配置热更新"]
    ),
    "### 3.4 ConfigMap 与 Secret": (
        "ConfigMap 存储非敏感配置，Secret 存储敏感信息（密码、密钥、证书），实现配置与镜像解耦。",
        "ConfigMap 以键值对或文件形式存储配置，可通过环境变量、命令行参数或 Volume 挂载到 Pod。Secret 类似但数据用 base64 编码（注意不是加密），可配置 etcd 加密静态存储和 RBAC 限制访问。两者更新后，挂载的 Volume 文件会自动更新（环境变量方式不会热更新）。",
        ["ConfigMap 挂载为 Volume 时文件更新自动生效，环境变量方式不更新", "Secret base64 编码非加密，生产环境需启用 etcd 加密 + RBAC", "Secret 类型：Opaque（通用）、dockerconfigjson（镜像仓库）、tls（证书）", "配置与镜像分离，同一镜像不同环境用不同 ConfigMap", "面试常考：ConfigMap vs Secret、热更新、Secret 安全性、配置注入方式"]
    ),
    "### 3.5 持久化存储": (
        "PV/PVC/StorageClass 提供持久化存储抽象，使 Pod 重建后数据不丢失。",
        "PV（PersistentVolume）是集群级存储资源（NFS、Ceph、云盘），PVC（PersistentVolumeClaim）是用户对存储的请求（大小、访问模式），StorageClass 动态创建 PV 无需管理员预先分配。PVC 绑定 PV 后挂载到 Pod。访问模式：RWO（单节点读写）、ROX（多节点只读）、RWX（多节点读写）。StatefulSet 使用 volumeClaimTemplates 为每个 Pod 创建独立 PVC。",
        ["PV 是集群资源，PVC 是命名空间资源，通过 accessModes/storageClassName 绑定", "StorageClass + provisioner 实现动态供给（自动创建 PV）", "RWO 单节点读写、RWX 多节点读写（NFS/CephFS）", "StatefulSet volumeClaimTemplates 每个 Pod 独立 PVC，有序绑定", "面试常考：PV/PVC 绑定流程、StorageClass 动态供给、StatefulSet 存储、访问模式"]
    ),
    "### 3.6 资源限制与 HPA": (
        "通过 resources.requests/limits 分配计算资源，HPA 根据 CPU/内存/自定义指标自动伸缩副本数。",
        "requests 是调度依据（K8s 保证节点有足够资源），limits 是上限（cgroups 限制，CPU 超 limit 被限流，内存超 limit 被 OOM Kill）。HPA 周期性（默认 15s）从 Metrics Server 获取指标，计算期望副本数 = ceil(当前副本数 × 当前指标/目标指标)，调整 Deployment replicas。支持 CPU/内存和自定义指标（Prometheus Adapter）。",
        ["requests 用于调度，limits 用于运行时限制（cgroups）", "CPU 可压缩（超 limit 限流），内存不可压缩（超 limit OOM Kill）", "HPA 公式：desiredReplicas = ceil(currentReplicas * currentMetric / desiredMetric)", "需要 Metrics Server 或 Prometheus Adapter 提供指标", "面试常考：requests vs limits、HPA 算法、OOM Kill、VPA 与 HPA 区别"]
    ),
    "### 3.7 健康检查与优雅停机": (
        "livenessProbe/readinessProbe/startupProbe 检测容器健康状态，实现自动恢复和零停机部署。",
        "livenessProbe 检测容器是否存活，失败则重启容器（解决死锁）。readinessProbe 检测是否就绪，失败则从 Service Endpoints 摘除（不重启）。startupProbe 给慢启动应用宽限时间，成功前其他探针不执行。探针方式：HTTP GET、TCP Socket、exec 命令。优雅停机：Pod 终止时先从 Endpoints 摘流，发送 SIGTERM，等待 terminationGracePeriodSeconds（默认 30s）后 SIGKILL。",
        ["liveness 失败重启容器，readiness 失败摘流不重启", "startupProbe 保护慢启动应用，成功前禁用其他探针", "探针参数：initialDelaySeconds、periodSeconds、failureThreshold、timeoutSeconds", "优雅停机：preStop Hook + SIGTERM + terminationGracePeriodSeconds", "面试常考：三种探针区别、优雅停机流程、SIGTERM、零停机部署"]
    ),
}

# ============================================================
# Service Mesh
# ============================================================
service_mesh = {
    "### 3.2 灰度发布（Canary）": (
        "通过 Istio 流量权重控制实现灰度发布，将小比例流量导到新版本验证后再全量发布。",
        "Istio VirtualService 配置 http.route 的 weight 字段，按百分比将流量分配到不同 Deployment（subset）。灰度过程：部署 v2（初始 0%）→ 5% 流量到 v2 → 监控指标 → 逐步调大权重（20%/50%）→ 100% 切 v2 → 删除 v1。可配合按 Header/Cookie 的精确路由实现内部测试。VirtualService + DestinationRule subset 共同实现。",
        ["VirtualService weight 配置流量百分比：v1:90, v2:10", "DestinationRule subsets 定义版本标签（version: v1/v2）", "可按 Header/Cookie 路由：特定用户先体验新版本", "结合 Prometheus/Grafana 监控灰度版本错误率和延迟", "面试常考：灰度发布原理、VirtualService/DestinationRule、流量切分策略"]
    ),
    "### 3.3 熔断与重试": (
        "Istio DestinationRule 配置异常检测（熔断）和 VirtualService 配置重试，提升服务韧性。",
        "熔断（OutlierDetection）：连续错误超过阈值（consecutiveErrors）或错误率超过百分比后，将异常实例从连接池驱逐一段时间（baseEjectionTime），避免级联故障。重试：VirtualService retries 配置 attempts（重试次数）、perTryTimeout（每次超时）、retryOn（重试条件）。超时：timeout 字段设置请求超时。这些都在 Sidecar 中执行，对应用代码无侵入。",
        ["熔断：连续 5xx 错误超过阈值后驱逐异常 Pod，定期恢复探测", "重试：attempts=3, perTryTimeout=2s，注意重试风暴（配合重试预算）", "超时：timeout 字段限制请求总时长，防止级联阻塞", "连接池设置：tcpMaxConnections/http2MaxRequests 限制并发", "面试常考：Istio 熔断 vs Sentinel、重试配置、超时与重试组合、连接池"]
    ),
    "### 3.4 mTLS 安全策略": (
        "Istio 通过双向 TLS（mTLS）实现服务间通信加密和身份认证，零信任网络基础。",
        "Istio Citadel（现 istiod）为每个服务签发 SPIFFE 格式的证书（spiffe://cluster/ns/<namespace>/sa/<serviceaccount>），Sidecar 代理自动处理 TLS 握手：客户端 Sidecar 用服务证书加密，服务端 Sidecar 验证客户端证书。PeerAuthentication 配置 mTLS 模式（DISABLE/PERMISSIVE/STRICT），PERMISSIVE 允许明文和 mTLS 混合（迁移期），STRICT 强制 mTLS。AuthorizationPolicy 实现 RBAC 授权。",
        ["证书由 istiod 自动签发和轮转，无需应用感知", "PERMISSIVE 模式兼容明文和 mTLS，用于迁移过渡", "STRICT 模式强制所有服务间通信加密", "AuthorizationPolicy 基于服务身份做 RBAC（允许/拒绝特定路径/方法）", "面试常考：mTLS 原理、SPIFFE 身份、PeerAuthentication、零信任"]
    ),
    "### 3.5 可观测性配置": (
        "Istio 自动生成指标、日志和分布式追踪，无需修改应用代码即可获得全链路可观测能力。",
        "Sidecar 代理（Envoy）自动生成遥测数据：Metrics（请求数/延迟/错误率，Prometheus 格式）、Access Logs（请求日志）、Distributed Tracing（OpenTelemetry/Jaeger/Zipkin，Sidecar 自动传播 trace header）。Kiali 提供服务拓扑图可视化。Envoy 访问日志记录每次请求的状态码、耗时、上游等信息。",
        ["Metrics 自动采集到 Prometheus，Grafana 看板展示 RED 指标", "追踪：Sidecar 自动传播 x-request-id/b3 trace header", "Kiali 可视化服务依赖拓扑和流量状态", "Envoy Access Log 记录每次请求详情", "面试常考：Istio 可观测三大支柱、trace header 传播、Kiali、Envoy 指标"]
    ),
    "### 3.8 外部服务管理（ServiceEntry）": (
        "ServiceEntry 将集群外部服务注册到 Istio 服务网格中，使外部服务也能享受 Sidecar 的流量管理能力。",
        "默认情况下网格内服务访问外部地址（如第三方 API）会被 Sidecar 拦截并按 allowlist 处理。ServiceEntry 将外部域名/IP 注册为网格服务，配置 DNS 名称、端点地址、端口和协议。注册后可对外部服务配置路由规则、重试、熔断、mTLS，并在可观测性中看到外部服务调用。",
        ["ServiceEntry 把外部依赖纳入网格管理，统一可观测和治理", "location: MESH_EXTERNAL 表示集群外服务", "resolution: DNS/STATIC/NONE 决定端点解析方式", "可对外部服务配置 VirtualService 重试、超时、故障注入", "面试常考：ServiceEntry 作用、访问外部服务方式、外部服务治理"]
    ),
}

# ============================================================
# 计网OS八股
# ============================================================
network_os = {
    "### 3.6 IO 多路复用（Java NIO）": (
        "IO 多路复用让一个线程同时监听多个 Channel 的 IO 事件，是高并发网络编程的核心技术。",
        "Linux 提供 select/poll/epoll 三种机制：select 有 1024 文件描述符限制且每次全量遍历；poll 去掉限制但仍全量遍历；epoll 使用事件驱动（epoll_create 创建实例、epoll_ctl 注册 fd、epoll_wait 等待就绪事件），内核通过回调将就绪 fd 加入就绪链表，只返回活跃连接，时间复杂度 O(1)。Java NIO 的 Selector 在 Linux 上基于 epoll 实现，Netty 进一步用 epoll 边缘触发（ET）+ 非阻塞 IO 实现 Reactor 模式。",
        ["select：1024 限制，每次调用全量拷贝 fd 集合到内核", "poll：用链表去掉 fd 数量限制，但仍全量遍历", "epoll：事件驱动，红黑树管理 fd，就绪链表返回活跃连接，O(1)", "epoll LT（水平触发，默认）只要缓冲区有数据就通知；ET（边缘触发）只通知一次，必须非阻塞读完", "面试常考：select/poll/epoll 区别、epoll 为什么高效、LT vs ET、Reactor 模式、Netty 线程模型"]
    ),
}


def run():
    tasks = [
        (os.path.join(BASE, "05-云原生与运维", "Kubernetes 知识点系统梳理_优化版.md"), k8s),
        (os.path.join(BASE, "05-云原生与运维", "Service Mesh 知识点系统梳理_优化版.md"), service_mesh),
        (os.path.join(BASE, "06-计算机基础", "计网OS八股 知识点系统梳理_优化版.md"), network_os),
    ]
    for path, cmap in tasks:
        lines, added = expand(path, cmap, False, False, "")
        print(f"  {os.path.basename(path)}: {lines} lines, {added} blocks added")


if __name__ == "__main__":
    run()
