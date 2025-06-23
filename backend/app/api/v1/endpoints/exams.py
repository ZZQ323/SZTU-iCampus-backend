"""
考试接口
提供考试查询、倒计时等功能
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.deps import get_current_user

router = APIRouter()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('../../data-service/sztu_campus.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/", summary="获取考试列表")
async def get_exams(
    semester: Optional[str] = Query(None, description="学期"),
    status: Optional[str] = Query(None, description="考试状态"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量"),
    current_user = Depends(get_current_user)
):
    """获取考试列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        cursor.execute("SELECT student_id FROM persons WHERE person_id = ?", (person_id,))
        student_info = cursor.fetchone()
        
        if not student_info or not student_info["student_id"]:
            raise HTTPException(status_code=403, detail="仅限学生查询考试")
        
        student_id = student_info["student_id"]
        
        # 构建查询条件 - 通过选课记录获取考试信息
        where_conditions = ["e.student_id = ?", "e.is_deleted = 0", "ci.is_deleted = 0"]
        params = [student_id]
        
        if semester:
            where_conditions.append("ci.semester = ?")
            params.append(semester)
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询考试列表
        sql = f"""
            SELECT ci.instance_id, ci.exam_date, ci.exam_location, ci.makeup_exam_date,
                   c.course_id, c.course_name, c.course_code, c.credit_hours,
                   ci.semester, ci.academic_year, ci.teacher_id,
                   p.name as teacher_name,
                   CASE 
                       WHEN ci.exam_date IS NULL THEN 'not_scheduled'
                       WHEN ci.exam_date > datetime('now') THEN 'upcoming'
                       ELSE 'completed'
                   END as exam_status
            FROM enrollments e
            JOIN course_instances ci ON e.course_instance_id = ci.instance_id
            JOIN courses c ON ci.course_id = c.course_id
            LEFT JOIN persons p ON ci.teacher_id = p.employee_id
            WHERE {where_clause}
            ORDER BY ci.exam_date ASC
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [limit, offset])
        exams = [dict(row) for row in cursor.fetchall()]
        
        # 计算倒计时
        for exam in exams:
            if exam["exam_date"]:
                exam_time = datetime.fromisoformat(exam["exam_date"])
                now = datetime.now()
                if exam_time > now:
                    countdown = exam_time - now
                    exam["countdown_days"] = countdown.days
                    exam["countdown_hours"] = countdown.seconds // 3600
                else:
                    exam["countdown_days"] = 0
                    exam["countdown_hours"] = 0
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "exams": exams,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": len(exams) == limit
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/{exam_id}", summary="获取考试详情")
async def get_exam_detail(
    exam_id: str,
    current_user = Depends(get_current_user)
):
    """获取考试详情"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 查询考试详情
        sql = """
            SELECT ci.instance_id, ci.exam_date, ci.exam_location, ci.makeup_exam_date,
                   c.course_id, c.course_name, c.course_code, c.credit_hours,
                   ci.semester, ci.academic_year, ci.teacher_id,
                   p.name as teacher_name, ci.class_start_date, ci.class_end_date,
                   c.assessment_method, c.exam_form
            FROM course_instances ci
            JOIN courses c ON ci.course_id = c.course_id
            LEFT JOIN persons p ON ci.teacher_id = p.employee_id
            WHERE ci.instance_id = ? AND ci.is_deleted = 0
        """
        cursor.execute(sql, (exam_id,))
        exam = cursor.fetchone()
        
        if not exam:
            raise HTTPException(status_code=404, detail="考试不存在")
        
        exam_dict = dict(exam)
        
        # 计算详细倒计时
        if exam_dict["exam_date"]:
            exam_time = datetime.fromisoformat(exam_dict["exam_date"])
            now = datetime.now()
            if exam_time > now:
                countdown = exam_time - now
                exam_dict["countdown"] = {
                    "days": countdown.days,
                    "hours": countdown.seconds // 3600,
                    "minutes": (countdown.seconds % 3600) // 60,
                    "total_seconds": int(countdown.total_seconds())
                }
            else:
                exam_dict["countdown"] = {
                    "days": 0,
                    "hours": 0,
                    "minutes": 0,
                    "total_seconds": 0
                }
        
        return {
            "code": 0,
            "message": "success",
            "data": exam_dict,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/{exam_id}/countdown", summary="获取考试倒计时")
async def get_exam_countdown(exam_id: str):
    """获取考试倒计时"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 查询考试时间
        cursor.execute(
            "SELECT exam_date, course_id FROM course_instances WHERE instance_id = ? AND is_deleted = 0",
            (exam_id,)
        )
        exam = cursor.fetchone()
        
        if not exam:
            raise HTTPException(status_code=404, detail="考试不存在")
        
        if not exam["exam_date"]:
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "exam_id": exam_id,
                    "status": "not_scheduled",
                    "message": "考试时间未安排"
                },
                "timestamp": datetime.now().isoformat()
            }
        
        exam_time = datetime.fromisoformat(exam["exam_date"])
        now = datetime.now()
        
        if exam_time <= now:
            status = "completed"
            countdown_data = {
                "days": 0,
                "hours": 0,
                "minutes": 0,
                "seconds": 0,
                "total_seconds": 0
            }
        else:
            status = "upcoming"
            countdown = exam_time - now
            countdown_data = {
                "days": countdown.days,
                "hours": countdown.seconds // 3600,
                "minutes": (countdown.seconds % 3600) // 60,
                "seconds": countdown.seconds % 60,
                "total_seconds": int(countdown.total_seconds())
            }
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "exam_id": exam_id,
                "exam_date": exam["exam_date"],
                "status": status,
                "countdown": countdown_data
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close() 