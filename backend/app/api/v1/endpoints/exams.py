"""
考试管理API端点
提供考试信息查询、考试安排等功能
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.api import deps

router = APIRouter(tags=["exams"])

@router.get("/")
async def get_exams(
    student_id: str = Query("2024001", description="学生学号"),
    exam_type: Optional[str] = Query(None, description="考试类型：final, midterm, makeup"),
    semester: Optional[str] = Query(None, description="学期"),
    upcoming_only: bool = Query(False, description="仅显示即将开始的考试"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(deps.get_db)
):
    """
    获取考试列表
    
    - **student_id**: 学生学号
    - **exam_type**: 考试类型筛选
    - **semester**: 学期筛选
    - **upcoming_only**: 是否只显示即将开始的考试
    """
    
    # 模拟考试数据（实际应从数据库查询）
    mock_exams = [
        {
            "id": 1,
            "course_name": "高等数学A",
            "course_code": "MATH001",
            "exam_type": "final",
            "exam_date": "2024-01-15",
            "start_time": "14:30",
            "end_time": "16:30",
            "duration": 120,
            "location": "教学楼A101",
            "seat_number": "A001",
            "teacher": "张教授",
            "exam_form": "闭卷",
            "total_score": 100,
            "status": "scheduled"
        },
        {
            "id": 2,
            "course_name": "大学英语",
            "course_code": "ENG001", 
            "exam_type": "final",
            "exam_date": "2024-01-16",
            "start_time": "09:00",
            "end_time": "11:00",
            "duration": 120,
            "location": "教学楼B203",
            "seat_number": "B015",
            "teacher": "李老师",
            "exam_form": "闭卷",
            "total_score": 100,
            "status": "scheduled"
        },
        {
            "id": 3,
            "course_name": "计算机程序设计",
            "course_code": "CS001",
            "exam_type": "final", 
            "exam_date": "2024-01-18",
            "start_time": "14:30",
            "end_time": "16:30",
            "duration": 120,
            "location": "实验楼C301",
            "seat_number": "C024",
            "teacher": "王副教授",
            "exam_form": "上机",
            "total_score": 100,
            "status": "scheduled"
        }
    ]
    
    # 根据参数筛选
    filtered_exams = mock_exams
    
    if exam_type:
        filtered_exams = [e for e in filtered_exams if e["exam_type"] == exam_type]
    
    # 分页
    total = len(filtered_exams)
    exams = filtered_exams[skip:skip + limit]
    
    # 计算下一场考试
    next_exam = None
    current_date = datetime.now().date()
    for exam in exams:
        exam_date = datetime.strptime(exam["exam_date"], "%Y-%m-%d").date()
        if exam_date >= current_date:
            next_exam = exam
            break
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "exams": exams,
            "total": total,
            "next_exam": next_exam,
            "student_id": student_id
        }
    }

@router.get("/{exam_id}")
async def get_exam_detail(
    exam_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    获取考试详情
    """
    # 模拟数据
    exam_detail = {
        "id": exam_id,
        "course_name": "高等数学A",
        "course_code": "MATH001",
        "exam_type": "final",
        "exam_date": "2024-01-15",
        "start_time": "14:30", 
        "end_time": "16:30",
        "duration": 120,
        "location": "教学楼A101",
        "seat_number": "A001",
        "teacher": "张教授",
        "exam_form": "闭卷",
        "total_score": 100,
        "status": "scheduled",
        "requirements": [
            "携带身份证和学生证",
            "禁止携带手机等电子设备",
            "考试用品：黑色签字笔、2B铅笔、橡皮擦",
            "提前30分钟到达考场"
        ],
        "notes": "请准时参加考试，迟到15分钟不得入场。"
    }
    
    return {
        "code": 0,
        "message": "success", 
        "data": exam_detail
    }

@router.get("/countdown/{exam_id}")
async def get_exam_countdown(
    exam_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    获取考试倒计时
    """
    # 模拟考试时间
    exam_datetime = datetime(2024, 1, 15, 14, 30, 0)
    current_datetime = datetime.now()
    
    diff = exam_datetime - current_datetime
    
    if diff.total_seconds() <= 0:
        return {
            "code": 0,
            "message": "success",
            "data": {
                "status": "started",
                "message": "考试已开始"
            }
        }
    
    days = diff.days
    seconds = diff.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "status": "countdown",
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": int(diff.total_seconds()),
            "formatted": f"{days}天{hours}小时{minutes}分{seconds}秒"
        }
    } 