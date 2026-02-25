"""
Domain Repositories - Interfaces cho data access
"""
from abc import ABC, abstractmethod
from typing import List
from .entities import ShortMemory, LongMemory, VectorSearchResult, ChatMessage


class IShortMemoryRepository(ABC):
    """Interface cho Short Memory (DynamoDB)"""
    
    @abstractmethod
    def get_recent_messages(self, user_id: str, limit: int = 5) -> List[ChatMessage]:
        """Lấy tin nhắn gần đây"""
        pass
    
    @abstractmethod
    def save_message(self, user_id: str, user_msg: str, ai_msg: str) -> None:
        """Lưu tin nhắn mới"""
        pass


class ILongMemoryRepository(ABC):
    """Interface cho Long Memory (Qdrant)"""
    
    @abstractmethod
    def search_memory(self, user_id: str, session_id: str, query: str, limit: int = 3) -> List[LongMemory]:
        """Tìm kiếm ký ức dài hạn"""
        pass
    
    @abstractmethod
    def save_chat_turn(self, user_id: str, session_id: str, user_msg: str, ai_msg: str) -> None:
        """Lưu lượt chat vào long memory"""
        pass
    
    @abstractmethod
    def clear_session(self, user_id: str, session_id: str) -> None:
        """Xóa session"""
        pass
    
    @abstractmethod
    def get_unique_sessions(self, user_id: str) -> List[dict]:
        """Lấy danh sách các session duy nhất của một user từ Qdrant"""
        pass

class IVectorDBRepository(ABC):
    """Interface cho Vector Database (Knowledge Base)"""
    
    @abstractmethod
    def search(self, query: str, limit: int = 3) -> List[VectorSearchResult]:
        """Tìm kiếm trong knowledge base"""
        pass


class ILLMService(ABC):
    """Interface cho LLM Service"""
    
    @abstractmethod
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response từ LLM"""
        pass
