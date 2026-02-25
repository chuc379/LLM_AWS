"""
Main Application - Dependency Injection & FastAPI Setup
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Infrastructure
from LLM_AWS.infrastructure.short_memory_repo import DynamoDBShortMemoryRepository
from LLM_AWS.infrastructure.long_memory_repo import QdrantLongMemoryRepository
from LLM_AWS.infrastructure.vector_db_repo import QdrantVectorDBRepository
from LLM_AWS.infrastructure.llm_service import GeminiLLMService

# LangGraph Agent
from LLM_AWS.langgraph_agent.agent_graph import ChatAgent

# Application
from LLM_AWS.application.chat_usecase import ChatUseCase

# Presentation
from LLM_AWS.presentation.chat_controller import create_chat_router
from LLM_AWS.presentation.session_controller import create_session_router
from LLM_AWS.presentation.chat_history_controller import create_chat_history_router


# Load environment variables
load_dotenv()


def create_app() -> FastAPI:
    """Factory function để tạo FastAPI app với dependency injection"""
    
    # Configuration - Đã loại bỏ hardcode strings
    config = {
        # AWS
        "aws_access": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "aws_region": os.getenv("AWS_REGION", "ap-southeast-1"),
        
        # Qdrant
        "qdrant_url": os.getenv("QDRANT_URL"),
        "qdrant_key": os.getenv("QDRANT_API_KEY"),
        
        # Gemini
        "gemini_key": os.getenv("GEMINI_API_KEY"),
        
        # Vector DB Collection
        "vector_collection": os.getenv("VECTOR_COLLECTION")
    }
    
    # Kiểm tra nhanh xem các key quan trọng có bị thiếu không
    missing_keys = [k for k, v in config.items() if v is None]
    if missing_keys:
        print(f"⚠️ Cảnh báo: Thiếu biến môi trường: {', '.join(missing_keys)}")
    
    print("🚀 Initializing application...")
    
    # Initialize repositories
    print("📦 Creating repositories...")
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
    
    # Initialize LangGraph Agent
    print("🤖 Creating LangGraph agent...")
    agent = ChatAgent(
        short_memory_repo=short_memory_repo,
        long_memory_repo=long_memory_repo,
        vector_db_repo=vector_db_repo,
        llm_service=llm_service
    )
    
    # Initialize Use Case
    print("💼 Creating use cases...")
    chat_usecase = ChatUseCase(agent=agent)
    
    # Create FastAPI app
    print("🌐 Creating FastAPI app...")
    app = FastAPI(
        title="AI Chat API with Memory & Vector DB",
        description="Clean Architecture + LangGraph + Gemini + AWS + Qdrant",
        version="1.0.0"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routers
    print("🔌 Registering routers...")
    chat_router = create_chat_router(chat_usecase)
    session_router = create_session_router(long_memory_repo) 
    chat_history_router = create_chat_history_router(long_memory_repo)
    app.include_router(chat_router)
    app.include_router(session_router)
    app.include_router(chat_history_router)
    
    @app.get("/")
    async def root():
        return {
            "message": "AI Chat API is running!",
            "docs": "/docs",
            "health": "/health"
        }
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "services": {
                "short_memory": "DynamoDB",
                "long_memory": "Qdrant",
                "vector_db": "Qdrant",
                "llm": "Gemini"
            }
        }
    
    print("✅ Application initialized successfully!")
    return app


# Create app instance (dùng chung cho cả uvicorn local và Lambda)
app = create_app()

# Handler cho AWS Lambda (RIC sẽ gọi vào đây)
handler = Mangum(app)


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting AI Chat API Server")
    print("="*60)
    print(f"📍 Server: http://localhost:7000")
    print(f"📚 Swagger UI: http://localhost:7000/docs")
    print(f"📖 ReDoc: http://localhost:7000/redoc")
    print(f"💚 Health Check: http://localhost:7000/health")
    print("="*60 + "\n")
    
    uvicorn.run(
        "LLM_AWS.main:app",
        host="0.0.0.0",
        port=7000,
        reload=True,
        log_level="info"
    )
