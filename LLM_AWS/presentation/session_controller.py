"""
Session Management Controller - Updated with Deep Logging
"""
import logging
import traceback
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from LLM_AWS.jwt_auth import get_current_user
from LLM_AWS.domain.repositories import ILongMemoryRepository

# Khởi tạo logger đồng bộ với hệ thống
logger = logging.getLogger("LLM_AWS.session")

class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: str
    last_message: str = ""

class CreateSessionRequest(BaseModel):
    title: str = "New Chat"

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

def create_session_router(long_memory_repo: ILongMemoryRepository) -> APIRouter:
    
    # SỬA: "/" -> "" để khớp chuẩn /api/sessions
    @router.get("", response_model=List[SessionResponse])
    async def get_sessions(user_id: str = Depends(get_current_user)):
        logger.info(f"🔍 [GET SESSIONS] Đang quét danh sách hội thoại cho User: {user_id}")
        try:
            unique_sessions = long_memory_repo.get_unique_sessions(user_id=user_id)
            logger.info(f"📊 [GET SESSIONS] Thành công. Tìm thấy {len(unique_sessions)} hội thoại.")
            return [
                SessionResponse(
                    session_id=s["session_id"],
                    title=s["title"],
                    created_at=s["created_at"],
                    last_message=s.get("last_message", "")
                ) for s in unique_sessions
            ]
        except Exception as e:
            logger.error(f"❌ [GET SESSIONS] Lỗi truy vấn Qdrant: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="Không thể lấy danh sách session")
    
    # SỬA: "/" -> ""
    @router.post("", response_model=SessionResponse)
    async def create_session(
        request: CreateSessionRequest,
        user_id: str = Depends(get_current_user)
    ):
        session_id = str(uuid.uuid4())
        logger.info(f"🆕 [CREATE SESSION] User {user_id} khởi tạo session mới: {session_id}")
        return SessionResponse(
            session_id=session_id,
            title=request.title,
            created_at=datetime.now().isoformat(),
            last_message=""
        )
    
    # Giữ nguyên các route có tham số vì chúng đã có cấu trúc path rõ ràng
    @router.delete("/{session_id}")
    async def delete_session(session_id: str, user_id: str = Depends(get_current_user)):
        logger.warning(f"🗑️ [DELETE SESSION] Đang xóa session {session_id}")
        try:
            long_memory_repo.clear_session(user_id=user_id, session_id=session_id)
            return {"message": "Session deleted"}
        except Exception as e:
            logger.error(f"❌ [DELETE SESSION] Lỗi: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.put("/{session_id}/title")
    async def update_session_title(session_id: str, request: CreateSessionRequest, user_id: str = Depends(get_current_user)):
        return {"session_id": session_id, "title": request.title}
    
    return router