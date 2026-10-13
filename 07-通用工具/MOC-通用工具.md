---
title: MOC - 通用工具
tags: [MOC, 通用工具, Git, 效率, 终端, 编辑器]
category: 通用工具
created: 2026-08-13
updated: 2026-08-27
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 重要
pre: []
aliases: [MOC-通用工具]
---

# MOC - 通用工具

> 全栈开发通用工具与效率技能索引，覆盖版本控制、编辑器、终端命令行、API调试、文档图表、自动化效率六大领域，共40+篇文档。
>
> **学习建议**：Git和终端是基础必学，编辑器选一个深耕，API调试和自动化按需学习。

---

## 📚 学习路线

```text
入门阶段：Git基础 → Linux命令 → VSCode配置 → Markdown语法
进阶阶段：Git高级 → 终端工具(fzf/tmux) → API调试(Postman/Apifox) → Mermaid图表
高级阶段：Git底层原理 → 脚本自动化 → Monorepo管理 → n8n自动化平台
专家阶段：Git Workflow设计 → 自定义工具链 → 效率平台搭建
```

---

## 📂 文档索引

### 一、版本控制（Git）

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Git 版本控制知识点系统梳理_优化版]] | Git核心概念、常用命令、分支管理、工作流、面试考点 | 🟢入门 |
| [[Git命令速查表]] | 高频命令速查，分支/合并/变基/撤销/暂存 | 🟢入门 |
| [[Git-高级命令与底层原理]] | reflog/bisect/对象模型/内部机制 | 🔴高级 |
| [[Git-冲突解决与变基]] | merge冲突处理、rebase交互式变基 | 🟡进阶 |
| [[Git-Hooks自动化]] | pre-commit/commit-msg钩子、Husky配置 | 🟡进阶 |
| [[Git-Worktree多工作树]] | 多分支并行开发、worktree使用场景 | 🟡进阶 |
| [[Git-LFS大文件管理]] | 大文件版本管理、二进制文件存储 | 🟡进阶 |

### 二、编辑器与IDE

| 文档 | 说明 | 难度 |
|------|------|------|
| [[VSCode-核心配置与插件]] | VSCode配置、必装插件、工作区设置 | 🟢入门 |
| [[VSCode-自定义Snippet与快捷键]] | 代码片段、快捷键自定义、效率提升 | 🟡进阶 |
| [[Cursor-AI编辑器深度使用]] | AI编程助手、Tab补全、Chat功能、规则配置 | 🟡进阶 |
| [[JetBrains-IDEA高效配置]] | IDEA配置、快捷键、插件、调试技巧 | 🟡进阶 |
| [[Vim-Neovim入门与配置]] | Vim模式、Neovim配置、插件生态 | 🔴高级 |
| [[Zed-高性能编辑器]] | Zed编辑器特性、协作编辑、配置 | 🟡进阶 |

### 三、终端与命令行

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Linux命令速查表]] | 文件/进程/网络/文本处理高频命令 | 🟢入门 |
| [[WindowsTerminal与PowerShell]] | Windows终端配置、PowerShell基础 | 🟢入门 |
| [[PowerShell脚本自动化]] | PowerShell脚本编写、批量操作 | 🟡进阶 |
| [[WSL2-开发环境配置]] | WSL2安装、Linux开发环境、与Windows互操作 | 🟡进阶 |
| [[Zsh与OhMyZsh]] | Zsh配置、主题、插件、别名 | 🟢入门 |
| [[Starship-跨平台提示符]] | Starship安装配置、自定义提示符 | 🟢入门 |
| [[fzf-模糊搜索神器]] | fzf安装、文件/历史/进程模糊搜索 | 🟡进阶 |
| [[tmux-终端复用]] | tmux会话/窗口/窗格管理、配置 | 🟡进阶 |
| [[atuin-命令历史增强]] | atuin安装、历史搜索、同步 | 🟢入门 |
| [[curl高级用法]] | HTTP请求、API测试、下载、调试 | 🟡进阶 |
| [[定时任务与Cron表达式]] | Cron语法、定时任务、系统调度 | 🟢入门 |
| [[常用CLI工具速查]] | jq/htop/rg/btop等常用CLI工具 | 🟡进阶 |

### 四、API调试工具

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Postman-高级用法与团队协作]] | Postman集合、环境变量、自动化测试、团队协作 | 🟡进阶 |
| [[Apifox-接口管理平台]] | Apifox接口设计、Mock、测试、文档一体化 | 🟡进阶 |
| [[Mock服务与接口模拟-Mockoon]] | Mockoon安装、接口Mock、前端开发解耦 | 🟢入门 |
| [[gRPC调试工具-bloomrpc]] | gRPC接口调试、bloomrpc使用 | 🟡进阶 |
| [[WebSocket调试工具]] | WebSocket连接测试、消息收发调试 | 🟡进阶 |

### 五、文档与图表

| 文档 | 说明 | 难度 |
|------|------|------|
| [[Markdown进阶语法]] | GFM语法、扩展语法、Obsidian特性 | 🟢入门 |
| [[Mermaid-图表绘制]] | 流程图/时序图/类图/甘特图/思维导图绘制 | 🟡进阶 |
| [[PlantUML-UML建模]] | UML类图/时序图/用例图、PlantUML语法 | 🔴高级 |
| [[文档自动生成工具]] | API文档生成、代码文档、静态站点 | 🟡进阶 |

### 六、自动化与效率

| 文档 | 说明 | 难度 |
|------|------|------|
| [[通用开发工具与终端效率知识点完整整合大全_优化版]] | Shell/Linux运维/正则/Vim/tmux/API调试/网络诊断/Git进阶 | 🟡进阶 |
| [[效率工具-枢纽]] | 效率工具集合索引、工作流优化 | 🟢入门 |
| [[浏览器开发者工具进阶]] | Chrome DevTools高级用法、性能分析、网络调试 | 🟡进阶 |
| [[n8n-开源自动化平台]] | n8n安装、工作流设计、节点使用、自动化场景 | 🟡进阶 |
| [[Monorepo管理策略]] | pnpm workspace/Turborepo/Nx、Monorepo最佳实践 | 🔴高级 |
| [[Python脚本-批量文件处理]] | Python批量重命名/格式转换/数据处理脚本 | 🟡进阶 |
| [[密码管理器-Bitwarden]] | Bitwarden安装、密码管理、自动填充、同步 | 🟢入门 |

---

## 🔗 知识关联

```text
通用工具
├── Git版本控制 ← 所有开发的基础
│   ├── 分支管理 → 团队协作
│   ├── CI/CD → 云原生运维
│   └── 代码规范 → Commitlint/Husky
├── 编辑器/IDE ← 开发效率核心
│   ├── VSCode → 前端/Python
│   ├── IDEA → Java/Kotlin
│   └── Vim/Neovim → 终端开发
├── 终端命令行 ← 运维/调试必备
│   ├── Linux → 服务器运维
│   ├── PowerShell → Windows自动化
│   └── 工具链(fzf/tmux/atuin) → 效率提升
├── API调试 ← 前后端联调
│   ├── Postman/Apifox → REST API
│   └── bloomrpc → gRPC
├── 文档图表 ← 知识输出
│   ├── Markdown → 笔记/文档
│   └── Mermaid/PlantUML → 架构图
└── 自动化效率 ← 重复工作自动化
    ├── n8n → 工作流自动化
    ├── Python脚本 → 批量处理
    └── Monorepo → 大型项目管理
```

---

## 🏷️ 相关标签

`#通用工具` `#Git` `#版本控制` `#编辑器` `#终端` `#Linux` `#效率` `#自动化`

---

[[Home|🏠 返回首页]]
