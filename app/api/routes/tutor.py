from fastapi import APIRouter, Depends
from app.models.requests import ExplainRequest
from app.models.responses import ExplainResponse
import time
import logging
import hashlib
import json

from app.api.dependencies import get_tenant_id, get_llm_service, get_rag_service
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.quota_service import QuotaService
from app.utils.cache import get_cache, set_cache
from app.ml.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tutor", tags=["tutor"])

quota = QuotaService()


# -----------------------
# REQUEST MODEL
# -----------------------
    # ...existing code...


# -----------------------
# CACHE KEY BUILDER (ROBUST)
# -----------------------
def build_cache_key(tenant: str, req: ExplainRequest) -> str:
    raw = {
        "t": tenant,
        "q": req.question.strip().lower(),
        "l": req.student_level,
        "s": req.teaching_style
    }

    encoded = json.dumps(raw, sort_keys=True)
    return "tutor:" + hashlib.sha256(encoded.encode()).hexdigest()


# -----------------------
# MAIN ENDPOINT
# -----------------------
@router.post("/explain", response_model=ExplainResponse, description="Generate a personalized explanation for a student question.")
async def explain(
    req: ExplainRequest,
    tenant: str = Depends(get_tenant_id),
    llm: LLMService = Depends(get_llm_service),
    rag: RAGService = Depends(get_rag_service)
):
    start_time = time.time()
    cache_key = build_cache_key(tenant, req)

    # -----------------------
    # 1. CACHE (FAST PATH)
    # -----------------------
    try:
        cached = await get_cache(cache_key)
        if cached:
            return ExplainResponse(
                answer=cached,
                cached=True,
                latency_ms=int((time.time() - start_time) * 1000),
                sources=None
            )
    except Exception as e:
        logger.warning(f"Cache read failed: {e}")

    # -----------------------
    # 2. RAG RETRIEVAL
    # -----------------------
    try:
        context_chunks = await rag.search(tenant, req.question)
    except Exception as e:
        logger.error(f"RAG failed: {e}")
        context_chunks = []

    context = "\n".join(context_chunks[:5]) if context_chunks else "No course material available."

    # -----------------------
    # 3. PROMPT BUILDING
    # -----------------------
    messages = PromptBuilder.tutor_prompt(
        question=req.question,
        context=context,
        student_level=req.student_level,
        teaching_style=req.teaching_style
    )

    # -----------------------
    # 4. DYNAMIC TOKEN ESTIMATION
    # -----------------------
    complexity = len(req.question.split())

    max_tokens = (
        300 if complexity < 10 else
        500 if complexity < 25 else
        800
    )

    estimated_tokens = min(1200, complexity * 2 + max_tokens)

    # -----------------------
    # 5. ATOMIC QUOTA CHECK (SAFE)
    # -----------------------
    try:
        if not quota.reserve(tenant, estimated_tokens):
            return ExplainResponse(
                answer="Quota exceeded",
                cached=False,
                latency_ms=int((time.time() - start_time) * 1000),
                sources=None
            )
    except Exception as e:
        logger.error(f"Quota system failed: {e}")

    # -----------------------
    # 6. LLM CALL
    # -----------------------
    try:
        answer = await llm.generate_completion(
            messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
    except Exception as e:
        logger.error(f"LLM failed: {e}")
        quota.rollback(tenant, estimated_tokens)
        return ExplainResponse(
            answer="AI service temporarily unavailable",
            cached=False,
            latency_ms=int((time.time() - start_time) * 1000),
            sources=None
        )

    # -----------------------
    # 7. CACHE WRITE
    # -----------------------
    try:
        await set_cache(cache_key, answer, ttl=3600)
    except Exception as e:
        logger.warning(f"Cache write failed: {e}")

    # -----------------------
    # 8. FINAL QUOTA COMMIT
    # -----------------------
    try:
        quota.commit(tenant, estimated_tokens)
    except Exception as e:
        logger.warning(f"Quota commit failed: {e}")

    # -----------------------
    # 9. RESPONSE
    # -----------------------
    latency = int((time.time() - start_time) * 1000)

    return ExplainResponse(
        answer=answer,
        cached=False,
        latency_ms=latency,
        sources=context_chunks if context_chunks else None
    )