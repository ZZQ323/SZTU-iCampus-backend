# main.py
from fastapi import FastAPI, Depends, status
from fastapi.responses import StreamingResponse
import json

# ① 引用 core 层
from app.core.config import settings
from app.core.queue import message_queue, notify_clients

# ② 引用 api 层（路由聚合器）
from app.api.v1.api import api_router

# ③ 引用公共依赖（演示如何在自身自定义接口里“串” api.deps 的依赖）
from app.api.deps import get_current_active_user

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# 把 v1 路由全部挂到 /api/v1
app.include_router(api_router, prefix=settings.API_V1_STR)

# ---------- 下面再加两个极简 endpoint，用来展示 core.queue 的用法 ----------

@app.post("/ping", status_code=status.HTTP_202_ACCEPTED)
async def ping():
    """向所有客户端推送一条 'pong' 消息。"""
    await notify_clients({"msg": "pong"})
    return {"detail": "pong queued"}

@app.get("/stream")
async def stream():
    """
    Server-Sent Events 流式接口：持续监听 message_queue，
    每有新消息就通过 SSE 向前端推送。
    """
    async def event_gen():
        while True:
            data = await message_queue.get()
            yield f"data: {json.dumps(data)}\n\n"
    return StreamingResponse(event_gen(), media_type="text/event-stream")


# ---------- 再来一个需要鉴权的接口，演示复用 api.deps ------------

@app.get("/me")
def read_me(current_user=Depends(get_current_active_user)):
    """依赖注入 get_current_active_user -> JWT 校验逻辑藏在 core.security"""
    return {"username": current_user.username, "is_superuser": current_user.is_superuser}
