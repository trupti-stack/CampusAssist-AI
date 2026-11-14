import logging
import re
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("campusassist.requests")
_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        supplied_id = request.headers.get("X-Request-ID", "")
        request_id = supplied_id if _SAFE_REQUEST_ID.fullmatch(supplied_id) else str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        status_code = 500
        error_type = None
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            error_type = type(exc).__name__
            raise
        finally:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                    "error_type": error_type,
                },
            )


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_bytes: int):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_bytes:
                    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
                    return JSONResponse(
                        status_code=413,
                        content={
                            "request_id": request_id,
                            "status_code": 413,
                            "error_type": "request_too_large",
                            "message": "The request body is too large.",
                        },
                        headers={"X-Request-ID": request_id},
                    )
            except ValueError:
                pass
        return await call_next(request)
