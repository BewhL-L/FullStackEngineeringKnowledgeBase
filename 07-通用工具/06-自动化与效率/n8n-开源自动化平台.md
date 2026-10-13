---
title: n8n-开源自动化平台
tags: [n8n, 自动化, 工作流, 低代码, Zapier替代, 自托管, 原子笔记]
category: 通用工具
created: 2026-08-12
updated: 2026-09-01
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: []
aliases: [n8n-开源自动化平台]
---



# n8n-开源自动化平台

> **文档说明**：系统讲解 n8n 开源工作流自动化平台，包括安装部署、核心概念、常用节点、工作流设计、表达式与数据转换、错误处理、自定义节点开发、API/Webhook、AI 集成，以及最佳实践和常见问题。
>
> **适用人群**：全栈开发者、运维工程师、产品经理、需要构建自动化工作流的开发者
>
> **前置知识**：[[Docker容器化实战]]、[[API设计最佳实践]]、[[Webhook与事件驱动架构]]

---

## 一、概述

### 1. 什么是 n8n

```text
n8n（nodemation）：
- 开源的工作流自动化平台
- 可视化拖拽编排，连接 400+ 应用和服务
- 可自托管，数据完全可控
- 支持自定义节点开发
- 公平代码（Fair-code）许可：可自托管免费，云服务收费

核心特点：
1. 可视化编辑器：拖拽节点，连线编排工作流
2. 自托管：Docker 一键部署，数据在自己服务器
3. 可扩展：自定义节点、自定义函数（JS/Python）
4. 灵活触发：Webhook、定时、事件、手动
5. 数据转换：内置表达式、代码节点、数据操作
6. 错误处理：重试、回退、错误工作流
7. 版本管理：工作流版本控制和回滚

n8n vs Zapier/Make：
- n8n：开源、自托管、免费（自托管）、可定制、技术向
- Zapier：SaaS、易用、贵、生态丰富、非技术向
- Make（Integromat）：SaaS、可视化强、中等价格、功能丰富
```

### 2. 应用场景

```text
n8n 典型应用场景：

1. 数据同步
   - 数据库 ↔ 表格（Airtable/Google Sheets）
   - CRM ↔ 邮件营销
   - 多系统数据同步

2. 通知与告警
   - 系统监控 → 飞书/Slack/钉钉通知
   - 表单提交 → 邮件/SMS 通知
   - 价格监控 → 告警

3. 内容自动化
   - RSS → 社交媒体发布
   - AI 生成内容 → 审核 → 发布
   - 文档转换和处理

4. 业务流程
   - 审批流程（请假/报销）
   - 客户入职流程
   - 订单处理流程

5. AI 工作流
   - 文档 → 向量库 → RAG 问答
   - 多模型协作（生成→审核→优化）
   - AI Agent 编排

6. DevOps 自动化
   - CI/CD 通知和审批
   - 服务器监控和自动恢复
   - 日志分析和告警
```

---

## 二、安装部署

### 1. Docker 部署（推荐）

```bash
# 快速启动
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# 访问 http://localhost:5678
```

```yaml
# docker-compose.yml（生产推荐）
version: "3.7"

services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - TZ=Asia/Shanghai
      - N8N_HOST=n8n.example.com
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://n8n.example.com/
      - GENERIC_TIMEZONE=Asia/Shanghai
      # 数据库
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=n8n_password
      # 安全
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your_secure_password
      # 队列模式（高并发）
      - EXECUTIONS_MODE=queue
      - QUEUE_BULL_REDIS_HOST=redis
      - QUEUE_BULL_REDIS_PORT=6379
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8n_password
      - POSTGRES_DB=n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

volumes:
  n8n_data:
  postgres_data:
  redis_data:
```

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f n8n

# 升级
docker-compose pull
docker-compose up -d
```

### 2. 部署模式

```text
n8n 部署模式：

1. 单实例模式（默认）
   - 所有进程在一个容器
   - 适合小规模、低并发
   - 简单，资源占用少

2. 队列模式（Queue Mode）
   - 主进程 + 多个 Worker 进程
   - Redis 作为队列
   - 适合高并发、大规模
   - Worker 可以水平扩展

3. 多租户（n8n Cloud）
   - 官方云服务
   - 无需运维
   - 按用户收费

队列模式架构：
┌─────────────┐
│   n8n main  │ ← 用户交互、API、Webhook
└──────┬──────┘
       │ 任务入队
┌──────▼──────┐
│    Redis    │ ← 任务队列
└──────┬──────┘
       │ 消费任务
┌──────▼──────┐
│ n8n worker  │ ← 执行工作流（可多个）
└─────────────┘
       │
┌──────▼──────┐
│  PostgreSQL │ ← 数据存储
└─────────────┘
```

### 3. 反向代理配置

```nginx
# Nginx 反向代理
server {
    listen 443 ssl http2;
    server_name n8n.example.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 600s;
    }
}
```

---

## 三、核心概念

### 1. 节点（Node）

```text
节点是 n8n 的基本构建块：
- 每个节点执行一个特定操作
- 节点之间通过连线传递数据
- 节点有输入和输出

节点类型：
1. 触发节点（Trigger）
   - 启动工作流
   - Webhook、定时、事件触发、手动
   - 没有输入，只有输出

2. 常规节点（Regular）
   - 执行具体操作
   - API 调用、数据转换、文件操作
   - 有输入和输出

3. 工具节点（Utility）
   - IF/Switch：条件分支
   - Merge：合并数据
   - Split Out：拆分数据
   - Set：设置数据
   - Code：自定义代码

4. 辅助节点（Helper）
   - No Operation：空操作（调试用）
   - Wait：等待
   - Execute Command：执行命令

节点参数：
- 每个节点有特定的参数配置
- 可以使用表达式动态设置参数
- 可以引用前面节点的输出数据
```

### 2. 工作流（Workflow）

```text
工作流是节点的有向图：
- 由多个节点和连线组成
- 从触发节点开始
- 数据沿连线流动
- 可以有分支和合并

工作流状态：
- 未激活（Inactive）：保存但不运行
- 已激活（Active）：触发节点生效，自动运行
- 执行中（Running）：正在执行

工作流执行：
- 手动执行：点击 Execute 按钮
- 自动执行：触发节点触发
- 测试执行：单节点测试

数据结构：
- n8n 中数据以 items 数组形式传递
- 每个 item 是一个 JSON 对象
- 节点处理 items，输出新的 items

示例数据流：
Trigger → [item1, item2] → NodeA → [item1', item2'] → NodeB
```

### 3. 凭证（Credentials）

```text
凭证用于连接外部服务：
- API Key、OAuth、用户名密码等
- 加密存储在数据库中
- 可以在多个工作流中复用
- 支持权限控制（谁可以使用）

凭证类型：
1. API Key：最简单，直接传入 API Key
2. OAuth2：授权码模式，适合第三方应用
3. Basic Auth：用户名密码
4. 自定义：其他认证方式

凭证管理：
- 创建：在 Credentials 页面添加
- 测试：连接测试
- 共享：与团队成员共享
- 轮换：定期更新密钥
```

---

## 四、常用节点

### 1. 触发节点

```text
常用触发节点：

1. Webhook
   - HTTP 请求触发工作流
   - 支持 GET/POST/PUT/DELETE
   - 可以接收 JSON/表单/文件
   - 用于接收外部系统通知

2. Schedule Trigger
   - 定时触发（Cron 表达式）
   - 每分钟/小时/天/周/月
   - 用于定时任务

3. Manual Trigger
   - 手动点击触发
   - 用于测试和一次性任务

4. Event Trigger
   - 监听 n8n 内部事件
   - 工作流执行完成/失败

5. Form Trigger
   - 生成表单页面
   - 表单提交触发工作流
   - 用于简单的数据收集

6. Email Trigger（IMAP）
   - 接收邮件触发
   - 用于邮件自动化

7. RSS Feed Trigger
   - RSS 更新触发
   - 用于内容监控
```

### 2. 数据操作节点

```text
常用数据操作节点：

1. Set
   - 设置/修改 item 的字段
   - 可以添加、删除、重命名字段
   - 支持表达式

2. Code
   - 执行自定义 JavaScript/Python 代码
   - 完全控制数据转换
   - 可以调用外部库

3. IF
   - 条件分支
   - 满足条件走 true 分支，否则 false 分支
   - 支持多个条件

4. Switch
   - 多条件分支
   - 根据值路由到不同分支
   - 类似 switch-case

5. Merge
   - 合并多个分支的数据
   - 支持 append/merge/multiply 模式

6. Split Out
   - 将数组字段拆分为多个 item
   - 用于批量处理

7. Aggregate
   - 聚合数据（分组、求和、计数）
   - 类似 SQL GROUP BY

8. Edit Fields
   - 图形化编辑字段
   - 添加/删除/重命名/修改
```

### 3. 集成节点

```text
常用集成节点（400+）：

通信协作：
- Slack、飞书、钉钉、企业微信
- Gmail、Outlook、SMTP
- Telegram、Discord、WhatsApp

数据存储：
- PostgreSQL、MySQL、MongoDB
- Airtable、Google Sheets
- Redis、Elasticsearch

开发工具：
- GitHub、GitLab
- Jira、Trello、Notion
- Jenkins、GitLab CI

云服务：
- AWS（S3、Lambda、SES）
- Google Cloud（Storage、Pub/Sub）
- Azure（Blob Storage、Functions）

AI/ML：
- OpenAI、Anthropic、Google AI
- Hugging Face、Replicate
- Pinecone、Weaviate、Milvus

支付电商：
- Stripe、PayPal
- Shopify、WooCommerce
- 支付宝、微信支付

社交媒体：
- Twitter/X、Facebook、Instagram
- LinkedIn、YouTube
- 小红书、抖音
```

---

## 五、表达式与数据转换

### 1. 表达式语法

```json
n8n 表达式语法（基于 JavaScript）：

基本语法：
{{ 表达式 }}

引用前面节点的数据：
{{ $json.fieldName }}           // 当前 item 的字段
{{ $node["节点名"].json.field }}  // 指定节点的输出
{{ $input.item.json.field }}     // 输入 item

常用变量：
- $json：当前 item 的 JSON 数据
- $node：所有节点的输出
- $input：输入数据
- $env：环境变量
- $now：当前时间
- $parameter：节点参数

示例：
{{ $json.name }}                    // 取 name 字段
{{ $json.age * 2 }}                // 计算
{{ $json.email.toLowerCase() }}    // 方法调用
{{ $now.toFormat('yyyy-MM-dd') }}  // 日期格式化
{{ $node["HTTP Request"].json.data }}  // 引用 HTTP 节点结果
{{ $env.SECRET_KEY }}              // 环境变量
```

### 2. Code 节点

```javascript
// Code 节点（JavaScript）
// 输入：items 数组
// 输出：返回新的 items 数组

// 示例1：简单转换
return items.map(item => ({
  json: {
    ...item.json,
    fullName: `${item.json.firstName} ${item.json.lastName}`,
    ageGroup: item.json.age >= 18 ? 'adult' : 'minor'
  }
}));

// 示例2：过滤
return items.filter(item => item.json.status === 'active');

// 示例3：聚合
const total = items.reduce((sum, item) => sum + item.json.amount, 0);
return [{ json: { total, count: items.length } }];

// 示例4：调用 API（需要 await）
const results = [];
for (const item of items) {
  const response = await this.helpers.httpRequest({
    method: 'GET',
    url: `https://api.example.com/users/${item.json.userId}`
  });
  results.push({ json: { ...item.json, userData: response } });
}
return results;

// 示例5：错误处理
try {
  const result = await doSomething();
  return [{ json: { success: true, result } }];
} catch (error) {
  return [{ json: { success: false, error: error.message } }];
}
```

```python
# Code 节点（Python，n8n 支持 Python）
# 输入：_input 包含 items
# 输出：返回列表

# 示例：数据转换
result = []
for item in _input:
    data = item.json
    data['full_name'] = f"{data['first_name']} {data['last_name']}"
    result.append({'json': data})
return result
```

---

## 六、错误处理

### 1. 节点级错误处理

```text
节点错误处理选项：
1. Continue On Fail（失败继续）
   - 节点失败不中断工作流
   - 错误信息传递到下一个节点
   - 适合非关键步骤

2. Retry On Fail（失败重试）
   - 失败后自动重试
   - 可设置重试次数和间隔
   - 适合临时故障（网络抖动）

3. Error Workflow（错误工作流）
   - 工作流失败时触发另一个工作流
   - 用于统一错误处理和通知
   - 可以获取错误详情

4. 节点输出错误
   - 节点有 error 输出端口
   - 失败时走 error 分支
   - 可以针对性处理
```

### 2. 错误工作流示例

```text
错误处理工作流设计：

主工作流失败 → 触发错误工作流 →
  1. 获取错误详情（工作流名、节点名、错误信息）
  2. 发送通知（飞书/Slack/邮件）
  3. 记录错误日志（数据库/日志服务）
  4. 根据错误类型决定是否重试
  5. 严重错误触发告警
```

```javascript
// 错误通知 Code 节点
const error = $input.first().json;

return [{
  json: {
    workflow: error.workflow.name,
    node: error.execution.lastNodeExecuted,
    error: error.execution.error.message,
    time: new Date().toISOString(),
    severity: error.execution.error.message.includes('timeout') ? 'warning' : 'critical'
  }
}];
```

### 3. 重试策略

```text
重试策略配置：

1. 固定间隔
   - 每次重试间隔相同
   - 简单，适合快速恢复

2. 指数退避
   - 间隔逐次翻倍（1s, 2s, 4s, 8s...）
   - 避免雪崩效应
   - 推荐使用

3. 最大重试次数
   - 通常 3-5 次
   - 避免无限重试

4. 可重试错误判断
   - 网络错误：可重试
   - 认证错误：不可重试
   - 业务错误：不可重试
   - 限流错误：可重试（等待更长时间）
```

---

## 七、自定义节点开发

### 1. 节点结构

```text
n8n 自定义节点：
- TypeScript/JavaScript 编写
- 继承 n8n-core 的 Node 类
- 定义参数、描述、执行逻辑
- 可以本地安装或发布到 npm

节点文件结构：
MyNode/
├── MyNode.node.ts      # 节点定义
├── MyNode.png          # 节点图标
└── package.json        # 包信息
```

```typescript
// MyNode.node.ts 示例
import { IExecuteFunctions, INodeExecutionData, INodeType, INodeTypeDescription } from 'n8n-workflow';

export class MyNode implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'My Custom Node',
    name: 'myNode',
    icon: 'file:MyNode.png',
    group: ['transform'],
    version: 1,
    description: '自定义节点示例',
    defaults: {
      name: 'My Node',
    },
    inputs: ['main'],
    outputs: ['main'],
    properties: [
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        options: [
          { name: 'Get', value: 'get' },
          { name: 'Create', value: 'create' },
        ],
        default: 'get',
      },
      {
        displayName: 'API Key',
        name: 'apiKey',
        type: 'string',
        default: '',
        required: true,
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const operation = this.getNodeParameter('operation', 0) as string;
    const apiKey = this.getNodeParameter('apiKey', 0) as string;

    const returnData: INodeExecutionData[] = [];

    for (let i = 0; i < items.length; i++) {
      try {
        if (operation === 'get') {
          // 执行 GET 操作
          const response = await this.helpers.httpRequest({
            method: 'GET',
            url: 'https://api.example.com/data',
            headers: { Authorization: `Bearer ${apiKey}` },
          });
          returnData.push({ json: response });
        } else if (operation === 'create') {
          // 执行 CREATE 操作
          const response = await this.helpers.httpRequest({
            method: 'POST',
            url: 'https://api.example.com/data',
            headers: { Authorization: `Bearer ${apiKey}` },
            body: items[i].json,
          });
          returnData.push({ json: response });
        }
      } catch (error) {
        if (this.continueOnFail()) {
          returnData.push({ json: { error: error.message }, itemIndex: i });
          continue;
        }
        throw error;
      }
    }

    return [returnData];
  }
}
```

### 2. 安装自定义节点

```bash
# 方式1：本地安装（开发测试）
# 将节点放到 ~/.n8n/custom/ 目录
mkdir -p ~/.n8n/custom
cp MyNode.node.js ~/.n8n/custom/

# 方式2：npm 包
# 发布到 npm 后安装
cd /usr/local/lib/node_modules/n8n
npm install n8n-nodes-mynode

# 方式3：Docker 挂载自定义节点
docker run -v ~/.n8n/custom:/home/node/.n8n/custom n8nio/n8n

# 重启 n8n 后节点生效
```

---

## 八、API 与 Webhook

### 1. REST API

```text
n8n 提供完整的 REST API：

认证：API Key（在 Settings → API 生成）

常用端点：
- GET /workflows：列出工作流
- POST /workflows：创建工作流
- GET /workflows/:id：获取工作流
- PUT /workflows/:id：更新工作流
- POST /workflows/:id/activate：激活工作流
- POST /workflows/:id/deactivate：停用工作流
- POST /workflows/:id/run：执行工作流
- GET /executions：列出执行记录
- GET /executions/:id：获取执行详情
- GET /credentials：列出凭证
```

```bash
# API 调用示例
# 获取工作流列表
curl -X GET "https://n8n.example.com/api/v1/workflows" \
  -H "X-N8N-API-KEY: your_api_key"

# 执行工作流
curl -X POST "https://n8n.example.com/api/v1/workflows/123/run" \
  -H "X-N8N-API-KEY: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"json": {"key": "value"}}]}'

# 创建工作流
curl -X POST "https://n8n.example.com/api/v1/workflows" \
  -H "X-N8N-API-KEY: your_api_key" \
  -H "Content-Type: application/json" \
  -d @workflow.json
```

### 2. Webhook 节点

```text
Webhook 节点：
- 生成一个 URL，外部系统可以调用
- 支持 GET/POST/PUT/DELETE/PATCH
- 可以接收 JSON、表单、文件
- 用于接收外部事件触发工作流

Webhook URL 格式：
- 测试 URL：http://n8n.example.com/webhook-test/<uuid>
- 生产 URL：http://n8n.example.com/webhook/<uuid>

响应配置：
- 立即响应：返回固定响应
- 等待工作流完成：返回工作流结果
- 自定义响应码和头

安全：
- 可以设置认证（Basic Auth/Header Auth）
- 可以限制 IP
- 可以验证签名（Webhook 签名验证）
```

```javascript
// Webhook 响应节点（Respond to Webhook）
// 可以自定义响应内容
return [{
  json: {
    status: 'success',
    message: '数据已接收',
    data: $input.first().json
  }
}];
// 响应码：200
// 响应头：Content-Type: application/json
```

---

## 九、AI 集成

### 1. OpenAI 节点

```text
n8n OpenAI 节点功能：
1. Chat：对话生成（GPT-4o、GPT-3.5-turbo）
2. Completion：文本补全
3. Embedding：文本向量化
4. Image：图像生成（DALL-E）
5. Audio：语音转文字（Whisper）
6. File：文件管理
7. Fine-tune：微调管理
8. Model：模型列表

常用参数：
- Model：选择模型
- Messages：对话消息
- Temperature：随机性（0-2）
- Max Tokens：最大输出长度
- System Prompt：系统提示
```

### 2. AI 工作流示例

```json
示例1：文档问答 RAG 工作流

Webhook（接收问题）
  → HTTP Request（查询向量库）
  → OpenAI Chat（基于检索结果回答）
  → Respond to Webhook（返回答案）

Prompt 模板：
基于以下文档回答问题，如果文档中没有相关信息，请说"我不知道"。

文档：
{{ $node["向量查询"].json.results }}

问题：{{ $json.question }}

答案：
```

```text
示例2：内容生成工作流

Schedule Trigger（每天早上 8 点）
  → RSS Read（获取技术新闻）
  → Code（筛选和摘要）
  → OpenAI Chat（生成日报）
  → Slack（发送到频道）
  → Gmail（邮件发送给订阅者）
```

```text
示例3：多模型协作工作流

Webhook（接收写作需求）
  → OpenAI Chat（GPT-4o 生成初稿）
  → Anthropic Claude（审核和优化）
  → OpenAI Chat（最终润色）
  → Google Docs（保存文档）
  → Slack（通知完成）
```

### 3. AI Agent 编排

```text
n8n 作为 AI Agent 编排工具：

优势：
- 可视化编排 Agent 流程
- 400+ 工具节点直接可用
- 错误处理和重试
- 监控和日志
- 团队协作

Agent 工作流模式：
1. ReAct 模式：思考→行动→观察 循环
   - 用 IF 节点判断是否完成
   - 用 Merge 节点循环
   - 用 Code 节点解析 LLM 输出

2. 多 Agent 协作：
   - 不同 Agent 负责不同任务
   - Agent 之间通过 n8n 传递数据
   - 协调器 Agent 分配任务

3. 工具调用：
   - LLM 输出工具调用指令
   - Code 节点解析并调用对应 n8n 节点
   - 结果返回给 LLM
```

---

## 十、最佳实践

### 1. 工作流设计

- [ ] **单一职责**：每个工作流做一件事，复杂任务拆分为多个工作流
- [ ] **命名规范**：工作流和节点用清晰的命名（如「同步订单到ERP」）
- [ ] **注释说明**：复杂节点添加注释，说明用途和逻辑
- [ ] **模块化**：可复用的逻辑抽取为子工作流（Execute Workflow 节点）
- [ ] **错误处理**：关键节点配置重试，工作流配置错误通知
- [ ] **版本管理**：重要修改前复制备份，利用 n8n 版本功能
- [ ] **测试优先**：先用测试数据验证，再激活生产

### 2. 性能优化

- [ ] **批量处理**：尽量批量处理，减少节点调用次数
- [ ] **并行执行**：独立的分支可以并行执行（n8n 默认并行）
- [ ] **队列模式**：高并发场景使用队列模式，多 Worker 处理
- [ ] **数据精简**：只传递需要的字段，避免大对象在节点间传递
- [ ] **缓存结果**：不常变化的数据用缓存（Redis/数据库）
- [ ] **限流控制**：调用外部 API 时注意限流，用 Wait 节点间隔
- [ ] **资源限制**：配置 Worker 内存和 CPU 限制，避免单个工作流耗尽资源

### 3. 安全实践

- [ ] **凭证加密**：使用 n8n 凭证管理，不要明文写在节点参数中
- [ ] **访问控制**：配置 Basic Auth 或 SSO，限制 n8n 访问
- [ ] **HTTPS**：生产环境必须用 HTTPS
- [ ] **Webhook 安全**：Webhook 配置认证和签名验证
- [ ] **环境变量**：敏感信息用环境变量，不硬编码
- [ ] **定期备份**：定期备份 n8n 数据（工作流、凭证、执行记录）
- [ ] **审计日志**：开启审计日志，记录用户操作
- [ ] **网络隔离**：n8n 部署在内网，通过反向代理访问

### 4. 运维监控

- [ ] **健康检查**：监控 n8n 进程和 API 健康状态
- [ ] **执行监控**：监控工作流执行成功率、失败率
- [ ] **告警通知**：失败率高、执行时间长时发送告警
- [ ] **日志收集**：集中收集 n8n 日志（ELK/Loki）
- [ ] **资源监控**：监控 CPU、内存、磁盘、数据库连接
- [ ] **定期清理**：清理旧的执行记录，释放数据库空间
- [ ] **升级策略**：测试环境先升级，验证后再升级生产

---

## 十一、常见问题与排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **Webhook 无法访问** | 端口未开放/反向代理配置错 | 检查防火墙、Nginx 配置、WEBHOOK_URL 环境变量 |
| **工作流执行慢** | 节点多/外部API慢/数据量大 | 并行执行、批量处理、优化API调用、队列模式 |
| **内存溢出** | 数据量太大/Code节点内存泄漏 | 分批处理、限制数据量、增加Worker内存、优化Code |
| **凭证失效** | API Key过期/权限变更 | 更新凭证、检查权限、测试连接 |
| **数据传递错误** | 表达式写错/节点名不对 | 检查表达式、用 $node["节点名"] 引用、调试查看输出 |
| **循环不停止** | IF条件错误/无限循环 | 检查条件、设置最大迭代次数、用计数器 |
| **编码问题** | 中文乱码/特殊字符 | 设置 UTF-8、URL 编码、检查 Content-Type |
| **数据库连接失败** | 网络/凭证/驱动问题 | 检查网络、凭证、数据库版本、驱动版本 |
| **升级后报错** | 版本不兼容/数据迁移 | 查看升级日志、备份后升级、回滚到旧版本 |
| **Worker 不消费任务** | Redis连接错/Worker未启动 | 检查 Redis 连接、启动 Worker、查看 Worker 日志 |
| **执行记录太多** | 未配置清理/高频工作流 | 配置执行记录保留时间、定期清理、用数据库分区 |
| **自定义节点不显示** | 安装位置错/未重启/编译错 | 检查 custom 目录、重启 n8n、查看启动日志 |
| **OAuth 认证失败** | 回调URL错/凭证错 | 检查 OAuth 回调 URL、Client ID/Secret、权限范围 |
| **大文件处理失败** | 超时/内存/大小限制 | 增加超时、分批处理、增加内存、检查上传限制 |
| **并发请求被限流** | 外部API限流 | 限流控制、Wait 间隔、批量请求、降级策略 |
| **工作流丢失** | 未备份/数据库损坏 | 定期备份、恢复备份、检查数据库健康 |
| **表达式不生效** | 语法错/未用 {{}} | 检查表达式语法、用表达式预览、查看节点输入 |
| **SSL 证书错误** | 证书过期/自签名 | 更新证书、配置 CA 证书、NODE_TLS_REJECT_UNAUTHORIZED（仅测试） |
| **时间不正确** | 时区配置错 | 设置 GENERIC_TIMEZONE、容器时区、检查系统时间 |
| **节点参数太多** | 操作复杂/参数嵌套 | 拆分为多个节点、用子工作流、用 Code 节点简化 |

---

## 十二、关联笔记

### 自动化与效率
- [[Zapier自动化入门]] · [[Make-Integromat进阶]] · [[Power Automate实战]]
- [[密码管理器-Bitwarden]] · [[Obsidian-高效知识管理]]

### 开发与运维
- [[Docker容器化实战]] · [[CI-CD安全与凭据管理]] · [[Jenkins流水线实战]]
- [[API设计最佳实践]] · [[Webhook与事件驱动架构]]

### AI 集成
- [[大模型应用开发入门]] · [[Python-LangChain应用开发]] · [[AI产品实战框架-从0到1]]
- [[RAG检索增强生成]] · [[AI Agent设计与实现]]

### 导航
- [[MOC-通用工具]] · [[MOC-云原生与运维]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Docker容器化实战]] 部署基础 → 学习本文 n8n 自动化平台 → 实践 [[API设计最佳实践]] API 集成 → 研究 [[AI产品实战框架-从0到1]] AI 工作流 → 深入 [[Python-LangChain应用开发]] AI 开发 → 构建完整的自动化与 AI 编排能力。

---

## 🔗 关联笔记

- [[MOC-通用工具]] — 返回本分类知识地图，查看更多相关文档

## 📖 前置知识

- 无特殊前置知识要求，具备基础编程概念即可

## 🏷️ 相关标签

`#n8n` `#自动化` `#工作流` `#低代码` `#Zapier替代` `#自托管`

[[Home|🏠 返回首页]] · [[MOC-通用工具|📚 返回分类]]
