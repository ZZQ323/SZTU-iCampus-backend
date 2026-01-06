import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import uuid

from src.redis_client import redis_client
from src.auth import schemas, utils
from src.auth.config import EXTERNAL_AUTH_CONFIG
from src.auth.exceptions import ExternalAuthException
from src.config import settings


class AuthService:
    """认证服务"""

    @staticmethod
    async def initiate_external_auth(return_url: str = "/") -> Dict[str, str]:
        """初始化外部认证"""
        # 生成PKCE参数
        state = utils.generate_state()
        code_verifier = utils.generate_code_verifier()
        code_challenge = utils.generate_code_challenge(code_verifier)

        # 存储state和code_verifier到Redis（短期存储，5分钟）
        auth_data = {
            "state": state,
            "code_verifier": code_verifier,
            "return_url": return_url,
            "created_at": datetime.utcnow().isoformat(),
        }
        await redis_client.set(f"auth:{state}", auth_data, expire=300)

        # 构建认证URL
        auth_url = utils.build_auth_url(
            auth_url=EXTERNAL_AUTH_CONFIG["auth_url"],
            client_id=EXTERNAL_AUTH_CONFIG["client_id"],
            redirect_uri=EXTERNAL_AUTH_CONFIG["redirect_uri"],
            scope=EXTERNAL_AUTH_CONFIG["scope"],
            state=state,
            code_challenge=code_challenge,
        )

        return {
            "auth_url": auth_url,
            "state": state,
        }

    @staticmethod
    async def handle_external_callback(code: str, state: str) -> schemas.Token:
        """处理外部认证回调"""
        # 从Redis获取state对应的数据
        auth_data = await redis_client.get(f"auth:{state}")
        if not auth_data:
            raise ExternalAuthException("Invalid state parameter")

        code_verifier = auth_data.get("code_verifier")

        # 向外部认证服务请求访问令牌
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                EXTERNAL_AUTH_CONFIG["token_url"],
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": EXTERNAL_AUTH_CONFIG["redirect_uri"],
                    "client_id": EXTERNAL_AUTH_CONFIG["client_id"],
                    "client_secret": EXTERNAL_AUTH_CONFIG["client_secret"],
                    "code_verifier": code_verifier,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if token_response.status_code != 200:
                raise ExternalAuthException(
                    f"Token request failed: {token_response.text}"
                )

            token_data = token_response.json()

            # 获取用户信息
            user_response = await client.get(
                EXTERNAL_AUTH_CONFIG["userinfo_url"],
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )

            if user_response.status_code != 200:
                raise ExternalAuthException(
                    f"User info request failed: {user_response.text}"
                )

            user_data = user_response.json()

        # 从Redis删除临时的auth数据
        await redis_client.delete(f"auth:{state}")

        return token_data

    @staticmethod
    async def create_session(
            user_data: Dict[str, Any],
            ip_address: Optional[str] = None,
            user_agent: Optional[str] = None
    ) -> str:
        """创建用户会话"""
        # 生成会话ID
        session_id = utils.generate_session_id()

        # 创建用户记录或更新现有用户
        user_id = user_data.get("sub") or str(uuid.uuid4())

        # 存储用户数据到Redis
        user_info = {
            "id": user_id,
            "username": user_data.get("preferred_username", user_data.get("email")),
            "email": user_data.get("email"),
            "full_name": user_data.get("name"),
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": user_data,
        }

        await redis_client.set(f"user:{user_id}", user_info)

        # 创建会话数据
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(seconds=settings.SESSION_EXPIRE_SECONDS)

        session_data = {
            "user_id": user_id,
            "user_data": user_info,
            "created_at": created_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        # 存储会话到Redis
        await redis_client.set_session(session_id, session_data)

        return session_id

    @staticmethod
    async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话数据"""
        return await redis_client.get_session(session_id)

    @staticmethod
    async def delete_session(session_id: str) -> bool:
        """删除会话"""
        return await redis_client.delete_session(session_id)

    @staticmethod
    async def refresh_session(session_id: str) -> Optional[str]:
        """刷新会话"""
        session_data = await redis_client.get_session(session_id)
        if not session_data:
            return None

        # 创建新会话
        new_session_id = utils.generate_session_id()

        # 更新过期时间
        session_data["created_at"] = datetime.utcnow().isoformat()
        session_data["expires_at"] = (
                datetime.utcnow() + timedelta(seconds=settings.SESSION_EXPIRE_SECONDS)
        ).isoformat()

        # 存储新会话
        await redis_client.set_session(new_session_id, session_data)

        # 删除旧会话
        await redis_client.delete_session(session_id)

        return new_session_id

    @staticmethod
    async def validate_session(session_id: str) -> bool:
        """验证会话是否有效"""
        session_data = await redis_client.get_session(session_id)
        if not session_data:
            return False

        # 检查会话是否过期
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        if expires_at < datetime.utcnow():
            await redis_client.delete_session(session_id)
            return False

        return True


auth_service = AuthService()