# ⚡ START HERE - Hướng dẫn chạy nhanh

## ⚠️ QUAN TRỌNG

**Bạn PHẢI chạy từ thư mục gốc `Bookies_Website`, KHÔNG phải từ trong `LLM_AWS`**

## 🚀 Cách chạy đúng

### Bước 1: Mở Terminal/CMD

```bash
# Windows CMD
cd D:\Bookies_Website

# PowerShell
cd D:\Bookies_Website

# Git Bash / Linux / Mac
cd /path/to/Bookies_Website
```

### Bước 2: Chạy server (chọn 1 cách)

```bash
# Cách 1: Python script (KHUYẾN NGHỊ)
python LLM_AWS/run_server.py

# Cách 2: Uvicorn command
uvicorn LLM_AWS.main:app --reload --port 7000

# Cách 3: Module mode
python -m LLM_AWS.main

# Cách 4: Windows Batch
LLM_AWS\start_server.bat

# Cách 5: PowerShell
.\LLM_AWS\start_server.ps1
```

## ✅ Khi thành công

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

## 🌐 Truy cập

Mở trình duyệt:
- **Swagger UI**: http://localhost:7000/docs
- **ReDoc**: http://localhost:7000/redoc
- **Health**: http://localhost:7000/health

## ❌ LỖI THƯỜNG GẶP

### Lỗi: ImportError: attempted relative import with no known parent package

**Nguyên nhân**: Bạn đang chạy từ trong thư mục `LLM_AWS`

**Giải pháp**:
```bash
# SAI ❌
cd D:\Bookies_Website\LLM_AWS
uvicorn main:app --reload --port 7000

# ĐÚNG ✅
cd D:\Bookies_Website
uvicorn LLM_AWS.main:app --reload --port 7000
```

### Lỗi: Module 'LLM_AWS' has no attribute 'main'

**Nguyên nhân**: Thiếu `__init__.py` hoặc import sai

**Giải pháp**: Đảm bảo đang ở thư mục gốc và chạy:
```bash
python LLM_AWS/run_server.py
```

### Lỗi: Port 7000 already in use

**Giải pháp**:
```bash
# Windows - Tìm và kill process
netstat -ano | findstr :7000
taskkill /PID <PID> /F

# Hoặc đổi port
uvicorn LLM_AWS.main:app --reload --port 8000
```

## 📝 Tóm tắt

1. ✅ Mở terminal ở thư mục `Bookies_Website` (gốc)
2. ✅ Chạy: `python LLM_AWS/run_server.py`
3. ✅ Mở: http://localhost:7000/docs
4. ✅ Test API với Swagger UI

## 🆘 Cần trợ giúp?

Đọc thêm:
- [QUICKSTART.md](QUICKSTART.md) - Hướng dẫn chi tiết
- [HOW_TO_RUN.md](HOW_TO_RUN.md) - Các cách chạy khác
- [README.md](README.md) - Documentation đầy đủ
