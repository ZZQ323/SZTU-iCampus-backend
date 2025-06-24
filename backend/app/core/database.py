"""
数据库直连管理器
直接连接SQLite数据库，替代HTTP调用data-service的方式
"""
import sqlite3
import threading
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Union
import logging
from pathlib import Path
import time

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite数据库管理器"""
    
    def __init__(self):
        self.db_path = settings.DATABASE_PATH
        self._local = threading.local()
        self._lock = threading.Lock()
        
    def _get_connection(self) -> sqlite3.Connection:
        """获取线程本地数据库连接"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=settings.DATABASE_TIMEOUT
            )
            # 设置行工厂，返回字典格式
            self._local.connection.row_factory = sqlite3.Row
            
        return self._local.connection
    
    @contextmanager
    def get_db_connection(self):
        """上下文管理器：获取数据库连接"""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """执行查询并返回结果"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # 将Row对象转换为字典
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_single(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> Optional[Dict[str, Any]]:
        """执行查询并返回单个结果"""
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def execute_update(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> int:
        """执行更新操作，返回影响的行数"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.rowcount
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查数据库文件
            db_file = Path(self.db_path)
            if not db_file.exists():
                return {
                    "status": "error",
                    "message": f"数据库文件不存在: {self.db_path}"
                }
            
            # 检查连接
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM persons")
                result = cursor.fetchone()
                user_count = result[0] if result else 0
                
                return {
                    "status": "healthy",
                    "database_path": str(db_file.absolute()),
                    "database_size": f"{db_file.stat().st_size / (1024*1024*1024):.2f} GB",
                    "user_count": user_count,
                    "connection": "active"
                }
                
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


# 创建全局数据库管理器实例
db_manager = DatabaseManager()


# ==================== 数据访问函数 ====================

def get_person_by_login(login_id: str) -> Optional[Dict[str, Any]]:
    """根据登录ID获取人员信息（学号或员工号）"""
    try:
        # 查询学生
        query = """
        SELECT * FROM persons 
        WHERE person_type = 'student' AND student_id = ?
        """
        result = db_manager.execute_single(query, (login_id,))
        if result:
            return result
        
        # 查询教师/管理员
        query = """
        SELECT * FROM persons 
        WHERE person_type IN ('teacher', 'admin', 'assistant_teacher') 
        AND employee_id = ?
        """
        result = db_manager.execute_single(query, (login_id,))
        return result
        
    except Exception as e:
        logger.error(f"获取用户信息失败 {login_id}: {e}")
        return None


def get_student_schedule(
    student_id: str, 
    semester: str = "2024-2025-1", 
    week_number: Optional[int] = None
) -> Dict[str, Any]:
    """获取学生课表"""
    try:
        query = """
        SELECT 
            ci.course_instance_id,
            c.course_code,
            c.course_name,
            ci.instructor_name as teacher_name,
            ci.class_time_json,
            ci.classroom_location as location,
            c.course_type,
            ci.semester,
            ci.weeks_schedule,
            c.credit_hours
        FROM course_instances ci
        JOIN courses c ON ci.course_id = c.course_id
        JOIN enrollments e ON ci.course_instance_id = e.course_instance_id
        WHERE e.student_id = ? AND ci.semester = ?
        """
        
        results = db_manager.execute_query(query, (student_id, semester))
        
        # 处理课程时间数据（假设class_time_json包含weekday、start_time、end_time信息）
        courses = []
        for row in results:
            # 这里需要解析class_time_json，简化处理
            courses.append({
                "course_id": row["course_code"],
                "course_name": row["course_name"],
                "teacher_name": row["teacher_name"],
                "location": row["location"],
                "course_type": row["course_type"],
                "semester": row["semester"],
                "weeks": row["weeks_schedule"] or "1-16周",
                "credit_hours": row["credit_hours"],
                # 这些字段需要从class_time_json解析
                "weekday": 1,  # 默认周一
                "start_time": "08:30",
                "end_time": "10:10",
            })
        
        return {
            "student_id": student_id,
            "semester": semester,
            "week_number": week_number or 1,
            "courses": courses
        }
        
    except Exception as e:
        logger.error(f"获取学生课表失败 {student_id}: {e}")
        return {
            "student_id": student_id,
            "semester": semester,
            "week_number": week_number or 1,
            "courses": []
        }


def get_student_grades(student_id: str, semester: Optional[str] = None) -> Dict[str, Any]:
    """获取学生成绩"""
    try:
        query = """
        SELECT 
            g.grade_id,
            c.course_code,
            c.course_name,
            c.credit_hours,
            g.usual_score,
            g.midterm_score,
            g.final_score,
            g.total_score,
            g.grade_level,
            g.grade_point,
            g.is_passed,
            ci.semester
        FROM grades g
        JOIN course_instances ci ON g.course_instance_id = ci.course_instance_id
        JOIN courses c ON ci.course_id = c.course_id
        WHERE g.student_id = ?
        """
        
        params = [student_id]
        if semester:
            query += " AND ci.semester = ?"
            params.append(semester)
        
        query += " ORDER BY ci.semester DESC, c.course_name"
        
        results = db_manager.execute_query(query, tuple(params))
        
        # 计算统计信息
        total_courses = len(results)
        passed_courses = sum(1 for r in results if r["is_passed"])
        total_credit_hours = sum(r["credit_hours"] for r in results if r["is_passed"])
        
        # 计算GPA
        total_grade_points = sum(
            r["grade_point"] * r["credit_hours"] 
            for r in results if r["grade_point"] is not None
        )
        total_credits_for_gpa = sum(
            r["credit_hours"] 
            for r in results if r["grade_point"] is not None
        )
        gpa = total_grade_points / total_credits_for_gpa if total_credits_for_gpa > 0 else 0.0
        
        return {
            "student_id": student_id,
            "semester": semester or "all",
            "grades": results,
            "statistics": {
                "total_courses": total_courses,
                "passed_courses": passed_courses,
                "total_credit_hours": total_credit_hours,
                "gpa": round(gpa, 2),
                "rank_in_class": None,  # 需要复杂查询
                "rank_in_major": None   # 需要复杂查询
            }
        }
        
    except Exception as e:
        logger.error(f"获取学生成绩失败 {student_id}: {e}")
        return {
            "student_id": student_id,
            "semester": semester or "all",
            "grades": [],
            "statistics": {
                "total_courses": 0,
                "passed_courses": 0,
                "total_credit_hours": 0,
                "gpa": 0.0,
                "rank_in_class": None,
                "rank_in_major": None
            }
        }


def get_announcements(
    page: int = 1,
    size: int = 10,
    category: Optional[str] = None,
    department: Optional[str] = None,
    priority: Optional[str] = None
) -> Dict[str, Any]:
    """获取公告列表"""
    try:
        # 构建基础查询
        query = """
        SELECT 
            announcement_id,
            title,
            content,
            summary,
            publisher_id,
            publisher_name,
            department,
            category,
            priority,
            is_urgent,
            is_pinned,
            publish_time,
            view_count,
            like_count,
            comment_count
        FROM announcements 
        WHERE 1=1
        """
        
        params = []
        
        # 添加过滤条件
        if category:
            query += " AND category = ?"
            params.append(category)
        if department:
            query += " AND department = ?"
            params.append(department)
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        # 排序：置顶优先，然后按发布时间倒序
        query += " ORDER BY is_pinned DESC, publish_time DESC"
        
        # 分页
        offset = (page - 1) * size
        query += " LIMIT ? OFFSET ?"
        params.extend([size, offset])
        
        results = db_manager.execute_query(query, tuple(params))
        
        # 获取总数
        count_query = "SELECT COUNT(*) as total FROM announcements WHERE 1=1"
        count_params = []
        if category:
            count_query += " AND category = ?"
            count_params.append(category)
        if department:
            count_query += " AND department = ?"
            count_params.append(department)
        if priority:
            count_query += " AND priority = ?"
            count_params.append(priority)
        
        total_result = db_manager.execute_single(count_query, tuple(count_params))
        total = total_result["total"] if total_result else 0
        
        return {
            "announcements": results,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
        
    except Exception as e:
        logger.error(f"获取公告列表失败: {e}")
        return {
            "announcements": [],
            "total": 0,
            "page": page,
            "size": size,
            "pages": 0
        }


def get_campus_card_info(person_id: str) -> Dict[str, Any]:
    """获取校园卡信息"""
    try:
        # 获取最新余额（从交易记录中计算）
        query = """
        SELECT 
            SUM(CASE WHEN transaction_type = 'recharge' THEN amount ELSE -amount END) as balance
        FROM transactions 
        WHERE person_id = ?
        """
        result = db_manager.execute_single(query, (person_id,))
        balance = result["balance"] if result and result["balance"] else 0.0
        
        # 获取卡片基本信息
        person_query = """
        SELECT student_id, employee_id, name FROM persons WHERE person_id = ?
        """
        person_result = db_manager.execute_single(person_query, (person_id,))
        
        card_number = "未知"
        if person_result:
            card_number = person_result.get("student_id") or person_result.get("employee_id") or "未知"
        
        return {
            "card_info": {
                "card_id": f"CC{person_id}",
                "card_number": card_number,
                "balance": float(balance),
                "card_status": "active",
                "daily_limit": 300,
                "total_recharge": 0.0,  # 需要额外计算
                "total_consumption": 0.0  # 需要额外计算
            }
        }
        
    except Exception as e:
        logger.error(f"获取校园卡信息失败 {person_id}: {e}")
        return {
            "card_info": {
                "card_id": f"CC{person_id}",
                "card_number": "未知",
                "balance": 0.0,
                "card_status": "active",
                "daily_limit": 300,
                "total_recharge": 0.0,
                "total_consumption": 0.0
            }
        }


def get_transactions(
    person_id: str,
    page: int = 1,
    size: int = 20,
    transaction_type: Optional[str] = None
) -> Dict[str, Any]:
    """获取交易记录"""
    try:
        query = """
        SELECT 
            transaction_id,
            transaction_type,
            amount,
            transaction_time,
            merchant_name,
            location_name,
            category,
            description
        FROM transactions 
        WHERE person_id = ?
        """
        
        params = [person_id]
        
        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)
        
        query += " ORDER BY transaction_time DESC LIMIT ? OFFSET ?"
        offset = (page - 1) * size
        params.extend([size, offset])
        
        results = db_manager.execute_query(query, tuple(params))
        
        # 计算余额（简化处理，每条记录显示当时余额）
        for i, transaction in enumerate(results):
            # 这里应该计算每笔交易后的余额，简化处理
            transaction["balance_after"] = 100.0  # 占位符
        
        # 获取总数
        count_query = "SELECT COUNT(*) as total FROM transactions WHERE person_id = ?"
        count_params = [person_id]
        if transaction_type:
            count_query += " AND transaction_type = ?"
            count_params.append(transaction_type)
        
        total_result = db_manager.execute_single(count_query, tuple(count_params))
        total = total_result["total"] if total_result else 0
        
        return {
            "transactions": results,
            "total": total,
            "page": page,
            "size": size
        }
        
    except Exception as e:
        logger.error(f"获取交易记录失败 {person_id}: {e}")
        return {
            "transactions": [],
            "total": 0,
            "page": page,
            "size": size
        }


def get_system_stats() -> Dict[str, Any]:
    """获取系统统计信息"""
    try:
        stats = {}
        
        # 用户统计
        stats["total_users"] = db_manager.execute_single(
            "SELECT COUNT(*) as count FROM persons"
        )["count"]
        
        stats["admin_count"] = db_manager.execute_single(
            "SELECT COUNT(*) as count FROM persons WHERE person_type = 'admin'"
        )["count"]
        
        stats["student_count"] = db_manager.execute_single(
            "SELECT COUNT(*) as count FROM persons WHERE person_type = 'student'"
        )["count"]
        
        stats["teacher_count"] = db_manager.execute_single(
            "SELECT COUNT(*) as count FROM persons WHERE person_type = 'teacher'"
        )["count"]
        
        # 公告统计
        stats["total_announcements"] = db_manager.execute_single(
            "SELECT COUNT(*) as count FROM announcements"
        )["count"]
        
        # 课程统计
        stats["total_courses"] = db_manager.execute_single(
            "SELECT COUNT(*) as count FROM courses"
        )["count"]
        
        return stats
        
    except Exception as e:
        logger.error(f"获取系统统计失败: {e}")
        return {
            "total_users": 0,
            "admin_count": 0,
            "student_count": 0,
            "teacher_count": 0,
            "total_announcements": 0,
            "total_courses": 0
        } 