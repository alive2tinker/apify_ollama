from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, ApiKey
from app.schemas import UserCreate, ApiKeyCreate, ApiKey, Token, User as UserSchema
from app.auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from app.crud import create_user, get_api_keys, create_api_key, update_api_key, delete_api_key
from datetime import timedelta

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", response_model=UserSchema)
async def create_new_user(
    user: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)

@router.get("/api-keys", response_model=List[ApiKey])
async def read_api_keys(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_keys = get_api_keys(db, skip=skip, limit=limit)
    return api_keys

@router.post("/api-keys", response_model=ApiKey)
async def create_new_api_key(
    api_key: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_api_key(db=db, api_key=api_key)

@router.put("/api-keys/{api_key_id}")
async def toggle_api_key(
    api_key_id: int,
    is_active: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_api_key = update_api_key(db=db, api_key_id=api_key_id, is_active=is_active)
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"message": "API key updated successfully"}

@router.delete("/api-keys/{api_key_id}")
async def remove_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_api_key = delete_api_key(db=db, api_key_id=api_key_id)
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"message": "API key deleted successfully"} 