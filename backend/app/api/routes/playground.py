from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_session
from app.db.session import get_db
from app.models.session import UserSession
from app.schemas.conversation import (
    ConsoleConversationDetail,
    PlaygroundConversationCreate,
    PlaygroundMessageCreate,
)
from app.services.audio_transcription_service import transcribe as transcribe_audio
from app.services.conversation_console_service import get_conversation_detail
from app.services.playground_service import (
    create_playground_conversation,
    handle_playground_audio,
    handle_playground_message,
)

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


@router.post("/audio", response_model=ConsoleConversationDetail)
async def send_audio(
    conversation_id: str = Form(...),
    audio: UploadFile = File(...),
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> ConsoleConversationDetail:
    """Aceita um arquivo de audio (multipart), transcreve via Whisper e
    processa como inbound do lead, igual o intake do WhatsApp faria."""
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio vazio.")

    filename = audio.filename or "audio.ogg"
    transcript = transcribe_audio(audio_bytes, filename=filename)
    if not transcript:
        raise HTTPException(status_code=422, detail="Nao foi possivel transcrever este audio.")

    conversation = handle_playground_audio(
        db,
        tenant=current_session.tenant,
        conversation_id=conversation_id,
        transcript=transcript,
        audio_filename=filename,
        audio_size_bytes=len(audio_bytes),
        mime_type=audio.content_type,
    )
    detail = get_conversation_detail(db, current_session.tenant_id, conversation.id)
    if detail is None:
        raise HTTPException(status_code=500, detail="Nao foi possivel carregar a conversa.")
    return detail
