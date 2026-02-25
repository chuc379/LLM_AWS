import time
import uuid
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models

class QdrantShortTermMemory:
    def __init__(self, url, key, gemini_key):
        # 1. Kết nối Qdrant
        self.client = QdrantClient(url=url, api_key=key, check_compatibility=False)
        self.collection_name = "short_term_vectors"
        self.dim = 768
        
        # 2. Cấu hình Gemini (Sửa lỗi Reauthentication bằng cách ép dùng API KEY)
        genai.configure(api_key=gemini_key)
        
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Khởi tạo collection và index nếu chưa có"""
        try:
            self.client.get_collection(self.collection_name)
            print(f"--- Đã kết nối tới Collection: {self.collection_name} ---")
        except Exception:
            print(f"--- Đang khởi tạo Collection mới: {self.collection_name} ---")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "vector": models.VectorParams(size=self.dim, distance=models.Distance.COSINE)
                }
            )
            # Index cho user_id và expiry_at để lọc và xóa nhanh
            self.client.create_payload_index(self.collection_name, "user_id", models.PayloadSchemaType.KEYWORD)
            self.client.create_payload_index(self.collection_name, "expiry_at", models.PayloadSchemaType.INTEGER)
            print("--- Đã tạo Collection và Index thành công ---")

    def _get_emb(self, text):
        """Lấy Embedding và xử lý lỗi xác thực gcloud"""
        try:
            # Task_type retrieval_document giúp tìm kiếm chính xác hơn
            result = genai.embed_content(
                model="models/gemini-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            emb = result['embedding']
            # Fix dimension 768
            if len(emb) > self.dim: return emb[:self.dim]
            if len(emb) < self.dim: return emb + [0.0] * (self.dim - len(emb))
            return emb
        except Exception as e:
            print(f"Lỗi Embedding: {e}")
            return [0.0] * self.dim

    def cleanup_expired_vectors(self):
        """Xóa các vector đã quá 24 giờ"""
        now = int(time.time())
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="expiry_at",
                                range=models.Range(lt=now) # lt = less than (nhỏ hơn bây giờ)
                            )
                        ]
                    )
                )
            )
            # print(f"--- Đã dọn dẹp các ký ức hết hạn ---")
        except Exception as e:
            print(f"Lỗi dọn dẹp: {e}")

    def upsert_short_term(self, user_id, session_id, text):
        """Lưu ký ức ngắn hạn (tự xóa sau 24h)"""
        # Bước 1: Dọn rác trước khi lưu mới
        self.cleanup_expired_vectors()
        
        vector = self._get_emb(text)
        now = int(time.time())
        expiry_at = now + (24 * 3600) # 24 giờ sau
        
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector={"vector": vector}, 
                        payload={
                            "user_id": user_id,
                            "session_id": session_id,
                            "content": text,
                            "timestamp": now,
                            "expiry_at": expiry_at # Mốc thời gian hết hạn
                        }
                    )
                ]
            )
            print(f"--- Đã lưu ký ức ngắn hạn (hết hạn sau 24h): {session_id} ---")
        except Exception as e:
            print(f"Lỗi Upsert Qdrant: {e}")

    def search_relevant_memories(self, user_id, query, limit=3):
        query_vector = self._get_emb(query)
        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                using="vector",
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))
                    ]
                ),
                limit=limit
            ).points
            return [hit.payload['content'] for hit in results]
        except Exception as e:
            print(f"Lỗi Search Qdrant: {e}")
            return []

if __name__ == "__main__":
    # URL và KEY Qdrant của bạn
    Q_URL = "https://a15c7255-307c-476b-8067-b79f6dac0c74.us-west-1-0.aws.cloud.qdrant.io"
    Q_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.U8yUySqfl97_BvbwvUiK45_xdea3S68r6gQCOOPDcPQ"
    # Dùng API Key Gemini MỚI (Lưu ý: Không dùng gcloud auth)
    G_KEY = "AIzaSyDVJBtZe27XWD3aVBha-t25XinVjEQmnQI" 

    v_memory = QdrantShortTermMemory(Q_URL, Q_KEY, G_KEY)
    
    UID = "nam_test_101"
    SID = "phien_chat_002"
    
    print("\n--- Test lưu ký ức ngắn hạn ---")
    v_memory.upsert_short_term(UID, SID, "Ngày mai tôi có cuộc hẹn lúc 9 giờ sáng")
    
    time.sleep(1) 
    
    print("\n--- Truy vấn ký ức liên quan ---")
    kq = v_memory.search_relevant_memories(UID, "Tôi có lịch hẹn lúc mấy giờ?")
    print(f"Kết quả: {kq}")
