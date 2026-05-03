from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime

