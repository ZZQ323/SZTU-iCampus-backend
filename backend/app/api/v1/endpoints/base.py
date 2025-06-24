"""
基础数据模块 API
提供学院、专业、班级、部门、场所等基础数据查询
严格遵循架构分离：不直接连接数据库，仅通过HTTP请求调用data-service
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.deps import get_current_user
# 🔄 使用HTTP客户端进行真正的HTTP请求，不导入Python模块
from app.core.http_client import http_client

router = APIRouter()

@router.get("/colleges", summary="获取学院列表")
async def get_colleges(current_user = Depends(get_current_user)):
    """获取学院列表"""
    try:
        # 🔄 HTTP请求data-service查询学院数据
        result = await http_client.query_table(
            "colleges",
            filters={"is_deleted": False},
            order_by="college_name ASC"
        )
        
        colleges = result.get("data", {}).get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "colleges": colleges,
                "total": len(colleges)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询学院列表失败: {str(e)}")

@router.get("/colleges/{college_id}/majors", summary="获取学院专业列表")
async def get_college_majors(
    college_id: str,
    current_user = Depends(get_current_user)
):
    """获取指定学院的专业列表"""
    try:
        # 🔄 HTTP请求data-service查询专业数据
        result = await http_client.query_table(
            "majors",
            filters={
                "college_id": college_id,
                "is_deleted": False
            },
            order_by="major_name ASC"
        )
        
        majors = result.get("data", {}).get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "college_id": college_id,
                "majors": majors,
                "total": len(majors)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询专业列表失败: {str(e)}")

@router.get("/majors", summary="获取专业列表")
async def get_majors(
    college_id: Optional[str] = Query(None, description="学院ID"),
    current_user = Depends(get_current_user)
):
    """获取专业列表"""
    try:
        filters = {"is_deleted": False}
        if college_id:
            filters["college_id"] = college_id
        
        # 🔄 HTTP请求data-service查询专业数据
        result = await http_client.query_table(
            "majors",
            filters=filters,
            order_by="major_name ASC"
        )
        
        majors = result.get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "majors": majors,
                "total": len(majors)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询专业列表失败: {str(e)}")

@router.get("/majors/{major_id}/classes", summary="获取专业班级列表")
async def get_major_classes(
    major_id: str,
    current_user = Depends(get_current_user)
):
    """获取指定专业的班级列表"""
    try:
        # 🔄 HTTP请求data-service查询班级数据
        result = await http_client.query_table(
            "classes",
            filters={
                "major_id": major_id,
                "is_deleted": False
            },
            order_by="class_name ASC"
        )
        
        classes = result.get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "major_id": major_id,
                "classes": classes,
                "total": len(classes)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询班级列表失败: {str(e)}")

@router.get("/classes", summary="获取班级列表")
async def get_classes(
    major_id: Optional[str] = Query(None, description="专业ID"),
    current_user = Depends(get_current_user)
):
    """获取班级列表"""
    try:
        filters = {"is_deleted": False}
        if major_id:
            filters["major_id"] = major_id
        
        # 🔄 HTTP请求data-service查询班级数据
        result = await http_client.query_table(
            "classes",
            filters=filters,
            order_by="class_name ASC"
        )
        
        classes = result.get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "classes": classes,
                "total": len(classes)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询班级列表失败: {str(e)}")

@router.get("/departments", summary="获取部门列表")
async def get_departments(current_user = Depends(get_current_user)):
    """获取部门列表"""
    try:
        # 🔄 HTTP请求data-service查询部门数据
        result = await http_client.query_table(
            "departments",
            filters={"is_deleted": False},
            order_by="department_name ASC"
        )
        
        departments = result.get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "departments": departments,
                "total": len(departments)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询部门列表失败: {str(e)}")

@router.get("/locations", summary="获取场所列表")
async def get_locations(current_user = Depends(get_current_user)):
    """获取场所列表"""
    try:
        # 🔄 HTTP请求data-service查询场所数据
        result = await http_client.query_table(
            "locations",
            filters={"is_deleted": False},
            order_by="location_name ASC"
        )
        
        locations = result.get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "locations": locations,
                "total": len(locations)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询场所列表失败: {str(e)}")

@router.get("/locations/{location_id}/occupations", summary="获取场所占用情况")
async def get_location_occupations(
    location_id: str,
    current_user = Depends(get_current_user)
):
    """获取指定场所的占用情况"""
    try:
        # 🔄 HTTP请求data-service查询占用情况
        result = await http_client.query_table(
            "room_occupations",
            filters={
                "location_id": location_id,
                "is_deleted": False
            },
            order_by="start_time ASC"
        )
        
        occupations = result.get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "location_id": location_id,
                "occupations": occupations,
                "total": len(occupations)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询场所占用情况失败: {str(e)}") 