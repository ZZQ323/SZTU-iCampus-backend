"""
公告接口
提供校园公告的查询、发布、管理等功能
"""
import sqlite3
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('../../data-service/sztu_campus.db')
    conn.row_factory = sqlite3.Row  # 启用字典式访问
    return conn

@router.get("/", summary="获取公告列表")
async def get_announcements(
    category: Optional[str] = Query(None, description="公告分类"),
    department: Optional[str] = Query(None, description="发布部门"),
    priority: Optional[str] = Query(None, description="优先级"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量")
):
    """获取公告列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 构建查询条件
        where_conditions = ["is_deleted = 0", "status = 'published'"]
        params = []
        
        if category:
            where_conditions.append("category = ?")
            params.append(category)
        
        if department:
            where_conditions.append("department = ?")
            params.append(department)
        
        if priority:
            where_conditions.append("priority = ?")
            params.append(priority)
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM announcements WHERE {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]
        
        # 查询公告列表
        sql = f"""
            SELECT announcement_id, title, content, summary, publisher_name, department, 
                   category, priority, is_urgent, is_pinned, publish_time, view_count,
                   target_audience, cover_image_url
            FROM announcements 
            WHERE {where_clause}
            ORDER BY is_pinned DESC, publish_time DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [limit, offset])
        announcements = [dict(row) for row in cursor.fetchall()]
        
        # 统计信息
        cursor.execute("SELECT COUNT(*) FROM announcements WHERE is_deleted = 0 AND priority = 'high'")
        high_priority_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM announcements WHERE is_deleted = 0 AND is_urgent = 1")
        urgent_count = cursor.fetchone()[0]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "announcements": announcements,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total
                },
                "stats": {
                    "total": total,
                    "high_priority": high_priority_count,
                    "urgent": urgent_count
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/{announcement_id}", summary="获取公告详情")
async def get_announcement_detail(announcement_id: str):
    """获取公告详情"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 查询公告详情
        sql = """
            SELECT announcement_id, title, content, content_html, summary, publisher_id, 
                   publisher_name, department, category, priority, status, is_urgent, 
                   is_pinned, publish_time, effective_date, expire_date, target_audience,
                   target_colleges, target_majors, target_grades, view_count, like_count,
                   comment_count, attachments, cover_image_url, created_at, updated_at
            FROM announcements 
            WHERE announcement_id = ? AND is_deleted = 0
        """
        cursor.execute(sql, (announcement_id,))
        announcement = cursor.fetchone()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="公告不存在")
        
        announcement_dict = dict(announcement)
        
        # 更新浏览次数
        cursor.execute(
            "UPDATE announcements SET view_count = view_count + 1 WHERE announcement_id = ?",
            (announcement_id,)
        )
        conn.commit()
        
        return {
            "code": 0,
            "message": "success",
            "data": announcement_dict,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.post("/{announcement_id}/read", summary="记录公告阅读")
async def mark_announcement_read(
    announcement_id: str,
    current_user = Depends(get_current_user)
):
    """记录公告阅读"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查公告是否存在
        cursor.execute(
            "SELECT announcement_id FROM announcements WHERE announcement_id = ? AND is_deleted = 0",
            (announcement_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="公告不存在")
        
        # 记录或更新阅读记录
        user_id = current_user.get("person_id")
        record_id = f"RR{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id[-4:]}"
        
        # 检查是否已有阅读记录
        cursor.execute(
            "SELECT record_id FROM user_reading_records WHERE user_id = ? AND content_type = 'announcement' AND content_id = ?",
            (user_id, announcement_id)
        )
        existing_record = cursor.fetchone()
        
        if existing_record:
            # 更新阅读记录
            cursor.execute("""
                UPDATE user_reading_records 
                SET last_read_time = CURRENT_TIMESTAMP, read_count = read_count + 1
                WHERE user_id = ? AND content_type = 'announcement' AND content_id = ?
            """, (user_id, announcement_id))
        else:
            # 创建新阅读记录
            cursor.execute("""
                INSERT INTO user_reading_records 
                (record_id, user_id, content_type, content_id, first_read_time, last_read_time, read_count)
                VALUES (?, ?, 'announcement', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
            """, (record_id, user_id, announcement_id))
        
        conn.commit()
        
        return {
            "code": 0,
            "message": "阅读记录已保存",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")
    finally:
        conn.close()


@router.get("/categories/list", summary="获取公告分类列表")
async def get_announcement_categories():
    """获取公告分类列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取所有分类及其数量
        sql = """
            SELECT category, COUNT(*) as count
            FROM announcements 
            WHERE is_deleted = 0 AND status = 'published'
            GROUP BY category
            ORDER BY count DESC
        """
        cursor.execute(sql)
        categories = [{"category": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "categories": categories
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/departments/list", summary="获取发布部门列表")
async def get_announcement_departments():
    """获取发布部门列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取所有发布部门及其数量
        sql = """
            SELECT department, COUNT(*) as count
            FROM announcements 
            WHERE is_deleted = 0 AND status = 'published'
            GROUP BY department
            ORDER BY count DESC
        """
        cursor.execute(sql)
        departments = [{"department": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "departments": departments
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/urgent/list", summary="获取紧急公告")
async def get_urgent_announcements():
    """获取紧急公告"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = """
            SELECT announcement_id, title, department, publish_time, priority
            FROM announcements 
            WHERE is_deleted = 0 AND status = 'published' AND is_urgent = 1
            ORDER BY publish_time DESC
            LIMIT 10
        """
        cursor.execute(sql)
        urgent_announcements = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "urgent_announcements": urgent_announcements
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close() 