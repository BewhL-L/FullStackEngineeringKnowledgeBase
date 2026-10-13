"""
增强版批量内容填充脚本
为所有三级笔记的四级子知识点生成结构化实际内容
"""
import re
import os
from pathlib import Path

BASE_DIR = r"C:\Users\23981\Desktop\AI文档\DouBao Document\全栈工程MarkDown文档\10-四级知识框架"

# ============================================================
# 知识点内容库：为常见技术术语预定义高质量内容
# ============================================================

CONTENT_LIBRARY = {
    # === Python ===
    "异步编程": {
        "concept": "异步编程是一种并发编程范式，通过事件循环和协程实现非阻塞IO，在单线程中处理多个任务。Python 通过 asyncio 模块提供原生异步支持。",
        "points": [
            "async/await 语法：async 定义协程函数，await 挂起等待异步操作",
            "事件循环（Event Loop）：调度和执行协程任务的核心机制",
            "非阻塞IO：网络请求、文件读写等操作不阻塞主线程",
            "协程 vs 线程：协程更轻量，切换开销更小，适合IO密集型任务",
            "asyncio.gather()：并发执行多个协程并收集结果",
        ],
        "code": """import asyncio

async def fetch_data(url):
    # 模拟异步IO操作
    await asyncio.sleep(1)
    return f"Data from {url}"

async def main():
    # 并发执行多个请求
    results = await asyncio.gather(
        fetch_data("https://api1.com"),
        fetch_data("https://api2.com"),
        fetch_data("https://api3.com"),
    )
    for r in results:
        print(r)

asyncio.run(main())""",
        "faq": "Q: 异步编程能加速CPU密集型任务吗？\nA: 不能。异步编程只对IO密集型任务有效，CPU密集型任务应使用多进程。",
    },
    "装饰器": {
        "concept": "装饰器是 Python 的一种语法糖，用于在不修改原函数代码的情况下扩展函数功能。本质上是一个接收函数并返回新函数的高阶函数。",
        "points": [
            "函数是一等公民：可以作为参数传递、作为返回值、赋值给变量",
            "@decorator 语法糖：等价于 func = decorator(func)",
            "带参数的装饰器：需要三层嵌套函数",
            "functools.wraps：保留原函数的元信息（名称、文档字符串）",
            "类装饰器：通过 __call__ 方法实现",
        ],
        "code": """import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "done"

# 带参数的装饰器
def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator""",
        "faq": "Q: 装饰器和继承有什么区别？\nA: 装饰器是组合模式，动态扩展功能；继承是静态的，通过子类扩展。装饰器更灵活，可叠加使用。",
    },
    # === FastAPI ===
    "依赖注入": {
        "concept": "依赖注入是一种设计模式，将对象的创建和使用分离，由外部容器负责注入依赖。FastAPI 通过 Depends() 实现强大的依赖注入系统。",
        "points": [
            "Depends() 声明依赖：FastAPI 自动解析并注入",
            "依赖嵌套：依赖可以依赖其他依赖，形成依赖树",
            "全局依赖：通过 app.dependencies 应用到所有路由",
            "依赖作用域：默认每个请求创建一次，可使用 yield 实现资源清理",
            "类依赖：可注入类实例，支持 __init__ 参数自动解析",
        ],
        "code": """from fastapi import FastAPI, Depends, HTTPException

app = FastAPI()

# 函数依赖
async def get_db():
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()

# 类依赖
class CurrentUser:
    def __init__(self, token: str = Header(...)):
        self.user = verify_token(token)
        if not self.user:
            raise HTTPException(401)

@app.get("/items/")
async def list_items(
    db = Depends(get_db),
    user: CurrentUser = Depends(),
):
    return db.query(Item).filter(owner=user.id).all()""",
        "faq": "Q: 依赖注入和直接 import 有什么区别？\nA: 依赖注入便于测试（可 mock 依赖）、复用和生命周期管理，直接 import 是硬编码耦合。",
    },
    # === Vue3 ===
    "响应式原理": {
        "concept": "Vue3 使用 ES6 Proxy 实现响应式系统，通过拦截对象的 get/set 操作自动追踪依赖并触发更新。相比 Vue2 的 Object.defineProperty，Proxy 支持数组、动态属性等。",
        "points": [
            "Proxy 代理：拦截对象的所有操作，包括属性访问、赋值、删除",
            "Reflect 操作：在拦截器中使用 Reflect 执行原始操作",
            "依赖收集（track）：在 get 时收集当前 effect 作为依赖",
            "触发更新（trigger）：在 set 时通知所有依赖重新执行",
            "ref vs reactive：ref 用于基本类型，reactive 用于对象",
        ],
        "code": """// Vue3 响应式核心原理简化实现
function reactive(target) {
  return new Proxy(target, {
    get(obj, key) {
      track(obj, key)  // 收集依赖
      return Reflect.get(obj, key)
    },
    set(obj, key, value) {
      Reflect.set(obj, key, value)
      trigger(obj, key)  // 触发更新
      return true
    }
  })
}

// 使用
const state = reactive({ count: 0 })
effect(() => console.log(state.count))  // 输出: 0
state.count++  // 触发更新，输出: 1""",
        "faq": "Q: Vue3 为什么用 Proxy 替代 Object.defineProperty？\nA: Proxy 支持数组索引修改、动态属性添加、Map/Set 等，且不需要递归遍历整个对象，性能更好。",
    },
    # === TypeScript ===
    "泛型": {
        "concept": "泛型是 TypeScript 的类型参数化机制，允许在定义函数、类或接口时不指定具体类型，使用时再确定。提高代码复用性和类型安全。",
        "points": [
            "类型参数 <T>：在函数/类定义时声明，使用时推断或指定",
            "泛型约束 extends：限制类型参数必须满足特定结构",
            "条件类型 T extends U ? X : Y：根据类型关系选择类型",
            "infer 关键字：在条件类型中提取类型",
            "工具类型：Partial、Required、Pick、Omit、Record 等",
        ],
        "code": """// 基础泛型函数
function identity<T>(arg: T): T {
  return arg
}
const num = identity<number>(42)  // 类型: number
const str = identity("hello")     // 类型推断: string

// 泛型约束
interface HasLength {
  length: number
}
function logLength<T extends HasLength>(arg: T): void {
  console.log(arg.length)
}

// 条件类型 + infer
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never
type FnReturn = ReturnType<() => string>  // string""",
        "faq": "Q: 泛型和 any 有什么区别？\nA: 泛型保留类型信息，编译器可以检查类型安全；any 放弃类型检查，失去类型安全保护。",
    },
    # === AI / RAG ===
    "RAG": {
        "concept": "RAG（Retrieval-Augmented Generation，检索增强生成）是一种结合信息检索和大语言模型的技术，通过从外部知识库检索相关文档并注入到 Prompt 中，让模型基于私有知识生成回答。",
        "points": [
            "索引阶段：文档加载 → 分块 → 向量化 → 存入向量数据库",
            "检索阶段：查询向量化 → 相似度搜索 → 返回 Top-K 相关文档",
            "生成阶段：将检索到的文档作为上下文拼入 Prompt → LLM 生成回答",
            "解决幻觉问题：模型基于检索到的事实回答，减少编造",
            "知识更新方便：只需更新向量库，无需重新训练模型",
        ],
        "code": """# RAG 基本流程伪代码
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI

# 1. 索引构建
documents = load_documents("docs/")
chunks = split_documents(documents, chunk_size=500)
vectorstore = Chroma.from_documents(chunks, OpenAIEmbeddings())

# 2. 检索
query = "如何配置 FastAPI 依赖注入？"
relevant_docs = vectorstore.similarity_search(query, k=3)

# 3. 生成
context = "\\n".join([doc.page_content for doc in relevant_docs])
prompt = f"基于以下内容回答问题：\\n{context}\\n\\n问题：{query}"
answer = ChatOpenAI().predict(prompt)""",
        "faq": "Q: RAG 和微调（Fine-tuning）有什么区别？\nA: RAG 是检索外部知识，适合频繁更新的知识；微调是将知识融入模型参数，适合风格/格式学习，成本高且更新慢。",
    },
    "Transformer": {
        "concept": "Transformer 是一种基于自注意力机制的神经网络架构，由 Google 在 2017 年提出，是现代大语言模型（GPT、BERT、LLaMA 等）的基础架构。",
        "points": [
            "自注意力（Self-Attention）：计算序列中每个 token 与其他所有 token 的关联权重",
            "多头注意力（Multi-Head Attention）：多组注意力并行捕捉不同语义关系",
            "位置编码（Positional Encoding）：为序列添加位置信息（Transformer 无递归结构）",
            "编码器-解码器架构：BERT 只用编码器，GPT 只用解码器",
            "残差连接 + LayerNorm：稳定深层网络训练",
        ],
        "code": """# 自注意力机制简化实现
import torch
import torch.nn.functional as F

def self_attention(Q, K, V):
    # Q, K, V: (batch, seq_len, d_model)
    d_k = Q.size(-1)
    # 计算注意力分数: Q @ K^T / sqrt(d_k)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / (d_k ** 0.5)
    # Softmax 归一化
    attn_weights = F.softmax(scores, dim=-1)
    # 加权求和
    output = torch.matmul(attn_weights, V)
    return output, attn_weights""",
        "faq": "Q: Transformer 为什么比 RNN 效果好？\nA: Transformer 通过自注意力实现并行计算（RNN 必须串行），且能直接捕捉长距离依赖，训练效率和效果都更优。",
    },
    # === DevOps ===
    "Docker": {
        "concept": "Docker 是一个开源的容器化平台，通过将应用及其依赖打包到轻量级容器中，实现应用在不同环境中的一致运行。容器共享主机内核，比虚拟机更轻量。",
        "points": [
            "镜像（Image）：只读模板，包含应用和依赖",
            "容器（Container）：镜像的运行实例，可读写",
            "Dockerfile：定义镜像构建步骤的脚本",
            "分层存储：镜像由多层组成，共享层节省空间",
            "Volume：数据持久化，容器删除后数据保留",
        ],
        "code": """# Dockerfile 示例
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# 构建和运行
# docker build -t myapp .
# docker run -p 8000:8000 myapp""",
        "faq": "Q: 容器和虚拟机有什么区别？\nA: 容器共享主机内核，启动快（秒级）、资源占用小；虚拟机有独立内核，启动慢（分钟级）、隔离性更强。",
    },
    "Kubernetes": {
        "concept": "Kubernetes（K8s）是 Google 开源的容器编排平台，用于自动化部署、扩展和管理容器化应用。提供服务发现、负载均衡、自动扩缩容、滚动更新等能力。",
        "points": [
            "Pod：最小调度单元，可包含一个或多个容器",
            "Deployment：管理 Pod 的副本数和更新策略",
            "Service：为 Pod 提供稳定的网络访问入口",
            "Ingress：HTTP/HTTPS 路由规则，外部流量入口",
            "ConfigMap/Secret：配置和敏感信息管理",
        ],
        "code": """# Deployment 示例
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000""",
        "faq": "Q: 什么时候需要用 Kubernetes 而不是 Docker Compose？\nA: 当需要多主机部署、自动扩缩容、高可用、滚动更新等生产级能力时，K8s 更适合；单机开发测试用 Docker Compose 更简单。",
    },
    # === CS 基础 ===
    "TCP": {
        "concept": "TCP（Transmission Control Protocol，传输控制协议）是一种面向连接的、可靠的传输层协议，通过三次握手建立连接、四次挥手断开连接，提供数据有序、无差错、不丢失的传输保证。",
        "points": [
            "三次握手：SYN → SYN+ACK → ACK，建立可靠连接",
            "四次挥手：FIN → ACK → FIN → ACK，优雅断开连接",
            "滑动窗口：流量控制，接收方告知发送方可接收的数据量",
            "拥塞控制：慢启动、拥塞避免、快重传、快恢复",
            "可靠传输：序号、确认号、超时重传机制",
        ],
        "code": """# TCP 三次握手（伪代码）
# 客户端 → 服务端: SYN, seq=x
# 服务端 → 客户端: SYN+ACK, seq=y, ack=x+1
# 客户端 → 服务端: ACK, ack=y+1
# 连接建立完成

# Python TCP 服务端
import socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 8080))
server.listen(5)
conn, addr = server.accept()
data = conn.recv(1024)
conn.send(b'Hello')
conn.close()""",
        "faq": "Q: 为什么连接建立需要三次握手而不是两次？\nA: 两次握手无法确认客户端的接收能力，可能导致服务端资源浪费（已失效的连接请求）。三次握手确保双方收发能力都正常。",
    },
    "数据结构": {
        "concept": "数据结构是计算机存储和组织数据的方式，选择合适的数据结构可以显著提高算法效率。常见数据结构包括数组、链表、栈、队列、树、图、哈希表等。",
        "points": [
            "数组：连续内存，随机访问 O(1)，插入删除 O(n)",
            "链表：非连续内存，插入删除 O(1)，随机访问 O(n)",
            "栈：后进先出（LIFO），常用于函数调用、表达式求值",
            "队列：先进先出（FIFO），常用于任务调度、BFS",
            "哈希表：键值对存储，平均 O(1) 查找，需处理哈希冲突",
        ],
        "code": """# 常见数据结构 Python 实现
# 栈
stack = []
stack.append(1)  # push
stack.pop()      # pop

# 队列
from collections import deque
queue = deque()
queue.append(1)  # enqueue
queue.popleft()  # dequeue

# 哈希表
hash_map = {}
hash_map["key"] = "value"
value = hash_map["key"]  # O(1)""",
        "faq": "Q: 数组和链表如何选择？\nA: 需要频繁随机访问选数组；需要频繁插入删除选链表。实际开发中数组（动态数组）使用更广泛。",
    },
}

# ============================================================
# 通用内容生成器：基于知识点名称生成结构化内容
# ============================================================

def generate_content(topic, section_name=""):
    """根据知识点名称生成结构化内容"""
    topic_clean = topic.strip()
    
    # 1. 优先查找内容库（模糊匹配）
    for key, content in CONTENT_LIBRARY.items():
        if key.lower() in topic_clean.lower() or topic_clean.lower() in key.lower():
            return content
    
    # 2. 基于关键词模式生成
    return generate_by_pattern(topic_clean, section_name)


def generate_by_pattern(topic, section_name):
    """基于知识点名称模式生成内容"""
    
    # 判断知识点类型
    is_code_related = any(kw in topic.lower() for kw in [
        'api', '函数', '方法', '配置', '部署', '安装', '命令',
        '代码', '实现', '封装', '调用', '请求', '响应', '接口',
        '框架', '库', '插件', '组件', '模块', '类', '对象',
        '算法', '数据结构', '协议', '架构', '设计', '模式',
        '优化', '性能', '缓存', '并发', '异步', '线程',
        'docker', 'k8s', 'git', 'vue', 'react', 'python', 'java',
        'fastapi', 'spring', 'sql', 'redis', 'kafka',
    ])
    
    # 生成概念解释
    concept = generate_concept(topic, section_name)
    
    # 生成核心要点
    points = generate_points(topic)
    
    # 生成代码示例
    code = generate_code(topic) if is_code_related else ""
    
    # 生成常见问题
    faq = generate_faq(topic)
    
    return {
        "concept": concept,
        "points": points,
        "code": code,
        "faq": faq,
    }


def generate_concept(topic, section_name):
    """生成概念解释"""
    templates = [
        f"{topic}是{section_name}领域中的重要概念，指在特定场景下用于解决特定问题的方法或机制。理解其原理和适用场景对于构建高质量系统至关重要。",
        f"{topic}是现代软件开发中常用的技术手段，通过特定的设计思路实现更高效、更可靠的系统功能。在实际项目中需要根据具体需求合理应用。",
        f"{topic}涉及系统设计的核心思想，关注如何在复杂环境中实现目标功能。掌握该知识点有助于深入理解技术栈的底层原理。",
        f"{topic}是工程实践中总结出的最佳实践，旨在解决特定场景下的共性问题。正确应用可以显著提升开发效率和系统质量。",
    ]
    return templates[hash(topic) % len(templates)]


def generate_points(topic):
    """生成核心要点"""
    base_points = [
        f"基本概念与定义：理解{topic}的核心含义和解决的问题",
        "工作原理与机制：掌握底层实现逻辑和关键流程",
        "适用场景与边界：明确什么时候使用、什么时候不适合",
        "最佳实践与注意事项：总结实际使用中的经验和坑点",
        "与相关技术的对比：理解差异化优势和选型依据",
    ]
    
    # 根据主题调整
    if any(kw in topic for kw in ['原理', '机制', '架构']):
        base_points = [
            f"核心思想：{topic}的设计理念和解决的根本问题",
            "关键组件：系统的主要组成部分及其职责",
            "工作流程：从输入到输出的完整处理链路",
            "性能特点：时间/空间复杂度和资源消耗",
            "演进历史：技术发展脉络和版本差异",
        ]
    elif any(kw in topic for kw in ['配置', '安装', '部署', '使用']):
        base_points = [
            "环境准备：前置依赖和系统要求",
            "基础配置：核心参数和默认值说明",
            "高级配置：生产环境的优化选项",
            "常见问题排查：配置错误的诊断方法",
            "最佳实践：推荐的配置方案和规范",
        ]
    elif any(kw in topic for kw in ['对比', '选型', 'vs']):
        base_points = [
            "设计理念差异：各自的核心定位和目标场景",
            "功能特性对比：关键能力的支持情况",
            "性能表现：吞吐量、延迟、资源占用",
            "生态与社区：成熟度、文档、第三方支持",
            "选型建议：不同场景下的推荐方案",
        ]
    
    return base_points


def generate_code(topic):
    """生成代码示例"""
    # 生成安全的标识符名称
    import re as _re
    safe_name = _re.sub(r'[^a-zA-Z]', '', topic)[:20] or "Example"
    
    # 根据主题生成不同语言的示例
    if any(kw in topic.lower() for kw in ['python', 'fastapi', 'django', 'flask', 'rag', 'llm', 'agent']):
        return f"""# {topic} 示例代码
# 基础用法示例
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info(f"开始执行 {topic}")
    # TODO: 实现具体逻辑
    logger.info("执行完成")

if __name__ == "__main__":
    main()"""
    elif any(kw in topic.lower() for kw in ['vue', 'typescript', '前端', '组件', 'pinia', 'vite']):
        return f"""// {topic} 示例代码
import {{ ref, computed }} from 'vue'

export function use{safe_name}() {{
  const state = ref(null)
  const isLoading = ref(false)
  
  const computedValue = computed(() => {{
    return state.value ? state.value.length : 0
  }})
  
  async function execute() {{
    isLoading.value = true
    try {{
      // TODO: 实现具体逻辑
      state.value = await fetchData()
    }} finally {{
      isLoading.value = false
    }}
  }}
  
  return {{ state, isLoading, computedValue, execute }}
}}"""
    elif any(kw in topic.lower() for kw in ['java', 'spring', 'jvm', 'maven']):
        return f"""// {topic} 示例代码
@Service
public class {safe_name}Service {{
    
    private static final Logger log = LoggerFactory.getLogger(getClass());
    
    public void execute() {{
        log.info("开始执行 {{}}", topic);
        // TODO: 实现具体逻辑
        log.info("执行完成");
    }}
}}"""
    elif any(kw in topic.lower() for kw in ['docker', 'k8s', 'kubernetes', 'devops', '部署']):
        return f"""# {topic} 配置示例
# 基础配置
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
    restart: unless-stopped"""
    elif any(kw in topic.lower() for kw in ['sql', '数据库', 'redis', 'mongo', 'postgres']):
        return f"""-- {topic} SQL 示例
-- 基础查询
SELECT * FROM table_name
WHERE condition = true
ORDER BY created_at DESC
LIMIT 10;

-- 索引创建
CREATE INDEX idx_column ON table_name(column_name);"""
    else:
        return f"""# {topic} 示例
# 基础用法
# TODO: 根据具体知识点补充代码示例"""


def generate_faq(topic):
    """生成常见问题"""
    faqs = [
        f"Q: {topic}和相关技术有什么区别？\nA: 核心区别在于设计目标和适用场景。{topic}更侧重于特定场景下的优化，而相关技术可能有更广泛的适用性。",
        f"Q: 学习{topic}有哪些常见误区？\nA: 常见误区包括只记概念不理解原理、不区分适用场景盲目使用、忽略性能和可维护性权衡。",
        f"Q: {topic}在生产环境中有哪些注意事项？\nA: 需要关注性能瓶颈、错误处理、资源清理、监控告警和安全边界，确保系统稳定可靠。",
    ]
    return faqs[hash(topic) % len(faqs)]


# ============================================================
# 笔记处理逻辑
# ============================================================

def process_note(filepath, section_name):
    """处理单篇笔记，填充四级子知识点内容"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 检查是否已经填充过（包含"待补充"说明未填充）
    if "待补充：" not in content:
        return False  # 已填充，跳过
    
    # 提取所有四级子知识点标题
    sub_titles = re.findall(r'### (\d+)\.\s+(.+?)\n', content)
    
    for num, title in sub_titles:
        # 生成内容
        generated = generate_content(title.strip(), section_name)
        
        # 构建替换内容
        points_text = "\n".join([f"- {p}" for p in generated["points"]])
        
        code_block = ""
        if generated["code"]:
            code_block = f"""**代码示例**：
{generated["code"]}
"""
        
        replacement = f"""### {num}. {title.strip()}

{generated["concept"]}

**核心要点**：
{points_text}

{code_block}
**常见问题**：
{generated["faq"]}

---
"""
        
        # 替换原有的占位内容
        # 匹配从 "### num. title" 到下一个 "---" 之间的内容
        pattern = rf'### {re.escape(num)}\.\s+{re.escape(title.strip())}\n.*?(?=\n---\n)'
        content = re.sub(pattern, replacement.rstrip(), content, flags=re.DOTALL)
    
    # 更新状态
    content = content.replace("status: 🔴 未开始", "status: 🟡 骨架已填充")
    content = content.replace("**学习状态**：🔴 未开始", "**学习状态**：🟡 骨架已填充（待深入完善）")
    
    # 更新学习日志
    content = content.replace(
        "| 2026-08-13 | 创建笔记骨架 | 🔴 未开始 |",
        "| 2026-08-13 | 创建笔记骨架 | 🔴 未开始 |\n| 2026-08-13 | 批量填充四级子知识点内容 | 🟡 骨架已填充 |"
    )
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return True


def main():
    total_processed = 0
    total_skipped = 0
    
    # 遍历所有板块目录
    for section_dir in sorted(os.listdir(BASE_DIR)):
        section_path = os.path.join(BASE_DIR, section_dir)
        if not os.path.isdir(section_path) or section_dir == "00-总控":
            continue
        
        section_name = section_dir.split("-", 1)[1] if "-" in section_dir else section_dir
        
        # 遍历所有 .md 文件（排除 MOC 和枢纽）
        md_files = list(Path(section_path).glob("*.md"))
        for md_file in md_files:
            if "MOC" in md_file.name or "枢纽" in md_file.name:
                continue
            
            try:
                processed = process_note(str(md_file), section_name)
                if processed:
                    total_processed += 1
                    print(f"✅ {section_dir}/{md_file.name}")
                else:
                    total_skipped += 1
                    print(f"⏭️  {section_dir}/{md_file.name} (已填充)")
            except Exception as e:
                print(f"❌ {section_dir}/{md_file.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"🎉 完成！处理 {total_processed} 篇，跳过 {total_skipped} 篇")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
