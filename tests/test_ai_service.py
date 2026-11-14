
import httpx
import pytest
from app.config import Settings
from app.services.ai_service import GeminiAIService, OpenAIService
from app.utils.errors import LLMTimeoutError


class FakeResponse:
    def __init__(self, data): self._data = data
    def raise_for_status(self): pass
    def json(self): return self._data


class FakeAsyncClient:
    def __init__(self, *args, **kwargs): pass
    response_data = {}
    captured = None
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): return False
    async def post(self, url, headers=None, json=None):
        FakeAsyncClient.captured = {"url": url, "headers": headers, "json": json}
        return FakeResponse(FakeAsyncClient.response_data)


def test_gemini_interactions_adapter_uses_store_false_and_output_cap(monkeypatch, tmp_path):
    import app.services.ai_service as module
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeAsyncClient)
    knowledge = tmp_path / "campus.json"
    knowledge.write_text('{"facts": []}', encoding="utf-8")
    settings = Settings(GEMINI_API_KEY="gemini-test", CAMPUS_KNOWLEDGE_PATH=str(knowledge), LLM_MAX_OUTPUT_TOKENS=77)
    FakeAsyncClient.response_data = {"steps": [{"type": "model_output", "content": [{"type": "text", "text": "Use the official portal."}]}]}
    service = GeminiAIService(settings)
    result = __import__("asyncio").run(service.answer("How do I get help?", []))
    assert result == "Use the official portal."
    assert FakeAsyncClient.captured["json"]["store"] is False
    assert FakeAsyncClient.captured["json"]["generation_config"]["max_output_tokens"] == 77
    assert FakeAsyncClient.captured["json"]["generation_config"]["thinking_level"] == "low"
    assert FakeAsyncClient.captured["headers"]["x-goog-api-key"] == "gemini-test"
    assert FakeAsyncClient.captured["headers"]["Api-Revision"] == "2026-05-20"


def test_openai_responses_adapter_extracts_text(monkeypatch, tmp_path):
    import app.services.ai_service as module
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeAsyncClient)
    knowledge = tmp_path / "campus.json"
    knowledge.write_text('{"facts": []}', encoding="utf-8")
    settings = Settings(OPENAI_API_KEY="openai-test", CAMPUS_KNOWLEDGE_PATH=str(knowledge))
    FakeAsyncClient.response_data = {"output": [{"type": "message", "content": [{"type": "output_text", "text": "Ask the student office."}]}]}
    service = OpenAIService(settings)
    result = __import__("asyncio").run(service.answer("Where should I ask?", []))
    assert result == "Ask the student office."
    assert FakeAsyncClient.captured["json"]["store"] is False
    assert FakeAsyncClient.captured["headers"]["Authorization"] == "Bearer openai-test"


def test_gemini_timeout_is_converted_to_application_timeout(monkeypatch, tmp_path):
    import asyncio
    import app.services.ai_service as module
    from app.utils.errors import LLMTimeoutError

    class TimeoutClient:
        def __init__(self, *args, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): return False
        async def post(self, *args, **kwargs):
            raise httpx.ReadTimeout("simulated timeout")

    monkeypatch.setattr(module.httpx, "AsyncClient", TimeoutClient)
    knowledge = tmp_path / "campus.json"
    knowledge.write_text('{"facts": []}', encoding="utf-8")
    settings = Settings(GEMINI_API_KEY="gemini-test", CAMPUS_KNOWLEDGE_PATH=str(knowledge))

    with pytest.raises(LLMTimeoutError):
        asyncio.run(GeminiAIService(settings).answer("Hello", []))
