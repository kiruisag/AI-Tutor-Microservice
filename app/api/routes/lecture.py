# app/api/routes/lecture.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.api.dependencies import get_llm_service
from app.services.llm_service import LLMService
from app.ml.prompt_builder import PromptBuilder
from app.models.requests import LectureRequest

router = APIRouter(prefix="/lecture", tags=["lecture"])

@router.websocket("/stream")
async def lecture_stream(websocket: WebSocket):
    await websocket.accept()
    llm: LLMService = get_llm_service()  # manual dependency for WebSocket
    try:
        # Receive initial parameters as JSON from client
        data = await websocket.receive_json()
        # Validate input using LectureRequest
        try:
            req = LectureRequest(**data)
        except Exception as e:
            await websocket.send_text(f"Input validation error: {str(e)}")
            await websocket.close()
            return
        # Build lecture prompt
        messages = PromptBuilder.lecture_prompt(req.topic, req.level)
        # Stream tokens
        async for token in llm.generate_stream(messages, max_tokens=1500):
            await websocket.send_text(token)
        await websocket.send_text("[END]")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
        await websocket.close()