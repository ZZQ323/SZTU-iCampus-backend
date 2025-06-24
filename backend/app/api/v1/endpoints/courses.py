"""
课程管理接口
提供课程信息查询、课程管理等功能
严格遵循架构分离：不直接连接数据库，仅通过HTTP请求调用data-service
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
import time

from app.api.deps import get_current_user
# 🔄 使用HTTP客户端进行真正的HTTP请求，不导入Python模块
from app.core.http_client import http_client

router = APIRouter()

@router.get("", summary="获取课程列表")
async def get_courses(
    college_id: Optional[str] = Query(None, description="学院ID"),
    major_id: Optional[str] = Query(None, description="专业ID"),
    course_type: Optional[str] = Query(None, description="课程类型"),
    current_user = Depends(get_current_user)
):
    """获取课程列表"""
    try:
        filters = {"is_deleted": False}
        if college_id:
            filters["college_id"] = college_id
        if major_id:
            filters["major_id"] = major_id
        if course_type:
            filters["course_type"] = course_type
        
        # 🔄 使用HTTP客户端查询课程数据
        result = await http_client.query_table(
            "courses",
            filters=filters,
            order_by="course_name ASC",
            limit=100
        )
        
        courses = result.get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "courses": courses,
                "total": len(courses)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询课程列表失败: {str(e)}")

@router.get("/{course_id}", summary="获取课程详情")
async def get_course_detail(
    course_id: str,
    current_user = Depends(get_current_user)
):
    """获取课程详情"""
    try:
        # 🔄 使用HTTP客户端查询课程详情
        result = await http_client.query_table(
            "courses",
            filters={
                "course_id": course_id,
                "is_deleted": False
            },
            limit=1
        )
        
        records = result.get("records", [])
        if not records:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        course = records[0]
        
        return {
            "code": 0,
            "message": "success",
            "data": course,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询课程详情失败: {str(e)}")

@router.post("/", summary="创建课程")
async def create_course(
    course_data: dict,
    current_user = Depends(get_current_user)
):
    """创建课程（管理员）"""
    try:
        # 检查权限
        if current_user["person_type"] not in ['admin', 'teacher']:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 生成课程ID
        course_id = f"C{int(datetime.now().timestamp())}"
        
        # 准备插入数据
        insert_data = {
            "course_id": course_id,
            "course_name": course_data.get("course_name"),
            "course_code": course_data.get("course_code"),
            "credit_hours": course_data.get("credit_hours", 0),
            "course_type": course_data.get("course_type", "required"),
            "college_id": course_data.get("college_id"),
            "major_id": course_data.get("major_id"),
            "description": course_data.get("description", ""),
            "created_by": current_user["person_id"],
            "created_at": datetime.now().isoformat(),
            "is_deleted": False
        }
        
        # 🔄 使用HTTP客户端插入课程
        await http_client._request(
            "POST",
            "/insert/courses",
            json_data=insert_data
        )
        
        return {
            "code": 0,
            "message": "创建课程成功",
            "data": insert_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建课程失败: {str(e)}")

@router.put("/{course_id}", summary="更新课程信息")
async def update_course(
    course_id: str,
    course_data: dict,
    current_user = Depends(get_current_user)
):
    """更新课程信息"""
    try:
        # 检查权限
        if current_user["person_type"] not in ['admin', 'teacher']:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 准备更新数据
        update_data = {
            "filters": {"course_id": course_id},
            "updates": {
                **course_data,
                "updated_by": current_user["person_id"],
                "updated_at": datetime.now().isoformat()
            }
        }
        
        # 🔄 使用HTTP客户端更新课程
        result = await http_client._request(
            "POST",
            "/update/courses",
            json_data=update_data
        )
        
        if result.get("data", {}).get("affected_rows", 0) == 0:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        return {
            "code": 0,
            "message": "更新课程成功",
            "data": {"course_id": course_id, "updated": True},
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新课程失败: {str(e)}")

@router.delete("/{course_id}", summary="删除课程")
async def delete_course(
    course_id: str,
    current_user = Depends(get_current_user)
):
    """删除课程"""
    try:
        # 检查权限
        if current_user["person_type"] not in ['admin']:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 🔄 使用HTTP客户端软删除课程
        result = await http_client._request(
            "DELETE",
            "/delete/courses",
            json_data={"course_id": course_id}
        )
        
        if result.get("data", {}).get("affected_rows", 0) == 0:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        return {
            "code": 0,
            "message": "删除课程成功",
            "data": {"course_id": course_id, "deleted": True},
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除课程失败: {str(e)}")

@router.get("/{course_id}/instances", summary="获取课程开课实例")
async def get_course_instances(
    course_id: str,
    current_user = Depends(get_current_user)
):
    """获取课程开课实例"""
    try:
        # 🔄 使用HTTP客户端查询开课实例
        result = await http_client.query_table(
            "course_instances",
            filters={
                "course_id": course_id,
                "is_deleted": False
            },
            order_by="semester DESC"
        )
        
        instances = result.get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "course_id": course_id,
                "instances": instances,
                "total": len(instances)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询开课实例失败: {str(e)}")

@router.post("/{course_id}/instances", summary="创建开课实例")
async def create_course_instance(
    course_id: str,
    instance_data: dict,
    current_user = Depends(get_current_user)
):
    """创建开课实例"""
    try:
        # 检查权限
        if current_user["person_type"] not in ['admin', 'teacher']:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 生成实例ID
        instance_id = f"CI{int(datetime.now().timestamp())}"
        
        # 准备插入数据
        insert_data = {
            "instance_id": instance_id,
            "course_id": course_id,
            "semester": instance_data.get("semester"),
            "academic_year": instance_data.get("academic_year"),
            "teacher_id": instance_data.get("teacher_id"),
            "instructor_name": instance_data.get("instructor_name"),
            "classroom_location": instance_data.get("classroom_location"),
            "max_students": instance_data.get("max_students", 50),
            "current_students": 0,
            "created_by": current_user["person_id"],
            "created_at": datetime.now().isoformat(),
            "is_deleted": False
        }
        
        # 🔄 使用HTTP客户端插入开课实例
        await http_client._request(
            "POST",
            "/insert/course_instances",
            json_data=insert_data
        )
        
        return {
            "code": 0,
            "message": "创建开课实例成功",
            "data": insert_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建开课实例失败: {str(e)}")

@router.get("/instances/{instance_id}/students", summary="获取选课学生列表")
async def get_instance_students(
    instance_id: str,
    current_user = Depends(get_current_user)
):
    """获取选课学生列表"""
    try:
        # 🔄 使用HTTP客户端查询选课学生
        result = await http_client.query_table(
            "enrollments",
            filters={
                "course_instance_id": instance_id,
                "is_deleted": False
            },
            order_by="enrollment_time ASC"
        )
        
        enrollments = result.get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "instance_id": instance_id,
                "enrollments": enrollments,
                "total": len(enrollments)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询选课学生失败: {str(e)}")

@router.get("/instances/{instance_id}/statistics", summary="获取课程统计")
async def get_instance_statistics(
    instance_id: str,
    current_user = Depends(get_current_user)
):
    """获取课程统计"""
    try:
        # 🔄 使用HTTP客户端获取统计信息（简化版本）
        enrolled_result = await http_client.query_table(
            "enrollments", 
            filters={"course_instance_id": instance_id, "is_deleted": False}
        )
        enrolled_count = len(enrolled_result.get("records", []))
        
        passed_result = await http_client.query_table(
            "grades",
            filters={"course_instance_id": instance_id, "is_passed": True}
        )
        passed_count = len(passed_result.get("records", []))
        
        # 计算平均分（简化版本）
        grades_result = await http_client.query_table(
            "grades",
            filters={"course_instance_id": instance_id}
        )
        grades = grades_result.get("records", [])
        
        total_score = sum(grade.get("total_score", 0) for grade in grades if grade.get("total_score"))
        avg_score = round(total_score / len(grades), 2) if grades else 0
        
        stats = {
            "instance_id": instance_id,
            "enrolled_count": enrolled_count,
            "passed_count": passed_count,
            "pass_rate": round((passed_count / enrolled_count * 100), 2) if enrolled_count > 0 else 0,
            "avg_score": avg_score
        }
        
        return {
            "code": 0,
            "message": "success",
            "data": {"statistics": stats},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取课程统计失败: {str(e)}") 