from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.dependencies import InMemorySlidingWindowLimiter
from app.middleware.request_context import RequestContextMiddleware, RequestSizeLimitMiddleware
from app.routes import health, chat, external_data
from app.utils.error_handlers import register_error_handlers
from app.utils.logging_config import configure_logging

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.LOG_LEVEL)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield

    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="A secure student campus-assistance API with configurable LLM and public weather data.",
        lifespan=lifespan,
    )
    app.state.rate_limiter = InMemorySlidingWindowLimiter()
    app.add_middleware(RequestSizeLimitMiddleware, max_bytes=settings.MAX_REQUEST_BODY_BYTES)
    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)

    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(external_data.router)

    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def home():
        return FileResponse(FRONTEND_DIR / "index.html")

    return app


app = create_app()
