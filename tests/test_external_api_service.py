
import asyncio
from app.config import Settings
from app.services.external_api_service import ExternalAPIService


class FakeResponse:
    def raise_for_status(self): pass
    def json(self):
        return {
            "latitude": 19.0, "longitude": 72.0, "timezone": "Asia/Kolkata",
            "current": {"time": "2026-11-14T10:00", "temperature_2m": 29.2,
                        "apparent_temperature": 31.0, "relative_humidity_2m": 68,
                        "precipitation": 0.0, "weather_code": 1, "wind_speed_10m": 8.4},
            "current_units": {"temperature_2m": "°C"}
        }


class FakeAsyncClient:
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): return False
    async def get(self, url, params=None):
        assert params["latitude"] == 19.0
        assert "temperature_2m" in params["current"]
        return FakeResponse()


def test_external_api_service_parses_only_selected_fields(monkeypatch):
    import app.services.external_api_service as module
    monkeypatch.setattr(module.httpx, "AsyncClient", lambda **kwargs: FakeAsyncClient())
    service = ExternalAPIService(Settings())
    data = asyncio.run(service.current_weather(19.0, 72.0))
    assert data["temperature_c"] == 29.2
    assert data["provider"] == "Open-Meteo"
    assert "current" not in data
