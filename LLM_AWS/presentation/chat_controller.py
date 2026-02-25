"""
Presentation Layer - FastAPI Chat Controller
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from LLM_AWS.jwt_auth import get_current_user
from LLM_AWS.application.chat_usecase import ChatUseCase
from LLM_AWS.domain.entities import ChatRequest


# Request/Response Models
class ChatRequestDTO(BaseModel):
    session_id: str
    message: str


class ChatResponseDTO(BaseModel):
    message: str
    sources: List[str]
    used_short_memory: bool
    used_long_memory: bool
    used_vector_db: bool


# Router
router = APIRouter(prefix="/api/chat", tags=["chat"])


def create_chat_router(chat_usecase: ChatUseCase) -> APIRouter:
    """Factory function để tạo router với dependencies"""
    
    @router.post("/", response_model=ChatResponseDTO)
    async def chat(
        request: ChatRequestDTO,
        user_id: str = Depends(get_current_user)
    ):
        """
        Chat endpoint với JWT authentication
        
        - Nhận JWT token từ header X-User-Authorization
        - Extract user_id từ JWT
        - Xử lý chat với LangGraph agent
        - Trả về response với sources và memory flags
        """
        try:
            # Create domain request
            chat_request = ChatRequest(
                user_id=user_id,
                session_id=request.session_id,
                message=request.message
            )
            
            # Execute use case
            response = chat_usecase.execute(chat_request)
            
            # Return DTO
            return ChatResponseDTO(
                message=response.message,
                sources=response.sources,
                used_short_memory=response.used_short_memory,
                used_long_memory=response.used_long_memory,
                used_vector_db=response.used_vector_db
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
