from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse, SimplifyRequest, SimplifyResponse
from app.services.ai_service import answer_question, simplify_text

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    return answer_question(question=payload.question, top_k=payload.top_k)


@router.post("/simplify", response_model=SimplifyResponse)
def simplify(payload: SimplifyRequest) -> SimplifyResponse:
    return simplify_text(payload.text)

