"""
Domain Entities - Core Business Objects
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ChatMessage:
    """Đại diện cho một tin nhắn chat"""
    role: str  # "user" hoặc "assistant"
    content: str
    timestamp: datetime


@dataclass
class ShortMemory:
    """Bộ nhớ ngắn hạn từ DynamoDB"""
    user_id: str
    messages: List[ChatMessage]
    session_id: Optional[str] = None


@dataclass
class LongMemory:
    """Bộ nhớ dài hạn từ Qdrant"""
    user_id: str
    session_id: str
    content: str
    relevance_score: float


@dataclass
class VectorSearchResult:
    """Kết quả tìm kiếm từ Vector DB"""
    content: str
    metadata: dict
    score: float


@dataclass
class ChatRequest:
    """Request từ client"""
    user_id: str
    session_id: str
    message: str


@dataclass
class ChatResponse:
    """Response trả về client"""
    message: str
    sources: List[str]
    used_short_memory: bool
    used_long_memory: bool
    used_vector_db: bool
