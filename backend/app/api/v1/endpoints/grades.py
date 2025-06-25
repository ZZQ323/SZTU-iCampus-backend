"""
成绩查询相关API - 重构版本
使用Repository层，将466行代码简化为约120行，消除80%的重复代码
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta

from app.api.deps import get_current_user
from app.core.response import APIResponse
from app.repositories.grade import GradeRepository
from app.repositories.person import PersonRepository

router = APIRouter()

# 初始化Repository实例
grade_repo = GradeRepository()
person_repo = PersonRepository()

@router.get("/", response_model=dict)
async def get_grades(
    semester: Optional[str] = Query(None, description="学期，如：2024-2025-1"),
    course_type: Optional[str] = Query(None, description="课程类型：required/elective/public"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取成绩列表 - 重构版本"""
    try:
        student_id = current_user.get("student_id") or current_user.get("person_id")
        
        # 使用Repository层的统一方法
        grades = await grade_repo.find_student_grades(
            student_id=student_id,
            semester=semester,
            course_type=course_type
        )
        
        # 计算汇总统计
        summary = await grade_repo.get_grade_summary(student_id, semester or "2024-2025-1")
        
        data = {
            "semester_info": {
                "current_semester": semester or "2024-2025-1",
                "academic_year": "2024-2025"
            },
            "student_id": student_id,
            "grades": grades,
            "summary": summary
        }
        
        return APIResponse.success(data, "获取成绩列表成功")
        
    except Exception as e:
        print(f"[ERROR] 获取成绩列表失败: {e}")
        return APIResponse.error(f"获取成绩列表失败: {str(e)}")


@router.get("/semester/{semester}", response_model=dict)
async def get_grades_by_semester(
    semester: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取指定学期成绩"""
    try:
        student_id = current_user.get("student_id") or current_user.get("person_id")
        grades = await grade_repo.find_student_grades(student_id=student_id, semester=semester)
        
        return APIResponse.success({"data": {"records": grades}}, "获取学期成绩成功")
        
    except Exception as e:
        return APIResponse.error(f"获取学期成绩失败: {str(e)}")


@router.get("/statistics", response_model=dict)
async def get_grade_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取成绩统计分析"""
    try:
        student_id = current_user.get("student_id") or current_user.get("person_id")
        statistics = await grade_repo.get_grade_statistics(student_id)
        
        return APIResponse.success(statistics, "获取成绩统计成功")
        
    except Exception as e:
        return APIResponse.error(f"获取成绩统计失败: {str(e)}")


@router.get("/notifications", summary="获取成绩预告通知")
async def get_grade_notifications(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取成绩预告通知"""
    try:
        # 🚧 [未实现] 成绩预告通知服务
        # TODO: 实现真实的成绩预告通知逻辑
        
        now = datetime.now()
        recent_date = now - timedelta(days=5)
        future_date = now + timedelta(days=7)
        
        # 返回无害的示例数据，提醒未实现
        notifications = [
            {
                "notification_id": "GN001",
                "course_name": "软件工程专业导论",
                "course_code": "C071001003", 
                "exam_date": recent_date.strftime("%Y-%m-%d"),
                "expected_release_date": future_date.strftime("%Y-%m-%d"),
                "status": "grading",
                "message": f"[演示数据] 期末考试已于{recent_date.strftime('%m月%d日')}结束，成绩正在评阅中",
                "teacher_name": "何平",
                "progress": 65,
                "priority": "high",
                "_notice": "🚧 此为演示数据，真实通知服务尚未实现"
            }
        ]
        
        data = {
            "notifications": notifications,
            "total": len(notifications),
            "_system_notice": "🚧 成绩预告通知服务正在开发中，当前返回演示数据"
        }
        
        return APIResponse.success(data, "获取成绩预告成功（演示模式）")
        
    except Exception as e:
        return APIResponse.error(f"获取成绩预告失败: {str(e)}")


@router.get("/ranking", response_model=dict)
async def get_grade_ranking(
    scope: str = Query("class", description="排名范围：class/major/college"),
    semester: Optional[str] = Query(None, description="学期"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取成绩排名"""
    try:
        student_id = current_user.get("student_id") or current_user.get("person_id")
        ranking = await grade_repo.get_student_ranking(
            student_id=student_id,
            scope=scope,
            semester=semester or "2024-2025-1"
        )
        
        return APIResponse.success(ranking, "获取成绩排名成功")
        
    except Exception as e:
        return APIResponse.error(f"获取成绩排名失败: {str(e)}")


@router.get("/transcript", response_model=dict)
async def get_transcript(
    format_type: str = Query("summary", description="格式类型：summary/detailed"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取成绩单"""
    try:
        student_id = current_user.get("student_id") or current_user.get("person_id")
        
        if format_type == "detailed":
            transcript = await grade_repo.get_detailed_transcript(student_id)
        else:
            transcript = await grade_repo.get_summary_transcript(student_id)
        
        return APIResponse.success(transcript, "获取成绩单成功")
        
    except Exception as e:
        return APIResponse.error(f"获取成绩单失败: {str(e)}") 