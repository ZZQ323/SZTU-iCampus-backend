"""
课程表接口
提供课程表查询、课程管理等功能
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.deps import get_current_user

router = APIRouter()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('../../data-service/sztu_campus.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/", summary="获取课程表列表")
async def get_schedules(
    semester: Optional[str] = Query(None, description="学期"),
    week_number: Optional[int] = Query(None, description="周次"),
    current_user = Depends(get_current_user)
):
    """获取当前用户的课程表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        cursor.execute("SELECT student_id FROM persons WHERE person_id = ?", (person_id,))
        student_info = cursor.fetchone()
        
        if not student_info or not student_info["student_id"]:
            raise HTTPException(status_code=403, detail="仅限学生查询课程表")
        
        student_id = student_info["student_id"]
        
        # 构建查询条件
        where_conditions = ["e.student_id = ?", "e.is_deleted = 0", "cs.is_deleted = 0"]
        params = [student_id]
        
        if semester:
            where_conditions.append("ci.semester = ?")
            params.append(semester)
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询课程表
        sql = f"""
            SELECT cs.schedule_id, cs.course_instance_id, cs.day_of_week, 
                   cs.start_time, cs.end_time, cs.classroom, cs.building,
                   cs.week_range, cs.class_type,
                   c.course_id, c.course_name, c.course_code, c.credit_hours,
                   ci.semester, ci.academic_year, ci.teacher_id,
                   p.name as teacher_name,
                   l.location_name, l.building_name
            FROM enrollments e
            JOIN course_instances ci ON e.course_instance_id = ci.instance_id
            JOIN courses c ON ci.course_id = c.course_id
            JOIN class_schedules cs ON ci.instance_id = cs.course_instance_id
            LEFT JOIN persons p ON ci.teacher_id = p.employee_id
            LEFT JOIN locations l ON cs.classroom = l.room_number
            WHERE {where_clause}
            ORDER BY cs.day_of_week, cs.start_time
        """
        cursor.execute(sql, params)
        schedules = [dict(row) for row in cursor.fetchall()]
        
        # 如果指定了周次，过滤周次
        if week_number:
            filtered_schedules = []
            for schedule in schedules:
                week_range = schedule.get("week_range", "")
                if week_range and is_week_in_range(week_number, week_range):
                    filtered_schedules.append(schedule)
            schedules = filtered_schedules
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "schedules": schedules,
                "semester": semester,
                "week_number": week_number
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/week/{week_number}", summary="获取指定周课程表")
async def get_week_schedule(
    week_number: int,
    semester: Optional[str] = Query(None, description="学期"),
    current_user = Depends(get_current_user)
):
    """获取指定周次的课程表"""
    
    if week_number < 1 or week_number > 30:
        raise HTTPException(status_code=400, detail="周次必须在1-30之间")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        cursor.execute("SELECT student_id FROM persons WHERE person_id = ?", (person_id,))
        student_info = cursor.fetchone()
        
        if not student_info or not student_info["student_id"]:
            raise HTTPException(status_code=403, detail="仅限学生查询课程表")
        
        student_id = student_info["student_id"]
        
        # 构建查询条件
        where_conditions = ["e.student_id = ?", "e.is_deleted = 0", "cs.is_deleted = 0"]
        params = [student_id]
        
        if semester:
            where_conditions.append("ci.semester = ?")
            params.append(semester)
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询课程表
        sql = f"""
            SELECT cs.schedule_id, cs.day_of_week, cs.start_time, cs.end_time,
                   cs.classroom, cs.building, cs.week_range, cs.class_type,
                   c.course_name, c.course_code, c.credit_hours,
                   ci.semester, ci.academic_year,
                   p.name as teacher_name
            FROM enrollments e
            JOIN course_instances ci ON e.course_instance_id = ci.instance_id
            JOIN courses c ON ci.course_id = c.course_id
            JOIN class_schedules cs ON ci.instance_id = cs.course_instance_id
            LEFT JOIN persons p ON ci.teacher_id = p.employee_id
            WHERE {where_clause}
            ORDER BY cs.day_of_week, cs.start_time
        """
        cursor.execute(sql, params)
        all_schedules = [dict(row) for row in cursor.fetchall()]
        
        # 过滤指定周次的课程
        week_schedules = []
        for schedule in all_schedules:
            week_range = schedule.get("week_range", "")
            if week_range and is_week_in_range(week_number, week_range):
                week_schedules.append(schedule)
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "week_number": week_number,
                "semester": semester,
                "schedules": week_schedules
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/current-week", summary="获取当前周课程表")
async def get_current_week_schedule(
    semester: Optional[str] = Query(None, description="学期"),
    current_user = Depends(get_current_user)
):
    """获取当前周次的课程表"""
    
    # 计算当前周次（简单实现，假设学期从第1周开始）
    current_week = get_current_week_number()
    
    # 调用指定周课程表接口
    return await get_week_schedule(current_week, semester, current_user)


@router.get("/grid/{week_number}", summary="获取课程表网格数据")
async def get_schedule_grid(
    week_number: int,
    semester: Optional[str] = Query(None, description="学期"),
    current_user = Depends(get_current_user)
):
    """获取指定周次的课程表网格数据，用于前端表格显示"""
    
    if week_number < 1 or week_number > 30:
        raise HTTPException(status_code=400, detail="周次必须在1-30之间")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        person_id = current_user.get("person_id")
        cursor.execute("SELECT student_id FROM persons WHERE person_id = ?", (person_id,))
        student_info = cursor.fetchone()
        
        if not student_info or not student_info["student_id"]:
            raise HTTPException(status_code=403, detail="仅限学生查询课程表")
        
        student_id = student_info["student_id"]
        
        # 获取该周的所有课程
        week_schedule_response = await get_week_schedule(week_number, semester, current_user)
        schedules = week_schedule_response["data"]["schedules"]
        
        # 生成7x12的网格数据（7天 x 12个时间段）
        grid = {}
        for day in range(1, 8):  # 1-7表示周一到周日
            grid[day] = {}
            for slot in range(1, 13):  # 1-12表示12个时间段
                grid[day][slot] = None
        
        # 填充课程数据到网格
        for schedule in schedules:
            day = schedule["day_of_week"]
            time_slot = get_time_slot_from_time(schedule["start_time"])
            
            if day in grid and time_slot in grid[day]:
                grid[day][time_slot] = {
                    "course_name": schedule["course_name"],
                    "course_code": schedule["course_code"],
                    "teacher_name": schedule["teacher_name"],
                    "classroom": schedule["classroom"],
                    "building": schedule["building"],
                    "start_time": schedule["start_time"],
                    "end_time": schedule["end_time"],
                    "class_type": schedule["class_type"]
                }
        
        # 时间段信息
        time_slots = [
            {"slot": 1, "start_time": "08:00", "end_time": "08:45"},
            {"slot": 2, "start_time": "08:50", "end_time": "09:35"},
            {"slot": 3, "start_time": "10:05", "end_time": "10:50"},
            {"slot": 4, "start_time": "10:55", "end_time": "11:40"},
            {"slot": 5, "start_time": "14:00", "end_time": "14:45"},
            {"slot": 6, "start_time": "14:50", "end_time": "15:35"},
            {"slot": 7, "start_time": "15:55", "end_time": "16:40"},
            {"slot": 8, "start_time": "16:45", "end_time": "17:30"},
            {"slot": 9, "start_time": "19:00", "end_time": "19:45"},
            {"slot": 10, "start_time": "19:50", "end_time": "20:35"},
            {"slot": 11, "start_time": "20:40", "end_time": "21:25"},
            {"slot": 12, "start_time": "21:30", "end_time": "22:15"}
        ]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "week_number": week_number,
                "semester": semester,
                "time_slots": time_slots,
                "schedule_grid": grid,
                "student_info": {
                    "student_id": student_id,
                    "name": current_user.get("name")
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


def is_week_in_range(week_number: int, week_range: str) -> bool:
    """检查周次是否在指定范围内"""
    if not week_range:
        return True
    
    try:
        # 处理格式如 "1-16" 或 "1-8,10-16"
        ranges = week_range.replace("周", "").split(",")
        for range_part in ranges:
            if "-" in range_part:
                start, end = range_part.split("-")
                if int(start) <= week_number <= int(end):
                    return True
            else:
                if week_number == int(range_part):
                    return True
        return False
    except:
        return True


def get_current_week_number() -> int:
    """获取当前学期周次"""
    # 简单实现：假设每年9月第一周为第1周
    now = datetime.now()
    
    # 确定学期开始时间
    if now.month >= 9:  # 秋季学期
        semester_start = datetime(now.year, 9, 1)
    elif now.month <= 2:  # 春季学期
        semester_start = datetime(now.year, 2, 15)
    else:  # 春季学期
        semester_start = datetime(now.year, 2, 15)
    
    # 计算周数
    weeks = (now - semester_start).days // 7 + 1
    return max(1, min(weeks, 20))  # 限制在1-20周之间


def get_time_slot_from_time(time_str: str) -> int:
    """根据时间字符串获取时间段编号"""
    try:
        time = datetime.strptime(time_str, "%H:%M:%S").time()
        hour = time.hour
        
        if hour < 9:
            return 1 if time.minute < 45 else 2
        elif hour < 11:
            return 3 if time.minute < 50 else 4
        elif hour < 16:
            return 5 if time.minute < 45 else 6
        elif hour < 18:
            return 7 if time.minute < 40 else 8
        else:
            if hour < 20:
                return 9
            elif hour < 21:
                return 10 if time.minute < 35 else 11
            else:
                return 12
    except:
        return 1 