from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.database import get_db
from app.auth import verify_api_key
from app.ollama_proxy import OllamaProxy
import json

router = APIRouter(prefix="/api", tags=["ollama"])

# Initialize Ollama proxy
ollama_proxy = OllamaProxy()

def get_api_key_header(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "X-API-Key"},
        )
    return x_api_key

def verify_api_key_dependency(api_key: str = Depends(get_api_key_header), db: Session = Depends(get_db)):
    db_api_key = verify_api_key(api_key, db)
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "X-API-Key"},
        )
    return db_api_key

@router.get("/tags")
async def list_models(api_key: str = Depends(verify_api_key_dependency)):
    """List available models"""
    response, status_code = await ollama_proxy.list_models()
    return response

@router.post("/generate")
async def generate_text(
    data: Dict[str, Any],
    api_key: str = Depends(verify_api_key_dependency)
):
    """Generate text using a model"""
    response, status_code = await ollama_proxy.generate(data)
    return response

@router.post("/chat")
async def chat_with_model(
    data: Dict[str, Any],
    api_key: str = Depends(verify_api_key_dependency)
):
    """Chat with a model"""
    response, status_code = await ollama_proxy.chat(data)
    return response

@router.post("/pull")
async def pull_model(
    data: Dict[str, Any],
    api_key: str = Depends(verify_api_key_dependency)
):
    """Pull a model"""
    response, status_code = await ollama_proxy.pull_model(data)
    return response

@router.post("/push")
async def push_model(
    data: Dict[str, Any],
    api_key: str = Depends(verify_api_key_dependency)
):
    """Push a model"""
    response, status_code = await ollama_proxy.push_model(data)
    return response

@router.post("/create")
async def create_model(
    data: Dict[str, Any],
    api_key: str = Depends(verify_api_key_dependency)
):
    """Create a model"""
    response, status_code = await ollama_proxy.create_model(data)
    return response

@router.delete("/delete")
async def delete_model(
    data: Dict[str, Any],
    api_key: str = Depends(verify_api_key_dependency)
):
    """Delete a model"""
    response, status_code = await ollama_proxy.delete_model(data.get("name"))
    return response

@router.post("/show")
async def show_model(
    data: Dict[str, Any],
    api_key: str = Depends(verify_api_key_dependency)
):
    """Show model information"""
    response, status_code = await ollama_proxy.show_model(data)
    return response 