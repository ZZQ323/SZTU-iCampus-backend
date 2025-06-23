"""
阅读记录模块 API
提供阅读记录、书签、分享等功能
"""
import sqlite3
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.deps import get_current_user

router = APIRouter()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('../../data-service/sztu_campus.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.post("/record", summary="记录阅读行为")
async def record_reading(
    content_type: str,
    content_id: str,
    read_duration: int = 0,
    current_user = Depends(get_current_user)
):
    """记录阅读行为"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        record_id = f"RR{datetime.now().strftime('%Y%m%d%H%M%S')}{person_id[-4:]}"
        
        # 检查是否已有阅读记录
        cursor.execute("""
            SELECT record_id FROM user_reading_records 
            WHERE user_id = ? AND content_type = ? AND content_id = ?
        """, (person_id, content_type, content_id))
        
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有记录
            cursor.execute("""
                UPDATE user_reading_records 
                SET last_read_time = CURRENT_TIMESTAMP,
                    read_count = read_count + 1,
                    read_duration = read_duration + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE record_id = ?
            """, (read_duration, existing["record_id"]))
        else:
            # 创建新记录
            cursor.execute("""
                INSERT INTO user_reading_records
                (record_id, user_id, content_type, content_id, 
                 first_read_time, last_read_time, read_count, read_duration,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, ?, 
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (record_id, person_id, content_type, content_id, read_duration))
        
        conn.commit()
        
        return {
            "code": 0,
            "message": "阅读记录成功",
            "data": {
                "record_id": record_id,
                "content_type": content_type,
                "content_id": content_id
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"记录失败: {str(e)}")
    finally:
        conn.close()


@router.get("/history", summary="获取阅读历史")
async def get_reading_history(
    content_type: Optional[str] = Query(None, description="内容类型"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量"),
    current_user = Depends(get_current_user)
):
    """获取阅读历史"""
    
    # 模拟阅读历史数据
    history = [
        {
            "record_id": "RR20250115001",
            "content_type": "announcement",
            "content_id": "ANN2025001",
            "content_title": "关于2024年寒假放假安排的通知",
            "first_read_time": "2025-01-15T10:00:00Z",
            "last_read_time": "2025-01-15T10:05:00Z",
            "read_count": 2,
            "read_duration": 300,
            "is_liked": False,
            "is_bookmarked": True
        },
        {
            "record_id": "RR20250115002",
            "content_type": "event",
            "content_id": "EV2025001",
            "content_title": "深圳技术大学第十二届运动会开幕式通知",
            "first_read_time": "2025-01-14T14:30:00Z",
            "last_read_time": "2025-01-14T14:35:00Z",
            "read_count": 1,
            "read_duration": 180,
            "is_liked": True,
            "is_bookmarked": False
        }
    ]
    
    if content_type:
        history = [h for h in history if h["content_type"] == content_type]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "history": history[offset:offset + limit],
            "pagination": {
                "total": len(history),
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < len(history)
            }
        },
        "timestamp": datetime.now().isoformat()
    }


@router.post("/bookmark", summary="添加书签")
async def add_bookmark(
    content_type: str,
    content_id: str,
    content_title: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """添加书签"""
    
    person_id = current_user.get("person_id")
    bookmark_id = f"BM{datetime.now().strftime('%Y%m%d%H%M%S')}{person_id[-4:]}"
    
    # 模拟添加书签
    bookmark = {
        "bookmark_id": bookmark_id,
        "content_type": content_type,
        "content_id": content_id,
        "content_title": content_title or "未知标题",
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "code": 0,
        "message": "书签添加成功",
        "data": bookmark,
        "timestamp": datetime.now().isoformat()
    }


@router.delete("/bookmark/{bookmark_id}", summary="删除书签")
async def delete_bookmark(
    bookmark_id: str,
    current_user = Depends(get_current_user)
):
    """删除书签"""
    
    return {
        "code": 0,
        "message": "书签删除成功",
        "data": {"bookmark_id": bookmark_id},
        "timestamp": datetime.now().isoformat()
    }


@router.get("/bookmarks", summary="获取书签列表")
async def get_bookmarks(
    content_type: Optional[str] = Query(None, description="内容类型"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量"),
    current_user = Depends(get_current_user)
):
    """获取书签列表"""
    
    # 模拟书签数据
    bookmarks = [
        {
            "bookmark_id": "BM20250115001",
            "content_type": "announcement",
            "content_id": "ANN2025001",
            "content_title": "关于2024年寒假放假安排的通知",
            "created_at": "2025-01-15T10:05:00Z"
        },
        {
            "bookmark_id": "BM20250114001",
            "content_type": "book",
            "content_id": "BK2025000001",
            "content_title": "一直商品注册",
            "created_at": "2025-01-14T16:20:00Z"
        }
    ]
    
    if content_type:
        bookmarks = [b for b in bookmarks if b["content_type"] == content_type]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "bookmarks": bookmarks[offset:offset + limit],
            "pagination": {
                "total": len(bookmarks),
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < len(bookmarks)
            }
        },
        "timestamp": datetime.now().isoformat()
    }


@router.post("/share", summary="分享内容")
async def share_content(
    content_type: str,
    content_id: str,
    share_method: str = "link",
    current_user = Depends(get_current_user)
):
    """分享内容"""
    
    person_id = current_user.get("person_id")
    share_id = f"SH{datetime.now().strftime('%Y%m%d%H%M%S')}{person_id[-4:]}"
    
    share_info = {
        "share_id": share_id,
        "content_type": content_type,
        "content_id": content_id,
        "share_method": share_method,
        "share_url": f"https://icamp.sztu.edu.cn/share/{content_type}/{content_id}",
        "share_code": f"IC{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "code": 0,
        "message": "分享成功",
        "data": share_info,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/analytics", summary="获取阅读分析")
async def get_reading_analytics(
    period: str = Query("week", description="统计周期: week, month, year"),
    current_user = Depends(get_current_user)
):
    """获取阅读分析"""
    
    # 模拟阅读分析数据
    analytics = {
        "period": period,
        "total_read_count": 45,
        "total_read_duration": 7200,  # 秒
        "avg_daily_reads": 6.4,
        "favorite_categories": [
            {"category": "announcement", "count": 18},
            {"category": "book", "count": 12},
            {"category": "event", "count": 8},
            {"category": "notice", "count": 7}
        ],
        "reading_trend": [
            {"date": "2025-01-09", "count": 5},
            {"date": "2025-01-10", "count": 8},
            {"date": "2025-01-11", "count": 6},
            {"date": "2025-01-12", "count": 7},
            {"date": "2025-01-13", "count": 4},
            {"date": "2025-01-14", "count": 9},
            {"date": "2025-01-15", "count": 6}
        ],
        "peak_hours": [
            {"hour": 9, "count": 8},
            {"hour": 14, "count": 12},
            {"hour": 20, "count": 15}
        ]
    }
    
    return {
        "code": 0,
        "message": "success",
        "data": analytics,
        "timestamp": datetime.now().isoformat()
    } 