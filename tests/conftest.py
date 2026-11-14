import pytest
from fastapi.testclient import TestClient
from app.config import Settings, get_settings
from app.main import create_app
from app.routes.chat import get_ai_service
from app.routes.external_data import get_external_api_service


class FakeAIService:
    provider = "test"
    model = "fake-model"
    async def answer(self, question, history):
        return "This is a mocked CampusAssist answer."


class FakeWeatherService:
    async def current_weather(self, latitude, longitude):
        return {
            "provider": "Open-Meteo", "latitude": latitude, "longitude": longitude,
            "timezone": "Asia/Kolkata", "observed_at": "2026-11-14T09:00",
            "temperature_c": 28.0, "apparent_temperature_c": 31.0,
            "relative_humidity_percent": 70, "precipitation_mm": 0.0,
            "weather_code": 2, "wind_speed_kmh": 12.0, "units": {}
        }


@pytest.fixture
def settings():
    return Settings(
        CAMPUSASSIST_API_KEY="test-token",
        LLM_PROVIDER="gemini", GEMINI_API_KEY="test-key",
        RATE_LIMIT_REQUESTS=10, RATE_LIMIT_WINDOW_SECONDS=60,
        MAX_QUESTION_CHARS=1500,
    )


@pytest.fixture
def make_client():
    def _make(settings_obj=None, ai_service=None, weather_service=None):
        app = create_app()
        config = settings_obj or Settings(CAMPUSASSIST_API_KEY="test-token", RATE_LIMIT_REQUESTS=10)
        app.dependency_overrides[get_settings] = lambda: config
        app.dependency_overrides[get_ai_service] = lambda: ai_service or FakeAIService()
        app.dependency_overrides[get_external_api_service] = lambda: weather_service or FakeWeatherService()
        client = TestClient(app, raise_server_exceptions=False)
        return client, app
    return _make


@pytest.fixture
def client(make_client, settings):
    client, app = make_client(settings)
    with client:
        yield client
