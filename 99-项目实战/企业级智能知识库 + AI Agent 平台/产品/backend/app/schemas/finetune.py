"""微调数据导出 schema"""
from pydantic import BaseModel, Field
from typing import Optional


class FinetuneExportRequest(BaseModel):
    """导出微调数据请求"""
    type: str = Field("sft", pattern="^(sft|dpo)$")
    kb_id: Optional[int] = None
