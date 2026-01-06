from fastapi import Depends, Request, HTTPException, status
from typing import Optional
import time

from src.redis_client import redis_client
from src.auth import schemas
from src.auth.service import auth_service
from src.auth.exceptions import InvalidSessionException, UnauthorizedException
from src.auth.config import SESSION_CONFIG
from src.auth.utils import parse_cookie_header


async def get_session_id(request: Request) -> Optional[str]:
    """从请求中获取会话ID"""
    # 优先从Cookie中获取
    cookie_header = request.headers.get("cookie")
    if cookie_header:
        cookies = parse_cookie_header(cookie_header)
        session_id = cookies.get(SESSION_CONFIG["cookie_name"])
        if session_id:
            return session_id

    # 其次从Authorization头中获取
    auth_header = request.headers.get("authorization")
    if auth_header:
        try:
            scheme, token = auth_header.split()
            if scheme.lower() == "bearer":
                return token
        except ValueError:
            pass

    return None


async def get_current_user(
        request: Request,
        session_id: Optional[str] = Depends(get_session_id),
) -> schemas.UserResponse:
    """获取当前用户依赖"""
    if not session_id:
        raise UnauthorizedException()

    # 验证会话
    if not await auth_service.validate_session(session_id):
        raise InvalidSessionException()

    # 获取会话数据
    session_data = await auth_service.get_session(session_id)
    if not session_data:
        raise InvalidSessionException()

    # 更新请求状态（可选）
    request.state.user = session_data["user_data"]
    request.state.session_id = session_id

    # 转换为响应模型
    user_data = session_data["user_data"]
    return schemas.UserResponse(**user_data)


async def get_current_user_optional(
        request: Request,
        session_id: Optional[str] = Depends(get_session_id),
) -> Optional[schemas.UserResponse]:
    """获取当前用户（可选）"""
    if not session_id:
        return None

    try:
        return await get_current_user(request, session_id)
    except (UnauthorizedException, InvalidSessionException):
        return None


def require_roles(*required_roles: str):
    """角色权限检查装饰器"""

    def role_checker(current_user: schemas.UserResponse = Depends(get_current_user)):
        user_roles = current_user.metadata.get("roles", [])

        # 检查是否有任意一个所需角色
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker