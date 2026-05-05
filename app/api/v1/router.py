from fastapi import APIRouter
from app.api.v1.endpoints import auth, notifications

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
