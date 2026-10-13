---
title: 常见错误FAQ合集
tags: [学习路径]
category: 学习路径
created: 2026-08-27
updated: 2026-08-27
difficulty: ⭐
status: ✅ 内容已完善
priority: 一般
pre: []
aliases: [常见错误FAQ合集]
---

# 常见错误 FAQ 合集

> **文档说明**：按板块整理的高频踩坑问题与解决方案，遇到报错先查这里。

---

## 一、Java/Spring Boot

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `NullPointerException` | 对象未初始化就调用 | 加null检查，用Optional，@NonNull |
| `ClassNotFoundException` | 缺少依赖或类名错误 | 检查pom.xml依赖，全类名是否正确 |
| `BeanCreationException` | Spring Bean创建失败 | 看Caused by，通常是循环依赖或配置错误 |
| `Circular Dependency` | Bean循环依赖 | 用@Lazy，重构代码，Setter注入 |
| `Transaction doesn't rollback` | 异常被catch或非RuntimeException | 抛出RuntimeException，@Transactional(rollbackFor=Exception.class) |
| `MySQLNonTransientConnectionException` | 数据库连接超时 | 配置连接池，检查wait_timeout |
|端口被占用| 8080被其他进程占用 | `netstat -ano \| findstr 8080` 找到PID杀掉，或改端口 |
| `401 Unauthorized` | Token缺失/过期/错误 | 检查Authorization头，Token是否有效 |
| `403 Forbidden` | 认证了但无权限 | 检查用户角色和接口权限配置 |
| `500 Internal Server Error` | 服务端异常 | 看日志堆栈，定位具体异常 |

---

## 二、Vue3/前端

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `Cannot read properties of undefined` | 访问了undefined的属性 | 用可选链`?.`，v-if判断，初始化默认值 |
| 响应式不生效 | 直接替换reactive对象/解构丢失 | 用`ref`，或`Object.assign`，用`toRefs`解构 |
| `v-model`不更新 | 自定义组件未正确实现 | 组件内用`defineModel`或`props.modelValue`+`emit('update:modelValue')` |
| 页面白屏 | JS报错/路由配置错 | F12看控制台，检查router配置 |
| 样式不生效 | scoped样式/优先级不够 | 用`:deep()`穿透，提高选择器优先级，检查类名 |
| `npm install`失败 | 网络/镜像/版本冲突 | 切淘宝镜像`npm config set registry https://registry.npmmirror.com`，删node_modules重装 |
| 热更新不生效 | Vite缓存/文件路径 | 重启dev server，检查文件名大小写 |
| `CORS error` | 跨域 | 后端配置CORS，或前端配置proxy代理 |
| 内存溢出`heap out of memory` | 构建时内存不足 | `NODE_OPTIONS=--max-old-space-size=4096` |

---

## 三、Python

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `ModuleNotFoundError` | 模块未安装/路径不对 | `pip install`，检查PYTHONPATH，虚拟环境是否激活 |
| `IndentationError` | 缩进不一致 | 统一用4空格，不要Tab和空格混用 |
| `TypeError: 'NoneType' object` | 函数返回None就调用 | 检查函数是否有return，加None判断 |
| `KeyError` | 字典key不存在 | 用`.get(key, default)`，或先`in`判断 |
| `pip install`慢 | 网络问题 | 用国内镜像`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| 虚拟环境不生效 | 没激活/用了系统Python | `source venv/bin/activate`（Windows: `venv\Scripts\activate`） |
| `asyncio`报错 | 异步函数没await/事件循环 | 确认所有async函数都await了，检查事件循环 |

---

## 四、MySQL/数据库

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `Access denied for user` | 用户名/密码错/权限不足 | 检查账号密码，GRANT授权 |
| `Too many connections` | 连接数满了 | 增大max_connections，检查连接池配置，关闭空闲连接 |
| `Lock wait timeout exceeded` | 行锁等待超时 | 检查长事务，优化SQL，缩短事务 |
| `Deadlock found` | 死锁 | 统一加锁顺序，缩短事务，`SHOW ENGINE INNODB STATUS`分析 |
| 慢查询 | 没索引/SQL写得差 | `EXPLAIN`分析，加索引，优化SQL |
| `Duplicate entry` | 唯一键冲突 | 检查数据，用`INSERT ... ON DUPLICATE KEY UPDATE` |
| 中文乱码 | 字符集不对 | 数据库/表/连接都用utf8mb4 |

---

## 五、Docker/K8s

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 容器启动后立即退出 | 前台进程退出 | CMD用前台进程，不要用后台运行 |
| `port is already allocated` | 端口被占用 | 换端口，或`docker ps`找到占用容器停掉 |
| 镜像构建慢 | 网络/缓存未利用 | 用国内镜像源，合理排序Dockerfile层利用缓存 |
| `CrashLoopBackOff` | Pod反复崩溃 | `kubectl logs <pod>`看日志，`kubectl describe pod`看事件 |
| `ImagePullBackOff` | 镜像拉取失败 | 检查镜像名/标签，私有仓库需配置secret |
| `OOMKilled` | 内存超限 | 增大resources.limits.memory，或优化内存使用 |
| `Connection refused` | 服务未启动/端口不对 | 检查容器内服务是否启动，端口映射是否正确 |

---

## 六、Git

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 提交错分支 | 没切分支就提交 | `git stash` → 切分支 → `git stash pop` |
| 提交了敏感信息 | 不小心提交了密码/密钥 | 立即改密码，`git filter-repo`清除历史，强制推送 |
| 冲突解决不了 | 多人改同一文件 | 仔细看`<<<<<<<`标记，手动合并，或`git checkout --theirs/--ours` |
| `detached HEAD` | 直接checkout了commit | `git switch -c new-branch`创建分支保存 |
| 想撤销最后一次提交 | 提交错了 | `git reset --soft HEAD~1`（保留修改）或`--hard`（丢弃修改） |
| `push rejected` | 远程有新提交 | 先`git pull --rebase`再push |

---

## 七、AI/LLM

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `401 Unauthorized` | API Key错误/过期/无余额 | 检查Key，确认账户有余额 |
| `429 Too Many Requests` | 请求频率超限 | 降低频率，加指数退避重试 |
| `context_length_exceeded` | 超过模型上下文窗口 | 截断历史对话，用支持更长上下文的模型 |
| 回答内容不对 | Prompt描述不清 | 更详细描述需求，给示例，调整temperature |
| 模型幻觉 | AI编造信息 | 要求给出处，关键信息人工核实，用RAG增强 |
| 流式输出中断 | 网络中断/超时 | 实现断线重连，记录已接收内容 |
| API调用慢 | 模型大/网络差 | 换更快的模型，检查网络，用就近节点 |

---

## 八、通用排查思路

1. **看错误信息**：先读完整的错误堆栈，定位第一行Caused by
2. **复现问题**：稳定复现才能定位
3. **二分法**：注释掉一半代码，逐步缩小范围
4. **查日志**：应用日志、系统日志、网络日志
5. **搜索引擎**：复制错误信息搜索，90%的问题别人遇到过
6. **问AI**：把错误信息和相关代码发给AI，让它分析

---

## 关联笔记
[[新手第一天入门指南]] · [[全栈+AI工程双轨融合学习路线图]] · [[面试准备与求职指南]]

> 💡 **提示**：遇到报错不要慌，先读错误信息，再搜索，最后才问人。培养独立排查问题的能力比记住答案更重要。
