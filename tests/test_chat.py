from app.utils.errors import LLMProviderError, LLMTimeoutError


class TimeoutAI:
    provider = "test"
    model = "timeout-model"
    async def answer(self, question, history): raise LLMTimeoutError()


class FailedAI:
    provider = "test"
    model = "failed-model"
    async def answer(self, question, history): raise LLMProviderError()


def test_valid_authenticated_chat_returns_answer(client):
    response = client.post("/chat", headers={"Authorization": "Bearer test-token"}, json={"question": "How do I contact IT?"})
    assert response.status_code == 200
    assert "mocked" in response.json()["answer"]
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_invalid_body_returns_422(client):
    response = client.post("/chat", headers={"Authorization": "Bearer test-token"}, json={"question": "   "})
    assert response.status_code == 422
    assert response.json()["error_type"] == "validation_error"


def test_oversized_question_returns_413(make_client, settings):
    client, _ = make_client(settings)
    with client:
        response = client.post("/chat", headers={"Authorization": "Bearer test-token"}, json={"question": "x" * 1501})
    assert response.status_code == 413
    assert response.json()["error_type"] == "input_too_large"


def test_llm_timeout_returns_504(make_client, settings):
    client, _ = make_client(settings, ai_service=TimeoutAI())
    with client:
        response = client.post("/chat", headers={"Authorization": "Bearer test-token"}, json={"question": "test"})
    assert response.status_code == 504
    assert response.json()["error_type"] == "llm_timeout"


def test_llm_provider_failure_returns_502(make_client, settings):
    client, _ = make_client(settings, ai_service=FailedAI())
    with client:
        response = client.post("/chat", headers={"Authorization": "Bearer test-token"}, json={"question": "test"})
    assert response.status_code == 502
    assert response.json()["error_type"] == "llm_provider_error"
