---
title: DevOps MOC（四级展开）
tags: [MOC, DevOps, 枢纽]
created: 2026-08-13
updated: 2026-08-13
hub: true
---

# ☁️ DevOps & 研发工程化 MOC

> 从代码到生产的全链路工程化体系，覆盖容器化、Kubernetes、CI/CD、监控可观测性与基础设施即代码。
> **标签前缀**：`#DevOps/`
> **枢纽核心笔记**：[[DevOps-工程化枢纽]]

---

## 📐 知识层级总览

```
一级：DevOps & 研发工程化
├── 二级：7.1 容器化
│   ├── 三级：Docker-核心原理与镜像优化
│   │   ├── 四级：镜像分层与UnionFS
│   │   ├── 四级：容器运行时
│   │   ├── 四级：网络模式
│   │   └── 四级：数据卷与持久化
│   ├── 三级：Docker-Compose编排
│   ├── 三级：Dockerfile最佳实践
│   └── 三级：多阶段构建与瘦身
├── 二级：7.2 Kubernetes
├── 二级：7.3 CI/CD
├── 二级：7.4 监控与可观测性
├── 二级：7.5 基础设施即代码
└── 二级：7.6 研发流程规范
```

---

## 📚 7.1 容器化

### [[Docker-核心原理与镜像优化|Docker 核心原理与镜像优化]]
> 容器技术的基础

- **四级子知识点**：
  - 镜像分层与 UnionFS
  - 容器运行时（containerd）
  - 网络模式（bridge/host/none）
  - 数据卷与持久化
  - 镜像优化策略
  - 安全最佳实践
  - 与虚拟机对比
- **标签**：`#DevOps/容器化`

### [[Docker-Compose编排|Docker Compose 编排]]
> 单机多容器编排

- **四级子知识点**：
  - compose 文件格式
  - 服务定义与依赖
  - 网络与卷配置
  - 环境变量与密钥
  - 扩展与覆盖
  - 生产环境使用
  - 与 K8s 的关系
- **标签**：`#DevOps/容器化`

### [[Dockerfile最佳实践|Dockerfile 最佳实践]]
> 高效镜像构建

- **四级子知识点**：
  - 指令详解
  - 层缓存优化
  - 多阶段构建
  - 非 root 用户
  - 镜像瘦身
  - 安全扫描
  - 构建参数
- **标签**：`#DevOps/容器化`

---

## 📚 7.2 Kubernetes

### [[K8s-核心概念与架构|K8s 核心概念与架构]]
> 容器编排事实标准

- **四级子知识点**：
  - K8s 架构（Master/Node）
  - etcd 与控制平面
  - kubelet 与 kube-proxy
  - 声明式 API
  - 控制器模式
  - 资源对象体系
  - 与 Docker Swarm 对比
- **标签**：`#DevOps/K8s`

### [[Pod与控制器Deployment|Pod 与控制器 Deployment]]
> K8s 最核心的工作负载

- **四级子知识点**：
  - Pod 定义与生命周期
  - 多容器 Pod
  - Deployment 滚动更新
  - 回滚与暂停
  - StatefulSet 有状态应用
  - DaemonSet 守护进程
  - Job/CronJob 批处理
- **标签**：`#DevOps/K8s`

### [[Service与Ingress|Service 与 Ingress]]
> K8s 服务暴露

- **四级子知识点**：
  - Service 类型（ClusterIP/NodePort/LoadBalancer）
  - 服务发现
  - Ingress 规则
  - Ingress Controller
  - TLS 证书
  - 灰度发布
  - 网关选型
- **标签**：`#DevOps/K8s`

### [[ConfigMap与Secret|ConfigMap 与 Secret]]
> K8s 配置管理

- **四级子知识点**：
  - ConfigMap 创建与使用
  - Secret 类型
  - 环境变量注入
  - 配置文件挂载
  - 热更新
  - 加密与安全
  - 外部配置中心集成
- **标签**：`#DevOps/K8s`

### [[Helm-Chart包管理|Helm Chart 包管理]]
> K8s 应用包管理

- **四级子知识点**：
  - Helm 架构
  - Chart 结构
  - 模板语法
  - Values 管理
  - 仓库与发布
  - 最佳实践
  - 与 Kustomize 对比
- **标签**：`#DevOps/K8s`

### [[K8s-资源限制与HPA|K8s 资源限制与 HPA]]
> 弹性伸缩与资源管理

- **四级子知识点**：
  - Requests 与 Limits
  - QoS 等级
  - HPA 自动扩缩
  - VPA 垂直扩缩
  - 集群自动伸缩
  - 资源配额
  - 限流与熔断
- **标签**：`#DevOps/K8s`

### [[K8s-故障排查手册|K8s 故障排查手册]]
> K8s 运维必备

- **四级子知识点**：
  - kubectl 调试命令
  - Pod 状态排查
  - 日志查看
  - 事件分析
  - 网络问题定位
  - 常见故障模式
  - 应急回滚
- **标签**：`#DevOps/K8s`

---

## 📚 7.3 CI/CD

### [[GitHub-Actions流水线设计|GitHub Actions 流水线设计]]
> 最流行的 CI/CD 平台

- **四级子知识点**：
  - Workflow 语法
  - Job 与 Step
  - 矩阵构建
  - 缓存优化
  - 环境与密钥
  - 自托管 Runner
  - 最佳实践
- **标签**：`#DevOps/CI-CD`

### [[GitLab-CI配置|GitLab CI 配置]]
> 自托管 CI/CD 方案

- **四级子知识点**：
  - .gitlab-ci.yml 语法
  - Stage 与 Job
  - Runner 配置
  - 缓存与制品
  - 环境部署
  - 与 GitHub Actions 对比
- **标签**：`#DevOps/CI-CD`

### [[ArgoCD-GitOps持续部署|ArgoCD GitOps 持续部署]]
> GitOps 持续部署标准

- **四级子知识点**：
  - GitOps 理念
  - ArgoCD 架构
  - Application 定义
  - 同步策略
  - 多环境管理
  - 回滚与审计
  - 与传统 CD 对比
- **标签**：`#DevOps/CI-CD`

### [[制品管理与镜像仓库|制品管理与镜像仓库]]
> 构建产物管理

- **四级子知识点**：
  - 镜像仓库（Harbor）
  - 制品仓库（Nexus）
  - 版本管理
  - 安全扫描
  - 镜像签名
  - 清理策略
- **标签**：`#DevOps/CI-CD`

---

## 📚 7.4 监控与可观测性

### [[Prometheus-指标采集|Prometheus 指标采集]]
> 云原生监控标准

- **四级子知识点**：
  - Prometheus 架构
  - 指标类型
  - PromQL 查询
  - 服务发现
  - 告警规则
  - 长期存储
  - 联邦集群
- **标签**：`#DevOps/可观测性`

### [[Grafana-可视化看板|Grafana 可视化看板]]
> 监控数据可视化

- **四级子知识点**：
  - 数据源配置
  - Dashboard 设计
  - 面板类型
  - 变量与模板
  - 告警通知
  - 权限管理
  - 最佳实践
- **标签**：`#DevOps/可观测性`

### [[ELK-日志聚合|ELK 日志聚合]]
> 日志收集与分析

- **四级子知识点**：
  - Elasticsearch 索引
  - Logstash 管道
  - Kibana 查询
  - Filebeat 采集
  - 日志规范
  - 性能优化
  - 与 Loki 对比
- **标签**：`#DevOps/可观测性`

### [[Jaeger-分布式链路追踪|Jaeger 分布式链路追踪]]
> 微服务可观测性

- **四级子知识点**：
  - 分布式追踪原理
  - OpenTelemetry 标准
  - Span 与 Trace
  - 采样策略
  - 性能影响
  - 与日志/指标关联
  - 故障定位
- **标签**：`#DevOps/可观测性`

### [[告警体系设计|告警体系设计]]
> 告警不是越多越好

- **四级子知识点**：
  - 告警分级
  - 告警收敛
  - 值班与升级
  - 告警渠道
  - 降噪策略
  - 告警复盘
  - SLO/SLI/SLA
- **标签**：`#DevOps/可观测性`

---

## 📚 7.5 基础设施即代码

### [[Terraform-基础设施编排|Terraform 基础设施编排]]
> IaC 事实标准

- **四级子知识点**：
  - Terraform 核心概念
  - HCL 语法
  - Provider 与 Resource
  - State 管理
  - Module 复用
  - 工作区与环境
  - 最佳实践
- **标签**：`#DevOps/IaC`

### [[Ansible-配置管理|Ansible 配置管理]]
> 自动化配置工具

- **四级子知识点**：
  - Ansible 架构
  - Inventory 管理
  - Playbook 编写
  - Role 组织
  - 变量与模板
  - 幂等性
  - 与 Terraform 配合
- **标签**：`#DevOps/IaC`

### [[Nginx-反向代理与负载均衡|Nginx 反向代理与负载均衡]]
> Web 服务器与负载均衡

- **四级子知识点**：
  - Nginx 架构
  - 反向代理
  - 负载均衡算法
  - 静态资源
  - 缓存配置
  - 安全加固
  - 性能调优
- **标签**：`#DevOps/IaC`

### [[Linux-运维常用命令手册|Linux 运维常用命令手册]]
> 运维速查

- **四级子知识点**：
  - 系统信息
  - 进程管理
  - 网络诊断
  - 磁盘与文件
  - 性能分析
  - 日志查看
  - 安全检查
- **标签**：`#DevOps/IaC`

---

## 📚 7.6 研发流程规范

### [[Git工作流-GitFlow与Trunk|Git 工作流 - GitFlow 与 Trunk]]
> 团队协作规范

- **四级子知识点**：
  - GitFlow 工作流
  - Trunk Based 开发
  - 分支策略
  - 代码合并
  - 发布流程
  - 热修复
  - 选型建议
- **标签**：`#DevOps/研发规范`

### [[代码评审规范|代码评审规范]]
> 代码质量保障

- **四级子知识点**：
  - 评审流程
  - 评审清单
  - 常见问题
  - 工具辅助
  - 文化建设
  - 效率提升
- **标签**：`#DevOps/研发规范`

### [[语义化版本与CHANGELOG|语义化版本与 CHANGELOG]]
> 版本管理规范

- **四级子知识点**：
  - SemVer 规范
  - 版本号含义
  - CHANGELOG 编写
  - 自动化生成
  - 破坏性变更
  - 预发布版本
- **标签**：`#DevOps/研发规范`

### [[API设计规范-OpenAPI|API 设计规范 - OpenAPI]]
> API 设计标准

- **四级子知识点**：
  - RESTful 设计
  - OpenAPI 规范
  - 版本化策略
  - 错误处理
  - 分页与过滤
  - 文档生成
  - 契约测试
- **标签**：`#DevOps/研发规范`

---

## 🔗 学习依赖路径

```
Docker → K8s → CI/CD → 监控 → IaC（可与研发规范并行）
   ↓       ↓       ↓        ↓
 镜像    Pod     GitHub   Prometheus
   ↓       ↓       ↓        ↓
   └──── 生产环境运维 ────┘
```

| 阶段 | 知识点 | 预计耗时 | 前置条件 |
|------|--------|----------|----------|
| 容器 | Docker 全套 | 10h | Linux 基础 |
| 编排 | K8s 全套 | 24h | Docker |
| CI/CD | 流水线 + GitOps | 12h | K8s |
| 监控 | 可观测性全套 | 14h | K8s |
| IaC | Terraform + Ansible | 12h | K8s |
| 规范 | Git + API + 版本 | 8h | 无 |

---

## 🌐 跨板块关联

| 关联板块 | 关联点 | 连接笔记 |
|----------|--------|----------|
| [[01-Python全栈/MOC-Python全栈|Python全栈]] | 服务部署、容器化、健康检查 | [[Dockerfile最佳实践]] |
| [[02-Java全栈/MOC-Java全栈|Java全栈]] | JVM 容器化、K8s 资源调度、APM | [[K8s-资源限制与HPA]] |
| [[06-AI工程化/MOC-AI工程化|AI工程化]] | GPU 节点调度、模型服务弹性伸缩 | [[模型服务化-OpenAI兼容API]] |
| [[03-Vue3TS前端/MOC-Vue3TS|Vue3TS前端]] | 前端自动化构建与部署 | [[GitHub-Actions流水线设计]] |
| [[09-效率工具链/MOC-效率工具|效率工具]] | CI/CD 是自动化工作流的核心 | [[ArgoCD-GitOps持续部署]] |

---

## 🌱 持续扩充方向

- [ ] K8s 1.30+ 新特性
- [ ] Serverless 容器
- [ ] eBPF 可观测性
- [ ] 平台工程（Internal Developer Platform）
- [ ] FinOps 云成本优化
- [ ] 混沌工程
- [ ] 安全左移（DevSecOps）
- [ ] 多云与混合云管理

---

## 📊 板块统计

- 二级分类：6 个
- 三级知识点（原子笔记）：24 篇
- 四级子知识点：约 130 个
- 枢纽笔记：1 篇
- 跨板块关联：5 条

---

[[10-四级知识框架/00-总控/四级框架总索引|← 返回四级框架总索引]] | [[Home|🏠 返回首页]]
