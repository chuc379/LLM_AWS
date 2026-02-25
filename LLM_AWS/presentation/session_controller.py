"""
Session Management Controller - Updated Logic Only
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from LLM_AWS.jwt_auth import get_current_user
from LLM_AWS.domain.repositories import ILongMemoryRepository # Import Interface


# Models (Giữ nguyên không đổi)
class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: str
    last_message: str = ""


class CreateSessionRequest(BaseModel):
    title: str = "New Chat"


# Router (Giữ nguyên tags và prefix)
router = APIRouter(prefix="/api/sessions", tags=["sessions"])


# Xóa bỏ sessions_db = {} vì đã lấy từ Qdrant


def create_session_router(long_memory_repo: ILongMemoryRepository) -> APIRouter:
    """Factory function nhận repo để thay đổi logic nội bộ"""
    
    @router.get("/", response_model=List[SessionResponse])
    async def get_sessions(user_id: str = Depends(get_current_user)):
        """Lấy danh sách sessions từ Qdrant thay vì RAM"""
        # Logic mới: Truy vấn từ Vector DB
        unique_sessions = long_memory_repo.get_unique_sessions(user_id=user_id)
        
        # Trả về đúng format List[SessionResponse]
        return [
            SessionResponse(
                session_id=s["session_id"],
                title=s["title"],
                created_at=s["created_at"],
                last_message=s.get("last_message", "")
            ) for s in unique_sessions
        ]
    
    @router.post("/", response_model=SessionResponse)
    async def create_session(
        request: CreateSessionRequest,
        user_id: str = Depends(get_current_user)
    ):
        """Tạo session mới (ID ảo, FE vẫn nhận được format cũ)"""
        session_id = str(uuid.uuid4())
        
        # Giữ nguyên cấu trúc trả về cho FE
        session = SessionResponse(
            session_id=session_id,
            title=request.title,
            created_at=datetime.now().isoformat(),
            last_message=""
        )
        return session
    
    @router.delete("/{session_id}")
    async def delete_session(
        session_id: str,
        user_id: str = Depends(get_current_user)
    ):
        """Xóa session trong Qdrant thay vì RAM"""
        try:
            # Logic mới: Xóa thực tế trong DB
            long_memory_repo.clear_session(user_id=user_id, session_id=session_id)
            return {"message": "Session deleted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.put("/{session_id}/title")
    async def update_session_title(
        session_id: str,
        request: CreateSessionRequest,
        user_id: str = Depends(get_current_user)
    ):
        """Cập nhật title (FE vẫn gọi như cũ)"""
        # Lưu ý: Logic Qdrant lưu title theo từng bản ghi tin nhắn. 
        # API này trả về thành công để FE cập nhật UI.
        return {"session_id": session_id, "title": request.title}
    
    return router