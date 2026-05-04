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
@limiter.limit("3/minute")
def me(request: Request, current_user: User = Depends(get_current_user)):
    return current_user