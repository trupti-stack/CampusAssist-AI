# Development phases and practical runbook

| Phase | Project result | Key verification |
|---|---|---|
| 1. Requirements and architecture | FastAPI + browser + LLM + Open-Meteo design | Review `README.md` architecture diagram |
| 2. Contracts and structure | Routers, schemas, configuration and folders | `GET /docs` |
| 3. Backend | Health, chat and external-data routes | Exercise endpoints locally |
| 4. Security | Bearer auth, rate limit, size and error controls | `pytest tests/test_auth.py tests/test_rate_limit.py` |
| 5. LLM | Gemini/OpenAI HTTP adapters | Add a valid provider key and ask one question |
| 6. External API | Server-side Open-Meteo integration | Request current weather using coordinates |
| 7. Frontend | Responsive chat, access token, history, weather panel | Open `/` in browser |
| 8. Observability | Request ID + JSON logs | Inspect server terminal |
| 9. Tests and performance | Mocked test suite + 20-request script | `pytest -q`; performance script |
| 10. Docker | Runtime-configured non-root container | `docker compose build` and `up -d` |
| 11. Git and docs | Commit plan, branch commands and README | `git log --graph --oneline --all` |
| 12. Compliance audit | Evidence checklist | Complete README checklist |

## Suggested command order

```powershell
# 1. Environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env

# 2. Add your credentials to .env, then run
uvicorn app.main:app --reload --port 8000

# 3. In another terminal
pytest -q
python scripts/performance_test.py --target health --count 20

# 4. Container verification (requires Docker Desktop)
docker compose build
docker compose up -d
docker compose ps
Invoke-RestMethod http://localhost:8000/health

docker compose down
```

## Troubleshooting

- **401:** check that the token entered in the page exactly matches `CAMPUSASSIST_API_KEY`; restart the server after changing `.env`.
- **503 authentication not configured:** `.env` is missing or the API access key is blank.
- **502 LLM error:** check provider choice, key, model access, billing/quota and network connectivity. Never paste the key into logs/screenshots.
- **504 LLM timeout:** confirm Gemini API access/billing is enabled for the Google AI Studio project, check network connectivity, and inspect the safe `llm_upstream_timeout` log. The default read timeout is 60 seconds.
- **429:** wait for `Retry-After` seconds or lower the test request rate; the default is ten requests per 60 seconds per IP.
- **No college-specific answer:** populate `data/campus_knowledge.json` with verified facts and restart the app.
- **Docker cannot bind port:** stop the local Uvicorn process or change the host-side compose port (for example `8001:8000`).
