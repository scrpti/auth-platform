from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.core.dependencies import get_current_user
from app.models.user import User
from typing import Dict

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_email: str):
        await websocket.accept()
        if user_email not in self.active_connections:
            self.active_connections[user_email] = []
        self.active_connections[user_email].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_email: str):
        if user_email in self.active_connections:
            self.active_connections[user_email].remove(websocket)
    
    async def send_to_user(self, email: str, message: dict):
        if email in self.active_connections:
            for connection in self.active_connections[email]:
                await connection.send_json(message)
    
    async def broadcast(self, message: dict):
        for connections in self.active_connections.values():
            for connection in connections:
                await connection.send_json(message)


manager = ConnectionManager()

@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    from app.core.security import decode_token
    from app.db.session import SessionLocal

    email = decode_token(token)
    if not email:
        await websocket.close(code=1008)
        return
    
    await manager.connect(websocket, email)
    try:
        await websocket.send_json({
            "type": "connected",
            "message": f"Welcome {email}"
        })
        while True:
            data = await websocket.receive_text()
            await manager.send_to_user(email, {
                "type": "echo",
                "message": data
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, email)

@router.post("/notify/{email}")
async def notify_user(
    email: str,
    message: str,
    current_user: User = Depends(get_current_user)
):
    await manager.send_to_user(email, {
        "type": "notification",
        "message": message,
        "from": current_user.email
    })
    return {"status": "sent"}