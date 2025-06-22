"""
SZTU-iCampus 胶水层主应用
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from app.core.config import settings
from app.api.v1.api import api_router

# 配置简单的logging（避免colorama问题）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info(f"🚀 {settings.PROJECT_NAME} v{settings.PROJECT_VERSION} 启动中...")
    logger.info(f"📊 DEBUG模式: {settings.DEBUG}")
    logger.info(f"🗄️  数据库路径: {settings.DATABASE_PATH}")
    
    # 初始化事件推送系统
    try:
        from app.core.events import start_event_system
        await start_event_system()
        logger.info("✅ 事件推送系统初始化完成")
    except Exception as e:
        logger.error(f"❌ 事件推送系统初始化失败: {e}")
    
    yield
    
    # 关闭时执行
    logger.info("👋 应用正在关闭...")

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="深圳技术大学智慧校园系统 - 胶水层API服务",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": 1,
            "msg": exc.detail,
            "data": None,
            "timestamp": int(time.time()),
            "version": settings.PROJECT_VERSION
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": 1,
            "msg": "服务器内部错误",
            "data": None,
            "timestamp": int(time.time()),
            "version": settings.PROJECT_VERSION
        }
    )

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 根路径
@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "status": 0,
        "msg": "SZTU-iCampus 胶水层服务正常运行",
        "data": {
            "service": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "debug": settings.DEBUG,
            "docs_url": f"{settings.API_V1_STR}/docs"
        },
        "timestamp": int(time.time()),
        "version": settings.PROJECT_VERSION
    }

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        import sqlite3
        db = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM persons")
        user_count = cursor.fetchone()[0]
        cursor.close()
        db.close()
        
        return {
            "status": 0,
            "msg": "服务健康",
            "data": {
                "database": "connected",
                "user_count": user_count,
                "service": "running"
            },
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": 1,
                "msg": "服务不健康",
                "data": {
                    "database": "disconnected",
                    "error": str(e)
                },
                "timestamp": int(time.time())
            }
        )

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🌟 启动 {settings.PROJECT_NAME} 开发服务器...")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 