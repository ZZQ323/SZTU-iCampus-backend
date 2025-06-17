"""
数据库配置文件
提供数据库连接、会话管理和基础模型定义
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./sztu_icampus.db"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_pre_ping=True  # 添加连接池健康检查
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建基类
Base = declarative_base()

# 获取数据库会话的依赖函数
def get_db():
    """
    获取数据库会话的依赖函数
    用于FastAPI的依赖注入系统
    """
    db = SessionLocal() # 创建一个新的数据库会话
    try:
        yield db # 将会话传递给调用者
    finally:
        db.close() # 请求结束后关闭会话