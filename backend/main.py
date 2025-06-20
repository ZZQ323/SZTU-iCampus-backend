"""
SZTU-iCampus 胶水层主程序
集成数据服务、缓存、流式推送等功能
"""
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from loguru import logger

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.data_service import init_data_service, close_data_service, data_service
from app.api.v1.api import api_router
from app.api.deps import get_current_user


# 配置日志
def setup_logging():
    """配置日志系统"""
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    
    # 移除默认handler
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # 添加文件输出
    logger.add(
        settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )


# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时的生命周期管理"""
    # 启动时执行
    logger.info("🚀 SZTU-iCampus 胶水层服务启动中...")
    
    # 初始化数据服务客户端
    await init_data_service()
    
    # 检查数据服务连接
    health_status = await data_service.get_health()
    if health_status.get("success", True):
        logger.info("✅ 数据服务连接正常")
    else:
        logger.warning("⚠️ 数据服务连接异常，将使用Mock数据")
    
    logger.info("🎉 胶水层服务启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("🛑 胶水层服务关闭中...")
    await close_data_service()
    logger.info("👋 胶水层服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SZTU-iCampus 校园服务统一入口胶水层",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"全局异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "内部服务器错误", "detail": str(exc) if settings.DEBUG else None}
    )


# === 健康检查和监控接口 ===

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 检查数据服务状态
        data_service_status = await data_service.get_health()
        
        # 检查Redis状态
        redis_status = "ok" if data_service.redis_client else "not_connected"
        
        return {
            "status": "ok",
            "service": "glue-layer",
            "version": settings.APP_VERSION,
            "timestamp": "2024-01-01T00:00:00Z",  # 这里应该使用实际时间
            "dependencies": {
                "data_service": data_service_status.get("status", "error"),
                "redis": redis_status
            }
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "服务不可用"}
        )


@app.get("/metrics")
async def get_metrics():
    """获取系统指标"""
    if not settings.METRICS_ENABLED:
        raise HTTPException(status_code=404, detail="指标监控已禁用")
    
    try:
        # 获取数据服务统计信息
        stats = await data_service.get_stats()
        
        return {
            "service": "glue-layer",
            "timestamp": "2024-01-01T00:00:00Z",
            "data_service_stats": stats,
            "cache_info": {
                "redis_connected": data_service.redis_client is not None
            }
        }
    except Exception as e:
        logger.error(f"获取指标失败: {e}")
        raise HTTPException(status_code=500, detail="获取指标失败")


# === 流式推送接口 ===

@app.get("/stream/events")
async def stream_events(user=Depends(get_current_user)):
    """SSE流式事件推送"""
    if not settings.SSE_ENABLED:
        raise HTTPException(status_code=404, detail="流式推送已禁用")
    
    async def event_generator():
        """事件生成器"""
        try:
            # 发送连接确认
            yield f"data: {{'type': 'connected', 'message': '连接成功', 'user_id': {user.get('id', 0)}}}\n\n"
            
            # 获取数据服务的流式推送
            async for line in data_service.stream_notifications():
                yield f"{line}\n\n"
                
        except Exception as e:
            logger.error(f"SSE推送异常: {e}")
            yield f"data: {{'type': 'error', 'message': '推送异常'}}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
        }
    )


# === 数据代理接口 ===

@app.get("/api/data/persons")
async def get_persons_proxy(
    role: str = None,
    page: int = 1,
    limit: int = 20,
    search: str = None,
    user=Depends(get_current_user)
):
    """人员数据代理接口"""
    try:
        result = await data_service.get_persons(
            role=role,
            page=page,
            limit=limit,
            search=search
        )
        return result
    except Exception as e:
        logger.error(f"获取人员数据失败: {e}")
        raise HTTPException(status_code=500, detail="获取人员数据失败")


@app.get("/api/data/courses")
async def get_courses_proxy(
    semester: str = None,
    teacher_id: int = None,
    page: int = 1,
    limit: int = 20,
    user=Depends(get_current_user)
):
    """课程数据代理接口"""
    try:
        result = await data_service.get_courses(
            semester=semester,
            teacher_id=teacher_id,
            page=page,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"获取课程数据失败: {e}")
        raise HTTPException(status_code=500, detail="获取课程数据失败")


@app.get("/api/data/announcements")
async def get_announcements_proxy(
    page: int = 1,
    limit: int = 10,
    category: str = None,
    user=Depends(get_current_user)
):
    """公告数据代理接口"""
    try:
        result = await data_service.get_announcements(
            page=page,
            limit=limit,
            category=category
        )
        return result
    except Exception as e:
        logger.error(f"获取公告数据失败: {e}")
        raise HTTPException(status_code=500, detail="获取公告数据失败")


@app.get("/api/data/schedule/{user_id}")
async def get_user_schedule_proxy(
    user_id: int,
    semester: str,
    current_user=Depends(get_current_user)
):
    """用户课表代理接口"""
    # 权限检查：只能查看自己的课表或管理员可以查看所有
    if current_user.get("id") != user_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    try:
        result = await data_service.get_user_schedule(user_id, semester)
        return result
    except Exception as e:
        logger.error(f"获取用户课表失败: {e}")
        raise HTTPException(status_code=500, detail="获取用户课表失败")


# === 缓存管理接口 ===

@app.delete("/api/cache/user/{user_id}")
async def clear_user_cache(
    user_id: int,
    current_user=Depends(get_current_user)
):
    """清除用户缓存"""
    # 权限检查
    if current_user.get("role") not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="权限不足")
    
    try:
        await data_service.invalidate_user_cache(user_id)
        return {"success": True, "message": f"用户 {user_id} 缓存已清理"}
    except Exception as e:
        logger.error(f"清理用户缓存失败: {e}")
        raise HTTPException(status_code=500, detail="清理缓存失败")


# === 配置管理接口 ===

@app.get("/api/config")
async def get_config(user=Depends(get_current_user)):
    """获取客户端配置"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    return {
        "data_service_enabled": settings.DATA_SERVICE_ENABLED,
        "sse_enabled": settings.SSE_ENABLED,
        "cache_expire_seconds": settings.CACHE_EXPIRE_SECONDS,
        "debug": settings.DEBUG,
        "version": settings.APP_VERSION
    }


@app.post("/api/config/toggle")
async def toggle_config(
    config_name: str,
    enabled: bool,
    user=Depends(get_current_user)
):
    """切换配置开关（仅限管理员）"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 这里可以实现配置的动态切换
    # 实际项目中需要持久化配置更改
    
    return {
        "success": True,
        "message": f"配置 {config_name} 已{'启用' if enabled else '禁用'}"
    }


# 挂载API路由
app.include_router(api_router, prefix="/api/v1")

# 静态文件服务（如果需要）
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    # 配置日志
    setup_logging()
    
    # 启动服务
    logger.info(f"🚀 启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📊 数据服务: {'启用' if settings.DATA_SERVICE_ENABLED else '禁用'}")
    logger.info(f"📡 流式推送: {'启用' if settings.SSE_ENABLED else '禁用'}")
    logger.info(f"💾 Redis缓存: {settings.REDIS_URL}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 