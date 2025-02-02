import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.config import settings
from app.config.logging_config_processor import init_logger
from app.routers import normalize_rout


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger = logging.getLogger(__name__)
        logger.info(f"Request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )


# noinspection PyTypeChecker
def create_app() -> FastAPI:
    # Initialize logger
    init_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting application")

    # Create required directories
    upload_dir = Path(settings.PATH_TO_UPLOAD_DIRECTORY)
    upload_dir.mkdir(parents=True, exist_ok=True)

    logs_dir = Path(settings.PATH_TO_LOGS)
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Initialize FastAPI app_api
    app_fastapi: FastAPI = FastAPI(
        title=settings.TITLE,
        version="1.0.0",
        description="API for normalizing bank statements"
    )

    app_fastapi.add_middleware(CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

    # Add request logging middleware
    app_fastapi.add_middleware(RequestLoggingMiddleware)

    # Include routers
    app_fastapi.include_router(normalize_rout.file_normalize_router)

    return app_fastapi


app_api = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", settings.PORT))
    uvicorn.run(
        "main:app_api",
        host="0.0.0.0",
        port=port,
        reload=settings.ENVIRONMENT == "development",
        reload_excludes=['*.log', '**/logs/*'],
        workers=int(os.getenv("WORKERS", 1))
    )
