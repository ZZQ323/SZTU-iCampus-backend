"""
事件接口
提供事件列表、详情查看、流式数据等功能
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()

# 模拟事件数据
MOCK_EVENTS = [
    {
        "id": 1,
        "title": "计算机学院学术讲座",
        "description": "邀请知名专家进行人工智能前沿技术分享",
        "event_type": "academic",
        "status": "upcoming",
        "start_time": (datetime.now() + timedelta(days=2)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=2, hours=2)).isoformat(),
        "location": "C1-101大礼堂",
        "organizer": "计算机学院",
        "max_participants": 200,
        "current_participants": 156,
        "registration_required": True,
        "registration_deadline": (datetime.now() + timedelta(days=1)).isoformat(),
        "tags": ["学术", "AI", "技术"],
        "image": "/images/events/ai_lecture.jpg"
    },
    {
        "id": 2,
        "title": "校园马拉松比赛",
        "description": "年度校园马拉松比赛，强身健体，挑战自我",
        "event_type": "sports",
        "status": "registration",
        "start_time": (datetime.now() + timedelta(days=7)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=7, hours=3)).isoformat(),
        "location": "校园跑道",
        "organizer": "体育部",
        "max_participants": 500,
        "current_participants": 342,
        "registration_required": True,
        "registration_deadline": (datetime.now() + timedelta(days=5)).isoformat(),
        "tags": ["体育", "马拉松", "健康"],
        "image": "/images/events/marathon.jpg"
    },
    {
        "id": 3,
        "title": "文艺晚会",
        "description": "庆祝建校周年文艺晚会，精彩节目不容错过",
        "event_type": "cultural",
        "status": "ongoing",
        "start_time": (datetime.now() - timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "location": "大学生活动中心",
        "organizer": "学生会",
        "max_participants": 800,
        "current_participants": 750,
        "registration_required": False,
        "registration_deadline": None,
        "tags": ["文艺", "表演", "庆典"],
        "image": "/images/events/cultural_show.jpg"
    },
    {
        "id": 4,
        "title": "创业项目展示会",
        "description": "学生创业项目展示和投资对接会",
        "event_type": "business",
        "status": "completed",
        "start_time": (datetime.now() - timedelta(days=3)).isoformat(),
        "end_time": (datetime.now() - timedelta(days=3, hours=-4)).isoformat(),
        "location": "创业园区",
        "organizer": "创新创业中心",
        "max_participants": 150,
        "current_participants": 138,
        "registration_required": True,
        "registration_deadline": (datetime.now() - timedelta(days=5)).isoformat(),
        "tags": ["创业", "投资", "项目"],
        "image": "/images/events/startup_demo.jpg"
    },
    {
        "id": 5,
        "title": "社团招新大会",
        "description": "各大社团集中招新，发现你的兴趣和才能",
        "event_type": "social",
        "status": "upcoming",
        "start_time": (datetime.now() + timedelta(days=14)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=14, hours=6)).isoformat(),
        "location": "中央广场",
        "organizer": "社团联合会",
        "max_participants": 1000,
        "current_participants": 0,
        "registration_required": False,
        "registration_deadline": None,
        "tags": ["社团", "招新", "兴趣"],
        "image": "/images/events/club_recruitment.jpg"
    }
]


@router.get("/", summary="获取事件列表")
async def get_events(
    event_type: Optional[str] = Query(None, description="事件类型：academic, sports, cultural, business, social"),
    status: Optional[str] = Query(None, description="事件状态：upcoming, ongoing, completed, registration"),
    location: Optional[str] = Query(None, description="事件地点"),
    organizer: Optional[str] = Query(None, description="主办方"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量"),
    db: Session = Depends(get_db)
):
    """获取事件列表"""
    
    # 过滤事件
    filtered_events = MOCK_EVENTS.copy()
    
    if event_type:
        filtered_events = [e for e in filtered_events if e.get("event_type") == event_type]
    
    if status:
        filtered_events = [e for e in filtered_events if e.get("status") == status]
    
    if location:
        filtered_events = [e for e in filtered_events if location.lower() in e.get("location", "").lower()]
    
    if organizer:
        filtered_events = [e for e in filtered_events if organizer.lower() in e.get("organizer", "").lower()]
    
    # 排序：即将开始的优先，然后按开始时间排序
    filtered_events.sort(key=lambda x: (
        x.get("status") != "upcoming",
        x.get("status") != "ongoing", 
        x.get("start_time", "")
    ))
    
    # 分页
    total = len(filtered_events)
    paginated_events = filtered_events[offset:offset + limit]
    
    # 统计信息
    stats = {
        "total": total,
        "upcoming": len([e for e in MOCK_EVENTS if e.get("status") == "upcoming"]),
        "ongoing": len([e for e in MOCK_EVENTS if e.get("status") == "ongoing"]),
        "registration": len([e for e in MOCK_EVENTS if e.get("status") == "registration"]),
        "completed": len([e for e in MOCK_EVENTS if e.get("status") == "completed"])
    }
    
    return {
        "status": "success",
        "data": {
            "events": paginated_events,
            "stats": stats,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        },
        "timestamp": datetime.now().isoformat()
    }





@router.post("/{event_id}/register", summary="报名参加事件")
async def register_event(
    event_id: int,
    participant_info: dict,
    db: Session = Depends(get_db)
):
    """报名参加事件"""
    
    # 查找事件
    event = next((e for e in MOCK_EVENTS if e["id"] == event_id), None)
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    # 检查报名状态
    if not event.get("registration_required", False):
        raise HTTPException(status_code=400, detail="该事件无需报名")
    
    if event.get("status") not in ["upcoming", "registration"]:
        raise HTTPException(status_code=400, detail="该事件当前不接受报名")
    
    # 检查报名截止时间
    if event.get("registration_deadline"):
        deadline = datetime.fromisoformat(event["registration_deadline"])
        if datetime.now() > deadline:
            raise HTTPException(status_code=400, detail="报名已截止")
    
    # 检查人数限制
    if event.get("current_participants", 0) >= event.get("max_participants", 0):
        raise HTTPException(status_code=400, detail="报名人数已满")
    
    # 模拟报名成功
    event["current_participants"] = event.get("current_participants", 0) + 1
    
    return {
        "status": "success",
        "message": "报名成功",
        "data": {
            "event_id": event_id,
            "event_title": event["title"],
            "registration_number": f"REG{event_id}{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "participant_count": event["current_participants"],
            "remaining_slots": event["max_participants"] - event["current_participants"]
        },
        "timestamp": datetime.now().isoformat()
    }


@router.delete("/{event_id}/register", summary="取消事件报名")
async def cancel_registration(
    event_id: int,
    db: Session = Depends(get_db)
):
    """取消事件报名"""
    
    # 查找事件
    event = next((e for e in MOCK_EVENTS if e["id"] == event_id), None)
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    # 模拟取消报名
    if event.get("current_participants", 0) > 0:
        event["current_participants"] -= 1
    
    return {
        "status": "success",
        "message": "取消报名成功",
        "data": {
            "event_id": event_id,
            "event_title": event["title"],
            "participant_count": event["current_participants"],
            "available_slots": event["max_participants"] - event["current_participants"]
        },
        "timestamp": datetime.now().isoformat()
    }


@router.get("/stream", summary="事件流式数据")
async def get_events_stream():
    """获取事件流式数据（SSE）"""
    
    async def generate_event_stream():
        """生成事件流数据"""
        counter = 0
        
        while True:
            # 模拟实时事件数据
            now = datetime.now()
            
            # 随机选择一个事件类型和状态更新
            import random
            event_types = ["academic", "sports", "cultural", "business", "social"]
            statuses = ["upcoming", "ongoing", "registration"]
            
            event_data = {
                "id": f"stream_{counter}",
                "type": "event_update",
                "timestamp": now.isoformat(),
                "data": {
                    "event_id": random.randint(1, 5),
                    "event_type": random.choice(event_types),
                    "status": random.choice(statuses),
                    "title": f"实时事件更新 {counter}",
                    "message": f"事件状态更新 - {now.strftime('%H:%M:%S')}",
                    "participant_count": random.randint(50, 200),
                    "location": "随机地点",
                    "urgency": random.choice(["low", "medium", "high"])
                }
            }
            
            # SSE格式输出
            yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
            
            counter += 1
            await asyncio.sleep(3)  # 每3秒推送一次
    
    return StreamingResponse(
        generate_event_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )


@router.get("/upcoming/today", summary="获取今日即将开始的事件")
async def get_today_upcoming_events(
    db: Session = Depends(get_db)
):
    """获取今日即将开始的事件"""
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    today_events = []
    for event in MOCK_EVENTS:
        event_start = datetime.fromisoformat(event["start_time"])
        if today_start <= event_start < today_end and event["status"] in ["upcoming", "ongoing"]:
            today_events.append(event)
    
    # 按开始时间排序
    today_events.sort(key=lambda x: x["start_time"])
    
    return {
        "status": "success",
        "data": {
            "events": today_events,
            "count": len(today_events),
            "date": now.date().isoformat()
        },
        "timestamp": datetime.now().isoformat()
    }


@router.get("/stats/summary", summary="获取事件统计摘要")
async def get_event_stats(
    db: Session = Depends(get_db)
):
    """获取事件统计摘要"""
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)
    
    stats = {
        "total": len(MOCK_EVENTS),
        "today": len([e for e in MOCK_EVENTS if today_start <= datetime.fromisoformat(e["start_time"]) < today_start + timedelta(days=1)]),
        "this_week": len([e for e in MOCK_EVENTS if datetime.fromisoformat(e["start_time"]) >= week_start]),
        "this_month": len([e for e in MOCK_EVENTS if datetime.fromisoformat(e["start_time"]) >= month_start]),
        "by_type": {
            "academic": len([e for e in MOCK_EVENTS if e.get("event_type") == "academic"]),
            "sports": len([e for e in MOCK_EVENTS if e.get("event_type") == "sports"]),
            "cultural": len([e for e in MOCK_EVENTS if e.get("event_type") == "cultural"]),
            "business": len([e for e in MOCK_EVENTS if e.get("event_type") == "business"]),
            "social": len([e for e in MOCK_EVENTS if e.get("event_type") == "social"])
        },
        "by_status": {
            "upcoming": len([e for e in MOCK_EVENTS if e.get("status") == "upcoming"]),
            "ongoing": len([e for e in MOCK_EVENTS if e.get("status") == "ongoing"]),
            "registration": len([e for e in MOCK_EVENTS if e.get("status") == "registration"]),
            "completed": len([e for e in MOCK_EVENTS if e.get("status") == "completed"])
        },
        "total_participants": sum([e.get("current_participants", 0) for e in MOCK_EVENTS]),
        "average_attendance": round(sum([e.get("current_participants", 0) / max(e.get("max_participants", 1), 1) for e in MOCK_EVENTS]) / len(MOCK_EVENTS) * 100, 1)
    }
    
    return {
        "status": "success",
        "data": stats,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/{event_id}", summary="获取事件详情")
async def get_event_detail(
    event_id: int,
    db: Session = Depends(get_db)
):
    """获取事件详情"""
    
    # 查找事件
    event = next((e for e in MOCK_EVENTS if e["id"] == event_id), None)
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    # 添加详细信息
    event_detail = event.copy()
    event_detail.update({
        "detailed_description": f"{event['description']}\n\n活动详情：\n• 主题丰富，内容精彩\n• 专业团队组织\n• 现场互动环节\n• 精美礼品赠送",
        "schedule": [
            {"time": "14:00-14:30", "activity": "签到入场"},
            {"time": "14:30-15:30", "activity": "主题演讲"},
            {"time": "15:30-16:00", "activity": "互动问答"},
            {"time": "16:00-16:30", "activity": "自由交流"}
        ],
        "requirements": [
            "请提前10分钟到场",
            "携带学生证或身份证",
            "保持会场秩序",
            "禁止录音录像"
        ],
        "contact": {
            "phone": "0755-12345678",
            "email": "events@sztu.edu.cn",
            "wechat": "SZTU_Events"
        }
    })
    
    return {
        "status": "success",
        "data": event_detail,
        "timestamp": datetime.now().isoformat()
    } 