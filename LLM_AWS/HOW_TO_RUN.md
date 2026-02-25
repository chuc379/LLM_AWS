# 🚀 Hướng dẫn chạy Server

## 📋 Yêu cầu

- Python 3.8+
- pip

## 🎯 Các cách chạy Server (Port 7000)

**⚠️ QUAN TRỌNG: Phải chạy từ thư mục gốc `Bookies_Website`, KHÔNG phải từ trong `LLM_AWS`**

```bash
# Đảm bảo bạn đang ở thư mục gốc
cd D:\Bookies_Website
```

### 1️⃣ Windows - Batch Script (Dễ nhất)

```cmd
cd D:\Bookies_Website
LLM_AWS\start_server.bat
```

### 2️⃣ Windows - PowerShell Script

```powershell
cd D:\Bookies_Website
.\LLM_AWS\start_server.ps1
```

Nếu gặp lỗi execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\LLM_AWS\start_server.ps1
```

### 3️⃣ Python Script (Cross-platform) - KHUYẾN NGHỊ

```bash
cd D:\Bookies_Website
python LLM_AWS/run_server.py
```

### 4️⃣ Module Mode

```bash
cd D:\Bookies_Website
python -m LLM_AWS.main
```

### 5️⃣ Uvicorn Command

```bash
cd D:\Bookies_Website
uvicorn LLM_AWS.main:app --reload --port 7000 --host 0.0.0.0
```

## 🌐 Truy cập Server

Sau khi chạy, mở trình duyệt:

| Service | URL |
|---------|-----|
| 🏠 Home | http://localhost:7000 |
| 📚 Swagger UI | http://localhost:7000/docs |
| 📖 ReDoc | http://localhost:7000/redoc |
| 💚 Health Check | http://localhost:7000/health |

## 🔧 Options

### Chạy với port khác

```bash
# Sửa trong run_server.py hoặc
uvicorn LLM_AWS.main:app --reload --port 8080
```

### Chạy không auto-reload

```bash
uvicorn LLM_AWS.main:app --port 7000
```

### Chạy với log level khác

```bash
uvicorn LLM_AWS.main:app --reload --port 7000 --log-level debug
```

## 🛑 Dừng Server

Nhấn `Ctrl + C` trong terminal

## 📊 Kiểm tra Server đang chạy

### Windows CMD
```cmd
netstat -ano | findstr :7000
```

### Windows PowerShell
```powershell
Get-NetTCPConnection -LocalPort 7000
```

### Linux/Mac
```bash
lsof -i :7000
```

## 🐛 Troubleshooting

### Port 7000 đã được sử dụng

**Windows:**
```cmd
# Tìm PID
netstat -ano | findstr :7000

# Kill process
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Tìm và kill
lsof -ti:7000 | xargs kill -9
```

### Module not found

```bash
# Đảm bảo ở thư mục gốc
cd /path/to/Bookies_Website

# Cài lại dependencies
pip install -r LLM_AWS/requirements.txt
```

### Import errors

```bash
# Thêm thư mục gốc vào PYTHONPATH
# Windows
set PYTHONPATH=%PYTHONPATH%;.

# Linux/Mac
export PYTHONPATH=$PYTHONPATH:.
```

## 📝 Logs

Server sẽ hiển thị logs chi tiết:

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

## 🎉 Success!

Khi thấy message trên, server đã sẵn sàng!

Truy cập Swagger UI để test: **http://localhost:7000/docs**
