"""
Presentation Layer - Chat History Controller
Lấy lịch sử các đoạn chat từ Qdrant (theo user_id + session_id)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from LLM_AWS.jwt_auth import get_current_user
from LLM_AWS.domain.repositories import ILongMemoryRepository


class ChatMessageDTO(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageDTO]


router = APIRouter(prefix="/api/chat-history", tags=["chat-history"])


def create_chat_history_router(long_memory_repo: ILongMemoryRepository) -> APIRouter:
    """Factory function để tạo router lấy lịch sử chat từ Qdrant"""

    @router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
    async def get_session_history(
        session_id: str,
        user_id: str = Depends(get_current_user)
    ):
        """
        Lấy lịch sử chat cho 1 session cụ thể từ Qdrant Cloud.

        - Dựa trên user_id lấy từ JWT
        - Lọc theo session_id
        - Trả về danh sách các message (user + assistant) theo thứ tự thời gian
        """
        try:
            turns = long_memory_repo.get_session_chat_turns(
                user_id=user_id,
                session_id=session_id,
                limit=100
            )

            messages: List[ChatMessageDTO] = []
            for turn in turns:
                ts = datetime.fromtimestamp(turn.get("timestamp", 0))
                user_msg = turn.get("user_msg", "")
                ai_msg = turn.get("ai_msg", "")

                if user_msg:
                    messages.append(ChatMessageDTO(
                        role="user",
                        content=user_msg,
                        timestamp=ts
                    ))
                if ai_msg:
                    messages.append(ChatMessageDTO(
                        role="assistant",
                        content=ai_msg,
                        timestamp=ts
                    ))

            return ChatHistoryResponse(
                session_id=session_id,
                messages=messages
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router

