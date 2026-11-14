import logging
import httpx
from app.config import Settings
from app.utils.errors import ExternalAPIError, ExternalAPITimeoutError

logger = logging.getLogger("campusassist.external_api")


class ExternalAPIService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def current_weather(self, latitude: float, longitude: float) -> dict:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "timezone": "auto",
        }
        try:
            async with httpx.AsyncClient(timeout=self.settings.EXTERNAL_API_TIMEOUT_SECONDS) as client:
                response = await client.get(self.settings.OPEN_METEO_BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise ExternalAPITimeoutError("Open-Meteo request timed out") from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise ExternalAPIError("Open-Meteo request failed") from exc

        current = data.get("current")
        if not isinstance(current, dict):
            raise ExternalAPIError("Open-Meteo response did not contain current conditions")
        logger.info("external_api_request_completed", extra={"provider": "open-meteo", "model": "forecast-api"})
        return {
            "provider": "Open-Meteo",
            "latitude": data.get("latitude", latitude),
            "longitude": data.get("longitude", longitude),
            "timezone": data.get("timezone", "unknown"),
            "observed_at": current.get("time"),
            "temperature_c": current.get("temperature_2m"),
            "apparent_temperature_c": current.get("apparent_temperature"),
            "relative_humidity_percent": current.get("relative_humidity_2m"),
            "precipitation_mm": current.get("precipitation"),
            "weather_code": current.get("weather_code"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "units": data.get("current_units", {}),
        }
