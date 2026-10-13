---
title: CI-CD流水线
tags: [CI/CD, DevOps, 自动化, 部署, 流水线]
category: 云原生与运维
created: 2026-08-31
updated: 2026-09-01
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[[CI-CD流水线设计]]", "[[Git版本控制核心命令]]"]
aliases: [持续集成持续部署, CICD, 自动化部署, CI-CD流水线设计]
---

# CI/CD 流水线

> 从代码提交到生产部署的完整自动化流水线：持续集成、持续交付、持续部署的原理、工具链和最佳实践。

## 概述

CI/CD（Continuous Integration / Continuous Delivery/Deployment）是现代软件开发的核心实践，通过自动化流水线将代码从提交到部署的全过程自动化，提高交付效率和质量。

**CI/CD 的三个阶段**：
```text
CI（持续集成）→ CD（持续交付）→ CD（持续部署）
  代码提交 → 构建 → 测试 → 打包 → 预发布环境 → 生产环境（自动/手动）
```

- **持续集成（CI）**：频繁将代码合并到主干，自动构建和测试，尽早发现问题
- **持续交付（CD）**：CI 的产物自动部署到预发布环境，随时可手动发布到生产
- **持续部署（CD）**：持续交付的进阶，通过自动化测试后自动部署到生产环境

**CI/CD 的核心价值**：
- 提高交付频率（从月/周到天/小时）
- 降低发布风险（小步快跑，自动化验证）
- 提高代码质量（自动化测试、代码检查）
- 减少人工操作（自动化构建、部署、回滚）
- 快速反馈（提交后立即知道是否有问题）

## 原理

### CI/CD 流水线的完整流程

```bash
开发者提交代码
  ↓
Git 触发 Webhook
  ↓
CI 服务器拉取代码
  ↓
依赖安装（npm install / mvn install / pip install）
  ↓
代码检查（ESLint / SonarQube / Checkstyle）
  ↓
单元测试（Jest / Vitest / JUnit / pytest）
  ↓
构建打包（Vite build / Maven package / Docker build）
  ↓
产物上传（Nexus / 镜像仓库 / 对象存储）
  ↓
集成测试（Testcontainers / 自动化E2E）
  ↓
部署到测试环境（kubectl apply / Helm upgrade）
  ↓
自动化验收测试（Cypress / Playwright）
  ↓
人工审批（可选，持续交付阶段）
  ↓
部署到生产环境（蓝绿/金丝雀/滚动更新）
  ↓
健康检查 + 监控告警
  ↓
异常自动回滚
```

### 核心概念

#### 1. 流水线即代码（Pipeline as Code）
- 用代码定义流水线（Jenkinsfile、.gitlab-ci.yml、GitHub Actions workflow）
- 版本控制、可审查、可复用
- 优势：变更可追溯、环境一致性、团队协作

#### 2. 构建环境隔离
- 每个构建在干净的环境中运行（Docker 容器）
- 避免"在我机器上能跑"的问题
- 实现：Docker、Kubernetes Pod、VM

#### 3. 制品管理（Artifact Management）
- 构建产物唯一标识、不可变
- 版本追溯：哪个提交构建的、谁构建的、什么时候
- 工具：Nexus、JFrog、Docker Registry、对象存储

#### 4. 部署策略

| 策略 | 原理 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|---------|
| 滚动更新 | 逐步替换旧实例 | 简单、无需额外资源 | 发布期间新旧共存 | 大多数场景 |
| 蓝绿部署 | 两套环境，切换流量 | 零停机、快速回滚 | 需要双倍资源 | 关键业务 |
| 金丝雀发布 | 小流量验证，逐步扩大 | 风险可控、影响小 | 复杂、需要流量治理 | 大规模生产 |
| 功能开关 | 代码中控制功能开关 | 灵活、可随时关闭 | 代码复杂度增加 | A/B测试、灰度 |

#### 5. 回滚机制
- 自动回滚：健康检查失败、错误率超阈值时自动回滚
- 手动回滚：一键回滚到上一个稳定版本
- 实现：Kubernetes rollout undo、Helm rollback、蓝绿切换

## 实操

### 1. GitHub Actions 流水线（前端项目）

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: registry.cn-hangzhou.aliyuncs.com
  IMAGE_NAME: my-org/my-app

jobs:
  # 阶段1：代码检查与测试
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type Check
        run: npm run type-check

      - name: Unit Test
        run: npm run test:coverage

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/

  # 阶段2：构建与镜像
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Build
        run: |
          npm ci
          npm run build

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}

      - name: Build and Push Docker Image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

  # 阶段3：部署到生产
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - name: Deploy to Kubernetes
        uses: steebchen/kubectl@v2
        with:
          config: ${{ secrets.KUBE_CONFIG }}
          version: v1.28.0
          command: set image deployment/my-app my-app=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/my-app --timeout=120s
```

### 2. GitLab CI 流水线（后端 Java 项目）

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=.m2/repository"
  DOCKER_REGISTRY: "registry.example.com"
  IMAGE_NAME: "my-org/order-service"

# 缓存 Maven 依赖
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .m2/repository/
    - target/

test:
  stage: test
  image: maven:3.9-eclipse-temurin-17
  script:
    - mvn clean verify
    - mvn sonar:sonar -Dsonar.host.url=$SONAR_URL -Dsonar.login=$SONAR_TOKEN
  artifacts:
    reports:
      junit: target/surefire-reports/TEST-*.xml
    paths:
      - target/site/jacoco/
  only:
    - merge_requests
    - main
    - develop

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker login -u $REGISTRY_USER -p $REGISTRY_PASSWORD $DOCKER_REGISTRY
    - docker build -t $DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHORT_SHA .
    - docker push $DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHORT_SHA
  only:
    - main

deploy_staging:
  stage: deploy
  image: bitnami/kubectl:1.28
  script:
    - kubectl set image deployment/order-service order-service=$DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHORT_SHA -n staging
    - kubectl rollout status deployment/order-service -n staging --timeout=120s
  environment:
    name: staging
  only:
    - main

deploy_production:
  stage: deploy
  image: bitnami/kubectl:1.28
  script:
    - kubectl set image deployment/order-service order-service=$DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHORT_SHA -n production
    - kubectl rollout status deployment/order-service -n production --timeout=120s
  environment:
    name: production
  when: manual  # 生产环境需要手动审批
  only:
    - main
```

### 3. Docker 多阶段构建（优化镜像体积）

```dockerfile
# 构建阶段
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段（Nginx）
FROM nginx:1.25-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 4. Kubernetes 健康检查与滚动更新

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # 最多多1个实例
      maxUnavailable: 0  # 不允许不可用
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
        - name: order-service
          image: registry.example.com/my-org/order-service:latest
          ports:
            - containerPort: 8080
          readinessProbe:      # 就绪探针
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          livenessProbe:       # 存活探针
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 60
            periodSeconds: 30
          resources:
            requests:
              cpu: 500m
              memory: 512Mi
            limits:
              cpu: 2000m
              memory: 2Gi
```

## 问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| CI构建慢 | 依赖未缓存 / 构建步骤串行 / 大镜像 | 配置依赖缓存(npm/maven) / 并行Job / 多阶段构建 / 优化Dockerfile |
| 测试不稳定（Flaky） | 测试依赖外部服务 / 时序问题 / 数据未清理 | 用Testcontainers / Mock外部依赖 / 测试隔离 / 重试机制 |
| 部署后服务不可用 | 健康检查配置错误 / 配置缺失 / 迁移失败 | 完善readiness/liveness探针 / 配置中心检查 / 数据库迁移先执行 |
| 回滚失败 | 旧版本镜像被删除 / 数据库不兼容 | 保留历史镜像 / 数据库变更向前兼容 / 蓝绿部署快速切换 |
| 环境不一致 | 本地/测试/生产配置不同 | Docker统一环境 / 配置中心管理 / Infrastructure as Code |
| 密钥泄露 | 密钥硬编码在代码/配置中 | 用Secrets管理 / 环境变量注入 / 代码扫描（gitleaks） |
| 镜像体积大 | 基础镜像过大 / 包含构建依赖 | 多阶段构建 / Alpine基础镜像 / 清理缓存 / .dockerignore |
| 流水线触发不生效 | Webhook配置错误 / 分支过滤 / 权限问题 | 检查Webhook / 检查on配置 / 检查CI服务器权限 |
| 并发构建冲突 | 多个构建同时操作同一资源 | 构建队列 / 资源锁 / 独立构建环境 |
| 生产部署风险高 | 直接全量发布 / 无验证 | 金丝雀发布 / 蓝绿部署 / 自动化验收测试 / 人工审批 |

## 拓展

**深入学习方向**：
1. **GitOps**：ArgoCD、Flux，用 Git 仓库作为基础设施的唯一真实来源
2. **基础设施即代码（IaC）**：Terraform、Pulumi，用代码管理云资源
3. **配置管理**：Ansible、Chef、Puppet，自动化服务器配置
4. **容器编排**：Kubernetes 深入学习，Helm、Kustomize
5. **服务网格**：Istio、Linkerd，流量管理、安全、可观测性
6. **混沌工程**：Chaos Mesh、Litmus，主动注入故障验证系统韧性
7. **可观测性**：OpenTelemetry、Prometheus、Grafana、Loki 全链路监控
8. **DevSecOps**：将安全融入 CI/CD 流水线（SAST、DAST、依赖扫描）

**相关笔记**：
- [[CI-CD流水线设计]]
- [[Git版本控制核心命令]]
- [[Git分支管理与工作流]]
- [[Kubernetes入门与实践]]
- [[Linux基础命令]]
- [[Prometheus监控与告警]]

**推荐工具链**：
- **CI/CD平台**：GitHub Actions、GitLab CI、Jenkins、CircleCI、Tekton
- **代码质量**：SonarQube、ESLint、Checkstyle、CodeQL
- **制品管理**：Nexus、JFrog、Harbor、Docker Registry
- **部署**：ArgoCD、Flux、Helm、Kustomize
- **监控**：Prometheus、Grafana、Alertmanager
- **日志**：ELK、Loki、Fluentd

**面试高频考点**：
1. CI/CD 的完整流程和每个阶段的作用
2. 持续交付和持续部署的区别
3. 蓝绿部署、金丝雀发布、滚动更新的区别和适用场景
4. 如何保证 CI/CD 的安全性（密钥管理、镜像扫描）
5. Docker 多阶段构建的原理和优势
6. Kubernetes 滚动更新的机制
7. 如何优化 CI 构建速度
8. 回滚机制的设计

---

[[MOC-云原生与运维|← 返回板块 MOC]] | [[知识库仪表盘|📊 仪表盘]] | [[Home|🏠 返回首页]]

---

## 💡 全文深度讲解

本文系统梳理了CI-CD流水线的核心知识体系，从概述入手，深入原理的底层机制，再通过实操掌握实战应用，最后涵盖问题与拓展。学习时建议先建立整体认知，再动手实践，最后结合常见问题深化理解。

## 📝 全文精简总结

- **概述**：掌握本模块的核心概念与关键要点
- **原理**：掌握本模块的核心概念与关键要点
- **实操**：掌握本模块的核心概念与关键要点
- **问题**：掌握本模块的核心概念与关键要点
- **拓展**：掌握本模块的核心概念与关键要点

