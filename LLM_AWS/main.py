"""
Main Application - Enhanced Debugging for AWS Lambda
"""
import logging
import os
import sys
import traceback
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from dotenv import load_dotenv

# 1. Cấu hình Logging cực kỳ chi tiết
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLM_AWS")
logger.setLevel(logging.DEBUG) # Chuyển sang DEBUG để xem chi tiết hơn

# Thêm parent directory vào path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

load_dotenv()

def create_app() -> FastAPI:
    try:
        # Import trong hàm để bắt lỗi nếu một trong các repo bị lỗi import/config
        from LLM_AWS.infrastructure.short_memory_repo import DynamoDBShortMemoryRepository
        from LLM_AWS.infrastructure.long_memory_repo import QdrantLongMemoryRepository
        from LLM_AWS.infrastructure.vector_db_repo import QdrantVectorDBRepository
        from LLM_AWS.infrastructure.llm_service import GeminiLLMService
        from LLM_AWS.langgraph_agent.agent_graph import ChatAgent
        from LLM_AWS.application.chat_usecase import ChatUseCase
        from LLM_AWS.presentation.chat_controller import create_chat_router
        from LLM_AWS.presentation.session_controller import create_session_router
        from LLM_AWS.presentation.chat_history_controller import create_chat_history_router

        config = {
            "aws_access": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "aws_region": os.getenv("AWS_REGION", "ap-southeast-1"),
            "qdrant_url": os.getenv("QDRANT_URL"),
            "qdrant_key": os.getenv("QDRANT_API_KEY"),
            "gemini_key": os.getenv("GEMINI_API_KEY"),
            "vector_collection": os.getenv("VECTOR_COLLECTION")
        }

        logger.info("🚀 Đang khởi tạo các thành phần hệ thống...")
        
        # Init Repos
        short_memory_repo = DynamoDBShortMemoryRepository(
            aws_access=config["aws_access"],
            aws_secret=config["aws_secret"],
            region=config["aws_region"]
        )
        long_memory_repo = QdrantLongMemoryRepository(
            qdrant_url=config["qdrant_url"], qdrant_key=config["qdrant_key"], gemini_key=config["gemini_key"]
        )
        vector_db_repo = QdrantVectorDBRepository(
            qdrant_url=config["qdrant_url"], qdrant_key=config["qdrant_key"],
            gemini_key=config["gemini_key"], collection_name=config["vector_collection"]
        )
        llm_service = GeminiLLMService(gemini_key=config["gemini_key"])
        
        agent = ChatAgent(
            short_memory_repo=short_memory_repo,
            long_memory_repo=long_memory_repo,
            vector_db_repo=vector_db_repo,
            llm_service=llm_service
        )
        chat_usecase = ChatUseCase(agent=agent)

        app = FastAPI(title="AI Chat API", redirect_slashes=False)

        # 2. Cấu hình CORS mạnh mẽ
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 3. Global Exception Handler (Bắt mọi lỗi Runtime và trả về JSON)
        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            err_msg = traceback.format_exc()
            logger.error(f"❌ CRASH DETECTED: {err_msg}")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": str(exc),
                    "traceback": err_msg,
                    "message": "Lỗi nội bộ server được bắt bởi Global Handler"
                },
            )

        # Middleware log request
        @app.middleware("http")
        async def log_requests(request: Request, call_next):
            logger.info(f"👉 Request: {request.method} {request.url.path}")
            response = await call_next(request)
            logger.info(f"👈 Response Status: {response.status_code}")
            return response

        # Routers
        app.include_router(create_chat_router(chat_usecase))
        app.include_router(create_session_router(long_memory_repo)) 
        app.include_router(create_chat_history_router(long_memory_repo))
        
        @app.get("/")
        async def root():
            return {"status": "online", "env_check": {k: "✅" if v else "❌" for k, v in config.items()}}

        logger.info("✅ Ứng dụng đã sẵn sàng!")
        return app

    except Exception as e:
        # In ra log ngay lập tức nếu khởi tạo thất bại
        print("💥 FATAL ERROR DURING STARTUP:")
        print(traceback.format_exc())
        raise e

# Khởi tạo app
try:
    app = create_app()
    # 4. Cấu hình Mangum để log chi tiết lỗi từ AWS Lambda
    handler = Mangum(app, lifespan="off") 
except Exception:
    # Nếu crash ngay từ đầu, tạo một handler giả để không sập toàn bộ Lambda
    def handler(event, context):
        print("❌ Lambda Handler failed to initialize")
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "body": "Lambda Initialization Failed. Check Logs."
        }