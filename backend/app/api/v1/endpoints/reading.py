"""
阅读记录模块 API - 通过HTTP请求data-service获取数据
"""
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends

from app.api.deps import get_current_user
# 🔄 使用HTTP客户端进行真正的HTTP请求，不导入Python模块
from app.core.http_client import http_client

router = APIRouter()

@router.post("/record", summary="记录阅读行为")
async def record_reading(
    content_type: str,
    content_id: str,
    read_time: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """记录阅读行为"""
    try:
        # 准备阅读记录数据
        reading_data = {
            "record_id": f"RD{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": current_user["person_id"],
            "content_type": content_type,
            "content_id": content_id,
            "read_duration": read_time or 0,
            "first_read_time": datetime.now().isoformat(),
            "last_read_time": datetime.now().isoformat(),
            "read_count": 1,
            "is_liked": False,
            "is_bookmarked": False,
            "is_shared": False,
            "is_deleted": False
        }
        
        # 🔄 HTTP请求data-service记录阅读 - 使用正确的表名
        result = await http_client._request(
            "POST",
            "/insert/user_reading_records",
            json_data=reading_data
        )
        
        return {
            "code": 0,
            "message": "阅读记录成功",
            "data": reading_data,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 422,  # 返回422而不是500，与前端错误匹配
            "message": f"记录阅读失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.get("/history", summary="获取阅读历史")
async def get_reading_history(
    content_type: Optional[str] = Query(None, description="内容类型"),
    limit: int = Query(20, description="返回条数"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取阅读历史"""
    try:
        filters = {
            "user_id": current_user["person_id"],
            "is_deleted": False
        }
        if content_type:
            filters["content_type"] = content_type
        
        # 🔄 HTTP请求data-service获取阅读历史
        result = await http_client.query_table(
            "reading_records",
            filters=filters,
            limit=limit,
            order_by="start_time DESC"
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
            "message": f"获取阅读历史失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.post("/bookmark", summary="添加书签")
async def add_bookmark(
    content_type: str,
    content_id: str,
    title: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """添加书签"""
    try:
        # 准备书签数据
        bookmark_data = {
            "bookmark_id": f"BM{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": current_user["person_id"],
            "content_type": content_type,
            "content_id": content_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "is_deleted": False
        }
        
        # 🔄 HTTP请求data-service添加书签
        result = await http_client._request(
            "POST",
            "/insert/bookmarks",
            json_data=bookmark_data
        )
        
        return {
            "code": 0,
            "message": "书签添加成功",
            "data": bookmark_data,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"添加书签失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.delete("/bookmark/{bookmark_id}", summary="删除书签")
async def delete_bookmark(
    bookmark_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """删除书签"""
    try:
        # 🔄 HTTP请求data-service删除书签
        result = await http_client._request(
            "DELETE",
            "/delete/bookmarks",
            json_data={
                "bookmark_id": bookmark_id,
                "user_id": current_user["person_id"]
            }
        )
        
        return {
            "code": 0,
            "message": "书签删除成功",
            "data": {"bookmark_id": bookmark_id},
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"删除书签失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.get("/bookmarks", summary="获取书签列表")
async def get_bookmarks(
    content_type: Optional[str] = Query(None, description="内容类型"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取书签列表"""
    try:
        filters = {
            "user_id": current_user["person_id"],
            "is_deleted": False
        }
        if content_type:
            filters["content_type"] = content_type
        
        # 🔄 HTTP请求data-service获取书签
        result = await http_client.query_table(
            "bookmarks",
            filters=filters,
            order_by="created_at DESC"
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
            "message": f"获取书签失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.post("/share", summary="分享内容")
async def share_content(
    content_type: str,
    content_id: str,
    share_method: str = "link",
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """分享内容"""
    
    try:
        # 调用data-service记录分享行为
        # 草拟吗的直连
        result = await http_client._request(
            "POST",
            "/insert/shares",
            json_data={
                "user_id": current_user["person_id"],
                "content_type": content_type,
                "content_id": content_id,
                "share_method": share_method
            }
        )
        
        return {
            "code": 0,
            "message": "分享成功",
            "data": result,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"分享失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.get("/analytics", summary="获取阅读分析")
async def get_reading_analytics(
    period: str = Query("week", description="统计周期: week, month, year"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取阅读分析"""
    
    try:
        # 调用data-service获取阅读分析数据
        # 草拟吗的直连
        result = await http_client._request(
            "GET",
            f"/analytics/reading?period={period}&user_id={current_user['person_id']}"
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
            "message": f"获取阅读分析失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        } 