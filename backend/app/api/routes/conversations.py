from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_session
from app.db.session import get_db
from app.models.session import UserSession
from app.schemas.conversation import ConsoleConversationDetail, ConsoleConversationSummary
from app.services.conversation_console_service import get_conversation_detail, list_active_conversations

router = APIRouter()


@router.get("/active", response_model=list[ConsoleConversationSummary])
def active_conversations(
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> list[ConsoleConversationSummary]:
    return list_active_conversations(db, current_session.tenant_id)


@router.get("/{conversation_id}", response_model=ConsoleConversationDetail)
def conversation_detail(
    conversation_id: str,
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> ConsoleConversationDetail:
    conversation = get_conversation_detail(db, current_session.tenant_id, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversa nao encontrada.")
    return conversation
