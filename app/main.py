from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models import Base, User, ApiKey, ApiRequestLog
from app.api_routes import router as api_router
from app.admin_routes import router as admin_router
from app.web_routes import router as web_router
from app.crud import create_user
from app.schemas import UserCreate
import os
import logging

# Configure logging based on environment
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

if not DEBUG:
    # Suppress bcrypt warnings in production
    logging.getLogger("passlib").setLevel(logging.ERROR)
    # Suppress other verbose logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ollama API Middleware",
    description="A middleware service that adds API key authentication to Ollama",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)
app.include_router(admin_router)
app.include_router(web_router)

@app.on_event("startup")
async def startup_event():
    """Initialize the application with a default admin user"""
    db = next(get_db())
    
    # Check if admin user exists
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        # Create default admin user
        admin_data = UserCreate(username="admin", password="admin123")
        create_user(db, admin_data)
        if DEBUG:
            print("Default admin user created: username=admin, password=admin123")
            print("Please change the default password after first login!")
        else:
            print("✅ Application started successfully")
    
    db.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ollama-middleware"}

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom documentation page"""
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 