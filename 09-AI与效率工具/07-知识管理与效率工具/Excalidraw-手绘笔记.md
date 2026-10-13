---
title: Excalidraw-手绘笔记
tags: [AI应用, AI工程化, LLM]
category: AI与效率工具
created: 2026-08-13
updated: 2026-09-08
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 重要
pre: ["[[Obsidian-核心插件配置]]"]
aliases: [Excalidraw-手绘笔记, Excalidraw, 手绘笔记]
---

# Excalidraw 手绘笔记

> **文档说明**：系统讲解 Obsidian Excalidraw 插件的使用方法，涵盖手绘风格图表绘制、与 Markdown 笔记的集成、脚本自动化（Excalidraw Automate）、模板库、从文本生成图表、架构图/流程图/思维导图绘制、导出与共享、与 Canvas 的联动，含具体的快捷键、脚本代码、模板示例和最佳实践。
>
> **适用人群**：Obsidian 用户、需要在笔记中绘制架构图/流程图的技术人员、视觉化思考者
>
> **前置知识**：[[Obsidian-核心插件配置]]、[[Obsidian-Canvas画布用法]]、[[Obsidian-双向链接与图谱]]

---

## 一、概述

<div style="background:linear-gradient(135deg,#11998e,#38ef7d);border-radius:16px;padding:20px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#fff;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes highlight{0%,100%{box-shadow:0 0 0 rgba(255,255,255,0)}50%{box-shadow:0 0 20px rgba(255,255,255,.4)}}.hl-box{background:rgba(255,255,255,.2);border-radius:10px;padding:14px 18px;margin:10px 0;animation:highlight 3s ease-in-out infinite;border-left:4px solid rgba(255,255,255,.6)}.hl-formula{font-family:monospace;font-size:14px;text-align:center;background:rgba(0,0,0,.15);border-radius:8px;padding:12px;margin:10px 0}</style>
<div style="text-align:center;font-size:15px;font-weight:700;margin-bottom:14px;padding-bottom:10px;border-bottom:1.5px solid rgba(255,255,255,.22);letter-spacing:1px;text-shadow:0 1px 3px rgba(0,0,0,.12)">📌 Excalidraw 手绘笔记</div>
<div class="hl-box">系统讲解 Obsidian Excalidraw 插件的使用方法，涵盖手绘风格图表绘制、与 Markdown 笔记的集成、脚本自动化（Excalidraw Automate）、模板库、从文本生成图表、架构图/流程图/思维导图绘制、导出与共享、与 Canvas 的联动，含具体的快捷键、脚本代码、模板示...</div>
<div class="hl-formula">画布创建 → 图形绘制 → 文字标注 → 样式美化 → 导出嵌入</div>
<div style="font-size:13px;opacity:.9;margin-top:8px">💡 工具是手段，高效的知识管理才是目标</div>
</div>

> 🔍 **知识点深度解析**
>
> **作用**：Excalidraw 手绘笔记 是 Obsidian 知识管理体系中的重要工具/方法，解决知识采集、组织、检索和利用中的效率问题，适用于构建个人知识管理系统和提升工作效率。
>
> **原理**：通过插件扩展和工作流设计，将 Obsidian 从简单的笔记工具升级为强大的知识管理平台，结合自动化和 AI 能力实现知识的高效处理和价值挖掘。
>
> **用法要点**：① 先掌握基础配置再深入高级功能 ② 建立适合自己的工作流而非照搬他人方案 ③ 善用快捷键和模板提升操作效率 ④ 定期回顾和优化知识管理方法

**Excalidraw** 是一个开源的手绘风格绘图工具，Obsidian Excalidraw 插件将其深度集成到 Obsidian 中，允许在笔记内直接创建和编辑手绘风格的图表。与传统绘图工具不同，Excalidraw 的手绘风格让图表看起来更自然、更有温度，特别适合技术架构图、流程图、思维导图、概念图等场景。

### 1. Excalidraw 解决的问题

| 痛点 | 解决方案 |
|------|---------|
| 笔记中需要画图时要切换到外部工具 | 在 Obsidian 内直接创建和编辑，无需切换应用 |
| 传统图表（draw.io/Visio）风格生硬 | 手绘风格自然亲和，适合个人笔记和分享 |
| 图表与笔记内容分离，管理困难 | Excalidraw 绘图保存为 .excalidraw.md 文件，与笔记统一管理 |
| 重复绘制相似图表耗时 | 模板库 + 脚本自动化，一键生成标准图表 |
| 无法从文本快速生成图表 | Excalidraw Automate 脚本支持从 Markdown/JSON 生成图表 |
| 图表无法引用笔记内容 | 支持在图中嵌入 `[[]]` 双链，点击跳转到笔记 |

### 2. Excalidraw 核心能力

```mermaid
graph TB
    subgraph 绘图能力
        D1[基础图形<br/>矩形/圆/菱形/箭头]
        D2[手绘画笔<br/>自由绘制]
        D3[文本与便签]
        D4[连接线<br/>智能路由]
        D5[图标库<br/>内置+自定义]
    end

    subgraph Obsidian集成
        I1[.excalidraw.md 文件]
        I2[双链嵌入<br/>[[]]链接]
        I3[模板系统]
        I4[脚本自动化<br/>Excalidraw Automate]
    end

    subgraph 输出
        O1[导出 PNG/SVG]
        O2[复制为图片]
        O3[嵌入笔记]
        O4[分享链接]
    end

    D1 --> I1
    D2 --> I1
    I1 --> I2
    I1 --> I3
    I3 --> I4
    I1 --> O1
    I1 --> O2
```

### 3. Excalidraw vs Canvas vs 传统绘图

| 维度 | Excalidraw | Canvas | draw.io |
|------|-----------|--------|---------|
| **风格** | 手绘风 | 卡片式笔记 | 专业图表 |
| **用途** | 图表/架构图/流程图 | 笔记组织/头脑风暴 | 专业流程图/UML |
| **文件格式** | .excalidraw.md | .canvas | .drawio |
| **双链支持** | ✅ 图中可嵌入双链 | ✅ 原生 | ❌ |
| **脚本自动化** | ✅ Automate | 有限 | ❌ |
| **学习曲线** | 平缓 | 最平缓 | 中等 |
| **导出** | PNG/SVG | PNG | PNG/SVG/PDF |

---

---

> 💡 **深度讲解**：本节围绕，深入剖析其使用方法与实践技巧，帮助读者建立高效的知识管理工作流。
>
> **📝 精简总结**：本节介绍了，掌握这些内容是提升 Obsidian 使用效率的重要基础。

## 二、底层原理

### 1. Excalidraw 文件结构

Obsidian Excalidraw 将绘图保存为 Markdown 文件，包含 YAML frontmatter 和 JSON 绘图数据：

---
excalidraw-plugin: parsed
tags: [excalidraw]
---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==

## Text Elements
架构图 ^text-1

## Embedded Files

## Drawing
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "id": "rect-1",
      "type": "rectangle",
      "x": 100,
      "y": 100,
      "width": 200,
      "height": 100,
      "text": "用户端",
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#dbeafe",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100
```text
    }
  ],
```
  "appState": {"gridSize": null},
  "files": {}
}
```
```

这种设计使得 Excalidraw 文件可以被 Obsidian 的搜索、双链、标签系统索引。

### 2. Excalidraw Automate 脚本原理

Excalidraw Automate 是基于 JavaScript 的脚本系统，可以：
- 从模板创建标准图表
- 从选中的 Markdown 文本生成图表
- 批量操作图形元素
- 与 Dataview/Templater 联动

脚本通过 `ea` 对象访问 Excalidraw API，支持创建元素、设置样式、添加文本等操作。

---

---

> 💡 **深度讲解**：本节围绕，深入剖析其使用方法与实践技巧，帮助读者建立高效的知识管理工作流。
>
> **📝 精简总结**：本节介绍了，掌握这些内容是提升 Obsidian 使用效率的重要基础。

## 三、实操

### 1. 基础绘图快捷键

| 快捷键 | 功能 |
|--------|------|
| `1` / `R` | 矩形工具 |
| `2` / `D` | 菱形工具 |
| `3` / `O` | 椭圆工具 |
| `4` / `L` | 箭头工具 |
| `5` / `X` | 画笔（自由绘制） |
| `6` / `T` | 文本工具 |
| `7` / `N` | 便签工具 |
| `V` | 选择工具 |
| `E` | 橡皮擦 |
| `Ctrl+C/V` | 复制/粘贴 |
| `Ctrl+D` | 复制选中元素 |
| `Ctrl+G` | 组合/取消组合 |
| `Ctrl+[` / `Ctrl+]` | 图层下移/上移 |
| `Ctrl+Z` / `Ctrl+Y` | 撤销/重做 |
| `+` / `-` | 放大/缩小 |
| `Space + 拖拽` | 平移画布 |
| `Shift + 拖拽` | 等比例缩放/直线 |
| `Alt + 拖拽` | 从中心绘制 |

### 2. 绘制架构图的标准流程

1. **设置画布**：打开 Excalidraw，设置网格（右上角菜单 → Show Grid）
2. **布局规划**：先用矩形框出主要模块的位置（不填文字）
3. **添加内容**：逐个矩形添加标题和描述
4. **连接关系**：用箭头连接模块，设置箭头样式
5. **美化样式**：统一配色（建议 ≤3 种颜色）、调整圆角和线条粗细
6. **添加注释**：用便签添加备注和说明
7. **导出**：右键 → Export as PNG/SVG

### 3. 配色方案推荐

```text
// Excalidraw 自定义调色板（设置 → Excalidraw → Theme）
{
  "技术架构图": {
    "用户层": "#dbeafe",
    "应用层": "#dcfce7",
    "数据层": "#fef3c7",
    "基础设施": "#fce7f3",
    "连接线": "#374151"
  },
  "流程图": {
    "开始/结束": "#bbf7d0",
    "处理": "#dbeafe",
    "判断": "#fef3c7",
    "输入/输出": "#e9d5ff"
  }
}
```

### 4. Excalidraw Automate 脚本示例

```mermaid
// scripts/create_architecture_diagram.js
// 从模板创建标准三层架构图
const ea = require("excalidraw-automate");

async function createArchitectureDiagram() {
  // 创建新画布
  const svg = await ea.createNewFile("架构图模板");

  // 定义颜色
  const colors = {
    user: "#dbeafe",
    app: "#dcfce7",
    data: "#fef3c7",
    infra: "#fce7f3",
  };

  // 用户层
  const userBox = await ea.addRect(100, 100, 180, 80, "用户端\n(Web/App)");
  userBox.backgroundColor = colors.user;

  // 应用层
  const apiBox = await ea.addRect(400, 50, 200, 60, "API 网关");
  apiBox.backgroundColor = colors.app;
  const serviceBox = await ea.addRect(400, 140, 200, 60, "微服务集群");
  serviceBox.backgroundColor = colors.app;

  // 数据层
  const dbBox = await ea.addRect(750, 80, 180, 80, "数据库\n(PostgreSQL)");
  dbBox.backgroundColor = colors.data;
  const cacheBox = await ea.addRect(750, 200, 180, 60, "缓存 (Redis)");
  cacheBox.backgroundColor = colors.data;

  // 基础设施
  const infraBox = await ea.addRect(400, 280, 530, 50, "基础设施：Docker / Kubernetes");
  infraBox.backgroundColor = colors.infra;

  // 连接线
  await ea.connectObjects(userBox, "right", apiBox, "left", {
    style: "arrow",
    label: "HTTPS",
  });
  await ea.connectObjects(apiBox, "bottom", serviceBox, "top");
  await ea.connectObjects(serviceBox, "right", dbBox, "left", { label: "SQL" });
  await ea.connectObjects(serviceBox, "right", cacheBox, "left", { label: "缓存" });

  // 添加标题
  await ea.addText(400, 20, "系统架构图", { fontSize: 24, bold: true });

  return svg;
}

module.exports = { createArchitectureDiagram };
```

### 5. 从 Markdown 生成思维导图

```mermaid
// scripts/markdown_to_mindmap.js
// 将选中的 Markdown 标题层级转为思维导图
async function markdownToMindmap() {
  const editor = ea.getEditor();
  const selectedText = ea.getSelection();
  if (!selectedText) {
    new Notice("请先选中 Markdown 文本");
    return;
  }

  // 解析标题层级
  const lines = selectedText.split("\n").filter(l => l.startsWith("#"));
  const nodes = [];
  let x = 100, y = 100;

  // 中心节点
  const center = await ea.addEllipse(400, 300, 200, 80, lines[0].replace(/^#+\s*/, ""));
  center.backgroundColor = "#dbeafe";

  // 子节点（放射布局）
  const radius = 250;
  lines.slice(1).forEach((line, i) => {
    const level = (line.match(/^#+/) || ["#"])[0].length;
    const text = line.replace(/^#+\s*/, "");
    const angle = (i / (lines.length - 1)) * 2 * Math.PI;
    const nx = 400 + radius * Math.cos(angle);
    const ny = 300 + radius * Math.sin(angle);

    const node = ea.addRect(nx - 60, ny - 25, 120, 50, text);
    node.backgroundColor = level <= 2 ? "#dcfce7" : "#fef3c7";
    ea.connectObjects(center, "center", node, "center", { style: "arrow" });
  });

  new Notice("思维导图已生成");
}
```

### 6. 模板使用

在 Excalidraw 中创建模板：
1. 绘制标准图表（如架构图、流程图、用户旅程图）
2. 全选 → 右键 → Add to Library
3. 命名模板（如"三层架构图""用户登录流程"）
4. 使用时：打开 Excalidraw → 左侧 Library 面板 → 点击模板插入

**常用模板清单**：
- 三层架构图（用户层/应用层/数据层）
- 用户登录流程图
- 微服务架构图
- 数据库 ER 图
- 思维导图模板
- 时间线/路线图
- 四象限分析图
- 用户旅程图

### 7. 与 Obsidian 笔记联动

<!-- 在笔记中嵌入 Excalidraw 图表 -->
---

> 💡 **深度讲解**：本节围绕，深入剖析其使用方法与实践技巧，帮助读者建立高效的知识管理工作流。
>
> **📝 精简总结**：本节介绍了，掌握这些内容是提升 Obsidian 使用效率的重要基础。

## 系统架构

![[架构图.excalidraw]]

<!-- 嵌入特定区域（通过标题锚点） -->
![[架构图.excalidraw#^text-1]]

```text
<!-- 在 Excalidraw 图中引用笔记 -->
<!-- 在文本元素中输入 [[]] 会自动转为双链 -->
用户端 [[前端技术栈]]
API 网关 [[统一AI网关设计与实现]]
数据库 [[PostgreSQL性能优化实战]]
```

---

## 四、常见问题与排查

| 问题现象 | 原因分析 | 解决方案 |
|---------|---------|---------|
| 打开 .excalidraw.md 显示的是代码而非画布 | 未切换到 Excalidraw 视图 | 点击右上角 "More options" → "Open in Excalidraw"；或设置默认用 Excalidraw 打开 |
| 手绘风格变成了直线/规整图形 | Roughness 设为 0（关闭手绘效果） | 选中元素 → 右侧属性面板 → Roughness 调到 1-2 |
| 导出的 PNG 模糊 | 导出分辨率太低 | 导出时设置 Scale=2x 或 3x；先放大画布再导出 |
| Excalidraw Automate 脚本不执行 | 脚本未正确注册，或 API 版本不兼容 | 在设置 → Excalidraw → Scripts 中确认脚本已启用；检查 `ea` API 调用方式；查看控制台错误 |
| 图中双链点击不跳转 | 文本中的 [[]] 未被识别为双链 | 确保文本是纯文本元素而非便签；用 `ea.addText` 创建的文本支持双链；升级插件到最新版 |
| 画布太大找不到元素 | 缩放过度或元素在画布外 | 按 `Ctrl+Shift+R` 重置视图；或 `Ctrl+A` 全选后缩放适应 |
| 连接线不自动避让 | 未开启智能路由 | 选中连接线 → 右侧面板 → "Elbowed" 或 "Curved" 路由；拖动连接点调整 |
| 模板库中的模板丢失 | 模板存储在插件数据中，重置 Obsidian 后丢失 | 定期备份 `.obsidian/plugins/obsidian-excalidraw-plugin/` 目录；将常用模板导出为 .excalidraw 文件 |
| 中文文字显示为方块 | 字体不支持中文 | 设置 → Excalidraw → Font Family 选择支持中文的字体（"Microsoft YaHei"/"PingFang SC"） |
| 大量元素时画布卡顿 | 元素过多（>500）或未使用组合 | 用 `Ctrl+G` 组合相关元素；复杂图拆分为多个子图；关闭网格和阴影 |

---

---

> 💡 **深度讲解**：本节围绕，深入剖析其使用方法与实践技巧，帮助读者建立高效的知识管理工作流。
>
> **📝 精简总结**：本节介绍了，掌握这些内容是提升 Obsidian 使用效率的重要基础。

## 五、进阶与最佳实践

### 1. 绘图规范

- **配色统一**：一张图不超过 3 种主色 + 1 种强调色
- **字体统一**：全图用同一种字体，标题加粗
- **对齐整齐**：用对齐工具（左对齐/居中/等间距）保持整洁
- **留白充足**：元素间距 ≥ 40px，避免拥挤
- **标注清晰**：连接线加标签，复杂图加编号和图例
- **粒度适中**：一张图不超过 15 个元素，复杂图拆分为多张

### 2. 与 Canvas 配合使用

- **Canvas** 用于组织笔记卡片和头脑风暴
- **Excalidraw** 用于绘制正式的架构图和流程图
- 可以在 Canvas 中嵌入 Excalidraw 文件作为卡片
- 也可以在 Excalidraw 中用双链引用 Canvas 中的笔记

### 3. 效率提升技巧

| 技巧 | 效果 |
|------|------|
| 建立个人模板库 | 常用图表一键插入，节省 80% 时间 |
| 用 Automate 脚本生成标准图 | 从文本/数据自动生成，零手动绘制 |
| 配色方案预设 | 统一视觉风格，不用每次选颜色 |
| 快捷键记忆 | 1-7 切换工具，V 选择，E 橡皮，效率翻倍 |
| 组合复用 | 常用组件组合后复制粘贴 |
| 双链嵌入 | 图中元素链接到笔记，构建知识网络 |

### 4. 导出与分享

- **嵌入笔记**：直接用 `![[filename.excalidraw]]` 嵌入
- **导出 PNG**：用于 PPT/文档/社交媒体
- **导出 SVG**：用于网页/可缩放场景
- **复制为图片**：直接粘贴到其他应用
- **分享 .excalidraw.md**：其他 Obsidian 用户可直接编辑

---

---

> 💡 **深度讲解**：本节围绕，深入剖析其使用方法与实践技巧，帮助读者建立高效的知识管理工作流。
>
> **📝 精简总结**：本节介绍了，掌握这些内容是提升 Obsidian 使用效率的重要基础。

## 六、关联笔记

### Obsidian 效率
- [[Obsidian-核心插件配置]] · [[Obsidian-Canvas画布用法]] · [[Obsidian-双向链接与图谱]]
- [[Obsidian-模板与快速输入]] · [[Templater-自动化模板]] · [[Obsidian-Dataview查询语言]]
- [[AI文档与PPT生成工作流]] · [[用AI辅助知识回顾与发现]]

### 导航
- [[MOC-AI与效率工具]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Obsidian-核心插件配置]] 搭建环境 → 学习本文 Excalidraw 基础绘图 → 实践 Excalidraw Automate 脚本自动化 → 配合 [[Obsidian-Canvas画布用法]] 做可视化知识管理 → 参考 [[AI文档与PPT生成工作流]] 输出高质量文档。

---

## 📖 前置知识

- [[Obsidian-核心插件配置]]

## 🏷️ 相关标签

`#Obsidian` `#效率工具` `#知识管理` `#可视化`

---

[[Home|🏠 返回首页]] · [[MOC-AIGC与Obsidian-四级展开|📚 返回分类]]

