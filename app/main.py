from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from fastapi.responses import JSONResponse
from app.api.v1.router import router
from app.core.limiter import limiter


app = FastAPI(title="Auth Platform", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test-limit")
@limiter.limit("3/minute")
def test_limit(request: Request):
    return {"ip": request.client.host}