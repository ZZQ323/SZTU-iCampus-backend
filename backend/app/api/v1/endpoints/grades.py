"""
成绩接口
提供成绩查询、统计分析等功能
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

@router.get("/", summary="获取成绩列表")
async def get_grades(
    semester: Optional[str] = Query(None, description="学期"),
    course_name: Optional[str] = Query(None, description="课程名称"),
    limit: int = Query(50, description="返回条数"),
    offset: int = Query(0, description="偏移量"),
    current_user = Depends(get_current_user)
):
    """获取当前用户的成绩列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取学生ID
        person_id = current_user.get("person_id")
        cursor.execute("SELECT student_id FROM persons WHERE person_id = ?", (person_id,))
        student_info = cursor.fetchone()
        
        if not student_info or not student_info["student_id"]:
            raise HTTPException(status_code=403, detail="仅限学生查询成绩")
        
        student_id = student_info["student_id"]
        
        # 构建查询条件
        where_conditions = ["g.student_id = ?", "g.is_deleted = 0"]
        params = [student_id]
        
        if semester:
            where_conditions.append("ci.semester = ?")
            params.append(semester)
        
        if course_name:
            where_conditions.append("c.course_name LIKE ?")
            params.append(f"%{course_name}%")
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询总数
        count_sql = f"""
            SELECT COUNT(*) 
            FROM grades g
            JOIN course_instances ci ON g.course_instance_id = ci.instance_id
            JOIN courses c ON ci.course_id = c.course_id
            WHERE {where_clause}
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]
        
        # 查询成绩列表
        sql = f"""
            SELECT g.grade_id, g.student_id, g.course_instance_id, g.usual_score, 
                   g.midterm_score, g.final_score, g.lab_score, g.homework_score,
                   g.total_score, g.grade_point, g.grade_level, g.exam_type,
                   g.exam_date, g.submit_date, g.grade_status, g.is_passed,
                   g.is_retake_required, g.teacher_comment,
                   c.course_id, c.course_name, c.course_code, c.credit_hours,
                   ci.semester, ci.academic_year, ci.teacher_id,
                   p.name as teacher_name
            FROM grades g
            JOIN course_instances ci ON g.course_instance_id = ci.instance_id
            JOIN courses c ON ci.course_id = c.course_id
            LEFT JOIN persons p ON ci.teacher_id = p.employee_id
            WHERE {where_clause}
            ORDER BY ci.semester DESC, g.submit_date DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [limit, offset])
        grades = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "grades": grades,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total
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


@router.get("/semester/{semester}", summary="获取指定学期成绩")
async def get_grades_by_semester(
    semester: str,
    current_user = Depends(get_current_user)
):
    """获取指定学期的成绩"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        cursor.execute("SELECT student_id FROM persons WHERE person_id = ?", (person_id,))
        student_info = cursor.fetchone()
        
        if not student_info or not student_info["student_id"]:
            raise HTTPException(status_code=403, detail="仅限学生查询成绩")
        
        student_id = student_info["student_id"]
        
        # 查询学期成绩
        sql = """
            SELECT g.grade_id, g.usual_score, g.midterm_score, g.final_score, 
                   g.lab_score, g.homework_score, g.total_score, g.grade_point, 
                   g.grade_level, g.is_passed, g.teacher_comment,
                   c.course_name, c.course_code, c.credit_hours, c.course_type,
                   ci.semester, ci.academic_year,
                   p.name as teacher_name
            FROM grades g
            JOIN course_instances ci ON g.course_instance_id = ci.instance_id
            JOIN courses c ON ci.course_id = c.course_id
            LEFT JOIN persons p ON ci.teacher_id = p.employee_id
            WHERE g.student_id = ? AND ci.semester = ? AND g.is_deleted = 0
            ORDER BY c.course_name
        """
        cursor.execute(sql, (student_id, semester))
        grades = [dict(row) for row in cursor.fetchall()]
        
        # 计算学期统计
        if grades:
            total_credits = sum(float(g["credit_hours"]) for g in grades if g["is_passed"])
            total_grade_points = sum(float(g["grade_point"]) * float(g["credit_hours"]) 
                                   for g in grades if g["grade_point"] and g["is_passed"])
            gpa = total_grade_points / total_credits if total_credits > 0 else 0
            
            passed_count = sum(1 for g in grades if g["is_passed"])
            failed_count = len(grades) - passed_count
            
            semester_stats = {
                "total_courses": len(grades),
                "passed_courses": passed_count,
                "failed_courses": failed_count,
                "total_credits": total_credits,
                "gpa": round(gpa, 2),
                "pass_rate": round(passed_count / len(grades) * 100, 2) if grades else 0
            }
        else:
            semester_stats = {
                "total_courses": 0,
                "passed_courses": 0,
                "failed_courses": 0,
                "total_credits": 0,
                "gpa": 0,
                "pass_rate": 0
            }
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "semester": semester,
                "grades": grades,
                "semester_stats": semester_stats
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/statistics", summary="获取成绩统计")
async def get_grade_statistics(current_user = Depends(get_current_user)):
    """获取成绩统计信息"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        cursor.execute("SELECT student_id FROM persons WHERE person_id = ?", (person_id,))
        student_info = cursor.fetchone()
        
        if not student_info or not student_info["student_id"]:
            raise HTTPException(status_code=403, detail="仅限学生查询成绩")
        
        student_id = student_info["student_id"]
        
        # 总体统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total_courses,
                COUNT(CASE WHEN g.is_passed = 1 THEN 1 END) as passed_courses,
                COUNT(CASE WHEN g.is_passed = 0 THEN 1 END) as failed_courses,
                COALESCE(AVG(g.total_score), 0) as avg_score,
                COALESCE(MAX(g.total_score), 0) as max_score,
                COALESCE(MIN(g.total_score), 0) as min_score,
                COALESCE(SUM(CASE WHEN g.is_passed = 1 THEN c.credit_hours ELSE 0 END), 0) as total_credits
            FROM grades g
            JOIN course_instances ci ON g.course_instance_id = ci.instance_id
            JOIN courses c ON ci.course_id = c.course_id
            WHERE g.student_id = ? AND g.is_deleted = 0
        """, (student_id,))
        
        overall_stats = dict(cursor.fetchone())
        
        # 计算总GPA
        cursor.execute("""
            SELECT 
                COALESCE(SUM(g.grade_point * c.credit_hours), 0) as total_grade_points,
                COALESCE(SUM(c.credit_hours), 0) as total_credit_hours
            FROM grades g
            JOIN course_instances ci ON g.course_instance_id = ci.instance_id
            JOIN courses c ON ci.course_id = c.course_id
            WHERE g.student_id = ? AND g.is_passed = 1 AND g.is_deleted = 0
        """, (student_id,))
        
        gpa_data = cursor.fetchone()
        total_gpa = (gpa_data["total_grade_points"] / gpa_data["total_credit_hours"] 
                    if gpa_data["total_credit_hours"] > 0 else 0)
        overall_stats["total_gpa"] = round(total_gpa, 2)
        
        # 按学期统计
        cursor.execute("""
            SELECT ci.semester, ci.academic_year,
                   COUNT(*) as course_count,
                   COALESCE(AVG(g.total_score), 0) as avg_score,
                   COUNT(CASE WHEN g.is_passed = 1 THEN 1 END) as passed_count,
                   COALESCE(SUM(CASE WHEN g.is_passed = 1 THEN c.credit_hours ELSE 0 END), 0) as credits
            FROM grades g
            JOIN course_instances ci ON g.course_instance_id = ci.instance_id
            JOIN courses c ON ci.course_id = c.course_id
            WHERE g.student_id = ? AND g.is_deleted = 0
            GROUP BY ci.semester, ci.academic_year
            ORDER BY ci.academic_year DESC, ci.semester DESC
        """, (student_id,))
        
        semester_stats = [dict(row) for row in cursor.fetchall()]
        
        # 按课程类型统计
        cursor.execute("""
            SELECT c.course_type,
                   COUNT(*) as course_count,
                   COALESCE(AVG(g.total_score), 0) as avg_score,
                   COUNT(CASE WHEN g.is_passed = 1 THEN 1 END) as passed_count
            FROM grades g
            JOIN course_instances ci ON g.course_instance_id = ci.instance_id
            JOIN courses c ON ci.course_id = c.course_id
            WHERE g.student_id = ? AND g.is_deleted = 0
            GROUP BY c.course_type
            ORDER BY course_count DESC
        """, (student_id,))
        
        course_type_stats = [dict(row) for row in cursor.fetchall()]
        
        # 成绩等级分布
        cursor.execute("""
            SELECT g.grade_level,
                   COUNT(*) as count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM grades WHERE student_id = ? AND is_deleted = 0), 2) as percentage
            FROM grades g
            WHERE g.student_id = ? AND g.is_deleted = 0 AND g.grade_level IS NOT NULL
            GROUP BY g.grade_level
            ORDER BY g.grade_level
        """, (student_id, student_id))
        
        grade_distribution = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "overall_stats": overall_stats,
                "semester_stats": semester_stats,
                "course_type_stats": course_type_stats,
                "grade_distribution": grade_distribution
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/ranking", summary="获取成绩排名")
async def get_grade_ranking(
    semester: Optional[str] = Query(None, description="学期"),
    current_user = Depends(get_current_user)
):
    """获取成绩排名信息"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        cursor.execute("SELECT student_id, class_id FROM persons WHERE person_id = ?", (person_id,))
        student_info = cursor.fetchone()
        
        if not student_info or not student_info["student_id"]:
            raise HTTPException(status_code=403, detail="仅限学生查询成绩")
        
        student_id = student_info["student_id"]
        class_id = student_info["class_id"]
        
        # 构建查询条件
        where_condition = "g.is_deleted = 0"
        params = []
        
        if semester:
            where_condition += " AND ci.semester = ?"
            params.append(semester)
        
        # 计算班级排名
        if class_id:
            sql = f"""
                WITH student_gpa AS (
                    SELECT 
                        p.student_id,
                        p.name,
                        p.class_id,
                        COALESCE(SUM(g.grade_point * c.credit_hours) / SUM(c.credit_hours), 0) as gpa,
                        COALESCE(AVG(g.total_score), 0) as avg_score
                    FROM persons p
                    LEFT JOIN grades g ON p.student_id = g.student_id AND g.is_deleted = 0
                    LEFT JOIN course_instances ci ON g.course_instance_id = ci.instance_id
                    LEFT JOIN courses c ON ci.course_id = c.course_id
                    WHERE p.class_id = ? AND p.person_type = 'student' {' AND ci.semester = ?' if semester else ''}
                    GROUP BY p.student_id, p.name, p.class_id
                ),
                ranked_students AS (
                    SELECT *,
                           ROW_NUMBER() OVER (ORDER BY gpa DESC, avg_score DESC) as rank
                    FROM student_gpa
                )
                SELECT rank, gpa, avg_score,
                       (SELECT COUNT(*) FROM student_gpa) as total_students
                FROM ranked_students
                WHERE student_id = ?
            """
            
            query_params = [class_id]
            if semester:
                query_params.append(semester)
            query_params.append(student_id)
            
            cursor.execute(sql, query_params)
            ranking_info = cursor.fetchone()
            
            if ranking_info:
                ranking_data = {
                    "class_rank": ranking_info["rank"],
                    "total_students": ranking_info["total_students"],
                    "gpa": round(ranking_info["gpa"], 2),
                    "avg_score": round(ranking_info["avg_score"], 2),
                    "class_id": class_id
                }
            else:
                ranking_data = None
        else:
            ranking_data = None
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "ranking": ranking_data,
                "semester": semester
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/semesters", summary="获取学期列表")
async def get_available_semesters(current_user = Depends(get_current_user)):
    """获取有成绩记录的学期列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        cursor.execute("SELECT student_id FROM persons WHERE person_id = ?", (person_id,))
        student_info = cursor.fetchone()
        
        if not student_info or not student_info["student_id"]:
            raise HTTPException(status_code=403, detail="仅限学生查询成绩")
        
        student_id = student_info["student_id"]
        
        # 查询可用学期
        cursor.execute("""
            SELECT ci.semester, ci.academic_year,
                   COUNT(*) as course_count,
                   COALESCE(AVG(g.total_score), 0) as avg_score
            FROM grades g
            JOIN course_instances ci ON g.course_instance_id = ci.instance_id
            WHERE g.student_id = ? AND g.is_deleted = 0
            GROUP BY ci.semester, ci.academic_year
            ORDER BY ci.academic_year DESC, ci.semester DESC
        """, (student_id,))
        
        semesters = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "semesters": semesters
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close() 