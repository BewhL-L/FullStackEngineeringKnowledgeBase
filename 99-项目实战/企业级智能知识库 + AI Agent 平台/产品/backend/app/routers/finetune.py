"""
微调数据导出路由
- 预览 / 导出 SFT、DPO 数据集（JSON）
- 前端可直接下载为 jsonl，再用 scripts/finetune 下的脚本训练
"""
import os
import json
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..models import User
from ..utils.deps import get_current_user
from ..database import get_db
from ..config import settings
from ..services.finetune_data import finetune_data_service
from ..schemas.finetune import FinetuneExportRequest
from .knowledge_bases import _get_owned_kb

router = APIRouter(prefix="/finetune", tags=["模型微调"])


@router.post("/preview", summary="预览可导出的微调数据")
def preview(
    data: FinetuneExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.kb_id:
        _get_owned_kb(db, data.kb_id, current_user.id)
    if data.type == "sft":
        dataset = finetune_data_service.build_sft_dataset(db, data.kb_id)
    else:
        dataset = finetune_data_service.build_dpo_dataset(db, data.kb_id)
    return {
        "type": data.type,
        "count": len(dataset),
        "sample": dataset[:3],
    }


@router.post("/export", summary="导出微调数据文件（jsonl）")
def export(
    data: FinetuneExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.kb_id:
        _get_owned_kb(db, data.kb_id, current_user.id)
    if data.type == "sft":
        dataset = finetune_data_service.build_sft_dataset(db, data.kb_id)
    else:
        dataset = finetune_data_service.build_dpo_dataset(db, data.kb_id)

    os.makedirs("./exports", exist_ok=True)
    filename = f"{data.type}_kb{data.kb_id or 'all'}.jsonl"
    path = os.path.join("./exports", filename)
    finetune_data_service.export_jsonl(dataset, path)
    return FileResponse(
        path, filename=filename, media_type="application/x-jsonlines"
    )
