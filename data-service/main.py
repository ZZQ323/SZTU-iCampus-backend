"""
SZTU-iCampus 数据服务主程序
独立的数据库服务，提供Mock数据生成和API接口
"""
import os
import uvicorn
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from loguru import logger

# 导入配置和数据库
from config import settings, MOCK_CONFIG
from database import get_db, db_manager, get_database_stats



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


def _build_where_conditions(filter_dict: dict, table_name: str = None) -> tuple:
    """构建WHERE条件 - 修复表别名问题"""
    conditions = []
    params = {}
    
    # 只有在实际使用JOIN时才使用表别名
    # 这里先不使用表别名，避免SQL错误
    prefix = ""
    
    for key, value in filter_dict.items():
        if key == "$or":
            # OR 条件处理
            or_conditions = []
            for or_condition in value:
                for or_key, or_value in or_condition.items():
                    param_key = f"or_{or_key}_{len(params)}"
                    or_conditions.append(f"{or_key} = :{param_key}")
                    params[param_key] = or_value
            conditions.append(f"({' OR '.join(or_conditions)})")
        
        elif key == "$and":
            # AND 条件处理
            for and_condition in value:
                for and_key, and_value in and_condition.items():
                    param_key = f"and_{and_key}_{len(params)}"
                    conditions.append(f"{and_key} = :{param_key}")
                    params[param_key] = and_value
        
        else:
            # 普通条件 - 不使用表别名
            param_key = f"param_{len(params)}"
            conditions.append(f"{key} = :{param_key}")
            params[param_key] = value
    
    return conditions, params


# 🔒 安全升级：API密钥验证中间件 - 使用HTTP请求头
async def verify_api_key(x_api_key: str = Header(..., description="API密钥，通过请求头传递")):
    """验证API密钥 - 通过HTTP请求头验证，增强安全性"""
    if x_api_key != settings.API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}...")
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
        
        # 使用SQL查询统计各表数据量
        from sqlalchemy import text
        
        stats = {}
        table_names = [
            "persons", "colleges", "majors", "classes", "courses", 
            "course_instances", "grades", "research_projects", 
            "assets", "books", "transactions"
        ]
        
        for table_name in table_names:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                stats[table_name] = result.fetchone()[0]
            except Exception as e:
                # 如果表不存在，设为0
                logger.debug(f"Table {table_name} not found: {e}")
                stats[table_name] = 0
        
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


@app.get("/stats/{table_name}/{field_name}", tags=["基础"])
async def get_field_statistics(
    table_name: str,
    field_name: str,
    operation: str = Query("count", description="统计操作: count, sum, avg, max, min"),
    group_by: Optional[str] = Query(None, description="分组字段"),
    filters: Optional[str] = Query(None, description="过滤条件JSON"),
    api_key_valid: bool = Depends(verify_api_key)
):
    """获取字段统计信息"""
    try:
        # 验证表名安全性
        allowed_tables = [
            "persons", "colleges", "majors", "classes", "departments", "courses", 
            "course_instances", "enrollments", "grades", "announcements", 
            "research_projects", "assets", "books", "borrow_records", 
            "transactions", "campus_cards", "library_seats", "user_reading_records"
        ]
        
        if table_name not in allowed_tables:
            raise HTTPException(status_code=400, detail=f"表 {table_name} 不允许访问")
        
        db = next(get_db())
        from sqlalchemy import text
        import json
        
        # 构建SQL查询
        if operation.lower() not in ['count', 'sum', 'avg', 'max', 'min']:
            operation = 'count'
        
        # 基础查询
        if operation.lower() == 'count':
            base_sql = f"SELECT COUNT(*) as result FROM {table_name}"
        else:
            base_sql = f"SELECT {operation.upper()}({field_name}) as result FROM {table_name}"
        
        # 添加WHERE条件
        where_conditions = []
        params = {}
        
        if filters:
            try:
                filter_dict = json.loads(filters)
                for key, value in filter_dict.items():
                    if key.startswith('$'):
                        continue  # 跳过特殊操作符
                    where_conditions.append(f"{key} = :{key}")
                    params[key] = value
            except json.JSONDecodeError:
                logger.warning(f"Invalid filters JSON: {filters}")
        
        # 构建完整SQL
        sql = base_sql
        if where_conditions:
            sql += " WHERE " + " AND ".join(where_conditions)
        
        if group_by:
            sql = sql.replace("SELECT COUNT(*) as result", f"SELECT {group_by}, COUNT(*) as result")
            sql += f" GROUP BY {group_by}"
        
        logger.info(f"执行统计查询: {sql} with params: {params}")
        
        # 执行查询
        result = db.execute(text(sql), params)
        
        if group_by:
            # 分组结果
            rows = result.fetchall()
            group_results = {}
            for row in rows:
                group_results[str(row[0])] = row[1]
            final_result = group_results
        else:
            # 单一结果
            row = result.fetchone()
            final_result = row[0] if row else 0
        
        return create_response(
            msg=f"Field statistics for {table_name}.{field_name} retrieved successfully",
            data={
                "table_name": table_name,
                "field_name": field_name,
                "operation": operation,
                "result": final_result,
                "group_by": group_by
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get field statistics: {e}")
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
        from sqlalchemy import text
        
        # 构建SQL查询
        where_conditions = []
        params = {}
        
        if person_type:
            where_conditions.append("person_type = :person_type")
            params["person_type"] = person_type
        if college_id:
            where_conditions.append("college_id = :college_id")
            params["college_id"] = college_id
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM persons{where_clause}"
        total_result = db.execute(text(count_sql), params)
        total = total_result.fetchone()[0]
        
        # 查询数据
        data_sql = f"SELECT * FROM persons{where_clause} LIMIT :limit OFFSET :offset"
        params.update({"limit": limit, "offset": offset})
        
        result = db.execute(text(data_sql), params)
        rows = result.fetchall()
        
        # 转换为字典格式
        persons_data = []
        for row in rows:
            person_dict = dict(row._mapping)
            # 基本脱敏处理
            if person_dict.get('phone'):
                phone = str(person_dict['phone'])
                person_dict['phone'] = phone[:3] + "****" + phone[-4:] if len(phone) >= 7 else phone
            if person_dict.get('id_card'):
                id_card = str(person_dict['id_card'])
                person_dict['id_card'] = id_card[:6] + "****" + id_card[-4:] if len(id_card) >= 10 else id_card
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
        from sqlalchemy import text
        
        result = db.execute(
            text("SELECT * FROM persons WHERE person_id = :person_id"),
            {"person_id": person_id}
        )
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Person not found")
        
        person_dict = dict(row._mapping)
        # 脱敏处理
        if person_dict.get('phone'):
            phone = str(person_dict['phone'])
            person_dict['phone'] = phone[:3] + "****" + phone[-4:] if len(phone) >= 7 else phone
        if person_dict.get('id_card'):
            id_card = str(person_dict['id_card'])
            person_dict['id_card'] = id_card[:6] + "****" + id_card[-4:] if len(id_card) >= 10 else id_card
        
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
        from sqlalchemy import text
        
        # 构建SQL查询
        where_conditions = []
        params = {}
        
        if college_id:
            where_conditions.append("college_id = :college_id")
            params["college_id"] = college_id
        if major_id:
            where_conditions.append("major_id = :major_id")
            params["major_id"] = major_id
        if course_type:
            where_conditions.append("course_type = :course_type")
            params["course_type"] = course_type
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM courses{where_clause}"
        total_result = db.execute(text(count_sql), params)
        total = total_result.fetchone()[0]
        
        # 查询数据
        data_sql = f"SELECT * FROM courses{where_clause} LIMIT :limit OFFSET :offset"
        params.update({"limit": limit, "offset": offset})
        
        result = db.execute(text(data_sql), params)
        rows = result.fetchall()
        
        courses_data = [dict(row._mapping) for row in rows]
        
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
        # 临时禁用Mock数据生成功能，因为缺少生成器
        raise HTTPException(
            status_code=501, 
            detail="Mock data generation temporarily disabled due to missing generators"
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
        # 临时禁用批量创建功能，因为缺少模型定义
        raise HTTPException(
            status_code=501, 
            detail="Batch creation temporarily disabled due to missing model definitions"
        )
        
    except Exception as e:
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


# ==================== 公告数据接口 ====================

@app.get("/announcements", tags=["公告管理"])
async def get_announcements(
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="每页条数"),
    category: Optional[str] = Query(None, description="公告分类"),
    priority: Optional[str] = Query(None, description="优先级"),
    is_pinned: Optional[bool] = Query(None, description="是否置顶"),
    api_key_valid: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """获取公告列表 - 读取真实数据库"""
    try:
        from sqlalchemy import text
        
        # 构建查询条件
        where_conditions = ["is_deleted = FALSE", "status = 'published'"]
        params = {}
        
        if category:
            where_conditions.append("category = :category")
            params["category"] = category
        if priority:
            where_conditions.append("priority = :priority") 
            params["priority"] = priority
        if is_pinned is not None:
            where_conditions.append("is_pinned = :is_pinned")
            params["is_pinned"] = is_pinned
        
        where_clause = " WHERE " + " AND ".join(where_conditions)
        
        # 计算偏移量
        offset = (page - 1) * size
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM announcements{where_clause}"
        total_result = db.execute(text(count_sql), params)
        total = total_result.fetchone()[0]
        
        # 查询数据（按置顶和发布时间排序）
        data_sql = f"""
        SELECT 
            announcement_id, title, content, summary, publisher_name, department,
            category, priority, is_urgent, is_pinned, publish_time, 
            target_audience, view_count, like_count, comment_count,
            cover_image_url, created_at, updated_at
        FROM announcements{where_clause}
        ORDER BY is_pinned DESC, publish_time DESC
        LIMIT :limit OFFSET :offset
        """
        params.update({"limit": size, "offset": offset})
        
        result = db.execute(text(data_sql), params)
        rows = result.fetchall()
        
        # 转换为字典格式
        announcements = []
        for row in rows:
            announcement = dict(row._mapping)
            # 转换时间格式
            if announcement.get('publish_time'):
                announcement['publish_time'] = str(announcement['publish_time'])
            if announcement.get('created_at'):
                announcement['created_at'] = str(announcement['created_at'])
            if announcement.get('updated_at'):
                announcement['updated_at'] = str(announcement['updated_at'])
            announcements.append(announcement)
        
        return create_response(
            msg="Announcements retrieved successfully",
            data={
                "total": total,
                "page": page,
                "size": size,
                "announcements": announcements
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get announcements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/announcements/{announcement_id}", tags=["公告管理"])
async def get_announcement_detail(
    announcement_id: str,
    api_key_valid: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """获取公告详情 - 读取真实数据库"""
    try:
        from sqlalchemy import text
        
        # 查询公告详情
        result = db.execute(
            text("""
            SELECT * FROM announcements 
            WHERE announcement_id = :announcement_id 
            AND is_deleted = FALSE 
            AND status = 'published'
            """),
            {"announcement_id": announcement_id}
        )
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Announcement not found")
        
        announcement = dict(row._mapping)
        
        # 转换时间格式
        time_fields = ['publish_time', 'effective_date', 'expire_date', 'created_at', 'updated_at', 'review_time']
        for field in time_fields:
            if announcement.get(field):
                announcement[field] = str(announcement[field])
        
        # 更新查看次数
        update_sql = text("""
        UPDATE announcements 
        SET view_count = view_count + 1, updated_at = CURRENT_TIMESTAMP
        WHERE announcement_id = :announcement_id
        """)
        db.execute(update_sql, {"announcement_id": announcement_id})
        db.commit()
        
        return create_response(
            msg="Announcement detail retrieved successfully",
            data=announcement
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get announcement {announcement_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 成绩数据接口 ====================

@app.get("/grades/student/{student_id}", tags=["成绩管理"])
async def get_student_grades(
    student_id: str,
    semester: Optional[str] = Query(None, description="学期，格式如：2024-2025-1"),
    api_key_valid: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """获取学生成绩 - 读取真实数据库"""
    try:
        from sqlalchemy import text
        
        # 构建查询条件
        where_conditions = ["g.student_id = :student_id"]
        params = {"student_id": student_id}
        
        if semester:
            where_conditions.append("ci.semester = :semester")
            params["semester"] = semester
        
        where_clause = " WHERE " + " AND ".join(where_conditions)
        
        # 查询成绩数据，关联课程实例和课程信息
        grades_sql = f"""
        SELECT 
            g.grade_id,
            g.student_id,
            g.course_instance_id,
            g.usual_score,
            g.midterm_score,
            g.final_score,
            g.lab_score,
            g.homework_score,
            g.total_score,
            g.grade_point,
            g.grade_level,
            g.score_weights,
            g.is_passed,
            g.teacher_comment,
            ci.semester,
            ci.academic_year,
            c.course_id,
            c.course_name,
            c.course_code,
            c.credit_hours,
            c.course_type,
            p.name as teacher_name
        FROM grades g
        JOIN course_instances ci ON g.course_instance_id = ci.instance_id
        JOIN courses c ON ci.course_id = c.course_id
        LEFT JOIN persons p ON ci.teacher_id = p.person_id
        {where_clause}
        ORDER BY ci.semester DESC, c.course_name
        """
        
        result = db.execute(text(grades_sql), params)
        grades_rows = result.fetchall()
        
        # 转换为字典格式
        grades_data = []
        for row in grades_rows:
            grade_dict = dict(row._mapping)
            grades_data.append({
                "course_id": grade_dict.get("course_id"),
                "course_name": grade_dict.get("course_name"),
                "course_code": grade_dict.get("course_code"),
                "credits": float(grade_dict.get("credit_hours", 0)),
                "teacher": grade_dict.get("teacher_name"),
                "regular_score": float(grade_dict.get("usual_score") or 0),
                "midterm_score": float(grade_dict.get("midterm_score") or 0),
                "final_score": float(grade_dict.get("final_score") or 0),
                "lab_score": float(grade_dict.get("lab_score") or 0),
                "homework_score": float(grade_dict.get("homework_score") or 0),
                "total_score": float(grade_dict.get("total_score") or 0),
                "grade_level": grade_dict.get("grade_level"),
                "gpa_points": float(grade_dict.get("grade_point") or 0),
                "course_type": grade_dict.get("course_type"),
                "semester": grade_dict.get("semester"),
                "academic_year": grade_dict.get("academic_year"),
                "is_passed": bool(grade_dict.get("is_passed")),
                "teacher_comment": grade_dict.get("teacher_comment")
            })
        
        # 计算统计信息
        if grades_data:
            total_credits = sum(g["credits"] for g in grades_data)
            total_score = sum(g["total_score"] * g["credits"] for g in grades_data) / total_credits if total_credits > 0 else 0
            total_gpa = sum(g["gpa_points"] * g["credits"] for g in grades_data) / total_credits if total_credits > 0 else 0
            passed_courses = sum(1 for g in grades_data if g["is_passed"])
            
            statistics = {
                "total_courses": len(grades_data),
                "passed_courses": passed_courses,
                "total_credits": total_credits,
                "avg_score": round(total_score, 2),
                "gpa": round(total_gpa, 2),
                "pass_rate": round(passed_courses / len(grades_data) * 100, 2) if grades_data else 0
            }
        else:
            statistics = {
                "total_courses": 0,
                "passed_courses": 0,
                "total_credits": 0,
                "avg_score": 0,
                "gpa": 0,
                "pass_rate": 0
            }
        
        # 获取学期信息
        semester_info = {
            "current_semester": semester or (grades_data[0]["semester"] if grades_data else "2024-2025-1"),
            "academic_year": grades_data[0]["academic_year"] if grades_data else "2024-2025"
        }
        
        return create_response(
            msg="Student grades retrieved successfully",
            data={
                "student_id": student_id,
                "semester_info": semester_info,
                "grades": grades_data,
                "summary": statistics
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get student grades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/grades/statistics/{student_id}", tags=["成绩管理"])
async def get_grade_statistics(
    student_id: str,
    api_key_valid: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """获取学生成绩统计分析"""
    try:
        from sqlalchemy import text
        
        # 获取所有学期的成绩统计
        stats_sql = """
        SELECT 
            ci.semester,
            ci.academic_year,
            COUNT(*) as course_count,
            SUM(c.credit_hours) as total_credits,
            AVG(g.total_score) as avg_score,
            AVG(g.grade_point) as avg_gpa,
            SUM(CASE WHEN g.is_passed = 1 THEN 1 ELSE 0 END) as passed_count
        FROM grades g
        JOIN course_instances ci ON g.course_instance_id = ci.instance_id
        JOIN courses c ON ci.course_id = c.course_id
        WHERE g.student_id = :student_id
        GROUP BY ci.semester, ci.academic_year
        ORDER BY ci.academic_year DESC, ci.semester DESC
        """
        
        result = db.execute(text(stats_sql), {"student_id": student_id})
        semester_stats = result.fetchall()
        
        # 按课程类型统计
        type_stats_sql = """
        SELECT 
            c.course_type,
            COUNT(*) as course_count,
            SUM(c.credit_hours) as total_credits,
            AVG(g.total_score) as avg_score,
            AVG(g.grade_point) as avg_gpa
        FROM grades g
        JOIN course_instances ci ON g.course_instance_id = ci.instance_id
        JOIN courses c ON ci.course_id = c.course_id
        WHERE g.student_id = :student_id
        GROUP BY c.course_type
        """
        
        type_result = db.execute(text(type_stats_sql), {"student_id": student_id})
        type_stats = type_result.fetchall()
        
        # 成绩分布统计
        distribution_sql = """
        SELECT 
            CASE 
                WHEN g.total_score >= 90 THEN 'excellent'
                WHEN g.total_score >= 80 THEN 'good'
                WHEN g.total_score >= 70 THEN 'average'
                ELSE 'poor'
            END as grade_range,
            COUNT(*) as count
        FROM grades g
        WHERE g.student_id = :student_id
        GROUP BY grade_range
        """
        
        dist_result = db.execute(text(distribution_sql), {"student_id": student_id})
        distribution = dist_result.fetchall()
        
        # 组织返回数据
        semester_trends = []
        for row in semester_stats:
            semester_trends.append({
                "semester": row.semester,
                "academic_year": row.academic_year,
                "course_count": row.course_count,
                "total_credits": float(row.total_credits or 0),
                "avg_score": round(float(row.avg_score or 0), 2),
                "gpa": round(float(row.avg_gpa or 0), 2),
                "pass_rate": round(row.passed_count / row.course_count * 100, 2) if row.course_count > 0 else 0
            })
        
        course_type_analysis = {}
        for row in type_stats:
            course_type_analysis[row.course_type or "unknown"] = {
                "count": row.course_count,
                "total_credits": float(row.total_credits or 0),
                "avg_score": round(float(row.avg_score or 0), 2),
                "gpa": round(float(row.avg_gpa or 0), 2)
            }
        
        performance_analysis = {
            "excellent_count": 0,  # 90分以上
            "good_count": 0,       # 80-89分
            "average_count": 0,    # 70-79分
            "poor_count": 0        # 70分以下
        }
        
        for row in distribution:
            performance_analysis[f"{row.grade_range}_count"] = row.count
        
        # 计算整体统计
        overall_stats = {}
        if semester_trends:
            overall_stats = {
                "total_semesters": len(semester_trends),
                "total_courses": sum(s["course_count"] for s in semester_trends),
                "total_credits": sum(s["total_credits"] for s in semester_trends),
                "overall_gpa": sum(s["gpa"] * s["total_credits"] for s in semester_trends) / sum(s["total_credits"] for s in semester_trends) if sum(s["total_credits"] for s in semester_trends) > 0 else 0,
                "overall_avg_score": sum(s["avg_score"] * s["course_count"] for s in semester_trends) / sum(s["course_count"] for s in semester_trends) if sum(s["course_count"] for s in semester_trends) > 0 else 0
            }
            overall_stats["overall_gpa"] = round(overall_stats["overall_gpa"], 2)
            overall_stats["overall_avg_score"] = round(overall_stats["overall_avg_score"], 2)
        
        return create_response(
            msg="Grade statistics retrieved successfully",
            data={
                "student_id": student_id,
                "overall": overall_stats,
                "semester_trends": semester_trends,
                "course_type_analysis": course_type_analysis,
                "performance_analysis": performance_analysis
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get grade statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 优化的登录查询接口 ====================

@app.post("/auth/login", tags=["认证"])
async def authenticate_user(
    login_request: dict,
    api_key_valid: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """用户认证登录 - 优化版本"""
    try:
        from sqlalchemy import text
        
        login_id = login_request.get("login_id")
        password = login_request.get("password")
        
        if not login_id or not password:
            raise HTTPException(status_code=400, detail="登录ID和密码不能为空")
        
        # 优化的查询：使用JOIN查询，只选择需要的字段，避免COUNT操作
        auth_sql = """
        SELECT 
            p.person_id,
            p.person_type,
            p.student_id,
            p.employee_id,
            p.name,
            p.phone,
            p.email,
            p.password_plain,
            p.wechat_openid,
            p.academic_status,
            p.employment_status,
            p.class_id,
            p.major_id,
            p.college_id,
            p.department_id,
            -- 关联查询相关信息
            c.college_name,
            m.major_name,
            cl.class_name,
            d.department_name
        FROM persons p
        LEFT JOIN colleges c ON p.college_id = c.college_id
        LEFT JOIN majors m ON p.major_id = m.major_id  
        LEFT JOIN classes cl ON p.class_id = cl.class_id
        LEFT JOIN departments d ON p.department_id = d.department_id
        WHERE (
            (p.person_type = 'student' AND p.student_id = :login_id)
            OR 
            (p.person_type IN ('teacher', 'admin', 'assistant_teacher') AND p.employee_id = :login_id)
        )
        AND p.is_deleted = 0 
        AND p.status = 'active'
        AND p.password_plain = :password
        LIMIT 1
        """
        
        result = db.execute(text(auth_sql), {
            "login_id": login_id,
            "password": password
        })
        
        user_row = result.fetchone()
        
        if not user_row:
            raise HTTPException(status_code=401, detail="登录ID或密码错误")
        
        # 转换为字典
        user_data = dict(user_row._mapping)
        
        # 脱敏处理
        if user_data.get('phone'):
            phone = str(user_data['phone'])
            user_data['phone'] = phone[:3] + "****" + phone[-4:] if len(phone) >= 7 else phone
        
        # 移除敏感信息
        user_data.pop('password_plain', None)
        
        return create_response(
            msg="登录成功",
            data={
                "user_info": user_data,
                "login_time": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户认证失败: {e}")
        raise HTTPException(status_code=500, detail="登录服务异常")


# ==================== 优化的通用查询接口 ====================

@app.get("/query/{table_name}", tags=["通用查询"])
async def query_table_optimized(
    table_name: str,
    filters: Optional[str] = Query(None, description="JSON格式的过滤条件"),
    fields: Optional[str] = Query(None, description="需要返回的字段，逗号分隔"),
    join_tables: Optional[str] = Query(None, description="需要JOIN的表，逗号分隔"),
    limit: int = Query(50, description="返回条数限制，默认50"),
    offset: int = Query(0, description="偏移量"),
    order_by: Optional[str] = Query(None, description="排序字段"),
    api_key_valid: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """优化的通用表查询接口 - 使用JOIN查询提升性能"""
    try:
        from sqlalchemy import text
        import json
        
        # 验证表名安全性
        allowed_tables = [
            "persons", "colleges", "majors", "classes", "courses", "course_instances",
            "grades", "announcements", "events", "books", "borrow_records", 
            "transactions", "campus_cards", "locations", "assets", "enrollments",
            "class_schedules", "user_reading_records", "event_registrations",
            "research_projects", "research_applications", "paper_library",
            "network_permissions", "system_access", "platform_configs",
            "device_registrations", "audit_logs", "workflow_instances",
            "grade_statistics", "room_occupations"
        ]
        
        if table_name not in allowed_tables:
            raise HTTPException(status_code=400, detail=f"Table {table_name} not allowed")
        
        # 构建查询条件
        where_conditions = []
        params = {}
        
        if filters:
            try:
                filter_dict = json.loads(filters)
                where_conditions, params = _build_where_conditions(filter_dict, table_name)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid filters JSON format")
        
        # 智能字段选择
        select_fields = _build_smart_select_fields(table_name, fields, join_tables)
        
        # 智能JOIN构建
        join_clause = _build_smart_joins(table_name, join_tables)
        
        # 构建WHERE子句
        where_clause = ""
        if where_conditions:
            where_clause = " WHERE " + " AND ".join(where_conditions)
        
        # 处理排序
        order_clause = ""
        if order_by:
            order_clause = f" ORDER BY {order_by}"
        else:
            # 默认排序优化
            order_clause = _get_default_order(table_name)
        
        # 优化的查询 - 避免COUNT操作，使用子查询
        data_sql = f"""
        SELECT {select_fields}
        FROM {table_name} 
        {join_clause}
        {where_clause}
        {order_clause}
        LIMIT :limit OFFSET :offset
        """
        
        params.update({"limit": limit, "offset": offset})
        
        result = db.execute(text(data_sql), params)
        rows = result.fetchall()
        
        # 转换为字典格式
        data = [dict(row._mapping) for row in rows]
        
        # 估算总数而不是精确计数（性能优化）
        estimated_total = len(data) + offset
        if len(data) == limit:
            estimated_total = "50+"  # 表示还有更多数据
        
        return create_response(
            msg=f"Query {table_name} successful",
            data={
                "table": table_name,
                "estimated_total": estimated_total,
                "limit": limit,
                "offset": offset,
                "count": len(data),
                "records": data,
                "has_more": len(data) == limit
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to query {table_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _build_smart_select_fields(table_name: str, fields: Optional[str], join_tables: Optional[str]) -> str:
    """智能构建查询字段"""
    
    # 定义核心字段映射，避免SELECT *
    core_fields = {
        "persons": [
            "person_id", "person_type", "student_id", "employee_id", "name", 
            "gender", "phone", "email", "college_id", "major_id", "class_id",
            "academic_status", "employment_status", "wechat_openid"
        ],
        "enrollments": [
            "enrollment_id", "student_id", "course_instance_id", "enrollment_status",
            "enrollment_date", "credit_hours", "is_mandatory"
        ],
        "course_instances": [
            "instance_id", "course_id", "teacher_id", "semester", "academic_year",
            "max_students", "current_students", "instance_status", "schedule_info"
        ],
        "courses": [
            "course_id", "course_name", "course_code", "course_type",
            "credit_hours", "total_hours", "major_id", "college_id"
        ],
        "grades": [
            "grade_id", "student_id", "course_instance_id", "midterm_score",
            "final_score", "total_score", "grade_level", "grade_point", "is_passed"
        ]
    }
    
    if fields:
        return fields
    
    # 使用核心字段而不是SELECT *
    table_fields = core_fields.get(table_name, ["*"])
    
    # 添加关联表字段
    if join_tables and table_name == "persons":
        if "colleges" in join_tables:
            table_fields.extend(["c.college_name", "c.college_code"])
        if "majors" in join_tables:
            table_fields.extend(["m.major_name", "m.major_code"])
        if "classes" in join_tables:
            table_fields.extend(["cl.class_name", "cl.grade"])
    
    return ", ".join(table_fields)


def _build_smart_joins(table_name: str, join_tables: Optional[str]) -> str:
    """智能构建JOIN子句 - 修复别名问题"""
    if not join_tables:
        return ""
    
    join_clause = ""
    
    # 为主表添加别名
    if table_name == "persons":
        # 需要修改FROM子句为: FROM persons p
        if "colleges" in join_tables:
            join_clause += " LEFT JOIN colleges c ON persons.college_id = c.college_id"
        if "majors" in join_tables:
            join_clause += " LEFT JOIN majors m ON persons.major_id = m.major_id"
        if "classes" in join_tables:
            join_clause += " LEFT JOIN classes cl ON persons.class_id = cl.class_id"
    
    elif table_name == "enrollments":
        if "course_instances" in join_tables:
            join_clause += " LEFT JOIN course_instances ci ON enrollments.course_instance_id = ci.instance_id"
        if "courses" in join_tables:
            join_clause += " LEFT JOIN courses c ON ci.course_id = c.course_id"
        if "persons" in join_tables:
            join_clause += " LEFT JOIN persons p ON enrollments.student_id = p.student_id"
    
    return join_clause


def _get_default_order(table_name: str) -> str:
    """获取默认排序 - 不使用表别名"""
    default_orders = {
        "persons": " ORDER BY updated_at DESC",
        "enrollments": " ORDER BY enrollment_date DESC", 
        "announcements": " ORDER BY publish_time DESC",
        "transactions": " ORDER BY transaction_time DESC",
        "grades": " ORDER BY updated_at DESC"
    }
    
    return default_orders.get(table_name, " ORDER BY updated_at DESC")


# ==================== 数据写入操作接口 ====================

@app.post("/insert/{table_name}", tags=["数据写入"])
async def insert_record(
    table_name: str,
    record_data: dict,
    api_key_valid: bool = Depends(verify_api_key)
):
    """插入新记录"""
    try:
        # 验证表名安全性
        allowed_tables = [
            "persons", "colleges", "majors", "classes", "departments", "courses", 
            "course_instances", "enrollments", "grades", "announcements", 
            "research_projects", "assets", "books", "borrow_records", 
            "transactions", "campus_cards", "library_seats", "user_reading_records",
            "card_operations", "seat_reservations", "user_bookmarks"
        ]
        
        if table_name not in allowed_tables:
            raise HTTPException(status_code=400, detail=f"表 {table_name} 不允许插入")
        
        db = next(get_db())
        from sqlalchemy import text
        
        # 构建INSERT SQL
        fields = list(record_data.keys())
        placeholders = [f":{field}" for field in fields]
        
        sql = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        
        logger.info(f"执行插入: {sql}")
        logger.debug(f"插入数据: {record_data}")
        
        # 执行插入
        result = db.execute(text(sql), record_data)
        db.commit()
        
        return create_response(
            msg=f"Record inserted into {table_name} successfully",
            data={
                "table_name": table_name,
                "affected_rows": result.rowcount,
                "inserted_data": record_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to insert into {table_name}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update/{table_name}", tags=["数据写入"])
async def update_records(
    table_name: str,
    update_data: dict,
    api_key_valid: bool = Depends(verify_api_key)
):
    """更新记录"""
    try:
        # 验证表名安全性
        allowed_tables = [
            "persons", "colleges", "majors", "classes", "departments", "courses", 
            "course_instances", "enrollments", "grades", "announcements", 
            "research_projects", "assets", "books", "borrow_records", 
            "transactions", "campus_cards", "library_seats", "user_reading_records",
            "card_operations", "seat_reservations", "user_bookmarks"
        ]
        
        if table_name not in allowed_tables:
            raise HTTPException(status_code=400, detail=f"表 {table_name} 不允许更新")
        
        # 检查必需的字段
        if "filters" not in update_data or "updates" not in update_data:
            raise HTTPException(status_code=400, detail="缺少必需的fields: filters, updates")
        
        db = next(get_db())
        from sqlalchemy import text
        import json
        
        filters = update_data["filters"]
        updates = update_data["updates"]
        
        # 构建UPDATE SQL
        set_clauses = []
        params = {}
        
        # 处理SET子句
        for field, value in updates.items():
            set_clauses.append(f"{field} = :set_{field}")
            params[f"set_{field}"] = value
        
        # 处理WHERE子句
        where_conditions = []
        for field, value in filters.items():
            where_conditions.append(f"{field} = :where_{field}")
            params[f"where_{field}"] = value
        
        sql = f"UPDATE {table_name} SET {', '.join(set_clauses)}"
        if where_conditions:
            sql += f" WHERE {' AND '.join(where_conditions)}"
        
        logger.info(f"执行更新: {sql}")
        logger.debug(f"更新参数: {params}")
        
        # 执行更新
        result = db.execute(text(sql), params)
        db.commit()
        
        return create_response(
            msg=f"Records in {table_name} updated successfully",
            data={
                "table_name": table_name,
                "affected_rows": result.rowcount,
                "filters": filters,
                "updates": updates
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update {table_name}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete/{table_name}", tags=["数据写入"])
async def delete_records(
    table_name: str,
    filters: dict,
    api_key_valid: bool = Depends(verify_api_key)
):
    """删除记录（软删除）"""
    try:
        # 验证表名安全性
        allowed_tables = [
            "persons", "colleges", "majors", "classes", "departments", "courses", 
            "course_instances", "enrollments", "grades", "announcements", 
            "research_projects", "assets", "books", "borrow_records", 
            "transactions", "campus_cards", "library_seats", "user_reading_records",
            "card_operations", "seat_reservations", "user_bookmarks"
        ]
        
        if table_name not in allowed_tables:
            raise HTTPException(status_code=400, detail=f"表 {table_name} 不允许删除")
        
        db = next(get_db())
        from sqlalchemy import text
        
        # 软删除：设置is_deleted=1
        where_conditions = []
        params = {}
        
        for field, value in filters.items():
            where_conditions.append(f"{field} = :{field}")
            params[field] = value
        
        # 添加删除时间
        params["deleted_at"] = datetime.now().isoformat()
        
        sql = f"UPDATE {table_name} SET is_deleted = 1, deleted_at = :deleted_at"
        if where_conditions:
            sql += f" WHERE {' AND '.join(where_conditions)}"
        
        logger.info(f"执行软删除: {sql}")
        
        # 执行删除
        result = db.execute(text(sql), params)
        db.commit()
        
        return create_response(
            msg=f"Records in {table_name} deleted successfully",
            data={
                "table_name": table_name,
                "affected_rows": result.rowcount,
                "filters": filters,
                "deleted_at": params["deleted_at"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete from {table_name}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


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