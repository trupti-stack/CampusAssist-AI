import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.errors import AppError

logger = logging.getLogger("campusassist.errors")


def _payload(request: Request, status_code: int, error_type: str, message: str) -> dict:
    return {
        "request_id": getattr(request.state, "request_id", "unknown"),
        "status_code": status_code,
        "error_type": error_type,
        "message": message,
    }


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_payload(request, exc.status_code, exc.error_type, exc.message),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        # Detailed Pydantic internals are intentionally not returned to clients.
        return JSONResponse(
            status_code=422,
            content=_payload(request, 422, "validation_error", "The request body or parameters are invalid."),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        messages = {
            404: "The requested resource was not found.",
            405: "The requested method is not allowed.",
        }
        message = messages.get(exc.status_code, "The request could not be completed.")
        return JSONResponse(
            status_code=exc.status_code,
            content=_payload(request, exc.status_code, "http_error", message),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception):
        logger.exception(
            "unhandled_application_error",
            extra={"request_id": getattr(request.state, "request_id", "unknown"), "error_type": type(exc).__name__},
        )
        return JSONResponse(
            status_code=500,
            content=_payload(request, 500, "internal_server_error", "An unexpected error occurred. Please try again."),
        )
