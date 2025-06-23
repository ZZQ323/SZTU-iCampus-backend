"""
课程管理模块 API
提供课程信息查询、开课管理等功能
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

@router.get("/", summary="获取课程列表")
async def get_courses(
    major_id: Optional[str] = Query(None, description="专业ID"),
    course_type: Optional[str] = Query(None, description="课程类型"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量")
):
    """获取课程列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        where_conditions = ["is_deleted = 0", "status = 'active'"]
        params = []
        
        if major_id:
            where_conditions.append("major_id = ?")
            params.append(major_id)
        
        if course_type:
            where_conditions.append("course_type = ?")
            params.append(course_type)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
            SELECT course_id, course_name, course_code, course_type,
                   credit_hours, total_hours, theory_hours, practice_hours,
                   major_id, description, difficulty_level, is_active
            FROM courses
            WHERE {where_clause}
            ORDER BY course_code
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [limit, offset])
        courses = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "courses": courses,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": len(courses) == limit
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/{course_id}", summary="获取课程详情")
async def get_course_detail(course_id: str):
    """获取课程详情"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = """
            SELECT * FROM courses
            WHERE course_id = ? AND is_deleted = 0
        """
        cursor.execute(sql, (course_id,))
        course = cursor.fetchone()
        
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        course_dict = dict(course)
        
        return {
            "code": 0,
            "message": "success",
            "data": course_dict,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/{course_id}/instances", summary="获取课程开课实例")
async def get_course_instances(
    course_id: str,
    semester: Optional[str] = Query(None, description="学期")
):
    """获取课程开课实例"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        where_conditions = ["course_id = ?", "is_deleted = 0"]
        params = [course_id]
        
        if semester:
            where_conditions.append("semester = ?")
            params.append(semester)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
            SELECT ci.instance_id, ci.semester, ci.academic_year,
                   ci.max_students, ci.current_students, ci.instance_status,
                   ci.class_start_date, ci.class_end_date,
                   p.name as teacher_name
            FROM course_instances ci
            LEFT JOIN persons p ON ci.teacher_id = p.employee_id
            WHERE {where_clause}
            ORDER BY ci.semester DESC
        """
        cursor.execute(sql, params)
        instances = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {"instances": instances},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/instances/{instance_id}/students", summary="获取选课学生列表")
async def get_instance_students(
    instance_id: str,
    current_user = Depends(get_current_user)
):
    """获取选课学生列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = """
            SELECT e.student_id, p.name, p.class_id, e.enrollment_status,
                   e.enrollment_date, e.credit_hours
            FROM enrollments e
            JOIN persons p ON e.student_id = p.student_id
            WHERE e.course_instance_id = ? AND e.is_deleted = 0
            ORDER BY p.name
        """
        cursor.execute(sql, (instance_id,))
        students = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "instance_id": instance_id,
                "students": students,
                "total_count": len(students)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/instances/{instance_id}/statistics", summary="获取课程统计")
async def get_instance_statistics(
    instance_id: str,
    current_user = Depends(get_current_user)
):
    """获取课程统计"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 查询基本统计
        cursor.execute("""
            SELECT COUNT(*) as enrolled_count,
                   AVG(CASE WHEN g.total_score IS NOT NULL THEN g.total_score END) as avg_score,
                   COUNT(CASE WHEN g.is_passed = 1 THEN 1 END) as passed_count
            FROM enrollments e
            LEFT JOIN grades g ON e.course_instance_id = g.course_instance_id 
                              AND e.student_id = g.student_id
            WHERE e.course_instance_id = ? AND e.is_deleted = 0
        """, (instance_id,))
        
        stats = dict(cursor.fetchone())
        
        # 计算通过率
        if stats["enrolled_count"] > 0:
            stats["pass_rate"] = round((stats["passed_count"] or 0) / stats["enrolled_count"] * 100, 2)
        else:
            stats["pass_rate"] = 0
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "instance_id": instance_id,
                "statistics": stats
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close() 