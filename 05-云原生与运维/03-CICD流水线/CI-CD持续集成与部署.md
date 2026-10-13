---
title: CI-CD持续集成与部署
tags: [CICD, CI, DevOps, Jenkins, GitLabCI, GitHubActions, ArgoCD, 流水线]
category: 云原生
created: 2026-08-29
updated: 2026-08-29
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[Git 版本控制知识点系统梳理_优化版]]"]
aliases: [CI/CD持续集成与部署]
---

# 🔄 CI/CD 持续集成与部署

> CI/CD（持续集成/持续部署）是 DevOps 的核心实践，通过自动化流水线将代码从提交到生产部署的全过程自动化，实现快速、可靠、高频的软件交付，是现代软件开发的必备能力。

---

## 一、CI/CD 概述

### 什么是 CI/CD
- **CI（Continuous Integration，持续集成）**：开发者频繁将代码合并到主干，每次合并都通过自动化构建和测试验证
- **CD（Continuous Delivery，持续交付）**：代码通过自动化测试后，自动部署到预发布环境，可随时一键发布到生产
- **CD（Continuous Deployment，持续部署）**：代码通过所有自动化测试后，自动部署到生产环境，无需人工干预

### CI/CD 的价值
| 价值 | 说明 |
|------|------|
| **快速交付** | 自动化流水线将部署时间从小时级降到分钟级 |
| **降低风险** | 频繁小批量发布，每次变更影响小，问题易定位 |
| **提高质量** | 自动化测试和代码检查在每次提交时运行，早期发现问题 |
| **减少人工** | 自动化构建、测试、部署，减少人工操作和人为错误 |
| **可追溯** | 每次部署都有完整记录，可追溯代码版本、构建过程、部署时间 |
| **快速回滚** | 自动化部署支持快速回滚，降低故障影响时间 |

### CI/CD 流水线阶段
```text
代码提交 → 代码检查 → 构建 → 单元测试 → 集成测试 → 制品打包 → 部署测试环境 → 验收测试 → 部署预发布 → 人工审批 → 部署生产 → 监控告警
```

**典型阶段说明**
| 阶段 | 说明 | 常用工具 |
|------|------|---------|
| 代码提交 | 开发者提交代码到版本控制系统 | Git、GitHub、GitLab |
| 代码检查 | 静态代码分析、代码规范、安全扫描 | ESLint、SonarQube、Trivy |
| 构建 | 编译代码、打包应用、构建镜像 | Maven、Gradle、npm、Docker |
| 单元测试 | 运行单元测试，生成覆盖率报告 | JUnit、Pytest、Jest、Vitest |
| 集成测试 | 运行集成测试，验证模块间交互 | TestContainers、Postman、Newman |
| 制品打包 | 打包应用制品，推送到制品仓库 | Nexus、Harbor、Docker Registry |
| 部署测试环境 | 部署到测试环境，运行自动化测试 | Ansible、Terraform、kubectl |
| 验收测试 | 运行端到端测试、性能测试、安全测试 | Selenium、Cypress、JMeter |
| 部署预发布 | 部署到预发布环境，进行最终验证 | ArgoCD、Flux、Spinnaker |
| 人工审批 | 关键部署需要人工审批（持续交付） | 人工确认 |
| 部署生产 | 部署到生产环境，灰度发布 | ArgoCD、Flux、Spinnaker |
| 监控告警 | 监控部署后系统状态，异常告警 | Prometheus、Grafana、Alertmanager |

---

## 二、CI/CD 工具对比

### 主流 CI/CD 工具
| 工具 | 类型 | 特点 | 适用场景 |
|------|------|------|---------|
| **Jenkins** | 自托管 | 功能强大、插件丰富、高度可定制、社区活跃 | 企业级、复杂流水线、自托管 |
| **GitLab CI/CD** | 集成式 | 与 GitLab 深度集成、YAML 配置、Docker 原生 | GitLab 用户、一体化 DevOps |
| **GitHub Actions** | 云服务 | 与 GitHub 深度集成、Marketplace 丰富、免费额度 | GitHub 用户、开源项目 |
| **ArgoCD** | GitOps | 声明式、GitOps、Kubernetes 原生、自动化同步 | K8s 环境、GitOps 持续部署 |
| **Flux** | GitOps | 轻量级、GitOps、Kubernetes 原生、CNCF 毕业 | K8s 环境、轻量级 GitOps |
| **Spinnaker** | 多云部署 | 多云部署、灰度发布、回滚、流水线编排 | 多云环境、复杂部署策略 |
| **CircleCI** | 云服务 | 快速、易用、Docker 原生、免费额度 | 中小团队、云原生 |
| **Travis CI** | 云服务 | 简单易用、GitHub 集成、免费额度 | 开源项目、简单流水线 |
| **TeamCity** | 自托管 | JetBrains 出品、智能构建、用户体验好 | JetBrains 生态、企业级 |
| **Bamboo** | 自托管 | Atlassian 出品、与 Jira/Bitbucket 集成 | Atlassian 生态、企业级 |

### 工具选型建议
- **小团队/开源项目**：GitHub Actions（免费额度、易用）
- **GitLab 用户**：GitLab CI/CD（一体化、深度集成）
- **企业级复杂流水线**：Jenkins（插件丰富、高度可定制）
- **Kubernetes 环境**：ArgoCD + Jenkins/GitLab CI（CI 用 Jenkins，CD 用 ArgoCD）
- **多云部署**：Spinnaker（多云支持、灰度发布）

---

## 三、Jenkins 流水线实战

### Jenkins 安装
**Docker Compose 部署**
```yaml
version: '3.8'
services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins-data:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - JAVA_OPTS=-Djenkins.install.runSetupWizard=false
    restart: unless-stopped

volumes:
  jenkins-data:
```

### Jenkinsfile（声明式流水线）
```groovy
pipeline {
    agent any

    environment {
        APP_NAME = 'myapp'
        APP_VERSION = "${env.BUILD_NUMBER}"
        DOCKER_REGISTRY = 'registry.example.com'
        IMAGE_NAME = "${DOCKER_REGISTRY}/${APP_NAME}:${APP_VERSION}"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('代码检查') {
            steps {
                echo 'Running code quality checks...'
                sh 'npm run lint'
                sh 'npm run format:check'
            }
        }

        stage('构建') {
            steps {
                echo 'Building application...'
                sh 'npm ci'
                sh 'npm run build'
            }
        }

        stage('单元测试') {
            steps {
                echo 'Running unit tests...'
                sh 'npm run test:unit'
            }
            post {
                always {
                    junit 'test-results/**/*.xml'
                    publishHTML(target: [
                        reportDir: 'coverage',
                        reportFiles: 'index.html',
                        reportName: 'Code Coverage'
                    ])
                }
            }
        }

        stage('构建镜像') {
            steps {
                echo 'Building Docker image...'
                sh "docker build -t ${IMAGE_NAME} ."
                sh "docker push ${IMAGE_NAME}"
            }
        }

        stage('部署测试环境') {
            steps {
                echo 'Deploying to test environment...'
                sh "kubectl set image deployment/${APP_NAME} ${APP_NAME}=${IMAGE_NAME} -n test"
                sh "kubectl rollout status deployment/${APP_NAME} -n test --timeout=120s"
            }
        }

        stage('集成测试') {
            steps {
                echo 'Running integration tests...'
                sh 'npm run test:integration'
            }
        }

        stage('部署预发布') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to staging environment...'
                sh "kubectl set image deployment/${APP_NAME} ${APP_NAME}=${IMAGE_NAME} -n staging"
                sh "kubectl rollout status deployment/${APP_NAME} -n staging --timeout=120s"
            }
        }

        stage('人工审批') {
            when {
                branch 'main'
            }
            steps {
                input message: '是否部署到生产环境？', ok: '部署'
            }
        }

        stage('部署生产') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production environment...'
                sh "kubectl set image deployment/${APP_NAME} ${APP_NAME}=${IMAGE_NAME} -n production"
                sh "kubectl rollout status deployment/${APP_NAME} -n production --timeout=300s"
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
            emailext (
                subject: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: "Pipeline completed successfully.\nBuild: ${env.BUILD_URL}",
                to: 'devops@example.com'
            )
        }
        failure {
            echo 'Pipeline failed!'
            emailext (
                subject: "FAILURE: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: "Pipeline failed.\nBuild: ${env.BUILD_URL}",
                to: 'devops@example.com'
            )
        }
        always {
            echo 'Cleaning up...'
            sh 'docker system prune -f'
        }
    }
}
```

### Jenkins 常用插件
| 插件 | 说明 |
|------|------|
| **Pipeline** | 流水线支持，定义 Jenkinsfile |
| **Git** | Git 版本控制集成 |
| **Docker** | Docker 构建和推送 |
| **Kubernetes** | K8s 动态 Agent、部署 |
| **SonarQube Scanner** | 代码质量扫描 |
| **JUnit** | 测试报告展示 |
| **HTML Publisher** | HTML 报告展示（覆盖率等） |
| **Email Extension** | 邮件通知扩展 |
| **Slack Notification** | Slack 通知 |
| **Credentials Binding** | 凭据管理 |
| **Config File Provider** | 配置文件管理 |
| **Build Timeout** | 构建超时控制 |
| **Timestamper** | 控制台时间戳 |
| **AnsiColor** | 控制台颜色输出 |

---

## 四、GitLab CI/CD 实战

```text
### .gitlab-ci.yml
```
```yaml
# 全局变量
variables:
  APP_NAME: "myapp"
  DOCKER_REGISTRY: "registry.example.com"
  IMAGE_NAME: "$DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHORT_SHA"

# 流水线阶段
stages:
  - lint
  - build
  - test
  - package
  - deploy-test
  - deploy-staging
  - deploy-production

# 缓存配置
cache:
  key: "$CI_COMMIT_REF_SLUG"
  paths:
    - node_modules/
    - .npm/

# 代码检查
lint:
  stage: lint
  image: node:18-alpine
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run lint
    - npm run format:check
  only:
    - merge_requests
    - main
    - develop

# 构建
build:
  stage: build
  image: node:18-alpine
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  only:
    - merge_requests
    - main
    - develop

# 单元测试
unit-test:
  stage: test
  image: node:18-alpine
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run test:unit
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  artifacts:
    reports:
      junit: test-results/junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
  only:
    - merge_requests
    - main
    - develop

# 构建镜像
package:
  stage: package
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $DOCKER_REGISTRY
    - docker build -t $IMAGE_NAME .
    - docker push $IMAGE_NAME
  only:
    - main
    - develop

# 部署测试环境
deploy-test:
  stage: deploy-test
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/$APP_NAME $APP_NAME=$IMAGE_NAME -n test
    - kubectl rollout status deployment/$APP_NAME -n test --timeout=120s
  environment:
    name: test
    url: https://test.example.com
  only:
    - develop

# 部署预发布
deploy-staging:
  stage: deploy-staging
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/$APP_NAME $APP_NAME=$IMAGE_NAME -n staging
    - kubectl rollout status deployment/$APP_NAME -n staging --timeout=120s
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main

# 部署生产（手动触发）
deploy-production:
  stage: deploy-production
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/$APP_NAME $APP_NAME=$IMAGE_NAME -n production
    - kubectl rollout status deployment/$APP_NAME -n production --timeout=300s
  environment:
    name: production
    url: https://www.example.com
  when: manual
  only:
    - main
```

### GitLab CI/CD 核心概念
| 概念 | 说明 |
|------|------|
| **Pipeline** | 流水线，由多个 Stage 组成 |
| **Stage** | 阶段，包含多个 Job，按顺序执行 |
| **Job** | 任务，具体执行的操作，可并行执行 |
| **Runner** | 执行器，运行 Job 的机器或容器 |
| **Artifacts** | 制品，Job 产出的文件，可在后续 Job 使用 |
| **Cache** | 缓存，加速构建，如 node_modules |
| **Environment** | 环境，部署目标，如 test/staging/production |
| **Variables** | 变量，全局或 Job 级别的环境变量 |
| **Only/Except** | 触发条件，控制 Job 在哪些分支触发 |
| **When** | 执行时机，如 manual（手动）、on_success、on_failure |

---

## 五、GitHub Actions 实战

### .github/workflows/ci.yml
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  APP_NAME: myapp
  DOCKER_REGISTRY: registry.example.com
  IMAGE_NAME: ${{ env.DOCKER_REGISTRY }}/${{ env.APP_NAME }}:${{ github.sha }}

jobs:
  # 代码检查
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run lint
        run: npm run lint

      - name: Check format
        run: npm run format:check

  # 构建和测试
  build-test:
    name: Build & Test
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Run unit tests
        run: npm run test:unit

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  # 构建并推送镜像
  docker-build:
    name: Docker Build & Push
    runs-on: ubuntu-latest
    needs: build-test
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.DOCKER_REGISTRY }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ env.IMAGE_NAME }}
          cache-from: type=registry,ref=${{ env.IMAGE_NAME }}
          cache-to: type=inline

  # 部署测试环境
  deploy-test:
    name: Deploy to Test
    runs-on: ubuntu-latest
    needs: docker-build
    if: github.ref == 'refs/heads/develop'
    environment: test
    steps:
      - uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'

      - name: Configure kubeconfig
        run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBE_CONFIG }}" > $HOME/.kube/config
          chmod 600 $HOME/.kube/config

      - name: Deploy
        run: |
          kubectl set image deployment/${{ env.APP_NAME }} ${{ env.APP_NAME }}=${{ env.IMAGE_NAME }} -n test
          kubectl rollout status deployment/${{ env.APP_NAME }} -n test --timeout=120s

  # 部署生产环境（手动审批）
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: docker-build
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'

      - name: Configure kubeconfig
        run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBE_CONFIG }}" > $HOME/.kube/config
          chmod 600 $HOME/.kube/config

      - name: Deploy
        run: |
          kubectl set image deployment/${{ env.APP_NAME }} ${{ env.APP_NAME }}=${{ env.IMAGE_NAME }} -n production
          kubectl rollout status deployment/${{ env.APP_NAME }} -n production --timeout=300s
```

### GitHub Actions 核心概念
| 概念 | 说明 |
|------|------|
| **Workflow** | 工作流，定义在 .github/workflows/ 目录下的 YAML 文件 |
| **Event** | 触发事件，如 push、pull_request、schedule |
| **Job** | 任务，在 Runner 上执行，可并行或串行 |
| **Step** | 步骤，Job 中的具体操作，可使用 Action 或运行命令 |
| **Action** | 动作，可复用的步骤，从 Marketplace 获取 |
| **Runner** | 运行器，执行 Job 的机器（GitHub 托管或自托管） |
| **Secrets** | 密钥，加密存储的敏感信息（密码、Token 等） |
| **Environment** | 环境，部署目标，支持保护规则和审批 |
| **Artifacts** | 制品，Workflow 产出的文件，可下载 |
| **Cache** | 缓存，加速构建，如依赖缓存 |

---

## 六、ArgoCD GitOps 持续部署

### 什么是 GitOps
GitOps 是一种持续部署方式，以 Git 仓库作为应用部署的唯一事实来源，通过 Git 提交触发自动化部署，实现声明式、可追溯、可回滚的部署流程。

### ArgoCD 核心概念
| 概念 | 说明 |
|------|------|
| **Application** | 应用，定义了 Git 仓库和目标集群的映射关系 |
| **Project** | 项目，对 Application 进行分组和权限控制 |
| **Sync** | 同步，将 Git 仓库中的配置同步到目标集群 |
| **Sync Policy** | 同步策略，如自动同步、自动修复、修剪 |
| **Health Check** | 健康检查，检查应用部署后的健康状态 |
| **Rollback** | 回滚，将应用回滚到之前的版本 |

### ArgoCD Application 定义
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/myapp-deploy.git
    targetRevision: main
    path: overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 3
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### ArgoCD 部署流程
```text
开发者提交代码 → CI 构建镜像 → 更新 Git 仓库中的部署配置 → ArgoCD 检测到 Git 变更 → 自动同步到 K8s 集群 → 健康检查 → 部署完成
```

### ArgoCD 最佳实践
- ✅ 使用 Kustomize 或 Helm 管理多环境配置
- ✅ 配置自动同步和自动修复（self-heal）
- ✅ 使用 ApplicationSet 管理多环境、多集群应用
- ✅ 配置健康检查，确保应用部署成功
- ✅ 使用 Projects 进行权限控制和资源限制
- ✅ 配置通知（Slack、邮件、Webhook）
- ✅ 定期备份 ArgoCD 配置
- ❌ 不要在 Git 仓库中存储敏感信息（使用 Sealed Secrets 或 External Secrets）
- ❌ 不要手动修改集群中的配置（会被 ArgoCD 自动修复）

---

## 七、CI/CD 最佳实践

### 1. 流水线设计
- ✅ 快速反馈：代码提交后 5-10 分钟内完成构建和测试
- ✅ 并行执行：独立的 Job 并行执行，缩短流水线时间
- ✅ 阶段清晰：按逻辑划分阶段（lint → build → test → deploy）
- ✅ 失败快速：失败的 Job 快速失败，不等待后续阶段
- ✅ 可重复：相同代码多次构建结果一致
- ❌ 不要在流水线中执行需要人工交互的操作
- ❌ 不要将所有操作放在一个 Job 中

### 2. 版本管理
- ✅ 使用语义化版本（SemVer）：MAJOR.MINOR.PATCH
- ✅ 镜像标签使用 Git Commit SHA 或版本号，不使用 latest
- ✅ 制品仓库保留历史版本，支持快速回滚
- ✅ 使用 Git Tag 标记发布版本
- ❌ 不要在生产环境使用 latest 标签
- ❌ 不要覆盖已发布的版本

### 3. 安全实践
- ✅ 使用凭据管理工具（Vault、Secrets Manager）
- ✅ CI/CD 系统中的密钥使用加密存储
- ✅ 构建过程中扫描镜像漏洞（Trivy、Clair）
- ✅ 代码安全扫描（SonarQube、Snyk、Dependabot）
- ✅ 最小权限原则：CI/CD 服务账号只授予必要权限
- ✅ 生产部署需要人工审批（持续交付）
- ❌ 不要在代码中硬编码密码、密钥
- ❌ 不要在日志中输出敏感信息

### 4. 测试策略
- ✅ 测试金字塔：大量单元测试 + 适量集成测试 + 少量端到端测试
- ✅ 单元测试在每次提交时运行
- ✅ 集成测试在合并到主干前运行
- ✅ 端到端测试在预发布环境运行
- ✅ 性能测试定期运行（如每周）
- ✅ 测试覆盖率作为质量门禁
- ❌ 不要只依赖手动测试
- ❌ 不要跳过测试以加快部署

### 5. 部署策略
| 策略 | 说明 | 适用场景 |
|------|------|---------|
| **滚动更新** | 逐步替换旧版本实例 | 大多数场景，零停机 |
| **蓝绿部署** | 同时运行两个环境，切换流量 | 关键应用，快速回滚 |
| **金丝雀发布** | 逐步增加新版本流量比例 | 高风险变更，灰度验证 |
| **功能开关** | 通过开关控制功能上线 | 未完成功能、A/B 测试 |
| **回滚** | 快速回滚到上一个版本 | 故障恢复 |

### 6. 监控和反馈
- ✅ 部署后自动运行健康检查
- ✅ 监控关键指标（错误率、延迟、吞吐量）
- ✅ 异常自动告警
- ✅ 部署失败自动回滚
- ✅ 收集部署频率、变更失败率、平均恢复时间等 DORA 指标
- ✅ 定期回顾和优化流水线

---

## 八、常见问题与排查

### 1. 流水线失败
**排查步骤**
```bash
# 1. 查看流水线日志
# Jenkins: 构建页面 → Console Output
# GitLab CI: Pipeline → Job → Logs
# GitHub Actions: Actions → Workflow run → Job → Logs

# 2. 定位失败阶段和命令
# 查看哪个 Stage/Job/Step 失败

# 3. 查看错误信息
# 查看具体的错误堆栈和错误信息

# 4. 本地复现
# 在本地环境执行失败的命令，复现问题

# 5. 检查环境差异
# 检查 CI 环境和本地环境的差异（版本、配置、依赖）
```

**常见原因**
| 原因 | 解决方案 |
|------|---------|
| 依赖安装失败 | 检查网络、镜像源、依赖版本、锁文件 |
| 测试失败 | 查看测试报告，修复失败的测试 |
| 代码检查失败 | 修复代码规范问题或调整规则 |
| 构建失败 | 检查编译错误、依赖缺失、配置错误 |
| 镜像构建失败 | 检查 Dockerfile、基础镜像、构建上下文 |
| 部署失败 | 检查集群状态、资源限制、配置错误、权限问题 |
| 凭据错误 | 检查密钥配置、权限、过期时间 |
| 资源不足 | 增加 Runner 资源或优化构建 |

### 2. 构建速度慢
**优化策略**
| 策略 | 说明 | 效果 |
|------|------|------|
| 依赖缓存 | 缓存 node_modules、.m2、.gradle 等 | 减少 50-80% 依赖安装时间 |
| 并行构建 | 独立模块并行构建 | 减少 30-50% 构建时间 |
| 分层缓存 | Docker 多阶段构建、层缓存 | 减少镜像构建时间 |
| 增量构建 | 只构建变更的模块 | 减少构建时间 |
| 优化测试 | 并行测试、只运行相关测试 | 减少测试时间 |
| 更大 Runner | 使用更高配置的 Runner | 减少计算时间 |
| 制品复用 | 复用之前构建的制品 | 避免重复构建 |

### 3. 部署失败
**排查步骤**
```bash
# 1. 查看部署日志
kubectl describe deployment <name> -n <namespace>
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# 2. 查看 Pod 状态
kubectl get pods -n <namespace>
kubectl describe pod <pod-name> -n <namespace>

# 3. 查看容器日志
kubectl logs <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --previous  # 查看上一个容器的日志

# 4. 检查资源
kubectl top nodes
kubectl top pods -n <namespace>

# 5. 检查配置
kubectl get configmap -n <namespace>
kubectl get secret -n <namespace>
```

**常见原因**
| 原因 | 解决方案 |
|------|---------|
| 镜像拉取失败 | 检查镜像地址、标签、仓库权限、网络 |
| 资源不足 | 增加资源限制或调整 Request/Limit |
| 配置错误 | 检查 ConfigMap、Secret、环境变量 |
| 健康检查失败 | 检查健康检查配置、应用启动时间 |
| 权限不足 | 检查 ServiceAccount、RBAC 权限 |
| 端口冲突 | 检查端口配置、Service 配置 |
| 依赖服务不可用 | 检查数据库、缓存、消息队列等依赖 |
| 应用启动失败 | 查看应用日志，修复启动错误 |

### 4. 回滚
**快速回滚方法**
```bash
# Kubernetes 回滚
kubectl rollout undo deployment/<name> -n <namespace>
kubectl rollout undo deployment/<name> --to-revision=<revision> -n <namespace>

# 查看回滚历史
kubectl rollout history deployment/<name> -n <namespace>

# ArgoCD 回滚
argocd app rollback <app-name> <revision>

# 镜像回滚
kubectl set image deployment/<name> <container>=<old-image> -n <namespace>
```

---

## 🔗 关联笔记

**CI/CD 工具**
- [[Jenkins流水线实战]] — Jenkins 流水线实战
- [[GitLab-CI配置]] — GitLab CI 配置
- [[GitHub-Actions流水线设计]] — GitHub Actions 流水线设计
- [[ArgoCD-GitOps持续部署]] — ArgoCD GitOps 持续部署

**DevOps 与云原生**
- [[Docker容器化]] — Docker 容器化
- [[Docker容器化实战]] — Docker 容器化实战
- [[Kubernetes 知识点系统梳理_优化版]] — Kubernetes 容器编排
- [[Prometheus监控体系]] — Prometheus 监控体系
- [[DevOps与云原生知识点完整整合大全_优化版]] — DevOps 与云原生完整知识体系

**代码质量与安全**
- [[SonarQube-代码质量门禁]] — SonarQube 代码质量门禁
- [[CI-CD安全与凭据管理]] — CI/CD 安全与凭据管理
- [[依赖漏洞检测-Snyk]] — 依赖漏洞检测 Snyk
- [[SBOM软件物料清单]] — SBOM 软件物料清单

---

## 📖 学习路径建议

1. **入门**：理解 CI/CD 基本概念，学习 Git 工作流，使用 GitHub Actions 或 GitLab CI 搭建简单流水线
2. **进阶**：深入 Jenkins/GitLab CI 配置，学习多阶段流水线、自动化测试、制品管理、Docker 镜像构建
3. **高级**：学习 GitOps（ArgoCD/Flux）、多环境部署、灰度发布、蓝绿部署、回滚策略、流水线优化
4. **专家**：设计企业级 CI/CD 平台、DevSecOps 集成、多云部署、可观测性、DORA 指标度量、持续改进

---

## 💡 精简总结

CI/CD（持续集成/持续部署）是 DevOps 的核心实践，通过自动化流水线将代码从提交到生产部署的全过程自动化，实现快速、可靠、高频的软件交付。核心流程包括：代码提交 → 代码检查 → 构建 → 单元测试 → 集成测试 → 制品打包 → 部署测试环境 → 验收测试 → 部署预发布 → 人工审批 → 部署生产 → 监控告警。主流工具包括 Jenkins（自托管、功能强大）、GitLab CI/CD（一体化）、GitHub Actions（云服务、易用）、ArgoCD（GitOps、K8s 原生）。最佳实践包括：快速反馈、并行执行、语义化版本、安全凭据管理、测试金字塔、灰度发布、监控告警。CI/CD 不是一次性搭建，而是持续优化的过程，需要根据团队和项目的实际情况不断调整和改进。

---

> **CI/CD 的本质不是自动化工具，而是一种文化——频繁、小批量、自动化地交付价值，让软件交付从艺术变成工程。**

[[Home|🏠 返回首页]] · [[MOC-云原生与运维|☁️ 云原生与运维]] · [[学习路线总览|🗺️ 学习路线]]
