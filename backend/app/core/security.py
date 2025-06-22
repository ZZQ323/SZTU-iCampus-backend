"""
安全相关功能：JWT token生成验证、密码加密验证等
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union, Tuple
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import HTTPException, status

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "sztu-icamp-secret-key-2024-very-secure")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityManager:
    """安全管理器"""
    
    @staticmethod
    def verify_password(plain_password: str, password_hash: str, salt: str) -> bool:
        """验证密码"""
        # 使用与数据库生成相同的哈希方法
        computed_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return computed_hash == password_hash
    
    @staticmethod
    def hash_password(password: str) -> Tuple[str, str]:
        """生成密码哈希和盐值"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """验证JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token无效",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def extract_user_from_token(token: str) -> Dict[str, Any]:
        """从token中提取用户信息"""
        payload = SecurityManager.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法验证用户身份"
            )
        return payload
    
    @staticmethod
    def check_permission(user: Dict[str, Any], required_permission: str, resource_type: str = "general") -> bool:
        """检查用户权限"""
        user_permissions = user.get("permissions", {})
        
        # 管理员拥有所有权限
        if user.get("person_type") == "admin":
            return True
        
        # 检查读权限
        if required_permission == "read":
            read_permissions = user_permissions.get("read", [])
            return "*" in read_permissions or resource_type in read_permissions
        
        # 检查写权限
        elif required_permission == "write":
            write_permissions = user_permissions.get("write", [])
            return "*" in write_permissions or resource_type in write_permissions
        
        # 检查分享权限
        elif required_permission == "share":
            share_permissions = user_permissions.get("share", [])
            return "*" in share_permissions or resource_type in share_permissions
        
        return False
    
    @staticmethod
    def generate_wechat_state() -> str:
        """生成微信OAuth state参数"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_login_attempts(login_attempts: int, account_locked: bool) -> bool:
        """验证登录尝试次数"""
        if account_locked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="账户已被锁定，请联系管理员"
            )
        
        if login_attempts >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="登录尝试次数过多，请稍后再试"
            )
        
        return True

# 创建全局安全管理器实例
security = SecurityManager()

# 兼容性函数，为旧代码提供支持
def get_password_hash(password: str) -> str:
    """兼容性函数：生成密码哈希"""
    password_hash, salt = security.hash_password(password)
    # 返回组合的哈希值用于兼容
    return f"{password_hash}:{salt}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """兼容性函数：验证密码"""
    try:
        if ":" in hashed_password:
            # 新格式：hash:salt
            password_hash, salt = hashed_password.split(":", 1)
            return security.verify_password(plain_password, password_hash, salt)
        else:
            # 旧格式或其他格式，返回False
            return False
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """兼容性函数：创建访问令牌"""
    return security.create_access_token(data, expires_delta)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """兼容性函数：验证令牌"""
    return security.verify_token(token) 