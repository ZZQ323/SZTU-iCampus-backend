from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, admin, schedule, exams, library, simple, notices, events

api_router = APIRouter()

# 简化API - 专为微信小程序优化 🚀 新增
api_router.include_router(simple.router, prefix="/simple", tags=["微信小程序API"])

# 原有API - 兼容保留
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
api_router.include_router(exams.router, prefix="/exams", tags=["exams"])
api_router.include_router(library.router, prefix="/library", tags=["library"])

# 新增API - 通知和事件
api_router.include_router(notices.router, prefix="/notices", tags=["notices"])
api_router.include_router(events.router, prefix="/events", tags=["events"]) 