# 🚀 Quick Start Guide

## Bước 1: Cài đặt Dependencies

```bash
cd LLM_AWS
pip install -r requirements.txt
```

## Bước 2: Chạy Server

```bash
# Cách 1: Dùng script (Khuyến nghị)
python run_server.py

# Cách 2: Chạy trực tiếp
python -m LLM_AWS.main

# Cách 3: Dùng uvicorn command
uvicorn LLM_AWS.main:app --reload --port 7000 --host 0.0.0.0
```

Bạn sẽ thấy:
```
======================================================================
🚀 AI Chat API Server - Clean Architecture + LangGraph
======================================================================
📍 Server URL:      http://localhost:7000
📚 Swagger UI:      http://localhost:7000/docs
📖 ReDoc:           http://localhost:7000/redoc
💚 Health Check:    http://localhost:7000/health
🔧 Auto-reload:     Enabled
======================================================================
```

## Bước 3: Truy cập Swagger UI

Mở trình duyệt và vào: **http://localhost:7000/docs**

Bạn sẽ thấy giao diện Swagger với:
- ✅ POST `/api/chat/` - Chat endpoint
- ✅ GET `/` - Root endpoint
- ✅ GET `/health` - Health check

## Bước 4: Test API

### Option 1: Dùng Swagger UI

1. Mở http://localhost:7000/docs
2. Click vào `POST /api/chat/`
3. Click "Try it out"
4. Nhập:
   - **X-User-Authorization**: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyJ9.xxx`
   - **Request body**:
     ```json
     {
       "session_id": "test_session",
       "message": "Hello!"
     }
     ```
5. Click "Execute"

### Option 2: Dùng curl

```bash
curl -X POST http://localhost:7000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "X-User-Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyJ9.xxx" \
  -d '{
    "session_id": "test_session",
    "message": "Hello, how are you?"
  }'
```

### Option 3: Dùng Test Script

```bash
python test_chat.py
```

## Bước 5: Kiểm tra Health

```bash
curl http://localhost:7000/health
```

Response:
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

## 🔑 Tạo JWT Token để Test

Nếu bạn cần tạo JWT token mới:

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "MY_SUPER_SECRET_KEY_1234567890ABCDEF"
user_id = "your_user_id"

payload = {
    "sub": user_id,
    "exp": datetime.utcnow() + timedelta(hours=24)
}

token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
print(f"Bearer {token}")
```

## 📊 Monitoring Logs

Khi server chạy, bạn sẽ thấy logs chi tiết:

```
🚀 Initializing application...
📦 Creating repositories...
🤖 Creating LangGraph agent...
💼 Creating use cases...
🌐 Creating FastAPI app...
🔌 Registering routers...
✅ Application initialized successfully!

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7000
```

Khi có request:
```
🚀 Starting chat for user: user_123
==================================================
📝 Fetching short memory...
🧠 Searching long memory...
🔍 Searching vector database...
🔨 Building context...
🤖 Generating AI response...
💾 Saving to memories...
✅ Saved to short memory
✅ Saved to long memory
==================================================
✅ Chat completed
==================================================
```

## 🛑 Dừng Server

Nhấn `Ctrl + C` trong terminal

## ⚙️ Configuration

Nếu muốn thay đổi cấu hình, tạo file `.env`:

```bash
cp .env.example .env
```

Sau đó chỉnh sửa các giá trị trong `.env`:
- AWS credentials
- Qdrant URL & API key
- Gemini API key
- Vector collection name

## 🐛 Troubleshooting

### Lỗi: Port 7000 đã được sử dụng

```bash
# Tìm process đang dùng port 7000
# Windows
netstat -ano | findstr :7000

# Kill process
taskkill /PID <PID> /F

# Hoặc đổi port trong run_server.py
```

### Lỗi: Module not found

```bash
# Đảm bảo đang ở thư mục gốc
cd /path/to/Bookies_Website

# Cài lại dependencies
pip install -r LLM_AWS/requirements.txt
```

### Lỗi: JWT Invalid

- Kiểm tra SECRET_KEY trong `jwt_auth.py` và script tạo token phải giống nhau
- Đảm bảo token chưa hết hạn (exp)

## 📚 Next Steps

1. Đọc [README.md](README.md) để hiểu chi tiết về architecture
2. Đọc [ARCHITECTURE.md](ARCHITECTURE.md) để hiểu workflow
3. Xem code trong các folder:
   - `domain/` - Business logic
   - `infrastructure/` - External services
   - `langgraph_agent/` - Workflow orchestration
   - `application/` - Use cases
   - `presentation/` - API controllers

## 🎉 Done!

Bây giờ bạn đã có một AI Chat API hoàn chỉnh với:
- ✅ Clean Architecture
- ✅ LangGraph workflow
- ✅ Short & Long Memory
- ✅ Vector Database (RAG)
- ✅ JWT Authentication
- ✅ Swagger UI

Happy coding! 🚀
