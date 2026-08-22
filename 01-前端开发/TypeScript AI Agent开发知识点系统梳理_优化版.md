---
title: TypeScript AI Agent 开发知识点系统梳理
tags: [前端, TypeScript, AIAgent, LangChain, VercelAISDK, AIGC, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# TypeScript AI Agent 开发知识点系统梳理（优化版）

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。


> **文档说明**：系统梳理 TypeScript/JavaScript 生态下 AI Agent 开发的核心技术，涵盖 LangChain.js、Vercel AI SDK、OpenAI Node SDK 三大方案，以及工具调用、RAG、记忆管理、流式输出、多 Agent 等实战内容。

---

## 1. 概述

TypeScript 生态在 AI Agent 开发领域非常活跃，核心方案包括 **LangChain.js**（功能全面，与 Python 版 LangChain 对齐）、**Vercel AI SDK**（轻量高性能，Next.js/Vue/React 全栈友好）、**OpenAI Node SDK**（官方底层 SDK）。TS 开发者可同时覆盖前端交互和后端 Agent 逻辑。

**三大方案对比**：

| 维度 | LangChain.js | Vercel AI SDK | OpenAI Node SDK |
|------|-------------|---------------|-----------------|
| 定位 | 全功能 LLM 框架 | 轻量全栈 AI 工具包 | 官方 API 封装 |
| 工具调用 | ✅ Agent/Tool | ✅ useChat/streamText | ✅ 原生 |
| RAG | ✅ 深度支持 | ⚠️ 需自建 | ❌ 需自建 |
| 流式输出 | ✅ | ✅ 一流 | ✅ |
| 前端集成 | ⚠️ 需适配 | ✅ useChat/useCompletion | ❌ 仅后端 |
| 多模型 | ✅ 多家 | ✅ 多家 | ❌ 仅 OpenAI |
| 学习曲线 | 较陡 | 平缓 | 平缓 |
| 适用 | 复杂 Agent/RAG | 全栈聊天应用 | 简单 API 调用 |

---


---
## 2. Vercel AI SDK（推荐全栈首选）

### 2.1 核心概念

Vercel AI SDK 是当前最流行的 TS/JS AI 开发工具包，提供统一的 `streamText`、`streamObject`、`useChat` 等 API，支持 React/Vue/Svelte 前端钩子。

**核心 API**：

| API | 说明 |
|-----|------|
| `streamText` | 流式文本生成（后端） |
| `streamObject` | 流式结构化对象生成（后端） |
| `useChat` | 前端聊天钩子（React/Vue） |
| `useCompletion` | 前端补全钩子 |
| `tool` | 定义工具函数 |
| `generateText` | 非流式文本生成 |
| `embed` | 文本向量化 |


> 🔍 **知识点深度解析**
>
> **作用**：理解 Vercel AI SDK 的核心 API 划分，是搭建全栈 AI 应用的基础。
>
> **原理**：SDK 统一封装了不同模型厂商的调用差异：后端用 streamText/streamObject/generateText 生成，前端用 useChat/useCompletion 钩子消费，tool/embed 提供工具与向量能力。
>
> **用法要点**：① streamText 流式文本，generateText 非流式，streamObject 流式结构化  ② useChat 自动管理会话状态，支持 React/Vue/Svelte  ③ tool 用 Zod 描述参数，embed 生成文本向量  ④ 选择 SDK 取决于是否要全栈一体化（Vercel AI SDK 最省心）  ⑤ 核心 API 命名清晰，后端生成/前端消费职责分明

### 2.2 后端：流式生成 + 工具调用

```typescript
// app/api/chat/route.ts
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

// 定义工具
const weatherTool = tool({
  description: '查询指定城市的天气',
  parameters: z.object({
    city: z.string().describe('城市名称'),
  }),
  execute: async ({ city }) => {
    const res = await fetch(`https://api.weather.com/${city}`);
    return res.json();
  },
});

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    messages,
    tools: { weather: weatherTool },
    maxSteps: 5,  // 允许多轮工具调用
  });

  return result.toDataStreamResponse();
}
```


> 🔍 **知识点深度解析**
>
> **作用**：后端路由是 AI 能力的入口，负责调用模型、定义工具并以流式返回。
>
> **原理**：streamText 接收 model/messages/tools，tools 由 tool() 定义（含 Zod 参数与 execute）；模型决定调用工具时 SDK 执行 execute 并把结果回灌继续生成，maxSteps 限制轮数；toDataStreamResponse 以 SSE 输出。
>
> **用法要点**：① 用 toDataStreamResponse() 暴露 SSE 流给前端 useChat  ② 工具 description 越清晰，模型越会正确调用  ③ maxSteps 允许多步推理（先查再算）  ④ 工具 execute 需处理异常并返回可序列化结果  ⑤ 后端只透传流，不缓冲完整响应以保低延迟

### 2.3 前端：useChat（Vue 3）

```vue
<script setup lang="ts">
import { useChat } from '@ai-sdk/vue';

const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
  api: '/api/chat',
  initialMessages: [
    { id: '1', role: 'system', content: '你是一个有用的助手' }
  ]
});
</script>

<template>
  <div class="chat-container">
    <div v-for="msg in messages" :key="msg.id" :class="msg.role">
      {{ msg.content }}
    </div>
    <form @submit="handleSubmit">
      <input
        :value="input"
        @input="handleInputChange"
        placeholder="输入消息..."
        :disabled="isLoading"
      />
      <button type="submit" :disabled="isLoading">发送</button>
    </form>
  </div>
</template>
```


> 🔍 **知识点深度解析**
>
> **作用**：useChat 让前端以极少代码获得完整聊天交互能力。
>
> **原理**：@ai-sdk/vue 的 useChat 内部维护 messages（含 role/content）、input、isLoading 等响应式状态，提交时 fetch 后端并增量解析流式响应自动追加到 messages。
>
> **用法要点**：① 解构 messages/input/handleInputChange/handleSubmit/isLoading 即可渲染  ② initialMessages 可预设 system 或历史  ③ 按 msg.role 区分用户/助手样式  ④ isLoading 用于禁用输入框  ⑤ api 指向后端 streamText 接口

### 2.4 结构化输出（streamObject）

```typescript
import { streamObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const UserProfileSchema = z.object({
  name: z.string(),
  age: z.number(),
  skills: z.array(z.string()),
  experience: z.array(z.object({
    company: z.string(),
    years: z.number(),
  })),
});

const result = await streamObject({
  model: openai('gpt-4o'),
  schema: UserProfileSchema,
  prompt: '从以下简历中提取信息：' + resumeText,
});

// 流式接收部分对象
for await (const partial of result.partialObjectStream) {
  console.log('当前提取进度:', partial);
}
```


> 🔍 **知识点深度解析**
>
> **作用**：让模型输出严格符合预设结构（JSON），便于程序消费。
>
> **原理**：streamObject 接收 Zod schema 作为输出约束，生成被校验并序列化为对象；partialObjectStream 可在生成过程中逐步吐出“部分对象”，便于前端实时占位。
>
> **用法要点**：① 用 z.object 定义输出 schema，字段类型即约束  ② 嵌套结构（数组/对象）也支持  ③ partialObjectStream 适合边生成边渲染  ④ 比手动 JSON.parse 更稳（避免格式破碎）  ⑤ 可用于信息抽取、表单自动填充

### 2.5 RAG 实现

```typescript
import { retrieve } from '@/lib/retrieval';

export async function POST(req: Request) {
  const { messages } = await req.json();
  const lastMessage = messages[messages.length - 1].content;

  // 检索相关文档
  const docs = await retrieve(lastMessage, 5);
  const context = docs.map(d => d.content).join('\n\n');

  const result = streamText({
    model: openai('gpt-4o'),
    system: `你是知识库助手。请根据以下上下文回答问题，不知道就说不知道。\n\n上下文：${context}`,
    messages,
  });

  return result.toDataStreamResponse();
}
```

> 🔍 **知识点深度解析**
>
> **作用**：Vercel AI SDK 是全栈 AI 应用的最佳选择，一套 SDK 覆盖后端生成和前端交互。
>
> **原理**：`streamText` 调用 LLM API 并将响应转为流式数据，通过 `toDataStreamResponse()` 以 SSE 格式返回前端。`useChat` 钩子自动管理 messages 数组、输入状态、加载状态，通过 fetch 调用后端 API 并解析流式响应。工具调用通过 `tool()` 定义（含 Zod schema 校验参数），LLM 返回 tool_call 时 SDK 自动执行 `execute` 函数，结果返回 LLM 继续生成（`maxSteps` 控制最大轮次）。`streamObject` 用 Zod schema 约束输出格式，支持流式接收部分对象。
>
> **用法要点**：① 后端用 `streamText` + `toDataStreamResponse`，前端用 `useChat`；② 工具用 Zod 定义参数 schema，description 是 LLM 理解工具的关键；③ `maxSteps` 允许多轮工具调用；④ Vue 3 用 `@ai-sdk/vue` 的 `useChat`；⑤ 面试常考：Vercel AI SDK 核心 API、工具调用流程、流式输出原理、useChat 使用。

---


---
## 3. LangChain.js

### 3.1 核心组件

| 组件 | 说明 |
|------|------|
| `ChatOpenAI` | OpenAI 聊天模型 |
| `ChatPromptTemplate` | 提示词模板 |
| `RunnableSequence` | 链式调用（LCEL） |
| `AgentExecutor` | Agent 执行器 |
| `DynamicTool` | 动态工具定义 |
| `ConversationBufferMemory` | 对话记忆 |
| `RecursiveCharacterTextSplitter` | 文本切分 |
| `MemoryVectorStore` | 内存向量存储 |


> 🔍 **知识点深度解析**
>
> **作用**：熟悉 LangChain.js 的组件体系，是组合复杂链与 Agent 的前提。
>
> **原理**：LangChain 将 LLM 应用拆成可组合单元：模型（ChatOpenAI）、提示模板、链（RunnableSequence）、Agent 执行器、工具、记忆、切分器、向量库。
>
> **用法要点**：① 模型与提示模板解耦，便于复用与测试  ② Runnable 接口让组件可 pipe 串联  ③ 记忆组件负责多轮上下文  ④ 切分器决定 RAG 检索粒度  ⑤ 组件化使复杂流程可维护、可观测

### 3.2 LCEL 链式调用

```typescript
import { ChatOpenAI } from '@langchain/openai';
import { ChatPromptTemplate } from '@langchain/core/prompts';
import { StringOutputParser } from '@langchain/core/output_parsers';

const prompt = ChatPromptTemplate.fromTemplate(
  '用中文解释{topic}，适合初学者'
);
const model = new ChatOpenAI({ model: 'gpt-4o', temperature: 0.7 });
const parser = new StringOutputParser();

// LCEL 管道
const chain = prompt.pipe(model).pipe(parser);

const result = await chain.invoke({ topic: 'Transformer注意力机制' });
```


> 🔍 **知识点深度解析**
>
> **作用**：LCEL 是 LangChain 推荐的声明式编排方式，比旧 AgentExecutor 更灵活。
>
> **原理**：LCEL 通过 pipe（|）把 Prompt → Model → OutputParser 串成 RunnableSequence；每个节点实现统一 Runnable 接口（invoke/stream/batch），可运行时组合、并行、分支与回退。
>
> **用法要点**：① prompt.pipe(model).pipe(parser) 即可形成链  ② chain.invoke(input) 触发执行  ③ 支持 stream 流式与 batch 批处理  ④ 中间件式组合，易于插入自定义节点  ⑤ 比字符串拼接更类型安全、易调试

### 3.3 Agent + 工具调用

```typescript
import { createReactAgent } from '@langchain/langgraph/prebuilt';
import { DynamicTool } from '@langchain/core/tools';

const searchTool = new DynamicTool({
  name: 'web_search',
  description: '搜索互联网获取最新信息',
  func: async (query: string) => {
    return await searchAPI(query);
  },
});

const calculatorTool = new DynamicTool({
  name: 'calculator',
  description: '执行数学计算',
  func: async (expression: string) => {
    return String(eval(expression));
  },
});

const agent = createReactAgent({
  llm: model,
  tools: [searchTool, calculatorTool],
});

const result = await agent.invoke({
  messages: [{ role: 'user', content: '2024年GDP增长率乘以2是多少？' }],
});
```


> 🔍 **知识点深度解析**
>
> **作用**：Agent 让模型自主决定调用哪些工具完成多步任务。
>
> **原理**：createReactAgent（LangGraph 预置）组合 LLM 与工具列表；运行时模型按 ReAct 思路“思考→调用工具→观察结果”循环，直到给出最终答案；DynamicTool 用 name/description/func 描述能力。
>
> **用法要点**：① 工具 description 是模型选择的关键  ② func 必须是 async 且返回字符串  ③ 避免用 eval 等危险实现（示例仅为演示）  ④ 多工具组合可实现检索+计算+问答  ⑤ Agent 适合开放、多步骤任务，简单任务用普通链即可

### 3.4 RAG 完整实现

```typescript
import { OpenAIEmbeddings } from '@langchain/openai';
import { MemoryVectorStore } from 'langchain/vectorstores/memory';
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter';

// 1. 文档切分
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 500,
  chunkOverlap: 50,
});
const docs = await splitter.createDocuments([longText]);

// 2. 向量化存储
const embeddings = new OpenAIEmbeddings();
const vectorStore = await MemoryVectorStore.fromDocuments(docs, embeddings);

// 3. 检索链
const retriever = vectorStore.asRetriever(5);
const relevantDocs = await retriever.invoke('用户问题');

// 4. 生成
const context = relevantDocs.map(d => d.pageContent).join('\n');
const answer = await chain.invoke({
  context,
  question: '用户问题',
});
```

---


> 🔍 **知识点深度解析**
>
> **作用**：RAG 让模型基于私有/最新知识作答，缓解幻觉与知识截止。
>
> **原理**：先把文档用 RecursiveCharacterTextSplitter 切成 chunk，用 OpenAIEmbeddings 向量化存入向量库；检索时把问题向量化，取 topK 相似 chunk 拼进提示词，再让模型据此生成答案。
>
> **用法要点**：① chunkSize/chunkOverlap 影响检索召回与噪声  ② embeddings 需与检索时同一模型  ③ asRetriever(k) 控制返回条数  ④ 上下文拼接要注意 token 上限  ⑤ 可加 rerank 提升相关性


---
## 4. OpenAI Node SDK（底层方案）

### 4.1 基础调用

```typescript
import OpenAI from 'openai';

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const completion = await client.chat.completions.create({
  model: 'gpt-4o',
  messages: [
    { role: 'system', content: '你是一个有用的助手' },
    { role: 'user', content: '你好' },
  ],
  temperature: 0.7,
});

console.log(completion.choices[0].message.content);
```


> 🔍 **知识点深度解析**
>
> **作用**：OpenAI Node SDK 是调用 GPT 的最底层封装，适合简单/定制场景。
>
> **原理**：实例化 OpenAI 客户端（传 apiKey），调用 chat.completions.create 传入 model/messages（role 分 system/user/assistant），返回 choices[0].message.content；temperature 控制随机性。
>
> **用法要点**：① messages 数组决定对话上下文  ② system 消息设定人设与约束  ③ temperature 越高越发散  ④ 用环境变量管理密钥，禁止硬编码  ⑤ 适合直接、无框架需求的小调用

### 4.2 流式输出

```typescript
const stream = await client.chat.completions.create({
  model: 'gpt-4o',
  messages: [{ role: 'user', content: '写一首诗' }],
  stream: true,
});

for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content || '');
}
```


> 🔍 **知识点深度解析**
>
> **作用**：流式让大模型“边生成边返回”，显著降低首字延迟、提升体验。
>
> **原理**：create 时传 stream:true，返回异步可迭代流；逐块读取 chunk.choices[0].delta.content 并写入响应体（或前端 SSE），实现打字机效果。
>
> **用法要点**：① stream:true 返回 AsyncIterable  ② 用 for await 逐块消费 delta.content  ③ 空值需兜底（?.）  ④ 后端常把流透传给前端避免缓冲  ⑤ 与前端打字机/Markdown 渲染配合

### 4.3 工具调用（手动实现）

```typescript
const tools = [{
  type: 'function',
  function: {
    name: 'get_weather',
    description: '查询天气',
    parameters: {
      type: 'object',
      properties: { city: { type: 'string' } },
      required: ['city'],
    },
  },
}];

const response = await client.chat.completions.create({
  model: 'gpt-4o',
  messages,
  tools,
});

const toolCall = response.choices[0].message.tool_calls?.[0];
if (toolCall) {
  const args = JSON.parse(toolCall.function.arguments);
  const result = await getWeather(args.city);
  // 将结果返回 LLM 继续生成
}
```

---


> 🔍 **知识点深度解析**
>
> **作用**：不依赖高级框架时，手工实现工具调用了解其底层机制。
>
> **原理**：在请求中传 tools（function 定义含 name/description/parameters JSON Schema）；模型回复 message.tool_calls 时，本地解析 arguments、执行对应函数、把结果作为新消息回传模型继续生成。
>
> **用法要点**：① tools 用 JSON Schema 描述参数  ② 需自检 tool_calls 是否存在再处理  ③ 执行结果以 assistant+tool 消息回灌  ④ 多轮循环可实现多步工具链  ⑤ 比 SDK 封装更可控，但需自己管理状态


---
## 5. 向量数据库集成（TS）

| 数据库 | SDK | 适用场景 |
|--------|-----|----------|
| **Pinecone** | `@pinecone-database/pinecone` | 托管向量数据库，生产首选 |
| **Supabase pgvector** | `@supabase/supabase-js` | PostgreSQL 扩展，全栈友好 |
| **Chroma** | `chromadb` | 本地开发，轻量 |
| **Qdrant** | `@qdrant/js-client-rest` | 高性能 Rust 实现 |
| **Redis** | `redis` | 已有 Redis 基础设施 |
| **Weaviate** | `weaviate-ts-client` | 模块化向量数据库 |

```typescript
// Pinecone 示例
import { Pinecone } from '@pinecone-database/pinecone';

const pc = new Pinecone({ apiKey: process.env.PINECONE_API_KEY });
const index = pc.index('my-index');

//  upsert 向量
await index.upsert([{
  id: 'doc1',
  values: embeddingVector,
  metadata: { text: '文档内容', source: 'file.pdf' },
}]);

// 相似度搜索
const results = await index.query({
  topK: 5,
  vector: queryEmbedding,
  includeMetadata: true,
});
```

---


---
## 6. 多 Agent 协作（LangGraph.js）

```typescript
import { StateGraph, END } from '@langchain/langgraph';
import { HumanMessage, AIMessage } from '@langchain/core/messages';

// 定义状态
const agentState = {
  messages: { value: (x, y) => x.concat(y), default: () => [] },
};

// 研究员节点
const researcherNode = async (state) => {
  const result = await researchAgent.invoke(state.messages);
  return { messages: [result] };
};

// 撰稿人节点
const writerNode = async (state) => {
  const result = await writerAgent.invoke(state.messages);
  return { messages: [result] };
};

// 构建图
const workflow = new StateGraph(agentState)
  .addNode('researcher', researcherNode)
  .addNode('writer', writerNode)
  .addEdge('researcher', 'writer')
  .addEdge('writer', END)
  .setEntryPoint('researcher');

const app = workflow.compile();
const result = await app.invoke({
  messages: [new HumanMessage('研究AI Agent最新进展并写一篇文章')],
});
```

---

## 6.1 模型路由与 Fallback

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';

// 模型分级路由
async function smartGenerate(prompt: string) {
  const complexity = estimateComplexity(prompt);
  const model = complexity < 50
    ? openai('gpt-4o-mini')
    : complexity < 80
    ? openai('gpt-4o')
    : anthropic('claude-3-5-sonnet-20240620');

  return generateText({ model, prompt });
}

// Fallback 降级链
async function generateWithFallback(prompt: string) {
  const models = [
    openai('gpt-4o'),
    openai('gpt-4o-mini'),
    anthropic('claude-3-haiku'),
  ];

  for (const model of models) {
    try {
      const { text } = await generateText({ model, prompt });
      return text;
    } catch (error) {
      console.warn(`模型 ${model.modelId} 失败，尝试下一个`);
      continue;
    }
  }
  throw new Error('所有模型均不可用');
}
```

---


> 🔍 **知识点深度解析**
>
> **作用**：模型路由与降级在成本、质量与可用性之间取得平衡。
>
> **原理**：路由按任务复杂度选择模型（简单用 mini、复杂用旗舰、超复杂用 Claude 等）；Fallback 把模型排成降级链，前一个失败（异常/限流）自动切下一个，直到全部失败才报错。
>
> **用法要点**：① 按复杂度/语种/成本分级路由  ② 降级链按稳定性与成本排序（主→备）  ③ 捕获异常后 continue 尝试下一模型  ④ 记录失败模型便于告警  ⑤ 可结合超时与限流策略

## 6.2 可观测性（LangSmith / Langfuse）

```typescript
// LangSmith 追踪
import { Client } from 'langsmith';

const langsmithClient = new Client({
  apiKey: process.env.LANGSMITH_API_KEY,
});

// LangChain.js 自动追踪
process.env.LANGCHAIN_TRACING_V2 = 'true';
process.env.LANGCHAIN_API_KEY = 'your-api-key';
process.env.LANGCHAIN_PROJECT = 'my-agent';

// 手动记录 Trace
async function tracedAgentCall(messages: any[]) {
  const runId = crypto.randomUUID();
  const startTime = Date.now();

  try {
    const result = await agent.invoke({ messages });
    await langsmithClient.createRun({
      runId,
      name: 'agent_call',
      runType: 'chain',
      inputs: { messages },
      outputs: { result },
      startTime,
      endTime: Date.now(),
      sessionName: 'production',
    });
    return result;
  } catch (error) {
    await langsmithClient.createRun({
      runId,
      name: 'agent_call',
      runType: 'chain',
      inputs: { messages },
      error: String(error),
      startTime,
      endTime: Date.now(),
    });
    throw error;
  }
}
```

---


> 🔍 **知识点深度解析**
>
> **作用**：可观测性用于追踪、调试与优化生产中的 Agent 调用。
>
> **原理**：LangSmith 通过环境变量开启自动追踪（记录每次 LLM/链的输入输出、延迟、token），也可手动 createRun 上报；Langfuse 提供开源自托管追踪；二者都能还原调用链路。
>
> **用法要点**：① LANGCHAIN_TRACING_V2=true 开启自动追踪  ② 按 project 隔离不同环境  ③ 手动 trace 记录输入/输出/错误/耗时  ④ 关注 token 消耗与 P95 延迟  ⑤ 生产环境必做，便于回归与成本控制

## 6.3 生产部署


> 🔍 **知识点深度解析**
>
> **作用**：部署形态决定延迟、成本与运维复杂度。
>
> **原理**：边缘函数（Vercel Edge/Cloudflare Workers）在全球节点就近执行、低延迟，适合轻量流式接口；Node.js 服务与 Docker 提供完整生态与可控性，适合重计算与私有部署。
>
> **用法要点**：① Vercel Edge 用 runtime='edge' 获得低延迟  ② Cloudflare Workers 可绑定 AI 网关  ③ 注意函数超时与冷启动限制  ④ 重逻辑用 Node/Docker 自行运维  ⑤ 流式响应需正确的 Content-Type（text/event-stream）

### Vercel Functions（Next.js / Nuxt）

```typescript
// app/api/chat/route.ts - Edge Runtime
export const runtime = 'edge';  // 边缘函数，低延迟

export async function POST(req: Request) {
  const { messages } = await req.json();
  const result = streamText({
    model: openai('gpt-4o'),
    messages,
  });
  return result.toDataStreamResponse();
}
```


> 🔍 **知识点深度解析**
>
> **作用**：Vercel Functions 是部署 AI 流式接口最省心的方式。
>
> **原理**：在 route.ts 中导出 POST，内部调用 streamText 并以 toDataStreamResponse 返回；设置 runtime='edge' 可在边缘节点运行，缩短到用户的网络距离。
>
> **用法要点**：① 用 Next/Nuxt 约定路由暴露 /api/chat  ② edge runtime 降低首字延迟  ③ 需处理超时与区域限制  ④ 配合 useChat 端到端流式  ⑤ 适合托管、无需自建服务

### Cloudflare Workers

```typescript
// worker.ts
export default {
  async fetch(request: Request, env: Env) {
    const { messages } = await request.json();
    const result = await env.AI.run('@cf/meta/llama-3-8b-instruct', {
      messages,
      stream: true,
    });
    return new Response(result, {
      headers: { 'Content-Type': 'text/event-stream' },
    });
  },
};
```


> 🔍 **知识点深度解析**
>
> **作用**：Cloudflare Workers 提供全球边缘运行与内置 AI 绑定。
>
> **原理**：Worker 的 fetch 处理函数接收请求，可调用 env.AI.run 在边缘执行模型（如 Llama），并以 SSE 流式返回；部署在全球节点，就近低延迟。
>
> **用法要点**：① 用 env.AI.run 调用绑定模型  ② 流式返回需设 text/event-stream 头  ③ 注意 CPU/冷启动限制  ④ 适合轻量推理与网关  ⑤ 与 R2/KV 结合可做无服务器 RAG

### 部署注意事项

| 平台 | 优势 | 限制 |
|------|------|------|
| **Vercel** | Next.js 原生、Edge Runtime | 函数超时限制 |
| **Cloudflare Workers** | 全球边缘、AI 绑定 | 冷启动、CPU 限制 |
| **Node.js 服务器** | 完整 Node 生态 | 需自行运维 |
| **Docker + K8s** | 完全可控 | 运维复杂 |

---


> 🔍 **知识点深度解析**
>
> **作用**：选择部署平台需权衡延迟、限制与运维成本。
>
> **原理**：各平台在运行时、超时、冷启动、生态上各有取舍：Vercel 易用但有函数超时，Cloudflare 全球边缘但 CPU 受限，Node/Docker 完全可控但需自运维。
>
> **用法要点**：① Vercel 原生 Next/Nuxt，适合前端主导团队  ② Cloudflare 适合全球低延迟与 AI 绑定  ③ Node 服务器生态完整  ④ Docker+K8s 可控但运维重  ⑤ 按流量与合规选择

## 6.4 错误处理与重试

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

async function generateWithRetry(prompt: string, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const { text } = await generateText({
        model: openai('gpt-4o'),
        prompt,
      });
      return text;
    } catch (error: any) {
      // 429 限流：指数退避
      if (error.status === 429) {
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(r => setTimeout(r, delay));
        continue;
      }
      // 5xx 服务端错误：重试
      if (error.status >= 500) {
        await new Promise(r => setTimeout(r, 1000 * (attempt + 1)));
        continue;
      }
      // 4xx 客户端错误：不重试
      throw error;
    }
  }
  throw new Error('重试次数耗尽');
}
```

---


> 🔍 **知识点深度解析**
>
> **作用**：健壮的错误处理保障生产环境稳定性。
>
> **原理**：对可恢复错误（429 限流、5xx 服务端）采用指数退避重试，对不可恢复错误（4xx 客户端）直接抛出；重试耗尽后降级或报错。
>
> **用法要点**：① 429 用 2^attempt 指数退避  ② 5xx 服务端错误重试  ③ 4xx 不重试（参数错误）  ④ 设最大重试次数防死循环  ⑤ 可叠加超时与备用模型降级


---
## 7. 面试高频考点

1. **Vercel AI SDK 核心**：streamText、useChat、tool、streamObject
2. **工具调用流程**：LLM 返回 tool_call → 执行工具 → 结果返回 LLM
3. **流式输出原理**：SSE、ReadableStream、逐块解析
4. **LangChain.js LCEL**：pipe 管道、Runnable 接口
5. **RAG 实现**：切分→向量化→存储→检索→生成
6. **结构化输出**：Zod schema、streamObject、JSON 约束
7. **useChat 使用**：messages/input/handleSubmit/isLoading
8. **OpenAI Node SDK**：chat.completions.create、stream、tools
9. **向量数据库**：Pinecone/Supabase pgvector/Chroma 对比
10. **多 Agent**：LangGraph StateGraph、节点/边/状态
11. **模型路由**：复杂度分级、Fallback 降级链、多模型容灾
12. **可观测性**：LangSmith/Langfuse 追踪、Token 统计、延迟监控
13. **生产部署**：Vercel Edge Functions、Cloudflare Workers、Docker
14. **错误处理**：429 指数退避、5xx 重试、4xx 不重试、超时控制
15. **记忆管理**：ConversationBufferMemory、按会话隔离、Redis 持久化
16. **国内模型接入**：通义/文心/豆包/DeepSeek 的 TS SDK
17. **成本控制**：模型分级、缓存、Token 统计、早期终止
18. **全栈架构**：前端 useChat → 后端 streamText → LLM API → 流式返回

---


---
## 📝 精简总结

- TS AI Agent 三大方案：Vercel AI SDK（全栈首选，轻量高性能）、LangChain.js（功能全面，RAG/Agent强）、OpenAI Node SDK（底层官方）
- Vercel AI SDK：`streamText` 后端流式生成 + `useChat` 前端聊天钩子 + `tool()` 工具定义 + `streamObject` 结构化输出
- 工具调用：LLM 判断需要工具 → 返回函数名+参数 → SDK 自动执行 execute → 结果返回 LLM 继续生成（maxSteps 控制轮次）
- 流式输出：SSE 数据流，前端 useChat 自动解析，逐字显示提升体验
- LangChain.js：LCEL 管道（prompt.pipe(model).pipe(parser)）、AgentExecutor、DynamicTool、ConversationBufferMemory
- RAG：RecursiveCharacterTextSplitter 切分 → OpenAIEmbeddings 向量化 → VectorStore 存储 → asRetriever 检索 → 上下文拼接生成
- OpenAI Node SDK：chat.completions.create、stream:true 流式、tools 手动实现工具调用
- 向量数据库：Pinecone（托管生产首选）、Supabase pgvector（全栈友好）、Chroma（本地开发）、Redis（已有基础设施）
- 多 Agent：LangGraph.js StateGraph，节点（处理函数）+ 边（流转）+ 状态（共享消息），顺序/并行/条件分支
- 模型路由：复杂度分级（简单用mini/复杂用4o）、Fallback 降级链（主模型失败自动切备用）
- 可观测性：LangSmith/Langfuse 追踪（记录输入输出/延迟/Token）、LANGCHAIN_TRACING_V2 自动追踪、生产环境必做
- 生产部署：Vercel Edge Functions（低延迟）、Cloudflare Workers（全球边缘+AI绑定）、Node.js服务器（完整生态）、Docker+K8s（完全可控）
- 错误处理：429 指数退避重试、5xx 服务端错误重试、4xx 客户端错误不重试、超时控制、降级备用模型
- Vue 3 集成：`@ai-sdk/vue` 的 useChat，响应式 messages/input/handleSubmit
- 结构化输出：Zod schema 约束，streamObject 流式接收部分对象
- 最佳实践：全栈用 Vercel AI SDK、复杂 Agent 用 LangChain.js、简单调用用 OpenAI SDK、生产用 Pinecone/Supabase pgvector、可观测性+错误重试+模型降级必做

---

[[01-前端开发/MOC-前端开发|← 返回前端开发 MOC]] | [[Home|🏠 返回首页]]
