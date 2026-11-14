from app.utils.errors import ExternalAPIError, ExternalAPITimeoutError


class FailedWeather:
    async def current_weather(self, latitude, longitude): raise ExternalAPIError()


class TimeoutWeather:
    async def current_weather(self, latitude, longitude): raise ExternalAPITimeoutError()


def test_external_weather_endpoint_returns_selected_fields(client):
    response = client.get("/external-data?latitude=19.07&longitude=72.87", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    assert response.json()["temperature_c"] == 28.0
    assert response.json()["provider"] == "Open-Meteo"


def test_external_api_failure_returns_502(make_client, settings):
    client, _ = make_client(settings, weather_service=FailedWeather())
    with client:
        response = client.get("/external-data?latitude=19&longitude=72", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 502


def test_external_api_timeout_returns_504(make_client, settings):
    client, _ = make_client(settings, weather_service=TimeoutWeather())
    with client:
        response = client.get("/external-data?latitude=19&longitude=72", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 504
