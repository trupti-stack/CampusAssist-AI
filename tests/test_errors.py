class CrashingAI:
    provider = "test"
    model = "crash-model"
    async def answer(self, question, history): raise RuntimeError("internal test detail must not leak")


def test_unexpected_exception_returns_safe_500(make_client, settings):
    client, _ = make_client(settings, ai_service=CrashingAI())
    with client:
        response = client.post("/chat", headers={"Authorization": "Bearer test-token"}, json={"question": "test"})
    assert response.status_code == 500
    assert response.json()["message"] == "An unexpected error occurred. Please try again."
    assert "internal test detail" not in response.text
