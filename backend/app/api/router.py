from fastapi import APIRouter

from app.api.routes import auth, conversations, health, whatsapp_webhook

api_router = APIRouter()
api_router.include_router(health.router, tags=["infra"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(whatsapp_webhook.router, prefix="/webhooks/whatsapp", tags=["webhooks"])
