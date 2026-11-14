from fastapi import APIRouter, Depends
from app.config import Settings, get_settings
from app.schemas.responses import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)):
    return HealthResponse(status="ok", service="campusassist-ai", environment=settings.APP_ENV)
