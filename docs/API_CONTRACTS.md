# CampusAssist AI — API contracts

All API responses are JSON. Error responses use the shape:

```json
{
  "request_id": "<correlation-id>",
  "status_code": 401,
  "error_type": "authentication_failed",
  "message": "A valid Bearer access token is required."
}
```

The same request ID is returned in the `X-Request-ID` response header. Clients may send a safe `X-Request-ID` value; otherwise the backend generates a UUID.

## `GET /health`

- Purpose: lightweight liveness check.
- Authentication: none.
- Query/body: none.
- `200`: `{"status":"ok","service":"campusassist-ai","environment":"development"}`.
- Other status: normally only infrastructure-level failures.

## `POST /chat`

- Purpose: ask the configured LLM about campus-related questions.
- Authentication: `Authorization: Bearer <CAMPUSASSIST_API_KEY>`.
- Rate limit: 10 requests per client IP per rolling 60 seconds by default.
- Request:

```json
{
  "question": "How can I contact the IT helpdesk?",
  "history": [
    {"role": "user", "content": "I need help with my account."},
    {"role": "assistant", "content": "Use the official IT support channel."}
  ]
}
```

`question` is required, trimmed, and limited by `MAX_QUESTION_CHARS` (default 1,500). `history` is optional, contains up to 8 recent `user`/`assistant` messages by default, and each message is limited to 2,000 characters. Empty input is rejected.

- `200` response:

```json
{
  "answer": "Please check the official campus portal for the current helpdesk contact.",
  "request_id": "<id>",
  "provider": "gemini",
  "model": "gemini-3.8-flash"
}
```

- Statuses: `401` missing/invalid token; `413` question/body too large; `422` invalid body; `429` rate limit exceeded; `502` LLM provider failure; `504` LLM timeout; `500` unexpected error; `503` if the access-token configuration is missing.

## `GET /external-data`

- Purpose: retrieve selected current-weather fields from Open-Meteo.
- Authentication: Bearer token.
- Rate limit: same per-client IP policy as `/chat`.
- Query parameters: `latitude` (required, -90..90), `longitude` (required, -180..180).
- Example: `/external-data?latitude=19.0760&longitude=72.8777`.
- `200` response includes provider, coordinates, timezone, observation time, temperature, apparent temperature, humidity, precipitation, weather code, wind speed, units, and request ID.
- Statuses: `401`, `422`, `429`, `502` third-party failure, `504` third-party timeout, `500` unexpected error.

## Security and response notes

The API access token is separate from the Gemini/OpenAI credential. The browser user must enter the demo token at runtime; the token is held in page memory only and is not committed in frontend code or persisted in local storage. For public production use, replace the shared demo token with per-user authentication (OAuth/OIDC or signed JWTs) behind HTTPS and a trusted reverse proxy/API gateway.
