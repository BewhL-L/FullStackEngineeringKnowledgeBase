---
title: Git 版本控制知识点系统梳理
tags: [通用工具, Git, 版本控制, 面试]
created: 2026-08-13
updated: 2026-08-13
---

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。

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


---
## 2. 核心概念

### 2.1 三个区域

```
工作区（Working Directory）→ git add → 暂存区（Staging Area/Index）→ git commit → 版本库（Repository）
```

- **工作区**：实际编辑的文件
- **暂存区**：`.git/index`，准备提交的文件快照
- **版本库**：`.git/`，提交历史和对象数据库

> 🔍 **知识点深度解析**
>
> **作用**：三个区域（工作区、暂存区、版本库）是 Git 数据流的核心模型，理解它才能正确执行 add/commit/reset。
>
> **原理**：Git 采用"内容寻址"设计。`git add` 把工作区文件快照写入 `.git/objects`（Blob）并在 `.git/index` 记录索引；`git commit` 将索引固化为 Tree 和 Commit 对象存入版本库。三个区域本质是"文件内容在不同阶段的拷贝 + 一份索引清单"。
>
> **用法要点**：① 工作区是你直接编辑的地方，改动不会自动进版本库；② 暂存区是"下次提交的预览"，可用 `git add -p` 精确挑选；③ 版本库是持久化历史，`commit` 后才真正落库；④ `git status` 一眼看清文件落在哪个区域；⑤ 理解区域流转能避免"忘了 add 就 commit"的常见错误；⑥ 面试常考：三区域职责与 add/commit 的数据走向。

### 2.2 文件状态

- **Untracked**：未跟踪（新文件）
- **Unmodified**：未修改
- **Modified**：已修改
- **Staged**：已暂存

> 🔍 **知识点深度解析**
>
> **作用**：文件状态（Untracked/Unmodified/Modified/Staged）描述了文件相对版本库的当前处境，是 `git status` 输出的基础。
>
> **原理**：Git 通过对比"工作区文件内容"与"暂存区索引"以及"最新提交"三者，判定状态：新文件未见记录→Untracked；与索引一致且已提交→Unmodified；工作区与索引不同→Modified；已写入索引待提交→Staged。状态是动态计算结果，不是单独存储的标记。
>
> **用法要点**：① Untracked 文件不会被 `commit` 自动纳入，需先 `add`；② Modified 只是工作区变化，未进暂存区；③ Staged 是已 `add` 待提交；④ `git add` 使 Modified→Staged，`git reset`/`restore --staged` 使 Staged→Modified；⑤ 理解状态机有助于排查"为什么我的修改没提交上去"；⑥ 面试常考：状态流转图与对应命令。

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


---
## 3. 常用命令

### 3.1 基础操作

```bash

> 🔍 **知识点深度解析**
>
> **作用**：Git 基础操作覆盖工作区→暂存区→本地仓库→远程仓库的完整提交流程。
>
> **原理**：git init 初始化仓库；git clone 克隆远程仓库。git add 将工作区修改加入暂存区（git add . 添加所有）。git commit -m "message" 将暂存区提交到本地仓库。git push 将本地提交推送到远程。git pull = git fetch + git merge，拉取远程更新并合并。git status 查看工作区状态，git diff 查看修改内容。
>
> **用法要点**：① 工作区→暂存区（add）→本地仓库（commit）→远程（push）  ② git add -p 交互式暂存，可只暂存部分修改  ③ git commit --amend 修改最后一次提交（未 push 时）  ④ git push -u origin main 首次推送并设置上游分支  ⑤ 面试常考：三个区域、add/commit/push 流程、pull vs fetch

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

> 🔍 **知识点深度解析**
>
> **作用**：基础操作（init/clone/add/commit/status/log/diff）是日常 90% 的使用场景，必须熟练掌握。
>
> **原理**：`clone` 本质是 `init` + 配置远程 + `fetch` + 检出；`git add .` 会递归把工作区变更写入索引；`git commit` 以索引为快照生成新提交并更新当前分支指针；`git log --graph` 通过提交间的父子指针画出分支拓扑。
>
> **用法要点**：① 首次协作用 `clone`，本地建仓用 `init`；② `git add -p` 可逐段暂存，避免提交无关改动；③ `git commit -am` 仅对"已跟踪"文件的修改生效，新文件仍需 `add`；④ `git commit --amend` 改写最近一次提交（未推送时可用）；⑤ 用 `git log --oneline --graph` 快速看分支结构；⑥ `git diff` / `git diff --staged` 分别在提交前后自查改动。

### 3.2 撤销操作

```bash

> 🔍 **知识点深度解析**
>
> **作用**：Git 撤销操作针对工作区、暂存区和提交历史分别提供不同命令，需注意已推送提交的安全撤销。
>
> **原理**：工作区撤销：git checkout -- <file> 或 git restore <file> 丢弃工作区修改。暂存区撤销：git reset HEAD <file> 或 git restore --staged <file> 取消暂存。修改最后提交：git commit --amend（未 push）。回退提交：git reset --soft/mixed/hard（未 push）；已 push 用 git revert 创建反向提交（安全，不改写历史）。
>
> **用法要点**：① git restore <file> 丢弃工作区修改（不可恢复）  ② git restore --staged <file> 取消暂存，保留工作区修改  ③ git reset --hard 彻底回退（慎用，会丢失修改）  ④ 已推送的提交用 git revert，不用 reset --force  ⑤ 面试常考：reset 三种模式、revert vs reset、amend

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

> 🔍 **知识点深度解析**
>
> **作用**：`merge` 是把一个分支的改动并入另一个分支的标准手段，适用于所有分支（含公共分支）。
>
> **原理**：Git 先找两个分支的最近共同祖先（merge base），对"祖先 + 两个分支头"做三方合并生成新内容；若目标分支自祖先起无任何新提交，则直接 Fast-forward 移动指针（不产生合并提交）；否则生成带两个父节点的合并提交，完整保留分叉历史。
>
> **用法要点**：① 默认 merge 可能 Fast-forward，可用 `--no-ff` 强制保留合并提交以体现分支脉络；② Fast-forward 不创建新提交，历史更"平"；③ 三方合并仅在内容冲突时需要手动解决；④ 合并冲突文件含 `<<<<<<<`/`=======`/`>>>>>>>` 标记；⑤ merge 不改写已有提交，对公共分支安全；⑥ 面试常考：Fast-forward 与三方合并的区别、何时产生合并提交。

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

> 🔍 **知识点深度解析**
>
> **作用**：Git 合并冲突发生在两个分支修改同一文件同一位置时，需手动编辑解决后标记完成。
>
> **原理**：git merge/rebase 时冲突，Git 在文件中标记 <<<<<<< HEAD（当前分支）、=======、>>>>>>> branch（合入分支）。手动编辑保留正确内容，删除冲突标记，git add 标记已解决，git commit（merge）或 git rebase --continue（rebase）完成。工具：VSCode/IDEA 内置冲突解决器可视化三窗格合并。预防：频繁拉取主分支、小颗粒提交、沟通避免改同一文件。
>
> **用法要点**：① 冲突标记：<<<<<<< HEAD / ======= / >>>>>>> branch  ② 手动编辑后 git add + git commit 完成 merge  ③ rebase 冲突：git add 后 git rebase --continue  ④ git mergetool 启动可视化合并工具  ⑤ 面试常考：冲突原因、解决流程、merge vs rebase 冲突处理

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

> 🔍 **知识点深度解析**
>
> **作用**：冲突解决是多人协作不可避免的环节，目标是得到一份双方改动都被正确保留的文件。
>
> **原理**：当同一文件的同一区域在两个分支被不同修改，Git 无法自动判定取舍，于是把两边内容都写入文件并用冲突标记（HEAD 一侧 vs 另一分支一侧）标注，交由人决策。merge 冲突解决后 `add`+`commit` 完成合并提交；rebase 冲突则在每个重放步骤解决后 `--continue`。
>
> **用法要点**：① 打开带标记的文件，删除 `<<<<<<<`、`=======`、`>>>>>>>` 并保留正确内容；② merge 冲突解决后 `git add <file>` 再 `git commit`；③ rebase 冲突解决后 `git add` 再 `git rebase --continue`，想放弃用 `git rebase --abort`；④ 可用 `git mergetool` 调用图形化工具辅助；⑤ 预防冲突：频繁 `pull`、小而专注的提交、沟通改动范围；⑥ 面试常考：冲突标记含义、merge/rebase 各自的解冲突流程。

---


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


---
## 7. Git 工作流

### 7.1 Git Flow

- `main`：生产分支
- `develop`：开发分支
- `feature/*`：功能分支（从 develop 切，合并回 develop）
- `release/*`：发布分支（从 develop 切，合并到 main 和 develop）
- `hotfix/*`：紧急修复（从 main 切，合并到 main 和 develop）

> 🔍 **知识点深度解析**
>
> **作用**：Git Flow 是一套严格的分支模型，适合有明确版本发布节奏、需要维护多个历史版本的团队。
>
> **原理**：它通过固定角色的分支协作：常驻的 `main`（生产）与 `develop`（集成分支），以及临时的 `feature/*`（新功能）、`release/*`（发布准备）、`hotfix/*`（线上紧急修复）。功能从 develop 切出并合回 develop，发布与修复最终都要同步回 main 和 develop，保证两边一致。
>
> **用法要点**：① `feature` 从 `develop` 切、合回 `develop`，不直接碰 main；② `release` 用于冻结功能、只修 bug，发布后合入 main（打 tag）与 develop；③ `hotfix` 从 main 切，修复后同时合入 main 和 develop；④ 分支多、流程重，小团队可能觉得繁琐；⑤ 适合需要长期维护多版本（如客户端软件）的项目；⑥ 面试常考：五类分支的职责与合并去向。

### 7.2 GitHub Flow（简单）

- `main`：始终可部署
- 功能分支从 main 切，开发完提 Pull Request
- Code Review 后合并到 main，自动部署

> 🔍 **知识点深度解析**
>
> **作用**：GitHub Flow 是极简工作流，适合持续部署、main 始终可上线的 Web 服务类项目。
>
> **原理**：它只保留一条长期分支 `main`（任何时候都可部署），任何改动都从 main 切出短命的功能分支，开发完成后通过 Pull Request 评审，合并回 main 即触发自动部署。靠 PR 的 Code Review 与 CI 闸门保证质量，而非复杂分支规则。
>
> **用法要点**：① 保持 main 永远可部署，不在 main 上直接堆半成品；② 功能分支命名随意、生命周期短，合并后即删；③ PR 是协作核心：评审、CI、讨论都在这里完成；④ 合并到 main 通常自动部署到生产；⑤ 比 Git Flow 轻量，适合高频发布；⑥ 面试常考：与 Git Flow 的差异、PR/Code Review 在流程中的角色。

### 7.3 Trunk Based Development

- 所有人直接向 main（trunk）提交
- 用 Feature Flag 控制未完成功能
- 频繁小提交，CI 保证质量

> 🔍 **知识点深度解析**
>
> **作用**：Trunk Based Development（主干开发）追求极高集成频率，适合强 CI/CD 能力、追求快速交付的团队。
>
> **原理**：几乎所有人都直接（或经极短分支）向主干 `main` 提交，依赖"频繁小提交 + 自动化测试/CI"在合入前拦截问题；未完成功能用 Feature Flag（特性开关）隐藏，而非长期分支，从而避免分叉与大规模合并冲突。
>
> **用法要点**：① 提交要小且频繁，避免长生命周期分支；② 用 Feature Flag 控制未完成功能的上线，而非靠分支隔离；③ CI 必须可靠，否则主干易被破坏；④ 可配合"短命分支"（几小时内合入）缓解直接提交风险；⑤ 与"分支泛滥"的工作流相比，能显著减少合并痛苦；⑥ 面试常考：与 Git Flow/GitHub Flow 的核心区别、Feature Flag 的作用。

---


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


---
## 9. 常见问题

### 9.1 .gitignore

```gitignore

> 🔍 **知识点深度解析**
>
> **作用**：.gitignore 指定不需要纳入版本控制的文件模式，避免构建产物、密钥和 IDE 文件进入仓库。
>
> **原理**：在仓库根目录创建 .gitignore，每行一个模式：精确文件名（.env）、通配符（*.log、target/、node_modules/）、取反（!important.log）。全局忽略：git config --global core.excludesfile ~/.gitignore_global。注意：已被跟踪的文件不会因 .gitignore 而忽略，需先 git rm --cached <file> 移除跟踪。
>
> **用法要点**：① target/、node_modules/、__pycache__/ 忽略构建产物  ② .env、*.key 忽略密钥和配置文件  ③ *.log、*.tmp 忽略临时文件  ④ 已跟踪文件需 git rm --cached 后 .gitignore 才生效  ⑤ 面试常考：.gitignore 语法、已跟踪文件忽略、全局忽略

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

> 🔍 **知识点深度解析**
>
> **作用**：`.gitignore` 告诉 Git 哪些文件/目录不应被纳入版本库，避免提交依赖、构建产物、密钥等噪音与敏感文件。
>
> **原理**：Git 在扫描工作区时按 `.gitignore` 规则逐行匹配路径；命中且非已被跟踪的文件会被忽略，不出现在 `git status` 也不被 `add`。规则支持目录后缀 `/`、通配符 `*`、取反 `!` 等，仓库级 `.gitignore` 对所有协作者生效，另有 `~/.gitignore_global` 做个人忽略。
>
> **用法要点**：① 依赖目录（`node_modules/`、`target/`）和构建产物（`dist/`、`build/`）应忽略；② IDE 配置（`.idea/`、`.vscode/`）按团队约定忽略；③ 密钥/环境变量（`.env`）绝对不要提交，可用 `.env.example` 代替；④ 已误提交的文件需先 `git rm --cached` 再从跟踪中移除；⑤ 可用 `git check-ignore <path>` 排查为何某文件被忽略；⑥ 面试常考：忽略规则语法、已跟踪文件如何停止跟踪。

### 9.2 大文件处理

- Git 不适合管理大文件（二进制、视频）
- 用 Git LFS（Large File Storage）管理大文件
- 或用 .gitignore 排除，存对象存储

> 🔍 **知识点深度解析**
>
> **作用**：大文件（视频、二进制、数据集）会急剧膨胀 `.git` 体积，拖慢克隆与传输，需要专门方案。
>
> **原理**：Git 的设计针对文本差异与小文件，大文件每次变更都会把所有版本完整存入对象库，导致仓库体积失控。`Git LFS` 把大文件内容存到外部存储，仓库里只保留一个指向实际文件的轻量指针（文本），从而保持仓库小巧。
>
> **用法要点**：① 使用 `git lfs install` 并 `git lfs track "*.psd"` 等声明大文件类型；② 没有 LFS 时，用 `.gitignore` 排除大文件，改存对象存储/网盘并提供下载脚本；③ 已提交的大文件要用 `git lfs migrate` 或 `filter-repo` 重写历史才能真正瘦身；④ 二进制文件难以 diff，尽量用文本或可增量格式；⑤ 团队协作时 LFS 需服务端支持；⑥ 面试常考：Git LFS 原理、为什么 Git 不适合直接管大文件。

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

> 🔍 **知识点深度解析**
>
> **作用**：规范的提交信息提升可读性，便于自动生成 CHANGELOG、定位变更与团队协作。
>
> **原理**：采用 Conventional Commits 约定：`<type>(<scope>): <subject>`，type 标明改动性质（feat/fix/docs/refactor/style/test/chore 等），scope 限定影响范围，subject 用祈使句简述。工具（如 standard-version、semantic-release）可据此自动判定版本号与生成日志。
>
> **用法要点**：① type 必须准确：新功能 feat、修 bug fix、文档 docs、重构 refactor、格式 style、测试 test、杂务 chore；② subject 简洁、以动词开头、不加句号；③ 复杂改动可在空一行后写 body 说明"为什么"；④ 配合 `commitlint` 在提交时校验格式；⑤ 统一规范后可用工具自动发版与写日志；⑥ 面试常考：Conventional Commits 格式、type 分类含义。

---


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
