from src.config import settings

# 外部认证配置
EXTERNAL_AUTH_CONFIG = {
    "auth_url": settings.EXTERNAL_AUTH_URL,
    "token_url": f"{settings.EXTERNAL_AUTH_URL}/oauth/token",
    "userinfo_url": f"{settings.EXTERNAL_AUTH_URL}/oauth/userinfo",
    "client_id": settings.EXTERNAL_CLIENT_ID,
    "client_secret": settings.EXTERNAL_CLIENT_SECRET,
    "redirect_uri": settings.EXTERNAL_REDIRECT_URI,
    "scope": settings.EXTERNAL_SCOPE,
}

# 会话配置
SESSION_CONFIG = {
    "cookie_name": settings.SESSION_COOKIE_NAME,
    "expire_seconds": settings.SESSION_EXPIRE_SECONDS,
}