import secrets
import hashlib
import base64
import time
from typing import Tuple
import urllib.parse


def generate_state() -> str:
    """生成随机的state参数，用于防止CSRF攻击"""
    return secrets.token_urlsafe(32)


def generate_code_verifier() -> str:
    """生成PKCE code_verifier"""
    return secrets.token_urlsafe(64)


def generate_code_challenge(code_verifier: str) -> str:
    """生成PKCE code_challenge"""
    # SHA256哈希
    sha256_hash = hashlib.sha256(code_verifier.encode()).digest()
    # Base64 URL安全编码
    code_challenge = base64.urlsafe_b64encode(sha256_hash).decode().rstrip("=")
    return code_challenge


def build_auth_url(
        auth_url: str,
        client_id: str,
        redirect_uri: str,
        scope: str,
        state: str,
        code_challenge: str,
        code_challenge_method: str = "S256"
) -> str:
    """构建外部认证URL"""
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
    }

    query_string = urllib.parse.urlencode(params)
    return f"{auth_url}?{query_string}"


def generate_session_id() -> str:
    """生成会话ID"""
    return secrets.token_urlsafe(32)


def parse_cookie_header(cookie_header: str) -> dict:
    """解析Cookie头"""
    cookies = {}
    if cookie_header:
        for cookie in cookie_header.split(";"):
            if "=" in cookie:
                key, value = cookie.strip().split("=", 1)
                cookies[key] = value
    return cookies