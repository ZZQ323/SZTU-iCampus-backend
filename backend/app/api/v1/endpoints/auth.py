"""
认证相关API
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
import time
from datetime import datetime, timedelta

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.response import APIResponse
from app.schemas.token import Token, LoginResponse, UserInfo, LoginResponseData
from app.schemas.auth import WeChatBindRequest, LoginRequest

# 🔄 使用HTTP客户端进行真正的HTTP请求，不导入Python模块
from app.core.http_client import http_client

router = APIRouter()
security = HTTPBearer()


@router.post("/login", summary="用户登录")
async def login(login_request: LoginRequest):
    """用户登录 - 通过HTTP请求调用data-service认证"""
    try:
        login_id = login_request.login_id.strip()
        password = login_request.password.strip()

        if not login_id or not password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="登录ID和密码不能为空"
            )

        # 🔄 HTTP请求data-service进行认证
        user_info = await http_client.authenticate_user(login_id, password)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        # 生成JWT token
        token = create_access_token(
            data={"sub": user_info["person_id"], "person_type": user_info.get("person_type", "student")}
        )

        # 构建响应数据
        response_data = LoginResponseData(
            access_token=token,
            token_type="bearer",
            expires_in=86400,  # 24小时
            user_info=UserInfo(
                person_id=user_info["person_id"],
                name=user_info["name"],
                person_type=user_info.get("person_type", "student"),
                student_id=user_info.get("student_id"),
                employee_id=user_info.get("employee_id"),
                college_name=user_info.get("college_name"),
                major_name=user_info.get("major_name"),
                class_name=user_info.get("class_name"),
                department_name=user_info.get("department_name"),
                phone=user_info.get("phone"),
                email=user_info.get("email"),
                academic_status=user_info.get("academic_status", "active"),
                employment_status=user_info.get("employment_status", "active")
            )
        )

        return APIResponse.success(response_data, "登录成功")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录处理失败: {str(e)}"
        )


@router.post("/logout", summary="用户登出")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """用户登出"""
    # JWT是无状态的，客户端删除token即可
    return APIResponse.success("登出成功")


@router.post("/wechat/bind", summary="绑定微信")
async def bind_wechat(
    request: WeChatBindRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """绑定微信账号"""
    try:
        # 🔄 HTTP请求data-service更新微信绑定
        result = await http_client._request(
            "POST",
            "/update/persons",
            json_data={
                "filters": {"person_id": current_user["person_id"]},
                "updates": {
                    "wechat_openid": request.openid,
                    "wechat_unionid": request.unionid,
                    "wechat_session_key": request.session_key,
                    "updated_at": datetime.now().isoformat()
                }
            }
        )
        
        if result.get("status") == "success":
            return APIResponse.success("微信绑定成功")
        else:
            raise HTTPException(status_code=500, detail="绑定失败")
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"微信绑定失败: {str(e)}"
        )


@router.delete("/wechat/unbind", summary="解绑微信")
async def unbind_wechat(current_user: Dict[str, Any] = Depends(get_current_user)):
    """解绑微信账号"""
    try:
        # 🔄 HTTP请求data-service清除微信绑定
        result = await http_client._request(
            "POST",
            "/update/persons",
            json_data={
                "filters": {"person_id": current_user["person_id"]},
                "updates": {
                    "wechat_openid": None,
                    "wechat_unionid": None,
                    "wechat_session_key": None,
                    "updated_at": datetime.now().isoformat()
                }
            }
        )
        
        if result.get("status") == "success":
            return APIResponse.success("微信解绑成功")
        else:
            raise HTTPException(status_code=500, detail="解绑失败")
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"微信解绑失败: {str(e)}"
        )


@router.get("/wechat/status", summary="查询微信绑定状态")
async def get_wechat_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """查询微信绑定状态"""
    try:
        # 🔄 HTTP请求data-service获取用户信息
        user_info = await http_client.get_person_by_id(current_user["person_id"])
        
        if not user_info:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        wechat_bound = bool(user_info.get("wechat_openid"))
        
        return APIResponse.success("查询成功", {
            "wechat_bound": wechat_bound,
            "openid": user_info.get("wechat_openid") if wechat_bound else None
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询绑定状态失败: {str(e)}"
        ) 