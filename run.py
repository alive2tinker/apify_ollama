#!/usr/bin/env python3
"""
Ollama API Middleware Runner
A simple script to run the FastAPI application
"""

import uvicorn
import socket
import os

def find_available_port(start_port=8000, max_attempts=100):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts}")

if __name__ == "__main__":
    # Check debug mode
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Find available port
    port = find_available_port(8000)
    
    if DEBUG:
        print("🚀 Starting Ollama API Middleware (DEBUG MODE)...")
        print(f"📖 Web UI: http://localhost:{port}")
        print(f"📚 API Docs: http://localhost:{port}/docs")
        print("🔑 Default admin: admin / admin123")
        print("⚠️  Please change the default password after first login!")
        print("-" * 50)
    else:
        print(f"🚀 Ollama API Middleware starting on port {port}")
        print(f"📖 Web UI: http://localhost:{port}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=DEBUG,  # Only enable reload in debug mode
        log_level="debug" if DEBUG else "info"
    ) 