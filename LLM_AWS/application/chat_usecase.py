"""
Application Layer - Chat Use Case
"""
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from LLM_AWS.domain.entities import ChatRequest, ChatResponse
from LLM_AWS.langgraph_agent.agent_graph import ChatAgent


class ChatUseCase:
    """Use case để xử lý chat request"""
    
    def __init__(self, agent: ChatAgent):
        self.agent = agent
    
    def execute(self, request: ChatRequest) -> ChatResponse:
        """Execute chat use case"""
        result = self.agent.chat(
            user_id=request.user_id,
            session_id=request.session_id,
            message=request.message
        )
        
        return ChatResponse(
            message=result["message"],
            sources=result.get("sources", []),
            used_short_memory=result.get("used_short_memory", False),
            used_long_memory=result.get("used_long_memory", False),
            used_vector_db=result.get("used_vector_db", False)
        )
