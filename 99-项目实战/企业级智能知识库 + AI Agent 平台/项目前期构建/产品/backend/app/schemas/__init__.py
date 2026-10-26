"""所有 Schema 汇总"""
from .user import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    PasswordUpdate, ModelUpdate,
)
from .knowledge_base import (
    KBCreate, KBUpdate, KBResponse, KBDetail,
    KbMemberInvite, KbMemberResponse, KbMemberList,
)
from .document import DocumentResponse, DocumentListResponse
from .chat import (
    ChatRequest, Source, MessageResponse,
    ConversationCreate, ConversationUpdate,
    ConversationResponse, ConversationDetail,
    FeedbackCreate, GlobalChatRequest,
)
from .wiki import (
    WikiPageResponse, WikiPageListItem, WikiGraphResponse,
    WikiGraphNode, WikiGraphEdge, WikiRecompileResponse,
    WikiPageEditRequest, WikiVersionResponse, WikiRollbackResponse,
)
from .structured import StructuredRequest, StructuredResponse, AnswerTemplate

__all__ = [
    "UserCreate", "UserLogin", "UserResponse", "TokenResponse",
    "PasswordUpdate", "ModelUpdate",
    "KBCreate", "KBUpdate", "KBResponse", "KBDetail",
    "KbMemberInvite", "KbMemberResponse", "KbMemberList",
    "DocumentResponse", "DocumentListResponse",
    "ChatRequest", "Source", "MessageResponse",
    "ConversationCreate", "ConversationUpdate",
    "ConversationResponse", "ConversationDetail",
    "FeedbackCreate", "GlobalChatRequest",
    "WikiPageResponse", "WikiPageListItem", "WikiGraphResponse",
    "WikiGraphNode", "WikiGraphEdge", "WikiRecompileResponse",
    "WikiPageEditRequest", "WikiVersionResponse", "WikiRollbackResponse",
    "StructuredRequest", "StructuredResponse", "AnswerTemplate",
]
