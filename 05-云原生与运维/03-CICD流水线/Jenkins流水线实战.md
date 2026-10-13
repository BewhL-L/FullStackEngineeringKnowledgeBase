---
title: Jenkins流水线实战
tags: [Jenkins, CI/CD, Pipeline, DevOps, CI, 持续交付, 原子笔记]
category: 云原生与运维
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[CI-CD安全与凭据管理]]", "[[Docker容器化实战]]", "[[容器安全与镜像扫描]]"]
aliases: [Jenkins流水线实战]
---

# Jenkins流水线实战

> **文档说明**：系统讲解 Jenkins 持续集成与持续交付流水线实战，包括安装配置、Declarative/Scripted Pipeline、多分支流水线、共享库、分布式构建、凭据管理、Git/Docker 集成，以及最佳实践和常见问题。
>
> **适用人群**：DevOps 工程师、后端开发者、运维工程师、需要构建 CI/CD 流水线的开发者
>
> **前置知识**：[[CI-CD安全与凭据管理]]、[[Docker容器化实战]]、[[容器安全与镜像扫描]]

---

## 一、概述

### 1. Jenkins 是什么

```text
Jenkins：
- 开源的持续集成/持续交付（CI/CD）自动化服务器
- 前身是 Hudson（2004 年 Sun 开发，2011 年分叉为 Jenkins）
- 用 Java 编写，可扩展（1800+ 插件）
- 支持各种构建、测试、部署自动化

核心功能：
1. 持续集成（CI）
   - 代码提交后自动构建和测试
   - 快速发现集成问题
   - 保证代码质量

2. 持续交付/部署（CD）
   - 自动化部署到测试/预发布/生产环境
   - 支持多种部署策略（蓝绿、金丝雀、滚动）
   - 审批流程

3. 自动化任务
   - 定时任务（cron）
   - 批处理
   - 报告生成
   - 任何可以脚本化的任务

Jenkins 的优势：
- 开源免费，社区活跃
- 插件生态丰富（几乎支持所有工具）
- 高度可定制
- 支持分布式构建
- 成熟稳定，企业级应用广泛

Jenkins 的劣势：
- UI 较老旧（Blue Ocean 改善）
- 插件管理复杂（兼容性问题）
- 配置即代码（JCasC）学习曲线
- 资源消耗较大
```

### 2. CI/CD 流程

```text
典型 CI/CD 流水线：

代码提交 → 触发构建 → 代码检查 → 单元测试 → 构建 → 集成测试 → 制品打包 → 部署测试环境 → 验收测试 → 部署预发布 → 审批 → 部署生产 → 监控

阶段详解：

1. 触发（Trigger）
   - 代码提交（Webhook）
   - 定时（cron）
   - 手动触发
   - 上游构建完成

2. 代码检出（Checkout）
   - 从 Git 仓库拉取代码
   - 检出特定分支/标签/commit

3. 代码质量检查（Lint/SAST）
   - 代码风格检查（ESLint/Checkstyle/flake8）
   - 静态代码分析（SonarQube）
   - 密钥扫描（gitleaks）
   - 依赖漏洞扫描（Snyk/Dependabot）

4. 单元测试（Unit Test）
   - 运行单元测试
   - 生成覆盖率报告
   - 覆盖率门槛

5. 构建（Build）
   - 编译代码
   - 打包（JAR/WAR/Docker 镜像）
   - 前端构建（npm run build）

6. 集成测试（Integration Test）
   - 启动服务（Docker Compose）
   - 运行集成测试
   - API 测试

7. 制品管理（Artifact）
   - 上传制品到仓库（Nexus/Artifactory）
   - Docker 镜像推送到 Registry
   - 版本标记

8. 部署（Deploy）
   - 部署到测试/预发布/生产
   - 蓝绿/金丝雀/滚动部署
   - 健康检查

9. 验收测试（E2E/Acceptance）
   - 端到端测试（Playwright/Selenium）
   - 性能测试
   - 安全扫描

10. 通知（Notification）
    - 构建结果通知（邮件/飞书/Slack）
    - 失败告警
    - 部署通知
```

---

## 二、安装与配置

### 1. Docker 安装（推荐）

```bash
# 拉取 Jenkins 镜像（LTS 版本）
docker pull jenkins/jenkins:lts

# 运行 Jenkins
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --restart unless-stopped \
  jenkins/jenkins:lts

# 查看初始管理员密码
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# 访问 http://localhost:8080
# 输入初始密码，安装推荐插件，创建管理员用户
```

```yaml
# docker-compose.yml
version: "3.8"

services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock  # 允许 Jenkins 调用 Docker
    environment:
      - TZ=Asia/Shanghai
      - JAVA_OPTS=-Duser.timezone=Asia/Shanghai -Xmx2g -Xms512m
    user: root  # 访问 Docker socket 需要 root（生产环境建议用 docker group）

volumes:
  jenkins_home:
```

### 2. 初始配置

```text
初始配置步骤：

1. 解锁 Jenkins
   - 访问 http://localhost:8080
   - 输入 initialAdminPassword

2. 安装插件
   - 选择"安装推荐的插件"（Install suggested plugins）
   - 或自定义选择插件
   - 推荐必装插件：
     - Pipeline（流水线）
     - Git（Git 集成）
     - Docker（Docker 集成）
     - Blue Ocean（现代化 UI）
     - Credentials Binding（凭据绑定）
     - Timestamper（时间戳）
     - AnsiColor（彩色输出）

3. 创建管理员用户
   - 用户名、密码、邮箱

4. 实例配置
   - Jenkins URL（http://jenkins.example.com:8080/）

5. 安装额外插件
   - Manage Jenkins → Plugins → Available plugins
   - 搜索并安装需要的插件
```

### 3. 配置即代码（JCasC）

```yaml
# JCasC（Jenkins Configuration as Code）
# jenkins.yaml
jenkins:
  systemMessage: "Jenkins CI/CD Server"
  numExecutors: 2
  mode: NORMAL
  scmCheckoutRetryCount: 3
  labelString: "master"

  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: "admin"
          password: "${ADMIN_PASSWORD}"
          name: "Administrator"
          email: "admin@example.com"

  authorizationStrategy:
    globalMatrix:
      permissions:
        - "Overall/Administer:admin"
        - "Overall/Read:authenticated"

  clouds:
    - docker:
        name: "docker"
        dockerApi:
          dockerHost:
            uri: "unix:///var/run/docker.sock"
        templates:
          - labelString: "docker-agent"
            dockerTemplateBase:
              image: "jenkins/inbound-agent:latest"
            remoteFs: "/home/jenkins"
            instanceCap: 5

credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              scope: GLOBAL
              id: "git-credentials"
              username: "${GIT_USERNAME}"
              password: "${GIT_PASSWORD}"
              description: "Git repository credentials"
          - string:
              scope: GLOBAL
              id: "dockerhub-token"
              secret: "${DOCKERHUB_TOKEN}"
              description: "Docker Hub access token"

tool:
  git:
    installations:
      - name: "Default"
        home: "git"
  docker:
    installations:
      - name: "Docker"
        home: "/usr/bin"

unclassified:
  location:
    url: "http://jenkins.example.com:8080/"
    adminAddress: "admin@example.com"
  timestamper:
    allPipelines: true
    systemTime: true
```

```bash
# 使用 JCasC 启动 Jenkins
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -v jenkins_home:/var/jenkins_home \
  -v $(pwd)/jenkins.yaml:/var/jenkins_home/jenkins.yaml \
  -e CASC_JENKINS_CONFIG=/var/jenkins_home/jenkins.yaml \
  -e ADMIN_PASSWORD=your_password \
  -e GIT_USERNAME=your_git_user \
  -e GIT_PASSWORD=your_git_pass \
  -e DOCKERHUB_TOKEN=your_token \
  jenkins/jenkins:lts
```

---

## 三、Pipeline 基础

### 1. Pipeline 类型

```text
Jenkins Pipeline 两种类型：

1. Declarative Pipeline（声明式流水线）
   - 更结构化，有固定的语法结构
   - 适合大多数场景
   - 可读性好，易于维护
   - 有内置的指令（agent/stages/steps/post）
   - 推荐使用

2. Scripted Pipeline（脚本式流水线）
   - 基于 Groovy 脚本，更灵活
   - 适合复杂逻辑
   - 学习曲线稍陡
   - 可以用完整的 Groovy 语法

3. 自由风格项目（Freestyle）
   - 传统方式，UI 配置
   - 不推荐新项目使用
   - 适合简单任务

Pipeline 定义位置：
- Jenkins UI 中直接编写（不推荐，不可版本控制）
- 项目仓库中的 Jenkinsfile（推荐，配置即代码）
- 共享库（Shared Library，复用公共逻辑）
```

### 2. Declarative Pipeline 基础结构

```groovy
// Jenkinsfile（Declarative Pipeline）
pipeline {
    // 1. agent：指定运行环境
    agent any
    // agent { label 'docker-agent' }
    // agent { docker { image 'node:20' } }
    // agent none  // 顶层不指定，每个 stage 单独指定

    // 2. options：流水线选项
    options {
        timestamps()           // 输出时间戳
        timeout(time: 30, unit: 'MINUTES')  // 超时
        buildDiscarder(logRotator(numToKeepStr: '10'))  // 保留最近10次构建
        disableConcurrentBuilds()  // 禁止并发构建
        ansiColor('xterm')  // 彩色输出
    }

    // 3. parameters：构建参数
    parameters {
        string(name: 'ENV', defaultValue: 'dev', description: '部署环境')
        choice(name: 'VERSION', choices: ['latest', 'v1.0', 'v2.0'], description: '版本')
        booleanParam(name: 'DEPLOY', defaultValue: true, description: '是否部署')
    }

    // 4. environment：环境变量
    environment {
        APP_NAME = 'myapp'
        DOCKER_REGISTRY = 'registry.example.com'
        // 凭据绑定
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-token')
        GIT_CREDENTIALS = credentials('git-credentials')
    }

    // 5. triggers：触发方式
    triggers {
        cron('H 2 * * *')  // 每天凌晨2点
        // pollSCM('H/15 * * * *')  // 每15分钟轮询 SCM
        // upstream(upstreamProjects: 'build-job', threshold: hudson.model.Result.SUCCESS)
    }

    // 6. stages：阶段定义（核心）
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo "Building ${APP_NAME}..."
                sh 'npm install'
                sh 'npm run build'
            }
        }

        stage('Test') {
            steps {
                sh 'npm test'
            }
            post {
                always {
                    junit 'test-results/**/*.xml'
                    cobertura 'coverage.xml'
                }
            }
        }

        stage('Deploy') {
            when {
                expression { return params.DEPLOY }
                branch 'main'
            }
            steps {
                echo "Deploying to ${params.ENV}..."
                sh './deploy.sh'
            }
        }
    }

    // 7. post：构建后操作
    post {
        success {
            echo 'Build succeeded!'
            // 飞书/Slack/邮件通知
        }
        failure {
            echo 'Build failed!'
            // 失败告警
        }
        unstable {
            echo 'Build unstable!'
        }
        always {
            echo 'Cleaning up...'
            // 清理工作空间
            // cleanWs()
        }
        changed {
            echo 'Build status changed!'
        }
    }
}
```

### 3. Scripted Pipeline

```groovy
// Jenkinsfile（Scripted Pipeline）
node('docker-agent') {
    try {
        stage('Checkout') {
            checkout scm
        }

        stage('Build') {
            echo "Building..."
            sh 'npm install'
            sh 'npm run build'
        }

        stage('Test') {
            try {
                sh 'npm test'
            } finally {
                junit 'test-results/**/*.xml'
            }
        }

        stage('Deploy') {
            if (env.BRANCH_NAME == 'main') {
                echo 'Deploying to production...'
                sh './deploy.sh'
            }
        }

        currentBuild.result = 'SUCCESS'
    } catch (Exception e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        // 通知
        if (currentBuild.result == 'FAILURE') {
            echo 'Build failed!'
        }
        cleanWs()
    }
}
```

---

## 四、多分支流水线

### 1. 多分支流水线配置

```text
多分支流水线（Multibranch Pipeline）：
- 自动为仓库的每个分支创建独立的流水线
- 新分支推送自动创建任务
- 分支删除自动清理任务
- 适合 Git Flow / GitHub Flow 工作流

配置步骤：
1. 新建 Item → Multibranch Pipeline
2. 配置 Branch Sources（Git/GitHub/GitLab）
3. 配置 Build Configuration（by default Jenkinsfile）
4. 配置 Scan Multibranch Pipeline Triggers
5. 保存，Jenkins 自动扫描分支并创建任务
```

```groovy
// Jenkinsfile（多分支流水线，根据分支执行不同逻辑）
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Test') {
            steps {
                sh 'npm install'
                sh 'npm run build'
                sh 'npm test'
            }
        }

        // 开发分支部署到开发环境
        stage('Deploy to Dev') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Deploying to development...'
                sh './deploy.sh dev'
            }
        }

        // 功能分支部署到测试环境（可选）
        stage('Deploy to Staging') {
            when {
                branch 'release/*'
            }
            steps {
                echo 'Deploying to staging...'
                sh './deploy.sh staging'
            }
        }

        // 主分支部署到生产（需要审批）
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                // 等待人工审批
                input(
                    message: 'Deploy to production?',
                    ok: 'Deploy',
                    submitter: 'admin,devops-team'
                )
                echo 'Deploying to production...'
                sh './deploy.sh prod'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
```

---

## 五、Docker 集成

### 1. Docker Agent

```groovy
// 使用 Docker 容器作为构建环境
pipeline {
    agent {
        docker {
            image 'node:20-alpine'
            args '-v /etc/localtime:/etc/localtime:ro'
            // alwaysPull true  // 每次拉取最新镜像
        }
    }

    stages {
        stage('Build') {
            steps {
                sh 'node --version'
                sh 'npm --version'
                sh 'npm install'
                sh 'npm run build'
            }
        }
    }
}

// 每个 stage 使用不同的 Docker 镜像
pipeline {
    agent none

    stages {
        stage('Build') {
            agent {
                docker { image 'node:20-alpine' }
            }
            steps {
                sh 'npm install && npm run build'
            }
        }

        stage('Test') {
            agent {
                docker { image 'node:20-alpine' }
            }
            steps {
                sh 'npm test'
            }
        }

        stage('Package') {
            agent {
                docker {
                    image 'docker:24'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                sh 'docker build -t myapp:latest .'
            }
        }
    }
}
```

### 2. Docker Compose 集成测试

```groovy
// 使用 Docker Compose 启动依赖服务进行集成测试
pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = "test-${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Start Services') {
            steps {
                sh 'docker-compose -f docker-compose.test.yml up -d'
                // 等待服务就绪
                sh '''
                    for i in {1..30}; do
                        if docker exec ${COMPOSE_PROJECT_NAME}-db-1 pg_isready -U test; then
                            echo "Database is ready"
                            break
                        fi
                        echo "Waiting for database... $i"
                        sleep 2
                    done
                '''
            }
        }

        stage('Integration Test') {
            steps {
                sh 'npm run test:integration'
            }
            post {
                always {
                    junit 'test-results/**/*.xml'
                }
            }
        }
    }

    post {
        always {
            // 清理 Docker Compose 服务
            sh 'docker-compose -f docker-compose.test.yml down -v'
        }
    }
}
```

### 3. 构建并推送 Docker 镜像

```groovy
pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'registry.example.com'
        IMAGE_NAME = 'myapp'
        // 凭据
        REGISTRY_CREDENTIALS = credentials('registry-credentials')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Image') {
            steps {
                script {
                    // 构建镜像，标签为 commit hash
                    def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    env.IMAGE_TAG = gitCommit
                    env.FULL_IMAGE = "${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

                    sh "docker build -t ${FULL_IMAGE} ."
                    // 同时打 latest 标签（主分支）
                    if (env.BRANCH_NAME == 'main') {
                        sh "docker tag ${FULL_IMAGE} ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        stage('Scan Image') {
            steps {
                // Trivy 镜像漏洞扫描
                sh "trivy image --severity CRITICAL,HIGH --exit-code 1 ${FULL_IMAGE}"
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                    echo "$REGISTRY_CREDENTIALS_PSW" | docker login $DOCKER_REGISTRY -u "$REGISTRY_CREDENTIALS_USR" --password-stdin
                    docker push $FULL_IMAGE
                    if [ "$BRANCH_NAME" = "main" ]; then
                        docker push $DOCKER_REGISTRY/$IMAGE_NAME:latest
                    fi
                '''
            }
        }
    }

    post {
        always {
            sh 'docker logout $DOCKER_REGISTRY || true'
            cleanWs()
        }
    }
}
```

---

## 六、共享库（Shared Library）

### 1. 共享库结构

```text
共享库（Shared Library）：
- 抽取公共的 Pipeline 逻辑，复用代码
- 独立的 Git 仓库
- 可以在多个 Jenkins 任务/项目中使用

目录结构：
shared-library/
├── src/                    # 类文件（Groovy 类）
│   └── com/
│       └── example/
│           ├── Docker.groovy
│           └── Deploy.groovy
├── vars/                   # 全局变量/自定义步骤（最常用）
│   ├── buildApp.groovy     # 自定义步骤 buildApp()
│   ├── deployApp.groovy    # 自定义步骤 deployApp()
│   └── notifyStatus.groovy # 自定义步骤 notifyStatus()
├── resources/              # 资源文件（配置/模板）
│   ├── Dockerfile.template
│   └── default-config.yaml
└── README.md
```

### 2. 自定义步骤

```groovy
// vars/buildApp.groovy
def call(Map config = [:]) {
    // 默认配置
    def appName = config.appName ?: env.JOB_NAME
    def buildCmd = config.buildCmd ?: 'npm run build'
    def testCmd = config.testCmd ?: 'npm test'

    stage('Checkout') {
        checkout scm
    }

    stage('Install Dependencies') {
        sh 'npm ci'
    }

    stage('Lint') {
        sh 'npm run lint'
    }

    stage('Test') {
        sh testCmd
    }
    post {
        always {
            junit 'test-results/**/*.xml'
        }
    }

    stage('Build') {
        sh buildCmd
    }

    echo "Build ${appName} completed successfully!"
}

// vars/deployApp.groovy
def call(Map config = [:]) {
    def environment = config.environment ?: 'dev'
    def image = config.image ?: "${env.DOCKER_REGISTRY}/${env.JOB_NAME}:${env.BUILD_NUMBER}"

    stage("Deploy to ${environment}") {
        // 生产环境需要审批
        if (environment == 'prod') {
            input(
                message: "Approve deployment to production?",
                ok: 'Deploy',
                submitter: 'admin'
            )
        }

        sh """
            kubectl set image deployment/${env.JOB_NAME} \
              ${env.JOB_NAME}=${image} \
              --namespace=${environment}
            kubectl rollout status deployment/${env.JOB_NAME} \
              --namespace=${environment} --timeout=300s
        """
    }
}

// vars/notifyStatus.groovy
def call(String status = 'SUCCESS') {
    def color = status == 'SUCCESS' ? 'green' : 'red'
    def message = "${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - ${status}"

    // 飞书通知
    sh """
        curl -X POST -H 'Content-Type: application/json' \
          -d '{"msg_type":"text","content":{"text":"${message}"}}' \
          "${FEISHU_WEBHOOK_URL}"
    """
}
```

### 3. 使用共享库

```groovy
// Jenkinsfile（使用共享库）
@Library('my-shared-library') _

pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                // 使用自定义步骤
                buildApp(
                    appName: 'my-web-app',
                    buildCmd: 'npm run build',
                    testCmd: 'npm test'
                )
            }
        }

        stage('Deploy') {
            steps {
                deployApp(
                    environment: 'prod',
                    image: 'registry.example.com/myapp:latest'
                )
            }
        }
    }

    post {
        success {
            notifyStatus('SUCCESS')
        }
        failure {
            notifyStatus('FAILURE')
        }
    }
}
```

---

## 七、凭据管理

### 1. 凭据类型

```text
Jenkins 支持的凭据类型：

1. Username with password（用户名密码）
   - Git 仓库认证
   - Docker Registry 认证
   - SSH 用户名密码

2. SSH Username with private key（SSH 私钥）
   - Git 仓库 SSH 认证
   - 服务器 SSH 登录

3. Secret text（密文文本）
   - API Token
   - Access Key
   - Webhook URL

4. Secret file（密文文件）
   - kubeconfig 文件
   - 服务账户 JSON
   - 证书文件

5. Certificate（证书）
   - SSL 证书
   - 客户端证书

6. Docker Host Certificate Authentication
   - Docker 守护进程认证
```

### 2. 凭据使用

```groovy
pipeline {
    agent any

    environment {
        // 方式1：credentials() 绑定用户名密码
        // 自动生成 _USR 和 _PSW 两个变量
        GIT_CREDENTIALS = credentials('git-credentials')

        // 方式2：绑定 secret text
        API_TOKEN = credentials('api-token')

        // 方式3：绑定 SSH 私钥
        // SSH_CREDENTIALS = credentials('ssh-credentials')
    }

    stages {
        stage('Git Clone') {
            steps {
                // 使用凭据克隆 Git 仓库
                git(
                    url: 'https://github.com/org/repo.git',
                    branch: 'main',
                    credentialsId: 'git-credentials'
                )
            }
        }

        stage('Docker Login') {
            steps {
                // 使用凭据登录 Docker Registry
                withCredentials([usernamePassword(
                    credentialsId: 'docker-registry',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo "$DOCKER_PASS" | docker login registry.example.com -u "$DOCKER_USER" --password-stdin'
                }
            }
        }

        stage('Deploy with Kubeconfig') {
            steps {
                // 使用 secret file（kubeconfig）
                withCredentials([file(
                    credentialsId: 'kubeconfig',
                    variable: 'KUBECONFIG_FILE'
                )]) {
                    sh 'kubectl --kubeconfig=$KUBECONFIG_FILE apply -f k8s/'
                }
            }
        }

        stage('SSH Deploy') {
            steps {
                // 使用 SSH 凭据
                sshagent(['ssh-deploy-key']) {
                    sh 'ssh user@server "cd /app && ./deploy.sh"'
                }
            }
        }
    }
}
```

---

## 八、与 Git 平台集成

### 1. GitHub 集成

```text
GitHub 集成方式：

1. GitHub App（推荐）
   - 安装 GitHub App 到组织/仓库
   - 细粒度权限控制
   - 自动配置 Webhook
   - 支持 GitHub Checks API

2. Personal Access Token（PAT）
   - 简单但权限较大
   - 配置 Webhook 手动触发

3. SSH Key
   - 用于克隆私有仓库

Webhook 配置：
- Payload URL: http://jenkins.example.com/github-webhook/
- Content type: application/json
- Events: Push、Pull request、Create
```

```groovy
// GitHub PR 构建
pipeline {
    agent any

    triggers {
        // GitHub PR 触发
        githubPush()
    }

    stages {
        stage('Checkout') {
            steps {
                // 检出 PR 分支
                githubscm pr: env.CHANGE_ID
            }
        }

        stage('Build & Test') {
            steps {
                sh 'npm install && npm test'
            }
        }
    }

    post {
        success {
            // 设置 PR 状态检查
            setGitHubPullRequestStatus state: 'SUCCESS', context: 'jenkins/build'
        }
        failure {
            setGitHubPullRequestStatus state: 'FAILURE', context: 'jenkins/build'
        }
    }
}
```

### 2. GitLab 集成

```text
GitLab 集成：

1. GitLab Plugin
   - 安装 GitLab 插件
   - 配置 GitLab 连接（URL + API Token）
   - 自动配置 Webhook

2. Webhook 手动配置
   - URL: http://jenkins.example.com/project/<job-name>
   - Secret Token
   - 触发事件：Push、Merge Request、Tag

3. GitLab CI 与 Jenkins 配合
   - GitLab CI 做简单检查
   - Jenkins 做复杂构建部署
```

---

## 九、分布式构建

### 1. Agent 概念

```text
Jenkins 分布式架构：

- Controller（控制器/Master）
  - 管理 Jenkins 配置、任务调度、Web UI
  - 不执行构建（生产环境建议）
  - 协调 Agent

- Agent（代理/Node）
  - 实际执行构建任务
  - 可以是物理机、虚拟机、容器、云实例
  - 通过标签（Label）分类
  - 可以动态创建/销毁（Docker/Kubernetes）

Agent 连接方式：
1. SSH Agent：通过 SSH 连接到远程机器
2. JNLP Agent：Agent 主动连接 Controller（inbound-agent）
3. Docker Agent：Docker 容器作为 Agent
4. Kubernetes Agent：K8s Pod 作为 Agent（动态创建）
5. 云 Agent：AWS EC2 / Azure VM / GCP GCE（动态创建）
```

### 2. Kubernetes 动态 Agent

```yaml
# Kubernetes Pod Template（Jenkins 配置）
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins: agent
spec:
  containers:
    - name: jnlp
      image: jenkins/inbound-agent:latest
      resources:
        requests:
          cpu: "500m"
          memory: "512Mi"
        limits:
          cpu: "2"
          memory: "2Gi"
      volumeMounts:
        - name: workspace
          mountPath: /home/jenkins/agent

    - name: docker
      image: docker:24-dind
      securityContext:
        privileged: true
      volumeMounts:
        - name: docker-certs
          mountPath: /certs/client

    - name: kubectl
      image: bitnami/kubectl:latest
      command: ["cat"]
      tty: true

  volumes:
    - name: workspace
      emptyDir: {}
    - name: docker-certs
      emptyDir: {}
```

```groovy
// 使用 Kubernetes 动态 Agent
pipeline {
    agent {
        kubernetes {
            label 'k8s-agent'
            yamlFile 'k8s/pod-template.yaml'
            // 或内联 YAML
            // yaml '''
            // apiVersion: v1
            // kind: Pod
            // ...
            // '''
        }
    }

    stages {
        stage('Build') {
            steps {
                container('docker') {
                    sh 'docker build -t myapp .'
                }
            }
        }

        stage('Deploy') {
            steps {
                container('kubectl') {
                    sh 'kubectl apply -f k8s/'
                }
            }
        }
    }
}
```

---

## 十、最佳实践

### 1. Pipeline 设计

- [ ] **Jenkinsfile 入库**：Pipeline 定义放在项目仓库，版本控制
- [ ] **使用 Declarative Pipeline**：结构化、可读性好，除非需要复杂逻辑
- [ ] **阶段清晰**：每个 stage 做一件事，命名清晰
- [ ] **复用代码**：公共逻辑抽取到共享库（Shared Library）
- [ ] **参数化构建**：用 parameters 支持不同环境/版本
- [ ] **超时控制**：设置合理的超时，避免挂死
- [ ] **并发控制**：同一项目禁止并发构建（disableConcurrentBuilds）
- [ ] **构建保留策略**：只保留最近 N 次构建，节省磁盘
- [ ] **清理工作空间**：构建后清理（cleanWs），避免磁盘满

### 2. 安全实践

- [ ] **凭据管理**：所有密钥用 Jenkins Credentials，不硬编码
- [ ] **最小权限**：凭据只授予必要权限
- [ ] **凭据轮换**：定期更换密钥
- [ ] **Controller 不执行构建**：生产环境 Controller 只做调度
- [ ] **Agent 隔离**：不同项目/环境用不同 Agent
- [ ] **Docker 安全**：不用 privileged 除非必要，扫描镜像
- [ ] **审计日志**：记录所有操作，支持审计
- [ ] **访问控制**：基于角色的权限控制（RBAC）
- [ ] **HTTPS**：Jenkins Web UI 用 HTTPS
- [ ] **插件安全**：只安装必要插件，定期更新

### 3. 性能优化

- [ ] **分布式构建**：用 Agent 分担构建负载
- [ ] **动态 Agent**：K8s/Docker 动态创建，按需使用
- [ ] **并行阶段**：独立的 stage 用 parallel 并行执行
- [ ] **缓存依赖**：npm/maven 依赖缓存，避免重复下载
- [ ] **增量构建**：只构建变更的模块
- [ ] **Docker 层缓存**：合理安排 Dockerfile 指令顺序
- [ ] **工作空间复用**：相同分支复用工作空间
- [ ] **限制构建历史**：只保留必要的构建记录
- [ ] **监控资源**：监控 Controller/Agent 的 CPU/内存/磁盘

### 4. 可观测性

- [ ] **构建通知**：成功/失败通知到飞书/Slack/邮件
- [ ] **构建趋势**：查看构建时长、成功率趋势
- [ ] **测试报告**：JUnit/Coobertura 报告可视化
- [ ] **制品管理**：构建产物归档和管理
- [ ] **日志聚合**：构建日志集中存储和搜索
- [ ] **告警**：构建失败率高、构建时间异常时告警
- [ ] **审计**：谁在什么时候做了什么操作

---

## 十一、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **构建一直挂起** | Agent 不足/标签不匹配/队列阻塞 | 检查 Agent 状态、标签匹配、队列、增加 Agent |
| **磁盘空间不足** | 构建历史太多/工作空间未清理/制品未清理 | 配置 buildDiscarder、cleanWs、清理旧制品、扩容磁盘 |
| **凭据不生效** | 凭据 ID 错/作用域不对/绑定方式错 | 检查凭据 ID、作用域（Global/System）、withCredentials 语法 |
| **Git 克隆失败** | 凭据错/网络问题/仓库地址错 | 检查凭据、网络、仓库 URL、分支名 |
| **Docker 命令找不到** | Agent 未安装 Docker/Docker 未启动 | 安装 Docker、启动 Docker 服务、用 Docker Agent |
| **Docker 权限拒绝** | Jenkins 用户不在 docker 组 | 将 jenkins 用户加入 docker 组、重启 Jenkins |
| **Pipeline 语法错误** | Declarative 语法不规范/Groovy 错误 | 用 VS Code Jenkins 插件校验、查看错误日志、参考文档 |
| **共享库加载失败** | 仓库地址错/凭据错/目录结构错 | 检查仓库配置、凭据、src/vars 目录结构、版本号 |
| **并发构建冲突** | 同一项目并发构建/共享资源冲突 | disableConcurrentBuilds、用不同工作空间、资源锁 |
| **构建超时** | 构建步骤卡住/网络超时/死锁 | 增加 timeout、检查卡住的步骤、网络连通性、加心跳 |
| **Agent 离线** | 网络断开/Agent 进程挂了/证书过期 | 检查网络、重启 Agent、更新证书、检查防火墙 |
| **K8s Agent 不启动** | 权限不足/资源不足/镜像拉取失败 | 检查 ServiceAccount 权限、资源配额、镜像拉取密钥 |
| **插件兼容性问题** | 插件版本冲突/Jenkins 版本太旧 | 更新 Jenkins、更新插件、查看插件兼容性矩阵 |
| **中文乱码** | JVM 编码设置/系统编码 | 设置 JAVA_OPTS=-Dfile.encoding=UTF-8、系统 locale |
| **构建慢** | 依赖未缓存/串行执行/Agent 性能差 | 缓存依赖、并行 stage、升级 Agent、增量构建 |
| **Webhook 不触发** | Webhook URL 错/网络不通/事件未配置 | 检查 Webhook URL、防火墙、事件类型、Jenkins 日志 |
| **测试报告不显示** | 报告路径错/格式不对/插件未装 | 检查 junit/cobertura 路径、XML 格式、安装插件 |
| **Docker 镜像推送失败** | 未登录/凭据错/镜像名错 | docker login、检查凭据、镜像名格式（registry/name:tag） |
| **Kubectl 命令失败** | kubeconfig 错/权限不足/集群不可达 | 检查 kubeconfig、RBAC 权限、网络连通性 |
| **邮件通知失败** | SMTP 配置错/凭据错/网络不通 | 检查 SMTP 配置、凭据、25 端口、用 465/587 端口 |
| **Jenkins 启动慢** | 插件太多/工作空间大/磁盘慢 | 减少插件、清理工作空间、用 SSD、调整 JVM 参数 |
| **内存溢出（OOM）** | 构建任务太多/JVM 内存不足 | 增加 JVM 内存（-Xmx）、减少并发构建、分布式构建 |

---

## 十二、关联笔记

### CI/CD 与 DevOps
- [[CI-CD安全与凭据管理]] · [[n8n-开源自动化平台]] · [[容器安全与镜像扫描]]
- [[多架构镜像构建-buildx]] · [[Kustomize-K8s配置管理]]

### 云原生与运维
- [[Docker容器化实战]] · [[K8s-核心概念与架构]] · [[APM应用性能监控-SkyWalking]]
- [[Operator与CRD开发]] · [[文件系统详解-ext4-btrfs]]

### 后端开发
- [[Java-应用性能调优实战]] · [[SpringValidation-参数校验]] · [[Python-代码覆盖率与质量门禁]]
- [[Python-集成测试与E2E测试]]

### 导航
- [[MOC-云原生与运维]] · [[MOC-后端开发]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Docker容器化实战]] 容器基础 → 学习 [[CI-CD安全与凭据管理]] 安全实践 → 深入本文 Jenkins 流水线 → 实践 [[K8s-核心概念与架构]] 容器编排 → 研究 [[APM应用性能监控-SkyWalking]] 监控 → 构建完整的 DevOps 与 CI/CD 体系。

---

## 💡 全文深度讲解

本文系统梳理了Jenkins流水线实战的核心知识体系，从概述入手，深入安装与配置的底层机制，再通过Pipeline 基础掌握实战应用，最后涵盖常见问题与排查与关联笔记。学习时建议先建立整体认知，再动手实践，最后结合常见问题深化理解。

## 📝 全文精简总结

- **概述**：掌握本模块的核心概念与关键要点
- **安装与配置**：掌握本模块的核心概念与关键要点
- **Pipeline 基础**：掌握本模块的核心概念与关键要点
- **多分支流水线**：掌握本模块的核心概念与关键要点
- **Docker 集成**：掌握本模块的核心概念与关键要点
- **共享库（Shared Library）**：掌握本模块的核心概念与关键要点
- **凭据管理**：掌握本模块的核心概念与关键要点
- **与 Git 平台集成**：掌握本模块的核心概念与关键要点
- 其余4个模块涵盖进阶主题与拓展内容

