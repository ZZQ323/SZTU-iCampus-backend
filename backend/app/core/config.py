"""
核心配置文件
"""
import os
from pathlib import Path
from typing import List, Optional
from pydantic import validator, AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SZTU-iCampus"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sztu-icamp-secret-key-2024-very-secure")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    ALGORITHM: str = "HS256"
    
    # 🔄 数据服务配置（恢复启用）
    DATA_SERVICE_ENABLED: bool = True  # 重新启用数据服务调用
    DATA_SERVICE_URL: str = os.getenv("DATA_SERVICE_URL", "http://127.0.0.1:8001")
    DATA_SERVICE_API_KEY: str = "sztu-data-service-key-2024"
    DATA_SERVICE_TIMEOUT: int = 30
    
    # 数据库配置（保留用于健康检查）
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data-service/sztu_campus.db")
    
    # Mock数据配置
    USE_MOCK_DATA: bool = False  # 使用真实数据服务数据
    
    # Redis配置（缓存）
    REDIS_URL: str = "redis://localhost:6379/1"
    CACHE_EXPIRE_SECONDS: int = 300  # 缓存过期时间5分钟
    
    # 流式推送配置
    SSE_ENABLED: bool = True  # SSE推送开关
    SSE_HEARTBEAT_INTERVAL: int = 30  # 心跳间隔（秒）
    SSE_RETRY_INTERVAL: int = 5000  # 客户端重连间隔（毫秒）
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
        "https://localhost",
        "https://localhost:8080", 
        "https://localhost:3000",
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 微信小程序配置
    WECHAT_APP_ID: Optional[str] = os.getenv("WECHAT_APP_ID")
    WECHAT_APP_SECRET: Optional[str] = os.getenv("WECHAT_APP_SECRET")
    
    # 监控配置
    METRICS_ENABLED: bool = True
    HEALTH_CHECK_INTERVAL: int = 60  # 健康检查间隔（秒）
    
    # 文件上传配置
    UPLOAD_PATH: str = os.getenv("UPLOAD_PATH", "uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局设置实例
settings = Settings()

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

# 确保必要的目录存在
def ensure_directories():
    """确保必要的目录存在"""
    
    # 创建日志目录
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建上传目录
    upload_dir = Path(settings.UPLOAD_PATH)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 日志目录: {log_dir.absolute()}")
    print(f"📁 上传目录: {upload_dir.absolute()}")
    print(f"🔗 数据服务: {settings.DATA_SERVICE_URL}")
    print(f"✅ 配置加载完成")

# 在导入时确保目录存在
ensure_directories() 