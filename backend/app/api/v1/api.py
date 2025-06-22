from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, simple, stream
# 暂时注释掉使用SQLAlchemy的模块，等后续修复
# from app.api.v1.endpoints import admin, schedule, exams, library, notices, events

api_router = APIRouter()

# 简化API - 专为微信小程序优化 🚀 新增
api_router.include_router(simple.router, prefix="/simple", tags=["微信小程序API"])

# 流式推送API - 事件驱动推送 🚀 新增
api_router.include_router(stream.router, prefix="/stream", tags=["流式推送"])

# 原有API - 兼容保留（已修复的模块）
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# 暂时注释掉，等待修复SQLAlchemy依赖
# api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
# api_router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
# api_router.include_router(exams.router, prefix="/exams", tags=["exams"])
# api_router.include_router(library.router, prefix="/library", tags=["library"])
# api_router.include_router(notices.router, prefix="/notices", tags=["notices"])
# api_router.include_router(events.router, prefix="/events", tags=["events"]) 