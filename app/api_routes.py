from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.database import get_db
from app.auth import verify_bearer_token
from app.ollama_proxy import OllamaProxy
from app.models import ApiRequestLog
from fastapi.responses import JSONResponse
import uuid
import time
import json

router = APIRouter(tags=["openai-compatible"])

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

# OpenAI-compatible /v1/models endpoint
@router.get("/v1/models")
async def openai_models(
    api_key_obj = Depends(verify_bearer_token_dependency),
    db: Session = Depends(get_db)
):
    log_api_request(db, api_key_obj, "/v1/models")
    ollama_response, _ = await ollama_proxy.list_models()
    # Map Ollama response to OpenAI models format
    models = ollama_response.get("models", [])
    openai_models = [
        {
            "id": m.get("name"),
            "object": "model",
            "created": int(time.time()),
            "owned_by": "ollama"
        } for m in models
    ]
    return JSONResponse(content={"object": "list", "data": openai_models})

# OpenAI-compatible /v1/completions endpoint
@router.post("/v1/completions")
async def openai_completions(
    request: Dict[str, Any],
    api_key_obj = Depends(verify_bearer_token_dependency),
    db: Session = Depends(get_db)
):
    log_api_request(db, api_key_obj, "/v1/completions")
    ollama_req = {
        "model": request.get("model"),
        "prompt": request.get("prompt"),
        "stream": False
    }
    ollama_response, _ = await ollama_proxy.generate(ollama_req)
    openai_resp = {
        "id": f"cmpl-{uuid.uuid4().hex}",
        "object": "text_completion",
        "created": int(time.time()),
        "model": request.get("model"),
        "choices": [
            {
                "text": ollama_response.get("response", ""),
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": ollama_response.get("prompt_eval_count", 0),
            "completion_tokens": ollama_response.get("eval_count", 0),
            "total_tokens": ollama_response.get("prompt_eval_count", 0) + ollama_response.get("eval_count", 0)
        }
    }
    return JSONResponse(content=openai_resp)

# OpenAI-compatible /v1/chat/completions endpoint
@router.post("/v1/chat/completions")
async def openai_chat_completions(
    request: Dict[str, Any],
    api_key_obj = Depends(verify_bearer_token_dependency),
    db: Session = Depends(get_db)
):
    log_api_request(db, api_key_obj, "/v1/chat/completions")
    ollama_req = {
        "model": request.get("model"),
        "messages": request.get("messages"),
        "stream": False
    }
    ollama_response, _ = await ollama_proxy.chat(ollama_req)
    openai_resp = {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.get("model"),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": ollama_response.get("message", {}).get("content", "") or ollama_response.get("response", "")
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": ollama_response.get("prompt_eval_count", 0),
            "completion_tokens": ollama_response.get("eval_count", 0),
            "total_tokens": ollama_response.get("prompt_eval_count", 0) + ollama_response.get("eval_count", 0)
        }
    }
    return JSONResponse(content=openai_resp) 