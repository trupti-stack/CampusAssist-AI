import logging
from fastapi import APIRouter, Depends, Request
from app.config import Settings, get_settings
from app.dependencies import require_api_key, enforce_rate_limit
from app.schemas.chat import ChatRequest
from app.schemas.responses import ChatResponse
from app.services.ai_service import BaseAIService, get_ai_service_for_settings
from app.utils.errors import AppError, LLMProviderError, LLMTimeoutError
from app.utils.errors import ExternalAPIError, ExternalAPITimeoutError

logger = logging.getLogger("campusassist.chat")
router = APIRouter(tags=["Chat"])


def get_ai_service(settings: Settings = Depends(get_settings)) -> BaseAIService:
    return get_ai_service_for_settings(settings)


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)])
async def chat(payload: ChatRequest, request: Request, settings: Settings = Depends(get_settings), ai_service: BaseAIService = Depends(get_ai_service)):
    if len(payload.question) > settings.MAX_QUESTION_CHARS:
        raise AppError(413, "input_too_large", f"The question must be {settings.MAX_QUESTION_CHARS} characters or fewer.")
    if len(payload.history) > settings.MAX_HISTORY_MESSAGES:
        raise AppError(422, "validation_error", "Too many conversation history messages were supplied.")
    try:
        answer = await ai_service.answer(payload.question, payload.history)
    except LLMTimeoutError as exc:
        logger.warning("llm_timeout", extra={"request_id": request.state.request_id, "error_type": "llm_timeout"})
        raise AppError(504, "llm_timeout", "The AI service took too long to respond. Please try again.") from exc
    except LLMProviderError as exc:
        logger.warning("llm_provider_failure", extra={"request_id": request.state.request_id, "error_type": "llm_provider_failure"})
        raise AppError(502, "llm_provider_error", "The AI service is temporarily unavailable.") from exc
    return ChatResponse(
        answer=answer,
        request_id=request.state.request_id,
        provider=ai_service.provider,
        model=ai_service.model,
    )
