# -*- coding: utf-8 -*-
"""第六批补充：遗漏的知识点深度解析"""
import os, sys
ENGINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "01-前端开发")
sys.path.insert(0, ENGINE_DIR)
from engine import expand

BASE = os.path.dirname(os.path.abspath(__file__))

supplement = {
    # MyBatis-Plus
    "### 3.8 常见问题排查": (
        "汇总 MyBatis-Plus 开发中的常见问题及解决方案，提升排错效率。",
        "常见问题：① 字段不对应（驼峰映射未开启或字段名不匹配，检查 map-underscore-to-camel-case 和 @TableField）；② 逻辑删除不生效（未配置 logic-delete-field 或注解）；③ 分页不生效（未配置 MybatisPlusInterceptor 分页插件）；④ 主键策略错误（@TableId type 设为 IdType.AUTO/ASSIGN_ID）；⑤ 批量插入慢（saveBatch 本质是循环单条，真正批量用 rewriteBatchedStatements=true）。",
        ["分页必须配置 MybatisPlusInterceptor + PaginationInnerInterceptor", "map-underscore-to-camel-case 默认开启，字段不匹配检查 @TableField", "逻辑删除需配置 logic-delete-field 和 logic-delete-value", "JDBC URL 加 rewriteBatchedStatements=true 让批量插入真正合并", "面试常考：分页插件原理、逻辑删除实现、批量插入优化"]
    ),
    # Spring Boot
    "### 3.7 打包与部署": (
        "Spring Boot 打包为可执行 JAR/WAR，通过 java -jar 或容器部署，支持多环境配置。",
        "spring-boot-maven-plugin 将应用打包为 fat JAR（内嵌 Tomcat），java -jar app.jar 启动。可执行 JAR 内部用 JarLauncher 加载 BOOT-INF/classes 和 BOOT-INF/lib。多环境用 --spring.profiles.active=prod 指定。Docker 部署用 eclipse-temurin/jre 基础镜像，分层构建优化镜像缓存。JVM 参数通过 JAVA_OPTS 环境变量传递。",
        ["mvn package 打 fat JAR，java -jar 启动", "java -jar app.jar --spring.profiles.active=prod", "Docker 分层构建：依赖层和应用层分离，利用缓存", "JVM 参数：-Xms/-Xmx/-XX:+UseG1GC，通过 JAVA_OPTS 传入", "面试常考：fat JAR 原理、JarLauncher、多环境部署、Docker 最佳实践"]
    ),
    # Spring Cloud
    "### 3.1 Nacos 服务注册": (
        "Nacos 作为服务注册中心，微服务启动时注册实例，消费者通过 Nacos 发现服务提供者。",
        "服务启动时 Nacos Client 向 Server 发送注册请求（IP/端口/服务名/元数据），维持心跳（5s 间隔，15s 未标记不健康，30s 摘除）。消费者从 Nacos 拉取服务列表并本地缓存，通过定时任务（10s）更新。Nacos 支持 AP/CP 切换（临时实例 AP Distro 协议，持久实例 CP Raft）。Spring Cloud LoadBalancer 从本地服务列表选择实例。",
        ["临时实例（默认）AP 模式，Distro 协议，心跳续约", "持久实例 CP 模式，Raft 协议，主动检测", "消费者本地缓存服务列表，Nacos 宕机仍可消费", "服务发现：@LoadBalanced + RestTemplate/OpenFeign", "面试常考：Nacos 注册流程、AP/CP 切换、心跳机制、与 Eureka 区别"]
    ),
    "### 3.6 分布式事务（Seata）": (
        "Seata 在 Spring Cloud 微服务架构中提供 AT/TCC/SAGA/XA 四种分布式事务模式。",
        "Seata 架构：TC（事务协调器，独立 Server）、TM（事务管理器，发起方）、RM（资源管理器，参与方）。@GlobalTransactional 标注全局事务发起方法，TM 向 TC 注册全局事务（XID），XID 通过请求头传播到各微服务，各分支事务注册到 TC。AT 模式一阶段各分支本地提交+注册分支，二阶段 TC 通知提交/回滚。Spring Cloud 中需引入 seata-spring-boot-starter 并配置 Nacos 注册中心。",
        ["TC/TM/RM 三角色，XID 贯穿全链路", "AT 模式最常用：undo_log 自动补偿，无侵入", "XID 通过 Feign 请求头拦截器传播", "高并发场景优先 TCC，长流程用 SAGA", "面试常考：Seata 架构、AT 模式、XID 传播、与本地消息表对比"]
    ),
    # MySQL
    "### 3.4 备份与恢复": (
        "MySQL 备份策略包括逻辑备份（mysqldump）、物理备份（XtraBackup）和 binlog 时间点恢复。",
        "mysqldump：逻辑备份，导出 SQL 语句，适合小库和跨版本迁移，--single-transaction 保证 InnoDB 一致性。XtraBackup：物理热备份，拷贝数据文件，不锁表，适合大库。binlog：记录所有更改操作，用于时间点恢复（PITR）：全量备份+重放 binlog 到指定时间点。恢复策略：定期全量+增量 binlog，定期演练恢复。",
        ["mysqldump --single-transaction 一致性逻辑备份", "XtraBackup 物理热备，不锁表，适合大库", "PITR：全量恢复 + mysqlbinlog 重放到指定时间点", "binlog_format=ROW 便于数据恢复和同步", "面试常考：mysqldump vs XtraBackup、PITR、binlog 恢复"]
    ),
    # 消息队列
    "### 3.8 MQ 监控与运维": (
        "MQ 监控覆盖消息堆积、消费延迟、吞吐量和死信队列，运维关注分区均衡和消息回溯。",
        "Kafka 监控：Consumer Lag（消费滞后量）是核心指标，通过 JMX 或 Kafka Monitor 采集；UnderReplicatedPartitions 检测副本同步异常。RocketMQ 监控：消费 TPS、堆积量、消息延迟。运维操作：分区重平衡（Kafka reassign-partitions）、消息回溯（按时间/offset 重置消费位点）、死信队列重放、Topic 扩分区。",
        ["Consumer Lag 是最核心告警指标，反映消费能力不足", "Kafka UnderReplicatedPartitions>0 说明副本同步异常", "消息回溯：重置 offset 到指定时间点重新消费", "死信队列需监控和人工处理，避免静默丢失", "面试常考：消息堆积处理、消费监控、消息回溯、分区重平衡"]
    ),
    # Kubernetes
    "### 3.8 常用 kubectl 命令": (
        "kubectl 是 K8s 命令行工具，覆盖资源查看、编辑、扩缩容、日志和调试操作。",
        "常用命令：kubectl get pods/services/deployments 查看资源（-o wide 显示 IP/节点，-w 监听变化）；kubectl describe 查看事件详情（排查调度失败）；kubectl logs 查看容器日志（-f 跟踪，--previous 看上一个崩溃容器）；kubectl exec 进入容器；kubectl scale 扩缩容；kubectl rollout status/undo 管理发布；kubectl apply -f 声明式更新。",
        ["kubectl get pods -A 查看所有命名空间 Pod", "kubectl describe pod <name> 查看事件排障", "kubectl logs -f <pod> 实时日志，--previous 崩溃前日志", "kubectl exec -it <pod> -- bash 进入容器", "面试常考：kubectl 常用命令、Pod 排障流程、日志查看"]
    ),
    # Service Mesh
    "### 3.1 Istio 安装与注入": (
        "Istio 安装通过 istioctl 或 Helm 部署控制面，Sidecar 注入支持自动和手动两种方式。",
        "istioctl install 安装 istiod 控制面（Pilot/Citadel/Galley 整合）。自动注入：命名空间加 label istio-injection=enabled，准入 Webhook 在 Pod 创建时自动注入 istio-proxy（Envoy）Sidecar。手动注入：istioctl kube-inject -f deployment.yaml | kubectl apply -f。注入后 Pod 中业务容器与 Envoy 共享网络命名空间（iptables 拦截所有进出流量到 Envoy）。",
        ["istioctl install --set profile=demo 安装", "命名空间 label istio-injection=enabled 开启自动注入", "Sidecar 与业务容器共享网络命名空间", "iptables 透明拦截所有流量到 Envoy", "面试常考：Sidecar 注入原理、iptables 拦截、istiod 组件"]
    ),
    # JVM
    "### 3.1 JVM 启动参数": (
        "JVM 启动参数控制堆内存、垃圾回收器、日志和调试选项，是性能调优的入口。",
        "堆内存：-Xms 初始堆、-Xmx 最大堆（生产设相同值避免动态扩缩）、-Xmn 新生代、-XX:MetaspaceSize 元空间。GC：-XX:+UseG1GC（JDK9+ 默认）、-XX:MaxGCPauseMillis 目标暂停时间。日志：-Xlog:gc*（JDK9+ 统一日志）。诊断：-XX:+HeapDumpOnOutOfMemoryError 自动 dump、-XX:HeapDumpPath 指定路径。",
        ["-Xms 和 -Xmx 设相同值，避免堆动态扩缩开销", "-XX:+UseG1GC JDK9+ 默认，低延迟；ZGC/Shenandoah 超低延迟", "-XX:+HeapDumpOnOutOfMemoryError OOM 时自动 dump", "-Xlog:gc*:file=gc.log:time,uptime,level,tags JDK9+ GC 日志", "面试常考：堆参数配置、GC 选择、OOM dump、JDK9+ 日志参数"]
    ),
    "### 3.3 GC 调优": (
        "GC 调优目标是降低停顿时间和提高吞吐量，核心是调整堆大小、新生代比例和 GC 器参数。",
        "调优步骤：① 开启 GC 日志分析停顿频率和耗时 ② 根据场景选 GC（Web 应用 G1/ZGC 低延迟，批处理 ParallelGC 高吞吐）③ 调整堆大小（Xmx 设为物理内存 70%，留元空间和直接内存）④ 调整新生代比例（G1 不用手动设新生代，用 MaxGCPauseMillis 自适应）⑤ 避免 Full GC（大对象直接进老年代、元空间不足、System.gc()）。",
        ["先监控再调优：GC 日志+APM 工具分析，不盲目调参", "G1 调 MaxGCPauseMillis 和 ParallelGCThreads", "避免 Full GC：控制大对象、元空间大小、禁用显式 GC", "ZGC/Shenandoah 适合 TB 级堆和亚毫秒停顿", "面试常考：GC 调优流程、G1 参数、Full GC 原因、停顿 vs 吞吐"]
    ),
    "### 3.7 OOM 与 StackOverflow 排查": (
        "OOM 和 StackOverflow 是 JVM 常见内存错误，需根据错误类型定位原因并修复。",
        "OOM 类型：Java heap space（堆内存不足，内存泄漏或堆太小，用 MAT 分析 dump）、Metaspace（类加载过多/泄漏，检查动态类生成）、GC overhead limit（GC 耗时占比>98% 但回收<2%）、Direct buffer memory（直接内存不足，NIO/Netty）、unable to create native thread（线程数超限）。StackOverflow：递归过深或方法调用链太长。排查：jmap dump + MAT 分析 dominator tree，jstack 看线程。",
        ["Heap OOM：MAT 分析 dominator tree 找大对象和泄漏点", "Metaspace OOM：检查 CGLIB/动态代理/热部署类加载泄漏", "GC overhead：98% 时间 GC 但只回收 2%，通常是堆快满了", "StackOverflow：检查递归终止条件和调用深度", "面试常考：OOM 类型、MAT 分析、jstack/jmap 用法、内存泄漏定位"]
    ),
    "### 3.8 JFR 飞行记录器": (
        "JFR（Java Flight Recorder）是 JDK 内置的低开销性能采集工具，持续记录 JVM 运行时事件用于诊断。",
        "JFR 采集线程调度、GC、锁竞争、IO、方法采样等事件，开销 <1%，可在生产环境常开。启动时 -XX:StartFlightRecording=duration=60s,filename=app.jfr，运行时 jcmd <pid> JFR.start/start/dump。用 JMC（JDK Mission Control）可视化分析。JFR 适合生产环境性能分析，比传统 profiler 开销低得多。",
        ["-XX:StartFlightRecording 启动时开启，jcmd 运行时控制", "开销 <1%，可生产环境常开", "JMC 可视化分析：GC/锁/IO/方法热点", "jcmd <pid> JFR.dump 导出当前记录", "面试常考：JFR 原理、与 async-profiler 对比、生产性能分析"]
    ),
    # AI Agent 实战
    "### 2.3 检索优化": (
        "检索优化通过查询改写、混合检索、重排序和上下文压缩提升 RAG 检索质量。",
        "查询改写：将口语化/指代模糊的问题改写为检索友好的查询（LLM 改写、HyDE 假设文档）。混合检索：向量检索（语义）+ BM25（关键词）结合，Reciprocal Rank Fusion（RRF）融合排序。重排序：Cross-encoder reranker 对 top-20 候选精排（比 bi-encoder 准但慢）。上下文压缩：去除检索文档中的无关段落，只保留与问题相关的句子。元数据过滤：按时间/类别/来源预过滤。",
        ["HyDE：先让 LLM 生成假设答案，用假设答案 embedding 检索", "混合检索：向量+BM25，RRF 融合排序", "Reranker：Cross-encoder 精排 top-20→top-5", "上下文压缩：LLM 提取检索文档中的相关片段", "面试常考：检索优化手段、HyDE、混合检索、reranker、RRF"]
    ),
    # AI Agent 核心概念 - #### headings
    "#### 1. 规划（Planning）": (
        "规划是 Agent 的决策核心，将复杂目标分解为可执行子任务并动态调整策略。",
        "规划能力来自 LLM 的推理能力：任务分解（将大目标拆为小步骤）、反思修正（根据执行结果调整计划）、多路径探索（ToT 思维树评估多条路径）。规划方法包括 ReAct（边想边做）、Plan-and-Execute（先规划后执行）、Reflexion（反思迭代）。规划质量取决于 LLM 推理能力、任务可分解性和反馈准确性。",
        ["任务分解：大目标→子任务→可执行步骤", "反思修正：执行失败后重新规划", "ToT 探索多条路径并评估选择", "简单任务不需要复杂规划，ReAct 即可", "面试常考：规划方法、任务分解、ReAct vs Plan-Execute"]
    ),
    "#### 2. 记忆（Memory）": (
        "记忆让 Agent 跨会话保留信息，分为短期工作记忆和长期持久记忆。",
        "短期记忆即上下文窗口中的对话历史和中间状态，容量受 token 限制，需摘要压缩。长期记忆用向量数据库持久化（对话历史、用户偏好、执行经验），通过 RAG 语义检索按需召回。记忆管理包括写入策略（重要性判断）、遗忘机制（TTL/低频归档）和摘要压缩（旧记忆合并）。",
        ["短期记忆=上下文窗口，容量有限", "长期记忆=向量数据库，RAG 检索召回", "记忆写入需判断重要性，避免噪声", "摘要压缩释放上下文空间", "面试常考：短期 vs 长期记忆、记忆管理、RAG 记忆"]
    ),
    # Obsidian 软件基础
    "### 2.4 双向链接": (
        "双向链接是 Obsidian 的核心特性，[[]] 创建链接，自动维护反向链接和关系图谱。",
        "输入 [[ 触发笔记补全，选择笔记创建链接。链接显示为可点击文本，Ctrl+点击打开目标笔记。Backlinks 面板显示所有链接到当前笔记的笔记（反向链接）。Outgoing Links 面板显示当前笔记的出链。链接不存在时显示为紫色虚线，点击可创建。关系图谱（Graph View）可视化所有笔记和链接，可按标签/文件夹着色过滤。",
        ["[[笔记名]] 创建链接，[[笔记名|显示名]] 自定义显示文本", "Backlinks 面板自动显示反向链接", "链接不存在时点击可快速创建新笔记", "Graph View 可视化知识网络，支持过滤和着色", "双向链接是 Obsidian 区别于传统笔记工具的核心"]
    ),
    "### 4.3 外观与体验": (
        "Obsidian 外观定制包括主题、字体、暗色模式和 CSS 片段，打造舒适的写作环境。",
        "设置→外观中选择主题（社区市场有 Things/Blue Topaz/Minimal 等），支持亮/暗模式自动切换。字体可分别设置界面字体和正文字体（推荐等宽字体写代码）。CSS 片段放在 .obsidian/snippets/ 目录，在设置中启用，可自定义行宽、标题编号、标签颜色等。Style Settings 插件为支持的主题提供可视化配置面板。",
        ["主题市场：Things/Blue Topaz/Minimal 等流行主题", "亮/暗模式可定时自动切换", "CSS 片段精确自定义样式，不修改主题文件", "Style Settings 插件可视化配置主题参数", "推荐：正文字体用 Inter/LXGW，代码用 JetBrains Mono"]
    ),
    "### 4.4 同步与备份": (
        "Obsidian 同步方案包括官方 Sync、Git、iCloud/Syncthing 和文件系统备份，确保数据安全。",
        "Obsidian Sync：官方付费，端到端加密，版本历史，跨平台最省心。Git：obsidian-git 插件自动 commit/push，版本历史完整，适合技术用户。iCloud：Apple 生态免费但仅限 Apple 设备。Syncthing：免费 P2P 全平台。文件备份：定期复制 Vault 到外部存储/网盘。推荐组合：Git 版本控制 + 定期云备份。",
        ["Obsidian Sync 最省心，端到端加密，付费", "obsidian-git：自动版本控制，技术用户首选", "iCloud 免费但 Apple 专属，Syncthing 免费全平台", "3-2-1 备份原则：3 份副本、2 种介质、1 份异地", "定期验证备份可恢复，避免备份了但无法使用"]
    ),
    # Obsidian 方法论
    "### 2.2 PARA 在 Obsidian 中的实现": (
        "在 Obsidian 中用文件夹+MOC+标签实现 PARA 方法，将笔记按可行动性组织。",
        "创建 1-Projects/、2-Areas/、3-Resources/、4-Archive/ 四个文件夹。项目笔记包含目标、任务列表和进度（Dataview 查询）。领域笔记是持续更新的主题 MOC。资源笔记是参考材料。完成的项目从 Projects 移入 Archive。Inbox 作为新内容入口，每周回顾时归入 P/A/R。标签补充标记状态（#status/active）。",
        ["四个文件夹对应 P/A/R/A，Inbox 作为入口", "项目笔记含目标/任务/截止日期，Dataview 聚合", "完成项目移入 Archive，保持 Projects 精简", "每周回顾：Inbox→P/A/R，项目进度检查", "MOC 可跨文件夹组织，不局限于 PARA 结构"]
    ),
    # Prompt 工程
    "### 2.2 提供上下文": (
        "在 Prompt 中提供充分背景信息（项目情况、约束条件、相关数据），让 LLM 给出贴合实际的回答。",
        "LLM 不知道你的项目背景，必须在 Prompt 中提供：技术栈版本、业务场景、已有代码、错误信息、约束条件。上下文越具体，回答越精准。技巧：用分隔符区分背景和任务、提供相关代码片段而非描述、给出数据样例、说明已尝试的方案。长上下文需注意 Token 预算，只提供相关信息。",
        ["提供技术栈、版本、业务场景等背景", "粘贴错误信息和相关代码，而非口头描述", "用分隔符（```/---）区分背景和指令", "说明已尝试的方案和结果，避免重复建议", "上下文质量决定回答质量，垃圾进垃圾出"]
    ),
    "### 2.3 指定角色": (
        "角色设定让 LLM 以特定专家身份和视角回答，提升专业领域输出质量。",
        "在 Prompt 开头指定角色：'你是资深 Java 架构师'、'你是有 10 年经验的前端工程师'、'你是技术文档翻译专家'。角色设定影响 LLM 的词汇选择、深度和关注点。可组合角色+技能+经验年限。配合系统提示（System Prompt）持久化角色设定。角色越具体（领域+经验+风格），输出越专业。",
        ["'你是 XX 专家'赋予专业视角", "角色+经验年限+技能组合更精确", "System Prompt 中固化角色，对话全程生效", "可要求角色用特定思维框架思考", "适合专业领域：代码审查、架构设计、医学/法律咨询"]
    ),
    "### 2.4 设定输出格式": (
        "明确指定输出格式（Markdown/JSON/表格/代码），让 LLM 输出可直接使用的结构化结果。",
        "指定格式：'用 Markdown 表格输出'、'返回 JSON，字段为...'、'先给代码再给解释'。提供格式示例或模板效果更好。JSON 输出可指定 Schema（字段名/类型/必填）。复杂格式可给 few-shot 示例。结构化输出便于程序解析（API 场景用 JSON mode 或 Function Calling）。",
        ["明确格式：Markdown/JSON/表格/代码块", "JSON 输出指定字段名和类型，API 场景用 JSON mode", "提供格式模板或示例，比文字描述更准确", "代码输出指定语言和注释要求", "结构化输出可直接被程序消费，减少后处理"]
    ),
    # 生成式 AI
    "### 2.3 自注意力机制": (
        "自注意力（Self-Attention）让序列中每个 token 关注所有其他 token，并行计算加权表示，是 Transformer 的核心。",
        "每个 token 映射为 Query、Key、Value 三个向量。Attention(Q,K,V) = softmax(QK^T/√d_k)V：Q 与所有 K 计算点积得到注意力分数，除以 √d_k 防止梯度消失，softmax 归一化为权重，对 V 加权求和。多头注意力将 Q/K/V 分成多组并行计算不同子空间的注意力，拼接后线性变换。自注意力复杂度 O(n²)，但可并行（RNN 是 O(n) 串行）。",
        ["QK^T 计算 token 间相关性，softmax 归一化", "除以 √d_k 防止点积过大导致 softmax 梯度消失", "多头注意力：多组 Q/K/V 关注不同语义关系", "O(n²) 复杂度，长序列优化：FlashAttention/稀疏注意力", "面试常考：QKV 含义、注意力公式、多头注意力、复杂度"]
    ),
    # 主流大模型
    "### 3.1 模型对比": (
        "从能力、速度、成本、上下文长度和开源/闭源等维度对比主流模型，按场景选型。",
        "GPT-4o/Claude 3.5 Opus 能力最强但最贵最慢，适合复杂推理和多模态。Claude 3.5 Sonnet/GPT-4o-mini 性价比高，适合日常开发和写作。开源模型（Llama 3/Qwen/DeepSeek）可私有部署，适合数据敏感场景。选型维度：推理能力（MMLU/GSM8K）、编码（HumanEval/SWE-bench）、上下文长度、延迟、价格、隐私要求。简单任务用小模型，复杂任务用大模型，路由策略降本。",
        ["旗舰模型：GPT-4o/Claude Opus/Gemini Pro，复杂任务", "性价比模型：GPT-4o-mini/Claude Sonnet/Haiku，日常任务", "开源模型：Llama 3/Qwen2.5/DeepSeek，私有部署", "选型看：能力基准+延迟+价格+上下文+隐私", "模型路由：简单任务小模型，复杂任务大模型，降本 50%+"]
    ),
}


def run():
    # Map heading to file path
    heading_to_file = {
        "### 3.8 常见问题排查": r"02-后端开发\MyBatis-Plus 知识点系统梳理_优化版.md",
        "### 3.7 打包与部署": r"02-后端开发\Spring Boot 知识点系统梳理_优化版.md",
        "### 3.1 Nacos 服务注册": r"02-后端开发\Spring Cloud微服务 知识点系统梳理_优化版.md",
        "### 3.6 分布式事务（Seata）": r"02-后端开发\Spring Cloud微服务 知识点系统梳理_优化版.md",
        "### 3.4 备份与恢复": r"03-数据库与缓存\MySQL 知识点系统梳理_优化版.md",
        "### 3.8 MQ 监控与运维": r"04-分布式与中间件\消息队列深度 知识点系统梳理_优化版.md",
        "### 3.8 常用 kubectl 命令": r"05-云原生与运维\Kubernetes 知识点系统梳理_优化版.md",
        "### 3.1 Istio 安装与注入": r"05-云原生与运维\Service Mesh 知识点系统梳理_优化版.md",
        "### 3.1 JVM 启动参数": r"06-计算机基础\JVM 知识点系统梳理_优化版.md",
        "### 3.3 GC 调优": r"06-计算机基础\JVM 知识点系统梳理_优化版.md",
        "### 3.7 OOM 与 StackOverflow 排查": r"06-计算机基础\JVM 知识点系统梳理_优化版.md",
        "### 3.8 JFR 飞行记录器": r"06-计算机基础\JVM 知识点系统梳理_优化版.md",
        "### 2.3 检索优化": r"09-AI与效率工具\AI Agent实战与能力优化知识点系统梳理_优化版.md",
        "#### 1. 规划（Planning）": r"09-AI与效率工具\AI Agent核心概念与架构知识点系统梳理_优化版.md",
        "#### 2. 记忆（Memory）": r"09-AI与效率工具\AI Agent核心概念与架构知识点系统梳理_优化版.md",
        "### 2.4 双向链接": r"09-AI与效率工具\Obsidian软件基础与核心插件知识点系统梳理_优化版.md",
        "### 4.3 外观与体验": r"09-AI与效率工具\Obsidian软件基础与核心插件知识点系统梳理_优化版.md",
        "### 4.4 同步与备份": r"09-AI与效率工具\Obsidian软件基础与核心插件知识点系统梳理_优化版.md",
        "### 2.2 PARA 在 Obsidian 中的实现": r"09-AI与效率工具\Obsidian知识管理方法论与工作流知识点系统梳理_优化版.md",
        "### 2.2 提供上下文": r"09-AI与效率工具\Prompt工程知识点系统梳理_优化版.md",
        "### 2.3 指定角色": r"09-AI与效率工具\Prompt工程知识点系统梳理_优化版.md",
        "### 2.4 设定输出格式": r"09-AI与效率工具\Prompt工程知识点系统梳理_优化版.md",
        "### 2.3 自注意力机制": r"09-AI与效率工具\生成式AI原理与应用知识点系统梳理_优化版.md",
        "### 3.1 模型对比": r"09-AI与效率工具\主流大模型与AI工具知识点系统梳理_优化版.md",
    }

    # Group by file
    from collections import defaultdict
    file_maps = defaultdict(dict)
    for heading, content in supplement.items():
        fpath = heading_to_file[heading]
        file_maps[fpath][heading] = content

    for fpath, cmap in file_maps.items():
        full_path = os.path.join(BASE, fpath)
        lines, added = expand(full_path, cmap, False, False, "")
        print(f"  {os.path.basename(fpath)}: {lines} lines, {added} blocks added")


if __name__ == "__main__":
    run()
