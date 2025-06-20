"""
SZTU-iCampus 数据服务主程序
独立的数据库服务，提供Mock数据生成和API接口
"""
import os
import uvicorn
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from loguru import logger

# 导入配置和数据库
from config import settings, MOCK_CONFIG
from database import get_db, db_manager, get_database_stats

# 导入所有模型
from models import *

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SZTU-iCampus 独立数据服务",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置日志
logger.add(
    settings.LOG_FILE,
    rotation="100 MB",
    retention="30 days",
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)


# 通用响应格式
def create_response(status: str = "success", msg: str = "", data: Any = None, 
                   timestamp: str = None, version: str = "1.0") -> Dict[str, Any]:
    """创建统一的API响应格式"""
    return {
        "status": status,
        "msg": msg,
        "data": data,
        "timestamp": timestamp or datetime.now().isoformat(),
        "version": version
    }


# API密钥验证中间件
async def verify_api_key(api_key: str = Query(..., description="API密钥")):
    """验证API密钥"""
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("Starting SZTU-iCampus Data Service...")
    
    # 检查数据库连接
    if db_manager.health_check()["sync_connection"]:
        logger.info("Database connection successful")
    else:
        logger.error("Database connection failed")
    
    logger.info(f"Service started on {settings.HOST}:{settings.PORT}")


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("Shutting down SZTU-iCampus Data Service...")
    db_manager.close_connections()
    logger.info("Service shutdown complete")


# ==================== 基础接口 ====================

@app.get("/", tags=["基础"])
async def root():
    """根路径接口"""
    return create_response(
        msg="Welcome to SZTU-iCampus Data Service",
        data={
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    )


@app.get("/health", tags=["基础"])
async def health_check():
    """健康检查接口"""
    try:
        health_info = db_manager.health_check()
        stats = get_database_stats()
        
        return create_response(
            msg="Service is healthy",
            data={
                "database": health_info,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content=create_response(
                status="error",
                msg=f"Service unhealthy: {str(e)}"
            )
        )


@app.get("/stats", tags=["基础"])
async def get_stats(api_key_valid: bool = Depends(verify_api_key)):
    """获取数据统计信息"""
    try:
        db = next(get_db())
        
        # 统计各表数据量
        stats = {
            "persons": db.query(Person).count(),
            "colleges": db.query(College).count(),
            "majors": db.query(Major).count(),
            "classes": db.query(Class).count(),
            "courses": db.query(Course).count(),
            "course_instances": db.query(CourseInstance).count(),
            "grades": db.query(Grade).count(),
            "research_projects": db.query(ResearchProject).count(),
            "assets": db.query(Asset).count(),
            "books": db.query(Book).count(),
            "transactions": db.query(Transaction).count(),
        }
        
        # 添加系统统计
        db_stats = get_database_stats()
        
        return create_response(
            msg="Statistics retrieved successfully",
            data={
                "table_counts": stats,
                "database": db_stats,
                "mock_config": MOCK_CONFIG
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 数据库管理接口 ====================

@app.post("/database/init", tags=["数据库管理"])
async def init_database(
    background_tasks: BackgroundTasks,
    api_key_valid: bool = Depends(verify_api_key)
):
    """初始化数据库"""
    try:
        background_tasks.add_task(db_manager.initialize)
        
        return create_response(
            msg="Database initialization started in background",
            data={"task": "initialize_database"}
        )
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/database/reset", tags=["数据库管理"])
async def reset_database(
    background_tasks: BackgroundTasks,
    api_key_valid: bool = Depends(verify_api_key)
):
    """重置数据库（危险操作）"""
    try:
        background_tasks.add_task(db_manager.reset)
        
        return create_response(
            msg="Database reset started in background",
            data={"task": "reset_database", "warning": "All data will be deleted"}
        )
        
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 人员数据接口 ====================

@app.get("/persons", tags=["人员管理"])
async def get_persons(
    person_type: Optional[str] = Query(None, description="人员类型"),
    college_id: Optional[str] = Query(None, description="学院ID"),
    limit: int = Query(100, description="返回条数限制"),
    offset: int = Query(0, description="偏移量"),
    api_key_valid: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """获取人员列表"""
    try:
        query = db.query(Person)
        
        if person_type:
            query = query.filter(Person.person_type == person_type)
        if college_id:
            query = query.filter(Person.college_id == college_id)
        
        # 分页
        total = query.count()
        persons = query.offset(offset).limit(limit).all()
        
        # 转换为字典格式，脱敏处理
        persons_data = []
        for person in persons:
            person_dict = person.to_dict()
            # 脱敏处理
            if person_dict.get('phone'):
                person_dict['phone'] = person.display_phone
            if person_dict.get('id_card'):
                person_dict['id_card'] = person.display_id_card
            persons_data.append(person_dict)
        
        return create_response(
            msg="Persons retrieved successfully",
            data={
                "total": total,
                "limit": limit,
                "offset": offset,
                "persons": persons_data
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get persons: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/persons/{person_id}", tags=["人员管理"])
async def get_person(
    person_id: str,
    api_key_valid: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """获取指定人员信息"""
    try:
        person = db.query(Person).filter(Person.person_id == person_id).first()
        
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        
        person_dict = person.to_dict()
        # 脱敏处理
        if person_dict.get('phone'):
            person_dict['phone'] = person.display_phone
        if person_dict.get('id_card'):
            person_dict['id_card'] = person.display_id_card
        
        return create_response(
            msg="Person retrieved successfully",
            data=person_dict
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get person {person_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 课程数据接口 ====================

@app.get("/courses", tags=["课程管理"])
async def get_courses(
    college_id: Optional[str] = Query(None, description="学院ID"),
    major_id: Optional[str] = Query(None, description="专业ID"),
    course_type: Optional[str] = Query(None, description="课程类型"),
    limit: int = Query(100, description="返回条数限制"),
    offset: int = Query(0, description="偏移量"),
    api_key_valid: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """获取课程列表"""
    try:
        query = db.query(Course)
        
        if college_id:
            query = query.filter(Course.college_id == college_id)
        if major_id:
            query = query.filter(Course.major_id == major_id)
        if course_type:
            query = query.filter(Course.course_type == course_type)
        
        # 分页
        total = query.count()
        courses = query.offset(offset).limit(limit).all()
        
        courses_data = [course.to_dict() for course in courses]
        
        return create_response(
            msg="Courses retrieved successfully",
            data={
                "total": total,
                "limit": limit,
                "offset": offset,
                "courses": courses_data
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Mock数据生成接口 ====================

@app.post("/mock/generate", tags=["Mock数据"])
async def generate_mock_data(
    background_tasks: BackgroundTasks,
    data_type: str = Query("all", description="数据类型：all/persons/courses/assets等"),
    count: Optional[int] = Query(None, description="生成数量（可选）"),
    api_key_valid: bool = Depends(verify_api_key)
):
    """生成Mock数据"""
    try:
        # 导入数据生成器
        from generators.base_generator import MockDataGenerator
        
        generator = MockDataGenerator()
        
        # 根据数据类型生成数据
        if data_type == "all":
            background_tasks.add_task(generator.generate_all_data)
            task_desc = "Generate all mock data"
        elif data_type == "persons":
            background_tasks.add_task(generator.generate_persons, count)
            task_desc = f"Generate {count or 'default'} person records"
        elif data_type == "courses":
            background_tasks.add_task(generator.generate_courses, count)
            task_desc = f"Generate {count or 'default'} course records"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported data type: {data_type}")
        
        return create_response(
            msg="Mock data generation started in background",
            data={
                "task": "generate_mock_data",
                "data_type": data_type,
                "count": count,
                "description": task_desc
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to generate mock data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 批量操作接口 ====================

@app.post("/batch/persons", tags=["批量操作"])
async def batch_create_persons(
    persons_data: List[Dict[str, Any]],
    api_key_valid: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """批量创建人员"""
    try:
        created_persons = []
        
        for person_data in persons_data:
            person = Person(**person_data)
            db.add(person)
            created_persons.append(person.person_id)
        
        db.commit()
        
        return create_response(
            msg="Persons created successfully",
            data={
                "created_count": len(created_persons),
                "person_ids": created_persons
            }
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to batch create persons: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 流式数据接口 ====================

@app.get("/stream/notifications", tags=["流式数据"])
async def stream_notifications(
    person_id: str = Query(..., description="人员ID"),
    api_key_valid: bool = Depends(verify_api_key)
):
    """流式通知接口（SSE）"""
    from fastapi.responses import StreamingResponse
    import asyncio
    import json
    
    async def generate_notifications():
        """生成实时通知数据"""
        counter = 0
        while True:
            # 模拟实时数据
            notification_data = {
                "id": f"notif_{counter}",
                "person_id": person_id,
                "type": "announcement",
                "title": f"测试通知 {counter}",
                "content": f"这是第 {counter} 条实时通知",
                "timestamp": datetime.now().isoformat(),
                "read": False
            }
            
            # SSE格式
            yield f"data: {json.dumps(notification_data)}\n\n"
            
            counter += 1
            await asyncio.sleep(5)  # 每5秒推送一次
    
    return StreamingResponse(
        generate_notifications(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


if __name__ == "__main__":
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower()
    ) 