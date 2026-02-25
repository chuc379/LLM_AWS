"""
LangGraph Agent State Definition
"""
from typing import TypedDict, List, Optional

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from LLM_AWS.domain.entities import ChatMessage, LongMemory, VectorSearchResult


class AgentState(TypedDict):
    """State của Agent trong LangGraph"""
    # Input
    user_id: str
    session_id: str
    user_message: str
    
    # Memory context
    short_memory: List[ChatMessage]
    long_memory: List[LongMemory]
    vector_results: List[VectorSearchResult]
    
    # Processing
    context_string: str
    final_prompt: str
    
    # Output
    ai_response: str
    sources: List[str]
    
    # Flags
    used_short_memory: bool
    used_long_memory: bool
    used_vector_db: bool
    
    # Error handling
    error: Optional[str]
