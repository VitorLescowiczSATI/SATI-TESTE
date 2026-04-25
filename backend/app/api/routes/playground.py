from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_session
from app.db.session import get_db
from app.models.session import UserSession
from app.schemas.conversation import (
    ConsoleConversationDetail,
    PlaygroundConversationCreate,
    PlaygroundMessageCreate,
)
from app.services.conversation_console_service import get_conversation_detail
from app.services.playground_service import create_playground_conversation, handle_playground_message

router = APIRouter()


@router.post("/conversations", response_model=ConsoleConversationDetail)
def create_conversation(
    payload: PlaygroundConversationCreate,
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> ConsoleConversationDetail:
    conversation = create_playground_conversation(
        db,
        tenant_id=current_session.tenant_id,
        lead_name=payload.lead_name,
    )
    detail = get_conversation_detail(db, current_session.tenant_id, conversation.id)
    if detail is None:
        raise HTTPException(status_code=500, detail="Nao foi possivel criar a conversa.")
    return detail


@router.post("/messages", response_model=ConsoleConversationDetail)
def send_message(
    payload: PlaygroundMessageCreate,
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> ConsoleConversationDetail:
    conversation = handle_playground_message(
        db,
        tenant=current_session.tenant,
        conversation_id=payload.conversation_id,
        message=payload.message,
    )
    detail = get_conversation_detail(db, current_session.tenant_id, conversation.id)
    if detail is None:
        raise HTTPException(status_code=500, detail="Nao foi possivel carregar a conversa.")
    return detail
