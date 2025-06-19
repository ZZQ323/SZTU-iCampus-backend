from fastapi import FastAPI, HTTPException, Depends, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
import json
import uvicorn
from datetime import datetime
import asyncio
import random
import time

from app.database import get_db, engine, Base

# 导入模型
from app.models.announcement import Announcement
from app.models.schedule import Schedule
from app.models.notice import Notice
from app.models.event import Event
from app.models.grade import Grade

# from app.api.v1.endpoints import auth
from app.api.v1.api import api_router
from app.core.security import verify_token

# 创建所有数据库表
Base.metadata.create_all(bind=engine)

# 一个名为 app 的 FastAPI 实例
app = FastAPI(
    title="SZTU iCampus API",
    description="深圳技术大学校园服务统一入口API - 基于流式封装技术",
    version="1.0.0"
)

# 配置 CORS 中间件
#   允许所有域访问 API，这对于跨域请求的场景非常重要。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 流式数据缓存和状态管理
class StreamDataManager:
    def __init__(self):
        self.last_announcement_id = 0  # 跟踪最新公告ID
            # 用于跟踪当前已发送的最后一个公告的 ID。
            # 通过它可以实现增量更新，仅发送新公告，而不是重复发送所有公告
        self.last_event_update = time.time() # 存储活跃的SSE连接
            # 它通常在活动的参与人数变化时更新。
        self.active_connections = set() 
            # 在使用 Server-Sent Events (SSE) 推送数据时，服务器会知道哪些客户端正在等待数据
        self.data_cache = {} # 接口响应缓存
            # 用于存储接口响应的数据，减少不必要的数据库查询(存在内存里面了，更快)
    # 获取最新公告
    
    def get_latest_announcements(self, db: Session):
        """获取最新公告数据"""
        announcements = db.query(Announcement).order_by(
            Announcement.created_at.desc()
        ).all() 
        # 查询 Announcement 表中的所有公告
        # 按创建时间（created_at）降序排列，返回所有公告数据
        return announcements
    
    # 获取公告增量数据
    def get_announcement_diff(self, db: Session):
        """
            获取公告增量数据 - 流式封装
            但是有个问题：如果运行一段事件之后，有新用户登录呢，只推送新的吗，那么怎么更新旧的呢？
        """
        current_announcements = self.get_latest_announcements(db)
        
        if not current_announcements:
            return None
        # id 是随着时间增长的吗？
        latest_id = current_announcements[0].id
        
        # 通过ID比对实现增量更新
        # 如果有新的公告（latest_id > self.last_announcement_id），则返回新增的公告
        if latest_id > self.last_announcement_id:
            # 筛选新公告
            new_announcements = [
                ann for ann in current_announcements 
                if ann.id > self.last_announcement_id
            ]
            self.last_announcement_id = latest_id
            return new_announcements
        
        return None
    # 模拟监控活动参与人数变化，并推送
    def simulate_event_participant_change(self, db: Session):
        """
            模拟活动参与人数实时变化 - 流式封装
        """
        events = db.query(Event).filter(
            Event.is_active == 1,
            Event.status == 'upcoming'
        ).all()
        
        if events:
            
            # 随机选择一个活动进行参与人数更新
            event = random.choice(events)
            
            # 模拟参与人数变化（80%概率增加，20%概率减少）
            change = random.choice([1, 1, 1, 1, -1])
            new_count = max(0, min(
                (event.current_participants or 0) + change,
                event.max_participants or 1000
            ))
            
            # 更新数据库
            # 将更新的参与人数保存到数据库
            event.current_participants = new_count
            db.commit()
            
            return {
                "id": event.id,
                "title": event.title,
                "current_participants": new_count,
                "max_participants": event.max_participants,
                "update_type": "participant_change",
                "timestamp": datetime.now().isoformat()
            }
        
        return None

# 全局流式数据管理器
stream_manager = StreamDataManager()

# 安全配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 将 auth.router 中定义的所有认证相关路由（登录、注册、令牌获取等）注册到主应用 app 中
# auth.router是文件里面的一个对象
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "🌊 欢迎使用深圳技术大学校园服务API",
        "features": ["实时数据推送", "智能缓存", "增量更新"],
        "stream_active_connections": len(stream_manager.active_connections)
    }

@app.get("/api/announcements")
async def get_announcements_public(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取校园公告列表（公开接口，智能缓存优化，避免重复查询）
    """
    cache_key = f"announcements_{skip}_{limit}"
    current_time = time.time()
    # 检查有效缓存（30秒内）
    if (cache_key in stream_manager.data_cache and 
        current_time - stream_manager.data_cache[cache_key]['timestamp'] < 30):
        print(f"[API] 📦 使用缓存数据 - 节省{30 - (current_time - stream_manager.data_cache[cache_key]['timestamp']):.1f}秒")
        return stream_manager.data_cache[cache_key]['data']
    # 无缓存时查询数据库
    announcements = db.query(Announcement).order_by(
        Announcement.created_at.desc()
    ).offset(skip).limit(limit).all()
    
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
    
    result = {
        "code": 0,
        "message": "success",
        "data": {
            "announcements": announcement_list,
            "total": len(announcement_list),
            "cached": False,
            "stream_connections": len(stream_manager.active_connections)
        }
    }
    
    # 缓存结果
    stream_manager.data_cache[cache_key] = {
        'data': result,
        'timestamp': current_time
    }
    
    return result

from fastapi.responses import StreamingResponse
@app.get("/api/announcements/stream")
async def get_announcements_stream(db: Session = Depends(get_db)):
    """
    公告流式推送 - 核心流式封装技术展示
    用户体验：新公告发布后立即推送，无需刷新页面
    """
    async def generate():
        connection_id = f"conn_{time.time()}"
        # 1. 新连接注册
        stream_manager.active_connections.add(connection_id)
        
        print(f"[流式推送] 🔗 新连接建立: {connection_id} (总连接数: {len(stream_manager.active_connections)})")
        
        try:
            # 首次连接时发送当前数据
            announcements = stream_manager.get_latest_announcements(db)
            # 2. 首次发送最新3条公告
            for announcement in announcements[:3]:  # 只发送最新3条
                data = {
                    "id": announcement.id,
                    "title": announcement.title,
                    "content": announcement.content,
                    "department": announcement.department,
                    "date": announcement.created_at.strftime("%Y-%m-%d"),
                    "time": announcement.created_at.strftime("%H:%M"),
                    "stream_type": "initial"
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
            
            # 3. 持续推送新公告（流式核心）
            while True:
                await asyncio.sleep(random.uniform(1000, 3000))  # 随机间隔推送新公告
                
                # 模拟新公告发布
                new_announcement_data = {
                    "id": 9999 + random.randint(1, 1000),
                    "title": f"🔔 实时推送测试公告 - {datetime.now().strftime('%H:%M:%S')}",
                    "content": f"这是一条通过流式封装技术实时推送的公告，发布时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}。用户无需刷新页面即可收到最新消息！",
                    "department": "信息技术中心",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M"),
                    "stream_type": "realtime_push"
                }
                # 模拟新公告推送
                print(f"[流式推送] 📢 推送新公告: {new_announcement_data['title']}")
                yield f"data: {json.dumps(new_announcement_data, ensure_ascii=False)}\n\n"
                # 推送成功反馈
                yield f"data: {json.dumps({'type': 'push_success', 'message': '新公告推送成功', 'timestamp': datetime.now().isoformat()}, ensure_ascii=False)}\n\n"
        except Exception as e:
            print(f"[流式推送] ❌ 连接错误: {e}")
        finally:
            stream_manager.active_connections.discard(connection_id)
            print(f"[流式推送] 🔌 连接断开: {connection_id} (剩余连接: {len(stream_manager.active_connections)})")
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Stream-Type": "announcements"
        }
    )

# 注释：课表API已迁移到 /api/v1/schedule，此处删除冗余实现

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
    query = db.query(Notice).filter(
        Notice.is_active == 1
    )
    
    # 按部门筛选
    if department:
        query = query.filter(Notice.department == department)
    
    # 按通知类型筛选
    if notice_type:
        query = query.filter(Notice.notice_type == notice_type)
    
    notices = query.order_by(
        Notice.priority.desc(),
        Notice.created_at.desc()
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
        notices = db.query(Notice).filter(
            Notice.is_active == 1
        ).order_by(
            Notice.priority.desc(),
            Notice.created_at.desc()
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
    query = db.query(Event).filter(
        Event.is_active == 1
    )
    
    # 按活动类型筛选
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    # 按活动状态筛选
    if status:
        query = query.filter(Event.status == status)
    
    # 按主办方筛选
    if organizer:
        query = query.filter(Event.organizer == organizer)
    
    events = query.order_by(
        Event.start_time.asc()
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
    🎯 活动流式推送 - 实时参与人数更新
    用户体验：看到活动参与人数实时跳动，增强互动感
    """
    async def generate():
        connection_id = f"event_conn_{time.time()}"
        stream_manager.active_connections.add(connection_id)
        
        print(f"[活动流] 🔗 活动流连接建立: {connection_id}")
        
        try:
            # 首次发送当前活动数据
            events = db.query(Event).filter(
                Event.is_active == 1
            ).order_by(Event.start_time.asc()).all()
            
            for event in events:
                data = {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "organizer": event.organizer,
                    "event_type": event.event_type.value if event.event_type else "academic",
                    "status": event.status.value if event.status else "upcoming",
                    "location": event.location,
                    "start_time": event.start_time.strftime("%Y-%m-%d %H:%M"),
                    "end_time": event.end_time.strftime("%Y-%m-%d %H:%M"),
                    "max_participants": event.max_participants,
                    "current_participants": event.current_participants,
                    "stream_type": "initial"
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
            
            # 🚀 实时推送参与人数变化 - 流式封装的视觉亮点
            while True:
                await asyncio.sleep(random.uniform(5, 15))  # 随机间隔更新
                
                update_data = stream_manager.simulate_event_participant_change(db)
                if update_data:
                    print(f"[活动流] 👥 推送参与人数更新: {update_data['title']} -> {update_data['current_participants']}")
                    yield f"data: {json.dumps(update_data, ensure_ascii=False)}\n\n"
                    
                    # 用户体验反馈
                    feedback = {
                        "type": "participant_update_success",
                        "message": f"活动参与人数实时更新",
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(feedback, ensure_ascii=False)}\n\n"
        
        except Exception as e:
            print(f"[活动流] ❌ 连接错误: {e}")
        finally:
            stream_manager.active_connections.discard(connection_id)
            print(f"[活动流] 🔌 连接断开: {connection_id}")
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Stream-Type": "events"
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
    query = db.query(Grade).filter(
        Grade.student_id == student_id
    )
    
    # 按学期筛选
    if semester:
        query = query.filter(Grade.semester == semester)
    
    # 按学年筛选
    if academic_year:
        query = query.filter(Grade.academic_year == academic_year)
    
    # 按课程类型筛选
    if course_type:
        query = query.filter(Grade.course_type == course_type)
    
    grades = query.order_by(
        Grade.academic_year.desc(),
        Grade.semester.desc(),
        Grade.total_score.desc()
    ).offset(skip).limit(limit).all()
    
    # 计算统计信息
    all_grades = db.query(Grade).filter(
        Grade.student_id == student_id
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
        grades = db.query(Grade).filter(
            Grade.student_id == student_id
        ).order_by(
            Grade.academic_year.desc(),
            Grade.semester.desc()
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
    """
    启动FastAPI应用服务器
    开发环境配置：
    - host: 0.0.0.0 (允许外部访问)
    - port: 8000 (默认端口)
    - reload: True (开发模式下自动重载)
    """
    uvicorn.run(
        "main:app",
        # host="0.0.0.0",
        host="127.0.0.1",  # 只允许本机访问
        port=8000,
        reload=True,
        # reload=False,  # 生产环境关闭自动重载
        log_level="info"
    ) 