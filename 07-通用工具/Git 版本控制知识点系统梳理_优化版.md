---
title: Git 版本控制知识点系统梳理
tags: [通用工具, Git, 版本控制, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# Git 版本控制知识点系统梳理（优化版）

> **文档说明**：系统梳理 Git 核心知识，涵盖工作区/暂存区/版本库、常用命令、分支管理、合并冲突、工作流、常见问题等。

---

## 1. 概述

Git 是分布式版本控制系统，由 Linus Torvalds 为 Linux 内核开发创建。与 SVN（集中式）不同，每个开发者本地都有完整的版本库。

**核心优势**：
- 分布式：本地完整仓库，离线可提交
- 速度快：大部分操作本地完成
- 分支轻量：分支创建切换成本极低
- 数据安全：哈希校验，不易丢失

---

## 2. 核心概念

### 2.1 三个区域

```
工作区（Working Directory）→ git add → 暂存区（Staging Area/Index）→ git commit → 版本库（Repository）
```

- **工作区**：实际编辑的文件
- **暂存区**：`.git/index`，准备提交的文件快照
- **版本库**：`.git/`，提交历史和对象数据库

### 2.2 文件状态

- **Untracked**：未跟踪（新文件）
- **Unmodified**：未修改
- **Modified**：已修改
- **Staged**：已暂存

### 2.3 三个对象

- **Blob**：文件内容
- **Tree**：目录结构（文件名 → Blob/Tree）
- **Commit**：提交（Tree + 父提交 + 作者 + 信息）

> 🔍 **知识点深度解析**
>
> **作用**：理解 Git 三个区域是正确使用 Git 的基础。
>
> **原理**：Git 是内容寻址文件系统，所有对象用 SHA-1 哈希标识。`git add` 将工作区文件内容生成 Blob 对象存入 `.git/objects/`，并在暂存区（index）记录文件名→Blob 映射。`git commit` 将暂存区生成 Tree 对象，再创建 Commit 对象（指向 Tree + 父 Commit），更新分支指针（HEAD→分支→Commit）。所以 commit 是不可变的（改了内容哈希就变），Git 通过引用（分支、标签、HEAD）指向 commit。
>
> **用法要点**：① `git status` 查看文件状态；② `git diff` 看工作区 vs 暂存区，`git diff --staged` 看暂存区 vs 版本库；③ 面试常考：三个区域、git add/commit 原理、文件状态流转、.git 目录结构。

---

## 3. 常用命令

### 3.1 基础操作

```bash
# 初始化/克隆
git init                    # 初始化仓库
git clone <url>             # 克隆远程仓库
git clone -b <branch> <url> # 克隆指定分支

# 配置
git config --global user.name "name"
git config --global user.email "email@example.com"
git config --list           # 查看配置

# 添加/提交
git add <file>              # 添加指定文件到暂存区
git add .                   # 添加所有修改和新文件
git add -p                  # 交互式添加（部分添加）
git commit -m "message"     # 提交
git commit -am "message"    # 跳过 add，直接提交已跟踪文件的修改
git commit --amend          # 修改上一次提交

# 查看
git status                  # 查看状态
git log --oneline --graph --all  # 查看提交历史（图形化）
git diff                    # 工作区 vs 暂存区
git diff --staged           # 暂存区 vs 版本库
git show <commit>           # 查看某次提交详情
```

### 3.2 撤销操作

```bash
# 撤销工作区修改（恢复到暂存区版本）
git checkout -- <file>      # 旧版
git restore <file>          # 新版（Git 2.23+）

# 撤销暂存（从暂存区移回工作区，不改变内容）
git reset HEAD <file>       # 旧版
git restore --staged <file> # 新版

# 回退提交
git reset --soft HEAD~1     # 回退到上一次提交，改动保留在暂存区
git reset --mixed HEAD~1    # 默认，改动保留在工作区
git reset --hard HEAD~1     # 彻底回退，改动丢弃（危险！）
git revert <commit>         # 新建提交撤销指定提交（安全，推荐公共分支）
```

> 🔍 **知识点深度解析**
>
> **作用**：撤销操作是 Git 最容易混淆的部分，理解 reset 三种模式很重要。
>
> **原理**：`git reset` 移动 HEAD（和分支指针）到指定 commit，根据模式决定暂存区和工作区是否同步：--soft 只动 HEAD（改动在暂存区），--mixed 动 HEAD+暂存区（改动在工作区，默认），--hard 动 HEAD+暂存区+工作区（彻底丢弃）。`git revert` 不修改历史，而是新建一个反向提交，适合公共分支（不会引起冲突）。`git commit --amend` 修改上一次提交（实际是替换，生成新 commit）。
>
> **用法要点**：① 已推送到远程的提交不要用 reset --hard（会改历史，别人拉取冲突），用 revert；② 本地未推送的提交可以 reset；③ git restore 是新版命令，比 checkout 更清晰；④ 面试常考：reset 三种模式、reset vs revert、撤销操作、--amend 用法。

---

## 4. 分支管理

```bash
# 查看分支
git branch                  # 本地分支
git branch -a               # 所有分支（含远程）
git branch -v               # 分支及最新提交

# 创建/切换
git branch <name>           # 创建分支
git checkout <name>         # 切换分支（旧版）
git switch <name>           # 切换分支（新版）
git checkout -b <name>      # 创建并切换（旧版）
git switch -c <name>        # 创建并切换（新版）

# 删除
git branch -d <name>        # 删除已合并分支
git branch -D <name>        # 强制删除（未合并也删）

# 重命名
git branch -m old new
```

---

## 5. 合并与变基

### 5.1 合并（merge）

```bash
git switch main
git merge feature           # 将 feature 合并到 main
```

**两种合并**：
- **Fast-forward**：目标分支没有新提交，直接移动指针（无新 commit）
- **三方合并**：目标分支有新提交，生成合并 commit（有两个父提交）

### 5.2 变基（rebase）

```bash
git switch feature
git rebase main             # 将 feature 的提交在 main 上重放
```

**merge vs rebase**：

| 特性 | merge | rebase |
|------|-------|--------|
| 历史 | 保留分叉，有合并 commit | 线性历史，无合并 commit |
| 安全性 | 安全，不改变已有 commit | 改变 commit 哈希，公共分支禁用 |
| 适用 | 公共分支合并 | 本地分支整理历史 |

> 🔍 **知识点深度解析**
>
> **作用**：merge 和 rebase 是合并分支的两种方式，选择正确的方式很重要。
>
> **原理**：merge 找到两个分支的共同祖先，做三方合并（祖先+两个分支头），生成合并 commit，保留完整历史。rebase 找到共同祖先，将当前分支的提交逐个在目标分支头上重放（生成新的 commit，哈希变了），结果是线性历史。rebase 黄金法则：**不要对已经推送到公共仓库的分支做 rebase**（会改历史，其他人基于旧 commit 的工作会冲突）。
>
> **用法要点**：① 公共分支用 merge，个人本地分支可用 rebase 整理历史；② rebase 过程中冲突解决后 `git rebase --continue`，放弃 `git rebase --abort`；③ 面试常考：merge vs rebase、rebase 黄金法则、Fast-forward、合并冲突解决。

### 5.3 冲突解决

```bash
# 合并冲突时，Git 标记冲突文件
<<<<<<< HEAD
当前分支内容
=======
合并进来的内容
>>>>>>> feature

# 手动编辑解决冲突后
git add <file>
git commit        # merge 冲突
# 或
git rebase --continue  # rebase 冲突
```

---

## 6. 远程仓库

```bash
# 远程管理
git remote -v               # 查看远程仓库
git remote add origin <url> # 添加远程
git remote set-url origin <url>  # 修改远程地址

# 拉取/推送
git fetch origin            # 拉取远程更新（不合并）
git pull origin main        # 拉取并合并（= fetch + merge）
git pull --rebase origin main    # 拉取并变基
git push origin main        # 推送到远程
git push -u origin main     # 推送并设置上游跟踪
git push --force            # 强制推送（危险！）
git push --force-with-lease # 安全强制推送（别人没改才成功）

# 远程分支
git checkout -b feature origin/feature  # 跟踪远程分支
git push origin --delete feature        # 删除远程分支
```

> 🔍 **知识点深度解析**
>
> **作用**：远程仓库操作是团队协作的基础。
>
> **原理**：`git fetch` 只下载远程更新到本地（origin/main），不改变工作区和当前分支；`git pull` = fetch + merge（或 rebase），会更新当前分支。`git push` 将本地提交上传到远程，如果远程有新提交会被拒绝，需要先 pull。`--force` 强制覆盖远程（会丢别人的提交），`--force-with-lease` 只在远程没有新提交时才强制，更安全。`-u` 设置上游后，后续 git push/pull 不需要指定分支。
>
> **用法要点**：① 推送前先 pull，避免冲突；② 不要随便 --force，用 --force-with-lease；③ git pull 默认 merge，可配置 pull.rebase=true 改用 rebase；④ 面试常考：fetch vs pull、push --force 风险、--force-with-lease、上游跟踪。

---

## 7. Git 工作流

### 7.1 Git Flow

- `main`：生产分支
- `develop`：开发分支
- `feature/*`：功能分支（从 develop 切，合并回 develop）
- `release/*`：发布分支（从 develop 切，合并到 main 和 develop）
- `hotfix/*`：紧急修复（从 main 切，合并到 main 和 develop）

### 7.2 GitHub Flow（简单）

- `main`：始终可部署
- 功能分支从 main 切，开发完提 Pull Request
- Code Review 后合并到 main，自动部署

### 7.3 Trunk Based Development

- 所有人直接向 main（trunk）提交
- 用 Feature Flag 控制未完成功能
- 频繁小提交，CI 保证质量

---

## 8. 其他实用命令

```bash
# 储藏（临时保存工作区修改）
git stash                   # 储藏
git stash list              # 查看储藏列表
git stash pop               # 恢复并删除储藏
git stash apply             # 恢复但不删除
git stash drop              # 删除储藏

# 标签
git tag v1.0.0              # 轻量标签
git tag -a v1.0.0 -m "release 1.0"  # 附注标签
git push origin v1.0.0      # 推送标签
git push --tags             # 推送所有标签

# 查看历史
git log --oneline --graph --all --decorate
git reflog                  # 查看所有操作记录（恢复误删的救命稻草）
git blame <file>            # 查看每行最后修改者

# 挑选提交
git cherry-pick <commit>    # 将指定提交应用到当前分支

# 二分查找（找引入 bug 的提交）
git bisect start
git bisect bad              # 当前版本有 bug
git bisect good <commit>    # 某个版本没问题
# Git 自动二分，逐个测试
git bisect reset            # 结束
```

> 🔍 **知识点深度解析**
>
> **作用**：reflog 和 stash 是救命工具，cherry-pick 和 bisect 是高级技巧。
>
> **原理**：`git reflog` 记录 HEAD 的所有移动历史（包括被 reset/rebase 丢弃的 commit），误操作后可以通过 reflog 找到丢失的 commit 哈希，用 `git reset --hard <hash>` 恢复。`git stash` 将工作区和暂存区的修改保存为一个栈，工作区恢复干净，之后可以 pop 恢复。`git cherry-pick` 将指定 commit 的改动应用到当前分支（生成新 commit）。`git bisect` 用二分法快速定位引入 bug 的提交。
>
> **用法要点**：① 误删 commit 不要慌，git reflog 找回来（30天内）；② 切换分支前有未提交修改，用 stash 暂存；③ cherry-pick 适合只需要某个分支的个别提交；④ 面试常考：reflog 作用、stash 用法、cherry-pick、bisect。

---

## 9. 常见问题

### 9.1 .gitignore

```gitignore
# 依赖
node_modules/
target/

# 构建产物
dist/
build/

# IDE
.idea/
.vscode/
*.iml

# 环境变量
.env
.env.local

# 系统文件
.DS_Store
Thumbs.db
```

### 9.2 大文件处理

- Git 不适合管理大文件（二进制、视频）
- 用 Git LFS（Large File Storage）管理大文件
- 或用 .gitignore 排除，存对象存储

### 9.3 提交信息规范

```
<type>(<scope>): <subject>

feat(auth): 添加微信登录功能
fix(api): 修复用户列表分页错误
docs: 更新 README
refactor: 重构用户服务
style: 格式化代码
test: 添加登录测试
chore: 更新依赖版本
```

---

## 10. 面试高频考点

1. **三个区域**：工作区/暂存区/版本库
2. **git add/commit 原理**：Blob/Tree/Commit 对象
3. **撤销操作**：reset 三种模式、restore、revert
4. **merge vs rebase**：区别、rebase 黄金法则
5. **fetch vs pull**：区别、pull --rebase
6. **push --force**：风险、--force-with-lease
7. **reflog**：恢复误删提交
8. **stash**：临时储藏
9. **冲突解决**：merge/rebase 冲突处理
10. **Git Flow**：工作流模型

---

## 📝 精简总结

- Git 是分布式版本控制，三个区域：工作区→暂存区→版本库
- 基础：add 暂存、commit 提交、status 查看、log 历史
- 撤销：restore 工作区、reset 回退、revert 反向提交
- 分支：branch 创建、switch 切换、merge/rebase 合并
- 远程：fetch 拉取、pull 拉取合并、push 推送
- 高级：stash 储藏、reflog 恢复、cherry-pick 挑选、bisect 二分
- 公共分支用 merge，本地分支可 rebase，不要 force push 公共分支
- 规范：Conventional Commits 提交格式、.gitignore 忽略文件

---

[[07-通用工具/MOC-通用工具|← 返回通用工具 MOC]] | [[Home|🏠 返回首页]]
