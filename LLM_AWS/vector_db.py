import boto3
import json
import uuid
import time
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# --- CẤU HÌNH MỚI (3072 DIM) ---
GENAI_API_KEY = "AIzaSyDVJBtZe27XWD3aVBha-t25XinVjEQmnQI"
AWS_CONFIG = {
    "aws_access_key_id": "AKIAWNREQUNE6TK6Y5M7",
    "aws_secret_access_key": "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",
    "region_name": "ap-southeast-1"
}
S3_BUCKET_NAME = "knowknowledge-base-chuong"
S3_PREFIX = "datalake/raw_data/"

QDRANT_URL = "https://a15c7255-307c-476b-8067-b79f6dac0c74.us-west-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.U8yUySqfl97_BvbwvUiK45_xdea3S68r6gQCOOPDcPQ"

# ĐỔI TÊN COLLECTION ĐỂ TẠO MỚI VỚI 3072 CHIỀU
COLLECTION_NAME = "nfl_wiki_gemini_3072" 
VECTOR_DIM = 3072 # Nâng cấp lên chuẩn cao nhất của model 004

# Khởi tạo clients
genai.configure(api_key=GENAI_API_KEY)
s3_client = boto3.client('s3', **AWS_CONFIG)
q_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, check_compatibility=False)

class WikiGeminiPipeline:
    def __init__(self):
        self.dim = VECTOR_DIM
        headers_to_split_on = [
            ("#", "Header_1"),
            ("##", "Header_2"),
            ("###", "Header_3"),
        ]
        self.header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            q_client.get_collection(COLLECTION_NAME)
            print(f"--- Đã kết nối Collection 3072: {COLLECTION_NAME} ---")
        except Exception:
            print(f"--- Đang tạo Collection mới với {self.dim} chiều... ---")
            q_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=self.dim, 
                    distance=models.Distance.COSINE
                )
            )

    def _get_emb_with_retry(self, text):
        for attempt in range(5):
            try:
                # Sử dụng model 004 trả về FULL 3072 chiều
                result = genai.embed_content(
                    model="models/gemini-embedding-001", 
                    content=text,
                    task_type="retrieval_document"
                    # Bỏ tham số output_dimensionality để lấy mặc định 3072
                )
                return result['embedding']
            except Exception as e:
                if "429" in str(e):
                    wait_time = (attempt + 1) * 30 
                    print(f"⚠️ Quota Limit. Nghỉ {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Error tại Embedding: {e}")
                    return None
        return None

    def process_all_s3(self):
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=S3_PREFIX)
        files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.json')]

        for key in files:
            print(f"\n🚀 Processing: {key}")
            obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
            data = json.loads(obj['Body'].read().decode('utf-8'))
            
            header_sections = self.header_splitter.split_text(data['content'])
            final_chunks = self.text_splitter.split_documents(header_sections)
            
            print(f"📊 Tạo được {len(final_chunks)} chunks (3072-dim).")

            points = []
            for i, doc in enumerate(final_chunks):
                metadata_str = " | ".join([f"{k}: {v}" for k, v in doc.metadata.items()])
                contextual_text = f"Context: {metadata_str}\nContent: {doc.page_content}"
                
                vector = self._get_emb_with_retry(contextual_text)
                if vector:
                    # Kiểm tra độ dài vector trước khi lưu (debug)
                    if len(vector) != self.dim:
                        print(f"⚠️ Sai chiều: Got {len(vector)}, expected {self.dim}")
                        continue

                    points.append(models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vector,
                        payload={
                            "title": data.get('title', 'NFL Wiki'),
                            "content": doc.page_content,
                            "metadata": doc.metadata,
                            "url": data.get('url', ''),
                            "timestamp": int(time.time())
                        }
                    ))
                    time.sleep(1.2) # Giữ an toàn cho Quota

                if len(points) >= 5:
                    q_client.upsert(collection_name=COLLECTION_NAME, points=points)
                    points = []
            
            if points:
                q_client.upsert(collection_name=COLLECTION_NAME, points=points)
            print(f"✅ Đã tải xong: {data.get('title')}")

def main():
    print("=== PIPELINE VECTOR DB (HIGH-PRECISION 3072) ===")
    pipeline = WikiGeminiPipeline()
    pipeline.process_all_s3()

if __name__ == "__main__":
    main()