# app/api/routes/slides.py
from fastapi import APIRouter, Depends
from app.models.requests import SlidesRequest
from app.models.responses import SlidesResponse
import json
from app.api.dependencies import get_llm_service, get_rag_service, get_tenant_id
from app.ml.prompt_builder import PromptBuilder

router = APIRouter(prefix="/slides", tags=["slides"])

    # ...existing code...

@router.post("/explain", response_model=SlidesResponse, description="Generate an explanation for a slide.")
async def explain_slide(
    req: SlidesRequest,
    tenant: str = Depends(get_tenant_id),
    llm = Depends(get_llm_service),
    rag = Depends(get_rag_service)
):
    # RAG context from slide keywords (here we just search using lecture_id for now)
    context_chunks = await rag.search(tenant, req.lecture_id[:200])
    context = "\n".join(context_chunks)
    messages = PromptBuilder.slide_explanation_prompt(
        slide_text=req.lecture_id,  # Placeholder: should fetch actual slide text by ID
        context=context,
        student_level="intermediate",
        teaching_style=req.format or "narrative"
    )
    response = await llm.generate_completion(messages, max_tokens=400)
    # Parse JSON safely
    try:
        explanation = json.loads(response)
        slides_url = explanation.get("slides_url", "")
        format_ = explanation.get("format", req.format or "pdf")
        generated_at = explanation.get("generated_at", "")
    except Exception:
        slides_url = ""
        format_ = req.format or "pdf"
        generated_at = ""
    return SlidesResponse(
        slides_url=slides_url,
        format=format_,
        generated_at=generated_at
    )