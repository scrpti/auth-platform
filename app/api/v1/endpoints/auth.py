from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, create_refresh_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import authenticate_user, create_user, get_user_by_email
from app.core.limiter import limiter
from app.core.cache import cache
from app.tasks import generate_report

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, data.email): #If mail already is registered we raise an error
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, data)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)
    if not user:#If we dont obtain user we couldnt find the credentials so we raise an error
        raise HTTPException(status_code=401, detail="Bad credentials")
    return TokenResponse(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )

@router.get("/me", response_model=UserResponse)
@limiter.limit("60/minute")
def me(request: Request, current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/profile/{user_id}")
@limiter.limit("30/minute")
def get_profile(request: Request, user_id: str, db: Session = Depends(get_db)):
    return _get_profile_cached(user_id, db)

@cache(expire=30)
def _get_profile_cached(user_id:str, db):
    import time
    time.sleep(1)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
    }

@router.post("/report")
@limiter.limit("5/minute")
def request_report(request: Request, current_user: User = Depends(get_current_user)):
    task = generate_report.delay(str(current_user.id))
    return {
        "message": "Reporte en proceso",
        "task_id": task.id
    }

@router.get("/report/{task_id}")
@limiter.limit("30/minute")
def get_report_status(request: Request, task_id: str, current_user: User = Depends(get_current_user)):
    from app.core.celery_app import celery_app
    task = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }