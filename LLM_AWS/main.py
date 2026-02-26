"""
Main Application - Optimized for AWS Lambda Logging & CORS
"""
import logging
import os
import sys
import traceback
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from dotenv import load_dotenv

# Cấu hình logging để log hiển thị rõ ràng trên CloudWatch
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLM_AWS")
logger.setLevel(logging.INFO)

# Thêm parent directory vào path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Infrastructure & Domain imports
from LLM_AWS.infrastructure.short_memory_repo import DynamoDBShortMemoryRepository
from LLM_AWS.infrastructure.long_memory_repo import QdrantLongMemoryRepository
from LLM_AWS.infrastructure.vector_db_repo import QdrantVectorDBRepository
from LLM_AWS.infrastructure.llm_service import GeminiLLMService
from LLM_AWS.langgraph_agent.agent_graph import ChatAgent
from LLM_AWS.application.chat_usecase import ChatUseCase
from LLM_AWS.presentation.chat_controller import create_chat_router
from LLM_AWS.presentation.session_controller import create_session_router
from LLM_AWS.presentation.chat_history_controller import create_chat_history_router

load_dotenv()

def create_app() -> FastAPI:
    """Factory function tạo FastAPI app với logging và cấu hình chống 307"""
    
    config = {
        "aws_access": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "aws_region": os.getenv("AWS_REGION", "ap-southeast-1"),
        "qdrant_url": os.getenv("QDRANT_URL"),
        "qdrant_key": os.getenv("QDRANT_API_KEY"),
        "gemini_key": os.getenv("GEMINI_API_KEY"),
        "vector_collection": os.getenv("VECTOR_COLLECTION")
    }
    
    missing_keys = [k for k, v in config.items() if v is None]
    if missing_keys:
        logger.warning(f"⚠️ Thiếu biến môi trường: {', '.join(missing_keys)}")
    
    logger.info("🚀 Đang khởi tạo ứng dụng...")
    
    try:
        # Initialize repositories
        short_memory_repo = DynamoDBShortMemoryRepository(
            aws_access=config["aws_access"],
            aws_secret=config["aws_secret"],
            region=config["aws_region"]
        )
        
        long_memory_repo = QdrantLongMemoryRepository(
            qdrant_url=config["qdrant_url"],
            qdrant_key=config["qdrant_key"],
            gemini_key=config["gemini_key"]
        )
        
        vector_db_repo = QdrantVectorDBRepository(
            qdrant_url=config["qdrant_url"],
            qdrant_key=config["qdrant_key"],
            gemini_key=config["gemini_key"],
            collection_name=config["vector_collection"]
        )
        
        llm_service = GeminiLLMService(gemini_key=config["gemini_key"])
        
        agent = ChatAgent(
            short_memory_repo=short_memory_repo,
            long_memory_repo=long_memory_repo,
            vector_db_repo=vector_db_repo,
            llm_service=llm_service
        )
        
        chat_usecase = ChatUseCase(agent=agent)
        
        # CẤU HÌNH QUAN TRỌNG: tắt redirect_slashes để tránh lỗi 307
        app = FastAPI(
            title="AI Chat API",
            version="1.0.0",
            redirect_slashes=False 
        )
        
        # CORS: Mở rộng để chấp nhận cả header tùy chỉnh của bạn
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"], # Để * khi debug, sau đó đổi thành domain FE của bạn
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Middleware để log mọi request đi vào (Để bạn thấy log INFO như local)
        @app.middleware("http")
        async def log_requests(request: Request, call_next):
            logger.info(f"👉 Request: {request.method} {request.url.path}")
            try:
                response = await call_next(request)
                logger.info(f"👈 Response Status: {response.status_code}")
                return response
            except Exception as e:
                logger.error(f"❌ Lỗi hệ thống: {str(e)}")
                logger.error(traceback.format_exc())
                raise e

        # Register routers
        app.include_router(create_chat_router(chat_usecase))
        app.include_router(create_session_router(long_memory_repo)) 
        app.include_router(create_chat_history_router(long_memory_repo))
        
        @app.get("/")
        async def root():
            return {"status": "online", "message": "Lambda is alive!"}

        logger.info("✅ Ứng dụng đã khởi tạo thành công!")
        return app

    except Exception as e:
        logger.error(f"💥 Lỗi nghiêm trọng khi khởi tạo: {str(e)}")
        logger.error(traceback.format_exc())
        raise e

app = create_app()
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("LLM_AWS.main:app", host="0.0.0.0", port=7000, reload=True)