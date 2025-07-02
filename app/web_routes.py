from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import User, ApiKey, ApiRequestLog
from app.auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from app.crud import create_user, get_api_keys, create_api_key, update_api_key, delete_api_key, get_user
from app.schemas import UserCreate, ApiKeyCreate
from datetime import timedelta, datetime, date
from sqlalchemy import func, and_
import os

router = APIRouter(tags=["web"])

# Templates
templates = Jinja2Templates(directory="app/templates")

# Session storage (in production, use Redis or database)
sessions = {}

def get_session_user(request: Request) -> Optional[User]:
    session_token = request.cookies.get("session_token")
    if session_token and session_token in sessions:
        return sessions[session_token]
    return None

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get statistics
    total_api_keys = db.query(ApiKey).count()
    active_api_keys = db.query(ApiKey).filter(ApiKey.is_active == True).count()
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Get recent activity (last 5 API keys with recent usage)
    recent_activity = db.query(ApiKey).order_by(ApiKey.last_used.desc()).limit(5).all()

    # Count API requests today
    today = date.today()
    requests_today = db.query(func.count()).select_from(ApiRequestLog).filter(
        func.date(ApiRequestLog.timestamp) == today
    ).scalar()

    stats = {
        "total_api_keys": total_api_keys,
        "active_api_keys": active_api_keys,
        "total_users": total_users,
        "active_users": active_users,
        "requests_today": requests_today,
        "requests_increase": 0  # Placeholder
    }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_user": user,
        "stats": stats,
        "recent_activity": recent_activity
    })

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password"
        })
    
    # Create session
    import secrets
    session_token = secrets.token_urlsafe(32)
    sessions[session_token] = user
    
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=3600)
    return response

@router.get("/logout")
async def logout(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token in sessions:
        del sessions[session_token]
    
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session_token")
    return response

@router.get("/api-keys", response_class=HTMLResponse)
async def api_keys_page(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    api_keys = get_api_keys(db)
    return templates.TemplateResponse("api_keys.html", {
        "request": request,
        "current_user": user,
        "api_keys": api_keys
    })

@router.post("/api-keys")
async def create_api_key_web(
    request: Request,
    key_name: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        api_key_data = ApiKeyCreate(key_name=key_name)
        new_api_key = create_api_key(db, api_key_data)
        return RedirectResponse(url="/api-keys?message=API key created successfully", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/api-keys?error={str(e)}", status_code=302)

@router.put("/api-keys/{api_key_id}")
async def update_api_key_web(
    api_key_id: int,
    request: Request,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    user = get_session_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    is_active = data.get("is_active")
    db_api_key = update_api_key(db, api_key_id, is_active)
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"message": "API key updated successfully"}

@router.delete("/api-keys/{api_key_id}")
async def delete_api_key_web(
    api_key_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_session_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db_api_key = delete_api_key(db, api_key_id)
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"message": "API key deleted successfully"}

@router.get("/users", response_class=HTMLResponse)
async def users_page(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    users = db.query(User).all()
    return templates.TemplateResponse("users.html", {
        "request": request,
        "current_user": user,
        "users": users
    })

@router.post("/users")
async def create_user_web(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        user_data = UserCreate(username=username, password=password)
        new_user = create_user(db, user_data)
        return RedirectResponse(url="/users?message=User created successfully", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/users?error={str(e)}", status_code=302) 