from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.database import get_db
from app.auth import verify_bearer_token
from app.ollama_proxy import OllamaProxy
from app.models import ApiRequestLog
import json

router = APIRouter(prefix="/api", tags=["ollama"])

# Initialize Ollama proxy
ollama_proxy = OllamaProxy()

def log_api_request(db, api_key_obj, endpoint: str):
    log = ApiRequestLog(api_key_id=api_key_obj.id, endpoint=endpoint)
    db.add(log)
    db.commit()

def get_bearer_token(credentials: str = Depends(HTTPBearer())):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

def verify_bearer_token_dependency(token: str = Depends(get_bearer_token), db: Session = Depends(get_db)):
    db_api_key = verify_bearer_token(token, db)
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_api_key

@router.get("/tags")
async def list_models(api_key_obj = Depends(verify_bearer_token_dependency), db: Session = Depends(get_db)):
    log_api_request(db, api_key_obj, "/api/tags")
    response, status_code = await ollama_proxy.list_models()
    return response

@router.post("/generate")
async def generate_text(
    data: Dict[str, Any],
    api_key_obj = Depends(verify_bearer_token_dependency),
    db: Session = Depends(get_db)
):
    log_api_request(db, api_key_obj, "/api/generate")
    response, status_code = await ollama_proxy.generate(data)
    return response

@router.post("/chat")
async def chat_with_model(
    data: Dict[str, Any],
    api_key_obj = Depends(verify_bearer_token_dependency),
    db: Session = Depends(get_db)
):
    log_api_request(db, api_key_obj, "/api/chat")
    response, status_code = await ollama_proxy.chat(data)
    return response

@router.post("/pull")
async def pull_model(
    data: Dict[str, Any],
    api_key_obj = Depends(verify_bearer_token_dependency),
    db: Session = Depends(get_db)
):
    log_api_request(db, api_key_obj, "/api/pull")
    response, status_code = await ollama_proxy.pull_model(data)
    return response

@router.post("/push")
async def push_model(
    data: Dict[str, Any],
    api_key_obj = Depends(verify_bearer_token_dependency),
    db: Session = Depends(get_db)
):
    log_api_request(db, api_key_obj, "/api/push")
    response, status_code = await ollama_proxy.push_model(data)
    return response

@router.post("/create")
async def create_model(
    data: Dict[str, Any],
    api_key_obj = Depends(verify_bearer_token_dependency),
    db: Session = Depends(get_db)
):
    log_api_request(db, api_key_obj, "/api/create")
    response, status_code = await ollama_proxy.create_model(data)
    return response

@router.delete("/delete")
async def delete_model(
    data: Dict[str, Any],
    api_key_obj = Depends(verify_bearer_token_dependency),
    db: Session = Depends(get_db)
):
    log_api_request(db, api_key_obj, "/api/delete")
    response, status_code = await ollama_proxy.delete_model(data.get("name"))
    return response

@router.post("/show")
async def show_model(
    data: Dict[str, Any],
    api_key_obj = Depends(verify_bearer_token_dependency),
    db: Session = Depends(get_db)
):
    log_api_request(db, api_key_obj, "/api/show")
    response, status_code = await ollama_proxy.show_model(data)
    return response 