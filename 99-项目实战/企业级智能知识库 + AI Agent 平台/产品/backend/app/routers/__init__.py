"""路由汇总"""
from . import (
    auth,
    knowledge_bases,
    documents,
    conversations,
    chat,
    stats,
    agent,
    evaluation,
    wiki,
    graphrag,
    finetune,
)

routers = [
    auth.router,
    knowledge_bases.router,
    documents.router,
    conversations.router,
    chat.router,
    stats.router,
    agent.router,
    evaluation.router,
    wiki.router,
    graphrag.router,
    finetune.router,
]
