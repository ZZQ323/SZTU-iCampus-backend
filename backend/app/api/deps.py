"""
依赖注入模块
用于用户认证、数据库会话等依赖
"""
from typing import Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from ..core.config import settings

# OAuth2 配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    获取当前用户信息
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        # 这里应该从数据库查询用户信息
        # 为了演示，返回模拟用户信息
        user_info = {
            "id": 1,
            "username": username,
            "email": f"{username}@sztu.edu.cn",
            "role": "student",  # 可以是 student, teacher, admin
            "is_active": True
        }
        
        return user_info
        
    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    获取当前活跃用户
    """
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_admin_user(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    获取管理员用户（权限检查）
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def create_access_token(data: dict) -> str:
    """
    创建JWT访问令牌
    """
    from datetime import datetime, timedelta
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# 可选的数据库会话依赖（如果需要本地数据库）
def get_db():
    """
    获取数据库会话（占位符）
    胶水层主要使用数据服务，这里保留接口以备不时之需
    """
    # 如果需要本地SQLite数据库，可以在这里实现
    pass 