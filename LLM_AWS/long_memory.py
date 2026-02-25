import time
import uuid
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models

class GeminiLongMemoryManager:
    def __init__(self, qdrant_url, qdrant_key, gemini_key):
        # 1. Khởi tạo Client với bỏ qua check version để tránh warning
        self.client = QdrantClient(url=qdrant_url, api_key=qdrant_key, check_compatibility=False)
        self.collection_name = "user_long_memory"
        self.dim = 768  # Cố định 768 theo cấu hình collection hiện tại của bạn
        
        # 2. Cấu hình Gemini
        genai.configure(api_key=gemini_key)
        
        # 3. Đảm bảo Collection tồn tại
        self._setup_collection()

    def _setup_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            print(f"--- Đang khởi tạo Collection mới: {self.collection_name} ---")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.dim, 
                    distance=models.Distance.COSINE
                )
            )
            # Index để filter nhanh theo ID
            self.client.create_payload_index(self.collection_name, "user_id", models.PayloadSchemaType.KEYWORD)
            self.client.create_payload_index(self.collection_name, "session_id", models.PayloadSchemaType.KEYWORD)

    def _get_embedding(self, text, is_query=False):
        """Dùng model 004 và ép về 768 chiều"""
        task = "retrieval_query" if is_query else "retrieval_document"
        try:
            result = genai.embed_content(
                model="models/gemini-embedding-001", # Model đời mới nhất
                content=text,
                task_type=task,
                output_dimensionality=self.dim # ÉP CHẶT VỀ 768 CHIỀU
            )
            return result['embedding']
        except Exception as e:
            print(f"Lỗi Embedding: {e}")
            # Fallback nếu model 004 lỗi thì dùng 001 (mặc định 768)
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type=task
            )
            return result['embedding']

    def save_chat_turn(self, user_id, session_id, user_msg, ai_msg):
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
                        "user_msg": user_msg,
                        "ai_msg": ai_msg,
                        "full_content": combined_text,
                        "timestamp": int(time.time())
                    }
                )
            ]
        )

    def search_memory(self, user_id, session_id, query, limit=3):
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
        return [hit.payload['full_content'] for hit in results]

    def clear_session(self, user_id, session_id):
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

# --- KHỐI CHẠY TEST ---
if __name__ == "__main__":
    URL = "https://a15c7255-307c-476b-8067-b79f6dac0c74.us-west-1-0.aws.cloud.qdrant.io"
    KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.U8yUySqfl97_BvbwvUiK45_xdea3S68r6gQCOOPDcPQ"
    G_KEY = "AIzaSyDVJBtZe27XWD3aVBha-t25XinVjEQmnQI" # Nhớ điền Key thật của bạn nhé

    memory = GeminiLongMemoryManager(URL, KEY, G_KEY)

    UID = "user_123"
    SID = "session_test_001"

    print("--- Đang lưu ký ức mới ---")
    memory.save_chat_turn(UID, SID, "Tôi thích uống cà phê sữa đá ít đường", "Đã ghi nhận sở thích của bạn.")
    
    # Chờ 1 giây để Qdrant kịp Index
    time.sleep(1)

    print("--- Đang tìm kiếm ký ức ---")
    kq = memory.search_memory(UID, SID, "Tôi uống cafe thế nào?")
    print(f"Kết quả: {kq}")