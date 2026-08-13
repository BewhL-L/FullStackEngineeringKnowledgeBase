---
title: 云原生与运维 MOC
tags: [MOC, 云原生, Kubernetes, ServiceMesh, 运维]
created: 2026-08-12
---

# ☁️ 云原生与运维 MOC

> 容器编排 Kubernetes 与服务网格 Service Mesh，现代云原生应用的基础设施。

---

## 📚 核心文档

### 容器技术
- [[05-云原生与运维/Docker 知识点系统梳理_优化版|Docker 知识点系统梳理]] — 容器原理、镜像、Dockerfile、数据卷、网络、Compose、多阶段构建

### 容器编排
- [[05-云原生与运维/Kubernetes 知识点系统梳理_优化版|Kubernetes 知识点系统梳理]] — Pod、Service、Deployment、ConfigMap、Ingress、调度策略、网络模型

### 服务网格
- [[05-云原生与运维/Service Mesh 知识点系统梳理_优化版|Service Mesh 知识点系统梳理]] — Istio 架构、流量管理、可观测性、安全通信、Sidecar 模式

### Web 服务器与反向代理
- [[05-云原生与运维/Nginx 知识点系统梳理_优化版|Nginx 知识点系统梳理]] — 反向代理、负载均衡、静态资源、HTTPS、限流、性能优化

### Linux 运维
- [[05-云原生与运维/Linux 常用命令知识点系统梳理_优化版|Linux 常用命令知识点系统梳理]] — 文件操作、文本三剑客、进程管理、网络、权限、系统监控

---

## 🔗 知识关联

```
微服务应用（Spring Cloud）
   ↓ 部署与编排
Kubernetes（容器编排）
   ↓ 服务治理
Service Mesh（服务网格）
```

- [[05-云原生与运维/Kubernetes 知识点系统梳理_优化版|Kubernetes]] 是容器编排事实标准，负责应用的部署、扩缩容、服务发现
- [[05-云原生与运维/Service Mesh 知识点系统梳理_优化版|Service Mesh]] 在 K8s 之上提供流量管理、可观测性、安全通信，将服务治理从应用代码中剥离
- 微服务 [[02-后端开发/Spring Cloud微服务 知识点系统梳理_优化版|Spring Cloud]] 应用通常部署在 K8s 上，可结合 Service Mesh 做更精细的流量控制
- 与 [[04-分布式与中间件/MOC-分布式与中间件|分布式中间件]] 共同构成分布式系统的基础设施层

---

## 📖 学习顺序

1. **Linux 基础**：[[05-云原生与运维/Linux 常用命令知识点系统梳理_优化版|Linux 常用命令]] — 命令行、进程、网络、权限
2. **Docker 容器**：[[05-云原生与运维/Docker 知识点系统梳理_优化版|Docker]] — 镜像、容器、Dockerfile、Compose
3. **Nginx**：[[05-云原生与运维/Nginx 知识点系统梳理_优化版|Nginx]] — 反向代理、负载均衡、HTTPS
4. **Kubernetes**：[[05-云原生与运维/Kubernetes 知识点系统梳理_优化版|Kubernetes]] — 核心资源对象、网络、存储
5. **Service Mesh**：[[05-云原生与运维/Service Mesh 知识点系统梳理_优化版|Service Mesh]] — Istio 架构与功能
6. **云原生进阶**：结合微服务理解云原生应用的完整部署与治理体系

---

## 🏷️ 相关标签

`#云原生` `#Docker` `#Kubernetes` `#K8s` `#ServiceMesh` `#Istio` `#Nginx` `#Linux` `#容器` `#运维`

---

[[Home|🏠 返回首页]]
