---
title: Git命令速查表
tags: [速查表, Git, 版本控制, 效率工具]
category: 通用工具
created: 2026-08-27
updated: 2026-08-27
difficulty: ⭐
status: ✅ 内容已完善
priority: 重要
pre: []
aliases: [Git命令速查表]
---

# Git命令速查表

> **文档说明**：Git常用命令速查表，覆盖基础操作、分支管理、远程协作、高级操作、问题排查。
>
> **适用人群**：所有开发者
>
> **使用方式**：快速查阅，面试前复习

---

## 一、基础配置

```bash
# 用户配置
git config --global user.name "name"
git config --global user.email "email@example.com"

# 查看配置
git config --list
git config user.name

# 别名配置
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --oneline --graph --all"

# 默认分支名
git config --global init.defaultBranch main

# 大小写敏感（Windows/Mac）
git config --global core.ignorecase false
```

---

## 二、创建与克隆

```bash
# 初始化仓库
git init
git init repo-name

# 克隆仓库
git clone https://github.com/user/repo.git
git clone -b branch-name url  # 克隆指定分支
git clone --depth 1 url       # 浅克隆（只取最新提交）
git clone --recursive url     # 递归克隆子模块
```

---

## 三、基本操作

| 命令 | 说明 | 示例 |
|------|------|------|
| `git status` | 查看状态 | `git status` `git st` |
| `git add` | 添加到暂存区 | `git add file` `git add .` `git add -p`（交互式） |
| `git commit` | 提交 | `git commit -m "msg"` `git commit -am "msg"`（跳过add） |
| `git commit --amend` | 修改上次提交 | `git commit --amend -m "new msg"` |
| `git rm` | 删除文件 | `git rm file` `git rm --cached file`（只从暂存区删） |
| `git mv` | 重命名 | `git mv old new` |
| `git restore` | 恢复文件 | `git restore file`（工作区） `git restore --staged file`（暂存区） |
| `git diff` | 查看差异 | `git diff`（工作区vs暂存区） `git diff --staged`（暂存区vs仓库） |

### .gitignore

```css
# 忽略文件
*.log
node_modules/
dist/
.env
.idea/
*.local

# 不忽略（取反）
!important.log

# 目录
/build/
/target/
```

---

## 四、分支管理

```bash
# 查看分支
git branch              # 本地分支
git branch -a           # 所有分支（本地+远程）
git branch -r           # 远程分支
git branch -v           # 分支最后提交

# 创建分支
git branch feature      # 创建分支
git checkout -b feature # 创建并切换
git switch -c feature   # 新版切换（推荐）

# 切换分支
git checkout feature
git switch feature      # 新版（推荐）
git switch -            # 切换到上一个分支

# 删除分支
git branch -d feature   # 删除已合并分支
git branch -D feature   # 强制删除

# 重命名分支
git branch -m old new
git branch -M new       # 强制重命名
```

---

## 五、合并与变基

```bash
# 合并
git merge feature              # 合并feature到当前分支
git merge --no-ff feature      # 禁止快进合并（生成合并提交）
git merge --squash feature     # 压缩合并（多个提交变一个）
git merge --abort              # 中止合并

# 变基
git rebase main                # 当前分支变基到main
git rebase -i HEAD~3           # 交互式变基（最近3个提交）
git rebase --abort             # 中止变基
git rebase --continue          # 解决冲突后继续
git rebase --skip              # 跳过当前提交

# 交互式变基操作
# p/pick 保留
# r/reword 保留但修改信息
# e/edit 保留但暂停修改
# s/squash 合并到上一个
# f/fixup 合并到上一个（丢弃信息）
# d/drop 删除
```

### merge vs rebase

| 维度 | merge | rebase |
|------|-------|--------|
| 历史 | 保留分支历史，有合并节点 | 线性历史，无合并节点 |
| 安全 | 安全，不改变已有提交 | 改变提交历史，公共分支慎用 |
| 适用 | 公共分支合并 | 个人分支整理 |

---

## 六、远程操作

```bash
# 远程仓库
git remote -v                    # 查看远程
git remote add origin url        # 添加远程
git remote remove origin         # 删除远程
git remote set-url origin url    # 修改远程URL

# 拉取
git fetch origin                 # 拉取远程更新（不合并）
git pull origin main             # 拉取并合并
git pull --rebase origin main    # 拉取并变基（推荐）

# 推送
git push origin main             # 推送到远程
git push -u origin main          # 推送并设置上游
git push --force origin main     # 强制推送（慎用）
git push --force-with-lease      # 安全强制推送（推荐）
git push origin --delete branch  # 删除远程分支
git push --tags                  # 推送标签
```

---

## 七、查看历史

```bash
# 查看日志
git log                          # 完整日志
git log --oneline                # 一行显示
git log --graph                  # 图形化
git log --oneline --graph --all  # 所有分支图形化
git log -p file                  # 文件变更历史
git log --author="name"          # 按作者
git log --since="2024-01-01"     # 按时间
git log --grep="keyword"         # 按提交信息搜索

# 查看提交
git show commit-id               # 查看提交详情
git show commit-id:file          # 查看某提交时的文件

# 统计
git shortlog -sn                 # 贡献者统计
git diff --stat                  # 变更统计
```

---

## 八、撤销与回退

```bash
# 工作区修改撤销
git restore file                 # 撤销工作区修改
git checkout -- file             # 旧版写法

# 暂存区撤销
git restore --staged file        # 从暂存区撤回
git reset HEAD file              # 旧版写法

# 回退提交
git reset --soft HEAD~1          # 回退提交，保留修改在暂存区
git reset --mixed HEAD~1         # 回退提交，保留修改在工作区（默认）
git reset --hard HEAD~1          # 回退提交，丢弃所有修改 ⚠️

# 回退到指定提交
git reset --hard commit-id

# 安全回退（生成新提交）
git revert commit-id             # 反向提交
git revert HEAD~2..HEAD          # 回退最近2个提交
```

### reset三种模式

```text
--soft   : HEAD回退，暂存区和工作区不变（修改还在暂存区）
--mixed  : HEAD+暂存区回退，工作区不变（修改还在工作区）默认
--hard   : HEAD+暂存区+工作区全部回退（修改丢失，慎用）
```

---

## 九、暂存（Stash）

```bash
# 暂存当前修改
git stash                        # 暂存
git stash save "message"         # 暂存并添加说明
git stash -u                     # 包含未跟踪文件

# 查看暂存列表
git stash list

# 恢复暂存
git stash apply                  # 恢复最近暂存（不删除）
git stash apply stash@{1}        # 恢复指定暂存
git stash pop                    # 恢复并删除最近暂存
git stash pop stash@{1}          # 恢复并删除指定暂存

# 删除暂存
git stash drop stash@{0}         # 删除指定暂存
git stash clear                  # 清空所有暂存

# 查看暂存内容
git stash show -p stash@{0}
```

---

## 十、标签

```bash
# 创建标签
git tag v1.0.0                   # 轻量标签
git tag -a v1.0.0 -m "release"   # 附注标签（推荐）
git tag -a v1.0.0 commit-id      # 给历史提交打标签

# 查看标签
git tag
git tag -l "v1.*"                # 过滤
git show v1.0.0                  # 查看标签详情

# 删除标签
git tag -d v1.0.0                # 本地删除
git push origin :refs/tags/v1.0.0  # 远程删除

# 推送标签
git push origin v1.0.0           # 推送单个
git push --tags                  # 推送所有
```

---

## 十一、问题排查

```bash
# 查看谁改了某行
git blame file

# 二分查找bug引入提交
git bisect start
git bisect bad                   # 当前版本有bug
git bisect good commit-id        # 这个版本没bug
# 测试后标记
git bisect good/bad
git bisect reset                 # 结束二分查找

# 查找修改某行的提交
git log -S "keyword"             # 搜索添加/删除某字符串的提交
git log -L 10,20:file            # 查看某行范围历史

# 引用日志（恢复误删）
git reflog                       # 查看所有HEAD移动记录
git reset --hard HEAD@{5}        # 恢复到某次状态
```

---

## 十二、常用工作流

### Feature Branch工作流

```bash
git switch -c feature/login      # 创建功能分支
# 开发...
git add . && git commit -m "feat: login"
git push -u origin feature/login
# PR/MR合并后
git switch main
git pull --rebase
git branch -d feature/login
```

```text
### Git Flow
```

```text
main        生产分支
develop     开发分支
feature/*   功能分支
release/*   发布分支
hotfix/*    热修复分支
```

---

## 关联文档

- [[Git-高级命令与底层原理]] — Git深度原理
- [[Git-Hooks自动化]] — Git Hooks
- [[Git-Worktree多分支并行]] — Worktree
- [[代码评审规范]] — Code Review

---

> 💡 **使用建议**：日常高频命令：status/add/commit/pull/push/branch/merge。进阶必学：rebase（整理提交历史）、stash（临时保存）、reflog（后悔药）、bisect（二分查bug）。团队协作推荐使用`pull --rebase`保持线性历史。

---

## 🔗 关联笔记

- [[MOC-通用工具]] — 返回本分类知识地图，查看更多相关文档

## 📖 前置知识

- 无特殊前置知识要求，具备基础编程概念即可

## 🏷️ 相关标签

`#速查表` `#Git` `#版本控制` `#效率工具`

[[Home|🏠 返回首页]] · [[MOC-通用工具|📚 返回分类]]
