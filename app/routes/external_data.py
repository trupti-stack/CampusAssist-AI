from fastapi import APIRouter, Depends, Query, Request
from app.config import Settings, get_settings
from app.dependencies import require_api_key, enforce_rate_limit
from app.schemas.responses import ExternalWeatherResponse
from app.services.external_api_service import ExternalAPIService
from app.utils.errors import AppError, ExternalAPIError, ExternalAPITimeoutError

router = APIRouter(tags=["External Data"])


def get_external_api_service(settings: Settings = Depends(get_settings)) -> ExternalAPIService:
    return ExternalAPIService(settings)


@router.get("/external-data", response_model=ExternalWeatherResponse, dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)])
async def external_data(
    request: Request,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    service: ExternalAPIService = Depends(get_external_api_service),
):
    try:
        data = await service.current_weather(latitude, longitude)
    except ExternalAPITimeoutError as exc:
        raise AppError(504, "external_api_timeout", "The weather service did not respond in time.") from exc
    except ExternalAPIError as exc:
        raise AppError(502, "external_api_error", "The weather service is temporarily unavailable.") from exc
    data["request_id"] = request.state.request_id
    return data
