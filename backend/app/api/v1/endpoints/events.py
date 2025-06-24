"""
活动事件模块 API - 通过HTTP请求data-service获取数据
"""
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends

from app.api.deps import get_current_user
# 🔄 使用HTTP客户端进行真正的HTTP请求，不导入Python模块
from app.core.http_client import http_client

router = APIRouter()

@router.get("", summary="获取活动列表")
async def get_events(
    category: Optional[str] = Query(None, description="活动分类"),
    status: Optional[str] = Query(None, description="活动状态"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取活动列表"""
    try:
        filters = {"is_deleted": False}
        if category:
            filters["category"] = category
        if status:
            filters["status"] = status
        
        # 🔄 HTTP请求data-service获取活动
        result = await http_client.query_table(
            "events",
            filters=filters,
            order_by="start_time ASC"
        )
        
        # 🔧 修复：提取events数组并按前端期望格式返回
        events = result.get("data", {}).get("records", [])
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "events": events,  # 前端期望的格式
                "total": len(events),
                "has_more": False
            },
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取活动列表失败: {str(e)}",
            "data": {
                "events": [],  # 确保失败时也返回正确格式
                "total": 0,
                "has_more": False
            },
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.get("/{event_id}", summary="获取活动详情")
async def get_event_detail(
    event_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取活动详情"""
    try:
        # 🔄 HTTP请求data-service获取活动详情
        result = await http_client.query_table(
            "events",
            filters={
                "event_id": event_id,
                "is_deleted": False
            },
            limit=1
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
            "message": f"获取活动详情失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.post("/", summary="创建活动")
async def create_event(
    event_data: dict,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """创建活动"""
    try:
        # 生成活动ID
        event_id = f"EVT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 准备插入数据
        insert_data = {
            "event_id": event_id,
            "title": event_data.get("title"),
            "description": event_data.get("description"),
            "category": event_data.get("category", "general"),
            "start_time": event_data.get("start_time"),
            "end_time": event_data.get("end_time"),
            "location": event_data.get("location"),
            "organizer_id": current_user["person_id"],
            "max_participants": event_data.get("max_participants", 100),
            "status": "upcoming",
            "created_at": datetime.now().isoformat(),
            "is_deleted": False
        }
        
        # 🔄 HTTP请求data-service创建活动
        result = await http_client._request(
            "POST",
            "/insert/events",
            json_data=insert_data
        )
        
        return {
            "code": 0,
            "message": "活动创建成功",
            "data": insert_data,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"创建活动失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.post("/{event_id}/register", summary="报名活动")
async def register_event(
    event_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """报名活动"""
    try:
        # 准备注册数据
        registration_data = {
            "registration_id": f"REG{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "event_id": event_id,
            "participant_id": current_user["person_id"],
            "registration_time": datetime.now().isoformat(),
            "status": "registered",
            "is_deleted": False
        }
        
        # 🔄 HTTP请求data-service进行报名
        result = await http_client._request(
            "POST",
            "/insert/event_registrations",
            json_data=registration_data
        )
        
        return {
            "code": 0,
            "message": "报名成功",
            "data": registration_data,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"报名失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.delete("/{event_id}/register", summary="取消报名")
async def cancel_event_registration(
    event_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """取消报名"""
    try:
        # 🔄 HTTP请求data-service取消报名
        result = await http_client._request(
            "DELETE",
            "/delete/event_registrations",
            json_data={
                "event_id": event_id,
                "participant_id": current_user["person_id"]
            }
        )
        
        return {
            "code": 0,
            "message": "取消报名成功",
            "data": {"event_id": event_id},
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"取消报名失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        } 