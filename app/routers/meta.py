import time
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
    }