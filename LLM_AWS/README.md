# AI Chat API - Clean Architecture + LangGraph

Hệ thống chat AI với Clean Architecture, sử dụng LangGraph để điều phối, tích hợp Short Memory (DynamoDB), Long Memory (Qdrant), Vector DB (Qdrant), và Gemini LLM.

## 🏗️ Kiến trúc

```
LLM_AWS/
├── domain/                 # Domain Layer (Entities & Interfaces)
│   ├── entities.py        # Business objects
│   └── repositories.py    # Repository interfaces
│
├── infrastructure/         # Infrastructure Layer (Implementations)
│   ├── short_memory_repo.py   # DynamoDB implementation
│   ├── long_memory_repo.py    # Qdrant long memory
│   ├── vector_db_repo.py      # Qdrant vector DB
│   └── llm_service.py          # Gemini LLM
│
├── langgraph_agent/       # LangGraph Orchestration
│   ├── agent_state.py     # State definition
│   └── agent_graph.py     # Workflow graph
│
├── application/           # Application Layer (Use Cases)
│   └── chat_usecase.py    # Chat business logic
│
├── presentation/          # Presentation Layer (API)
│   └── chat_controller.py # FastAPI endpoints
│
├── jwt_auth.py           # JWT authentication
└── main.py               # Application entry point
```

## 🔄 LangGraph Workflow

```
┌─────────────────────┐
│  fetch_short_memory │ ← Lấy lịch sử chat từ DynamoDB
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  fetch_long_memory  │ ← Tìm kiếm ký ức dài hạn từ Qdrant
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  search_vector_db   │ ← Tìm kiếm knowledge base
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   build_context     │ ← Xây dựng context từ tất cả nguồn
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ generate_response   │ ← Generate response từ Gemini
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   save_memories     │ ← Lưu vào short & long memory
└─────────────────────┘
```

## 🚀 Cài đặt

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Tạo file .env (optional)
cp .env.example .env

# 3. Chạy server với uvicorn (Port 7000)

# Windows - Batch Script
start_server.bat

# Windows - PowerShell
.\start_server.ps1

# Python Script (Cross-platform)
python run_server.py

# Hoặc chạy trực tiếp
python -m LLM_AWS.main

# Hoặc với uvicorn command
uvicorn LLM_AWS.main:app --reload --port 7000
```

## 🌐 Access Points

Sau khi chạy server, truy cập:

- **API Base**: http://localhost:7000
- **Swagger UI**: http://localhost:7000/docs
- **ReDoc**: http://localhost:7000/redoc
- **Health Check**: http://localhost:7000/health

## 📝 Environment Variables

Tạo file `.env` (hoặc sử dụng giá trị mặc định trong code):

```env
# AWS
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=ap-southeast-1

# Qdrant
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key

# Gemini
GEMINI_API_KEY=your_gemini_key

# Vector DB Collection
VECTOR_COLLECTION=nfl_wiki_gemini_3072
```

## 🔐 Authentication

API sử dụng JWT authentication qua header `X-User-Authorization`:

```bash
curl -X POST http://localhost:7000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "X-User-Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "session_id": "session_123",
    "message": "Hello, how are you?"
  }'
```

## 📡 API Endpoints

### POST /api/chat/

Chat với AI agent.

**Request:**
```json
{
  "session_id": "session_123",
  "message": "What is NFL?"
}
```

**Response:**
```json
{
  "message": "NFL stands for National Football League...",
  "sources": [
    "https://en.wikipedia.org/wiki/NFL"
  ],
  "used_short_memory": true,
  "used_long_memory": true,
  "used_vector_db": true
}
```

### GET /health

Kiểm tra health của services.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "short_memory": "DynamoDB",
    "long_memory": "Qdrant",
    "vector_db": "Qdrant",
    "llm": "Gemini"
  }
}
```

## 🧪 Testing

```bash
# Test với curl
curl -X POST http://localhost:7000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "X-User-Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyJ9.xxx" \
  -d '{
    "session_id": "test_session",
    "message": "Tell me about NFL"
  }'

# Hoặc dùng test script
python test_chat.py
```

## 🎯 Features

- ✅ **Clean Architecture** - Tách biệt rõ ràng các layer
- ✅ **LangGraph** - Orchestration workflow với state management
- ✅ **Short Memory** - Lịch sử chat gần đây (DynamoDB)
- ✅ **Long Memory** - Ký ức dài hạn với semantic search (Qdrant)
- ✅ **Vector DB** - Knowledge base với RAG (Qdrant)
- ✅ **JWT Auth** - Xác thực người dùng
- ✅ **Dependency Injection** - Dễ dàng test và maintain
- ✅ **Type Safety** - Sử dụng TypedDict và Pydantic

## 📚 Tech Stack

- **Framework**: FastAPI
- **LLM**: Google Gemini
- **Short Memory**: AWS DynamoDB
- **Long Memory**: Qdrant Vector DB
- **Vector DB**: Qdrant Vector DB
- **Orchestration**: LangGraph
- **Auth**: JWT (PyJWT)

## 🔧 Development

```bash
# Run with auto-reload
python run_server.py

# Hoặc với uvicorn trực tiếp
uvicorn LLM_AWS.main:app --reload --port 7000

# Access API docs
open http://localhost:7000/docs

# Access ReDoc
open http://localhost:7000/redoc
```

## 📖 Documentation

- API Documentation: http://localhost:7000/docs
- ReDoc: http://localhost:7000/redoc
- Health Check: http://localhost:7000/health

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License
