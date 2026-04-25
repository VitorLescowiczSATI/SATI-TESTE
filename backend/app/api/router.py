from fastapi import APIRouter

from app.api.routes import admin, auth, conversations, health, playground, whatsapp_webhook

api_router = APIRouter()
api_router.include_router(health.router, tags=["infra"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(playground.router, prefix="/playground", tags=["playground"])
api_router.include_router(whatsapp_webhook.router, prefix="/webhooks/whatsapp", tags=["webhooks"])
