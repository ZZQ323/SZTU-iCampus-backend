from fastapi import APIRouter, Depends, Request, Response, status, Query
from fastapi.responses import RedirectResponse
from typing import Optional

from src.auth import schemas, service
from src.auth.dependencies import get_current_user, get_current_user_optional
from src.auth.service import auth_service
from src.auth.config import SESSION_CONFIG
from src.auth.exceptions import ExternalAuthException

router = APIRouter()


@router.get("/login")
async def login(
        return_url: Optional[str] = Query("/", description="登录后重定向的URL")
):
    """
    初始化外部登录流程
    """
    auth_data = await auth_service.initiate_external_auth(return_url)
    return RedirectResponse(url=auth_data["auth_url"], status_code=status.HTTP_302_FOUND)


@router.get("/callback")
async def callback(
        request: Request,
        response: Response,
        code: str = Query(...),
        state: str = Query(...),
):
    """
    处理外部认证回调
    """
    try:
        # 处理回调，获取访问令牌
        token_data = await auth_service.handle_external_callback(code, state)

        # 使用访问令牌获取用户信息（简化版，实际应从token_data获取）
        user_data = {
            "sub": "user_id_from_token",
            "email": "user@example.com",
            "name": "User Name",
            "preferred_username": "username",
        }

        # 创建会话
        session_id = await auth_service.create_session(
            user_data=user_data,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        # 设置Cookie
        response.set_cookie(
            key=SESSION_CONFIG["cookie_name"],
            value=session_id,
            max_age=SESSION_CONFIG["expire_seconds"],
            httponly=True,
            secure=not request.app.debug,  # 生产环境启用HTTPS
            samesite="lax",
        )

        # 重定向到原始页面或首页
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    except ExternalAuthException as e:
        # 认证失败，重定向到错误页面或登录页
        return RedirectResponse(
            url=f"/login?error={str(e)}",
            status_code=status.HTTP_302_FOUND
        )


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
        current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    获取当前登录用户信息
    """
    return current_user


@router.post("/logout")
async def logout(
        request: Request,
        response: Response,
        current_user: schemas.UserResponse = Depends(get_current_user_optional)
):
    """
    用户登出
    """
    session_id = await request.state.session_id if hasattr(request.state, 'session_id') else None

    if session_id:
        # 删除会话
        await auth_service.delete_session(session_id)

        # 清除Cookie
        response.delete_cookie(
            key=SESSION_CONFIG["cookie_name"],
            httponly=True,
            samesite="lax",
        )

    return {"message": "Successfully logged out"}


@router.post("/refresh")
async def refresh_session(
        request: Request,
        response: Response,
        current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    刷新会话
    """
    old_session_id = await request.state.session_id if hasattr(request.state, 'session_id') else None

    if old_session_id:
        # 刷新会话
        new_session_id = await auth_service.refresh_session(old_session_id)

        if new_session_id:
            # 更新Cookie
            response.set_cookie(
                key=SESSION_CONFIG["cookie_name"],
                value=new_session_id,
                max_age=SESSION_CONFIG["expire_seconds"],
                httponly=True,
                secure=not request.app.debug,
                samesite="lax",
            )

            return {"message": "Session refreshed"}

    return {"message": "Session refresh failed"}


@router.get("/sessions")
async def list_sessions(
        current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    获取用户的所有活跃会话（简化版）
    """
    # 实际实现需要从Redis查询用户的所有会话
    return {"sessions": []}


@router.delete("/sessions/{session_id}")
async def revoke_session(
        session_id: str,
        current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    撤销特定会话
    """
    success = await auth_service.delete_session(session_id)
    return {"success": success}


@router.get("/status")
async def auth_status(
        current_user: Optional[schemas.UserResponse] = Depends(get_current_user_optional)
):
    """
    检查认证状态
    """
    return {
        "authenticated": current_user is not None,
        "user": current_user.dict() if current_user else None,
    }