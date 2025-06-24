"""
校园卡模块 API - 严格按照API文档要求，通过HTTP请求data-service获取数据
"""
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.deps import get_current_user
from app.core.http_client import http_client

router = APIRouter()

@router.get("", summary="获取校园卡信息")
async def get_campus_card_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """获取校园卡信息"""
    try:
        # 🔄 HTTP请求data-service获取校园卡信息
        result = await http_client.query_table(
            "campus_cards",
            filters={
                "person_id": current_user["person_id"],
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
            "message": f"获取校园卡信息失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }

@router.get("/transactions", summary="获取交易记录")
async def get_transactions(
    page: int = Query(1, description="页码"),
    size: int = Query(20, description="每页数量"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取交易记录"""
    try:
        offset = (page - 1) * size
        filters = {
            "person_id": current_user["person_id"],
            "is_deleted": False
        }
        
        # 🔄 HTTP请求data-service获取交易记录
        result = await http_client.query_table(
            "transactions",
            filters=filters,
            limit=size,
            offset=offset,
            order_by="transaction_time DESC"
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
            "message": f"获取交易记录失败: {str(e)}",
            "data": None,
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }