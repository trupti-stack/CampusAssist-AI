def test_health_is_public_and_reports_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers.get("X-Request-ID")
