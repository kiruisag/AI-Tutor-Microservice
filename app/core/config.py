# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Literal, Optional


class Settings(BaseSettings):

    # -----------------------
    # CORE SECURITY
    # -----------------------
    api_key: str = Field(..., alias="AI_SERVICE_API_KEY")
    jwt_secret: str = Field(..., alias="JWT_SECRET")

    # -----------------------
    # LLM PROVIDERS
    # -----------------------
    llm_provider: Literal["openai", "gemini", "vertex", "mock"] = Field(
        "openai",
        alias="LLM_PROVIDER"
    )

    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4o-mini"

    gemini_api_key: Optional[str] = Field(None, alias="GEMINI_API_KEY")

    vertex_project_id: Optional[str] = Field(None, alias="VERTEX_PROJECT_ID")
    vertex_location: str = Field("us-central1", alias="VERTEX_LOCATION")

    # -----------------------
    # RAG / VECTOR DB
    # -----------------------
    vector_db_type: Literal["in_memory", "pinecone", "qdrant", "pgvector"] = "in_memory"

    pinecone_api_key: Optional[str] = Field(None, alias="PINECONE_API_KEY")
    pinecone_index: str = "lms-vectors"

    # -----------------------
    # INFRASTRUCTURE
    # -----------------------
    redis_url: str = Field("redis://localhost:6379", alias="REDIS_URL")

    # -----------------------
    # TTS
    # -----------------------
    tts_provider: Literal["google", "elevenlabs", "azure"] = "google"
    google_tts_credentials: Optional[str] = None

    # -----------------------
    # MULTI-TENANT CONTROL
    # -----------------------
    tenant_header: str = "X-Tenant-ID"
    rate_limit_per_minute: int = 100

    # -----------------------
    # QDRANT (VECTOR DB)
    # -----------------------
    qdrant_url: str = Field("http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(None, alias="QDRANT_API_KEY")
    qdrant_collection: str = Field("lms_vectors", alias="QDRANT_COLLECTION")

    # -----------------------
    # ENV CONTROL
    # -----------------------
    debug: bool = False
    env: Literal["dev", "staging", "prod"] = "dev"

    class Config:
        env_file = ".env"
        extra = "ignore"

    # -----------------------
    # VALIDATION LAYER (CRITICAL)
    # -----------------------
    @field_validator("openai_api_key")
    @classmethod
    def validate_openai(cls, v, values):
        if values.data.get("llm_provider") == "openai" and not v:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        return v

    @field_validator("gemini_api_key")
    @classmethod
    def validate_gemini(cls, v, values):
        if values.data.get("llm_provider") == "gemini" and not v:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        return v

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v):
        if not v or len(v) < 10:
            raise ValueError("AI_SERVICE_API_KEY is missing or too weak")
        return v


settings = Settings()