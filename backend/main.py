from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
import json
import uvicorn
from datetime import datetime

from app.database import get_db, engine
from app.models import announcement as models, schedule as schedule_models, notice as notice_models, event as event_models, grade as grade_models
from app.schemas import announcement as schemas, schedule as schedule_schemas, notice as notice_schemas, event as event_schemas, grade as grade_schemas
from app.api.v1.endpoints import auth
from app.core.security import verify_token

# 创建数据库表
models.Base.metadata.create_all(bind=engine)
schedule_models.Base.metadata.create_all(bind=engine)
notice_models.Base.metadata.create_all(bind=engine)
event_models.Base.metadata.create_all(bind=engine)
grade_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SZTU iCampus API",
    description="深圳技术大学校园服务统一入口API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 包含认证路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "欢迎使用深圳技术大学校园服务API"}

@app.get("/api/announcements")
async def get_announcements_public(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取校园公告列表（公开接口，无需认证）
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    """
    announcements = db.query(models.Announcement).order_by(
        models.Announcement.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    # 转换为前端期望的格式
    announcement_list = []
    for ann in announcements:
        announcement_list.append({
            "id": ann.id,
            "title": ann.title,
            "content": ann.content,
            "department": ann.department,
            "date": ann.created_at.strftime("%Y-%m-%d"),
            "time": ann.created_at.strftime("%H:%M")
        })
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "announcements": announcement_list,
            "total": len(announcement_list)
        }
    }

@app.get("/api/announcements/secure", response_model=List[schemas.Announcement])
async def get_announcements_secure(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    获取校园公告列表（需要认证）
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    """
    # 验证token
    verify_token(token)
    
    announcements = db.query(models.Announcement).offset(skip).limit(limit).all()
    return announcements

@app.get("/api/announcements/stream")
async def get_announcements_stream(
    db: Session = Depends(get_db)
):
    """
    使用流式响应获取校园公告（无需认证）
    """
    async def generate():
        announcements = db.query(models.Announcement).order_by(
            models.Announcement.created_at.desc()
        ).all()
        
        for announcement in announcements:
            data = {
                "id": announcement.id,
                "title": announcement.title,
                "content": announcement.content,
                "department": announcement.department,
                "created_at": announcement.created_at.isoformat(),
                "updated_at": announcement.updated_at.isoformat()
            }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    
    return Response(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/api/announcements", response_model=schemas.Announcement)
async def create_announcement(
    announcement: schemas.AnnouncementCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    创建新的校园公告（需要认证）
    """
    # 验证token
    verify_token(token)
    
    db_announcement = models.Announcement(**announcement.dict())
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement

@app.get("/api/schedule")
async def get_schedule(
    student_id: str = "2024001",
    week: int = 1,
    db: Session = Depends(get_db)
):
    """
    获取课表信息（公开接口，无需认证）
    - **student_id**: 学生学号
    - **week**: 周次
    """
    schedules = db.query(schedule_models.Schedule).filter(
        schedule_models.Schedule.student_id == student_id
    ).all()
    
    # 转换为前端期望的格式
    schedule_list = []
    for schedule in schedules:
        schedule_list.append({
            "id": schedule.id,
            "course_name": schedule.course_name,
            "teacher": schedule.teacher,
            "classroom": schedule.classroom,
            "week_day": schedule.week_day,
            "start_time": schedule.start_time,
            "end_time": schedule.end_time,
            "weeks": schedule.weeks,
            "course_type": schedule.course_type,
            "credits": schedule.credits
        })
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "schedules": schedule_list,
            "total": len(schedule_list),
            "current_week": week,
            "student_id": student_id
        }
    }

@app.get("/api/notices")
async def get_notices(
    skip: int = 0,
    limit: int = 10,
    department: str = None,
    notice_type: str = None,
    db: Session = Depends(get_db)
):
    """
    获取部门通知列表（公开接口，无需认证）
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **department**: 按部门筛选
    - **notice_type**: 按通知类型筛选
    """
    query = db.query(notice_models.Notice).filter(
        notice_models.Notice.is_active == 1
    )
    
    # 按部门筛选
    if department:
        query = query.filter(notice_models.Notice.department == department)
    
    # 按通知类型筛选
    if notice_type:
        query = query.filter(notice_models.Notice.notice_type == notice_type)
    
    notices = query.order_by(
        notice_models.Notice.priority.desc(),
        notice_models.Notice.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    # 转换为前端期望的格式
    notice_list = []
    for notice in notices:
        notice_list.append({
            "id": notice.id,
            "title": notice.title,
            "content": notice.content,
            "department": notice.department,
            "notice_type": notice.notice_type.value if notice.notice_type else "normal",
            "priority": notice.priority.value if notice.priority else "medium",
            "target_audience": notice.target_audience,
            "date": notice.created_at.strftime("%Y-%m-%d"),
            "time": notice.created_at.strftime("%H:%M"),
            "effective_date": notice.effective_date.strftime("%Y-%m-%d %H:%M") if notice.effective_date else None,
            "expire_date": notice.expire_date.strftime("%Y-%m-%d %H:%M") if notice.expire_date else None
        })
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "notices": notice_list,
            "total": len(notice_list)
        }
    }

@app.get("/api/notices/stream")
async def get_notices_stream(
    db: Session = Depends(get_db)
):
    """
    使用流式响应获取部门通知（无需认证）
    """
    async def generate():
        notices = db.query(notice_models.Notice).filter(
            notice_models.Notice.is_active == 1
        ).order_by(
            notice_models.Notice.priority.desc(),
            notice_models.Notice.created_at.desc()
        ).all()
        
        for notice in notices:
            data = {
                "id": notice.id,
                "title": notice.title,
                "content": notice.content,
                "department": notice.department,
                "notice_type": notice.notice_type.value if notice.notice_type else "normal",
                "priority": notice.priority.value if notice.priority else "medium",
                "target_audience": notice.target_audience,
                "created_at": notice.created_at.isoformat(),
                "updated_at": notice.updated_at.isoformat() if notice.updated_at else None
            }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    
    return Response(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/api/events")
async def get_events(
    skip: int = 0,
    limit: int = 10,
    event_type: str = None,
    status: str = None,
    organizer: str = None,
    db: Session = Depends(get_db)
):
    """
    获取活动列表（公开接口，无需认证）
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **event_type**: 按活动类型筛选
    - **status**: 按活动状态筛选
    - **organizer**: 按主办方筛选
    """
    query = db.query(event_models.Event).filter(
        event_models.Event.is_active == 1
    )
    
    # 按活动类型筛选
    if event_type:
        query = query.filter(event_models.Event.event_type == event_type)
    
    # 按活动状态筛选
    if status:
        query = query.filter(event_models.Event.status == status)
    
    # 按主办方筛选
    if organizer:
        query = query.filter(event_models.Event.organizer == organizer)
    
    events = query.order_by(
        event_models.Event.start_time.asc()
    ).offset(skip).limit(limit).all()
    
    # 转换为前端期望的格式
    event_list = []
    for event in events:
        event_list.append({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "organizer": event.organizer,
            "event_type": event.event_type.value if event.event_type else "academic",
            "status": event.status.value if event.status else "upcoming",
            "location": event.location,
            "start_time": event.start_time.strftime("%Y-%m-%d %H:%M"),
            "end_time": event.end_time.strftime("%Y-%m-%d %H:%M"),
            "date": event.start_time.strftime("%Y-%m-%d"),
            "time": event.start_time.strftime("%H:%M"),
            "registration_deadline": event.registration_deadline.strftime("%Y-%m-%d %H:%M") if event.registration_deadline else None,
            "max_participants": event.max_participants,
            "current_participants": event.current_participants,
            "contact_info": event.contact_info,
            "requirements": event.requirements
        })
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "events": event_list,
            "total": len(event_list)
        }
    }

@app.get("/api/events/stream")
async def get_events_stream(
    db: Session = Depends(get_db)
):
    """
    使用流式响应获取活动数据（无需认证）
    """
    async def generate():
        events = db.query(event_models.Event).filter(
            event_models.Event.is_active == 1
        ).order_by(
            event_models.Event.start_time.asc()
        ).all()
        
        for event in events:
            data = {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "organizer": event.organizer,
                "event_type": event.event_type.value if event.event_type else "academic",
                "status": event.status.value if event.status else "upcoming",
                "location": event.location,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "created_at": event.created_at.isoformat(),
                "updated_at": event.updated_at.isoformat() if event.updated_at else None
            }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    
    return Response(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/api/grades")
async def get_grades(
    student_id: str = "2024001",
    semester: str = None,
    academic_year: str = None,
    course_type: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    获取学生成绩列表（公开接口，无需认证）
    - **student_id**: 学生学号
    - **semester**: 学期筛选
    - **academic_year**: 学年筛选
    - **course_type**: 课程类型筛选
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    """
    query = db.query(grade_models.Grade).filter(
        grade_models.Grade.student_id == student_id
    )
    
    # 按学期筛选
    if semester:
        query = query.filter(grade_models.Grade.semester == semester)
    
    # 按学年筛选
    if academic_year:
        query = query.filter(grade_models.Grade.academic_year == academic_year)
    
    # 按课程类型筛选
    if course_type:
        query = query.filter(grade_models.Grade.course_type == course_type)
    
    grades = query.order_by(
        grade_models.Grade.academic_year.desc(),
        grade_models.Grade.semester.desc(),
        grade_models.Grade.total_score.desc()
    ).offset(skip).limit(limit).all()
    
    # 计算统计信息
    all_grades = db.query(grade_models.Grade).filter(
        grade_models.Grade.student_id == student_id
    ).all()
    
    total_courses = len(all_grades)
    total_credits = sum(g.credits for g in all_grades)
    avg_score = sum(g.total_score for g in all_grades) / total_courses if total_courses > 0 else 0
    avg_gpa = sum(g.gpa_points for g in all_grades if g.gpa_points) / len([g for g in all_grades if g.gpa_points]) if any(g.gpa_points for g in all_grades) else 0
    pass_count = len([g for g in all_grades if g.status.value == "pass"]) if all_grades else 0
    pass_rate = (pass_count / total_courses * 100) if total_courses > 0 else 0
    
    # 转换为前端期望的格式
    grade_list = []
    for grade in grades:
        grade_list.append({
            "id": grade.id,
            "course_code": grade.course_code,
            "course_name": grade.course_name,
            "course_type": grade.course_type,
            "credits": grade.credits,
            "semester": grade.semester,
            "academic_year": grade.academic_year,
            "teacher_name": grade.teacher_name,
            "regular_score": grade.regular_score,
            "midterm_score": grade.midterm_score,
            "final_score": grade.final_score,
            "total_score": grade.total_score,
            "grade_level": grade.grade_level,
            "gpa_points": grade.gpa_points,
            "status": grade.status.value if grade.status else "pass",
            "class_rank": grade.class_rank,
            "class_total": grade.class_total,
            "exam_date": grade.exam_date.strftime("%Y-%m-%d") if grade.exam_date else None,
            "publish_date": grade.publish_date.strftime("%Y-%m-%d %H:%M") if grade.publish_date else None
        })
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "grades": grade_list,
            "total": len(grade_list),
            "summary": {
                "total_courses": total_courses,
                "total_credits": total_credits,
                "avg_score": round(avg_score, 2),
                "avg_gpa": round(avg_gpa, 2),
                "pass_rate": round(pass_rate, 2),
                "student_id": student_id
            }
        }
    }

@app.get("/api/grades/stream")
async def get_grades_stream(
    student_id: str = "2024001",
    db: Session = Depends(get_db)
):
    """
    使用流式响应获取成绩数据（无需认证）
    """
    async def generate():
        grades = db.query(grade_models.Grade).filter(
            grade_models.Grade.student_id == student_id
        ).order_by(
            grade_models.Grade.academic_year.desc(),
            grade_models.Grade.semester.desc()
        ).all()
        
        for grade in grades:
            data = {
                "id": grade.id,
                "course_code": grade.course_code,
                "course_name": grade.course_name,
                "total_score": grade.total_score,
                "grade_level": grade.grade_level,
                "gpa_points": grade.gpa_points,
                "semester": grade.semester,
                "academic_year": grade.academic_year,
                "created_at": grade.created_at.isoformat(),
                "updated_at": grade.updated_at.isoformat() if grade.updated_at else None
            }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    
    return Response(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 