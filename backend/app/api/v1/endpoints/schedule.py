"""
课程表接口
提供课程表查询、课程管理等功能
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
import time

from app.api.deps import get_current_user
# 🔄 使用HTTP客户端进行真正的HTTP请求，不导入Python模块
from app.core.http_client import http_client

router = APIRouter()

@router.get("/", response_model=dict)
async def get_schedule(
    semester: Optional[str] = Query(None, description="学期，如：2024-2025-1"),
    week_number: Optional[int] = Query(None, ge=1, le=20, description="周次"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取课表列表"""
    try:
        # 🔄 HTTP请求data-service获取课表
        if current_user["person_type"] == "student":
            student_id = current_user.get("student_id")
            if not student_id:
                raise HTTPException(status_code=400, detail="学生ID不能为空")
            
            schedule_data = await http_client.get_student_schedule(
                student_id=student_id,
                semester=semester,
                week_number=week_number
            )
        else:
            # 教师课表逻辑
            schedule_data = {
                "semester": semester or "2024-2025-1",
                "week_number": week_number,
                "courses": []
            }
        
        return {
            "code": 0,
            "message": "获取课表成功",
            "data": schedule_data,
            "timestamp": int(time.time()),
            "version": "v1.0"
        }
        
    except Exception as e:
        print(f"获取课表错误: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取课表失败"
        )


@router.get("/week/{week_number}", response_model=dict)
async def get_schedule_by_week(
    week_number: int,
    semester: Optional[str] = Query("2024-2025-1", description="学期"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取指定周课表"""
    try:
        # 🔄 HTTP请求data-service获取指定周课表
        if current_user["person_type"] == "student":
            student_id = current_user.get("student_id")
            if not student_id:
                raise HTTPException(status_code=400, detail="学生ID不能为空")
            
            schedule_data = await http_client.get_student_schedule(
                student_id=student_id,
                semester=semester,
                week_number=week_number
            )
        else:
            schedule_data = {
                "semester": semester or "2024-2025-1",
                "week_number": week_number,
                "courses": []
            }
        
        return {
            "code": 0,
            "message": "获取周课表成功",
            "data": schedule_data,
            "timestamp": int(time.time()),
            "version": "v1.0"
        }
        
    except Exception as e:
        print(f"获取周课表错误: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取周课表失败"
        )


@router.get("/current-week", response_model=dict)
async def get_current_week_schedule(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取当前周课表"""
    try:
        # 计算当前周数
        current_week = 1  # 简化处理，实际应根据学期开始时间计算
        
        # 🔄 HTTP请求data-service获取当前周课表
        if current_user["person_type"] == "student":
            student_id = current_user.get("student_id")
            if not student_id:
                raise HTTPException(status_code=400, detail="学生ID不能为空")
            
            schedule_data = await http_client.get_student_schedule(
                student_id=student_id,
                semester="2024-2025-1",
                week_number=current_week
            )
        else:
            schedule_data = {
                "semester": "2024-2025-1",
                "week_number": current_week,
                "courses": []
            }
        
        return {
            "code": 0,
            "message": "获取当前周课表成功",
            "data": schedule_data,
            "timestamp": int(time.time()),
            "version": "v1.0"
        }
        
    except Exception as e:
        print(f"获取当前周课表错误: {e}")
        raise HTTPException(
            status_code=500,
            detail="获取当前周课表失败"
        )


@router.get("/grid/{week_number}", response_model=dict)
async def get_schedule_grid(
    week_number: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取课表网格数据"""
    try:
        # 🔄 HTTP请求data-service获取课表数据
        schedule_data = await http_client.get_student_schedule(
            student_id=current_user.get("student_id"),
            semester="2024-2025-1",
            week_number=week_number
        )
        
        # 转换为网格格式
        grid_data = []
        for course in schedule_data.get("courses", []):
            schedule_info = course.get("schedule", {})
            grid_data.append({
                "day": schedule_info.get("weekday", 1),
                "period": 1,  # 简化处理
                "course": course
            })
        
        return {
            "code": 0,
            "message": "获取课表网格数据成功",
            "data": {
                "week_number": week_number,
                "grid": grid_data,
                "time_slots": {
                    "1": {"name": "第1-2节", "time": "08:30-10:10"},
                    "2": {"name": "第3-4节", "time": "10:30-12:10"},
                    "3": {"name": "第5-6节", "time": "14:00-15:40"},
                    "4": {"name": "第7-8节", "time": "16:00-17:40"},
                    "5": {"name": "第9-10节", "time": "19:00-20:40"}
                }
            },
            "timestamp": int(time.time()),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取课表网格失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }


@router.get("/today", response_model=dict)
async def get_today_schedule(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取今日课表"""
    try:
        current_week = 10
        student_id = current_user.get("student_id") or current_user.get("person_id")
        result = await http_client.get_student_schedule(
            student_id=student_id,
            week_number=current_week
        )
        
        # 获取今天是周几
        today_weekday = datetime.now().weekday() + 1  # 1=周一, 7=周日
        
        # 过滤今日课程
        today_courses = [
            course for course in result["courses"]
            if course["weekday"] == today_weekday
        ]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "weekday": today_weekday,
                "weekday_name": ["", "周一", "周二", "周三", "周四", "周五", "周六", "周日"][today_weekday],
                "courses": today_courses,
                "course_count": len(today_courses)
            },
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取今日课表失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }


@router.get("/conflicts", response_model=dict)
async def check_schedule_conflicts(
    week_number: Optional[int] = Query(None, description="检查的周次"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """检查课表冲突"""
    try:
        student_id = current_user.get("student_id") or current_user.get("person_id")
        result = await http_client.get_student_schedule(
            student_id=student_id,
            week_number=week_number
        )
        
        # 简单的冲突检测逻辑
        conflicts = []
        courses = result["courses"]
        
        for i, course1 in enumerate(courses):
            for j, course2 in enumerate(courses[i+1:], i+1):
                if (course1["weekday"] == course2["weekday"] and 
                    course1["start_time"] == course2["start_time"]):
                    conflicts.append({
                        "type": "time_conflict",
                        "courses": [course1, course2],
                        "description": f"{course1['course_name']} 与 {course2['course_name']} 时间冲突"
                    })
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "has_conflicts": len(conflicts) > 0,
                "conflict_count": len(conflicts),
                "conflicts": conflicts
            },
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"检查课表冲突失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.post("/", summary="添加课程（学生选课）")
async def add_course(
    course_instance_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """添加课程（学生选课）"""
    try:
        if current_user["person_type"] != "student":
            raise HTTPException(status_code=403, detail="只有学生可以选课")
        
        # 🔄 HTTP请求data-service进行选课
        result = await http_client._request(
            "POST",
            "/insert/enrollments",
            json_data={
                "enrollment_id": f"ENR{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "student_id": current_user["student_id"],
                "course_instance_id": course_instance_id,
                "enrollment_status": "completed",
                "enrollment_time": datetime.now().isoformat(),
                "is_deleted": False
            }
        )
        
        if result.get("status") == "success":
            return {
                "code": 0,
                "message": "选课成功",
                "data": {"course_instance_id": course_instance_id},
                "timestamp": datetime.now().isoformat(),
                "version": "v1.0"
            }
        else:
            raise HTTPException(status_code=500, detail="选课失败")
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "code": 500,
            "message": f"选课失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.delete("/{schedule_id}", summary="删除课程")
async def delete_course(
    schedule_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """删除课程（退课）"""
    try:
        if current_user["person_type"] != "student":
            raise HTTPException(status_code=403, detail="只有学生可以退课")
        
        # 🔄 HTTP请求data-service进行退课
        result = await http_client._request(
            "DELETE",
            "/delete/enrollments",
            json_data={"enrollment_id": schedule_id}
        )
        
        if result.get("status") == "success":
            return {
                "code": 0,
                "message": "退课成功",
                "data": {"schedule_id": schedule_id},
                "timestamp": datetime.now().isoformat(),
                "version": "v1.0"
            }
        else:
            raise HTTPException(status_code=500, detail="退课失败")
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "code": 500,
            "message": f"退课失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        } 