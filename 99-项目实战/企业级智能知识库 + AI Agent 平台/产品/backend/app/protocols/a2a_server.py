"""
A2A（Agent2Agent）协议示例
让本系统的知识库 Agent 能被其他 A2A 客户端 / Agent 发现并调用：
- Agent Card：GET /a2a/.well-known/agent.json
- 发送消息：POST /a2a/（JSON-RPC，method=message/send）
为便于理解，这里同步执行并直接返回 Task，不依赖额外 SDK。
kb_id 可放在 message.metadata.kb_id 中传入。
"""
import uuid

from fastapi import APIRouter, Request

from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/a2a", tags=["A2A"])

AGENT_CARD = {
    "protocolVersion": "0.2.0",
    "name": "enterprise-kb-agent",
    "description": "企业知识库问答 Agent（RAG + 工具调用）",
    "url": "http://localhost:8000/a2a/",
    "version": "1.0.0",
    "capabilities": {"streaming": False, "pushNotifications": False},
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],
    "skills": [
        {
            "id": "kb-qa",
            "name": "知识库问答",
            "description": "基于企业知识库回答问题并给出依据",
            "tags": ["rag", "knowledge-base"],
        }
    ],
}


@router.get("/.well-known/agent.json")
async def agent_card():
    return AGENT_CARD


@router.post("/")
async def rpc(request: Request):
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})
    req_id = body.get("id")

    if method in ("message/send", "message/stream"):
        text, kb_id = _extract(params)
        answer = await _answer(text, kb_id)
        return _ok(req_id, _task(answer))
    if method == "tasks/get":
        return _ok(req_id, {"id": params.get("id"), "status": {"state": "completed"}})
    return _err(req_id, -32601, f"Method not found: {method}")


def _extract(params: dict):
    msg = params.get("message", {})
    parts = msg.get("parts", [])
    text = "".join(p.get("text", "") for p in parts if "text" in p) or msg.get("text", "")
    metadata = msg.get("metadata", {}) or {}
    kb_id = metadata.get("kb_id")
    return text, kb_id


async def _answer(text: str, kb_id=None):
    from ..services.rag_service import rag_service

    target = kb_id or 1
    r = await rag_service.chat(target, text)
    return r["answer"]


def _task(output: str) -> dict:
    return {
        "id": uuid.uuid4().hex,
        "status": {"state": "completed"},
        "artifacts": [{"parts": [{"text": output}]}],
    }


def _ok(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
