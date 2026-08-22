# -*- coding: utf-8 -*-
"""第四批扩展：AI与效率工具（8个文件）"""
import os, sys
ENGINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "01-前端开发")
sys.path.insert(0, ENGINE_DIR)
from engine import expand

BASE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# AI Agent 核心概念与架构
# ============================================================
agent_core = {
    "### 2.1 感知-决策-执行循环": (
        "Agent 通过感知环境输入、LLM 决策规划、执行工具调用并观察结果的循环，自主完成多步骤任务。",
        "循环从接收用户目标开始：感知模块收集环境信息（用户输入、工具返回、上下文），LLM 作为决策核心进行推理（Thought）选择行动（Action），执行器调用工具获取观察结果（Observation），结果反馈给 LLM 继续推理，直到任务完成或达到终止条件。这个循环本质是 ReAct 范式的工程化，每轮 LLM 调用都是一次无状态推理，状态由外部消息历史维护。",
        ["循环由 LLM 推理驱动，每轮包含 Thought→Action→Observation", "需要设置最大循环次数和终止条件，防止无限循环", "工具返回结果过长时需截断或摘要，避免上下文爆炸", "可在循环中加入人工确认节点（Human-in-the-loop）", "面试常考：Agent 循环流程、ReAct 模式、终止条件设计、状态管理"]
    ),
    "### 3.1 ReAct（Reasoning + Acting）": (
        "ReAct 将推理（Thought）和行动（Action）交替进行，让 LLM 边思考边调用工具，是 Agent 最经典的范式。",
        "ReAct 提示 LLM 按 Thought→Action→Observation 格式输出：Thought 分析当前状态和下一步计划，Action 输出工具调用（JSON），系统执行工具返回 Observation，LLM 据此继续 Thought。这种交错模式让 LLM 的推理链与外部信息交互，比纯推理（CoT）更准确（能获取实时信息），比纯行动更可控（有显式推理链可追溯）。",
        ["Thought→Action→Observation 循环，推理链可追溯", "比纯 CoT 更准确：可获取外部信息纠正推理", "Action 必须是结构化工具调用，系统解析后执行", "Observation 是工具返回结果，拼接到上下文供下轮推理", "面试常考：ReAct 原理、与 CoT 区别、提示词格式、ReAct 优缺点"]
    ),
    "### 3.2 Plan-and-Execute": (
        "先由 Planner 一次性制定完整执行计划，再由 Executor 逐步执行，适合目标明确的复杂任务。",
        "Plan-and-Execute 将规划和执行分离：Planner LLM 接收目标后生成有序步骤列表（Plan），Executor 逐个执行每个步骤（可调用工具或子 Agent），执行完后可由 Replanner 检查结果并调整剩余计划。这种模式减少了 LLM 调用次数（不需要每步都重新规划），但灵活性不如 ReAct，适合步骤明确的工作流。",
        ["Planner 生成步骤列表，Executor 逐步执行，Replanner 检查调整", "比 ReAct 减少 LLM 调用次数，Token 成本更低", "计划可能因环境变化而失效，需要重规划机制", "适合报告生成、数据处理等步骤明确的任务", "面试常考：Plan-and-Execute vs ReAct、规划执行分离、重规划"]
    ),
    "### 3.3 Reflexion（反思型 Agent）": (
        "Agent 执行任务后进行自我反思，将经验教训存入记忆，在后续尝试中改进，实现迭代提升。",
        "Reflexion 在 Actor（执行）基础上增加 Evaluator（评估结果）和 Self-Reflection（反思失败原因）：执行失败后，LLM 分析失败原因生成反思文本，存入长期记忆。下次尝试时将历史反思作为上下文，避免重复犯错。反思内容是自然语言（而非参数更新），相当于让 LLM 从经验中学习。",
        ["Actor 执行→Evaluator 评估→Self-Reflection 反思→记忆→重试", "反思是自然语言经验，不更新模型参数", "适合代码调试、数学推理等可验证对错的任务", "反思记忆需控制数量，避免上下文过长", "面试常考：Reflexion 机制、与微调区别、反思记忆、迭代提升"]
    ),
    "### 4.1 原理": (
        "Function Calling 让 LLM 输出结构化的工具调用请求，系统执行后将结果返回 LLM，实现 LLM 与外部世界的交互。",
        "开发者在 API 请求中提供 tools 定义（name/description/parameters JSON Schema），LLM 训练时学会在需要时输出 tool_calls 结构（函数名+参数 JSON），而非自然语言。应用解析 tool_calls 执行对应函数，将结果以 role=tool 消息返回，LLM 根据结果继续生成。这本质是 LLM 做了参数提取和路由决策，实际执行由应用代码完成。",
        ["tools 定义包含 name/description/parameters（JSON Schema）", "LLM 输出 tool_calls，应用解析执行后返回 role=tool 消息", "description 质量直接影响 LLM 选择工具的准确性", "并行工具调用：一次返回多个 tool_calls", "面试常考：Function Calling 原理、工具定义、执行流程、与 RAG 区别"]
    ),
    "### 4.2 常用工具类型": (
        "Agent 可调用搜索、代码执行、API、文件操作、浏览器、数据库、向量检索等工具扩展能力边界。",
        "搜索工具获取实时信息（弥补知识截止），代码执行工具进行精确计算和数据处理（Python REPL），API 工具调用外部服务（天气/支付/CRM），文件工具读写文档，浏览器工具操作网页（Playwright），数据库工具执行 SQL，向量检索工具实现 RAG。工具设计原则：描述清晰、参数明确、粒度适中、错误信息友好。",
        ["搜索工具解决知识截止和实时信息问题", "代码执行工具解决 LLM 数学计算不可靠问题", "工具粒度适中：太粗 LLM 不会用，太细调用次数多", "每个工具应有清晰的 description 和参数说明", "面试常考：工具类型、工具设计原则、RAG 检索工具、代码执行沙箱"]
    ),
    "### 5.1 记忆层级": (
        "Agent 记忆分为感觉记忆、短期工作记忆和长期记忆，对应人类认知架构，解决上下文有限和知识持久化问题。",
        "感觉记忆是原始输入（用户消息、工具结果），短期记忆是当前上下文窗口中的对话历史和中间状态（容量有限，受 token 限制），长期记忆是外部持久化存储（向量数据库），通过语义检索按需召回。工作记忆是当前任务的临时状态（变量、步骤进度）。记忆管理需要摘要压缩（旧对话压缩为摘要）、重要性评分和遗忘机制。",
        ["短期记忆=上下文窗口，容量有限，需管理 token 预算", "长期记忆=向量数据库，通过 RAG 语义检索召回", "摘要压缩：将旧对话压缩为摘要释放上下文空间", "记忆写入需判断重要性，避免噪声污染记忆库", "面试常考：记忆层级、短期 vs 长期、摘要压缩、记忆管理"]
    ),
    "### 5.2 长期记忆实现": (
        "通过向量数据库持久化存储对话历史、用户偏好和知识，用 embedding 语义检索实现按需召回。",
        "实现流程：记忆内容经 embedding 模型转为向量存入向量库（Pinecone/Milvus/Chroma），检索时将当前查询向量化，用余弦相似度检索 top-k 相关记忆，拼接到 LLM 上下文。记忆管理包括：重要性评分（LLM 打分决定是否存储）、时效性（TTL 过期）、摘要（多条记忆合并）、遗忘（低频记忆归档）。",
        ["embedding 向量化 + 余弦相似度检索是核心", "记忆类型：情景记忆（事件）、语义记忆（知识）、程序性记忆（技能）", "重要性评分过滤低价值记忆，减少噪声", "用户偏好记忆可实现个性化（记住用户习惯）", "面试常考：向量检索原理、记忆 CRUD、重要性评分、记忆与 RAG 关系"]
    ),
    "### 5.3 RAG（检索增强生成）": (
        "RAG 通过检索外部知识库并将相关文档拼入提示词，让 LLM 基于准确信息生成回答，减少幻觉。",
        "RAG 流程：文档切分为 chunk → embedding 向量化存入向量库 → 用户问题向量化 → 相似度检索 top-k chunks → 将 chunks 拼入 prompt 作为上下文 → LLM 基于上下文生成回答并引用来源。高级 RAG 包括查询改写、混合检索（向量+关键词）、重排序（reranker）、多跳检索。RAG 解决知识截止、私有数据问答和幻觉问题。",
        ["文档切分策略：固定长度/语义切分/递归切分，重叠避免断句", "检索质量决定回答质量：chunk 大小、top-k、embedding 模型都影响", "混合检索（向量+BM25）+ reranker 提升召回准确率", "必须引用来源，让用户可验证", "面试常考：RAG 完整流程、chunk 策略、混合检索、reranker、RAG vs 微调"]
    ),
    "### 6.1 概念": (
        "Multi-Agent 系统由多个专业化 Agent 协作完成单 Agent 难以胜任的复杂任务，通过分工提升可靠性和质量。",
        "多 Agent 系统中每个 Agent 有独立角色（规划者/执行者/审查者）、工具集和记忆，通过消息传递协作。相比单 Agent，多 Agent 可并行处理子任务、互相校验（辩论/审查减少错误）、专业化分工（每个 Agent prompt 更聚焦）。但增加了 Token 成本、协调复杂度和调试难度。",
        ["角色专业化：每个 Agent 有明确职责和系统提示", "消息传递是 Agent 间通信方式（共享对话或定向消息）", "适合复杂任务：代码开发（架构师+程序员+测试）、研究报告", "成本和延迟随 Agent 数量增加，需权衡", "面试常考：Multi-Agent vs 单 Agent、协作模式、通信机制、适用场景"]
    ),
    "### 6.2 协作模式": (
        "多 Agent 协作有顺序流水线、并行、辩论、层级管理和自主协作等模式，按任务特点选择。",
        "顺序协作（流水线）：A→B→C 依次处理，前一个输出是后一个输入（研究→写作→校对）。并行协作：多个 Agent 同时处理后汇总（多源搜索）。辩论模式：多 Agent 互相质疑达成共识（提升准确性）。层级模式：Manager 分配任务给 Worker 并汇总。自主协作：Agent 自主决定与谁通信（AutoGen 群聊）。",
        ["顺序模式适合有明确阶段的任务（内容创作流水线）", "并行模式适合可独立的子任务（多源信息收集）", "辩论模式适合需要准确性的决策（多视角审查）", "层级模式适合复杂项目管理（Manager-Worker）", "面试常考：协作模式对比、CrewAI/AutoGen、消息路由、成本控制"]
    ),
    "### 6.3 典型架构（CrewAI）": (
        "CrewAI 等框架用角色化 Agent + 任务编排实现多 Agent 协作，定义 Agent 角色、目标和任务依赖。",
        "CrewAI 中定义 Agent（role/goal/backstory/tools）、Task（description/expected_output/agent）、Crew（agents/tasks/process）。Process 支持 sequential（顺序执行）和 hierarchical（层级管理，自动分配 Manager）。任务间可通过 context 传递输出。框架处理消息路由、工具调用和结果汇总，开发者只需定义角色和任务。",
        ["Agent 定义：role（角色）、goal（目标）、backstory（背景）、tools", "Task 定义：描述、期望输出、负责 Agent、依赖的上游 Task", "sequential 顺序执行，hierarchical 自动选 Manager 分配", "任务输出可作为下游任务的 context", "面试常考：CrewAI 架构、Agent/Task/Crew 关系、sequential vs hierarchical"]
    ),
    "## 8.1 Agent 类型分类": (
        "按智能水平从低到高分为反射型、基于模型、基于目标、基于效用和理性 Agent，体现 Agent 能力演进。",
        "反射型 Agent 直接根据感知做反应（无状态，类似 if-else）。基于模型的 Agent 维护内部世界状态模型。基于目标的 Agent 朝目标规划行动。基于效用的 Agent 在多个目标间评估效用选最优。理性 Agent 追求期望效用最大化（理论框架）。实际 LLM Agent 多为基于目标+效用的混合体。",
        ["反射型最简单但无记忆，基于模型型维护内部状态", "基于目标型能规划，基于效用型能权衡多目标", "LLM Agent 通常是目标导向 + 工具调用 + 记忆的组合", "分类来自 Russell & Norvig《人工智能》教材", "面试常考：Agent 类型分类、各类型特点、LLM Agent 属于哪种"]
    ),
    "## 8.2 规划算法": (
        "Agent 规划算法包括 HTN 层次任务网络、MCTS 蒙特卡洛树搜索、ToT 思维树等，决定任务分解和路径选择策略。",
        "HTN 将复杂任务递归分解为子任务直到可执行。MCTS 通过选择-扩展-模拟-回传搜索决策树，在巨大空间中找最优行动。ToT 让 LLM 生成多个推理分支并评估，探索多条路径后选最优（比单链 CoT 更全面）。规划与执行分离：Planner 生成计划，Executor 执行并反馈。",
        ["HTN 递归分解任务，适合结构化领域", "MCTS 四步：选择→扩展→模拟→回传，平衡探索与利用", "ToT 思维树：多分支推理+评估+剪枝，适合复杂推理", "规划质量取决于 LLM 推理能力和任务可分解性", "面试常考：HTN/MCTS/ToT 原理、ToT vs CoT、规划执行分离"]
    ),
    "## 8.3 记忆类型详解": (
        "Agent 记忆按内容分为情景记忆、语义记忆、程序性记忆和工作记忆，各有不同的存储和检索方式。",
        "情景记忆存储具体事件和对话历史（时序化，向量检索）。语义记忆存储事实知识和概念（结构化知识库/RAG）。程序性记忆存储技能和操作流程（工具使用方法、代码模板）。工作记忆是当前任务的临时状态（上下文窗口中的变量和中间结果）。不同记忆类型有不同的写入策略、检索方式和生命周期。",
        ["情景记忆：事件/对话，向量库，时序检索", "语义记忆：事实/概念，知识图谱/RAG，语义检索", "程序性记忆：技能/流程，工具定义/代码模板，模式匹配", "工作记忆：当前状态，上下文窗口，容量有限", "面试常考：四种记忆类型、存储方式、检索策略、记忆协作"]
    ),
    "## 8.4 MCP（Model Context Protocol）": (
        "MCP 是 Anthropic 提出的工具调用标准化协议，让工具以 MCP Server 形式提供，任何支持 MCP 的 Client 都能即插即用。",
        "MCP 采用 Client-Server 架构：MCP Server 暴露 Resources（资源/数据）、Tools（可执行函数）、Prompts（提示词模板）三种能力，MCP Client（如 Claude Desktop、IDE）通过 stdio/SSE 连接 Server。协议基于 JSON-RPC 2.0，定义了工具发现、调用、流式响应等标准消息。目标是解决 N×M 工具集成问题（每个 Agent 接每个工具），变为 N+M（Agent 接 MCP，工具实现 MCP）。",
        ["三种能力：Resources（只读数据）、Tools（可执行）、Prompts（模板）", "基于 JSON-RPC 2.0，支持 stdio 本地和 SSE 远程传输", "解决工具碎片化：一次实现 MCP Server，所有 MCP Client 可用", "类似 LSP（语言服务器协议）之于编辑器，MCP 之于 AI Agent", "面试常考：MCP 架构、三种能力类型、与 Function Calling 关系、解决什么问题"]
    ),
    "## 8.5 Agent 评估基准": (
        "AgentBench/WebArena/SWE-bench/GAIA 等基准从不同维度评估 Agent 的多步推理、工具使用和任务完成能力。",
        "AgentBench 在 8 个环境（操作系统、数据库、知识图谱等）评估 Agent。WebArena 在真实网站上执行复杂任务（购物、表单填写）。SWE-bench 让 Agent 修复真实 GitHub Issue（评估代码能力）。GAIA 设计需要多步推理+工具使用的通用助手任务。评估指标通常是任务成功率，而非 BLEU 等文本相似度。",
        ["SWE-bench：真实 GitHub Issue 修复，考验代码理解和编辑能力", "WebArena：真实网页操作，考验浏览器工具使用", "GAIA：通用助手任务，考验多步推理+工具组合", "评估核心是任务成功率（端到端），不是单轮文本质量", "面试常考：主流 Agent 基准、评估指标、Agent 评估难点"]
    ),
    "## 8.6 Agent 安全与对齐": (
        "Agent 安全关注工具滥用、权限边界、目标漂移和可中断性，确保 Agent 行为在可控范围内。",
        "工具滥用防护：敏感操作（删除/支付/发邮件）需人工确认，工具权限最小化。沙箱执行：代码执行在隔离容器中，限制网络和文件访问。目标漂移：Agent 在多步执行中偏离原始目标，需监控和目标对齐。Prompt 注入：恶意输入诱导 Agent 执行非预期操作，需输入过滤和指令优先级。可中断性：随时可停止 Agent，设置最大步数和预算。",
        ["敏感工具调用需 Human-in-the-loop 确认", "代码执行用沙箱（Docker/微虚拟机）隔离", "Prompt 注入防护：系统指令与用户输入分离，输入消毒", "设置最大循环次数、Token 预算和超时，防止失控", "面试常考：Agent 安全风险、Prompt 注入、最小权限、沙箱、目标漂移"]
    ),
}

# ============================================================
# AI Agent 开发框架
# ============================================================
agent_frameworks = {
    "### 2.1 定位": (
        "LangChain 是最流行的 LLM 应用开发框架，提供链式调用、工具集成、记忆和 Agent 抽象。",
        "LangChain 将 LLM 应用拆分为 Model/Prompt/Chain/Tool/Memory/Retriever/Agent 等组件，通过 LCEL（LangChain Expression Language）用管道符组合。核心价值是丰富的集成（数百种工具/向量库/LLM）和标准化抽象，但抽象层较重，版本迭代快，生产环境需谨慎锁定版本。",
        ["核心抽象：Model/Prompt/Chain/Tool/Memory/Retriever/Agent", "LCEL 用 | 管道符组合组件，支持流式和异步", "集成生态最丰富，适合快速原型", "抽象层较重，简单场景可能过度设计", "面试常考：LangChain 核心组件、LCEL、LangChain vs 原生 API"]
    ),
    "### 2.2 核心概念": (
        "LangChain 的核心概念包括 Chain（链）、Tool（工具）、Memory（记忆）、Retriever（检索器）和 Agent（智能体）。",
        "Chain 是组件的有序组合（如 PromptTemplate→LLM→OutputParser）。Tool 是 Agent 可调用的函数封装。Memory 管理对话历史（Buffer/Summary/Vector）。Retriever 是文档检索接口（向量库检索）。Agent 是 LLM+工具+循环的执行引擎，决定调用哪个工具。LCEL 用 Runnable 协议统一所有组件接口。",
        ["Chain：组件组合，LCEL 用 | 连接 Runnable", "Memory：ConversationBufferMemory/SummaryMemory/VectorStoreRetrieverMemory", "Retriever：get_relevant_documents() 接口，向量库实现", "AgentExecutor 运行 ReAct 循环，处理工具调用和观察", "面试常考：Chain 类型、Memory 类型、Retriever 接口、AgentExecutor"]
    ),
    "### 2.3 基本用法": (
        "通过 PromptTemplate 格式化提示、LLM 生成、OutputParser 解析输出，用 LCEL 管道组合成链。",
        "基本流程：定义 PromptTemplate（含变量占位符）→ 绑定 LLM → 加 OutputParser → 用 | 组成 chain → chain.invoke({变量}) 执行。LCEL 的 Runnable 协议提供 invoke/stream/batch 方法，自动支持同步异步和流式。Agent 用法：初始化 LLM、定义 tools、create_react_agent、用 AgentExecutor 调用。",
        ["prompt | llm | parser 是最基本的 LCEL 链", "chain.invoke() 同步、.stream() 流式、.batch() 批量", "RunnableParallel 可并行执行多个分支", "Agent 用 create_react_agent + AgentExecutor", "面试常考：LCEL 语法、Runnable 协议、流式输出、Agent 创建"]
    ),
    "### 3.1 定位": (
        "LlamaIndex 专注于 LLM 与私有数据的连接，是 RAG 场景最专业的框架。",
        "LlamaIndex（原 GPT Index）核心能力是数据摄入（Connector 读取各种数据源）、索引构建（Index 将文档组织为可检索结构）、查询引擎（QueryEngine 编排检索-生成）。相比 LangChain 的大而全，LlamaIndex 在 RAG 和数据索引方面更深入，提供多种索引类型（向量/关键词/树/知识图谱）和高级检索策略。",
        ["核心定位：RAG 和数据索引框架，专注 LLM+私有数据", "数据连接器支持 PDF/Notion/数据库/API 等上百种数据源", "索引类型：VectorStoreIndex/SummaryIndex/TreeIndex/KnowledgeGraphIndex", "查询引擎支持子问题分解、路由查询、多步查询", "面试常考：LlamaIndex vs LangChain、索引类型、RAG 高级策略"]
    ),
    "### 3.2 核心能力": (
        "LlamaIndex 提供数据摄入、索引构建、检索查询和响应合成的完整 RAG 工具链。",
        "数据摄入：SimpleDirectoryReader/Reader 读取文档，NodeParser 切分为 Node。索引：VectorStoreIndex 将 Node embedding 存入向量库。检索：Retriever 定义检索策略（向量/关键词/混合）。查询：QueryEngine 编排检索+生成，ChatEngine 支持多轮对话。响应合成：将多个检索结果与问题组合生成回答，支持 refine/tree_summarize 等模式。",
        ["Node 是 LlamaIndex 的基本数据单元（文档+元数据+关系）", "NodeParser 切分文档，支持句子/语义/层次切分", "Retriever 检索策略：向量/关键词/混合/自动合并", "Response Synthesizer：refine（逐块精炼）、compact（压缩）、tree_summarize", "面试常考：Node/Index/Retriever/QueryEngine 关系、响应合成模式"]
    ),
    "### 3.3 基本用法": (
        "加载文档→切分节点→构建索引→创建查询引擎→执行查询，是 LlamaIndex RAG 的标准流程。",
        "SimpleDirectoryReader 加载文档，SentenceSplitter 切分为 Node，VectorStoreIndex.from_documents() 构建索引（自动 embedding），index.as_query_engine() 创建查询引擎，query_engine.query(question) 执行检索+生成。持久化用 storage_context 保存/加载索引。",
        ["VectorStoreIndex.from_documents(docs) 一键构建索引", "query_engine.query() 检索+生成，response 包含答案和来源节点", "storage_context.persist() 持久化，load_index_from_storage() 加载", "可配置 llm/embed_model/vector_store 等组件", "面试常考：LlamaIndex RAG 流程、索引持久化、查询引擎配置"]
    ),
    "### 3.4 LangChain vs LlamaIndex": (
        "LangChain 是通用 LLM 应用框架（Agent/Chain/工具），LlamaIndex 专注 RAG 和数据索引，两者可组合使用。",
        "LangChain 优势在 Agent 生态、工具集成和链式编排；LlamaIndex 优势在数据摄入、索引类型和检索策略深度。LangChain 也有 RAG 模块但较基础，LlamaIndex 也有 Agent 能力但非核心。生产中常用 LlamaIndex 做检索层，LangChain 做 Agent 编排层，两者互补。",
        ["LangChain：大而全，Agent/工具/Chain 生态强", "LlamaIndex：专而精，RAG/索引/检索策略深", "可组合：LlamaIndex Retriever 作为 LangChain 工具", "选型：纯 RAG 选 LlamaIndex，Agent 工作流选 LangChain", "面试常考：两者定位区别、如何组合、选型建议"]
    ),
    "### 4.1 定位": (
        "LangGraph 是 LangChain 团队推出的有状态多 Agent 编排框架，用图结构定义 Agent 工作流。",
        "LangGraph 将 Agent 工作流建模为有向图：节点（Node）是计算步骤（Agent/工具/函数），边（Edge）定义流转逻辑（条件边/循环），State 在节点间传递。相比 AgentExecutor 的固定 ReAct 循环，LangGraph 支持循环、分支、持久化状态和人机协作中断，适合复杂可控的 Agent 工作流。",
        ["图模型：Node（计算）+ Edge（流转）+ State（共享状态）", "支持循环和条件分支，比线性 Chain 更灵活", "内置检查点（checkpoint）持久化状态，支持中断恢复", "支持 human-in-the-loop：中断等待人工输入后继续", "面试常考：LangGraph vs AgentExecutor、图模型、状态管理、人机协作"]
    ),
    "### 4.2 核心概念": (
        "LangGraph 的核心概念包括 StateGraph、Node、Edge、Conditional Edge 和 Checkpointer。",
        "StateGraph 定义状态结构（TypedDict）和图拓扑。Node 是接收 state 返回 state 更新的函数。Edge 连接节点，普通边固定流转，conditional_edge 根据状态函数决定下一节点。START 和 END 是虚拟节点标记入口和出口。Checkpointer 在每步后保存状态快照，支持回滚、暂停和恢复。",
        ["StateGraph[TState]：TState 定义图中流转的状态结构", "add_node/add_edge/add_conditional_edges 构建图", "条件边：路由函数返回下一节点名称，实现分支", "Checkpointer：MemorySaver/SqliteSaver 持久化每步状态", "面试常考：StateGraph 构建、条件边、checkpoint、时间旅行调试"]
    ),
    "### 4.3 适用场景": (
        "LangGraph 适合需要循环、分支、持久化和人机协作的复杂 Agent 工作流，如多 Agent 协作、审批流程。",
        "典型场景：多 Agent 协作（Supervisor 路由到不同专家 Agent）、人机协作工作流（Agent 执行到敏感操作暂停，人工审批后继续）、持久化长任务（中断后可恢复）、复杂条件分支（根据工具结果走不同路径）。简单单 Agent 任务用 LangChain AgentExecutor 即可，不需要图。",
        ["多 Agent Supervisor 模式：一个调度 Agent 路由到专家 Agent", "审批流：Agent 准备方案→中断→人工批准→继续执行", "持久化：checkpoint 保存状态，服务重启后恢复", "时间旅行：可回退到任意 checkpoint 调试", "面试常考：LangGraph 适用场景、Supervisor 模式、人机协作实现"]
    ),
    "### 5.1 定位": (
        "AutoGen 是微软开源的多 Agent 对话框架，让多个 Agent 通过对话协作完成任务。",
        "AutoGen 核心是 ConversableAgent，Agent 之间通过对话消息协作。支持人类参与（HumanInputAgent）、代码执行（Docker 沙箱）、嵌套对话和群聊（GroupChat）。Agent 可注册 reply 方法（LLM/函数/代码执行），对话可自动终止或人工介入。相比 LangGraph 的图编排，AutoGen 更偏向自由对话式协作。",
        ["ConversableAgent 是核心，Agent 间通过消息对话协作", "支持 GroupChatManager 管理多 Agent 群聊", "内置代码执行沙箱（Docker），支持自动执行和反馈", "HumanInputAgent 实现人机协作", "面试常考：AutoGen 对话模型、GroupChat、代码执行、与 LangGraph 区别"]
    ),
    "### 5.2 核心概念": (
        "AutoGen 的核心概念包括 ConversableAgent、AssistantAgent、UserProxyAgent 和 GroupChat。",
        "ConversableAgent 是基类，可发送/接收消息、注册回复函数。AssistantAgent 配置为 LLM 助手（默认系统提示）。UserProxyAgent 代表用户，可执行代码和人工输入。GroupChat 管理多个 Agent 的对话流程（轮次/选择下一个发言者）。Agent 可注册 function（工具）和 code execution。",
        ["AssistantAgent：LLM 驱动的助手，生成代码和回答", "UserProxyAgent：执行代码、调用函数、可人工输入", "register_function 注册工具，register_reply 注册自定义回复", "GroupChat + GroupChatManager 编排多 Agent 对话", "面试常考：Agent 类型、消息流转、代码执行、GroupChat 选择策略"]
    ),
    "### 5.3 特点": (
        "AutoGen 特点是对话驱动协作、内置代码执行、灵活的人机协作和多 Agent 群聊。",
        "对话驱动：Agent 间通过自然语言消息协作，灵活但可能不够可控。代码执行：UserProxy 可在 Docker 中执行 LLM 生成的代码并反馈结果。人机协作：可配置每轮人工确认或仅在特定条件介入。嵌套对话：Agent 可启动子对话。群聊：支持自动选择发言者和轮次管理。",
        ["对话式协作灵活但 Token 消耗可能较大", "Docker 代码执行安全隔离，支持自动反馈循环", "human_input_mode：ALWAYS/NEVER/TERMINATE", "嵌套对话支持 Agent 内部启动子任务", "面试常考：AutoGen 优缺点、代码执行安全、人机协作模式"]
    ),
    "### 6.1 定位": (
        "CrewAI 是角色扮演式多 Agent 框架，通过定义角色、目标和任务来编排 Agent 团队。",
        "CrewAI 让开发者像组建团队一样定义 Agent（role/goal/backstory）和 Task（description/expected_output），Crew 按 sequential 或 hierarchical 流程执行。设计理念是让 Agent 有明确的角色身份和目标，比通用 Agent 更聚焦。支持工具集成、记忆、异步任务和流程定制。",
        ["角色扮演：role+goal+backstory 让 Agent 身份明确", "Task 驱动：每个任务有描述、期望输出和负责 Agent", "sequential 顺序执行，hierarchical 层级管理", "独立于 LangChain，可独立使用或集成", "面试常考：CrewAI 定位、Agent/Task/Crew、与 AutoGen 区别"]
    ),
    "### 6.2 核心概念": (
        "CrewAI 的核心概念是 Agent（角色）、Task（任务）、Crew（团队）和 Process（流程）。",
        "Agent 有 role（角色名）、goal（目标）、backstory（背景故事）、tools（工具集）、llm（模型）。Task 有 description、expected_output、agent、context（依赖任务）。Crew 组合 agents 和 tasks，指定 process（sequential/hierarchical）。hierarchical 模式自动创建 Manager Agent 分配任务。",
        ["Agent.backstory 增强角色代入感，影响 LLM 行为", "Task.context 引用上游任务输出，实现数据传递", "Process.sequential 按任务列表顺序执行", "Process.hierarchical 自动选 Manager Agent 协调", "面试常考：CrewAI 核心概念、任务依赖、流程类型"]
    ),
    "### 6.3 特点": (
        "CrewAI 特点是角色扮演直观、任务驱动、上手简单，内置记忆和异步支持。",
        "角色扮演让非技术用户也能理解 Agent 分工。任务输出结构化（expected_output），便于质量控制。支持短期/长期/实体记忆。异步执行提高效率。相比 AutoGen 的自由对话，CrewAI 的流程更可控，适合结构化工作流。但灵活性不如 LangGraph。",
        ["角色扮演直观，适合业务人员理解和设计", "expected_output 约束输出格式，提高结果质量", "内置记忆系统（短期/长期/实体记忆）", "sequential 流程可控，hierarchical 自动管理", "面试常考：CrewAI 特点、与 LangChain/LangGraph/AutoGen 对比"]
    ),
    "### 7.1 定位": (
        "Semantic Kernel 是微软推出的 SDK，将 LLM 与编程语言原生集成，支持 C#/Python/Java。",
        "Semantic Kernel（SK）核心概念是 Plugin（函数集合）、Planner（规划器）和 Kernel（容器）。开发者用原生代码定义 Native Function（C#/Python 函数）和 Prompt Function（提示词模板），Planner 自动组合函数完成任务。深度集成 Azure OpenAI 和微软生态，适合企业级 .NET 环境。",
        ["Kernel 是核心容器，管理 LLM/插件/记忆", "Plugin = Native Function（代码）+ Prompt Function（提示词）", "Planner 自动规划函数调用链（类似 Agent）", "企业级：支持 .NET/Python/Java，Azure 集成深", "面试常考：Semantic Kernel 架构、Plugin/Planner/Kernel、与 LangChain 区别"]
    ),
    "### 7.2 核心功能": (
        "Semantic Kernel 提供插件系统、规划器、记忆连接器和企业级集成能力。",
        "插件系统：函数即插件，可从 OpenAPI 规范导入。规划器：Handlebars/Stepwise Planner 自动编排函数。记忆：Vector Store 抽象支持多种向量库。连接器：Azure OpenAI/OpenAI/HuggingFace。过滤器：函数调用前后钩子（权限/日志/重试）。",
        ["Planner 自动将目标分解为函数调用序列", "OpenAPI 插件导入：自动生成工具定义", "Vector Store 抽象层，切换向量库不改代码", "Function Filter 实现权限控制和可观测性", "面试常考：SK Planner、插件机制、企业级特性"]
    ),
    "### 7.3 适用场景": (
        "Semantic Kernel 适合微软技术栈企业、需要将 LLM 深度集成到现有 .NET/Python 应用的场景。",
        "典型场景：企业内部 Copilot 应用（Office/Teams 扩展）、.NET 后端 LLM 集成、Azure 云原生 AI 应用、需要严格权限控制和审计的企业场景。对于纯 Python 快速原型，LangChain/LlamaIndex 更灵活。",
        [".NET 企业应用首选，与 Azure/M365 生态深度集成", "适合需要严格治理（权限/审计/合规）的企业场景", "多语言 SDK（C#/Python/Java）支持混合技术栈", "与 LangChain 定位不同：SK 更偏工程化和企业集成", "面试常考：SK 适用场景、与 LangChain 对比、企业级 AI 应用"]
    ),
    "## 8.1 其他重要框架": (
        "除主流框架外，还有 Dify（低代码平台）、Coze（字节 Bot 平台）、n8n（工作流+AI）等快速应用构建工具。",
        "Dify 是开源 LLM 应用开发平台，可视化编排 Agent/RAG/工作流，支持自部署。Coze 是字节跳动的 Bot 开发平台，零代码创建 AI Bot 并发布到多平台。n8n/Zapier 是工作流自动化工具，通过节点连接 AI 和 SaaS 服务。这些工具降低了 AI 应用开发门槛，适合非工程师和快速验证。",
        ["Dify：可视化+自部署，RAG/Agent/工作流一体", "Coze：零代码 Bot 平台，插件生态丰富，多平台发布", "n8n：工作流自动化+AI 节点，自部署可选", "低代码平台适合快速验证，复杂逻辑仍需代码框架", "面试常考：低代码 AI 平台、Dify/Coze/n8n 区别、选型"]
    ),
    "### 8.2 LangChain vs LangGraph 深度对比": (
        "LangChain 的 AgentExecutor 是固定 ReAct 循环，LangGraph 用图模型支持任意工作流，后者更灵活可控。",
        "AgentExecutor 隐藏了执行循环，开发者只能配置工具和提示词，适合标准 ReAct 场景。LangGraph 暴露状态图，开发者完全控制节点逻辑、条件分支、循环和中断，适合需要精细控制的复杂工作流。LangGraph 内置状态持久化和时间旅行，AgentExecutor 无此能力。LangGraph 是 LangChain 的超集，可调用 LangChain 组件。",
        ["AgentExecutor：黑盒 ReAct 循环，简单场景够用", "LangGraph：白盒图编排，支持循环/分支/中断/持久化", "LangGraph 状态在节点间显式传递，可追踪和调试", "简单 Agent 用 AgentExecutor，复杂工作流用 LangGraph", "面试常考：何时用 LangGraph、图 vs 链、状态持久化"]
    ),
    "### 8.3 生产部署与可观测性": (
        "Agent 生产部署需要考虑可观测性（追踪/日志/指标）、成本控制、错误处理和评估体系。",
        "可观测性：LangSmith/Langfuse 追踪每次 LLM 调用（输入/输出/Token/延迟），可视化 Agent 执行路径。成本控制：Token 计数、模型路由（简单任务用小模型）、缓存。错误处理：工具调用重试、LLM 输出解析失败回退、最大步数限制。评估：离线测试集+在线监控成功率和用户反馈。",
        ["LangSmith/Langfuse：全链路追踪，可视化 Agent 执行树", "Token 计数和预算控制，模型路由降本", "重试/回退/超时策略保证可靠性", "离线评估集+在线指标监控持续改进", "面试常考：Agent 可观测性、LangSmith、成本优化、生产可靠性"]
    ),
    "### 8.4 模型路由与降级": (
        "根据任务复杂度路由到不同模型（简单用小模型、复杂用大模型），并在主模型失败时降级，平衡成本和可靠性。",
        "路由策略：用小模型/分类器判断任务类型，简单问答用小模型（便宜快），复杂推理用大模型（贵但强）。降级链：主模型失败→备用模型→规则兜底。实现上可在 LLM 抽象层加路由逻辑，或用 LangChain RouterChain。也可按工具调用需求路由（需要工具的用支持 Function Calling 的模型）。",
        ["路由：分类器判断任务复杂度，选择性价比最优模型", "降级：主模型超时/错误→备用模型→规则回复", "缓存：相同问题直接返回缓存结果，省 Token", "模型抽象层统一接口，切换模型不改业务代码", "面试常考：模型路由策略、降级方案、成本优化、高可用设计"]
    ),
}

# ============================================================
# AI Agent 实战与能力优化
# ============================================================
agent_practice = {
    "### 2.1 RAG 完整流程": (
        "RAG 完整流程包括文档加载、切分、向量化、存储、检索、重排和生成，每一步都影响最终回答质量。",
        "离线阶段：文档加载（PDF/网页/数据库）→ 文本切分（chunk）→ embedding 向量化 → 存入向量数据库。在线阶段：问题向量化 → 向量检索 top-k →（可选）查询改写/混合检索 → reranker 重排序 → 拼接上下文 → LLM 生成回答 → 引用来源。每一步都有优化空间：切分策略、embedding 模型、检索参数、reranker、prompt 模板。",
        ["离线：加载→切分→embedding→入库；在线：检索→重排→生成", "切分质量影响检索：太大引入噪声，太小丢失上下文", "混合检索（向量+BM25）+ reranker 显著提升准确率", "生成时必须引用来源，支持溯源验证", "面试常考：RAG 全流程、各环节优化、chunk 策略、reranker"]
    ),
    "### 2.2 文本切分优化": (
        "文本切分策略直接影响检索质量，需根据文档类型选择固定切分、语义切分或递归切分，并设置重叠。",
        "固定长度切分：按 token/字符数切，简单但可能切断语义。递归切分：按段落→句子→词的优先级切分，尽量保持语义完整。语义切分：用 embedding 相似度判断主题边界。文档结构切分：按 Markdown 标题/HTML 标签切分。重叠（overlap）：相邻 chunk 共享部分文本，避免边界信息丢失。chunk 大小通常 256-1024 token，根据文档类型调整。",
        ["递归字符切分（RecursiveCharacterTextSplitter）最常用", "chunk_size 512-1024，overlap 50-100 是常见配置", "代码按函数/类切分，Markdown 按标题切分", "语义切分质量高但计算成本大", "面试常考：切分策略、chunk size 选择、overlap 作用、结构化文档切分"]
    ),
    "### 3.1 幻觉类型": (
        "LLM 幻觉分为事实性幻觉（编造不存在的事实）和忠实性幻觉（与上下文矛盾），RAG Agent 中需重点防控。",
        "事实性幻觉：模型编造训练数据中没有或错误的信息（虚构 API、不存在的论文）。忠实性幻觉：回答与提供的上下文矛盾（忽略检索到的文档，凭记忆回答）。RAG 场景还包括：检索到错误文档导致的幻觉、对文档过度推断、引用不存在的来源。幻觉成因包括训练数据噪声、概率生成机制、上下文信息不足和领域知识缺乏。",
        ["事实性幻觉：编造不存在的信息（虚构 API/论文/事件）", "忠实性幻觉：回答与检索上下文矛盾", "RAG 特有：检索到不相关文档、过度推断、伪造引用", "幻觉不可完全消除，只能通过工程手段降低", "面试常考：幻觉类型、幻觉成因、RAG 如何减少幻觉"]
    ),
    "### 3.2 控制方法": (
        "通过 Prompt 约束、RAG  grounding、温度调节、自我验证和引用强制等手段控制幻觉。",
        "Prompt 约束：明确要求只基于上下文回答，不知道就说不知道。RAG grounding：提供准确检索内容，减少模型自由发挥。temperature=0 降低随机性。自我验证：让 LLM 检查回答是否有来源支持（Self-Consistency/Citations）。引用强制：要求每个事实标注来源 chunk。链式验证（Chain-of-Verification）：生成回答后自动提出验证问题并逐一核实。",
        ["Prompt：'只基于以下上下文回答，不确定则说不知道'", "temperature=0 / top_p=1 降低随机性", "强制引用来源，无来源的信息标记为推测", "Chain-of-Verification：生成→提验证问题→核实→修正", "面试常考：幻觉控制手段、RAG grounding、CoVe、引用验证"]
    ),
    "### 3.3 幻觉评估": (
        "通过事实性准确率、答案忠实度和引用准确率等指标量化幻觉程度，指导优化方向。",
        "评估方法：构建标注测试集（问题+正确答案+来源文档），自动评估用 LLM-as-Judge 判断回答是否忠实于上下文（faithfulness）和是否回答了问题（answer relevancy）。引用准确率：检查引用的来源是否真的支持回答。RAGAS 框架专门评估 RAG：faithfulness（忠实度）、answer_relevancy（答案相关性）、context_precision/recall（上下文精确率/召回率）。",
        ["faithfulness：回答中的事实是否都能在上下文中找到依据", "answer_relevancy：回答是否切题", "context_precision/recall：检索到的上下文是否相关/完整", "RAGAS 是 RAG 专用评估框架，自动化指标计算", "面试常考：RAG 评估指标、RAGAS、faithfulness、LLM-as-Judge"]
    ),
    "### 4.1 工具设计原则": (
        "好的工具设计需要描述清晰、参数明确、粒度适中、错误友好，是 Agent 正确使用工具的前提。",
        "工具命名用动词+名词（get_weather/send_email），description 说明何时使用和做什么（LLM 根据 description 选择工具）。参数用 JSON Schema 严格定义类型和枚举值，减少 LLM 参数错误。粒度：一个工具做一件事，避免万能工具。错误信息应可操作（告诉 LLM 如何修正而非仅报错）。工具数量控制在 10-20 个以内，过多导致选择困难。",
        ["description 是 LLM 选择工具的唯一依据，必须清晰说明使用场景", "参数 JSON Schema 严格定义类型/必填/枚举/描述", "粒度适中：太粗 LLM 不会用，太细调用次数多", "错误信息可操作：'参数 X 应为日期格式 YYYY-MM-DD'", "面试常考：工具设计原则、description 重要性、参数校验、工具数量"]
    ),
    "### 4.2 工具选择优化": (
        "通过工具描述优化、示例引导、检索式工具选择和子 Agent 分工提升 LLM 工具选择准确率。",
        "工具描述中加入 few-shot 示例（什么场景用什么工具）。工具太多时用检索式选择：先将工具 description embedding，根据用户意图检索 top-k 工具再传给 LLM（减少上下文干扰）。子 Agent 分工：不同领域专家 Agent 各自持有相关工具，主 Agent 路由到专家 Agent。强制工具调用：对特定意图强制使用特定工具。",
        ["description 加入使用示例，提升 LLM 选择准确率", "工具检索（Tool RAG）：embedding 工具描述，按意图召回相关工具", "子 Agent 分工：每个专家 Agent 只持有领域工具", "结构化输出解析失败时重试或引导 LLM 修正格式", "面试常考：工具选择优化、Tool RAG、子 Agent 分工、few-shot"]
    ),
    "### 4.3 工具执行安全": (
        "工具执行需沙箱隔离、权限控制、参数校验和审计日志，防止 Agent 执行危险操作。",
        "代码执行在 Docker/微虚拟机沙箱中（限制网络、文件系统、资源）。文件操作限制在指定目录（chroot/路径白名单）。API 调用限制可访问的端点和方法（HTTP 方法白名单）。敏感操作（删除/支付/发送）需人工确认。参数校验在执行前检查类型和范围。全量审计日志记录每次工具调用（谁/何时/参数/结果）。",
        ["代码执行：Docker/gVisor/Firecracker 沙箱隔离", "最小权限：工具只授予完成任务所需的最小权限", "敏感操作 Human-in-the-loop 确认", "参数白名单校验 + 速率限制防滥用", "面试常考：工具安全、沙箱方案、权限控制、审计日志"]
    ),
    "### 5.1 评估维度": (
        "Agent 评估覆盖任务成功率、工具使用准确率、效率（步数/Token/时间）、安全性和用户满意度。",
        "任务成功率是核心指标：端到端完成任务的比例。工具使用：工具选择准确率、参数正确率、无效调用比例。效率：平均步数、Token 消耗、端到端延迟。安全：越权操作次数、Prompt 注入抵抗率。鲁棒性：对模糊输入和错误的恢复能力。用户满意度：人工评分或反馈率。",
        ["任务成功率（端到端）是最核心的业务指标", "工具使用准确率和参数正确率反映 Agent 能力", "效率指标：步数/Token/延迟，影响成本和体验", "安全指标：越权次数、注入抵抗率", "面试常考：Agent 评估维度、成功率计算、效率指标"]
    ),
    "### 5.2 评估方法": (
        "Agent 评估方法包括离线测试集评估、LLM-as-Judge、人工评估和在线 A/B 测试。",
        "离线评估：构建标注测试集（任务+期望结果），自动运行 Agent 并评分。LLM-as-Judge：用强模型（GPT-4）评判 Agent 输出质量（成本低但有偏差）。人工评估：对复杂任务人工打分（准确但慢贵）。在线评估：A/B 测试对比不同 Agent 版本的成功率和用户满意度。轨迹评估：检查 Agent 的执行路径是否合理（不只是最终结果）。",
        ["离线测试集用于回归测试，每次修改后自动运行", "LLM-as-Judge 可扩展但需校准偏差", "人工评估作为金标准，定期校准自动评估", "轨迹评估：检查中间步骤是否合理，不只看结果", "面试常考：评估方法对比、LLM-as-Judge 偏差、A/B 测试"]
    ),
    "### 5.3 测试集构建": (
        "构建有代表性的 Agent 测试集需覆盖典型场景、边界情况和对抗样本，按难度分层。",
        "测试集来源：真实用户日志（ anonymize）、人工设计典型任务、边界情况（空输入/超长输入/模糊指令）、对抗样本（Prompt 注入/恶意请求）。分层：简单（单步工具调用）、中等（2-3 步）、复杂（多步+规划+错误恢复）。每条测试用例包含：输入、期望结果、检查点（必须调用的工具/必须验证的条件）。",
        ["从真实日志采样保证代表性，人工补充边界 case", "按难度分层：单步/多步/复杂工作流", "包含对抗样本测试安全性", "测试集需持续更新，覆盖新发现的 bad case", "面试常考：测试集构建方法、分层策略、对抗样本、回归测试"]
    ),
    "### 6.1 成本优化": (
        "通过模型路由、Prompt 压缩、缓存、批处理和 Token 监控降低 Agent 的 LLM 调用成本。",
        "模型路由：简单任务用小模型（Haiku/8B），复杂推理用大模型。Prompt 压缩：对话历史摘要、系统提示精简、工具描述按需加载。缓存：相同问题缓存回答（语义缓存用 embedding 相似度匹配）。批处理：批量调用 API（Batch API 半价）。Token 监控：按用户/会话/功能统计 Token 消耗，设置预算告警。减少循环步数：优化规划能力减少无效工具调用。",
        ["模型路由：分类器判断任务难度，选择性价比模型", "语义缓存：相似问题直接返回缓存，命中率可达 30%+", "对话历史摘要压缩，释放上下文空间", "Batch API 适合非实时任务，价格减半", "面试常考：Token 成本优化、模型路由、语义缓存、Prompt 压缩"]
    ),
    "### 6.2 性能优化": (
        "通过并行调用、流式输出、模型选择和架构优化降低 Agent 响应延迟。",
        "并行工具调用：无依赖的工具同时调用（LLM 支持 parallel tool calls）。流式输出：首 Token 时间（TTFT）比完整响应更影响体验，SSE 流式返回。快速模型：简单步骤用快速小模型。预取/预测：提前加载可能需要的数据。架构优化：减少不必要的 LLM 调用（规则预处理）、工具响应精简（只返回必要字段）。",
        ["parallel tool calls：无依赖工具并行执行", "SSE 流式输出，降低首字节延迟", "工具返回结果精简，避免大段 JSON 占用上下文", "简单分类/提取用小模型，延迟低", "面试常考：Agent 延迟优化、并行调用、流式输出、TTFT"]
    ),
    "### 7.1 Prompt 注入防护": (
        "Prompt 注入通过恶意输入覆盖系统指令，诱导 Agent 执行非预期操作，需多层防护。",
        "直接注入：用户输入中包含'忽略以上指令...'等覆盖系统提示。间接注入：工具返回内容（网页/文档）中藏有注入指令。防护：输入消毒（过滤可疑模式）、指令分层（系统指令优先级最高，用分隔符隔离用户输入）、工具权限最小化、输出编码（工具返回内容当数据而非指令处理）、敏感操作人工确认、监控异常行为。",
        ["直接注入：用户消息覆盖系统指令；间接注入：工具返回藏指令", "用分隔符（<user_input>）明确隔离系统指令和外部内容", "工具返回内容标记为不可信数据，不作为指令执行", "敏感操作人工确认是最后防线", "面试常考：Prompt 注入类型、间接注入、防护手段、指令优先级"]
    ),
    "### 7.2 数据安全": (
        "Agent 数据安全涉及 PII 保护、数据脱敏、传输加密和访问控制，防止敏感信息泄露。",
        "PII（个人身份信息）检测和脱敏：日志和记忆中不存储明文手机号/身份证/密码。传输加密：HTTPS/TLS。访问控制：RBAC 限制 Agent 可访问的数据范围。记忆安全：长期记忆中不存敏感数据，或加密存储。多租户隔离：不同用户的数据和记忆严格隔离。数据保留策略：定期清理过期数据。",
        ["PII 检测脱敏：正则/NER 识别手机号/身份证/邮箱后掩码", "日志中不记录敏感参数和用户数据", "记忆存储加密，多租户数据隔离", "RBAC：Agent 只能访问授权范围内的数据", "面试常考：PII 保护、数据脱敏、多租户隔离、记忆安全"]
    ),
    "### 7.3 操作安全": (
        "操作安全确保 Agent 的工具调用在授权范围内，防止误操作和恶意操作造成损害。",
        "白名单机制：Agent 只能调用预定义的工具和 API 端点。操作确认：写操作（创建/修改/删除）需确认或审批流。速率限制：防止 Agent 循环调用导致资源耗尽。回滚能力：关键操作支持撤销。审计日志：完整记录操作链以便追溯。环境隔离：生产操作和测试操作分离，Agent 默认在沙箱环境。",
        ["工具白名单 + API 端点白名单", "写操作需确认，删除等高危操作需人工审批", "速率限制和预算上限防止失控", "完整审计日志支持事后追溯", "面试常考：操作安全、白名单、审批流、审计、回滚"]
    ),
    "### 8.1 知识库问答 Agent": (
        "知识库问答 Agent 结合 RAG 和多轮对话，基于企业私有文档准确回答问题并引用来源。",
        "架构：文档摄入管道（加载→切分→embedding→入库）→ 检索服务（向量+关键词混合检索+rerank）→ 对话 Agent（多轮上下文管理+引用生成）。关键优化：查询改写（将口语化问题转为检索友好查询）、多轮对话中的指代消解、引用来源标注、无答案时诚实回复'未找到相关信息'。",
        ["查询改写：将'它怎么用'改写为具体实体+问题", "混合检索+reranker 提升召回准确率", "多轮对话需管理指代和上下文", "强制引用来源，无结果时诚实回复", "面试常考：知识库问答架构、查询改写、多轮 RAG、引用"]
    ),
    "### 8.2 数据分析 Agent": (
        "数据分析 Agent 能理解自然语言分析需求，自动编写 SQL/Python 代码查询数据并生成图表和洞察。",
        "架构：用户问题 → Schema 理解（表结构/字段描述）→ 计划分析步骤 → 生成 SQL/Python → 沙箱执行 → 观察结果 → 修正或生成可视化 → 总结洞察。关键能力：Schema 感知（将表结构注入 prompt）、代码纠错（执行报错后自动修正）、安全（只读 SQL、限制全表扫描）、结果解释（不只给数字，给业务含义）。",
        ["Schema 注入：将相关表结构和字段注释提供给 LLM", "代码执行-观察-修正循环，SQL 报错自动修正", "安全：只读权限、LIMIT 限制、禁止 DDL/DML", "生成图表和业务洞察，不只是原始数据", "面试常考：Text2SQL、代码纠错循环、数据安全、Schema 链接"]
    ),
    "### 8.3 编程 Agent": (
        "编程 Agent 能理解代码库、编写和修改代码、运行测试并调试，代表产品有 Cursor Agent、Devin。",
        "架构：代码库索引（文件树+符号+embedding）→ 上下文检索（相关代码片段）→ 代码生成/修改（AST 感知编辑）→ 测试执行 → 错误分析 → 修正循环。关键能力：仓库级上下文理解（RAG over code）、精确代码编辑（diff 而非重写）、终端命令执行、测试驱动（写测试→实现→通过）、长任务规划。",
        ["代码 RAG：embedding 代码片段，检索相关上下文", "精确编辑：生成 diff/patch 而非重写整个文件", "执行测试→分析失败→修正循环", "沙箱执行命令，限制危险操作", "面试常考：编程 Agent 架构、代码 RAG、diff 编辑、Devin/Cursor"]
    ),
    "## 8.4 Agent 监控与可观测性": (
        "Agent 可观测性通过追踪、日志、指标和告警监控 Agent 运行状态，快速定位问题。",
        "Trace 追踪：每次 Agent 运行记录完整执行树（LLM 调用/工具调用/耗时/Token），Langfuse/LangSmith 提供可视化。日志：结构化记录输入输出和错误。指标：成功率/延迟/Token 消耗/工具调用分布。告警：成功率下降、延迟升高、成本超预算时告警。Replay：可重放历史执行轨迹用于调试。",
        ["Trace：记录每步 LLM/工具调用的输入输出耗时", "Langfuse 开源自托管，LangSmith 云服务", "关键指标：成功率、P95 延迟、Token/次、工具错误率", "Replay 功能重放历史轨迹调试", "面试常考：Agent 可观测性、Trace 结构、Langfuse、监控指标"]
    ),
    "## 8.5 错误恢复与重试": (
        "Agent 错误恢复机制处理工具调用失败、LLM 输出解析错误和逻辑偏差，保证任务可靠完成。",
        "工具调用失败：指数退避重试（网络错误）、换工具/换参数重试（业务错误）、降级到备选方案。解析错误：JSON 解析失败时让 LLM 修正格式或用正则提取。逻辑偏差：设置检查点验证中间结果，偏差时回退到上一步重新规划。最大重试次数限制，超过后优雅失败并报告原因。",
        ["瞬时错误（网络超时）：指数退避重试", "业务错误（参数错误）：让 LLM 根据错误信息修正后重试", "解析失败：格式修复提示或正则提取", "检查点验证+回退重规划，防止错误累积", "面试常考：错误分类、重试策略、回退机制、优雅失败"]
    ),
    "## 8.6 人机协作（Human-in-the-loop）": (
        "Human-in-the-loop 在 Agent 执行中引入人工审批、输入和纠错，平衡自动化与可控性。",
        "典型模式：审批模式（Agent 准备方案，人工批准后执行）、协助模式（Agent 遇到不确定时请求人工输入）、纠错模式（人工可中断和修正 Agent 行为）。实现：在图工作流中设置中断点（LangGraph interrupt），暂停执行等待人工输入，超时处理。适用于高风险操作（支付/删除/发送邮件）和 Agent 不确定的决策。",
        ["审批模式：Agent 提议→人工确认→执行", "协助模式：Agent 主动请求人工提供信息", "纠错模式：人工可中断、修改、重定向 Agent", "LangGraph interrupt/checkpoint 实现暂停恢复", "面试常考：HITL 模式、中断恢复、审批流、适用场景"]
    ),
    "## 8.7 Agent 安全沙箱": (
        "安全沙箱为 Agent 代码执行提供隔离环境，限制资源访问，防止恶意代码损害宿主系统。",
        "沙箱技术层级：Docker 容器（namespace+cgroup 隔离，轻量但共享内核）、gVisor（用户态内核，更强隔离）、Firecracker（microVM，强隔离但启动慢）、WASM 沙箱（轻量安全）。限制：网络访问白名单、文件系统只读+临时目录、CPU/内存限制、系统调用过滤（seccomp）、执行超时。",
        ["Docker 最常用，gVisor/Firecracker 隔离更强", "网络白名单：只允许访问必要的 API", "文件系统：只读镜像+临时可写目录", "资源限制：CPU/内存/超时，防止 fork bomb", "面试常考：沙箱技术对比、Docker/gVisor/Firecracker、资源限制"]
    ),
    "## 8.8 成本监控与预算控制": (
        "成本监控实时追踪 Token 消耗和 API 费用，设置预算上限和告警，防止 Agent 失控导致高额账单。",
        "实现：每次 LLM 调用记录 model/prompt_tokens/completion_tokens/cost，按用户/会话/功能聚合。预算控制：会话级/用户级/全局预算，达到阈值时降级（换小模型）或拒绝。告警：日/月预算 80% 时通知。优化：缓存命中、模型路由、减少无效循环。OpenAI Batch API 等半价选项用于非实时任务。",
        ["按用户/会话/功能维度统计 Token 和费用", "多级预算：会话级/用户级/全局，阈值触发降级或停止", "80% 预算告警，避免意外超支", "缓存和模型路由是最有效的降本手段", "面试常考：成本监控维度、预算控制策略、降本手段、Token 统计"]
    ),
}


def run():
    tasks = [
        (os.path.join(BASE, "09-AI与效率工具", "AI Agent核心概念与架构知识点系统梳理_优化版.md"), agent_core, True, False, ""),
        (os.path.join(BASE, "09-AI与效率工具", "AI Agent开发框架知识点系统梳理_优化版.md"), agent_frameworks, True, False, ""),
        (os.path.join(BASE, "09-AI与效率工具", "AI Agent实战与能力优化知识点系统梳理_优化版.md"), agent_practice, True, False, ""),
    ]
    for path, cmap, add_note, add_summary, summary in tasks:
        lines, added = expand(path, cmap, add_note, add_summary, summary)
        print(f"  {os.path.basename(path)}: {lines} lines, {added} blocks added")


if __name__ == "__main__":
    run()
