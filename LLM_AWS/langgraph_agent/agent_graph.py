"""
LangGraph Agent - Orchestration Logic
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from LLM_AWS.langgraph_agent.agent_state import AgentState
from LLM_AWS.domain.repositories import (
    IShortMemoryRepository,
    ILongMemoryRepository,
    IVectorDBRepository,
    ILLMService
)


class ChatAgent:
    """LangGraph Agent để điều phối chat flow"""
    
    def __init__(
        self,
        short_memory_repo: IShortMemoryRepository,
        long_memory_repo: ILongMemoryRepository,
        vector_db_repo: IVectorDBRepository,
        llm_service: ILLMService
    ):
        self.short_memory_repo = short_memory_repo
        self.long_memory_repo = long_memory_repo
        self.vector_db_repo = vector_db_repo
        self.llm_service = llm_service
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Xây dựng LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("fetch_short_memory", self._fetch_short_memory)
        workflow.add_node("fetch_long_memory", self._fetch_long_memory)
        workflow.add_node("search_vector_db", self._search_vector_db)
        workflow.add_node("build_context", self._build_context)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("save_memories", self._save_memories)
        
        # Define edges
        workflow.set_entry_point("fetch_short_memory")
        workflow.add_edge("fetch_short_memory", "fetch_long_memory")
        workflow.add_edge("fetch_long_memory", "search_vector_db")
        workflow.add_edge("search_vector_db", "build_context")
        workflow.add_edge("build_context", "generate_response")
        workflow.add_edge("generate_response", "save_memories")
        workflow.add_edge("save_memories", END)
        
        return workflow.compile()
    
    def _fetch_short_memory(self, state: AgentState) -> Dict[str, Any]:
        """Node 1: Lấy short memory từ DynamoDB"""
        print("📝 Fetching short memory...")
        try:
            messages = self.short_memory_repo.get_recent_messages(state["user_id"], limit=5)
            return {
                "short_memory": messages,
                "used_short_memory": len(messages) > 0
            }
        except Exception as e:
            print(f"Error fetching short memory: {e}")
            return {
                "short_memory": [],
                "used_short_memory": False
            }
    
    def _fetch_long_memory(self, state: AgentState) -> Dict[str, Any]:
        """Node 2: Tìm kiếm long memory từ Qdrant"""
        print("🧠 Searching long memory...")
        try:
            memories = self.long_memory_repo.search_memory(
                state["user_id"],
                state["session_id"],
                state["user_message"],
                limit=3
            )
            return {
                "long_memory": memories,
                "used_long_memory": len(memories) > 0
            }
        except Exception as e:
            print(f"Error fetching long memory: {e}")
            return {
                "long_memory": [],
                "used_long_memory": False
            }
    
    def _search_vector_db(self, state: AgentState) -> Dict[str, Any]:
        """Node 3: Tìm kiếm trong Vector DB (Knowledge Base)"""
        print("🔍 Searching vector database...")
        try:
            results = self.vector_db_repo.search(state["user_message"], limit=3)
            sources = [r.metadata.get('url', '') for r in results if r.metadata.get('url')]
            return {
                "vector_results": results,
                "sources": sources,
                "used_vector_db": len(results) > 0
            }
        except Exception as e:
            print(f"Error searching vector DB: {e}")
            return {
                "vector_results": [],
                "sources": [],
                "used_vector_db": False
            }
    
    def _build_context(self, state: AgentState) -> Dict[str, Any]:
        """Node 4: Xây dựng context từ tất cả nguồn"""
        print("🔨 Building context...")
        
        context_parts = []
        
        # Short memory context
        if state.get("used_short_memory") and state.get("short_memory"):
            context_parts.append("=== Lịch sử trò chuyện gần đây ===")
            for msg in state["short_memory"]:
                role = "Người dùng" if msg.role == "user" else "AI"
                context_parts.append(f"{role}: {msg.content}")
        
        # Long memory context
        if state.get("used_long_memory") and state.get("long_memory"):
            context_parts.append("\n=== Ký ức liên quan ===")
            for mem in state["long_memory"]:
                context_parts.append(f"- {mem.content} (độ liên quan: {mem.relevance_score:.2f})")
        
        # Vector DB context
        if state.get("used_vector_db") and state.get("vector_results"):
            context_parts.append("\n=== Kiến thức từ cơ sở dữ liệu ===")
            for result in state["vector_results"]:
                context_parts.append(f"- {result.content[:200]}...")
                if result.metadata.get('title'):
                    context_parts.append(f"  (Nguồn: {result.metadata['title']})")
        
        context_string = "\n".join(context_parts)
        
        # Build final prompt
        final_prompt = f"""Bạn là một trợ lý AI thông minh. Hãy trả lời câu hỏi dựa trên ngữ cảnh được cung cấp.

{context_string}

Câu hỏi mới: {state["user_message"]}

Hãy trả lời một cách tự nhiên, thân thiện và chính xác. Nếu thông tin không đủ, hãy nói rõ."""
        
        return {
            "context_string": context_string,
            "final_prompt": final_prompt
        }
    
    def _generate_response(self, state: AgentState) -> Dict[str, Any]:
        """Node 5: Generate response từ LLM"""
        print("🤖 Generating AI response...")
        try:
            response = self.llm_service.generate_response(state["final_prompt"])
            return {"ai_response": response}
        except Exception as e:
            print(f"Error generating response: {e}")
            return {"ai_response": f"Xin lỗi, tôi gặp lỗi: {str(e)}"}
    
    def _save_memories(self, state: AgentState) -> Dict[str, Any]:
        """Node 6: Lưu vào cả short và long memory"""
        print("💾 Saving to memories...")
        
        user_msg = state["user_message"]
        ai_msg = state["ai_response"]
        
        # Save to short memory (DynamoDB)
        try:
            self.short_memory_repo.save_message(state["user_id"], user_msg, ai_msg)
            print("✅ Saved to short memory")
        except Exception as e:
            print(f"Error saving to short memory: {e}")
        
        # Save to long memory (Qdrant)
        try:
            self.long_memory_repo.save_chat_turn(
                state["user_id"],
                state["session_id"],
                user_msg,
                ai_msg
            )
            print("✅ Saved to long memory")
        except Exception as e:
            print(f"Error saving to long memory: {e}")
        
        return {}
    
    def chat(self, user_id: str, session_id: str, message: str) -> Dict[str, Any]:
        """Main entry point để chat"""
        print(f"\n{'='*50}")
        print(f"🚀 Starting chat for user: {user_id}")
        print(f"{'='*50}\n")
        
        # Initialize state
        initial_state: AgentState = {
            "user_id": user_id,
            "session_id": session_id,
            "user_message": message,
            "short_memory": [],
            "long_memory": [],
            "vector_results": [],
            "context_string": "",
            "final_prompt": "",
            "ai_response": "",
            "sources": [],
            "used_short_memory": False,
            "used_long_memory": False,
            "used_vector_db": False,
            "error": None
        }
        
        # Run graph
        final_state = self.graph.invoke(initial_state)
        
        print(f"\n{'='*50}")
        print(f"✅ Chat completed")
        print(f"{'='*50}\n")
        
        return {
            "message": final_state["ai_response"],
            "sources": final_state.get("sources", []),
            "used_short_memory": final_state.get("used_short_memory", False),
            "used_long_memory": final_state.get("used_long_memory", False),
            "used_vector_db": final_state.get("used_vector_db", False)
        }
