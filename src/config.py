import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "FastAPI Project"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8040
    RELOAD: bool = True

    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_POOL_SIZE: int = 10

    # 会话配置
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "your-session-secret-key")
    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_EXPIRE_SECONDS: int = 3600  # 1小时

    # 外部登录服务配置
    EXTERNAL_AUTH_URL: str = os.getenv("EXTERNAL_AUTH_URL", "")
    EXTERNAL_CLIENT_ID: str = os.getenv("EXTERNAL_CLIENT_ID")
    EXTERNAL_CLIENT_SECRET: str = os.getenv("EXTERNAL_CLIENT_SECRET")
    EXTERNAL_REDIRECT_URI: str = os.getenv("EXTERNAL_REDIRECT_URI", "http://localhost:8000/api/v1/auth/callback")
    EXTERNAL_SCOPE: str = "openid profile email"

    # CORS配置
    BACKEND_CORS_ORIGINS: list = ["*"]

    # 环境
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()