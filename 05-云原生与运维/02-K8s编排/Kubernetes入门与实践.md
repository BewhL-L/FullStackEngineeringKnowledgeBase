---
title: Kubernetes入门与实践
tags: [Kubernetes, K8s, 容器编排, 云原生, Docker, 微服务部署]
category: 云原生与运维
created: 2026-09-07
updated: 2026-09-07
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[Docker-核心原理与镜像优化]]", "[[Docker-Compose编排]]"]
aliases: [K8s入门与实践, Kubernetes入门, K8s实战]
---

# Kubernetes入门与实践

> Kubernetes（K8s）是Google开源的容器编排平台，已成为云原生时代的事实标准。它提供自动化部署、弹性伸缩、服务发现、负载均衡、滚动更新等能力，让应用在成百上千个容器节点上稳定运行。
>
> **学习路径**：核心概念 → Pod/Deployment → Service/Ingress → 配置管理 → 存储 → 监控运维。

---

## 一、概述：K8s是什么

### 1.1 为什么需要K8s

| 痛点 | 手动运维 | K8s自动化 |
|------|---------|----------|
| 应用部署 | 逐台SSH部署 | 一条命令部署到集群 |
| 弹性伸缩 | 手动加机器、起服务 | HPA自动按CPU/流量扩缩 |
| 故障恢复 | 人工发现、重启 | 健康检查自动重启/漂移 |
| 服务发现 | 手动维护IP/配置 | CoreDNS自动服务发现 |
| 滚动更新 | 逐台操作、易出错 | 声明式滚动更新、一键回滚 |
| 资源隔离 | 进程混部互相影响 | Namespace + ResourceQuota隔离 |

### 1.2 K8s架构

```text
Kubernetes Cluster
├── Master Node（控制平面）
│   ├── kube-apiserver    — 集群API入口，所有操作经此
│   ├── etcd               — 分布式KV存储，保存集群状态
│   ├── kube-scheduler     — 调度Pod到合适的Node
│   ├── kube-controller-manager — 控制器（Deployment/ReplicaSet等）
│   └── cloud-controller-manager — 云厂商集成（可选）
└── Worker Node（数据平面）
    ├── kubelet            — 节点代理，管理Pod生命周期
    ├── kube-proxy         — 网络代理，实现Service负载均衡
    ├── container-runtime  — 容器运行时（containerd/CRI-O）
    └── Pods               — 实际运行的应用容器组
```

### 1.3 核心概念速查

| 概念 | 作用 | 类比 |
|------|------|------|
| Pod | K8s最小调度单元，含1+个容器 | 虚拟机（共享网络/存储） |
| Deployment | 管理Pod副本数、滚动更新 | 进程管理器 |
| Service | 为Pod提供稳定访问入口+负载均衡 | 负载均衡器 |
| Ingress | HTTP/HTTPS路由规则，外部访问入口 | Nginx反向代理 |
| ConfigMap | 非敏感配置管理 | 配置文件 |
| Secret | 敏感信息管理（密码/密钥） | 加密配置 |
| Volume | 持久化存储 | 磁盘挂载 |
| Namespace | 资源隔离分区 | 虚拟集群 |

---

## 二、底层原理：Pod调度与网络

### 2.1 Pod调度流程

```text
用户提交 Deployment YAML
         ↓
kube-apiserver 接收 → 写入 etcd
         ↓
kube-controller-manager 检测到期望副本数 → 创建 ReplicaSet → 创建 Pod（未调度）
         ↓
kube-scheduler 监听未调度Pod → 过滤节点（资源/亲和性/污点）→ 打分 → 选最优节点
         ↓
目标节点 kubelet 检测到分配给自己的Pod → 拉取镜像 → 启动容器 → 上报状态
         ↓
Pod Running → kube-proxy 配置 Service 路由
```

### 2.2 K8s网络模型

**核心原则**：
1. 每个Pod有独立IP，Pod内容器共享网络命名空间
2. Pod之间可以直接通信（无需NAT）
3. Node与Pod之间可以直接通信
4. 容器看到的IP = 其他容器看到的IP

**Service网络（ClusterIP）**：
```text
Client Pod → Service IP（虚拟IP）→ kube-proxy（iptables/IPVS）→ 后端Pod IP
```

---

## 三、实操：部署第一个应用

### 3.1 安装minikube（本地开发）

```bash
# Windows
choco install minikube
minikube start --driver=docker --cpus=4 --memory=8192
minikube status
kubectl get nodes
```

### 3.2 Deployment + Service 部署Nginx

```yaml
# nginx-deploy.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deploy
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25-alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 256Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

```bash
kubectl apply -f nginx-deploy.yaml
kubectl get pods -l app=nginx -o wide
kubectl get svc nginx-svc
kubectl describe deployment nginx-deploy
```

### 3.3 Ingress暴露外部访问

```yaml
# nginx-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: nginx.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-svc
            port:
              number: 80
```

### 3.4 ConfigMap + Secret配置注入

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  app.properties: |
    server.port=8080
    log.level=INFO
    cache.ttl=300
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  db-password: cGFzc3dvcmQxMjM=  # base64编码
---
# Pod中使用
spec:
  containers:
  - name: app
    image: myapp:1.0
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: db-password
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

### 3.5 常用命令速查

```bash
# 查看资源
kubectl get pods|svc|deploy|ingress|cm|secret|pv|pvc -n <namespace>
kubectl describe pod <pod-name>
kubectl logs <pod-name> -c <container> --tail=100 -f

# 操作
kubectl apply -f file.yaml
kubectl delete -f file.yaml
kubectl scale deploy <name> --replicas=5
kubectl rollout status deploy <name>
kubectl rollout undo deploy <name>  # 回滚

# 进入容器
kubectl exec -it <pod-name> -- /bin/sh

# 端口转发
kubectl port-forward svc/<svc-name> 8080:80
```

---

## 四、常见问题与排查

### 4.1 Pod一直Pending

**原因排查**：
```bash
kubectl describe pod <pod-name>
# 查看 Events 部分：
# - Insufficient cpu/memory → 节点资源不足，需扩容或降低requests
# - node(s) had untolerated taint → 污点容忍问题
# - node(s) didn't match node selector → 节点选择器不匹配
# - 0/3 nodes are available → 所有节点都不满足条件
```

### 4.2 Pod CrashLoopBackOff

**排查步骤**：
```bash
# 1. 查看日志
kubectl logs <pod-name> --previous  # 查看上一次崩溃的日志

# 2. 查看事件
kubectl describe pod <pod-name> | grep -A5 Events

# 3. 常见原因
# - 配置错误（环境变量/配置文件缺失）
# - 依赖服务未启动（数据库/Redis连不上）
# - 健康检查失败（livenessProbe路径错误）
# - 资源不足（OOMKilled → 看 dmesg 或 describe 中的 Last State）
# - 镜像拉取失败（ImagePullBackOff → 检查镜像名/标签/Secret）
```

### 4.3 Service无法访问

```bash
# 1. 检查Service selector是否匹配Pod标签
kubectl get svc <svc-name> -o yaml | grep selector
kubectl get pods --show-labels

# 2. 检查Endpoints是否有后端
kubectl get endpoints <svc-name>
# 若为空 → selector不匹配或Pod未Ready

# 3. 检查端口映射
kubectl describe svc <svc-name>
# Port(服务端口) → TargetPort(容器端口) 是否正确
```

---

## 五、进阶与最佳实践

### 5.1 HPA自动伸缩

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
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
```

### 5.2 资源限制最佳实践

```yaml
resources:
  requests:   # 调度依据，保证最低资源
    cpu: 200m      # 0.2核
    memory: 256Mi
  limits:     # 硬限制，超过会被OOMKill或throttle
    cpu: 1000m     # 1核
    memory: 512Mi
```

**原则**：
- requests = 正常负载下的资源需求
- limits = requests × 2~3（应对流量突增）
- CPU可以超卖（throttle），Memory不建议超卖（OOM）
- 关键服务设置 Guaranteed QoS（requests=limits）

### 5.3 生产环境检查清单

- [ ] 所有Pod设置 resources requests/limits
- [ ] 配置 livenessProbe + readinessProbe
- [ ] 使用 Deployment 管理无状态应用，StatefulSet 管理有状态应用
- [ ] 敏感信息用 Secret，非敏感用 ConfigMap
- [ ] 外部访问通过 Ingress，不直接暴露 NodePort
- [ ] 配置 HPA + Cluster Autoscaler
- [ ] 日志采集（EFK/Loki）+ 监控（Prometheus+Grafana）
- [ ] 命名空间按环境/团队隔离（dev/staging/prod）
- [ ] RBAC权限最小化
- [ ] 镜像使用固定标签，不使用 latest

---

## 💡 全文深度讲解

本文系统梳理了Kubernetes入门与实践的核心知识体系，从概述：K8s是什么入手，深入底层原理：Pod调度与网络的底层机制，再通过实操：部署第一个应用掌握实战应用，最后涵盖进阶与最佳实践与关联笔记。学习时建议先建立整体认知，再动手实践，最后结合常见问题深化理解。

## 📝 全文精简总结

- **概述：K8s是什么**：掌握本模块的核心概念与关键要点
- **底层原理：Pod调度与网络**：掌握本模块的核心概念与关键要点
- **实操：部署第一个应用**：掌握本模块的核心概念与关键要点
- **常见问题与排查**：掌握本模块的核心概念与关键要点
- **进阶与最佳实践**：掌握本模块的核心概念与关键要点
- **关联笔记**：掌握本模块的核心概念与关键要点


---

## 关联笔记

- [[Docker-核心原理与镜像优化]] — 容器基础
- [[K8s-核心概念与架构]] — K8s核心概念
- [[Pod与控制器Deployment]] — Pod与Deployment
- [[Service与Ingress]] — 服务暴露
- [[ConfigMap与Secret]] — 配置管理
- [[Helm-Chart包管理]] — Helm包管理
- [[K8s-故障排查手册]] — 故障排查
