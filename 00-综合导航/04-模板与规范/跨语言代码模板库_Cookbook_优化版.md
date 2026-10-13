---
title: 跨语言代码模板库 Cookbook（优化版）
tags: [MOC, 模板库, Cookbook, Dockerfile, CI/CD, Helm, Terraform, Prometheus, OpenAPI]
created: 2026-08-25
updated: 2026-08-25
status: ✅ 内容已完善
priority: 常规
pre: []
aliases: [跨语言代码模板库_Cookbook_优化版]
category: 综合导航
difficulty: ⭐⭐

---

# 📦 跨语言代码模板库 Cookbook（优化版）

> 本库补齐「维度二：可复用模板」缺口——把多语言、多场景的即用片段沉淀为一处，新项目复制即跑。覆盖应用层(.gitignore/Dockerfile/CI/OpenAPI)、 infra 层(Helm/Terraform/Prometheus)。
> **格式标准**：场景说明 → 模板代码 → 注释要点（💡 + 📝 + 🔍）→ 全文总结。

---

## 目录

1. `.gitignore` 多语言模板
2. 多阶段 `Dockerfile` 模板
3. CI/CD `GitHub Actions` 模板
4. `.editorconfig` 通用模板
5. `OpenAPI` 接口契约模板
6. `Helm Chart` 模板
7. `Terraform` 模块模板
8. `Prometheus` 告警规则模板

---

## 一、`.gitignore` 多语言模板

### 1.1 模板
```gitignore
# ---- 通用 ----
.DS_Store
.idea/
*.log
.env
.env.*

# ---- Python ----
__pycache__/
*.py[cod]
.venv/
.mypy_cache/
.pytest_cache/

# ---- Node ----
node_modules/
dist/
.next/
coverage/

# ---- Java ----
target/
*.class
.mvn/

# ---- Go ----
/bin/
*.test
```

### 1.2 要点
💡 **深度讲解**：`.env` 必须忽略——密钥入库是最高危泄露源；用 `.env.example` 提交占位。
📝 **精简总结**：按技术栈叠加规则；密钥与构建产物永不入库。
🔍 **知识点深度解析**：作用=防误提交；原理=Git 忽略匹配；要点=团队统一一份根 `.gitignore`。

---

## 二、多阶段 `Dockerfile` 模板

### 2.1 模板（Node 示例，Python/Java 同理）
```dockerfile
# ---- 构建阶段 ----
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- 运行阶段 ----
FROM node:20-alpine AS run
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
USER node                       # 非 root
EXPOSE 3000
CMD ["node","dist/index.js"]
```

### 2.2 要点
💡 **深度讲解**：多阶段让最终镜像只剩运行时依赖，体积可从 1GB+ 降到几十 MB；`USER node` 降权限是容器安全基线。
📝 **精简总结**：分 build/run 两阶段；用 alpine/slim；非 root 运行；`npm ci` 而非 `install` 保可复现。
🔍 **知识点深度解析**：作用=瘦身+安全；原理=层复用；要点=固定基础镜像 digest 防漂移。

---

## 三、CI/CD `GitHub Actions` 模板

### 3.1 模板
```yaml
name: ci
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt && ruff check . && mypy . && pytest
      - run: docker build -t app:${{ github.sha }} .
```

### 3.2 要点
💡 **深度讲解**：CI 至少跑「lint + 类型 + 测试 + 构建」四段；门禁失败即阻断合并，把问题挡在仓库外。
📝 **精简总结**：checkout 用 v4；缓存依赖提速；质量门禁前置；镜像打 sha 标签可溯源。
🔍 **知识点深度解析**：作用=质量左移；原理=每次推送触发；要点=密钥走 `secrets`，勿硬编码。

---

## 四、`.editorconfig` 通用模板

### 4.1 模板
```ini
root = true
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2
[*.py]
indent_size = 4
[*.md]
trim_trailing_whitespace = false
```

### 4.2 要点
💡 **深度讲解**：`.editorconfig` 跨编辑器统一风格，比「各自 IDE 设置」可靠，消除「换行符差异导致整文件 diff」。
📝 **精简总结**：根目录放一份；按语言调缩进；Markdown 关尾部去空防误改。
🔍 **知识点深度解析**：作用=消除环境差异；原理=声明式优先；要点=提交进仓库而非本地。

---

## 五、`OpenAPI` 接口契约模板

### 5.1 模板
```yaml
openapi: 3.0.3
info: { title: Order API, version: 1.0.0 }
paths:
  /orders:
    post:
      summary: 创建订单
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/Order' }
      responses:
        '201': { description: 已创建 }
components:
  schemas:
    Order:
      type: object
      required: [userId, amount]
      properties:
        userId: { type: string }
        amount: { type: number }
```

### 5.2 要点
💡 **深度讲解**：OpenAPI 是前后端契约单一事实源，可自动生成客户端 SDK、Mock Server 与文档，减少联调扯皮。
📝 **精简总结**：先写契约再编码；`required` 标必填；用 `$ref` 复用 schema；接 Swagger UI 自动出文档。
🔍 **知识点深度解析**：作用=接口即文档；原理=机器可读描述；要点=CI 校验契约兼容性防破坏。

---

## 六、`Helm Chart` 模板

### 6.1 模板（节选 `templates/deployment.yaml`）
```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: {{ .Release.Name }}-app }
spec:
  replicas: {{ .Values.replicas }}
  template:
    spec:
      containers:
      - name: app
        image: "{{ .Values.image.repo }}:{{ .Values.image.tag }}"
        resources:
          requests: { cpu: "100m", memory: "128Mi" }
          limits:   { cpu: "500m", memory: "256Mi" }
```

### 6.2 要点
💡 **深度讲解**：Helm 用 Go template 把 K8s 清单参数化，`values.yaml` 区分环境；`requests/limits` 是调度与防饿死的必需。
📝 **精简总结**：模板抽变量到 `values.yaml`；务必设资源 request/limit；用 `helm lint` + `helm template` 预检。
🔍 **知识点深度解析**：作用=K8s 配置复用；原理=模板渲染；要点=镜像 tag 用变量，禁 `latest`。

---

## 七、`Terraform` 模块模板

### 7.1 模板
```hcl
variable "region" { type = string  default = "ap-guangzhou" }
resource "tencentcloud_instance" "web" {
  instance_name = "web"
  instance_type = "S5.MEDIUM2"
  image_id      = "img-xxxx"
  availability_zone = "${var.region}-2"
}
output "private_ip" { value = tencentcloud_instance.web.private_ip }
```

### 7.2 要点
💡 **深度讲解**：Terraform 用「状态文件 state」映射真实资源；`plan` 预览变更、`apply` 执行，IaC 让环境可版本化、可回滚。
📝 **精简总结**：远程后端存 state（防丢失/锁冲突）；`terraform plan` 必审；敏感输出标 `sensitive=true`。
🔍 **知识点深度解析**：作用=基础设施即代码；原理=声明式+状态比对；要点=state 加密 + 锁，勿提交本地 state。

---

## 八、`Prometheus` 告警规则模板

### 8.1 模板
```yaml
groups:
- name: app
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{code=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
    for: 5m
    labels: { severity: critical }
    annotations:
      summary: "错误率 >5% 持续 5 分钟"
      runbook: "https://wiki/internal/err-rate"
```

### 8.2 要点
💡 **深度讲解**：`for: 5m` 避免瞬时抖动误告；`rate()` 取速率而非瞬时；附 `runbook` 让告警「自带处置手册」。
📝 **精简总结**：用 `rate` 看趋势；设 `for` 防抖；标签分级(severity)；告警绑定 runbook 提升 MTTR。
🔍 **知识点深度解析**：作用=可观测告警；原理=拉取指标+规则评估；要点=RED 指标(速率/错误/时延)配告警。

---

## 📎 原子笔记纵向下钻

> 以下为 `10-四级知识框架/07-DevOps` 与 `09-效率工具链` 中对应的模板类原子笔记，按本篇章节骨架归类。

### 一、`.gitignore` 多语言模板
- [[Git-高级命令与底层原理|Git 高级命令与底层原理]]

### 二、多阶段 `Dockerfile` 模板
- [[Dockerfile最佳实践|Dockerfile 最佳实践]]
- [[Docker-核心原理与镜像优化|Docker 核心原理与镜像优化]]
- [[Docker-Compose编排|Docker Compose 编排]]

### 三、CI/CD `GitHub Actions` 模板
- [[GitHub-Actions流水线设计|GitHub Actions 流水线设计]]
- [[GitLab-CI配置|GitLab CI 配置]]

### 四、`.editorconfig` 通用模板
- [[VSCode-核心配置与插件|VSCode 核心配置与插件]]

### 五、`OpenAPI` 接口契约模板
- [[API设计规范-OpenAPI|API 设计规范 OpenAPI]]

### 六、`Helm Chart` 模板
- [[Helm-Chart包管理|Helm Chart 包管理]]

### 七、`Terraform` 模块模板
- [[Terraform-基础设施编排|Terraform 基础设施编排]]
- [[Ansible-配置管理|Ansible 配置管理]]

### 八、`Prometheus` 告警规则模板
- [[Prometheus-指标采集|Prometheus 指标采集]]
- [[Grafana-可视化看板|Grafana 可视化看板]]
- [[告警体系设计|告警体系设计]]
- [[ELK-日志聚合|ELK 日志聚合]]
- [[Jaeger-分布式链路追踪|Jaeger 分布式链路追踪]]

### 🗂 文档与图表模板
- [[Mermaid-图表绘制|Mermaid 图表绘制]]
- [[PlantUML-UML建模|PlantUML UML 建模]]
- [[Markdown进阶语法|Markdown 进阶语法]]
- [[文档自动生成工具|文档自动生成工具]]

### 🗂 相关 MOC
- [[MOC-DevOps-四级展开|DevOps MOC]]
- [[MOC-效率工具链-四级展开|效率工具链 MOC]]

## 全文精简总结

Cookbook 是「复制即跑」的效率资产：应用层(.gitignore/Dockerfile/CI/OpenAPI) + infra 层(Helm/Terraform/Prometheus) 全覆盖。建议各板块在旗舰大全末尾加「🧩 可复用模板」小节并链接本库，形成「概念讲解 + 即拷模板」闭环。

[[知识库学习适配性评估与优化报告|← 六维度评估报告]] | [[Home|🏠 返回首页]]
