from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str


class ChatResponse(BaseModel):
    answer: str
    request_id: str
    provider: str
    model: str


class ErrorResponse(BaseModel):
    request_id: str
    status_code: int
    error_type: str
    message: str


class ExternalWeatherResponse(BaseModel):
    provider: str
    latitude: float
    longitude: float
    timezone: str
    observed_at: str | None = None
    temperature_c: float | None = None
    apparent_temperature_c: float | None = None
    relative_humidity_percent: float | None = None
    precipitation_mm: float | None = None
    weather_code: int | None = None
    wind_speed_kmh: float | None = None
    units: dict = Field(default_factory=dict)
    request_id: str
