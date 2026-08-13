---
title: DevOps工程化枢纽
tags: [枢纽, DevOps, hub]
created: 2026-08-13
updated: 2026-08-13
hub: true
hub_type: 技术枢纽
---

# ☁️ DevOps 工程化枢纽

> 从代码到生产的全链路工程化体系，连接容器化、Kubernetes、CI/CD、可观测性与基础设施即代码。
> **所属板块**：[[07-DevOps/MOC-DevOps-四级展开|DevOps]]
> **标签前缀**：`#DevOps/`

---

## 📌 枢纽定位

| 维度 | 说明 |
|------|------|
| 定位 | 研发运维一体化的知识汇聚点 |
| 覆盖范围 | 容器化 → K8s → CI/CD → 监控可观测 → IaC → 研发规范 |
| 上游依赖 | [[CS-基础原理枢纽|CS基础]]（Linux/网络） |
| 下游延伸 | 所有开发板块的部署运维、[[项目实战-枢纽|项目实战]] |
| 核心能力 | 构建自动化、可扩展、可观测的生产环境 |

---

## 🔑 核心知识节点

### 第一层：必须掌握

- [[Docker-核心原理与镜像优化|Docker 核心原理]] — 容器化基础
- [[K8s-核心概念与架构|K8s 核心概念]] — 容器编排标准
- [[GitHub-Actions流水线设计|GitHub Actions]] — CI/CD 标准
- [[Prometheus-指标采集|Prometheus]] — 云原生监控标准

### 第二层：深入理解

- [[Pod与控制器Deployment|Pod 与 Deployment]] — K8s 工作负载
- [[Service与Ingress|Service 与 Ingress]] — 服务暴露
- [[ArgoCD-GitOps持续部署|ArgoCD GitOps]] — 持续部署
- [[ELK-日志聚合|ELK 日志聚合]] — 日志收集分析

### 第三层：拓展延伸

- [[Helm-Chart包管理|Helm Chart]] — K8s 包管理
- [[Jaeger-分布式链路追踪|Jaeger 链路追踪]] — 微服务可观测
- [[Terraform-基础设施编排|Terraform]] — IaC 标准
- [[K8s-故障排查手册|K8s 故障排查]] — 运维必备

---

## 🕸️ 知识网络

```
容器化（Docker）
    │
    └── Kubernetes
          ├── 工作负载（Pod/Deployment/StatefulSet）
          ├── 服务发现（Service/Ingress）
          ├── 配置管理（ConfigMap/Secret）
          ├── 包管理（Helm）
          └── 弹性伸缩（HPA）

CI/CD
    ├── GitHub Actions / GitLab CI
    ├── ArgoCD（GitOps）
    └── 制品管理（Harbor/Nexus）

可观测性
    ├── 指标（Prometheus + Grafana）
    ├── 日志（ELK/Loki）
    └── 链路追踪（Jaeger/OpenTelemetry）

IaC + 研发规范
    ├── Terraform / Ansible
    ├── Git 工作流
    └── API 设计规范
```

---

## 🔗 上下游横向关联

### 入向依赖
- [[CS-基础原理枢纽|CS基础]] — Linux、网络
- [[效率工具-枢纽|效率工具]] — 终端、脚本

### 出向延伸
- 所有开发板块的部署运维
- [[AI-工程化技术枢纽|AI工程化]] — GPU 节点调度

---

## 🌐 跨板块枢纽连接

| 连接枢纽 | 关联点 | 关键笔记 |
|----------|--------|----------|
| [[Python-全栈技术枢纽|Python全栈]] | 服务容器化部署 | [[Dockerfile最佳实践]] |
| [[Java-全栈技术枢纽|Java全栈]] | JVM 容器化、APM | [[K8s-资源限制与HPA]] |
| [[AI-工程化技术枢纽|AI工程化]] | GPU 调度、模型服务弹性 | [[模型服务化-OpenAI兼容API]] |
| [[Vue3TS-前端技术枢纽|Vue3TS前端]] | 前端自动化构建部署 | [[GitHub-Actions流水线设计]] |

---

## 📝 维护日志

| 日期 | 变更 |
|------|------|
| 2026-08-13 | 初始创建 |

---

## ⚠️ 知识边界

- 具体语言的部署细节归入对应开发枢纽
- 云厂商特定服务（AWS/Azure/阿里云）暂不深入
- 安全（DevSecOps）作为拓展方向

---

[[10-四级知识框架/00-总控/四级框架总索引|← 返回四级框架总索引]] | [[07-DevOps/MOC-DevOps-四级展开|📂 返回板块MOC]] | [[Home|🏠 返回首页]]
