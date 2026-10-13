---
title: CI-CD安全与凭据管理
tags: [DevSecOps, CI/CD, 凭据管理, Secret, 供应链安全, 原子笔记]
category: 云原生与运维
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[容器安全与镜像扫描]]", "[[常见攻击与防御手段]]", "[[密码学基础-对称非对称哈希]]"]
aliases: [CI-CD安全与凭据管理]
---

# CI-CD安全与凭据管理

> **文档说明**：系统讲解 CI/CD 流水线安全与凭据管理，包括 Secret 管理、GitHub Actions/GitLab CI 安全配置、供应链安全（SLSA、依赖扫描）、镜像安全、流水线最佳实践，以及常见攻击和防御。
>
> **适用人群**：DevOps 工程师、SRE、后端开发者、需要构建安全 CI/CD 流水线的开发者
>
> **前置知识**：[[容器安全与镜像扫描]]、[[常见攻击与防御手段]]、[[密码学基础-对称非对称哈希]]

---

## 一、概述

### 1. CI/CD 安全威胁

```text
CI/CD 流水线的安全风险：
1. 凭据泄露：API Key、Token、密码硬编码或日志泄露
2. 依赖投毒：恶意依赖包混入构建
3. 镜像漏洞：基础镜像有已知漏洞
4. 流水线注入：恶意 PR 修改流水线配置
5. 权限过大：CI/CD 服务账户权限过高
6. 供应链攻击：构建过程被篡改
7. 制品污染：构建产物被篡改
8. 日志泄露：构建日志中包含敏感信息

CI/CD 是高价值攻击目标：
- 流水线有生产环境部署权限
- 可以访问代码仓库、镜像仓库、云服务
- 一次入侵可以影响所有用户
- SolarWinds、Codecov、npm 事件都是供应链攻击
```

### 2. DevSecOps 理念

```text
DevSecOps = Dev + Sec + Ops
- 安全左移：在开发早期就融入安全
- 自动化：安全检查自动化，不拖慢流水线
- 持续监控：运行时持续监控安全状态
- 责任共担：每个人都对安全负责

安全在流水线中的位置：
1. 代码提交：pre-commit 钩子（密钥扫描、格式检查）
2. PR 检查：静态代码扫描、依赖扫描、安全评审
3. 构建阶段：镜像扫描、SBOM 生成、制品签名
4. 测试阶段：DAST 扫描、渗透测试
5. 部署阶段：部署审批、策略校验、灰度发布
6. 运行阶段：运行时监控、漏洞扫描、应急响应
```

---

## 二、凭据管理

### 1. 凭据管理原则

```text
凭据管理核心原则：
1. 永不硬编码：密钥不写在代码里
2. 最小权限：凭据只授予必要权限
3. 短期有效：优先用短期 Token，而非长期密码
4. 定期轮换：定期更换密钥
5. 审计日志：记录凭据使用情况
6. 加密存储：凭据加密存储
7. 隔离环境：不同环境用不同凭据
8. 即时撤销：泄露时能立即撤销
```

### 2. 凭据存储方案

| 方案 | 特点 | 适用场景 |
|------|------|---------|
| **CI/CD 平台 Secrets** | GitHub Secrets/GitLab CI Variables | 简单项目、流水线专用 |
| **HashiCorp Vault** | 企业级、动态密钥、审计 | 中大型企业、多环境 |
| **云厂商密钥管理** | AWS Secrets Manager/Azure Key Vault/GCP Secret Manager | 云原生环境 |
| **Kubernetes Secrets** | K8s 原生、Base64 编码 | K8s 环境（需配合加密） |
| **Sealed Secrets** | K8s Secret 加密，可提交到 Git | GitOps 工作流 |
| **SOPS** | Mozilla 出品，加密 YAML/JSON | 配置文件加密 |
| **1Password/ Bitwarden** | 密码管理器，团队共享 | 小团队、手动使用 |

### 3. GitHub Actions 凭据管理

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    # 环境级 Secrets（需要环境审批）
    environment: production
    
    env:
      # 从 Secrets 读取，不硬编码
      AWS_REGION: us-east-1
    
    steps:
      - uses: actions/checkout@v4
      
      # 配置 AWS 凭证（用 OIDC 而非长期密钥）
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions-role
          aws-region: ${{ env.AWS_REGION }}
      
      # 使用 Secrets
      - name: Deploy
        run: ./deploy.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

```yaml
# GitHub Actions 安全最佳实践：

# 1. 最小权限的 GITHUB_TOKEN
permissions:
  contents: read
  packages: write
  # 不默认给所有权限

# 2. 固定 Action 版本（用 SHA，不用 @latest）
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1

# 3. 环境保护规则（生产环境需要审批）
# 在 GitHub 仓库 Settings → Environments 配置
# - Required reviewers：需要指定人员审批
# - Wait timer：等待时间
# - Deployment branches：限制分支

# 4. 防止 Secrets 泄露到日志
# GitHub 会自动屏蔽 Secrets 值
# 但要注意：echo $SECRET > file 可能写入文件
# 不要用 set-output 传递密钥
```

### 4. GitLab CI 凭据管理

```yaml
# .gitlab-ci.yml
variables:
  # 项目级变量（在 Settings → CI/CD → Variables 配置）
  # 勾选 "Masked" 防止泄露到日志
  # 勾选 "Protected" 只在受保护分支可用

deploy:
  stage: deploy
  image: alpine:3.19
  only:
    - main
  environment:
    name: production
  script:
    - echo "Deploying..."
    - ./deploy.sh
  # 变量在脚本中自动可用
  # $API_KEY, $DB_PASSWORD
```

### 5. HashiCorp Vault

```bash
# Vault 基本操作

# 启动开发模式 Vault
vault server -dev

# 写入密钥
vault kv put secret/myapp api_key=abc123 db_password=secret

# 读取密钥
vault kv get secret/myapp

# 动态密钥（数据库凭证自动生成和过期）
vault secrets enable database
vault write database/config/my-db \
  plugin_name=mysql-database-plugin \
  connection_url="{{username}}:{{password}}@tcp(db:3306)/" \
  allowed_roles="my-role" \
  username="vault-admin" \
  password="admin-password"

vault write database/roles/my-role \
  db_name=my-db \
  creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';GRANT SELECT ON *.* TO '{{name}}'@'%';" \
  default_ttl="1h" \
  max_ttl="24h"

# 获取动态数据库凭证（1小时后自动过期）
vault read database/creds/my-role
```

```yaml
# CI/CD 中使用 Vault（Vault Action）
- name: Import Secrets
  uses: hashicorp/vault-action@v2
  with:
    url: https://vault.example.com
    method: jwt
    role: github-actions
    secrets: |
      secret/data/myapp api_key | API_KEY ;
      secret/data/myapp db_password | DB_PASSWORD
```

### 6. 密钥扫描（防止提交到 Git）

```bash
# 工具：
# - git-secrets：AWS 出品，扫描提交
# - truffleHog：扫描 Git 历史中的密钥
# - gitleaks：Go 编写，快速扫描
# - detect-secrets：Yelp 出品，pre-commit 集成

# gitleaks 扫描
gitleaks detect --source . --verbose

# truffleHog 扫描 Git 历史
trufflehog filesystem . --include-paths .

# pre-commit 钩子配置
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

```bash
# 已经泄露了密钥怎么办？
# 1. 立即撤销/轮换密钥（最重要！）
# 2. 从 Git 历史中清除（git filter-repo / BFG）
# 3. 但假设密钥已经泄露，必须轮换
# 4. 审计密钥使用记录，查看是否被滥用

# 用 git filter-repo 清除历史
git filter-repo --replace-text <(echo 'api_key=abc123==>***REMOVED***')

# 注意：清除历史不能替代密钥轮换！
```

---

## 三、供应链安全

### 1. SLSA 框架

```text
SLSA（Supply-chain Levels for Software Artifacts）：
- Google 提出的供应链安全框架
- 4 个安全等级，从 L1 到 L4
- 覆盖构建、来源、依赖、分发全流程

SLSA 等级：
L1（入门）：有构建过程文档，生成 provenance
L2（进阶）：托管构建服务，生成签名 provenance
L3（高级）：构建环境隔离，防篡改，provenance 不可伪造
L4（最高）：可验证的构建，双人工审批，严格隔离

关键实践：
1. 生成 SBOM（软件物料清单）
2. 构建 provenance（构建来源证明）
3. 制品签名（Cosign）
4. 依赖锁定和扫描
5. 构建环境隔离和可复现
```

### 2. SBOM（软件物料清单）

```bash
# SBOM 工具：
# - Syft：Anchore 出品，生成 SBOM
# - CycloneDX：OWASP 标准格式
# - SPDX：Linux 基金会标准格式

# 用 Syft 生成 SBOM
syft myapp:latest -o spdx-json > sbom.spdx.json
syft myapp:latest -o cyclonedx-json > sbom.cdx.json

# 从 SBOM 扫描漏洞（Grype）
grype sbom:sbom.spdx.json

# 从代码生成 SBOM
syft dir:. -o spdx-json
```

### 3. 依赖漏洞扫描

```yaml
# GitHub Actions 依赖扫描
name: Security Scan

on: [push, pull_request]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # npm 依赖审计
      - name: npm audit
        run: npm audit --audit-level=high
      
      # Snyk 扫描
      - name: Snyk scan
        uses: snyk/actions/node@master
        continue-on-error: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      
      # Trivy 扫描依赖和镜像
      - name: Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
      
      # Dependabot（GitHub 内置）
      # 在 .github/dependabot.yml 配置
      # 自动创建依赖更新 PR
```

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
  
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
  
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 4. 制品签名

```bash
# Cosign（Sigstore 项目）
# 安装
brew install cosign

# 生成密钥对
cosign generate-key-pair

# 签名镜像
cosign sign --key cosign.key myapp:latest

# 验证签名
cosign verify --key cosign.pub myapp:latest

# 无密钥签名（OIDC + Fulcio）
cosign sign myapp:latest

# GitHub Actions 中签名
- name: Sign image
  uses: sigstore/cosign-installer@v3
- run: cosign sign --yes ${{ env.REGISTRY }}/myapp:${{ github.sha }}
  env:
    COSIGN_EXPERIMENTAL: "true"
```

---

## 四、镜像安全

### 1. 镜像扫描

```yaml
# GitHub Actions 镜像扫描
- name: Build image
  run: docker build -t myapp:${{ github.sha }} .

- name: Trivy image scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myapp:${{ github.sha }}
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'  # 高危漏洞阻断构建

- name: Upload Trivy results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

### 2. 安全的 Dockerfile

```dockerfile
# ✅ 安全的 Dockerfile 实践

# 1. 使用具体版本标签，不用 latest
FROM node:20-alpine AS builder

# 2. 非 root 用户运行
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# 3. 先复制依赖文件，利用缓存
COPY package*.json ./
RUN npm ci --only=production

# 4. 复制源码
COPY . .

# 5. 构建
RUN npm run build

# 多阶段构建：运行阶段用最小镜像
FROM node:20-alpine

# 6. 非 root 用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

WORKDIR /app

# 7. 只复制必要文件
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

# 8. 只读文件系统（运行时加 --read-only）
# 9. 不暴露敏感端口
EXPOSE 3000

# 10. 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/main.js"]

# ❌ 避免：
# FROM ubuntu:latest  # 大、有漏洞、版本不固定
# USER root            # root 运行
# COPY . .             # 复制全部（含 .git、密钥）
# RUN npm install      # 开发依赖也装上
```

### 3. 基础镜像选择

```text
基础镜像安全选择：

1. distroless（Google 出品）
   - 只包含应用和运行时依赖
   - 无 shell、无包管理器
   - 攻击面最小
   - gcr.io/distroless/nodejs20-debian12

2. Alpine
   - 小（~5MB）
   - 有包管理器（apk）
   - musl libc（某些应用不兼容）
   - node:20-alpine

3. 瘦身版 Debian/Ubuntu
   - 兼容性好
   - 体积中等
   - node:20-bookworm-slim

4. scratch
   - 空镜像
   - 只适合静态编译的程序（Go/Rust）
   - FROM scratch

推荐：
- Node.js：distroless 或 alpine
- Java：distroless/java 或 eclipse-temurin:17-jre-alpine
- Go：scratch 或 distroless/static
- Python：python:3.12-slim
```

---

## 五、流水线安全最佳实践

### 1. 流水线安全清单

```text
代码阶段：
- [ ] pre-commit 钩子：密钥扫描、代码格式、lint
- [ ] 分支保护：main 分支禁止直接推送，需要 PR
- [ ] PR 评审：至少 1 人审批，安全相关需安全团队审批
- [ ] 代码扫描：SAST（SonarQube/CodeQL）
- [ ] 依赖扫描：npm audit/Snyk/Dependabot
- [ ] 密钥扫描：gitleaks/truffleHog

构建阶段：
- [ ] 固定基础镜像版本，不用 latest
- [ ] 多阶段构建，最小化运行镜像
- [ ] 非 root 用户运行
- [ ] 镜像扫描：Trivy/Clair/Snyk
- [ ] 生成 SBOM
- [ ] 制品签名：Cosign
- [ ] 构建环境隔离：ephemeral runner

测试阶段：
- [ ] 单元测试 + 覆盖率门槛
- [ ] 集成测试
- [ ] DAST 扫描：OWASP ZAP
- [ ] API 安全测试
- [ ] 性能测试

部署阶段：
- [ ] 环境隔离：dev/staging/prod 分离
- [ ] 部署审批：生产环境需要人工审批
- [ ] 最小权限：部署账户最小权限
- [ ] 策略校验：OPA/Kyverno 策略检查
- [ ] 灰度发布：Canary/Blue-Green
- [ ] 回滚预案：快速回滚机制

运行阶段：
- [ ] 运行时监控：Falco/Sysdig
- [ ] 漏洞监控：持续扫描运行中镜像
- [ ] 日志审计：关键操作审计日志
- [ ] 入侵检测：异常行为检测
- [ ] 应急响应：安全事件响应预案
```

### 2. GitHub Actions 安全配置

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

# 最小权限
permissions:
  contents: read
  pull-requests: read
  security-events: write

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - run: npm ci
      - run: npm test
      - run: npm run lint

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # CodeQL 分析
      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: javascript
      
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
      
      # 密钥扫描
      - name: Gitleaks scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      # 依赖扫描
      - name: npm audit
        run: npm audit --audit-level=high
        continue-on-error: true

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Build image
        run: docker build -t ghcr.io/${{ github.repository }}:${{ github.sha }} .
      
      - name: Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
      
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Push image
        run: docker push ghcr.io/${{ github.repository }}:${{ github.sha }}
      
      - name: Sign image
        uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes ghcr.io/${{ github.repository }}:${{ github.sha }}
        env:
          COSIGN_EXPERIMENTAL: "true"
```

### 3. 分支保护规则

```text
GitHub 分支保护（Settings → Branches）：

main 分支保护：
- ✅ Require a pull request before merging
  - ✅ Require approvals: 1（或更多）
  - ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require status checks to pass before merging
  - 选择需要通过的检查（test/security/build）
- ✅ Require signed commits（可选）
- ✅ Include administrators（管理员也受限制）
- ✅ Restrict who can push to matching branches
- ✅ Lock branch（完全锁定，只能通过 PR）

保护标签（Tags）：
- 防止强制推送和删除标签
- v* 标签保护
```

---

## 六、常见攻击与防御

### 1. 凭据泄露

```text
攻击方式：
1. 硬编码密钥提交到 Git
2. 构建日志中打印密钥
3. 错误信息中泄露密钥
4. 上传到公开的代码仓库
5. 截图/录屏泄露

防御：
1. pre-commit 密钥扫描（gitleaks/detect-secrets）
2. CI 中密钥扫描（truffleHog）
3. 日志脱敏（CI 平台自动屏蔽 Secrets）
4. 代码仓库私有，公开前审计
5. 定期扫描 Git 历史
6. 泄露后立即轮换密钥

应急响应：
1. 立即撤销/轮换泄露的密钥
2. 审计密钥使用记录
3. 从 Git 历史清除（但假设已泄露）
4. 通知受影响方
5. 调查泄露原因，修复流程
```

### 2. 依赖投毒

```text
攻击方式：
1. 发布恶意 npm/PyPI 包（名称混淆）
2. 攻陷维护者账户，发布恶意版本
3.  typosquatting（名称仿冒：lodash → lodashh）
4. 依赖混淆（私有包名与公开包名冲突）
5. 植入后门（如 event-stream 事件）

防御：
1. 依赖锁定（package-lock.json/yarn.lock/poetry.lock）
2. 依赖扫描（npm audit/Snyk/Dependabot）
3. 最小依赖（减少不必要的依赖）
4. 固定版本（不用 ^/~ 范围）
5. 私有注册表（Verdaccio/Nexus，白名单）
6. 依赖审查（升级前审查变更）
7. npm scope（使用组织 scope）
```

### 3. 流水线注入

```text
攻击方式：
1. 恶意 PR 修改流水线配置（.github/workflows/*.yml）
2. 注入恶意脚本到构建脚本
3. 修改 Dockerfile 植入后门
4. pull_request_target 陷阱（恶意 PR 访问 Secrets）

防御：
1. 流水线配置变更需要安全评审
2. 外部贡献者的 PR 不自动运行需要 Secrets 的流水线
3. 用 pull_request 而非 pull_request_target
4. 构建脚本纳入代码审查
5. Dockerfile 安全扫描
6. 最小权限的 GITHUB_TOKEN
7. 固定 Action 版本（用 SHA）
```

```yaml
# ❌ 危险：pull_request_target 可以访问 Secrets
on:
  pull_request_target:
    types: [opened]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}  # 检出恶意代码
      - run: npm install  # 执行恶意代码
        env:
          SECRET: ${{ secrets.SECRET }}  # 恶意代码可以访问密钥

# ✅ 安全：pull_request 不访问 Secrets
on:
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install
      - run: npm test
        # 不需要 Secrets
```

### 4. 镜像投毒

```text
攻击方式：
1. 攻陷镜像仓库账户，上传恶意镜像
2. 仿冒官方镜像（docker pull mysql → 恶意镜像）
3. 基础镜像被植入后门
4. 构建过程中被篡改

防御：
1. 镜像签名验证（Cosign）
2. 只使用可信基础镜像（官方/verified publisher）
3. 固定镜像 digest（@sha256:...）
4. 私有镜像仓库（Harbor/Registry）
5. 镜像扫描（Trivy/Clair）
6. 构建环境隔离（ephemeral runner）
7. SBOM 和 provenance
```

---

## 七、最佳实践总结

### 1. 凭据管理

- [ ] **永不硬编码**：密钥不写在代码、配置、脚本中
- [ ] **使用 Secret 管理工具**：Vault/云厂商密钥管理/CI Secrets
- [ ] **最小权限**：凭据只授予必要权限
- [ ] **短期凭证优先**：OIDC/动态密钥，而非长期密码
- [ ] **定期轮换**：90天/180天轮换一次
- [ ] **审计日志**：记录凭据使用，异常告警
- [ ] **环境隔离**：dev/staging/prod 用不同凭据
- [ ] **密钥扫描**：pre-commit + CI 扫描
- [ ] **泄露应急**：有预案，泄露后立即轮换
- [ ] **日志脱敏**：CI 日志不打印密钥

### 2. 流水线安全

- [ ] **分支保护**：main 分支需 PR + 审批 + 检查通过
- [ ] **最小权限**：GITHUB_TOKEN/服务账户最小权限
- [ ] **固定版本**：Action/基础镜像用 SHA/具体版本
- [ ] **安全检查自动化**：SAST/DAST/依赖/镜像/密钥扫描
- [ ] **部署审批**：生产环境需要人工审批
- [ ] **环境隔离**：不同环境不同流水线/凭据
- [ ] **制品签名**：Cosign 签名，部署前验证
- [ ] **SBOM**：生成软件物料清单
- [ ] **构建隔离**：ephemeral runner，构建后销毁
- [ ] **审计日志**：所有流水线操作可追溯

### 3. 供应链安全

- [ ] **依赖锁定**：lock 文件提交到仓库
- [ ] **依赖扫描**：定期扫描漏洞
- [ ] **自动更新**：Dependabot/Renovate 自动更新
- [ ] **最小依赖**：删除不必要的依赖
- [ ] **私有注册表**：白名单控制依赖来源
- [ ] **SLSA 等级**：逐步提升 SLSA 等级
- [ ] **可复现构建**：相同输入产生相同输出
- [ ] **构建 provenance**：生成构建来源证明

---

## 八、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **密钥泄露到 Git** | 硬编码密钥并提交 | 立即轮换密钥、git filter-repo 清除历史、加 pre-commit 扫描 |
| **CI 日志泄露密钥** | echo 打印密钥/未 mask | CI 平台自动屏蔽、检查脚本、用环境变量不打印 |
| **依赖有漏洞** | 依赖版本旧 | npm audit、Snyk、Dependabot 自动更新、升级到安全版本 |
| **镜像有高危漏洞** | 基础镜像旧/依赖有漏洞 | Trivy 扫描、更新基础镜像、用 distroless、阻断高危构建 |
| **流水线被恶意 PR 篡改** | pull_request_target/权限过大 | 用 pull_request、流水线变更需审批、最小权限 |
| **部署到生产不需要审批** | 未配置环境保护 | 配置 environment、required reviewers、分支保护 |
| **GITHUB_TOKEN 权限过大** | 默认权限过高 | 在 workflow 中设置 permissions: contents: read |
| **Action 被投毒** | 用 @latest/未固定版本 | 用 SHA 固定版本、定期审查、用官方/verified Action |
| **镜像被篡改** | 未验证签名/用 latest | Cosign 签名验证、用 digest 固定、私有仓库 |
| **构建慢/资源浪费** | 未缓存/全量构建 | 依赖缓存、分层构建、仅构建变更部分 |
| **凭据无法轮换** | 硬编码/多处使用 | 用 Secret 管理工具、统一管理、自动化轮换 |
| **审计日志缺失** | 未开启审计 | 开启 CI/云服务审计日志、集中收集、告警 |
| **npm 包被投毒** | 名称混淆/未锁定版本 | 锁定版本、私有注册表、依赖审查、npm scope |
| **生产环境凭据被开发环境使用** | 未隔离环境 | 不同环境不同凭据、环境变量区分、访问控制 |
| **构建产物被篡改** | 构建环境不安全 | ephemeral runner、构建签名、可复现构建、provenance |
| **密钥扫描漏报** | 工具配置不当/基线未更新 | 更新工具、维护 .secrets.baseline、多种工具组合 |
| **OIDC 配置错误** | 信任策略过宽 | 限制 subject、最小信任、审计 OIDC 使用 |
| **K8s Secret 不安全** | 默认 Base64 编码 | 用 Sealed Secrets/External Secrets、etcd 加密、RBAC 控制 |
| **流水线并发导致竞态** | 未加锁/并发部署 | 用 concurrency 限制、部署锁、串行部署 |

---

## 九、关联笔记

### 安全相关
- [[容器安全与镜像扫描]] · [[常见攻击与防御手段]] · [[密码学基础-对称非对称哈希]]
- [[前端安全-XSS-CSRF防护]] · [[API安全最佳实践]] · [[Java-数据加密与脱敏]]
- [[AI安全与对齐基础]] · [[密码管理器-Bitwarden]]

### 云原生与运维
- [[Docker容器化实战]] · [[多架构镜像构建-buildx]] · [[K8s-核心概念与架构]]
- [[Kustomize-K8s配置管理]] · [[Operator与CRD开发]] · [[APM应用性能监控-SkyWalking]]

### 工具与效率
- [[Jenkins流水线实战]] · [[n8n-开源自动化平台]] · [[Zed-高性能编辑器]]

### 导航
- [[MOC-云原生与运维]] · [[MOC-计算机基础]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[容器安全与镜像扫描]] 容器安全 → 深入本文 CI/CD 安全 → 学习 [[常见攻击与防御手段]] 攻防知识 → 实践 [[K8s-核心概念与架构]] 云原生 → 研究 [[密码学基础-对称非对称哈希]] 密码学 → 构建完整的 DevSecOps 安全体系。

---

## 💡 全文深度讲解

本文系统梳理了CI-CD安全与凭据管理的核心知识体系，从概述入手，深入凭据管理的底层机制，再通过供应链安全掌握实战应用，最后涵盖常见问题与排查与关联笔记。学习时建议先建立整体认知，再动手实践，最后结合常见问题深化理解。

## 📝 全文精简总结

- **概述**：掌握本模块的核心概念与关键要点
- **凭据管理**：掌握本模块的核心概念与关键要点
- **供应链安全**：掌握本模块的核心概念与关键要点
- **镜像安全**：掌握本模块的核心概念与关键要点
- **流水线安全最佳实践**：掌握本模块的核心概念与关键要点
- **常见攻击与防御**：掌握本模块的核心概念与关键要点
- **最佳实践总结**：掌握本模块的核心概念与关键要点
- **常见问题与排查**：掌握本模块的核心概念与关键要点
- 其余1个模块涵盖进阶主题与拓展内容

