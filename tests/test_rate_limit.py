from app.config import Settings


def test_rate_limit_returns_429_after_configured_number(make_client):
    config = Settings(CAMPUSASSIST_API_KEY="test-token", RATE_LIMIT_REQUESTS=2, RATE_LIMIT_WINDOW_SECONDS=60)
    client, _ = make_client(config)
    with client:
        headers = {"Authorization": "Bearer test-token"}
        first = client.post("/chat", headers=headers, json={"question": "first"})
        second = client.post("/chat", headers=headers, json={"question": "second"})
        third = client.post("/chat", headers=headers, json={"question": "third"})
    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert third.headers.get("Retry-After")
