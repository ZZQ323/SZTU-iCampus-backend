"""
基础数据模块 API
提供学院、专业、班级、部门、场所等基础数据查询
"""
import sqlite3
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('../../data-service/sztu_campus.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/colleges", summary="获取学院列表")
async def get_colleges():
    """获取学院列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = """
            SELECT college_id, college_name, college_code, phone, email,
                   main_building, total_teachers, total_students, total_majors,
                   description
            FROM colleges
            WHERE is_deleted = 0 AND status = 'active'
            ORDER BY college_id
        """
        cursor.execute(sql)
        colleges = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {"colleges": colleges},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/colleges/{college_id}/majors", summary="获取学院专业列表")
async def get_college_majors(college_id: str):
    """获取学院专业列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = """
            SELECT major_id, major_name, major_code, duration_years,
                   degree_type, total_teachers, total_students, total_classes,
                   enrollment_quota, tuition_fee, description
            FROM majors
            WHERE college_id = ? AND is_deleted = 0 AND status = 'active'
            ORDER BY major_code
        """
        cursor.execute(sql, (college_id,))
        majors = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {"majors": majors},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/majors", summary="获取专业列表")
async def get_majors(
    college_id: Optional[str] = Query(None, description="学院ID"),
    degree_type: Optional[str] = Query(None, description="学位类型")
):
    """获取专业列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        where_conditions = ["is_deleted = 0", "status = 'active'"]
        params = []
        
        if college_id:
            where_conditions.append("college_id = ?")
            params.append(college_id)
        
        if degree_type:
            where_conditions.append("degree_type = ?")
            params.append(degree_type)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
            SELECT m.major_id, m.major_name, m.major_code, m.college_id,
                   m.duration_years, m.degree_type, m.enrollment_quota,
                   c.college_name
            FROM majors m
            JOIN colleges c ON m.college_id = c.college_id
            WHERE {where_clause}
            ORDER BY m.major_code
        """
        cursor.execute(sql, params)
        majors = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {"majors": majors},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/majors/{major_id}/classes", summary="获取专业班级列表")
async def get_major_classes(major_id: str):
    """获取专业班级列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        sql = """
            SELECT class_id, class_name, class_code, grade, semester_enrolled,
                   total_students, male_count, female_count, graduation_date,
                   classroom_location
            FROM classes
            WHERE major_id = ? AND is_deleted = 0 AND status = 'active'
            ORDER BY grade DESC, class_code
        """
        cursor.execute(sql, (major_id,))
        classes = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {"classes": classes},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/classes", summary="获取班级列表")
async def get_classes(
    major_id: Optional[str] = Query(None, description="专业ID"),
    grade: Optional[int] = Query(None, description="年级"),
    college_id: Optional[str] = Query(None, description="学院ID")
):
    """获取班级列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        where_conditions = ["cl.is_deleted = 0", "cl.status = 'active'"]
        params = []
        
        if major_id:
            where_conditions.append("cl.major_id = ?")
            params.append(major_id)
        
        if grade:
            where_conditions.append("cl.grade = ?")
            params.append(grade)
        
        if college_id:
            where_conditions.append("cl.college_id = ?")
            params.append(college_id)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
            SELECT cl.class_id, cl.class_name, cl.class_code, cl.grade,
                   cl.total_students, cl.graduation_date,
                   m.major_name, c.college_name
            FROM classes cl
            JOIN majors m ON cl.major_id = m.major_id
            JOIN colleges c ON cl.college_id = c.college_id
            WHERE {where_clause}
            ORDER BY cl.grade DESC, cl.class_code
        """
        cursor.execute(sql, params)
        classes = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {"classes": classes},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/departments", summary="获取部门列表")
async def get_departments():
    """获取部门列表"""
    
    # 模拟部门数据（因为departments表为空）
    departments = [
        {
            "department_id": "D001",
            "department_name": "教务处",
            "department_type": "administrative",
            "phone": "0755-26000001",
            "email": "jwc@sztu.edu.cn",
            "office_location": "行政楼201",
            "description": "负责学校教学管理工作"
        },
        {
            "department_id": "D002", 
            "department_name": "学生处",
            "department_type": "administrative",
            "phone": "0755-26000002",
            "email": "xsc@sztu.edu.cn",
            "office_location": "行政楼301",
            "description": "负责学生事务管理工作"
        },
        {
            "department_id": "D003",
            "department_name": "科研处",
            "department_type": "administrative", 
            "phone": "0755-26000003",
            "email": "kyc@sztu.edu.cn",
            "office_location": "行政楼401",
            "description": "负责科研项目管理工作"
        }
    ]
    
    return {
        "code": 0,
        "message": "success",
        "data": {"departments": departments},
        "timestamp": datetime.now().isoformat()
    }


@router.get("/locations", summary="获取场所列表")
async def get_locations(
    location_type: Optional[str] = Query(None, description="场所类型"),
    building_code: Optional[str] = Query(None, description="建筑代码"),
    is_available: Optional[bool] = Query(None, description="是否可用")
):
    """获取场所列表"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        where_conditions = ["is_deleted = 0", "status = 'active'"]
        params = []
        
        if location_type:
            where_conditions.append("location_type = ?")
            params.append(location_type)
        
        if building_code:
            where_conditions.append("building_code = ?")
            params.append(building_code)
        
        if is_available is not None:
            where_conditions.append("is_available = ?")
            params.append(1 if is_available else 0)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
            SELECT location_id, location_name, location_type, building_code,
                   building_name, floor, room_number, capacity, area,
                   is_available, booking_required
            FROM locations
            WHERE {where_clause}
            ORDER BY building_code, floor, room_number
            LIMIT 100
        """
        cursor.execute(sql, params)
        locations = [dict(row) for row in cursor.fetchall()]
        
        return {
            "code": 0,
            "message": "success",
            "data": {"locations": locations},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()


@router.get("/locations/{location_id}/occupations", summary="获取场所占用情况")
async def get_location_occupations(location_id: str):
    """获取场所占用情况"""
    
    # 模拟占用数据（因为room_occupations表为空）
    occupations = [
        {
            "occupation_id": "OCC20250001",
            "start_time": "2025-01-15T08:00:00Z",
            "end_time": "2025-01-15T09:40:00Z",
            "occupant_type": "course",
            "occupant_name": "高等数学A",
            "status": "confirmed",
            "weekday": 1
        },
        {
            "occupation_id": "OCC20250002",
            "start_time": "2025-01-15T10:00:00Z", 
            "end_time": "2025-01-15T11:40:00Z",
            "occupant_type": "course",
            "occupant_name": "线性代数",
            "status": "confirmed",
            "weekday": 1
        }
    ]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "location_id": location_id,
            "occupations": occupations
        },
        "timestamp": datetime.now().isoformat()
    } 