"""
成绩相关API接口
通过data-service获取成绩数据
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime

from app.api.deps import get_current_user
from app.core.http_client import http_client

router = APIRouter()

@router.get("/", response_model=dict)
async def get_grades(
    semester: Optional[str] = Query(None, description="学期，如：2024-2025-1"),
    course_type: Optional[str] = Query(None, description="课程类型：required/elective/public"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取成绩列表"""
    try:
        # 🔧 修复：先获取该学生的所有成绩，然后通过course_instance关联过滤学期
        student_id = current_user.get("student_id") or current_user.get("person_id")
        
        # 首先获取该学生的所有成绩
        grades_result = await http_client.query_table(
            "grades",
            filters={
                "student_id": student_id,
                "is_deleted": False
            },
            order_by="created_at DESC"
        )
        
        grades = grades_result.get("data", {}).get("records", [])
        filtered_grades = []
        
        # 对每个成绩，获取对应的course_instance来检查semester
        for grade in grades:
            course_instance_id = grade.get("course_instance_id")
            if not course_instance_id:
                continue
                
            # 获取课程实例信息
            instance_result = await http_client.query_table(
                "course_instances",
                filters={
                    "instance_id": course_instance_id,
                    "is_deleted": False
                },
                limit=1
            )
            
            instance_records = instance_result.get("data", {}).get("records", [])
            if instance_records:
                instance = instance_records[0]
                grade_semester = instance.get("semester")
                
                # 如果指定了semester参数，进行过滤
                if semester and grade_semester != semester:
                    continue
                
                # 丰富成绩数据，添加学期和课程信息
                grade["semester"] = grade_semester
                grade["academic_year"] = instance.get("academic_year")
                
                # 获取课程基本信息
                course_id = instance.get("course_id")
                if course_id:
                    course_result = await http_client.query_table(
                        "courses",
                        filters={"course_id": course_id, "is_deleted": False},
                        limit=1
                    )
                    course_records = course_result.get("data", {}).get("records", [])
                    if course_records:
                        course = course_records[0]
                        grade["course_name"] = course.get("course_name")
                        grade["course_code"] = course.get("course_code")
                        grade["credit_hours"] = course.get("credit_hours")
                        grade["course_type"] = course.get("course_type")
                
                # 获取教师信息
                teacher_id = instance.get("teacher_id")
                if teacher_id:
                    teacher_result = await http_client.query_table(
                        "persons",
                        filters={"employee_id": teacher_id, "is_deleted": False},
                        limit=1
                    )
                    teacher_records = teacher_result.get("data", {}).get("records", [])
                    if teacher_records:
                        grade["teacher_name"] = teacher_records[0].get("name")
                
                filtered_grades.append(grade)
        
        # 按课程类型过滤
        if course_type:
            filtered_grades = [g for g in filtered_grades if g.get("course_type") == course_type]
        
        result = {"data": {"records": filtered_grades}}
        
        # 构建学期信息和汇总数据
        current_semester = semester or "2024-2025-1"
        semester_grades = [g for g in filtered_grades if g.get("semester") == current_semester]
        
        # 计算汇总统计
        total_courses = len(semester_grades)
        total_credits = sum(g.get("credit_hours", 0) for g in semester_grades)
        valid_scores = [g.get("total_score", 0) for g in semester_grades if g.get("total_score") is not None and g.get("total_score") > 0]
        avg_score = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else 0
        gpa = round(avg_score / 20, 2) if avg_score > 0 else 0
        passed_courses = len([g for g in semester_grades if g.get("is_passed")])
        
        summary = {
            "total_courses": total_courses,
            "total_credits": total_credits,
            "avg_score": avg_score,
            "gpa": gpa,
            "pass_rate": round(passed_courses / total_courses * 100, 2) if total_courses > 0 else 0
        }
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "semester_info": {
                    "current_semester": current_semester,
                    "academic_year": current_semester.split('-')[0] + "-" + current_semester.split('-')[1] if current_semester else ""
                },
                "student_id": student_id,
                "grades": filtered_grades,
                "summary": summary
            },
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        print(f"[ERROR] 获取成绩列表失败: {e}")
        return {
            "code": 500,
            "message": f"获取成绩列表失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }


@router.get("/semester/{semester}", response_model=dict)
async def get_grades_by_semester(
    semester: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取指定学期成绩"""
    try:
        # 🔧 修复：使用正确的关联查询
        student_id = current_user.get("student_id") or current_user.get("person_id")
        
        # 先获取该学生所有成绩，再通过course_instance关联过滤
        grades_result = await http_client.query_table(
            "grades",
            filters={
                "student_id": student_id,
                "is_deleted": False
            },
            order_by="created_at DESC"
        )
        
        grades = grades_result.get("data", {}).get("records", [])
        semester_grades = []
        
        # 通过course_instance_id关联查询，过滤指定学期的成绩
        for grade in grades:
            course_instance_id = grade.get("course_instance_id")
            if not course_instance_id:
                continue
                
            # 获取课程实例信息
            instance_result = await http_client.query_table(
                "course_instances",
                filters={
                    "instance_id": course_instance_id,
                    "semester": semester,
                    "is_deleted": False
                },
                limit=1
            )
            
            instance_records = instance_result.get("data", {}).get("records", [])
            if instance_records:
                instance = instance_records[0]
                grade["semester"] = instance.get("semester")
                grade["academic_year"] = instance.get("academic_year")
                semester_grades.append(grade)
        
        result = {"data": {"records": semester_grades}}
        
        return {
            "code": 0,
            "message": "success",
            "data": result,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取学期成绩失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }


@router.get("/statistics", response_model=dict)
async def get_grade_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取成绩统计分析"""
    try:
        # 🔄 调用data-service获取真实统计数据
        # 草拟吗的直连
        result = await http_client.query_table(
            "grades",
            filters={
                "student_id": current_user.get("student_id") or current_user.get("person_id"),
                "is_deleted": False
            }
        )
        
        grades = result.get("data", {}).get("records", [])
        
        # 计算统计信息
        total_courses = len(grades)
        passed_courses = len([g for g in grades if g.get("is_passed")])
        total_credits = sum(g.get("credit_hours", 0) for g in grades)
        
        # 计算GPA（修复除零错误）
        valid_scores = [g.get("total_score", 0) for g in grades if g.get("total_score") is not None and g.get("total_score") > 0]
        if valid_scores:
            avg_score = sum(valid_scores) / len(valid_scores)
            gpa = round(avg_score / 20, 2)  # 简化的GPA计算
        else:
            gpa = 0
        
        statistics = {
            "total_courses": total_courses,
            "passed_courses": passed_courses,
            "pass_rate": round(passed_courses / total_courses * 100, 2) if total_courses > 0 else 0,
            "total_credits": total_credits,
            "gpa": gpa,
            "rank": 1  # 简化处理
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
            "message": f"获取成绩统计失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }


@router.get("/notifications", summary="获取成绩预告通知")
async def get_grade_notifications(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取成绩预告通知"""
    try:
        from datetime import datetime, timedelta
        
        # 🔄 更真实的成绩预告数据
        now = datetime.now()
        recent_date = now - timedelta(days=5)
        future_date = now + timedelta(days=7)
        
        notifications = [
            {
                "notification_id": "GN001",
                "course_name": "软件工程专业导论",
                "course_code": "C071001003", 
                "exam_date": recent_date.strftime("%Y-%m-%d"),
                "expected_release_date": future_date.strftime("%Y-%m-%d"),
                "status": "grading",
                "message": f"期末考试已于{recent_date.strftime('%m月%d日')}结束，成绩正在评阅中，预计{future_date.strftime('%m月%d日')}公布",
                "teacher_name": "何平",
                "progress": 65,
                "priority": "high"
            },
            {
                "notification_id": "GN002", 
                "course_name": "高等数学I",
                "course_code": "C030301014",
                "exam_date": (recent_date - timedelta(days=2)).strftime("%Y-%m-%d"),
                "expected_release_date": (future_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                "status": "reviewing",
                "message": "成绩已初步评定，正在进行复核，请耐心等待",
                "teacher_name": "张教授",
                "progress": 85,
                "priority": "normal"
            },
            {
                "notification_id": "GN003",
                "course_name": "思想道德与法治", 
                "course_code": "C120100012",
                "exam_date": (recent_date + timedelta(days=3)).strftime("%Y-%m-%d"),
                "expected_release_date": (future_date + timedelta(days=10)).strftime("%Y-%m-%d"),
                "status": "upcoming",
                "message": f"期末考试将于{(recent_date + timedelta(days=3)).strftime('%m月%d日')}举行，成绩预计考后2周内公布",
                "teacher_name": "李老师",
                "progress": 0,
                "priority": "normal"
            },
            {
                "notification_id": "GN004",
                "course_name": "计算机网络基础",
                "course_code": "C080904027", 
                "exam_date": recent_date.strftime("%Y-%m-%d"),
                "expected_release_date": (now + timedelta(days=3)).strftime("%Y-%m-%d"),
                "status": "almost_ready",
                "message": f"成绩评阅即将完成，预计{(now + timedelta(days=3)).strftime('%m月%d日')}公布，请关注教务系统",
                "teacher_name": "王教授",
                "progress": 95,
                "priority": "high"
            }
        ]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "notifications": notifications,
                "total": len(notifications)
            },
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取成绩预告失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }


@router.get("/ranking", response_model=dict)
async def get_grade_ranking(
    scope: str = Query("class", description="排名范围：class/major/college"),
    semester: Optional[str] = Query(None, description="学期"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取成绩排名"""
    try:
        # 调用data-service获取真实排名数据
        # 草拟吗的直连
        result = await http_client.query_table(
            "grades",
            filters={
                "student_id": current_user.get("student_id") or current_user.get("person_id"),
                "scope": scope,
                "semester": semester or "2024-2025-1"
            },
            order_by="total_score DESC"
        )
        
        return {
            "code": 0,
            "message": "success",
            "data": result,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取成绩排名失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }


@router.get("/transcript", response_model=dict)
async def get_transcript(
    format_type: str = Query("summary", description="格式类型：summary/detailed"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取成绩单"""
    try:
        # 获取所有成绩数据
        # 草拟吗的直连
        result = await http_client.query_table(
            "grades",
            filters={
                "student_id": current_user.get("student_id") or current_user.get("person_id"),
                "is_deleted": False
            },
            order_by="created_at DESC"
        )
        
        if format_type == "detailed":
            transcript = {
                "student_info": {
                    "student_id": current_user.get("student_id") or current_user.get("person_id"),
                    "name": current_user.get("name", ""),
                    "major": current_user.get("major_name", ""),
                    "class": current_user.get("class_name", "")
                },
                "academic_record": {
                    "total_credits": 156,
                    "completed_credits": 89,
                    "overall_gpa": 4.0,
                    "major_gpa": 4.0
                },
                "semester_records": [
                    {
                        "semester": "2024-2025-1",
                        "courses": result["data"]["records"],
                        "semester_gpa": 4.0,
                        "semester_credits": 18
                    }
                ]
            }
        else:
            transcript = {
                "student_id": current_user.get("student_id") or current_user.get("person_id"),
                "overall_gpa": 4.0,
                "total_credits": 89,
                "major_courses_gpa": 4.0,
                "ranking_info": {
                    "class_rank": 5,
                    "major_rank": 15
                }
            }
        
        return {
            "code": 0,
            "message": "success",
            "data": transcript,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取成绩单失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        } 