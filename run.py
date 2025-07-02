#!/usr/bin/env python3
"""
Ollama API Middleware Runner
A simple script to run the FastAPI application
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting Ollama API Middleware...")
    print("📖 Web UI: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔑 Default admin: admin / admin123")
    print("⚠️  Please change the default password after first login!")
    print("-" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 