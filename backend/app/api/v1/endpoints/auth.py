from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
import requests

from app import crud, models
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token, verify_token
from app.utils import (
    generate_password_reset_token,
    verify_password_reset_token,
)
from app.schemas.token import Token
from app.schemas.user import UserCreate, User
from app.schemas.msg import Msg
from app.models.user import User as UserModel
from app.database import get_db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        db, student_id=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect student ID or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/login/test-token", response_model=User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user

@router.post("/password-recovery/{email}", response_model=Msg)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    user = crud.user.get_by_email(db, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    # TODO: 发送重置密码邮件
    return {"msg": "Password recovery email sent"}

@router.post("/reset-password/", response_model=Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}

@router.post("/test-login", response_model=Token)
async def test_login(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    测试用登录接口
    """
    student_id = data.get("student_id")
    name = data.get("name")
    
    if not student_id or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="student_id and name are required"
        )
    
    # 查找或创建测试用户
    user = db.query(UserModel).filter(UserModel.student_id == student_id).first()
    if not user:
        user = UserModel(
            openid=f"test_{student_id}",
            student_id=student_id,
            name=name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.openid},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/wx-login", response_model=Token)
async def wx_login(code: str, db: Session = Depends(get_db)):
    """
    微信小程序登录
    """
    # 获取微信openid
    url = f"https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WECHAT_APP_ID,
        "secret": settings.WECHAT_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    response = requests.get(url, params=params)
    result = response.json()
    
    if "errcode" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid code"
        )
    
    openid = result["openid"]
    
    # 查找或创建用户
    user = db.query(UserModel).filter(UserModel.openid == openid).first()
    if not user:
        # 这里应该调用微信用户信息接口获取用户信息
        # 为了演示，我们创建一个临时用户
        user = UserModel(
            openid=openid,
            student_id="temp_" + openid[:8],
            name="临时用户"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.openid},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    获取当前用户信息
    """
    payload = verify_token(token)
    openid = payload.get("sub")
    if openid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(UserModel).filter(UserModel.openid == openid).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user 