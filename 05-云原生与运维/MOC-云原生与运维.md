---
title: 云原生与运维 MOC
tags: [Docker, Kubernetes, Linux, Nginx, MOC, 云原生, DevOps, CI/CD]
category: 云原生与运维
created: 2026-08-12
updated: 2026-09-01
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: []
aliases: [MOC-容器化]
---

# ☁️ 云原生与运维 MOC

> 现代云原生技术栈与 DevOps 运维体系，覆盖容器化、K8s编排、CI/CD流水线、监控可观测、基础设施即代码、网络与Linux六大领域，共 50 篇文档。
>
> **学习建议**：先掌握 Docker 容器化，再深入 Kubernetes 编排，然后学习 CI/CD 和监控可观测，最后探索 IaC 和云原生架构。

---

## 📚 学习路线

```text
入门阶段：Linux基础 → Docker容器 → Docker Compose → Nginx反向代理
进阶阶段：K8s核心概念 → Pod/Deployment/Service → Ingress → Helm → CI/CD流水线
高级阶段：K8s深入(Operator/CRD/HPA) → 监控可观测(Prometheus/Grafana/ELK) → Service Mesh
专家阶段：IaC(Terraform/Ansible) → GitOps(ArgoCD) → 混沌工程 → 高可用架构 → AIOps
```

---

## 📂 文档索引

### 一、容器化

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Docker 知识点系统梳理_优化版\|Docker知识点系统梳理]] | Docker核心概念、镜像、容器、仓库、网络、数据卷、Dockerfile、Compose、面试考点 | 🟡进阶 |
| [[Docker命令速查表]] | Docker高频命令速查、镜像管理、容器管理、网络、数据卷、清理、调试 | 🟢入门 |
| [[Dockerfile最佳实践]] | Dockerfile编写最佳实践、多阶段构建、层缓存、镜像瘦身、安全、.dockerignore | 🟡进阶 |
| [[Docker-核心原理与镜像优化]] | Docker核心原理、Namespace/Cgroups、UnionFS、镜像分层、镜像优化、构建加速 | 🔴高级 |
| [[Docker-Compose编排]] | Docker Compose编排、多容器应用、服务定义、网络、数据卷、环境变量、部署 | 🟡进阶 |
| [[多架构镜像构建-buildx]] | 多架构镜像构建、buildx、QEMU、ARM64/AMD64、manifest、构建优化、跨平台部署 | 🟡进阶 |
| [[容器安全与镜像扫描]] | 容器安全、镜像扫描、Trivy、漏洞管理、最小权限、只读文件系统、网络隔离 | 🔴高级 |

### 二、K8s编排

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Kubernetes 知识点系统梳理_优化版\|Kubernetes知识点系统梳理]] | K8s核心概念、架构、Pod、控制器、Service、存储、网络、安全、运维、面试考点 | 🔴高级 |
| [[K8s-核心概念与架构]] | K8s核心概念、架构设计、Master/Node、etcd、API Server、Scheduler、Controller Manager | 🟡进阶 |
| [[Pod与控制器Deployment]] | Pod生命周期、容器、探针、Deployment、ReplicaSet、滚动更新、回滚、扩缩容 | 🟡进阶 |
| [[Service与Ingress]] | Service类型、ClusterIP/NodePort/LoadBalancer、Ingress、Ingress Controller、路由规则、TLS | 🟡进阶 |
| [[ConfigMap与Secret]] | ConfigMap配置管理、Secret敏感信息、环境变量、配置文件、挂载、加密、外部配置 | 🟡进阶 |
| [[K8s-资源限制与HPA]] | 资源限制、Requests/Limits、QoS、HPA水平自动扩缩、VPA、Cluster Autoscaler、指标 | 🔴高级 |
| [[Helm-Chart包管理]] | Helm包管理、Chart结构、模板、Values、Release、仓库、依赖、版本管理、最佳实践 | 🟡进阶 |
| [[Kustomize-K8s配置管理]] | Kustomize配置管理、Overlay、Base、Patch、生成器、转换器、多环境管理 | 🟡进阶 |
| [[Operator与CRD开发]] | Operator模式、CRD自定义资源、Controller、Reconcile、Operator SDK、kubebuilder、最佳实践 | 🔴高级 |
| [[Service Mesh 知识点系统梳理_优化版\|Service Mesh知识点系统梳理]] | Service Mesh、Istio、Sidecar、流量管理、可观测性、安全、VirtualService、DestinationRule | 🔴高级 |
| [[K8s-故障排查手册]] | K8s故障排查、Pod状态、事件、日志、网络、存储、权限、资源、常见问题、工具 | 🔴高级 |
| [[kubectl命令速查表]] | kubectl命令速查、资源管理、调试、日志、执行、配置、插件、常用操作 | 🟢入门 |

### 三、CI/CD流水线

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Jenkins流水线实战]] | Jenkins流水线、Pipeline as Code、Jenkinsfile、阶段、步骤、代理、凭据、多分支、最佳实践 | 🟡进阶 |
| [[GitLab-CI配置]] | GitLab CI/CD、.gitlab-ci.yml、Job、Stage、Runner、缓存、制品、环境、部署 | 🟡进阶 |
| [[GitHub-Actions流水线设计]] | GitHub Actions、Workflow、Job、Step、Action、Runner、矩阵、缓存、制品、部署、最佳实践 | 🟡进阶 |
| [[ArgoCD-GitOps持续部署]] | ArgoCD、GitOps、应用管理、同步策略、回滚、多集群、ApplicationSet、最佳实践 | 🔴高级 |
| [[CI-CD安全与凭据管理]] | CI/CD安全、凭据管理、Secret、密钥轮换、最小权限、供应链安全、SBOM、签名验证 | 🔴高级 |

### 四、监控可观测

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Prometheus-指标采集]] | Prometheus监控、指标采集、PromQL、Exporter、告警规则、服务发现、存储、联邦、高可用 | 🔴高级 |
| [[Grafana-可视化看板]] | Grafana可视化、Dashboard、Panel、数据源、变量、告警、权限、模板、最佳实践 | 🟡进阶 |
| [[ELK-日志聚合]] | ELK栈、Elasticsearch、Logstash、Kibana、Beats、日志采集、解析、检索、可视化、性能 | 🔴高级 |
| [[Jaeger-分布式链路追踪]] | Jaeger链路追踪、OpenTelemetry、Trace/Span、采样、存储、UI、性能分析、最佳实践 | 🔴高级 |
| [[APM应用性能监控-SkyWalking]] | SkyWalking APM、Agent、Trace、拓扑、性能分析、告警、自定义埋点、多语言支持 | 🔴高级 |
| [[Sentry错误监控与追踪]] | Sentry错误监控、异常捕获、堆栈还原、Release、性能监控、告警、集成、最佳实践 | 🟡进阶 |
| [[告警体系设计]] | 告警体系设计、告警分级、降噪、抑制、聚合、值班、On-Call、升级、复盘、最佳实践 | 🔴高级 |
| [[AIOps智能运维实战]] | AIOps智能运维、异常检测、根因分析、预测、自动化、机器学习、监控数据、最佳实践 | 🔴高级 |

### 五、基础设施即代码

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Terraform-基础设施编排]] | Terraform IaC、HCL、Provider、Resource、Module、State、Plan/Apply、工作区、后端、最佳实践 | 🔴高级 |
| [[Ansible-配置管理]] | Ansible配置管理、Inventory、Playbook、Module、Role、变量、模板、循环、条件、最佳实践 | 🟡进阶 |
| [[Pulumi-现代IaC]] | Pulumi现代IaC、多语言、TypeScript/Python/Go、资源、组件、Stack、状态、与Terraform对比 | 🟡进阶 |
| [[制品管理与镜像仓库]] | 制品管理、镜像仓库、Harbor、Nexus、版本管理、清理、安全扫描、复制、最佳实践 | 🟡进阶 |
| [[依赖漏洞检测-Snyk]] | Snyk依赖漏洞检测、代码扫描、容器扫描、IaC扫描、依赖管理、修复、CI/CD集成、最佳实践 | 🟡进阶 |
| [[SBOM软件物料清单]] | SBOM软件物料清单、SPDX、CycloneDX、生成工具、依赖追踪、漏洞管理、供应链安全、合规 | 🔴高级 |
| [[混沌工程-ChaosMesh]] | 混沌工程、ChaosMesh、故障注入、实验设计、稳态验证、自动化、K8s混沌、最佳实践 | 🔴高级 |

### 六、网络与Linux

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Linux 常用命令知识点系统梳理_优化版\|Linux常用命令知识点系统梳理]] | Linux常用命令、文件管理、进程管理、网络、文本处理、权限、磁盘、Shell、面试考点 | 🟡进阶 |
| [[Linux-运维常用命令手册]] | Linux运维常用命令、系统监控、性能分析、网络诊断、日志查看、安全、故障排查 | 🟡进阶 |
| [[Nginx 知识点系统梳理_优化版\|Nginx知识点系统梳理]] | Nginx核心、配置、反向代理、负载均衡、静态资源、缓存、SSL、安全、性能优化、面试考点 | 🟡进阶 |
| [[Nginx-反向代理与负载均衡]] | Nginx反向代理、负载均衡算法、upstream、健康检查、会话保持、WebSocket、缓存、SSL终止 | 🟡进阶 |
| [[Git工作流-GitFlow与Trunk]] | Git工作流、GitFlow、Trunk Based、分支策略、发布流程、代码评审、合并策略、最佳实践 | 🟡进阶 |
| [[代码评审规范]] | 代码评审规范、评审流程、Checklist、代码质量、安全、性能、最佳实践、工具集成 | 🟡进阶 |
| [[语义化版本与CHANGELOG]] | 语义化版本SemVer、版本号规则、CHANGELOG编写、发布流程、兼容性、依赖管理、最佳实践 | 🟢入门 |
| [[API设计规范-OpenAPI]] | OpenAPI规范、API设计、RESTful、文档生成、Swagger、版本管理、错误处理、安全、最佳实践 | 🟡进阶 |
| [[高可用架构设计]] | 高可用架构、冗余、故障转移、负载均衡、限流熔断、容灾备份、SLA、容量规划、最佳实践 | 🔴高级 |
| [[DevOps与云原生知识点完整整合大全_优化版\|DevOps与云原生知识点完整整合大全]] | DevOps与云原生完整知识体系、Docker/K8s/CI-CD/监控/IaC/安全/网络/Linux/架构设计 | 🔴高级 |

### 七、项目管理与协作

| 文档 | 说明 | 难度 |
|------|------|------|
| [[敏捷开发与Scrum]] | 敏捷宣言、Scrum框架（角色/事件/工件）、故事点估算、看板可视化、常见误区、规模化敏捷 | 🟡进阶 |

---

## 🔗 知识关联

```text
云原生与运维体系
├── 容器化 ← 应用打包与隔离
│   ├── Docker → 镜像、容器、仓库
│   ├── Docker Compose → 多容器编排
│   └── 容器安全 → 镜像扫描、最小权限
├── K8s编排 ← 容器编排与调度
│   ├── Pod/Deployment → 工作负载
│   ├── Service/Ingress → 网络访问
│   ├── ConfigMap/Secret → 配置管理
│   ├── Helm → 包管理
│   ├── Operator → 自动化运维
│   └── Service Mesh → 服务网格
├── CI/CD流水线 ← 持续集成与部署
│   ├── Jenkins/GitLab CI → 流水线
│   ├── GitHub Actions → 云端CI
│   ├── ArgoCD → GitOps部署
│   └── CI/CD安全 → 凭据、供应链
├── 监控可观测 ← 系统可观测性
│   ├── Prometheus → 指标监控
│   ├── Grafana → 可视化
│   ├── ELK → 日志聚合
│   ├── Jaeger/SkyWalking → 链路追踪
│   ├── Sentry → 错误监控
│   └── AIOps → 智能运维
├── 基础设施即代码 ← 基础设施自动化
│   ├── Terraform → 基础设施编排
│   ├── Ansible → 配置管理
│   ├── Pulumi → 现代IaC
│   ├── 混沌工程 → 故障注入
│   └── SBOM → 软件物料清单
└── 网络与Linux ← 基础运维
    ├── Linux → 命令、系统管理
    ├── Nginx → 反向代理、负载均衡
    ├── Git工作流 → 分支策略
    └── 高可用架构 → 架构设计
```

- **Docker** 是容器化的基础，与 [[MOC-后端开发|后端开发]] 应用部署紧密关联
- **Kubernetes** 是容器编排的标准，与 [[MOC-分布式与中间件|分布式系统]] 紧密关联
- **CI/CD** 是 DevOps 的核心，与 [[MOC-通用工具|通用工具]] Git 工作流紧密关联
- **监控可观测** 是系统稳定性的保障，与 [[SkyWalking-分布式链路追踪|SkyWalking]] 紧密关联
- **IaC** 是基础设施自动化的趋势，与云平台和 K8s 紧密关联

---

## 📖 学习顺序

1. **Linux基础**：[[Linux 常用命令知识点系统梳理_优化版|Linux常用命令]] → [[Nginx 知识点系统梳理_优化版|Nginx]]
2. **容器化**：[[Docker 知识点系统梳理_优化版|Docker]] → [[Dockerfile最佳实践|Dockerfile]] → [[Docker-Compose编排|Docker Compose]]
3. **K8s入门**：[[K8s-核心概念与架构|K8s核心概念]] → [[Pod与控制器Deployment|Pod/Deployment]] → [[Service与Ingress|Service/Ingress]]
4. **K8s深入**：[[Kubernetes 知识点系统梳理_优化版|K8s大全]] → [[Helm-Chart包管理|Helm]] → [[K8s-资源限制与HPA|HPA]] → [[Operator与CRD开发|Operator]]
5. **CI/CD**：[[Jenkins流水线实战|Jenkins]] → [[GitHub-Actions流水线设计|GitHub Actions]] → [[ArgoCD-GitOps持续部署|ArgoCD]]
6. **监控可观测**：[[Prometheus-指标采集|Prometheus]] → [[Grafana-可视化看板|Grafana]] → [[ELK-日志聚合|ELK]] → [[Jaeger-分布式链路追踪|Jaeger]]
7. **IaC**：[[Terraform-基础设施编排|Terraform]] → [[Ansible-配置管理|Ansible]]
8. **高级**：[[Service Mesh 知识点系统梳理_优化版|Service Mesh]] → [[混沌工程-ChaosMesh|混沌工程]] → [[高可用架构设计|高可用架构]]

---

## 🚀 知识域旗舰全集

- [[DevOps与云原生知识点完整整合大全_优化版|DevOps与云原生知识点完整整合大全]] — Docker/K8s/CI-CD/监控/IaC/安全/网络/Linux/架构设计完整知识体系

## 🧩 排查与进阶手册

- [[K8s-故障排查手册|K8s故障排查手册]] — Pod状态、事件、日志、网络、存储、权限、资源、常见问题、工具

## 🏷️ 相关标签

`#云原生` `#Docker` `#Kubernetes` `#K8s` `#DevOps` `#CI/CD` `#监控` `#Prometheus` `#Grafana` `#ELK` `#Terraform` `#Ansible` `#Nginx` `#Linux` `#ServiceMesh` `#GitOps` `#高可用`

---

[[Home|🏠 返回首页]] · [[MOC-综合导航|📚 综合导航]] · [[学习路线总览|🗺️ 学习路线]]
---

## 📝 新增文档（2026-09）

- [[Kubernetes入门与实践|Kubernetes入门与实践]]
- [[Docker容器化部署实战|Docker容器化部署实战]]

