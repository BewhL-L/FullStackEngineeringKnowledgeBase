---
title: kubectl命令速查表
tags: [K8s/kubectl, 命令速查, 云原生, 原子笔记]
category: 云原生与运维
created: 2026-08-12
updated: 2026-09-01
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: []
aliases: [kubectl命令速查表]
---



# kubectl命令速查表

> **文档说明**：kubectl 命令的完整速查手册，涵盖集群管理、资源操作、Pod/Deployment/Service 管理、日志调试、配置切换、高级命令、常用别名，以及生产环境最佳实践。
>
> **适用人群**：后端开发、运维工程师、全栈开发者、需要操作 K8s 集群的开发者
>
> **前置知识**：[[K8s-核心概念与架构]]、[[Docker容器化实战]]、[[K8s-服务发现与负载均衡]]

---

## 一、概述

### 1. kubectl 是什么

**kubectl** 是 Kubernetes 的命令行工具，用于与 K8s 集群交互，管理集群资源和应用生命周期。

```bash
kubectl 工作流程：
kubectl 命令 → 本地 kubeconfig 认证 → API Server → etcd → 各组件执行
```

### 2. 命令结构

```bash
kubectl [command] [TYPE] [NAME] [flags]

# command: 操作（get、describe、create、delete...）
# TYPE: 资源类型（pod、deployment、service...）
# NAME: 资源名称（可选，省略则操作所有）
# flags: 选项（-n 命名空间、-o 输出格式...）
```

### 3. 资源类型缩写

| 全称 | 缩写 |
|------|------|
| pods | po |
| services | svc |
| deployments | deploy |
| replicasets | rs |
| daemonsets | ds |
| statefulsets | sts |
| jobs | job |
| cronjobs | cj |
| configmaps | cm |
| secrets | secret |
| namespaces | ns |
| nodes | no |
| persistentvolumes | pv |
| persistentvolumeclaims | pvc |
| ingresses | ing |
| serviceaccounts | sa |
| roles | role |
| rolebindings | rolebinding |
| clusterroles | clusterrole |
| horizontalpodautoscalers | hpa |
| networkpolicies | netpol |

---

## 二、集群与配置

### 1. 集群信息

```bash
# 查看集群信息
kubectl cluster-info

# 查看集群版本
kubectl version --short

# 查看 API 资源列表
kubectl api-resources

# 查看 API 版本
kubectl api-versions
```

### 2. 上下文管理

```bash
# 查看所有上下文
kubectl config get-contexts

# 查看当前上下文
kubectl config current-context

# 切换上下文
kubectl config use-context <context-name>

# 切换命名空间（当前上下文）
kubectl config set-context --current --namespace=<namespace>

# 重命名上下文
kubectl config rename-context <old> <new>

# 删除上下文
kubectl config delete-context <name>
```

### 3. 节点管理

```bash
# 查看节点
kubectl get nodes
kubectl get nodes -o wide  # 详细信息（IP、OS、版本）

# 查看节点详情
kubectl describe node <node-name>

# 标记节点不可调度（维护）
kubectl cordon <node-name>

# 标记节点可调度
kubectl uncordon <node-name>

# 驱逐节点上的 Pod（维护前）
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 查看节点资源使用
kubectl top nodes
```

---

## 三、资源查看

### 1. get 命令

```bash
# 基本查看
kubectl get pods
kubectl get pods -n <namespace>
kubectl get pods --all-namespaces  # 或 -A

# 查看所有资源
kubectl get all
kubectl get all -n <namespace>

# 输出格式
kubectl get pods -o wide       # 宽格式（IP、节点）
kubectl get pods -o yaml       # YAML 格式
kubectl get pods -o json       # JSON 格式
kubectl get pods -o jsonpath='{.items[*].metadata.name}'  # JSONPath

# 标签筛选
kubectl get pods -l app=nginx
kubectl get pods -l app=nginx,tier=frontend
kubectl get pods -l 'app in (nginx, redis)'

# 字段筛选
kubectl get pods --field-selector status.phase=Running

# 排序
kubectl get pods --sort-by=.metadata.name
kubectl get pods --sort-by=.status.startTime

# 持续监控
kubectl get pods -w  # watch 模式
```

### 2. describe 命令

```bash
# 查看资源详情（事件、状态、配置）
kubectl describe pod <pod-name>
kubectl describe pod <pod-name> -n <namespace>
kubectl describe deployment <deploy-name>
kubectl describe service <svc-name>
kubectl describe node <node-name>
```

### 3. 常用查看组合

```bash
# 查看 Pod 及其所在节点
kubectl get pods -o wide

# 查看所有命名空间的 Pod
kubectl get pods -A

# 查看不健康的 Pod
kubectl get pods -A | grep -v Running

# 查看 Pod 的标签
kubectl get pods --show-labels

# 查看 Deployment 的滚动更新状态
kubectl rollout status deployment/<name>
```

---

## 四、资源创建与更新

### 1. 声明式（推荐）

```bash
# 从 YAML 文件创建/更新
kubectl apply -f deployment.yaml

# 从目录创建
kubectl apply -f ./k8s/

# 从 URL 创建
kubectl apply -f https://example.com/deployment.yaml

# 预览变更（不实际执行）
kubectl apply -f deployment.yaml --dry-run=client

# 查看差异
kubectl diff -f deployment.yaml
```

### 2. 命令式

```bash
# 创建 Deployment
kubectl create deployment nginx --image=nginx:latest --replicas=3

# 创建 Service
kubectl expose deployment nginx --port=80 --type=ClusterIP

# 创建 ConfigMap
kubectl create configmap app-config --from-file=config.yaml
kubectl create configmap app-config --from-literal=key=value

# 创建 Secret
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=secret

# 创建命名空间
kubectl create namespace <name>
```

### 3. 编辑与更新

```bash
# 在线编辑资源
kubectl edit deployment <name>
kubectl edit svc <name>

# 更新镜像
kubectl set image deployment/<name> container=image:tag

# 缩放副本
kubectl scale deployment <name> --replicas=5

# 滚动更新
kubectl rollout restart deployment/<name>

# 暂停/恢复滚动更新
kubectl rollout pause deployment/<name>
kubectl rollout resume deployment/<name>

# 回滚
kubectl rollout undo deployment/<name>
kubectl rollout undo deployment/<name> --to-revision=2

# 查看更新历史
kubectl rollout history deployment/<name>
```

### 4. 删除资源

```bash
# 删除 Pod
kubectl delete pod <pod-name>

# 删除 Deployment
kubectl delete deployment <name>

# 从文件删除
kubectl delete -f deployment.yaml

# 按标签删除
kubectl delete pods -l app=nginx

# 删除命名空间（会删除该命名空间下所有资源！）
kubectl delete namespace <name>

# 强制删除（不等待优雅终止）
kubectl delete pod <pod-name> --force --grace-period=0
```

---

## 五、Pod 操作

### 1. 日志查看

```bash
# 查看 Pod 日志
kubectl logs <pod-name>

# 持续跟踪日志
kubectl logs -f <pod-name>

# 查看最近 N 行
kubectl logs --tail=100 <pod-name>

# 查看最近 N 分钟的日志
kubectl logs --since=10m <pod-name>

# 多容器 Pod 指定容器
kubectl logs <pod-name> -c <container-name>

# 查看上一个容器的日志（崩溃重启后）
kubectl logs <pod-name> --previous

# 按标签查看所有 Pod 日志
kubectl logs -l app=nginx --all-containers

# 时间戳
kubectl logs --timestamps <pod-name>
```

### 2. 进入容器

```bash
# 进入 Pod 的 shell
kubectl exec -it <pod-name> -- /bin/bash
kubectl exec -it <pod-name> -- /bin/sh  # Alpine 镜像

# 多容器指定容器
kubectl exec -it <pod-name> -c <container> -- /bin/bash

# 执行单条命令
kubectl exec <pod-name> -- ls /app
kubectl exec <pod-name> -- env
kubectl exec <pod-name> -- cat /etc/hosts
```

### 3. 端口转发

```bash
# 本地端口转发到 Pod
kubectl port-forward pod/<pod-name> 8080:80

# 转发到 Service
kubectl port-forward svc/<svc-name> 8080:80

# 转发到 Deployment
kubectl port-forward deployment/<name> 8080:80

# 本地和目标端口相同
kubectl port-forward pod/<pod-name> 8080
```

### 4. 复制文件

```bash
# 从 Pod 复制文件到本地
kubectl cp <namespace>/<pod-name>:/path/to/file ./local-file

# 从本地复制到 Pod
kubectl cp ./local-file <namespace>/<pod-name>:/path/to/file

# 指定容器
kubectl cp ./file <pod-name>:/path -c <container>
```

---

## 六、调试与排障

### 1. 事件查看

```bash
# 查看命名空间事件
kubectl get events
kubectl get events -n <namespace>
kubectl get events -A  # 所有命名空间

# 按时间排序
kubectl get events --sort-by=.lastTimestamp

# 查看 Pod 的事件（describe 中也包含）
kubectl describe pod <pod-name> | grep -A 20 Events
```

### 2. 临时调试容器

```bash
# 临时调试容器（K8s 1.23+，Ephemeral Containers）
kubectl debug -it <pod-name> --image=busybox --target=<container-name>

# 复制 Pod 并添加调试容器
kubectl debug -it <pod-name> --image=busybox --copy-to=debug-pod

# 在节点上调试（特权容器）
kubectl debug node/<node-name> -it --image=busybox
```

### 3. 网络调试

```bash
# 创建临时调试 Pod
kubectl run debug --image=nicolaka/netshoot --rm -it --restart=Never -- bash

# 测试 Service 连通性
kubectl run curl --image=curlimages/curl --rm -it --restart=Never -- \
  curl http://<service-name>.<namespace>.svc.cluster.local

# DNS 解析测试
kubectl run dnsutils --image=registry.k8s.io/e2e-test-images/jessie-dnsutils:1.3 \
  --rm -it --restart=Never -- nslookup kubernetes.default
```

### 4. 资源使用

```bash
# 查看 Pod 资源使用
kubectl top pods
kubectl top pods -n <namespace>
kubectl top pods --containers  # 按容器显示

# 查看节点资源使用
kubectl top nodes

# 按 CPU 排序
kubectl top pods --sort-by=cpu

# 按内存排序
kubectl top pods --sort-by=memory
```

---

## 七、配置与密钥

### 1. ConfigMap

```bash
# 创建 ConfigMap
kubectl create configmap <name> --from-file=config.yaml
kubectl create configmap <name> --from-literal=key1=value1 --from-literal=key2=value2
kubectl create configmap <name> --from-env-file=.env

# 查看
kubectl get configmaps
kubectl describe configmap <name>
kubectl get configmap <name> -o yaml
```

### 2. Secret

```bash
# 创建 Secret
kubectl create secret generic <name> \
  --from-literal=username=admin \
  --from-literal=password=secret

# 从文件创建
kubectl create secret generic <name> --from-file=ssh-privatekey=~/.ssh/id_rsa

# Docker registry 密钥
kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=pass \
  --docker-email=user@example.com

# TLS 证书
kubectl create secret tls <name> --cert=tls.crt --key=tls.key

# 查看（base64 编码）
kubectl get secret <name> -o yaml
# 解码
kubectl get secret <name> -o jsonpath='{.data.password}' | base64 -d
```

---

## 八、高级命令

### 1. 标签与注解

```bash
# 添加标签
kubectl label pod <pod-name> env=production
kubectl label pod <pod-name> env=staging --overwrite  # 覆盖

# 删除标签
kubectl label pod <pod-name> env-

# 添加注解
kubectl annotate pod <pod-name> description="my app"

# 查看标签
kubectl get pods --show-labels
```

### 2. 污点与容忍

```bash
# 添加污点
kubectl taint nodes <node> key=value:NoSchedule

# 删除污点
kubectl taint nodes <node> key=value:NoSchedule-

# 查看节点污点
kubectl describe node <node> | grep Taints
```

### 3. 自动伸缩

```bash
# 创建 HPA
kubectl autoscale deployment <name> --min=2 --max=10 --cpu-percent=80

# 查看 HPA
kubectl get hpa
kubectl describe hpa <name>
```

### 4. 资源导出

```bash
# 导出资源为 YAML（去除运行时字段）
kubectl get deployment <name> -o yaml --export  # 旧版
kubectl get deployment <name> -o yaml | grep -v 'resourceVersion\|uid\|creationTimestamp\|selfLink\|generation\|managedFields'  # 手动清理

# 导出所有资源
kubectl get all -o yaml > cluster-backup.yaml
```

---

## 九、常用别名与快捷方式

### 1. Shell 别名

```bash
# ~/.bashrc 或 ~/.zshrc
alias k='kubectl'
alias kg='kubectl get'
alias kgp='kubectl get pods'
alias kgd='kubectl get deployments'
alias kgs='kubectl get services'
alias kgn='kubectl get nodes'
alias kd='kubectl describe'
alias kdp='kubectl describe pod'
alias kdel='kubectl delete'
alias kex='kubectl exec -it'
alias kl='kubectl logs -f'
alias kctx='kubectl config use-context'
alias kns='kubectl config set-context --current --namespace'
```

### 2. kubectl 插件（krew）

```bash
# 安装 krew（插件管理器）
# https://krew.sigs.k8s.io/docs/user-guide/setup/install/

# 常用插件
kubectl krew install ctx      # 上下文切换
kubectl krew install ns       # 命名空间切换
kubectl krew install tree     # 资源树视图
kubectl krew install view-secret  # 查看 Secret（自动解码）
kubectl krew install df-pv    # PV 磁盘使用
kubectl krew install access-matrix  # 权限矩阵

# 使用插件
kubectl ctx          # 切换上下文
kubectl ns           # 切换命名空间
kubectl tree deploy <name>  # 查看资源树
```

---

## 十、最佳实践

### 1. 操作规范

- [ ] **使用声明式**：优先 `apply -f`，避免命令式创建
- [ ] **使用命名空间**：按环境/团队隔离资源
- [ ] **dry-run 验证**：变更前用 `--dry-run=client` 预览
- [ ] **diff 检查**：`kubectl diff` 查看变更差异
- [ ] **资源限制**：为 Pod 设置 requests 和 limits
- [ ] **健康检查**：配置 livenessProbe 和 readinessProbe
- [ ] **滚动更新**：使用 `rollout restart` 而非删 Pod
- [ ] **备份配置**：重要资源导出 YAML 备份

### 2. 安全规范

- [ ] **最小权限**：ServiceAccount 只授予必要权限
- [ ] **RBAC 管理**：不使用 cluster-admin 日常操作
- [ ] **Secret 加密**：敏感信息用 Secret，不写在 ConfigMap
- [ ] **镜像安全**：使用可信镜像源，扫描镜像漏洞
- [ ] **网络策略**：配置 NetworkPolicy 限制通信
- [ ] **审计日志**：开启 API Server 审计

### 3. 排障流程

```text
Pod 排障流程：
1. kubectl get pods → 查看状态（Pending/CrashLoopBackOff/ImagePullBackOff）
2. kubectl describe pod → 查看事件和原因
3. kubectl logs → 查看应用日志
4. kubectl logs --previous → 查看上一次崩溃日志
5. kubectl exec → 进入容器排查
6. kubectl debug → 临时调试容器
```

---

## 十一、常见问题与排查

| 问题 | 原因 | 排查命令 |
|------|------|---------|
| **Pod Pending** | 资源不足 / 调度失败 | `kubectl describe pod` 看 Events |
| **CrashLoopBackOff** | 应用启动失败 / 配置错误 | `kubectl logs --previous` |
| **ImagePullBackOff** | 镜像不存在 / 认证失败 | `kubectl describe pod` 看镜像拉取错误 |
| **CrashLoopBackOff** | 应用启动失败 / 配置错误 | `kubectl logs --previous` |
| **OOMKilled** | 内存超出 limits | `kubectl describe pod` 看 Last State |
| **Service 不通** | 标签选择器不匹配 / 端口错误 | `kubectl get endpoints` 检查后端 |
| **DNS 解析失败** | CoreDNS 异常 / 网络策略 | `kubectl get pods -n kube-system` |
| **节点 NotReady** | kubelet 异常 / 资源耗尽 | `kubectl describe node` |
| **PV 绑定失败** | StorageClass 不存在 / 容量不足 | `kubectl get pvc` 查看状态 |
| **HPA 不生效** | metrics-server 未安装 / 无资源请求 | `kubectl top pods` 验证 |
| **权限被拒** | RBAC 权限不足 | `kubectl auth can-i` 检查权限 |
| **端口转发失败** | Pod 未就绪 / 端口错误 | `kubectl get pods` 检查状态 |
| **日志为空** | 应用输出到文件而非 stdout | 检查应用日志配置 |
| **配置未生效** | ConfigMap 更新但 Pod 未重启 | `kubectl rollout restart` |
| **滚动更新卡住** | 就绪探针失败 / 资源不足 | `kubectl rollout status` + `describe` |

---

## 十二、关联笔记

### K8s 相关
- [[K8s-核心概念与架构]] · [[K8s-服务发现与负载均衡]] · [[K8s-存储与配置管理]]
- [[K8s-网络模型与CNI]] · [[云原生架构设计]]

### 容器与运维
- [[Docker容器化实战]] · [[多架构镜像构建-buildx]] · [[APM应用性能监控-SkyWalking]]
- [[SBOM软件物料清单]] · [[依赖漏洞检测-Snyk]]

### 导航
- [[MOC-云原生与运维]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Docker容器化实战]] 容器基础 → 学习 [[K8s-核心概念与架构]] K8s 架构 → 熟练本文 kubectl 命令 → 实践 [[K8s-服务发现与负载均衡]] 服务管理 → 研究 [[云原生架构设计]] 云原生体系 → 构建完整的云原生运维能力。
