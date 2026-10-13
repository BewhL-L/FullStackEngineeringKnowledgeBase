---
title: DevOps与云原生知识点完整整合大全
tags: [DevOps, Docker, Kubernetes, CI/CD, 可观测性, IaC, DevSecOps]
category: 云原生
created: 2026-08-25
updated: 2026-08-25
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: []
aliases: [DevOps与云原生知识点完整整合大全_优化版]
---

# DevOps与云原生知识点完整整合大全

> **优化版说明**：本文档参照《Java知识点完整整合大全》的排版风格，系统梳理 DevOps 与云原生 6 大知识域（容器化 / Kubernetes / CI-CD / 监控可观测性 / IaC / DevSecOps）。每知识点含概述、核心特性、常用用法、注意事项四模块，附「🔍 知识点深度解析」、「💡 深度讲解」与「📝 精简总结」。

---

## 目录

1. [容器化：Docker](#1-容器化docker)
2. [Kubernetes 容器编排](#2-kubernetes-容器编排)
3. [CI/CD 持续集成与交付](#3-cicd-持续集成与交付)
4. [监控与可观测性](#4-监控与可观测性)
5. [基础设施即代码 IaC](#5-基础设施即代码-iac)
6. [DevSecOps 与安全左移](#6-devsecops-与安全左移)

---

## 1. 容器化：Docker

### 1.1 概述

Docker 用容器封装应用与其依赖，实现"一次构建、到处运行"。核心：镜像（只读模板）、容器（运行实例）、仓库（镜像分发）。底层靠 Linux 命名空间（隔离）与 cgroups（限额）。

> 🔍 **知识点深度解析**
>
> **作用**：容器解决"在我机器能跑"的环境不一致问题，是云原生与微服务的交付标准。
>
> **原理**：镜像分层（UnionFS）只读叠加，容器在其上加可写层；命名空间隔离 PID/网络/挂载等，cgroups 限制 CPU/内存；仓库（Registry）分发镜像。
>
> **用法要点**：① 用多阶段构建缩小镜像；② 基础镜像选 slim/alpine；③ 非 root 运行；④ 固定基础镜像版本；⑤ 不在镜像存密钥。

### 1.2 核心特性

**镜像**：分层、可缓存、可复用、Digest 寻址。

**容器**：轻量、秒级启停、可移植。

**网络/存储**：桥接/主机/None 网络，Volume 持久化。

**编排前置**：Compose 单机多容器。

> 🔍 **知识点深度解析**
>
> **作用**：分层让构建缓存高效；Volume 解决容器易失；Compose 编排开发环境。
>
> **原理**：镜像每层有 hash，改动层才重建，未变层命中缓存；Volume 挂载宿主机目录绕过可写层持久化；Compose 用 YAML 定义服务依赖与网络。
>
> **用法要点**：① 把变动少层放前、源码层放后提缓存命中；② 状态用 Volume 而非容器层；③ 开发用 Compose，生产用 K8s；④ 镜像扫描查漏洞；⑤ 资源限额防单容器吃满。

### 1.3 常用用法

```dockerfile
# 多阶段构建（Go 示例）
FROM golang:1.22 AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o app .

FROM alpine:3.20
COPY --from=build /src/app /usr/local/bin/app
USER 1000                       # 非 root
ENTRYPOINT ["/usr/local/bin/app"]
```

```bash
docker build -t myapp:1.0 .
docker run -d -p 8080:8080 --memory=512m --name myapp myapp:1.0
```

> 🔍 **知识点深度解析**
>
> **作用**：多阶段构建把编译环境与运行环境分离，最终镜像仅含二进制，体积小、攻击面小。
>
> **原理**：`build` 阶段编译出二进制，`alpine` 阶段只 COPY 二进制；`CGO_ENABLED=0` 静态编译免 libc；`USER 1000` 降权。
>
> **用法要点**：① 多阶段几乎必用；② 运行阶段用 distroless/alpine；③ 设 --memory/--cpus 限额；④ 用 digest 固定镜像（image@sha256:...）；⑤ 定期重新构建获安全补丁。

### 1.4 注意事项

1. **镜像膨胀**：未多阶段/装冗余致大镜像，拉取慢、攻击面大
2. **root 运行**：容器 root≈宿主机风险，用非 root
3. **密钥泄露**：勿写进镜像，用 Secret/外部配置
4. **latest 标签**：不可复现，固定版本/digest
5. **漏洞**：基础镜像带 CVE，定期扫描与更新

> 💡 **深度讲解**：Docker 用"分层 + 命名空间 + cgroups"把应用和环境打包成可移植单元。工程要点是镜像治理：多阶段构建（编译与运行分离）让最终镜像只剩二进制，体积小且安全；分层顺序影响缓存——把稳定层（依赖安装）放前、易变层（源码）放后，构建命中率高。三大安全底线：非 root 运行、密钥不进镜像（用 Secret/挂载）、镜像扫描查 CVE。绝不用 latest（不可复现），固定版本或 digest。容器层易失，状态必须挂 Volume。Compose 管开发多容器，K8s 管生产编排。

> 📝 **精简总结**：Docker=镜像(分层)/容器(隔离+限额)/仓库；构建=多阶段+alpine+非root；要点=缓存分层/Volume持久/固定digest；安全=非root/密钥外置/镜像扫描/禁latest。

---

## 2. Kubernetes 容器编排

### 2.1 概述

Kubernetes（K8s）容器编排标准，自动化部署、扩缩容、自愈。核心对象：Pod（最小调度单元）、Deployment（无状态）、Service（服务发现）、Ingress（入口）、ConfigMap/Secret（配置）。

> 🔍 **知识点深度解析**
>
> **作用**：当容器多到人工管不过来，K8s 提供声明式编排——你描述期望状态，它维持。
>
> **原理**：控制平面（API Server/etcd/Scheduler/Controller）监听状态并调谐（reconcile）使实际趋近期望；Pod 是共享网络的容器组；ReplicaSet 保副本数；kubelet 管节点上的 Pod。
>
> **用法要点**：① 无状态用 Deployment，有状态用 StatefulSet；② 配置用 ConfigMap，敏感用 Secret；③ 暴露用 Service+Ingress；④ 资源 limits 必设（防饿死）；⑤ 用 HPA 按指标自动扩。

### 2.2 核心特性

**工作负载**：Pod、Deployment、StatefulSet、DaemonSet、Job/CronJob。

**网络/服务**：Service（ClusterIP/NodePort/LoadBalancer）、Ingress、DNS。

**配置**：ConfigMap、Secret、 downward API。

**弹性/运维**：HPA（自动扩）、探针（liveness/readiness）、滚动更新、Namespace。

> 🔍 **知识点深度解析**
>
> **作用**：对象模型覆盖"跑什么/怎么发现/怎么配置/怎么扩缩/怎么健康"。
>
> **原理**：readiness 探针通才接流量、liveness 失败才重启；HPA 按 CPU/自定义指标调副本；滚动更新逐批替换保可用；StatefulSet 给稳定网络标识与持久卷。
>
> **用法要点**：① 必配 readiness/liveness 探针；② 资源 request/limit 都要设；③ 滚动更新配 maxSurge/maxUnavailable；④ Ingress 统一入口+TLS；⑤ Namespace 做环境/租户隔离。

### 2.3 常用用法

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: myapp }
spec:
  replicas: 3
  selector: { matchLabels: { app: myapp } }
  template:
    metadata: { labels: { app: myapp } }
    spec:
      containers:
      - name: myapp
        image: myapp:1.0
        resources: { requests: { cpu: "100m", memory: "128Mi" }, limits: { cpu: "500m", memory: "256Mi" } }
        readinessProbe: { httpGet: { path: /health, port: 8080 }, initialDelaySeconds: 5 }
        livenessProbe:  { httpGet: { path: /health, port: 8080 }, initialDelaySeconds: 10 }
```

```bash
kubectl apply -f deploy.yaml
kubectl get pods -l app=myapp
kubectl rollout status deployment/myapp
```

> 🔍 **知识点深度解析**
>
> **作用**：该 YAML 是生产级 Deployment 骨架——副本、资源限额、探针齐全。
>
> **原理**：`requests` 供调度预留，`limits` 防超用；探针让流量只在就绪后进入、异常时重启；`kubectl rollout` 观察滚动进度可回滚。
>
> **用法要点**：① requests/limits 必设防调度失衡；② 探针路径真实健康；③ 改镜像触发滚动更新；④ 异常 `kubectl rollout undo`；⑤ 用 `kubectl logs/exec/describe` 排障。

### 2.4 注意事项

1. **资源不设限**：Pod 吃满节点，引发雪崩，必设 limits
2. **探针误配**：liveness 过严致频繁重启，readiness 不准致流量进不了
3. **Secret 明文**：etcd 默认不加密，启用加密+外部 Secret 管理
4. **镜像 latest**：不可复现，固定 tag/digest
5. **权限过大**：Pod 用特权/挂载 socket 风险，最小权限

> 💡 **深度讲解**：K8s 是"声明式编排"——你写期望状态（YAML），控制平面持续调谐。核心对象：Pod（调度单元）、Deployment（无状态主流）、Service（稳定访问）、Ingress（统一入口）。生产四要素：资源 requests/limits（防雪崩）、readiness/liveness 探针（健康与流量门）、滚动更新（不停机）、HPA（按指标扩缩）。StatefulSet 服务状态应用（稳定标识+持久卷）。最大坑：不设资源限额导致节点被吃满；探针配错导致重启风暴或流量进黑洞；Secret 明文存 etcd 需加密。安全遵循最小权限（非特权、不用 host socket）。K8s 还支持 Operator/CRD 扩展（如数据库、AI 网关）。

> 📝 **精简总结**：K8s=声明式编排(Pod/Deployment/Service/Ingress)；要点=资源限额/探针/滚动更新/HPA；有状态=StatefulSet；配置=ConfigMap/Secret；注意=必设limits/探针误配/Secret加密/最小权限。

---

## 3. CI/CD 持续集成与交付

### 3.1 概述

CI/CD 自动化构建、测试、部署。CI 频繁合码自动测；CD 自动/半自动发布到各环境。代表：GitHub Actions、GitLab CI、ArgoCD（GitOps）、Jenkins。

> 🔍 **知识点深度解析**
>
> **作用**：CI/CD 把"人肉发布"变"流水线"，提速、降错、可回滚。
>
> **原理**：代码推送触发流水线（触发→拉码→构建→测试→打包→部署）；GitOps 以 Git 为唯一真相源，ArgoCD 监听仓库自动同步集群；制品（镜像/包）入仓库。
>
> **用法要点**：① 提交即跑单测（快反馈）；② 流水线分层（lint→test→build→deploy）；③ 环境用变量隔离；④ 制品不可变（构建一次多处部署）；⑤ 生产用审批/金丝雀。

### 3.2 核心特性

**阶段**：触发→ checkout → 构建 → 测试 → 打包 → 部署 → 验证。

**模式**：CI（自动测）、CD（自动发）、GitOps（Git 驱动同步）。

**制品**：镜像仓库、Nexus/Artifactory、语义版本。

**策略**：蓝绿、金丝雀、滚动。

> 🔍 **知识点深度解析**
>
> **作用**：阶段化与发布策略决定质量与风险；GitOps 让集群状态可追溯、可回滚。
>
> **原理**：GitOps 把期望清单存 Git，控制器比对实际并自动 reconcil；金丝雀先放小流量验证再全量；蓝绿两套环境切流量零停机；制品不可变保证各环境一致。
>
> **用法要点**：① 流水线快失败（lint/test 前置）；② 制品一次构建多环境复用；③ 生产用金丝雀/蓝绿降风险；④ GitOps 审查即发布；⑤ 密钥用 Secrets 不硬编码。

### 3.3 常用用法

```yaml
# GitHub Actions 示例
name: ci
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test                 # 单测先跑（快失败）
      - run: docker build -t myapp:${{ github.sha }} .
      - run: docker push myapp:${{ github.sha }}
```

```bash
# ArgoCD 同步（GitOps）
argocd app sync myapp          # 把 Git 清单同步到集群
```

> 🔍 **知识点深度解析**
>
> **作用**：该流水线展示"拉码→装依赖→单测→构建→推镜像"最小 CI；镜像用 commit SHA 作不可变 tag。
>
> **原理**：`on: [push]` 触发；步骤顺序即阶段；`${{ github.sha }}` 作镜像 tag 保证不可变与可追溯；ArgoCD `app sync` 将 Git 期望态落到集群。
>
> **用法要点**：① 单测失败立即阻断；② tag 用 SHA 而非 latest；③ 缓存依赖加速；④ 密钥用 Secrets 上下文；⑤ 构建矩阵覆盖多版本。

### 3.4 注意事项

1. **密钥硬编码**：流水线明文密钥泄露，用 Secrets/ OIDC
2. **慢流水线**：全量测试在 CI 拖慢，分层+缓存
3. **制品可变**：同 tag 重推致环境不一致，用不可变 tag
4. **跳测试直发**：漏测上线即故障，门禁必过
5. **回滚缺失**：无回滚预案，故障恢复慢

> 💡 **深度讲解**：CI/CD 的本质是"把发布从手工艺术变成可重复流水线"。CI 让每次提交自动构建测试（快反馈、早发现问题）；CD 自动化部署；GitOps（ArgoCD）进一步把 Git 作为集群状态的唯一真相源，变更即 PR、同步即发布、回滚即回退提交。发布策略决定风险：金丝雀（小流量验证）、蓝绿（瞬间切换）、滚动（逐批）。三大纪律：制品不可变（SHA tag，一次构建多处部署）、密钥走 Secrets/OIDC 不硬编码、流水线快失败（lint/test 前置）。务必准备回滚预案——故障恢复速度=MTTR。

> 📝 **精简总结**：CI/CD=自动构建测发；阶段=触发→构建→测试→打包→部署；模式=CI/CD/GitOps(ArgoCD)；策略=金丝雀/蓝绿/滚动；纪律=制品不可变/密钥外置/快失败/有回滚。

---

## 4. 监控与可观测性

### 4.1 概述

可观测性三支柱：Metrics（指标）、Logs（日志）、Traces（链路）。工具：Prometheus（指标采集）、Grafana（看板）、ELK/Loki（日志）、Jaeger（链路）、Sentry（错误）。

> 🔍 **知识点深度解析**
>
> **作用**：分布式系统"看不见就管不了"，三支柱让故障可定位、性能可量化、用户可追踪。
>
> **原理**：Metrics 用时序数据库（Prometheus 拉模型+PromQL）；Logs 集中收集检索；Traces 用 TraceID 串起一次请求跨服务链路（OpenTelemetry 标准）；三者靠同一 TraceID/标签关联。
>
> **用法要点**：① 核心指标（RED：速率/错误/时延）上监控；② 日志结构化（JSON）+ 级别；③ 跨服务传 TraceID；④ 告警有分级与值班；⑤ SLO/SLI 驱动。

### 4.2 核心特性

**指标**：RED（请求/错误/时延）、USE（利用率/饱和/错误）、4黄金信号。

**日志**：集中采集、结构化、检索、保留策略。

**链路**：Span/Trace、采样、依赖拓扑。

**告警**：阈值/异常检测、分级、值班（on-call）。

> 🔍 **知识点深度解析**
>
> **作用**：指标看趋势、日志查细节、链路定位置，三者互补。
>
> **原理**：RED 法（Rate/Errors/Duration）覆盖服务健康；PromQL 做聚合与告警；OTel 统一埋点跨语言；采样控成本（高流量不全采）；告警疲劳靠分级与静默。
>
> **用法要点**：① 服务级 RED 指标必上；② 日志 JSON 化便于检索；③ TraceID 跨服务传递；④ 告警接 IM/电话+值班；⑤ 用 SLO 定可用性目标。

### 4.3 常用用法

```yaml
# Prometheus 抓取配置（片段）
scrape_configs:
  - job_name: myapp
    static_configs:
      - targets: ['myapp:8080']     # /metrics 端点
# 告警规则（PromQL）
# rate(http_errors_total[5m]) / rate(http_requests_total[5m]) > 0.05  → 告警
```

```bash
# 查最近 5 分钟 P99 时延
promtool query instant 'histogram_quantile(0.99, rate(http_duration_seconds_bucket[5m]))'
```

> 🔍 **知识点深度解析**
>
> **作用**：Prometheus 拉取 `/metrics`，PromQL 做聚合与分位；错误率超阈值触发告警。
>
> **原理**：`scrape_configs` 定义抓取目标；`rate(...[5m])` 算窗口速率；`histogram_quantile` 从直方图算 P99；错误率比值超 5% 告警。
>
> **用法要点**：① 应用暴露 `/metrics`（client lib）；② 直方图埋点算分位；③ 告警阈值基于 SLO；④ 多实例用 `sum by` 聚合；⑤ Grafana 建可视化。

### 4.4 注意事项

1. **指标爆炸**：高基数标签（如 user_id）撑爆时序库，控制基数
2. **日志敏感**：明文日志泄隐私，脱敏+级控
3. **采样失联**：链路采样过高漏关键 trace，关键路径全采
4. **告警疲劳**：阈值松/无分级致无视，分级+值班
5. **无 SLO**：监控无目标，先定 SLI/SLO

> 💡 **深度讲解**：可观测性是"凭输出推断内部状态"的能力，三支柱缺一不可：Metrics（趋势/告警）、Logs（细节/排障）、Traces（跨服务定位）。RED 法（Rate/Errors/Duration）是服务监控黄金模板，Prometheus+Grafana 是事实标准，OTel 统一埋点。成本陷阱：高基数标签（把 user_id 当标签）会撑爆时序库，必须控制基数；日志含敏感信息要脱敏；链路采样过高会漏关键路径。告警要分级 + 值班，否则变噪音（告警疲劳）。先定 SLO/SLI 再监控——没有目标就没有"正常与否"的判断。

> 📝 **精简总结**：可观测性=Metrics/Logs/Traces三支柱；指标=RED(率/错/时延)/USE；工具=Prometheus/Grafana/ELK/Jaeger/Sentry；链路=OTel+TraceID；注意=高基数标签/日志脱敏/采样失联/告警疲劳/先定SLO。

---

## 5. 基础设施即代码 IaC

### 5.1 概述

IaC 用代码声明基础设施（云资源/网络/集群），可版本化、复用、审计。代表：Terraform（多云）、Ansible（配置管理）、Pulumi（编程语言写）、Kubernetes YAML（声明式）。

> 🔍 **知识点深度解析**
>
> **作用**：手动点控制台不可复现、难审计、易漂移；IaC 让基础设施像应用一样可版本管理与回滚。
>
> **原理**：声明式（描述期望态，工具调谐）如 Terraform/HCL、K8s YAML；命令式（描述步骤）如 Ansible playbook；状态文件记录已建资源用于增量变更与销毁。
>
> **用法要点**：① 基础设施入 Git 评审；② 用远程状态（锁防并发）；③ 模块化复用；④ 变量与环境分离；⑤ 变更走 plan 预览再 apply。

### 5.2 核心特性

**工具**：Terraform（资源编排）、Ansible（配置/软件）、Pulumi（代码写）、CloudFormation（AWS）。

**形态**：声明式（期望态）vs 命令式（步骤）。

**关键概念**：状态文件、计划（plan）、模块、Provider、漂移检测。

> 🔍 **知识点深度解析**
>
> **作用**：工具各擅其职——Terraform 管资源、Ansible 管配置、Pulumi 用熟悉语言。
>
> **原理**：Terraform 读 HCL 生成执行计划（增/删/改），apply 调云 API 并写 state；`terraform plan` 预览变更防误删；模块参数化复用；Provider 抽象各云。
>
> **用法要点**：① 远程后端存 state（加密+锁）；② plan 必审再 apply；③ 模块抽公共组件；④ 变量分层（多环境）；⑤ 定期 `terraform plan` 检测漂移。

### 5.3 常用用法

```hcl
# Terraform 示例
terraform {
  backend "s3" { bucket = "tf-state", key = "prod/terraform.tfstate", encrypt = true }
}
provider "aws" { region = "ap-east-1" }
resource "aws_instance" "web" {
  ami           = var.ami
  instance_type = "t3.medium"
  tags = { Name = "web-${var.env}" }
}
```

```bash
terraform init && terraform plan -out=tf.plan   # 预览
terraform apply tf.plan                          # 执行
```

> 🔍 **知识点深度解析**
>
> **作用**：该示例声明一台 EC2，远端 state 防并发改、加密保安全；plan 预览再 apply。
>
> **原理**：`backend "s3"` 存状态并加锁；`plan -out` 固化计划避免 apply 时漂移；变量 `var.*` 分离环境；`tags` 便于管理。
>
> **用法要点**：① 远程 state 必加密+锁；② 永远先 plan 再审；③ 变量与环境分离；④ 模块复用避免重复；⑤ CI 中 apply 需审批。

### 5.4 注意事项

1. **状态丢失**：state 是唯一真相，远程备份+锁，勿手改
2. **误删**：plan 不审直接 apply 可能删生产，强制审批
3. **密钥**：state 可能含明文 secret，加密+最小权限
4. **漂移**：控制台手改致 IaC 与实际不一致，定期 plan 检测
5. **依赖循环**：资源互相依赖，模块化+depends_on 理清

> 💡 **深度讲解**：IaC 把基础设施变成"可评审、可回滚、可复现"的代码。声明式（Terraform/HCL、K8s YAML）描述期望态由工具调谐，命令式（Ansible）描述步骤。两个命门：状态文件与计划预览。state 是 Terraform 的唯一真相源，必须远端存储（加密+锁），丢失或手改会灾难；apply 前必 `plan` 审查，防止误删生产资源（强制审批）。密钥可能进 state，需加密与最小权限。控制台手改造成"漂移"，定期 plan 检测并纠正。变量与环境分离、模块复用是规模化关键。Pulumi 让熟悉语言写基础设施，降低学习成本。

> 📝 **精简总结**：IaC=基础设施即代码(可版本/复用/审计)；工具=Terraform(资源)/Ansible(配置)/Pulumi(代码)/K8s YAML；形态=声明式(期望态)/命令式(步骤)；命门=状态文件(远端加密锁)/plan必审；注意=误删/密钥/漂移/循环依赖。

---

## 6. DevSecOps 与安全左移

### 6.1 概述

DevSecOps 把安全嵌入 DevOps 全流程（左移：越早越好），覆盖代码、依赖、镜像、基础设施、运行时。核心：SAST/DAST、SCA（依赖扫描）、镜像扫描、策略即代码、RBAC。

> 🔍 **知识点深度解析**
>
> **作用**：安全事后补成本高且易漏，左移让漏洞在开发/构建阶段就暴露。
>
> **原理**：SAST 静态扫代码（如 SonarQube）、SCA 扫依赖漏洞（如 Snyk/Trivy）、DAST 运行时扫（如 ZAP）、镜像扫描查基础镜像 CVE、策略即代码（OPA）校验 YAML、RBAC 控集群权限。
>
> **用法要点**：① 依赖漏洞 CI 阻断（SCA）；② 镜像构建即扫（Trivy）；③ 代码质量+安全门禁；④ K8s 用 RBAC/PSA 最小权限；⑤ SBOM 盘点物料。

### 6.2 核心特性

**扫描**：SAST（代码）、SCA（依赖）、DAST（运行）、IaC 扫描、镜像扫描。

**治理**：SBOM（物料清单）、策略即代码（OPA）、审批门禁。

**运行时安全**：RBAC、Pod Security、网络策略、Secret 管理、运行时防护。

**合规**：等保/行业监管要求、审计留痕。

> 🔍 **知识点深度解析**
>
> **作用**：多层扫描覆盖"代码→依赖→镜像→运行"，策略与权限守住边界。
>
> **原理**：SCA 比对依赖与漏洞库（CVE）给修复建议；OPA 用 Rego 策略校验 K8s YAML（如禁特权容器）；Pod Security Admission 分级（privileged/baseline/restricted）；RBAC 最小授权。
>
> **用法要点**：① CI 集成 SCA+SAST 门禁；② 镜像扫描入流水线阻断高危；③ OPA 校验准入；④ RBAC 按角色最小授权；⑤ SBOM 用于应急溯源。

### 6.3 常用用法

```bash
# 依赖与镜像扫描（CI 中）
trivy fs --severity HIGH,CRITICAL ./          # SCA：扫项目依赖漏洞
trivy image --severity HIGH,CRITICAL myapp:1.0 # 镜像扫描 CVE
# 失败非零退出码 → 流水线阻断
```

```yaml
# OPA/K8s 策略示例（禁特权容器，示意）
# violation[msg] { input.spec.containers[_].securityContext.privileged; msg := "禁止特权容器" }
```

> 🔍 **知识点深度解析**
>
> **作用**：Trivy 在 CI 同时扫依赖与镜像，高危即非零退出阻断发布；OPA 在准入时拒违规 YAML。
>
> **原理**：`trivy fs` 扫文件树依赖清单（lock 文件）比对 CVE；`trivy image` 解镜像层查 OS/语言包漏洞；OPA Rego 在 Admission 时评估拒绝特权容器。
>
> **用法要点**：① 高危漏洞设阻断、中低仅告警；② 固定基础镜像版本便于复扫；③ 策略即代码纳入版本库；④ 扫描结果进看板跟踪修复；⑤ 定期重扫（新 CVE）。

### 6.4 注意事项

1. **门禁过严**：全量阻断拖慢，按严重度分级（CI 拦高危、低危跟踪）
2. **依赖炸弹**：间接依赖带漏洞，SCA 须递归
3. **镜像裸奔**：不扫描上线即带 CVE，构建即扫
4. **权限过大**：K8s 特权/广 RBAC 风险，最小授权
5. **合规缺位**：等保/行业要求前置，审计算法留痕

> 💡 **深度讲解**：DevSecOps 不是加一个安全团队，而是把安全能力织进每条流水线——越左移（越早）成本越低。扫描分层：SAST（代码静态）、SCA（依赖漏洞，最常见的真实入口）、DAST（运行时）、镜像扫描（基础镜像 CVE）、IaC 扫描（错误配置）。治理靠 SBOM（物料清单，应急溯源）+ 策略即代码（OPA 校验 YAML）+ 门禁（高危阻断）。运行时靠 RBAC（最小授权）、Pod Security（禁特权）、网络策略（隔离）、Secret 管理。关键平衡：门禁过严会拖慢交付，按严重度分级（CI 拦 HIGH/CRITICAL，低危建单跟踪）。合规（等保/行业）必须前置而非事后。

> 📝 **精简总结**：DevSecOps=安全左移(早暴露低成本)；扫描=SAST(代码)/SCA(依赖)/DAST(运行)/镜像/IaC；治理=SBOM+策略即代码(OPA)+门禁；运行时=RBAC/PodSecurity/网络策略/Secret；注意=门禁分级/依赖递归/镜像必扫/最小权限/合规前置。

---

> 📝 **精简总结（全文）**：本文档系统梳理 DevOps 与云原生 6 大域——容器化（Docker 分层/多阶段/非 root/扫描）、Kubernetes（Pod/Deployment/Service/探针/资源限额/HPA）、CI/CD（流水线/GitOps/金丝雀/不可变制品）、可观测性（Metrics/Logs/Traces + RED + Prometheus）、IaC（Terraform/Ansible/状态文件/plan）、DevSecOps（SAST/SCA/镜像扫描/OPA/RBAC）。每域按"概述→核心特性→常用用法→注意事项"展开，附深度解析。学习建议：先 Docker 与 CI/CD 上手，再深入 K8s 与可观测性，最后以 IaC 与 DevSecOps 闭环安全与可复现。

---

## 相关笔记

- [[Vue3+TypeScript核心知识点总结_优化版]]
- [[算法与数据结构知识点完整整合大全_优化版]]
- [[设计模式知识点系统梳理_优化版]]
