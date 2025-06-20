"""
通知接口
提供通知列表、详情查看等功能
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()

# 模拟通知数据
MOCK_NOTICES = [
    {
        "id": 1,
        "title": "期末考试安排通知",
        "content": "2024年6月25日-28日进行期末考试，请同学们合理安排复习时间，准时参加考试。",
        "type": "exam",
        "priority": "high",
        "publisher": "教务处",
        "publish_time": (datetime.now() - timedelta(hours=2)).isoformat(),
        "read_status": False,
        "attachments": []
    },
    {
        "id": 2,
        "title": "图书馆闭馆通知",
        "content": "因系统维护，图书馆将于6月22日18:00-23:00暂停服务，给您带来不便敬请谅解。",
        "type": "library",
        "priority": "medium",
        "publisher": "图书馆",
        "publish_time": (datetime.now() - timedelta(hours=5)).isoformat(),
        "read_status": True,
        "attachments": []
    },
    {
        "id": 3,
        "title": "学费缴费截止提醒",
        "content": "请尚未缴费的同学于6月30日前完成学费缴纳，逾期将影响正常选课。",
        "type": "finance",
        "priority": "high",
        "publisher": "财务处",
        "publish_time": (datetime.now() - timedelta(days=1)).isoformat(),
        "read_status": False,
        "attachments": [
            {"name": "缴费指南.pdf", "url": "/files/payment_guide.pdf"}
        ]
    },
    {
        "id": 4,
        "title": "校园网络维护通知",
        "content": "6月23日凌晨2:00-4:00进行校园网络设备维护，期间可能出现网络中断。",
        "type": "technical",
        "priority": "medium",
        "publisher": "信息中心",
        "publish_time": (datetime.now() - timedelta(days=2)).isoformat(),
        "read_status": True,
        "attachments": []
    },
    {
        "id": 5,
        "title": "暑期实习岗位推荐",
        "content": "学院为大家推荐优质实习岗位，详情请查看附件。有意向的同学请及时报名。",
        "type": "career",
        "priority": "medium",
        "publisher": "学院办公室",
        "publish_time": (datetime.now() - timedelta(days=3)).isoformat(),
        "read_status": False,
        "attachments": [
            {"name": "实习岗位列表.xlsx", "url": "/files/internship_list.xlsx"}
        ]
    }
]


@router.get("/", summary="获取通知列表")
async def get_notices(
    type: Optional[str] = Query(None, description="通知类型：exam, library, finance, technical, career"),
    priority: Optional[str] = Query(None, description="优先级：high, medium, low"),
    read_status: Optional[bool] = Query(None, description="阅读状态：true已读, false未读"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量"),
    db: Session = Depends(get_db)
):
    """获取通知列表"""
    
    # 过滤通知
    filtered_notices = MOCK_NOTICES.copy()
    
    if type:
        filtered_notices = [n for n in filtered_notices if n.get("type") == type]
    
    if priority:
        filtered_notices = [n for n in filtered_notices if n.get("priority") == priority]
    
    if read_status is not None:
        filtered_notices = [n for n in filtered_notices if n.get("read_status") == read_status]
    
    # 排序：未读优先，然后按时间倒序
    filtered_notices.sort(key=lambda x: (x.get("read_status", True), x.get("publish_time", "")), reverse=True)
    
    # 分页
    total = len(filtered_notices)
    paginated_notices = filtered_notices[offset:offset + limit]
    
    # 统计信息
    stats = {
        "total": total,
        "unread": len([n for n in MOCK_NOTICES if not n.get("read_status", True)]),
        "high_priority": len([n for n in MOCK_NOTICES if n.get("priority") == "high"]),
        "today": len([n for n in MOCK_NOTICES if n.get("publish_time", "").startswith(datetime.now().date().isoformat())])
    }
    
    return {
        "status": "success",
        "data": {
            "notices": paginated_notices,
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


@router.get("/{notice_id}", summary="获取通知详情")
async def get_notice_detail(
    notice_id: int,
    db: Session = Depends(get_db)
):
    """获取通知详情"""
    
    # 查找通知
    notice = next((n for n in MOCK_NOTICES if n["id"] == notice_id), None)
    
    if not notice:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    # 模拟标记为已读
    notice_copy = notice.copy()
    notice_copy["read_status"] = True
    notice_copy["read_time"] = datetime.now().isoformat()
    
    return {
        "status": "success",
        "data": notice_copy,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/{notice_id}/read", summary="标记通知为已读")
async def mark_notice_read(
    notice_id: int,
    db: Session = Depends(get_db)
):
    """标记通知为已读"""
    
    # 查找通知
    notice = next((n for n in MOCK_NOTICES if n["id"] == notice_id), None)
    
    if not notice:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    # 在实际应用中，这里会更新数据库
    notice["read_status"] = True
    notice["read_time"] = datetime.now().isoformat()
    
    return {
        "status": "success",
        "message": "通知已标记为已读",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/batch/read", summary="批量标记通知为已读")
async def batch_mark_read(
    notice_ids: List[int],
    db: Session = Depends(get_db)
):
    """批量标记通知为已读"""
    
    updated_count = 0
    
    for notice_id in notice_ids:
        notice = next((n for n in MOCK_NOTICES if n["id"] == notice_id), None)
        if notice and not notice.get("read_status", True):
            notice["read_status"] = True
            notice["read_time"] = datetime.now().isoformat()
            updated_count += 1
    
    return {
        "status": "success",
        "message": f"已标记 {updated_count} 条通知为已读",
        "data": {
            "updated_count": updated_count,
            "total_requested": len(notice_ids)
        },
        "timestamp": datetime.now().isoformat()
    }


@router.get("/stats/summary", summary="获取通知统计摘要")
async def get_notice_stats(
    db: Session = Depends(get_db)
):
    """获取通知统计摘要"""
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    
    stats = {
        "total": len(MOCK_NOTICES),
        "unread": len([n for n in MOCK_NOTICES if not n.get("read_status", True)]),
        "today": len([n for n in MOCK_NOTICES if datetime.fromisoformat(n.get("publish_time", "")).date() == now.date()]),
        "this_week": len([n for n in MOCK_NOTICES if datetime.fromisoformat(n.get("publish_time", "")) >= week_start]),
        "by_type": {
            "exam": len([n for n in MOCK_NOTICES if n.get("type") == "exam"]),
            "library": len([n for n in MOCK_NOTICES if n.get("type") == "library"]),
            "finance": len([n for n in MOCK_NOTICES if n.get("type") == "finance"]),
            "technical": len([n for n in MOCK_NOTICES if n.get("type") == "technical"]),
            "career": len([n for n in MOCK_NOTICES if n.get("type") == "career"])
        },
        "by_priority": {
            "high": len([n for n in MOCK_NOTICES if n.get("priority") == "high"]),
            "medium": len([n for n in MOCK_NOTICES if n.get("priority") == "medium"]),
            "low": len([n for n in MOCK_NOTICES if n.get("priority") == "low"])
        }
    }
    
    return {
        "status": "success",
        "data": stats,
        "timestamp": datetime.now().isoformat()
    } 