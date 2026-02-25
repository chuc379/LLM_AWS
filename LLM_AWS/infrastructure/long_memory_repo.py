"""
Infrastructure - Long Memory Repository Implementation (Qdrant)
"""
import time
import uuid
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models

from typing import List, Dict, Any
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from LLM_AWS.domain.repositories import ILongMemoryRepository
from LLM_AWS.domain.entities import LongMemory


class QdrantLongMemoryRepository(ILongMemoryRepository):
    def __init__(self, qdrant_url: str, qdrant_key: str, gemini_key: str):
        self.client = QdrantClient(url=qdrant_url, api_key=qdrant_key, check_compatibility=False)
        self.collection_name = "user_long_memory"
        self.dim = 768
        
        genai.configure(api_key=gemini_key)
        self._setup_collection()
    
    def _setup_collection(self):
        """Đảm bảo collection tồn tại"""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            print(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.dim,
                    distance=models.Distance.COSINE
                )
            )
            self.client.create_payload_index(
                self.collection_name,
                "user_id",
                models.PayloadSchemaType.KEYWORD
            )
            self.client.create_payload_index(
                self.collection_name,
                "session_id",
                models.PayloadSchemaType.KEYWORD
            )
    
    def _get_embedding(self, text: str, is_query: bool = False) -> List[float]:
        """Tạo embedding từ text"""
        task = "retrieval_query" if is_query else "retrieval_document"
        try:
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type=task,
                output_dimensionality=self.dim
            )
            return result['embedding']
        except Exception as e:
            print(f"Embedding error: {e}")
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type=task
            )
            return result['embedding']
    
    def search_memory(self, user_id: str, session_id: str, query: str, limit: int = 3) -> List[LongMemory]:
        """Tìm kiếm ký ức dài hạn"""
        query_vector = self._get_embedding(query, is_query=True)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id)),
                    models.FieldCondition(key="session_id", match=models.MatchValue(value=session_id))
                ]
            ),
            limit=limit,
            with_payload=True
        )
        
        return [
            LongMemory(
                user_id=user_id,
                session_id=session_id,
                content=hit.payload['full_content'],
                relevance_score=hit.score
            )
            for hit in results
        ]
    
    def save_chat_turn(self, user_id: str, session_id: str, user_msg: str, ai_msg: str, title: str = "Cuộc trò chuyện mới") -> None:
        """Lưu lượt chat kèm theo title để hiển thị ở danh sách session"""
        combined_text = f"Người dùng: {user_msg}\nAI: {ai_msg}"
        vector = self._get_embedding(combined_text, is_query=False)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "user_id": user_id,
                        "session_id": session_id,
                        "title": title, # Lưu title vào đây
                        "user_msg": user_msg,
                        "ai_msg": ai_msg,
                        "full_content": combined_text,
                        "timestamp": int(time.time())
                    }
                )
            ]
        )

    def get_unique_sessions(self, user_id: str) -> List[Dict[str, Any]]:
            """
            LẤY DANH SÁCH SESSION DUY NHẤT TỪ QDRANT (Sử dụng Scroll để đảm bảo tính tương thích)
            """
            try:
                from datetime import datetime
                
                # 1. Lấy dữ liệu thô từ Qdrant (Scroll hoạt động ổn định trên mọi phiên bản)
                # Chúng ta quét 100 bản ghi gần nhất để tìm các session_id khác nhau
                records, _ = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=models.Filter(
                        must=[
                            models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))
                        ]
                    ),
                    limit=100,
                    with_payload=True,
                    with_vectors=False
                )

                # 2. Dùng Dictionary để lọc ra các session_id duy nhất và lấy tin nhắn mới nhất
                unique_sessions_dict = {}
                for rec in records:
                    p = rec.payload
                    s_id = p.get("session_id")
                    if not s_id:
                        continue
                    
                    # Lấy timestamp để so sánh
                    current_ts = p.get("timestamp", 0)
                    
                    # Nếu chưa thấy session này HOẶC tin nhắn này mới hơn tin nhắn đã lưu trong dict
                    if s_id not in unique_sessions_dict or current_ts > unique_sessions_dict[s_id]["_ts"]:
                        unique_sessions_dict[s_id] = {
                            "session_id": s_id,
                            "title": p.get("title", "Cuộc trò chuyện mới"),
                            "created_at": datetime.fromtimestamp(current_ts).isoformat() if current_ts > 0 else datetime.now().isoformat(),
                            "last_message": (p.get("ai_msg", "")[:50] + "...") if p.get("ai_msg") else "",
                            "_ts": current_ts  # Dùng nội bộ để sắp xếp
                        }

                # 3. Chuyển đổi thành danh sách và sắp xếp theo thời gian mới nhất lên đầu
                sessions = list(unique_sessions_dict.values())
                sessions.sort(key=lambda x: x['_ts'], reverse=True)
                
                # Xóa trường tạm thời _ts trước khi trả về
                for s in sessions:
                    s.pop("_ts", None)
                
                return sessions

            except Exception as e:
                print(f"❌ Error fetching unique sessions with scroll: {e}")
                return []    
    def get_session_chat_turns(self, user_id: str, session_id: str, limit: int = 50):
        """Lấy các lượt chat (user_msg, ai_msg, timestamp) của một session từ Qdrant"""
        try:
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id)),
                        models.FieldCondition(key="session_id", match=models.MatchValue(value=session_id))
                    ]
                ),
                limit=limit,
                with_payload=True
            )

            # Sắp xếp theo thời gian cũ -> mới
            sorted_results = sorted(results, key=lambda r: r.payload.get("timestamp", 0))

            turns = []
            for hit in sorted_results:
                payload = hit.payload or {}
                turns.append({
                    "user_msg": payload.get("user_msg", ""),
                    "ai_msg": payload.get("ai_msg", ""),
                    "timestamp": payload.get("timestamp", 0)
                })
            
            return turns
        except Exception as e:
            print(f"Error fetching session history from Qdrant: {e}")
            return []
    
    def clear_session(self, user_id: str, session_id: str) -> None:
        """Xóa session"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id)),
                        models.FieldCondition(key="session_id", match=models.MatchValue(value=session_id))
                    ]
                )
            )
        )
