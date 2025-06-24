"""
用户管理相关API接口
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.msg import Msg
from app.api.deps import get_current_user, CurrentUser

router = APIRouter()

@router.get("/me", summary="获取当前用户信息")
def read_user_me(
    current_user: CurrentUser,
) -> Any:
    """
    获取当前用户信息
    """
    return current_user

@router.get("/profile", summary="获取用户资料")
def get_user_profile(
    current_user: CurrentUser,
) -> Any:
    """
    获取用户详细资料
    """
    # 返回简化的用户资料信息
    return {
        "person_id": current_user["person_id"],
        "name": current_user["name"],
        "person_type": current_user["person_type"],
        "email": current_user.get("email"),
        "phone": current_user.get("phone"),
        "college_name": current_user.get("college_name"),
        "major_name": current_user.get("major_name"),
        "class_name": current_user.get("class_name")
    }

@router.get("", summary="用户管理功能")
def user_management_placeholder() -> Msg:
    """
    用户管理功能占位符
    后续可扩展为完整的用户管理功能
    """
    return Msg(msg="用户管理功能开发中...") 