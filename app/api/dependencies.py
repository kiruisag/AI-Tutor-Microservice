# app/api/dependencies.py

from fastapi import Request, HTTPException
from app.core.config import settings
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.personalization import PersonalizationEngine


# ---------- Singleton Instances ----------
_llm_service = None
_rag_service = None
_personalization_engine = None


def get_tenant_id(request: Request) -> str:
    tenant = request.headers.get(settings.tenant_header)

    if not tenant:
        raise HTTPException(
            status_code=400,
            detail="Missing X-Tenant-ID header"
        )

    return tenant


# ---------- LLM Service (Singleton) ----------
def get_llm_service() -> LLMService:
    global _llm_service

    if _llm_service is None:
        _llm_service = LLMService()

    return _llm_service


# ---------- RAG Service (Singleton - IMPORTANT FIX) ----------
def get_rag_service() -> RAGService:
    global _rag_service

    if _rag_service is None:
        _rag_service = RAGService()

    return _rag_service


# ---------- Personalization Engine ----------
def get_personalization_engine() -> PersonalizationEngine:
    global _personalization_engine

    if _personalization_engine is None:
        _personalization_engine = PersonalizationEngine()

    return _personalization_engine