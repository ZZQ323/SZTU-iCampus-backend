"""
考试接口
提供考试查询、倒计时等功能 - 通过data-service获取数据
"""
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.deps import get_current_user
# 🔄 使用HTTP客户端进行真正的HTTP请求，不导入Python模块
from app.core.http_client import http_client

router = APIRouter()

@router.get("", summary="获取考试列表")
async def get_exams(
    semester: Optional[str] = Query(None, description="学期"),
    exam_type: Optional[str] = Query(None, description="考试类型"),
    status: Optional[str] = Query(None, description="考试状态"),
    limit: int = Query(20, description="返回条数"),
    offset: int = Query(0, description="偏移量"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取考试列表"""
    try:
        # 🔄 从enrollments和course_instances表获取考试数据
        enrollments_result = await http_client.query_table(
            "enrollments",
            filters={
                "student_id": current_user.get("student_id"),
                "enrollment_status": "completed",
                "is_deleted": False
            },
            limit=100
        )
        
        enrollments = enrollments_result.get("data", {}).get("records", [])
        exams = []
        
        for enrollment in enrollments:
            instance_id = enrollment.get("course_instance_id")
            if not instance_id:
                continue
                
            # 获取课程实例信息（包含考试信息）
            instance_result = await http_client.query_table(
                "course_instances",
                filters={
                    "instance_id": instance_id,
                    "is_deleted": False
                },
                limit=1
            )
            
            instances = instance_result.get("data", {}).get("records", [])
            if not instances:
                continue
                
            instance = instances[0]
            
            # 获取课程基本信息
            course_result = await http_client.query_table(
                "courses",
                filters={
                    "course_id": instance.get("course_id"),
                    "is_deleted": False
                },
                limit=1
            )
            
            courses = course_result.get("data", {}).get("records", [])
            
            # 如果有考试信息，则添加到列表
            if instance.get("exam_date"):
                exam = {
                    "exam_id": f"EX{instance_id}",
                    "course_name": courses[0].get("course_name") if courses else None,
                    "course_code": instance.get("course_id"),
                    "exam_date": instance.get("exam_date"),
                    "exam_location": instance.get("exam_location"),
                    "makeup_exam_date": instance.get("makeup_exam_date")
                }
                exams.append(exam)
        
        # 分页处理
        total = len(exams)
        paginated_exams = exams[offset:offset + limit]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "exams": paginated_exams,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            },
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取考试列表失败: {str(e)}",
            "data": {
                "exams": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "has_more": False
            },
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }


@router.get("/statistics", summary="获取考试统计")
async def get_exam_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取考试统计"""
    try:
        # 🔄 从实际数据计算统计
        enrollments_result = await http_client.query_table(
            "enrollments",
            filters={
                "student_id": current_user.get("student_id"),
                "enrollment_status": "completed",
                "is_deleted": False
            },
            limit=100
        )
        
        enrollments = enrollments_result.get("data", {}).get("records", [])
        total_exams = 0
        upcoming_exams = 0
        completed_exams = 0
        
        for enrollment in enrollments:
            instance_id = enrollment.get("course_instance_id")
            if not instance_id:
                continue
                
            instance_result = await http_client.query_table(
                "course_instances", 
                filters={
                    "instance_id": instance_id,
                    "is_deleted": False
                },
                limit=1
            )
            
            instances = instance_result.get("data", {}).get("records", [])
            if instances and instances[0].get("exam_date"):
                total_exams += 1
                exam_date = instances[0].get("exam_date")
                if exam_date:
                    from datetime import datetime
                    try:
                        exam_datetime = datetime.fromisoformat(exam_date.replace('Z', '+00:00'))
                        if exam_datetime > datetime.now():
                            upcoming_exams += 1
                        else:
                            completed_exams += 1
                    except:
                        upcoming_exams += 1
        
        # 🔥 删除所有模拟数据，只返回真实计算结果
        statistics = {
            "total_exams": total_exams,
            "upcoming_exams": upcoming_exams,
            "completed_exams": completed_exams,
            "not_scheduled_count": len(enrollments) - total_exams
        }
        
        return {
            "code": 0,
            "message": "success",
            "data": statistics,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取考试统计失败: {str(e)}",
            "data": {
                "total_exams": 0,
                "upcoming_exams": 0,
                "completed_exams": 0,
                "not_scheduled_count": 0,
                "average_score": 0,
                "next_exam": None,
                "recent_exams": []
            },
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }


@router.get("/{exam_id}", summary="获取考试详情")
async def get_exam_detail(
    exam_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取考试详情"""
    try:
        instance_id = exam_id.replace("EX", "") if exam_id.startswith("EX") else exam_id
        
        instance_result = await http_client.query_table(
            "course_instances",
            filters={
                "instance_id": instance_id,
                "is_deleted": False
            },
            limit=1
        )
        
        instances = instance_result.get("data", {}).get("records", [])
        if not instances:
            return {
                "code": 404,
                "message": "考试不存在",
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "version": "v1.0"
            }
        
        instance = instances[0]
        
        # 获取课程基本信息
        course_result = await http_client.query_table(
            "courses",
            filters={
                "course_id": instance.get("course_id"),
                "is_deleted": False
            },
            limit=1
        )
        
        courses = course_result.get("data", {}).get("records", [])
        
        # 🔥 删除所有模拟数据，只返回数据库真实数据
        exam_detail = {
            "exam_id": exam_id,
            "course_name": courses[0].get("course_name") if courses else None,
            "course_code": instance.get("course_id"),
            "exam_date": instance.get("exam_date"),
            "exam_location": instance.get("exam_location"),
            "makeup_exam_date": instance.get("makeup_exam_date"),
            "teacher_id": instance.get("teacher_id"),
            "instance_status": instance.get("instance_status")
        }
        
        return {
            "code": 0,
            "message": "success",
            "data": exam_detail,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取考试详情失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }


@router.get("/{exam_id}/countdown", summary="获取考试倒计时")
async def get_exam_countdown(
    exam_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取考试倒计时"""
    try:
        # 🔄 修复：从course_instances表获取考试信息（exam_id格式为EXinstance_id）
        instance_id = exam_id.replace("EX", "") if exam_id.startswith("EX") else exam_id
        
        # 获取课程实例信息（包含考试信息）
        instance_result = await http_client.query_table(
            "course_instances",
            filters={
                "instance_id": instance_id,
                "is_deleted": False
            },
            limit=1
        )
        
        instances = instance_result.get("data", {}).get("records", [])
        if not instances:
            return {
                "code": 404,
                "message": "考试不存在",
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "version": "v1.0"
            }
        
        instance = instances[0]
        exam_date = instance.get("exam_date")
        
        # 计算倒计时
        if not exam_date:
            countdown_data = {
                "exam_id": exam_id,
                "status": "not_scheduled",
                "message": "考试时间未安排",
                "countdown": None
            }
        else:
            try:
                exam_time = datetime.fromisoformat(exam_date.replace("Z", "+00:00"))
                now = datetime.now()
                
                if exam_time <= now:
                    countdown_data = {
                        "exam_id": exam_id,
                        "exam_date": exam_date,
                        "status": "completed",
                        "countdown": {
                            "days": 0,
                            "hours": 0,
                            "minutes": 0,
                            "seconds": 0,
                            "total_seconds": 0
                        }
                    }
                else:
                    countdown = exam_time - now
                    countdown_data = {
                        "exam_id": exam_id,
                        "exam_date": exam_date,
                        "status": "upcoming",
                        "countdown": {
                            "days": countdown.days,
                            "hours": countdown.seconds // 3600,
                            "minutes": (countdown.seconds % 3600) // 60,
                            "seconds": countdown.seconds % 60,
                            "total_seconds": int(countdown.total_seconds())
                        }
                    }
            except (ValueError, TypeError):
                countdown_data = {
                    "exam_id": exam_id,
                    "status": "error",
                    "message": "考试时间格式错误",
                    "countdown": None
                }
        
        return {
            "code": 0,
            "message": "success",
            "data": countdown_data,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取考试倒计时失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        } 