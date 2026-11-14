def test_missing_authentication_returns_401(client):
    response = client.post("/chat", json={"question": "Where is the library?"})
    assert response.status_code == 401
    assert response.json()["error_type"] == "authentication_failed"


def test_invalid_authentication_returns_401(client):
    response = client.post("/chat", headers={"Authorization": "Bearer wrong"}, json={"question": "Where is the library?"})
    assert response.status_code == 401


def test_unconfigured_server_key_returns_503(make_client):
    from app.config import Settings
    config = Settings(CAMPUSASSIST_API_KEY="")
    client, _ = make_client(config)
    with client:
        response = client.post("/chat", headers={"Authorization": "Bearer test-token"}, json={"question": "test"})
    assert response.status_code == 503
    assert response.json()["error_type"] == "authentication_not_configured"
