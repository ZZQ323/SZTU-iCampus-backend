from fastapi import APIRouter

# 导入所有API模块
from app.api.v1.endpoints import (
    auth, users, admin, stream,
    announcements, campus_card, grades, schedule,
    exams, library, events, base, courses, files, reading
)

api_router = APIRouter()

# 注册所有路由，确保完全按照文档规范
api_router.include_router(auth.router, prefix="/auth", tags=["认证模块"])
api_router.include_router(users.router, prefix="/users", tags=["用户模块"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["课程表"])
api_router.include_router(grades.router, prefix="/grades", tags=["成绩查询"])
api_router.include_router(exams.router, prefix="/exams", tags=["考试模块"])
api_router.include_router(library.router, prefix="/library", tags=["图书馆"])
api_router.include_router(campus_card.router, prefix="/campus-card", tags=["校园卡"])
api_router.include_router(announcements.router, prefix="/announcements", tags=["公告模块"])
api_router.include_router(events.router, prefix="/events", tags=["活动模块"])
api_router.include_router(base.router, prefix="/base", tags=["基础数据"])
api_router.include_router(courses.router, prefix="/courses", tags=["课程管理"])
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])
api_router.include_router(reading.router, prefix="/reading", tags=["阅读记录"])
api_router.include_router(stream.router, prefix="/stream", tags=["流式推送"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理员"])

# 其他模块（简化实现）
@api_router.get("/research/projects", tags=["科研管理"])
async def get_research_projects():
    """获取科研项目列表"""
    return {"code": 0, "message": "success", "data": {"projects": []}}

@api_router.get("/assets", tags=["资产管理"])
async def get_assets():
    """获取资产列表"""
    return {"code": 0, "message": "success", "data": {"assets": []}}

@api_router.get("/permissions/network", tags=["权限管理"])
async def get_network_permissions():
    """获取网络权限信息"""
    return {"code": 0, "message": "success", "data": {"permissions": []}}

@api_router.get("/workflows/instances", tags=["工作流"])
async def get_workflow_instances():
    """获取工作流实例列表"""
    return {"code": 0, "message": "success", "data": {"instances": []}}

@api_router.get("/statistics/overview", tags=["统计报表"])
async def get_statistics_overview():
    """获取系统概览统计"""
    return {"code": 0, "message": "success", "data": {"overview": {}}}

# 保留原有的注释供参考
# 剩余功能模块，当前仅保留路由结构，后续逐步实现
# - 科研管理模块 (research)
# - 资产管理模块 (assets)
# - 权限管理模块 (permissions)
# - 工作流模块 (workflows)
# - 统计报表模块 (statistics) 