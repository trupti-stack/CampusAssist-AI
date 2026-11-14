# 20-request performance run — measured result

**Run date:** 14 November 2026 (Asia/Kolkata; the container log timestamp was 13 November 2026 UTC)  
**Target:** `GET /health`  
**Method:** 20 sequential HTTP requests through the locally running Uvicorn server, using `scripts/performance_test.py --target health --count 20`.  
**Scope:** This is a measured API liveness/HTTP baseline only. It does not include an LLM call or Open-Meteo request, and must not be presented as end-to-end chat latency.

| Metric | Measured result |
|---|---:|
| Total requests | 20 |
| Successful requests | 20 |
| Failed requests | 0 |
| Success rate | 100.00% |
| Error rate | 0.00% |
| Average latency | 9.56 ms |
| Maximum latency | 59.46 ms |
| Rate-limit events | 0 |

The first request included local server/warm-up overhead. All 20 requests returned HTTP 200. This small single-host sequential sample is not a production load test and should not be generalized to other machines or deployments. For the protected `/chat` endpoint, use the script's `--target chat` option only after configuring an API key; it makes real LLM calls and the default 10-per-minute policy can trigger HTTP 429.

**Additional verification in this environment:** `GET /` returned HTTP 200; `GET /health` returned `status=ok`; an unauthenticated `POST /chat` returned HTTP 401 with a request ID. Automated mocked tests passed (see the project README). Docker was not installed here. A live Open-Meteo request returned HTTP 502 in this environment, so live third-party connectivity remains to be verified on the user's machine; the endpoint's success/timeout/failure paths are covered with mocked tests.
