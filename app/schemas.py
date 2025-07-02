from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ApiKeyBase(BaseModel):
    key_name: str

class ApiKeyCreate(ApiKeyBase):
    pass

class ApiKey(ApiKeyBase):
    id: int
    api_key: str
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 