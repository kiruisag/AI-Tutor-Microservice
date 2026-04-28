from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.exceptions import AIServiceError
import logging
import uuid

logger = logging.getLogger(__name__)

async def exception_handler(request: Request, exc: Exception):
    trace_id = str(uuid.uuid4())
    logger.error(f"Unhandled exception: {exc}", extra={"trace_id": trace_id, "path": str(request.url)})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": str(exc),
            "trace_id": trace_id
        },
    )

async def ai_service_exception_handler(request: Request, exc: AIServiceError):
    trace_id = str(uuid.uuid4())
    logger.error(f"AIServiceError: {exc}", extra={"trace_id": trace_id, "path": str(request.url)})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "trace_id": trace_id
        },
    )
