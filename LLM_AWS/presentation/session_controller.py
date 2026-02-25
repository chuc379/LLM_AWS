"""
Session Management Controller
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


# Models
class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: str
    last_message: str = ""


class CreateSessionRequest(BaseModel):
    title: str = "New Chat"


# Router
router = APIRouter(prefix="/api/sessions", tags=["sessions"])


# In-memory storage (trong production nên dùng database)
sessions_db = {}


def create_session_router() -> APIRouter:
    """Factory function để tạo session router"""
    
    @router.get("/", response_model=List[SessionResponse])
    async def get_sessions(user_id: str = Depends(get_current_user)):
        """Lấy danh sách sessions của user"""
        user_sessions = sessions_db.get(user_id, [])
        return user_sessions
    
    @router.post("/", response_model=SessionResponse)
    async def create_session(
        request: CreateSessionRequest,
        user_id: str = Depends(get_current_user)
    ):
        """Tạo session mới"""
        session_id = str(uuid.uuid4())
        session = SessionResponse(
            session_id=session_id,
            title=request.title,
            created_at=datetime.now().isoformat(),
            last_message=""
        )
        
        if user_id not in sessions_db:
            sessions_db[user_id] = []
        
        sessions_db[user_id].append(session)
        return session
    
    @router.delete("/{session_id}")
    async def delete_session(
        session_id: str,
        user_id: str = Depends(get_current_user)
    ):
        """Xóa session"""
        if user_id in sessions_db:
            sessions_db[user_id] = [
                s for s in sessions_db[user_id] 
                if s.session_id != session_id
            ]
        return {"message": "Session deleted"}
    
    @router.put("/{session_id}/title")
    async def update_session_title(
        session_id: str,
        request: CreateSessionRequest,
        user_id: str = Depends(get_current_user)
    ):
        """Cập nhật title của session"""
        if user_id in sessions_db:
            for session in sessions_db[user_id]:
                if session.session_id == session_id:
                    session.title = request.title
                    return session
        
        raise HTTPException(status_code=404, detail="Session not found")
    
    return router
