# SSE实现 (app/api/v1/notifications.py)
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter()

@router.get("/stream/notifications")
async def notification_stream():
    async def event_generator():
        while True:
            # 获取实时通知数据
            if new_notification := check_new_notifications():
                yield f"data: {json.dumps(new_notification)}\n\n"
            await asyncio.sleep(1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )

# WebSocket实现 (app/api/v1/ws.py)
from fastapi import WebSocket

@router.websocket("/ws/seat-reservation")
async def websocket_seat_updates(websocket: WebSocket):
    await websocket.accept()
    seat_manager.subscribe(websocket)
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except WebSocketDisconnect:
        seat_manager.unsubscribe(websocket)