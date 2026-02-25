"""
Script để chạy server với uvicorn
"""
import uvicorn

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 AI Chat API Server - Clean Architecture + LangGraph")
    print("="*70)
    print(f"📍 Server URL:      http://localhost:7000")
    print(f"📚 Swagger UI:      http://localhost:7000/docs")
    print(f"📖 ReDoc:           http://localhost:7000/redoc")
    print(f"💚 Health Check:    http://localhost:7000/health")
    print(f"🔧 Auto-reload:     Enabled")
    print("="*70)
    print("\n💡 Tip: Nhấn Ctrl+C để dừng server\n")
    
    uvicorn.run(
        "LLM_AWS.main:app",
        host="0.0.0.0",
        port=7000,
        reload=True,
        log_level="info",
        access_log=True
    )
