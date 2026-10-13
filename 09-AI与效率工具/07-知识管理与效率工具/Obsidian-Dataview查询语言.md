---
title: Obsidian-Dataview查询语言
tags: [AI应用, AI工程化, LLM]
category: AI与效率工具
created: 2026-08-13
updated: 2026-09-08
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 重要
pre: ["[[Obsidian-核心插件配置]]"]
aliases: [Obsidian-Dataview查询语言, Dataview查询, Dataview DQL]
---

# Obsidian Dataview 查询语言

> **文档说明**：系统讲解 Obsidian Dataview 插件的查询语言（DQL），涵盖数据模型（页面/任务/列表）、Frontmatter 元数据查询、四种查询类型（LIST/TABLE/TASK/CALENDAR）、过滤条件、排序与分组、聚合函数、内联查询、JS API、与 Templater/Periodic Notes 的联动，含 20+ 个真实可用的 DQL 查询示例和最佳实践。
>
> **适用人群**：Obsidian 用户、需要从笔记中提取和展示数据的知识工作者、有 SQL 基础的技术用户
>
> **前置知识**：[[Obsidian-核心插件配置]]、[[Frontmatter元数据规范]]、[[Obsidian-双向链接与图谱]]

---

## 一、概述

<div style="background:linear-gradient(135deg,#11998e,#38ef7d);border-radius:16px;padding:20px;margin:16px 0;font-family:-apple-system,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#fff;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.14),0 3px 10px rgba(0,0,0,.08)">
<style>@keyframes highlight{0%,100%{box-shadow:0 0 0 rgba(255,255,255,0)}50%{box-shadow:0 0 20px rgba(255,255,255,.4)}}.hl-box{background:rgba(255,255,255,.2);border-radius:10px;padding:14px 18px;margin:10px 0;animation:highlight 3s ease-in-out infinite;border-left:4px solid rgba(255,255,255,.6)}.hl-formula{font-family:monospace;font-size:14px;text-align:center;background:rgba(0,0,0,.15);border-radius:8px;padding:12px;margin:10px 0}</style>
<div style="text-align:center;font-size:15px;font-weight:700;margin-bottom:14px;padding-bottom:10px;border-bottom:1.5px solid rgba(255,255,255,.22);letter-spacing:1px;text-shadow:0 1px 3px rgba(0,0,0,.12)">📌 Obsidian Dataview 查询语言</div>
<div class="hl-box">系统讲解 Obsidian Dataview 插件的查询语言（DQL），涵盖数据模型（页面/任务/列表）、Frontmatter 元数据查询、四种查询类型（LIST/TABLE/TASK/CALENDAR）、过滤条件、排序与分组、聚合函数、内联查询、JS API、与 Templater/Period...</div>
<div class="hl-formula">数据源 → 查询语句 → 过滤排序 → 渲染输出 → 动态更新</div>
<div style="font-size:13px;opacity:.9;margin-top:8px">💡 工具是手段，高效的知识管理才是目标</div>
</div>

> 🔍 **知识点深度解析**
>
> **作用**：Obsidian Dataview 查询语言 是 Obsidian 知识管理体系中的重要工具/方法，解决知识采集、组织、检索和利用中的效率问题，适用于构建个人知识管理系统和提升工作效率。
>
> **原理**：通过插件扩展和工作流设计，将 Obsidian 从简单的笔记工具升级为强大的知识管理平台，结合自动化和 AI 能力实现知识的高效处理和价值挖掘。
>
> **用法要点**：① 先掌握基础配置再深入高级功能 ② 建立适合自己的工作流而非照搬他人方案 ③ 善用快捷键和模板提升操作效率 ④ 定期回顾和优化知识管理方法

**Dataview** 是 Obsidian 最强大的插件之一，它将整个笔记库视为一个数据库，通过类 SQL 的查询语言（DQL）从笔记的 Frontmatter、内容、任务、标签中提取数据，并以表格、列表、任务、日历等形式展示。Dataview 的核心价值是**让笔记数据可查询、可聚合、可可视化**——不需要手动整理，查询自动更新。

### 1. Dataview 解决的问题

| 痛点 | 解决方案 |
|------|---------|
| 笔记分散，无法全局查看 | DQL 查询所有笔记，按条件筛选和排序 |
| 任务散落在各篇笔记中 | TASK 查询聚合所有未完成任务 |
| 元数据无法统计分析 | TABLE 查询 + 聚合函数，生成统计报表 |
| 手动维护索引容易过时 | 查询结果自动更新，永远是最新的 |
| 无法按标签/分类/日期筛选 | WHERE 子句灵活过滤 |
| 学习进度/阅读进度无法追踪 | 基于 Frontmatter 的进度查询和仪表盘 |

### 2. Dataview 数据模型

```mermaid
graph TB
    subgraph 数据源
        FM[Frontmatter 元数据<br/>title/tags/date/status...]
        CONTENT[笔记内容<br/>标题/段落/列表]
        TASKS[任务项<br/>- [ ] 任务]
        LINKS[双链<br/>[[]]]
        TAGS[标签<br/>#tag]
    end

    subgraph 查询类型
        LIST[LIST 列表]
        TABLE[TABLE 表格]
        TASK[TASK 任务]
        CAL[CALENDAR 日历]
    end

    FM --> LIST
    FM --> TABLE
    CONTENT --> LIST
    TASKS --> TASK
    LINKS --> TABLE
    TAGS --> LIST
    FM --> CAL
```

### 3. DQL 基本语法

```python
<查询类型> <字段>
FROM <来源>
WHERE <条件>
SORT <字段> <ASC/DESC>
GROUP BY <字段>
LIMIT <数量>
```

与 SQL 类似，但更简洁，针对笔记数据优化。

---

---

> 💡 **深度讲解**：本节围绕，深入剖析其使用方法与实践技巧，帮助读者建立高效的知识管理工作流。
>
> **📝 精简总结**：本节介绍了，掌握这些内容是提升 Obsidian 使用效率的重要基础。

## 二、底层原理

### 1. 索引机制

Dataview 在 Obsidian 启动时扫描所有笔记，构建内存索引：
- 解析每篇笔记的 Frontmatter（YAML）
- 提取任务（`- [ ]` / `- [x]`）
- 提取标签（`#tag`）和双链（`[[]]`）
- 监听文件变化，增量更新索引

查询时直接在内存索引上执行，速度极快（1000 篇笔记查询 < 10ms）。

### 2. 隐式字段

Dataview 为每篇笔记自动生成以下隐式字段，无需在 Frontmatter 中定义：

| 字段 | 说明 | 示例 |
|------|------|------|
| `file.name` | 文件名（不含扩展名） | "Dataview查询语言" |
| `file.folder` | 所在文件夹 | "09-AI与效率工具/07-Obsidian效率" |
| `file.path` | 完整路径 | "09-AI与效率工具/07-Obsidian效率/Dataview.md" |
| `file.ext` | 扩展名 | "md" |
| `file.link` | 笔记链接 | [[Dataview查询语言]] |
| `file.size` | 文件大小（字节） | 15360 |
| `file.ctime` | 创建时间 | 2026-08-13 |
| `file.mtime` | 修改时间 | 2026-09-07 |
| `file.day` | 文件名中的日期 | 2026-09-07（日记） |
| `file.tags` | 所有标签 | ["#AI", "#Dataview"] |
| `file.etags` | 所有标签（含嵌套） | ["#AI", "#AI/Dataview"] |
| `file.lists` | 所有列表项 | [...] |
| `file.tasks` | 所有任务 | [...] |
| `file.outlinks` | 出链 | [[笔记A]], [[笔记B]] |
| `file.inlinks` | 入链 | [[笔记C]] |
| `file.aliases` | 别名 | ["DQL"] |

### 3. 函数与操作符

| 类别 | 常用函数/操作符 |
|------|---------------|
| **比较** | `=`, `!=`, `<`, `>`, `<=`, `>=` |
| **逻辑** | `AND`, `OR`, `NOT` |
| **字符串** | `contains()`, `startswith()`, `endswith()`, `replace()`, `lower()`, `upper()`, `substring()` |
| **数组** | `length()`, `flat()`, `contains()` |
| **日期** | `date()`, `dur()`, `dateformat()` |
| **数学** | `sum()`, `avg()`, `min()`, `max()`, `round()` |
| **其他** | `choice()`, `default()`, `typeof()` |

---

---

> 💡 **深度讲解**：本节围绕，深入剖析其使用方法与实践技巧，帮助读者建立高效的知识管理工作流。
>
> **📝 精简总结**：本节介绍了，掌握这些内容是提升 Obsidian 使用效率的重要基础。

## 三、实操

### 1. LIST 查询

```python
// 列出所有 AI 相关笔记
LIST
FROM #AI
SORT file.name ASC
```

```python
// 列出本周创建的笔记
LIST file.ctime AS "创建时间"
FROM ""
WHERE file.ctime >= date(today) - dur(7 days)
SORT file.ctime DESC
```

```python
// 列出某篇笔记的所有反向链接（被哪些笔记引用）
LIST
FROM [[]]
SORT file.name ASC
```

```python
// 列出所有含特定标签且未完成的笔记
LIST status AS "状态"
FROM #项目
WHERE status != "✅ 已完成"
SORT priority DESC
```

### 2. TABLE 查询

```python
// 所有书籍笔记表格
TABLE author AS "作者", rating AS "评分", status AS "状态", file.mtime AS "更新时间"
FROM #书籍
SORT rating DESC
```

```python
// 技术笔记按分类统计
TABLE length(rows) AS "笔记数", max(file.mtime) AS "最近更新"
FROM #技术
GROUP BY category
SORT length(rows) DESC
```

```text
// 学习进度仪表盘
TABLE
  status AS "状态",
  difficulty AS "难度",
  priority AS "优先级",
  choice(status = "✅ 内容已完善", "🟢", choice(status = "🚧 草稿中", "🟡", "🔴")) AS "进度灯"
FROM "全栈工程知识库"
SORT file.mtime DESC
LIMIT 20
```

```python
// 本月日记汇总
TABLE length(file.tasks) AS "任务数", length(filter(file.tasks, (t) => t.completed)) AS "已完成"
FROM "01-Daily/2026/09"
SORT file.name ASC
```

```python
// 高价值笔记（被多次引用）
TABLE length(file.inlinks) AS "被引用次数", file.tags AS "标签"
FROM ""
WHERE length(file.inlinks) >= 3
SORT length(file.inlinks) DESC
LIMIT 20
```

### 3. TASK 查询

```python
// 所有未完成任务
TASK
FROM ""
WHERE !completed
SORT due ASC
```

```python
// 本周到期的任务
TASK
FROM ""
WHERE !completed AND due <= date(today) + dur(7 days)
SORT due ASC
```

```python
// 按笔记分组的未完成任务
TASK
FROM #项目
WHERE !completed
GROUP BY file.link
```

```python
// 今天到期的任务
TASK
FROM ""
WHERE !completed AND due = date(today)
```

```python
// 已过期未完成的任务
TASK
FROM ""
WHERE !completed AND due < date(today)
SORT due ASC
```

### 4. CALENDAR 查询

```python
// 日记创建日历
CALENDAR file.ctime
FROM "01-Daily"
```

```python
// 笔记创建热力图
CALENDAR file.ctime
FROM ""
WHERE file.ctime >= date(today) - dur(365 days)
```

### 5. 内联查询

```text
<!-- 在笔记正文中直接使用内联查询 -->
本知识库共有 `=length(filter(file.list, (f) => contains(f.tags, "#技术")))` 篇技术笔记。

最近更新的笔记：`=sort(filter(file.list, (f) => f.mtime >= date(today) - dur(7 days)), (f) => f.mtime DESC)[0].link`

当前笔记被 `=length(this.file.inlinks)` 篇笔记引用。

今天是 `=dateformat(date(today), "yyyy年MM月dd日 dddd")`。
```

### 6. 复杂查询示例

```sql
// 项目管理仪表盘
TABLE
  file.link AS "项目",
  status AS "状态",
  priority AS "优先级",
  dateformat(file.ctime, "yyyy-MM-dd") AS "创建日期",
  length(filter(file.tasks, (t) => !t.completed)) AS "待办数",
  length(file.tasks) AS "总任务数",
  round(length(filter(file.tasks, (t) => t.completed)) / length(file.tasks) * 100) + "%" AS "完成率"
FROM #项目
WHERE status != "✅ 已完成"
SORT priority DESC, file.mtime DESC
```

```sql
// MOC 自动生成：列出某分类下所有笔记
TABLE
  file.link AS "笔记",
  difficulty AS "难度",
  status AS "状态",
  choice(contains(status, "已完善"), "✅", "🚧") AS "图标"
FROM "全栈工程知识库/09-AI与效率工具"
WHERE file.name != "MOC-AI与效率工具"
SORT file.name ASC
```

```sql
// 阅读清单：未读完的书
TABLE
  author AS "作者",
  rating AS "评分",
  progress AS "进度",
  file.link AS "笔记"
FROM #书籍
WHERE status = "📖 在读" OR status = "📌 想读"
SORT priority DESC
```

### 7. Dataview JS（高级）

```javascript
// 用 JS 生成更复杂的视图
const pages = dv.pages('#技术').where(p => p.status === '✅ 内容已完善');
const byCategory = pages.groupBy(p => p.category);

for (const group of byCategory) {
  dv.header(3, group.key);
  dv.table(
    ["笔记", "难度", "更新时间"],
    group.rows
      .sort(p => p.file.mtime, 'desc')
      .map(p => [p.file.link, p.difficulty, p.file.mtime.toFormat('yyyy-MM-dd')])
  );
}
```

```bash
// 生成标签云
const tags = dv.pages().file.tags.flat();
const tagCount = {};
for (const tag of tags) {
  tagCount[tag] = (tagCount[tag] || 0) + 1;
}
const sorted = Object.entries(tagCount).sort((a, b) => b[1] - a[1]).slice(0, 20);
dv.paragraph(sorted.map(([tag, count]) => 
  `<span style="font-size:${Math.min(12 + count * 2, 28)}px; margin-right:8px;">${tag}(${count})</span>`
).join(''));
```

### 8. 与 Templater 联动

<!-- Templater 模板中嵌入 Dataview 查询 -->
---

> 💡 **深度讲解**：本节围绕，深入剖析其使用方法与实践技巧，帮助读者建立高效的知识管理工作流。
>
> **📝 精简总结**：本节介绍了，掌握这些内容是提升 Obsidian 使用效率的重要基础。

## 本周任务
TASK
```python
FROM ""
WHERE !completed AND due >= date(<% tp.date.now("YYYY-MM-DD", -6) %>) AND due <= date(<% tp.date.now("YYYY-MM-DD") %>)
```
SORT due ASC

## 本周新增笔记
LIST
```python
FROM ""
WHERE file.ctime >= date(<% tp.date.now("YYYY-MM-DD", -6) %>)
```
SORT file.ctime DESC
```
```

---

## 四、常见问题与排查

| 问题现象 | 原因分析 | 解决方案 |
|---------|---------|---------|
| 查询结果为空 | FROM 路径错误，或 WHERE 条件太严格，或标签/字段名拼写错误 | 去掉 WHERE 测试；确认路径大小写正确；Frontmatter 字段名区分大小写；用 `FROM ""` 查询所有笔记 |
| 日期比较不生效 | 日期字段是字符串而非 date 类型，或格式不对 | Frontmatter 中日期用 `YYYY-MM-DD` 格式；查询中用 `date(field)` 转换；日记用 `file.day` |
| 任务查询不显示任务 | 任务格式不是 `- [ ]`，或任务在折叠块中 | 确保任务用标准 `- [ ]` 格式；Dataview 不识别非标准任务格式；展开折叠块 |
| TABLE 中字段显示 "-" | Frontmatter 中未定义该字段，或字段名不匹配 | 检查 Frontmatter；用 `default(field, "默认值")` 处理缺失值；字段名区分大小写 |
| 内联查询不渲染 | 未启用内联查询，或语法错误 | 设置 → Dataview → Enable Inline Queries；语法用 `=expression`；复杂表达式用 `$=...` |
| GROUP BY 后无法访问字段 | GROUP BY 后字段在 `rows` 中 | 用 `rows.field` 访问；聚合用 `length(rows)`, `max(rows.field)` |
| 大量笔记时查询慢 | 查询未限制范围，或使用了复杂 JS | 用 `FROM "文件夹"` 限制范围；避免 `FROM ""` 全库扫描；复杂计算用 Dataview JS 缓存结果 |
| 标签查询不匹配嵌套标签 | `#AI` 不匹配 `#AI/Dataview`（默认精确匹配） | 用 `contains(file.tags, "#AI")` 匹配嵌套；或用 `FROM #AI/Dataview` 精确指定 |
| file.day 为 null | 文件名不含日期，或格式不标准 | 日记文件名用 `YYYY-MM-DD` 格式；非日记用 Frontmatter 的 date 字段 |
| 修改 Frontmatter 后查询不更新 | Dataview 索引未刷新 | 等待几秒（自动监听）；或命令面板 → "Dataview: Force Refresh"；重启 Obsidian |
| 双链字段无法比较 | `[[]]` 是链接对象，不是字符串 | 用 `link.path` 或 `link.file.name`；比较用 `contains(outlinks, [[目标]])` |

---

---

> 💡 **深度讲解**：本节围绕，深入剖析其使用方法与实践技巧，帮助读者建立高效的知识管理工作流。
>
> **📝 精简总结**：本节介绍了，掌握这些内容是提升 Obsidian 使用效率的重要基础。

## 五、进阶与最佳实践

### 1. Frontmatter 设计规范

Dataview 查询的质量取决于 Frontmatter 的规范性：

```text
---
title: 笔记标题
category: 分类名          # 用于 GROUP BY
status: ✅ 内容已完善     # 固定枚举值
difficulty: ⭐⭐⭐        # 固定格式
priority: 核心            # 核心/重要/普通
tags: [标签1, 标签2]      # 数组格式
created: 2026-08-13       # 标准日期
updated: 2026-09-07
rating: 5                 # 数字类型（1-5）
progress: 80              # 数字类型（0-100）
due: 2026-09-30           # 截止日期
---
```

**原则**：
- 字段名统一（用 `status` 不用 `state`/`Status`）
- 枚举值固定（状态用固定的几个值）
- 日期用 `YYYY-MM-DD`
- 数字字段用数字类型（不加引号）

### 2. 常用查询模板库

建立 `templates/dataview/` 目录，存放常用查询：
- `recent-notes.md`：最近更新的笔记
- `pending-tasks.md`：待办任务汇总
- `project-dashboard.md`：项目仪表盘
- `reading-list.md`：阅读清单
- `knowledge-map.md`：知识地图（按分类统计）
- `weekly-review.md`：周记数据汇总

### 3. 性能优化

| 优化项 | 方法 |
|--------|------|
| 限制范围 | 用 `FROM "文件夹"` 而非 `FROM ""` |
| 减少全库扫描 | 避免在每个笔记中放全库查询 |
| 缓存结果 | 复杂查询结果写入笔记，定期刷新 |
| 用 DQL 而非 JS | DQL 比 Dataview JS 快 2-5 倍 |
| 避免正则 | 用 `contains()` 而非 `regexmatch()` |

### 4. 仪表盘构建

在 MOC 或首页笔记中构建个人仪表盘：

## 📊 个人知识仪表盘

---

> 💡 **深度讲解**：本节围绕，深入剖析其使用方法与实践技巧，帮助读者建立高效的知识管理工作流。
>
> **📝 精简总结**：本节介绍了，掌握这些内容是提升 Obsidian 使用效率的重要基础。

## 待办任务
TASK
```python
FROM ""
WHERE !completed AND due <= date(today) + dur(3 days)
```
SORT due ASC
LIMIT 10

## 最近更新
TABLE file.mtime AS "更新时间", category AS "分类"
```python
FROM ""
WHERE file.mtime >= date(today) - dur(7 days)
```
SORT file.mtime DESC
LIMIT 10

## 分类统计
TABLE length(rows) AS "笔记数"
```python
FROM "全栈工程知识库"
GROUP BY category
```
SORT length(rows) DESC
```
```

---

## 六、关联笔记

### Obsidian 效率
- [[Obsidian-核心插件配置]] · [[Frontmatter元数据规范]] · [[Obsidian-双向链接与图谱]]
- [[Templater-自动化模板]] · [[Calendar与PeriodicNotes]] · [[Obsidian-Canvas画布用法]]
- [[Omnisearch-全文搜索增强]] · [[用AI辅助知识回顾与发现]]

### 导航
- [[MOC-AI与效率工具]] · [[全栈+AI工程双轨融合学习路线图]]

> **学习路径建议**：先掌握 [[Frontmatter元数据规范]] 设计结构化元数据 → 学习本文 DQL 基础语法 → 实践 LIST/TABLE/TASK 查询 → 深入 Dataview JS 高级用法 → 构建个人知识仪表盘。

---

## 📖 前置知识

- [[Obsidian-核心插件配置]]

## 🏷️ 相关标签

`#Obsidian` `#效率工具` `#知识管理` `#数据库`

---

[[Home|🏠 返回首页]] · [[MOC-AIGC与Obsidian-四级展开|📚 返回分类]]

