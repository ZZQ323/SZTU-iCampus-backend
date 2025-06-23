"""
活动模块 API
提供活动列表、详情、报名、签到等功能
"""
import sqlite3
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.deps import get_current_user

router = APIRouter()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('../../data-service/sztu_campus.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/", summary="获取活动列表")
async def get_events(
    event_type: Optional[str] = Query(None, description="活动类型"),
    status: Optional[str] = Query(None, description="活动状态"),
    organizer: Optional[str] = Query(None, description="主办方"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量")
):
    """获取活动列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 构建查询条件
        where_conditions = ["is_deleted = 0"]
        params = []
        
        if event_type:
            where_conditions.append("event_type = ?")
            params.append(event_type)
        
        if status:
            where_conditions.append("status = ?")
            params.append(status)
        
        if organizer:
            where_conditions.append("organizer_name LIKE ?")
            params.append(f"%{organizer}%")
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询活动列表
        sql = f"""
            SELECT event_id, title, short_description, event_type, category,
                   organizer_name, start_time, end_time, location_name,
                   max_participants, current_participants, registration_required,
                   registration_fee, status, poster_url, view_count
            FROM events
            WHERE {where_clause}
            ORDER BY start_time DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [limit, offset])
        events = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "events": events,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": len(events) == limit
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/{event_id}", summary="获取活动详情")
async def get_event_detail(event_id: str):
    """获取活动详情"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = """
            SELECT * FROM events
            WHERE event_id = ? AND is_deleted = 0
        """
        cursor.execute(sql, (event_id,))
        event = cursor.fetchone()
        
        if not event:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        event_dict = dict(event)
        
        # 更新浏览次数
        cursor.execute(
            "UPDATE events SET view_count = view_count + 1 WHERE event_id = ?",
            (event_id,)
        )
        conn.commit()
        
        return {
            "code": 0,
            "message": "success",
            "data": event_dict,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()


@router.post("/", summary="创建活动")
async def create_event(
    title: str,
    description: str,
    event_type: str,
    start_time: str,
    end_time: str,
    location_name: str,
    max_participants: Optional[int] = None,
    current_user = Depends(get_current_user)
):
    """创建活动（教师/管理员）"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        organizer_name = current_user.get("name", "未知用户")
        
        event_id = f"EV{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute("""
            INSERT INTO events 
            (event_id, title, description, event_type, organizer_id, organizer_name,
             start_time, end_time, location_name, max_participants, current_participants,
             status, created_at, updated_at, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'planned', 
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
        """, (event_id, title, description, event_type, person_id, organizer_name,
              start_time, end_time, location_name, max_participants))
        
        conn.commit()
        
        return {
            "code": 0,
            "message": "活动创建成功",
            "data": {"event_id": event_id},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")
    finally:
        conn.close()


@router.post("/{event_id}/register", summary="报名活动")
async def register_event(
    event_id: str,
    current_user = Depends(get_current_user)
):
    """报名活动"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        participant_name = current_user.get("name", "未知用户")
        
        # 检查活动是否存在
        cursor.execute("SELECT * FROM events WHERE event_id = ? AND is_deleted = 0", (event_id,))
        event = cursor.fetchone()
        
        if not event:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        # 检查是否已报名
        cursor.execute("""
            SELECT registration_id FROM event_registrations 
            WHERE event_id = ? AND participant_id = ? AND is_deleted = 0
        """, (event_id, person_id))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="您已报名此活动")
        
        # 创建报名记录
        registration_id = f"REG{datetime.now().strftime('%Y%m%d%H%M%S')}{person_id[-4:]}"
        
        cursor.execute("""
            INSERT INTO event_registrations
            (registration_id, event_id, participant_id, participant_name,
             registration_time, registration_status, created_at, updated_at, is_deleted)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 'registered', 
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
        """, (registration_id, event_id, person_id, participant_name))
        
        # 更新参与人数
        cursor.execute("""
            UPDATE events 
            SET current_participants = current_participants + 1
            WHERE event_id = ?
        """, (event_id,))
        
        conn.commit()
        
        return {
            "code": 0,
            "message": "报名成功",
            "data": {"registration_id": registration_id},
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"报名失败: {str(e)}")
    finally:
        conn.close()


@router.delete("/{event_id}/register", summary="取消报名")
async def cancel_registration(
    event_id: str,
    current_user = Depends(get_current_user)
):
    """取消报名"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        
        # 查询报名记录
        cursor.execute("""
            SELECT registration_id FROM event_registrations
            WHERE event_id = ? AND participant_id = ? AND registration_status = 'registered' AND is_deleted = 0
        """, (event_id, person_id))
        
        registration = cursor.fetchone()
        if not registration:
            raise HTTPException(status_code=404, detail="未找到报名记录")
        
        # 取消报名
        cursor.execute("""
            UPDATE event_registrations 
            SET registration_status = 'cancelled', updated_at = CURRENT_TIMESTAMP
            WHERE registration_id = ?
        """, (registration["registration_id"],))
        
        # 更新参与人数
        cursor.execute("""
            UPDATE events 
            SET current_participants = current_participants - 1
            WHERE event_id = ?
        """, (event_id,))
        
        conn.commit()
        
        return {
            "code": 0,
            "message": "取消报名成功",
            "data": {},
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"取消失败: {str(e)}")
    finally:
        conn.close() 