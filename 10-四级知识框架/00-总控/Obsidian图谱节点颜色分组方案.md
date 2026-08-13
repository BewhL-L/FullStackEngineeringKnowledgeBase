---
title: Obsidian 图谱节点颜色分组方案（全量·分级）
tags: [Obsidian, 图谱, 配色, 可视化, 效率工具]
created: 2026-08-13
updated: 2026-08-13
---

# 🎨 Obsidian 图谱节点颜色分组方案（全量·分级）

> 覆盖**全部 12 个知识大类 + 各核心子分类**的分级配色规则。同一大类共用一个色相家族（看到颜色即知领域），
> 子分类靠明暗/饱和度拉开，保证图谱可视化时**区分度清晰、逻辑对应、无遗漏**。
> **适用版本**：Obsidian 1.4+ ｜ **主题**：深色主题优先。

---

## 一、设计原则

- **色相家族制**：每个大类一种基色（hue），其下子分类均为该 hue 的明暗/饱和度变体 → “逻辑对应”。
- **库内一致**：`10-四级知识框架` 下的子文件夹与顶层同名大类共用同一色相（如 Python 全栈无论在哪都是蓝），跨库一眼可辨。
- **区分度**：12 个大类基色在色环上尽量分散（相邻色相差 ≥ 25°）；子分类靠明度阶梯区分，深色背景下均可见。
- **两种上色方式**：
  - **文件夹（path）**：零维护，放进对应文件夹自动上色——适用于 `10-四级知识框架/*` 与 12 个大类根目录。
  - **标签（tag）**：一篇笔记可多色、可跨文件夹细分——适用于**扁平概要目录**（01~09 的 `.md` 文件无法用 path 再细分），需给笔记加 `tag:大类/子类`。

```
色环分布（相邻大类色相差≥25°）：
  绿(142°)──前端   蓝(217°)──Python   红(0°)──Java后端
      │                    │                │
  青(190°)──数据缓存   靛(245°)──云原生   橙(25°)──分布式
      │                                    │
  黄(48°)──通用工具   紫(280°)──AI   粉(330°)──知识管理
      │                                    │
  石板灰──综合/基础   品红(300°)──四级框架枢纽   蓝绿(170°)──项目实战
```

---

## 二、知识大类配色总表（12 个主色）

| 序号 | 知识大类 | 主色 | 色值 | 色系 | 图谱查询（大类根） |
|------|----------|------|------|------|--------------------|
| 01 | 00-综合导航 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#64748B;vertical-align:middle;margin-right:6px"></span> | `#64748B` | 综合导航 / 元知识 | `path:00-综合导航` |
| 02 | 01-前端开发 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#22C55E;vertical-align:middle;margin-right:6px"></span> | `#22C55E` | 前端开发 | `path:01-前端开发` |
| 03 | 02-后端开发 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#EF4444;vertical-align:middle;margin-right:6px"></span> | `#EF4444` | 后端开发 · Java 体系 | `path:02-后端开发` |
| 04 | 03-数据库与缓存 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#06B6D4;vertical-align:middle;margin-right:6px"></span> | `#06B6D4` | 数据库与缓存 | `path:03-数据库与缓存` |
| 05 | 04-分布式与中间件 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#F97316;vertical-align:middle;margin-right:6px"></span> | `#F97316` | 分布式与中间件 | `path:04-分布式与中间件` |
| 06 | 05-云原生与运维 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#6366F1;vertical-align:middle;margin-right:6px"></span> | `#6366F1` | 云原生与运维 | `path:05-云原生与运维` |
| 07 | 06-计算机基础 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#475569;vertical-align:middle;margin-right:6px"></span> | `#475569` | 计算机基础 | `path:06-计算机基础` |
| 08 | 07-通用工具 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#EAB308;vertical-align:middle;margin-right:6px"></span> | `#EAB308` | 通用工具 | `path:07-通用工具` |
| 09 | 08-Python全栈 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#3B82F6;vertical-align:middle;margin-right:6px"></span> | `#3B82F6` | Python 全栈 | `path:08-Python全栈` |
| 10 | 09-AI与效率工具 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#A855F7;vertical-align:middle;margin-right:6px"></span> | `#A855F7` | AI 与效率工具 | `path:09-AI与效率工具` |
| 11 | 10-四级知识框架 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#D946EF;vertical-align:middle;margin-right:6px"></span> | `#D946EF` | 四级知识框架 | `path:10-四级知识框架` |
| 12 | 99-项目实战 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#14B8A6;vertical-align:middle;margin-right:6px"></span> | `#14B8A6` | 项目实战 | `path:99-项目实战` |

> 注：实际图谱里 `10-四级知识框架` 的主色（品红）会被其下 11 个子文件夹的**领域色**（更具体、排在前面）覆盖，
> 仅 `00-总控` 等未单独归类的文件才显示品红。

---

## 三、核心子分类分级配色（按层级）

> 格式：**子分类 | 颜色色块 | 色值 | 图谱查询**。文件夹类用 `path`，扁平文件类用 `tag`（需给笔记打标签）。

### 00-综合导航 · 综合导航 / 元知识（MOC·模板·规则·工作流·索引）

| 核心子分类 | 颜色 | 色值 | 图谱查询 |
|------------|------|------|----------|
| 全局导航 MOC 枢纽 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#64748B;vertical-align:middle;margin-right:6px"></span> | `#64748B` | `path:00-综合导航` |
| 模板库 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#94A3B8;vertical-align:middle;margin-right:6px"></span> | `#94A3B8` | `tag:导航/模板` |
| 规则与规范 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#475569;vertical-align:middle;margin-right:6px"></span> | `#475569` | `tag:导航/规则` |
| 工作流 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#CBD5E1;vertical-align:middle;margin-right:6px"></span> | `#CBD5E1` | `tag:导航/工作流` |
| 标签索引 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#334155;vertical-align:middle;margin-right:6px"></span> | `#334155` | `tag:导航/索引` |

### 01-前端开发 · 前端开发（JS / TS / Vue3 / CSS / 工程化）

| 核心子分类 | 颜色 | 色值 | 图谱查询 |
|------------|------|------|----------|
| JavaScript 核心 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#16A34A;vertical-align:middle;margin-right:6px"></span> | `#16A34A` | `tag:前端/JS` |
| TypeScript（Agent/AIGC） | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#22C55E;vertical-align:middle;margin-right:6px"></span> | `#22C55E` | `tag:前端/TS` |
| Vue3 核心与快速上手 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#4ADE80;vertical-align:middle;margin-right:6px"></span> | `#4ADE80` | `tag:前端/Vue3` |
| Vue3 AI Agent 前端集成 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#86EFAC;vertical-align:middle;margin-right:6px"></span> | `#86EFAC` | `tag:前端/Vue3Agent` |
| Vue3 AIGC 前端应用 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#BBF7D0;vertical-align:middle;margin-right:6px"></span> | `#BBF7D0` | `tag:前端/Vue3AIGC` |
| Element Plus 组件库 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#15803D;vertical-align:middle;margin-right:6px"></span> | `#15803D` | `tag:前端/ElementPlus` |
| CSS 进阶 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#065F46;vertical-align:middle;margin-right:6px"></span> | `#065F46` | `tag:前端/CSS` |
| 前端工程化 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#10B981;vertical-align:middle;margin-right:6px"></span> | `#10B981` | `tag:前端/工程化` |

### 02-后端开发 · 后端开发 · Java 体系（Spring / 并发 / 设计模式）

| 核心子分类 | 颜色 | 色值 | 图谱查询 |
|------------|------|------|----------|
| Java 整合大全 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#EF4444;vertical-align:middle;margin-right:6px"></span> | `#EF4444` | `tag:后端/Java` |
| Java AI Agent 开发 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#F87171;vertical-align:middle;margin-right:6px"></span> | `#F87171` | `tag:后端/JavaAgent` |
| Java AIGC 应用 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#FCA5A5;vertical-align:middle;margin-right:6px"></span> | `#FCA5A5` | `tag:后端/JavaAIGC` |
| Spring Boot | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#DC2626;vertical-align:middle;margin-right:6px"></span> | `#DC2626` | `tag:后端/SpringBoot` |
| Spring Cloud 微服务 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#B91C1C;vertical-align:middle;margin-right:6px"></span> | `#B91C1C` | `tag:后端/SpringCloud` |
| Spring 原理 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#991B1B;vertical-align:middle;margin-right:6px"></span> | `#991B1B` | `tag:后端/Spring原理` |
| MyBatis-Plus | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#7F1D1D;vertical-align:middle;margin-right:6px"></span> | `#7F1D1D` | `tag:后端/MyBatis` |
| 并发编程 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#FCA5A5;vertical-align:middle;margin-right:6px"></span> | `#FCA5A5` | `tag:后端/并发` |
| 设计模式 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#FECACA;vertical-align:middle;margin-right:6px"></span> | `#FECACA` | `tag:后端/设计模式` |

### 03-数据库与缓存 · 数据库与缓存（MySQL / Redis / Mongo / ES）

| 核心子分类 | 颜色 | 色值 | 图谱查询 |
|------------|------|------|----------|
| MySQL | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#0891B2;vertical-align:middle;margin-right:6px"></span> | `#0891B2` | `tag:数据/MySQL` |
| Redis | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#06B6D4;vertical-align:middle;margin-right:6px"></span> | `#06B6D4` | `tag:数据/Redis` |
| MongoDB | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#67E8F9;vertical-align:middle;margin-right:6px"></span> | `#67E8F9` | `tag:数据/MongoDB` |
| Elasticsearch | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#22D3EE;vertical-align:middle;margin-right:6px"></span> | `#22D3EE` | `tag:数据/ES` |

### 04-分布式与中间件 · 分布式与中间件（微服务 / MQ / 事务 / 锁）

| 核心子分类 | 颜色 | 色值 | 图谱查询 |
|------------|------|------|----------|
| 微服务核心组件 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#EA580C;vertical-align:middle;margin-right:6px"></span> | `#EA580C` | `tag:分布/微服务` |
| 消息队列深度 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#F97316;vertical-align:middle;margin-right:6px"></span> | `#F97316` | `tag:分布/MQ` |
| 分布式事务 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#FB923C;vertical-align:middle;margin-right:6px"></span> | `#FB923C` | `tag:分布/事务` |
| 分布式锁 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#FDBA74;vertical-align:middle;margin-right:6px"></span> | `#FDBA74` | `tag:分布/锁` |

### 05-云原生与运维 · 云原生与运维（Docker / K8s / Linux / Nginx / Mesh）

| 核心子分类 | 颜色 | 色值 | 图谱查询 |
|------------|------|------|----------|
| Docker | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#6366F1;vertical-align:middle;margin-right:6px"></span> | `#6366F1` | `tag:运维/Docker` |
| Kubernetes | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#4F46E5;vertical-align:middle;margin-right:6px"></span> | `#4F46E5` | `tag:运维/K8s` |
| Linux 常用命令 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#818CF8;vertical-align:middle;margin-right:6px"></span> | `#818CF8` | `tag:运维/Linux` |
| Nginx | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#A5B4FC;vertical-align:middle;margin-right:6px"></span> | `#A5B4FC` | `tag:运维/Nginx` |
| Service Mesh | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#C7D2FE;vertical-align:middle;margin-right:6px"></span> | `#C7D2FE` | `tag:运维/Mesh` |

### 06-计算机基础 · 计算机基础（HTTP / JVM / 算法 / 计网OS）

| 核心子分类 | 颜色 | 色值 | 图谱查询 |
|------------|------|------|----------|
| HTTP 协议深度 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#475569;vertical-align:middle;margin-right:6px"></span> | `#475569` | `tag:基础/HTTP` |
| JVM | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#334155;vertical-align:middle;margin-right:6px"></span> | `#334155` | `tag:基础/JVM` |
| 数据结构与算法 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#64748B;vertical-align:middle;margin-right:6px"></span> | `#64748B` | `tag:基础/算法` |
| 计网 OS 八股 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#1E293B;vertical-align:middle;margin-right:6px"></span> | `#1E293B` | `tag:基础/计网OS` |

### 07-通用工具 · 通用工具（Git 版本控制）

| 核心子分类 | 颜色 | 色值 | 图谱查询 |
|------------|------|------|----------|
| Git 版本控制 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#EAB308;vertical-align:middle;margin-right:6px"></span> | `#EAB308` | `tag:工具/Git` |
| 其他 CLI / 效率脚本 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#FDE047;vertical-align:middle;margin-right:6px"></span> | `#FDE047` | `tag:工具/CLI` |

### 08-Python全栈 · Python 全栈（语言 / Web / 数据 / 部署）

| 核心子分类 | 颜色 | 色值 | 图谱查询 |
|------------|------|------|----------|
| 语言基础与进阶 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#2563EB;vertical-align:middle;margin-right:6px"></span> | `#2563EB` | `tag:Py/语言` |
| Web 开发框架 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#3B82F6;vertical-align:middle;margin-right:6px"></span> | `#3B82F6` | `tag:Py/Web` |
| 数据库与缓存 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#60A5FA;vertical-align:middle;margin-right:6px"></span> | `#60A5FA` | `tag:Py/数据` |
| 中间件与异步任务 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#93C5FD;vertical-align:middle;margin-right:6px"></span> | `#93C5FD` | `tag:Py/异步` |
| 性能优化 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#1D4ED8;vertical-align:middle;margin-right:6px"></span> | `#1D4ED8` | `tag:Py/性能` |
| 安全防护 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#BFDBFE;vertical-align:middle;margin-right:6px"></span> | `#BFDBFE` | `tag:Py/安全` |
| 接口设计与文档 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#7DD3FC;vertical-align:middle;margin-right:6px"></span> | `#7DD3FC` | `tag:Py/接口` |
| 测试工程 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#DBEAFE;vertical-align:middle;margin-right:6px"></span> | `#DBEAFE` | `tag:Py/测试` |
| 前端集成 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#60A5FA;vertical-align:middle;margin-right:6px"></span> | `#60A5FA` | `tag:Py/前端` |
| 部署运维 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#1E40AF;vertical-align:middle;margin-right:6px"></span> | `#1E40AF` | `tag:Py/部署` |

### 09-AI与效率工具 · AI 与效率工具（Agent / Prompt / 大模型 / Obsidian）

| 核心子分类 | 颜色 | 色值 | 图谱查询 |
|------------|------|------|----------|
| AI Agent 核心概念与架构 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#A855F7;vertical-align:middle;margin-right:6px"></span> | `#A855F7` | `tag:AI/Agent核心` |
| AI Agent 开发框架 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#C084FC;vertical-align:middle;margin-right:6px"></span> | `#C084FC` | `tag:AI/Agent框架` |
| AI Agent 实战与能力优化 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#D8B4FE;vertical-align:middle;margin-right:6px"></span> | `#D8B4FE` | `tag:AI/Agent实战` |
| Prompt 工程 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#7E22CE;vertical-align:middle;margin-right:6px"></span> | `#7E22CE` | `tag:AI/Prompt` |
| 生成式 AI 原理与应用 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#9333EA;vertical-align:middle;margin-right:6px"></span> | `#9333EA` | `tag:AI/生成式` |
| 主流大模型与 AI 工具 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#6B21A8;vertical-align:middle;margin-right:6px"></span> | `#6B21A8` | `tag:AI/大模型` |
| Obsidian 软件基础与核心插件 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#E9D5FF;vertical-align:middle;margin-right:6px"></span> | `#E9D5FF` | `tag:AI/Obsidian基础` |
| Obsidian 知识管理方法论 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#F3E8FF;vertical-align:middle;margin-right:6px"></span> | `#F3E8FF` | `tag:AI/Obsidian方法` |

### 10-四级知识框架 · 四级知识框架（原子笔记枢纽 · 子分类继承领域色相）

| 核心子分类 | 颜色 | 色值 | 图谱查询 |
|------------|------|------|----------|
| 00-总控（索引/方案） | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#E2E8F0;vertical-align:middle;margin-right:6px"></span> | `#E2E8F0` | `path:10-四级知识框架/00-总控` |
| 01-Python全栈 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#3B82F6;vertical-align:middle;margin-right:6px"></span> | `#3B82F6` | `path:10-四级知识框架/01-Python全栈` |
| 02-Java全栈 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#EF4444;vertical-align:middle;margin-right:6px"></span> | `#EF4444` | `path:10-四级知识框架/02-Java全栈` |
| 03-Vue3TS前端 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#22C55E;vertical-align:middle;margin-right:6px"></span> | `#22C55E` | `path:10-四级知识框架/03-Vue3TS前端` |
| 04-AIGC与Obsidian | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#C084FC;vertical-align:middle;margin-right:6px"></span> | `#C084FC` | `path:10-四级知识框架/04-AIGC与Obsidian` |
| 05-CS基础 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#475569;vertical-align:middle;margin-right:6px"></span> | `#475569` | `path:10-四级知识框架/05-CS基础` |
| 06-AI工程化 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#7C3AED;vertical-align:middle;margin-right:6px"></span> | `#7C3AED` | `path:10-四级知识框架/06-AI工程化` |
| 07-DevOps | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#6366F1;vertical-align:middle;margin-right:6px"></span> | `#6366F1` | `path:10-四级知识框架/07-DevOps` |
| 08-知识管理方法论 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#EC4899;vertical-align:middle;margin-right:6px"></span> | `#EC4899` | `path:10-四级知识框架/08-知识管理方法论` |
| 09-效率工具链 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#F59E0B;vertical-align:middle;margin-right:6px"></span> | `#F59E0B` | `path:10-四级知识框架/09-效率工具链` |
| 10-项目实战 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#14B8A6;vertical-align:middle;margin-right:6px"></span> | `#14B8A6` | `path:10-四级知识框架/10-项目实战` |

### 99-项目实战 · 项目实战（案例 / MOC / 复盘）

| 核心子分类 | 颜色 | 色值 | 图谱查询 |
|------------|------|------|----------|
| 项目实战总览 MOC | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#14B8A6;vertical-align:middle;margin-right:6px"></span> | `#14B8A6` | `path:99-项目实战` |
| 实战案例集（RAG/电商/客服…） | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#0D9488;vertical-align:middle;margin-right:6px"></span> | `#0D9488` | `tag:实战/案例` |
| 项目复盘与模板 | <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#5EEAD4;vertical-align:middle;margin-right:6px"></span> | `#5EEAD4` | `tag:实战/复盘` |

---

## 四、Obsidian 图谱配置（直接可用）

### 4.1 自动写入 `graph.json`（已生成）

本方案已自动写入 vault 的 `.obsidian/graph.json` → `colorGroups`，**打开/刷新图谱即生效**。
生成规则：
1. 保留原 `file:Home`、`tag:MOC`、`tag:面试`、`path:Inbox` 高亮组（枢纽/面试笔记统一高亮，不被大类色覆盖）。
2. 先写**更具体**的组（四级框架子文件夹 11 个 + 扁平目录子分类 tag 组），后写**大类根目录** 12 个——Obsidian 自上而下匹配，具体优先。

### 4.2 手动检查 / 重配步骤

1. 打开图谱视图（`Ctrl/Cmd + G`）；点右上角 ⚙️ → **颜色组（Color groups）**。
2. 确认每组 `查询` 与 `颜色` 与第三节一致；顺序：**具体组在上，大类组在下**。
3. 扁平概要目录（01~09）的子分类若未显示细分色，说明笔记缺 `tag:大类/子类`，用 Templater 模板在新建时自动打标签即可。

---

## 五、维护建议

1. **新笔记**：用模板自动加 `tag:大类/子类`，扁平目录子分类才能自动上色。
2. **季度审查**：在图谱搜索 `-path:10-四级知识框架 -tag:MOC` 看是否有未归类孤岛，补标签。
3. **跨库一致**：Python/Java/前端/AI/知识管理 等在 `10-四级知识框架` 与顶层目录共用同色相，勿改其一而漏改另一。
4. **性能**：节点 > 500 时关闭动画类 CSS；大类色足够区分，无需给每个叶子 notes 单独配色。

> 生成覆盖：12 大类、73 个核心子分类，全量无遗漏。

[[10-四级知识框架/00-总控/四级框架总索引|← 返回四级框架总索引]] | [[Home|🏠 返回首页]]