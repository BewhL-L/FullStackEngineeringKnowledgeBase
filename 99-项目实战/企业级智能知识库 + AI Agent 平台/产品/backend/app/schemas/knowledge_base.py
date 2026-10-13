"""知识库相关 Schema"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class KBCreate(BaseModel):
    """创建知识库"""
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: str = Field("", max_length=500, description="描述")


class KBUpdate(BaseModel):
    """更新知识库"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class KBResponse(BaseModel):
    """知识库响应"""
    id: int
    name: str
    description: str
    embed_code: Optional[str] = None
    document_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KBDetail(KBResponse):
    """知识库详情"""
    pass
