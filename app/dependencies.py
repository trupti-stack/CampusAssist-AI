import hmac
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings
from app.utils.errors import AppError

bearer_scheme = HTTPBearer(auto_error=False)


async def require_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> None:
    configured_key = settings.CAMPUSASSIST_API_KEY.strip()
    if not configured_key:
        raise AppError(503, "authentication_not_configured", "The service is not configured for authenticated access.")
    supplied = credentials.credentials if credentials and credentials.scheme.lower() == "bearer" else ""
    if not supplied or not hmac.compare_digest(supplied, configured_key):
        raise AppError(401, "authentication_failed", "A valid Bearer access token is required.", headers={"WWW-Authenticate": "Bearer"})


class InMemorySlidingWindowLimiter:
    """Per-process sliding-window limiter. Use Redis/a gateway for multi-instance deployments."""

    def __init__(self):
        self._events = defaultdict(deque)
        self._lock = Lock()

    def check(self, client_id: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            events = self._events[client_id]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                retry_after = max(1, int(window_seconds - (now - events[0])))
                return False, retry_after
            events.append(now)
            return True, 0


async def enforce_rate_limit(request: Request, settings: Settings = Depends(get_settings)) -> None:
    client_ip = request.client.host if request.client else "unknown"
    allowed, retry_after = request.app.state.rate_limiter.check(
        client_ip, settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW_SECONDS
    )
    if not allowed:
        raise AppError(
            429,
            "rate_limit_exceeded",
            f"Request limit reached. Please retry in about {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )
