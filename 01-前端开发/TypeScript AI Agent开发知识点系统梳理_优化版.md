---
title: TypeScript AI Agent 开发知识点系统梳理
tags: [前端, TypeScript, AIAgent, LangChain, VercelAISDK, AIGC, 面试]
created: 2026-08-13
updated: 2026-08-13
---

# TypeScript AI Agent 开发知识点系统梳理（优化版）

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

## 6.3 生产部署

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

### 部署注意事项

| 平台 | 优势 | 限制 |
|------|------|------|
| **Vercel** | Next.js 原生、Edge Runtime | 函数超时限制 |
| **Cloudflare Workers** | 全球边缘、AI 绑定 | 冷启动、CPU 限制 |
| **Node.js 服务器** | 完整 Node 生态 | 需自行运维 |
| **Docker + K8s** | 完全可控 | 运维复杂 |

---

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
