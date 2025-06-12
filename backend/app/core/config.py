from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, EmailStr, validator

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "SZTU iCampus"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT设置
    SECRET_KEY: str = "your-secret-key-here"  # 在生产环境中应该使用环境变量
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 微信小程序设置（测试用）
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""
    
    # 数据库配置
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "sztu_icampus"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./app.db"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 超级管理员配置
    FIRST_SUPERUSER: str = "admin"
    FIRST_SUPERUSER_PASSWORD: str = "admin"

    class Config:
        case_sensitive = True
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )

settings = Settings() 