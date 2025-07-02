from sqlalchemy.orm import Session
from app.models import User, ApiKey
from app.schemas import UserCreate, ApiKeyCreate
from app.auth import get_password_hash, generate_api_key

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_api_keys(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ApiKey).offset(skip).limit(limit).all()

def get_api_key(db: Session, api_key_id: int):
    return db.query(ApiKey).filter(ApiKey.id == api_key_id).first()

def create_api_key(db: Session, api_key: ApiKeyCreate):
    generated_key = generate_api_key()
    db_api_key = ApiKey(key_name=api_key.key_name, api_key=generated_key)
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

def update_api_key(db: Session, api_key_id: int, is_active: bool):
    db_api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if db_api_key:
        db_api_key.is_active = is_active
        db.commit()
        db.refresh(db_api_key)
    return db_api_key

def delete_api_key(db: Session, api_key_id: int):
    db_api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if db_api_key:
        db.delete(db_api_key)
        db.commit()
    return db_api_key 