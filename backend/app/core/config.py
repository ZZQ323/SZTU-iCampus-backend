"""
核心配置文件
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "SZTU-iCampus Glue Layer"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 安全配置
    SECRET_KEY: str = "sztu-icampus-secret-key-2024"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    ALGORITHM: str = "HS256"
    
    # 数据库配置（胶水层轻量级数据库）
    DATABASE_URL: str = "sqlite:///./sztu_icampus.db"
    
    # 数据服务配置 🚀 新增
    DATA_SERVICE_ENABLED: bool = True  # 数据服务开关
    DATA_SERVICE_URL: str = "http://localhost:8001"  # 数据服务地址
    DATA_SERVICE_API_KEY: str = "sztu-data-service-key-2024"  # API密钥
    DATA_SERVICE_TIMEOUT: int = 30  # 请求超时时间
    
    # Mock数据配置
    USE_MOCK_DATA: bool = False  # Mock数据开关，False时使用数据服务
    
    # Redis配置（缓存）
    REDIS_URL: str = "redis://localhost:6379/1"
    CACHE_EXPIRE_SECONDS: int = 300  # 缓存过期时间5分钟
    
    # 流式推送配置
    SSE_ENABLED: bool = True  # SSE推送开关
    SSE_HEARTBEAT_INTERVAL: int = 30  # 心跳间隔（秒）
    SSE_RETRY_INTERVAL: int = 5000  # 客户端重连间隔（毫秒）
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/glue-layer.log"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "https://servicewechat.com",  # 微信小程序域名
    ]
    
    # 微信小程序配置
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""
    
    # 监控配置
    METRICS_ENABLED: bool = True
    HEALTH_CHECK_INTERVAL: int = 60  # 健康检查间隔（秒）
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局设置实例
settings = Settings()

# 数据服务API路径配置
DATA_SERVICE_PATHS = {
    "health": "/health",
    "stats": "/stats",
    "persons": "/persons",
    "courses": "/courses", 
    "grades": "/grades",
    "announcements": "/announcements",
    "notifications": "/notifications",
    "library": "/library",
    "transactions": "/transactions",
    "stream_notifications": "/stream/notifications",
}

# 缓存键配置
CACHE_KEYS = {
    "user_info": "user:{user_id}",
    "course_schedule": "schedule:{user_id}:{semester}",
    "announcements": "announcements:page:{page}",
    "library_info": "library:{user_id}",
    "grades": "grades:{user_id}:{semester}",
    "stats": "stats:general",
}

# 权限配置
PERMISSIONS = {
    "admin": ["read", "write", "delete", "manage"],
    "teacher": ["read", "write"],
    "student": ["read"],
    "guest": [],
}

# 流式推送事件类型
SSE_EVENT_TYPES = {
    "announcement": "新公告",
    "notice": "部门通知", 
    "grade_update": "成绩更新",
    "course_change": "课程变更",
    "library_reminder": "图书到期提醒",
    "system_message": "系统消息",
} 