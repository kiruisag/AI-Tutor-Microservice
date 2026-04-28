# app/main.py
from fastapi import FastAPI, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import tutor, lecture, slides, curriculum
from app.core.security import verify_api_key
from app.core.config import settings
from app.core.middleware import exception_handler, ai_service_exception_handler
from app.core.exceptions import AIServiceError

app = FastAPI(
    title="Afrisol AI Microservice",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url=None
)

# Register exception handlers
app.add_exception_handler(Exception, exception_handler)
app.add_exception_handler(AIServiceError, ai_service_exception_handler)

# -----------------------
# CORS CONFIG (secure)
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if hasattr(settings, "cors_origins") else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# -----------------------
# ROUTER REGISTRATION
# -----------------------

# Core AI (protected)
app.include_router(
    tutor.router,
    prefix="/api/v1",
    dependencies=[Depends(verify_api_key)]
)

# Lecture streaming (often JWT-based later, so no global dependency here)
app.include_router(
    lecture.router,
    prefix="/api/v1/lecture"
)

# Slide AI (protected)
app.include_router(
    slides.router,
    prefix="/api/v1/slides",
    dependencies=[Depends(verify_api_key)]
)

# Curriculum generation (heavy + expensive)
app.include_router(
    curriculum.router,
    prefix="/api/v1/curriculum",
    dependencies=[Depends(verify_api_key)]
)

# -----------------------
# HEALTH CHECK
# -----------------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ai-microservice",
        "version": "1.0.0"
    }