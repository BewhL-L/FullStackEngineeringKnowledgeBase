"""知识库管理路由"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import User, KnowledgeBase, Document, Conversation
from ..schemas import KBCreate, KBUpdate, KBResponse
from ..utils.deps import get_current_user
from ..services import document_service

router = APIRouter(prefix="/kb", tags=["知识库"])


@router.post("", response_model=KBResponse, summary="创建知识库")
def create_kb(
    data: KBCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb = KnowledgeBase(
        name=data.name,
        description=data.description,
        user_id=current_user.id,
        embed_code=uuid.uuid4().hex[:16],
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return _to_response(kb, 0)


@router.get("", summary="知识库列表（分页）")
def list_kb(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(KnowledgeBase).filter(KnowledgeBase.user_id == current_user.id)
    if keyword:
        query = query.filter(KnowledgeBase.name.contains(keyword))
    total = query.count()
    kbs = query.order_by(KnowledgeBase.updated_at.desc()) \
        .offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for kb in kbs:
        doc_count = db.query(func.count(Document.id)) \
            .filter(Document.kb_id == kb.id, Document.status == "completed").scalar()
        items.append(_to_response(kb, doc_count).model_dump())
    return {"total": total, "items": items}


@router.get("/{kb_id}", response_model=KBResponse, summary="知识库详情")
def get_kb(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb = _get_owned_kb(db, kb_id, current_user.id)
    doc_count = db.query(func.count(Document.id)) \
        .filter(Document.kb_id == kb_id, Document.status == "completed").scalar()
    return _to_response(kb, doc_count)


@router.put("/{kb_id}", response_model=KBResponse, summary="更新知识库")
def update_kb(
    kb_id: int,
    data: KBUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb = _get_owned_kb(db, kb_id, current_user.id)
    if data.name is not None:
        kb.name = data.name
    if data.description is not None:
        kb.description = data.description
    db.commit()
    db.refresh(kb)
    doc_count = db.query(func.count(Document.id)) \
        .filter(Document.kb_id == kb_id, Document.status == "completed").scalar()
    return _to_response(kb, doc_count)


@router.delete("/{kb_id}", summary="删除知识库")
def delete_kb(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb = _get_owned_kb(db, kb_id, current_user.id)
    # 先删向量库
    document_service.delete_kb_vectors(kb_id)
    db.delete(kb)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{kb_id}/embed-code", summary="获取嵌入代码")
def get_embed_code(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb = _get_owned_kb(db, kb_id, current_user.id)
    return {
        "embed_code": kb.embed_code,
        "iframe_code": f'<iframe src="/embed/{kb.embed_code}" width="400" height="600" frameborder="0"></iframe>',
        "script_code": f'<script src="/embed/{kb.embed_code}.js" async></script>',
    }


def _get_owned_kb(db: Session, kb_id: int, user_id: int) -> KnowledgeBase:
    """获取知识库并校验归属"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if kb.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权操作该知识库")
    return kb


def _to_response(kb: KnowledgeBase, doc_count: int) -> KBResponse:
    return KBResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description or "",
        embed_code=kb.embed_code,
        document_count=doc_count,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
    )
