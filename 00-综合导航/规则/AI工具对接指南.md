---
title: AI工具对接指南
tags: [规则, 知识库, 自增长, AI工具, 自动化]
created: 2026-08-13
---

# 🤖 AI 工具对接指南

> 本指南说明如何配置 AI 工具（Claude Code / Codex / 豆包 / Cursor 等）作为知识库的维护者，包括系统提示词、工作流指令模板和自动化配置。

---

## 1. 支持的 AI 工具

| 工具 | 类型 | 优势 | 适用场景 |
|------|------|------|----------|
| **Claude Code** | CLI 编码助手 | 上下文长、文件操作强、遵循规则好 | 批量处理 Inbox、重构、MOC 更新 |
| **OpenAI Codex** | CLI 编码助手 | 代码能力强、GPT-4o | 代码相关知识处理、技术文档生成 |
| **豆包（本工具）** | 对话式助手 | 中文好、直接操作本地文件 | 单篇处理、问答、规则咨询 |
| **Cursor** | IDE 编辑器 | 内嵌编辑器、Composer 批量改文件 | 边写代码边记录知识 |
| **Obsidian Copilot** | Obsidian 插件 | 直接在 Obsidian 内操作 | 日常快速处理、问答 |

---

## 2. 核心配置：系统提示词

所有 AI 工具处理知识库时，必须加载以下系统提示词。将此内容保存为 `00-综合导航/规则/AI系统提示词.md`，每次启动 AI 工具时加载。

### 2.1 系统提示词全文

```
# 角色
你是这个 Obsidian 知识库的维护助手。你的任务是帮助用户维护一个自增长的全栈工程知识库。

# 知识库位置
根目录：C:\Users\23981\Desktop\AI文档\DouBao Document\全栈工程MarkDown文档

# 必须遵守的规则（按优先级）
1. 先阅读规则文件再操作：
   - 00-综合导航/规则/知识摄入标准.md
   - 00-综合导航/规则/原子化笔记规范.md
   - 00-综合导航/规则/质量校验规则.md
   - 00-综合导航/规则/标签命名规范.md
2. 不删除、不修改用户已有的知识文档，除非用户明确要求
3. 新建笔记必须遵循原子化笔记规范的模板
4. 所有操作完成后必须执行质量校验
5. 涉及合并、拆分、删除等重构操作，必须先列出方案让用户确认

# 目录结构
- Inbox/：知识收件箱，待处理的原始笔记
- 00-综合导航/：MOC、规则、模板、工作流
- 01-前端开发/ ~ 09-AI与效率工具/：知识归档区
- 99-项目实战/：项目型知识
- attachments/：附件

# 标准工作流
## 处理 Inbox
1. 读取 Inbox/ 中 status: 待处理 的笔记
2. 按原子化笔记规范拆解为原子概念
3. 为每个概念生成笔记草稿（存 Inbox/_草稿/）
4. 执行质量校验
5. 通过校验的归档到对应分类目录
6. 更新对应分类的 MOC
7. 将原 Inbox 笔记标记为 status: 已处理

## 周度重构
1. 扫描全库，识别孤儿笔记、重复笔记、链接不足的笔记
2. 生成重构报告
3. 列出合并/拆分/补充链接的建议
4. 等待用户确认后执行

## MOC 更新
1. 当有新笔记归档时，自动添加到对应分类 MOC
2. 每月检查 MOC 完整性

# 输出格式
- 操作前说明要做什么
- 操作后给出完成报告（处理了多少篇、归档到哪里、发现了什么问题）
- 遇到不确定的地方主动提问，不要猜测
```

### 2.2 各工具加载方式

**Claude Code**：
```bash
# 在知识库根目录启动，自动读取 .claude/settings.json
claude

# 或手动加载提示词
claude --system-prompt "$(cat '00-综合导航/规则/AI系统提示词.md')"
```

**Codex**：
```bash
# 创建 .codex/rules.md 放入系统提示词
codex
```

**豆包（本工具）**：
- 直接在对话中发送："请加载知识库维护规则，按自增长知识库架构处理以下任务"
- 或引用规则文件路径

**Cursor**：
- 设置 → Rules → 添加知识库规则文件路径
- 或在 `.cursor/rules` 目录下创建规则文件

---

## 3. 常用工作流指令模板

### 3.1 处理 Inbox

```
请处理 Inbox 中的待处理笔记：
1. 列出 Inbox/ 中所有 status: 待处理 的笔记
2. 选择最旧的 3 篇进行处理
3. 按原子化笔记规范拆解
4. 生成笔记草稿，执行质量校验
5. 通过校验的归档到对应分类，更新 MOC
6. 给出处理报告
```

### 3.2 单篇知识摄入

```
请将以下内容作为新知识摄入：
来源：<说明来源>
内容：<粘贴内容>

按以下步骤处理：
1. 存入 Inbox（按命名规范）
2. 拆解为原子概念
3. 生成原子笔记
4. 质量校验
5. 归档 + 更新 MOC
```

### 3.3 概念深度补充

```
请为 [[概念名]] 这篇笔记补充深入理解部分：
1. 先读取该笔记当前内容
2. 补充底层原理、代码示例、常见误区
3. 检查关联链接是否充分，不足则补充
4. 更新 updated 日期
5. 给出补充报告
```

### 3.4 周度重构

```
请执行周度知识库重构：
1. 扫描全库，生成审计报告（孤儿笔记/重复/链接不足/过时）
2. 列出 Top 5 需要优化的笔记
3. 对每个问题给出具体操作建议
4. 等待我确认后再执行
```

### 3.5 MOC 更新

```
请检查并更新 [[01-前端开发/MOC-前端开发]]：
1. 列出该目录下所有知识文档
2. 对比 MOC 中已有的链接，找出缺失的
3. 按子分类整理添加缺失的文档
4. 更新文档统计数字
```

---

## 4. 自动化脚本（可选）

### 4.1 Inbox 处理脚本（PowerShell + AI API）

```powershell
# scripts/process-inbox.ps1
# 配合 AI API 自动处理 Inbox（需自行配置 API Key）

$vaultPath = "C:\Users\23981\Desktop\AI文档\DouBao Document\全栈工程MarkDown文档"
$inboxPath = Join-Path $vaultPath "Inbox"

# 查找待处理笔记
$pendingNotes = Get-ChildItem $inboxPath -Filter "*.md" | Where-Object {
    $content = Get-Content $_.FullName -Raw -Encoding UTF8
    $content -match "status:\s*待处理"
}

Write-Host "发现 $($pendingNotes.Count) 篇待处理笔记"

# 输出待处理列表（供 AI 工具读取后批量处理）
$pendingNotes | ForEach-Object {
    Write-Host "  - $($_.Name)"
}
```

### 4.2 质量校验脚本

```powershell
# scripts/quality-check.ps1
# 扫描笔记，检查基础结构完整性

$vaultPath = "C:\Users\23981\Desktop\AI文档\DouBao Document\全栈工程MarkDown文档"
$knowledgeDirs = @("01-前端开发", "02-后端开发", "03-数据库与缓存", "04-分布式与中间件",
                   "05-云原生与运维", "06-计算机基础", "07-通用工具", "08-Python全栈",
                   "09-AI与效率工具", "99-项目实战")

$issues = @()

foreach ($dir in $knowledgeDirs) {
    $dirPath = Join-Path $vaultPath $dir
    if (-not (Test-Path $dirPath)) { continue }

    Get-ChildItem $dirPath -Filter "*.md" -Recurse | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -Encoding UTF8

        # 检查 front matter
        if ($content -notmatch "^---") {
            $issues += "$($_.Name): 缺少 front matter"
        }
        # 检查标签
        if ($content -notmatch "tags:") {
            $issues += "$($_.Name): 缺少 tags"
        }
        # 检查双向链接数量
        $linkCount = ([regex]::Matches($content, "\[\[[^\]]+\]\]")).Count
        if ($linkCount -lt 2) {
            $issues += "$($_.Name): 双向链接不足 ($linkCount 个)"
        }
    }
}

Write-Host "发现 $($issues.Count) 个质量问题"
$issues | ForEach-Object { Write-Host "  $_" }
```

### 4.3 标签统计脚本

```powershell
# scripts/tag-stats.ps1
# 统计标签使用频率

$vaultPath = "C:\Users\23981\Desktop\AI文档\DouBao Document\全栈工程MarkDown文档"
$tagCounts = @{}

Get-ChildItem $vaultPath -Filter "*.md" -Recurse | Where-Object {
    $_.FullName -notmatch "\\.obsidian\\"
} | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -Encoding UTF8
    if ($content -match "tags:\s*\[([^\]]+)\]") {
        $tags = $matches[1] -split "," | ForEach-Object { $_.Trim() }
        foreach ($tag in $tags) {
            if ($tag) {
                $tagCounts[$tag] = ($tagCounts[$tag] + 1)
            }
        }
    }
}

$tagCounts.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 20 | ForEach-Object {
    Write-Host "$($_.Key): $($_.Value)篇"
}
```

---

## 5. Obsidian 插件推荐

| 插件 | 用途 | 与自增长体系的配合 |
|------|------|-------------------|
| **Templater** | 高级模板 | 原子化笔记模板自动填充日期、标签 |
| **Dataview** | 数据查询 | 自动生成 MOC、查询待处理笔记、质量报告 |
| **Tasks** | 任务管理 | 追踪待处理、待审核、待合并的笔记 |
| **Calendar** | 日历视图 | 按日期查看 Inbox 摄入和知识增长 |
| **Graph Analysis** | 图谱分析 | 识别孤儿节点、知识孤岛、连接薄弱点 |
| **Copilot** | AI 助手 | 直接在 Obsidian 内调用 AI 处理笔记 |

### 5.1 Dataview 自动 MOC 示例

在 MOC 文件中使用 Dataview 自动列出该分类的所有笔记：

```markdown
```dataview
TABLE tags, created
FROM "01-前端开发"
WHERE !contains(file.name, "MOC")
SORT created DESC
```
```

### 5.2 Dataview 待处理队列

```markdown
```dataview
TABLE source, created
FROM "Inbox"
WHERE status = "待处理"
SORT created ASC
```
```

---

## 6. 安全边界

AI 工具操作知识库时必须遵守：

1. **不删除**：不删除任何笔记，除非用户明确要求
2. **不覆盖**：修改已有笔记前先备份或确认
3. **不猜测**：不确定的分类/标签主动询问用户
4. **可追溯**：所有自动生成的内容标注 `source: AI生成`
5. **人工确认**：合并、拆分、重构等结构性操作必须人工确认后执行
6. **原始保留**：Inbox 原始笔记处理后标记「已处理」，不删除

---

[[00-综合导航/自增长知识库架构说明|← 返回架构说明]] | [[00-综合导航/MOC-综合导航|← 返回综合导航 MOC]] | [[Home|🏠 返回首页]]
