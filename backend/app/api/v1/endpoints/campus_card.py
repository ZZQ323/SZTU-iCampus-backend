"""
校园卡模块 API - 重构版本
使用Repository层，消除重复代码，提升可维护性
"""
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Query, Depends

from app.api.deps import get_current_user
from app.core.response import APIResponse
from app.repositories.campus_card import CampusCardRepository

router = APIRouter()

# 初始化Repository实例
campus_card_repo = CampusCardRepository()

@router.get("/info", summary="获取校园卡信息")
async def get_campus_card_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """获取校园卡信息"""
    try:
        card_info = await campus_card_repo.find_by_person_id(current_user["person_id"])
        
        if not card_info:
            return APIResponse.not_found("校园卡信息不存在")
        
        return APIResponse.success(card_info.to_dict(), "获取校园卡信息成功")
        
    except Exception as e:
        return APIResponse.error(f"获取校园卡信息失败: {str(e)}")


@router.get("/transactions", summary="获取交易记录")
async def get_transactions(
    page: int = Query(1, description="页码"),
    size: int = Query(20, description="每页数量"),
    transaction_type: Optional[str] = Query(None, description="交易类型"),
    date_from: Optional[str] = Query(None, description="开始日期"),
    date_to: Optional[str] = Query(None, description="结束日期"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取交易记录"""
    try:
        # 构建过滤条件
        filters = {}
        if transaction_type:
            filters["transaction_type"] = transaction_type
        if date_from:
            filters["date_from"] = date_from
        if date_to:
            filters["date_to"] = date_to
        
        transactions = await campus_card_repo.find_transactions_paginated(
            person_id=current_user["person_id"],
            filters=filters,
            page=page,
            size=size
        )
        
        return APIResponse.paginated(transactions, page, size, "获取交易记录成功")
        
    except Exception as e:
        return APIResponse.error(f"获取交易记录失败: {str(e)}")


@router.get("/balance", summary="获取余额信息")
async def get_card_balance(current_user: Dict[str, Any] = Depends(get_current_user)):
    """获取校园卡余额信息"""
    try:
        balance_info = await campus_card_repo.get_balance_info(current_user["person_id"])
        
        return APIResponse.success(balance_info, "获取余额信息成功")
        
    except Exception as e:
        return APIResponse.error(f"获取余额信息失败: {str(e)}")


@router.get("/statistics", summary="获取消费统计")
async def get_consumption_statistics(
    period: str = Query("month", description="统计周期：day/week/month/year"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取消费统计"""
    try:
        # 🚧 [未实现] 复杂的统计分析功能
        # TODO: 实现按时间周期的详细消费统计
        
        statistics = await campus_card_repo.get_consumption_statistics(
            person_id=current_user["person_id"],
            period=period
        )
        
        return APIResponse.success(statistics, f"获取{period}消费统计成功")
        
    except Exception as e:
        return APIResponse.error(f"获取消费统计失败: {str(e)}")


@router.get("/recent", summary="获取最近交易")
async def get_recent_transactions(
    limit: int = Query(10, description="记录数量"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取最近交易记录"""
    try:
        recent_transactions = await campus_card_repo.find_recent_transactions(
            person_id=current_user["person_id"],
            limit=limit
        )
        
        return APIResponse.list_response(recent_transactions, "获取最近交易成功")
        
    except Exception as e:
        return APIResponse.error(f"获取最近交易失败: {str(e)}")