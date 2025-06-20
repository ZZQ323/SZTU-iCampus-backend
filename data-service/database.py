"""
数据库连接配置和会话管理
"""
import asyncio
from typing import AsyncGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from loguru import logger

from config import settings, DATABASE_CONFIG


# 创建基础模型类
Base = declarative_base()

# 同步数据库引擎
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=DATABASE_CONFIG["echo"],
    pool_size=DATABASE_CONFIG["pool_size"],
    max_overflow=DATABASE_CONFIG["max_overflow"],
    pool_pre_ping=True,  # 连接池预检查
    pool_recycle=3600,   # 连接回收时间（秒）
)

# 异步数据库引擎（用于高性能场景）
async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(
    async_database_url,
    echo=DATABASE_CONFIG["echo"],
    pool_size=DATABASE_CONFIG["pool_size"],
    max_overflow=DATABASE_CONFIG["max_overflow"],
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def get_db() -> Session:
    """
    获取同步数据库会话
    用于普通的CRUD操作
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话
    用于高并发场景
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Async database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


def create_database():
    """
    创建数据库（如果不存在）
    """
    try:
        # 从完整URL中提取数据库名
        db_name = settings.DATABASE_URL.split("/")[-1]
        base_url = settings.DATABASE_URL.rsplit("/", 1)[0]
        
        # 连接到默认的postgres数据库
        temp_engine = create_engine(f"{base_url}/postgres")
        
        with temp_engine.connect() as conn:
            # 设置autocommit模式以执行CREATE DATABASE
            conn.execute(text("COMMIT"))
            
            # 检查数据库是否存在
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name}
            )
            
            if not result.fetchone():
                # 创建数据库
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"Database '{db_name}' created successfully")
            else:
                logger.info(f"Database '{db_name}' already exists")
                
        temp_engine.dispose()
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise


def create_tables():
    """
    创建所有数据表
    """
    try:
        # 导入所有模型以确保它们被注册
        from models import (
            person, organization, course, research, 
            asset, library, finance, permission
        )
        
        # 创建所有表
        Base.metadata.create_all(bind=sync_engine)
        logger.info("All tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


def drop_tables():
    """
    删除所有数据表（慎用！）
    """
    try:
        Base.metadata.drop_all(bind=sync_engine)
        logger.warning("All tables dropped")
        
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        raise


def check_database_connection():
    """
    检查数据库连接状态
    """
    try:
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"Database connection successful. PostgreSQL version: {version}")
            return True
            
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def check_async_database_connection():
    """
    检查异步数据库连接状态
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"Async database connection successful. PostgreSQL version: {version}")
            return True
            
    except Exception as e:
        logger.error(f"Async database connection failed: {e}")
        return False


def get_database_stats():
    """
    获取数据库统计信息
    """
    try:
        with sync_engine.connect() as conn:
            # 获取数据库大小
            db_name = settings.DATABASE_URL.split("/")[-1]
            size_result = conn.execute(
                text("SELECT pg_size_pretty(pg_database_size(:db_name))"),
                {"db_name": db_name}
            )
            db_size = size_result.fetchone()[0]
            
            # 获取连接数
            connections_result = conn.execute(
                text("""
                    SELECT count(*) 
                    FROM pg_stat_activity 
                    WHERE datname = :db_name
                """),
                {"db_name": db_name}
            )
            active_connections = connections_result.fetchone()[0]
            
            # 获取表数量
            tables_result = conn.execute(
                text("""
                    SELECT count(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
            )
            table_count = tables_result.fetchone()[0]
            
            return {
                "database_size": db_size,
                "active_connections": active_connections,
                "table_count": table_count,
                "engine_pool_size": sync_engine.pool.size(),
                "engine_checked_out": sync_engine.pool.checkedout(),
            }
            
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return None


class DatabaseManager:
    """
    数据库管理器类
    提供数据库初始化、重置、备份等功能
    """
    
    def __init__(self):
        self.sync_engine = sync_engine
        self.async_engine = async_engine
    
    def initialize(self):
        """
        初始化数据库
        """
        logger.info("Initializing database...")
        create_database()
        create_tables()
        logger.info("Database initialization completed")
    
    def reset(self):
        """
        重置数据库
        """
        logger.warning("Resetting database...")
        drop_tables()
        create_tables()
        logger.info("Database reset completed")
    
    def health_check(self):
        """
        数据库健康检查
        """
        return {
            "sync_connection": check_database_connection(),
            "stats": get_database_stats()
        }
    
    async def async_health_check(self):
        """
        异步数据库健康检查
        """
        return {
            "async_connection": await check_async_database_connection(),
            "stats": get_database_stats()
        }
    
    def close_connections(self):
        """
        关闭所有连接
        """
        sync_engine.dispose()
        logger.info("Database connections closed")
    
    async def close_async_connections(self):
        """
        关闭异步连接
        """
        await async_engine.dispose()
        logger.info("Async database connections closed")


# 全局数据库管理器实例
db_manager = DatabaseManager()


# 数据库事务装饰器
def with_transaction(func):
    """
    数据库事务装饰器
    自动处理事务提交和回滚
    """
    def wrapper(*args, **kwargs):
        db = SessionLocal()
        try:
            result = func(db, *args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Transaction failed: {e}")
            raise
        finally:
            db.close()
    
    return wrapper


# 批量操作辅助函数
def bulk_insert(model_class, data_list: list, batch_size: int = 1000):
    """
    批量插入数据
    """
    db = SessionLocal()
    try:
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            db.bulk_insert_mappings(model_class, batch)
            db.commit()
            logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
            
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk insert failed: {e}")
        raise
    finally:
        db.close()


def bulk_update(model_class, data_list: list, batch_size: int = 1000):
    """
    批量更新数据
    """
    db = SessionLocal()
    try:
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            db.bulk_update_mappings(model_class, batch)
            db.commit()
            logger.info(f"Updated batch {i//batch_size + 1}: {len(batch)} records")
            
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk update failed: {e}")
        raise
    finally:
        db.close() 