"""
认证相关API接口
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.schemas.auth import (
    LoginRequest, LoginResponse, UserInfo, ChangePasswordRequest,
    ResetPasswordRequest, TokenValidateResponse, UpdateProfileRequest,
    WechatLoginRequest, WechatBindCheckRequest, WechatBindCheckResponse,
    WechatBindRequest, WechatUnbindRequest, WechatLoginResponse
)
from app.schemas.msg import Msg
from app.api.deps import get_db, get_current_user, CurrentUser, Database
from app.core.security import security
from app.core.config import settings
from app.core.wechat import wechat_service

router = APIRouter()

@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Database
):
    """
    用户登录接口
    支持学号/工号 + 密码登录
    """
    
    # 查找用户
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            person_id, person_type, name, student_id, employee_id,
            password_hash, password_salt, login_attempts, account_locked,
            college_id, major_id, class_id, email, phone, wechat_openid,
            last_login, academic_status, employment_status
        FROM persons 
        WHERE (student_id = ? OR employee_id = ?) 
        AND (student_id IS NOT NULL OR employee_id IS NOT NULL)
    """, (login_data.login_id, login_data.login_id))
    
    user_row = cursor.fetchone()
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查账户状态
    security.validate_login_attempts(user_row["login_attempts"], user_row["account_locked"])
    
    # 验证密码
    if not security.verify_password(
        login_data.password, 
        user_row["password_hash"], 
        user_row["password_salt"]
    ):
        # 增加失败尝试次数
        new_attempts = user_row["login_attempts"] + 1
        should_lock = new_attempts >= 5
        
        cursor.execute("""
            UPDATE persons 
            SET login_attempts = ?, account_locked = ? 
            WHERE person_id = ?
        """, (new_attempts, should_lock, user_row["person_id"]))
        db.commit()
        
        # 记录登录尝试
        log_login_attempt(db, login_data.login_id, False, request, "密码错误")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 登录成功，重置失败次数，更新最后登录时间
    cursor.execute("""
        UPDATE persons 
        SET login_attempts = 0, last_login = ?
        WHERE person_id = ?
    """, (datetime.utcnow().isoformat(), user_row["person_id"]))
    db.commit()
    
    # 记录成功登录
    log_login_attempt(db, login_data.login_id, True, request)
    
    # 获取扩展用户信息
    user_info = build_user_info(db, user_row)
    
    # 创建访问令牌
    token_data = {
        "sub": user_row["person_id"],
        "person_type": user_row["person_type"],
        "login_id": login_data.login_id
    }
    
    expires_delta = timedelta(days=7) if login_data.remember_me else timedelta(hours=24)
    access_token = security.create_access_token(token_data, expires_delta)
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(expires_delta.total_seconds()),
        user=user_info
    )

@router.post("/logout", response_model=Msg, summary="用户登出")
async def logout(current_user: CurrentUser):
    """
    用户登出接口
    """
    # 在实际应用中，可以将token加入黑名单
    # 这里简单返回成功消息
    return Msg(msg="登出成功")

@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: CurrentUser,
    db: Database
):
    """
    获取当前登录用户的详细信息
    """
    # 从数据库获取最新的用户信息
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            person_id, person_type, name, student_id, employee_id,
            college_id, major_id, class_id, email, phone, wechat_openid,
            last_login, academic_status, employment_status
        FROM persons 
        WHERE person_id = ?
    """, (current_user["person_id"],))
    
    user_row = cursor.fetchone()
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户信息不存在"
        )
    
    return build_user_info(db, user_row)

@router.post("/change-password", response_model=Msg, summary="修改密码")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: Database
):
    """
    修改密码接口
    """
    
    # 获取当前用户的密码信息
    cursor = db.cursor()
    cursor.execute("""
        SELECT password_hash, password_salt 
        FROM persons 
        WHERE person_id = ?
    """, (current_user["person_id"],))
    
    user_row = cursor.fetchone()
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 验证原密码
    if not security.verify_password(
        password_data.old_password,
        user_row["password_hash"],
        user_row["password_salt"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 生成新密码哈希
    new_hash, new_salt = security.hash_password(password_data.new_password)
    
    # 更新密码
    cursor.execute("""
        UPDATE persons 
        SET password_hash = ?, password_salt = ?, password_plain = ?
        WHERE person_id = ?
    """, (new_hash, new_salt, password_data.new_password, current_user["person_id"]))
    
    db.commit()
    
    return Msg(msg="密码修改成功")

@router.post("/reset-password", response_model=Msg, summary="重置密码")
async def reset_password(
    reset_data: ResetPasswordRequest,
    db: Database
):
    """
    重置密码接口（通过身份证后4位验证）
    """
    
    # 查找用户并验证身份证
    cursor = db.cursor()
    cursor.execute("""
        SELECT person_id, id_card 
        FROM persons 
        WHERE (student_id = ? OR employee_id = ?)
        AND (student_id IS NOT NULL OR employee_id IS NOT NULL)
    """, (reset_data.login_id, reset_data.login_id))
    
    user_row = cursor.fetchone()
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 验证身份证后4位
    if not user_row["id_card"] or not user_row["id_card"].endswith(reset_data.id_card_last4):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="身份证信息验证失败"
        )
    
    # 生成新密码哈希
    new_hash, new_salt = security.hash_password(reset_data.new_password)
    
    # 更新密码并解锁账户
    cursor.execute("""
        UPDATE persons 
        SET password_hash = ?, password_salt = ?, password_plain = ?,
            login_attempts = 0, account_locked = 0
        WHERE person_id = ?
    """, (new_hash, new_salt, reset_data.new_password, user_row["person_id"]))
    
    db.commit()
    
    return Msg(msg="密码重置成功")

@router.post("/validate-token", response_model=TokenValidateResponse, summary="验证Token")
async def validate_token(current_user: CurrentUser):
    """
    验证Token有效性
    """
    
    return TokenValidateResponse(
        valid=True,
        user=UserInfo(**current_user),
        expires_at=None  # 可以从token中提取过期时间
    )

@router.post("/update-profile", response_model=Msg, summary="更新用户资料")
async def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: CurrentUser,
    db: Database
):
    """
    更新用户资料
    """
    
    # 构建更新字段
    update_fields = []
    update_values = []
    
    if profile_data.email is not None:
        update_fields.append("email = ?")
        update_values.append(profile_data.email)
    
    if profile_data.phone is not None:
        update_fields.append("phone = ?")
        update_values.append(profile_data.phone)
    
    if not update_fields:
        return Msg(msg="没有需要更新的字段")
    
    # 更新数据库
    cursor = db.cursor()
    cursor.execute(f"""
        UPDATE persons 
        SET {', '.join(update_fields)}
        WHERE person_id = ?
    """, update_values + [current_user["person_id"]])
    
    db.commit()
    
    return Msg(msg="资料更新成功")

# ================== 微信相关API ==================

@router.post("/wechat/check-bind", response_model=WechatBindCheckResponse, summary="检查微信绑定状态")
async def check_wechat_bind(
    check_data: WechatBindCheckRequest,
    db: Database
):
    """
    检查微信号是否已绑定校园账号
    """
    
    # 获取微信用户信息
    wechat_info = await wechat_service.process_login_code(check_data.code)
    if not wechat_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="获取微信信息失败"
        )
    
    openid = wechat_info.get('openid')
    if not openid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="微信OpenID获取失败"
        )
    
    # 查询是否已绑定
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            person_id, person_type, name, student_id, employee_id,
            college_id, major_id, class_id, email, phone, wechat_openid,
            last_login, academic_status, employment_status
        FROM persons 
        WHERE wechat_openid = ?
    """, (openid,))
    
    user_row = cursor.fetchone()
    
    if user_row:
        # 已绑定，返回用户信息
        user_info = build_user_info(db, user_row)
        return WechatBindCheckResponse(
            is_bound=True,
            user_info=user_info,
            openid=openid
        )
    else:
        # 未绑定
        return WechatBindCheckResponse(
            is_bound=False,
            user_info=None,
            openid=openid
        )

@router.post("/wechat/bind", response_model=Msg, summary="绑定微信账号")
async def bind_wechat(
    bind_data: WechatBindRequest,
    db: Database
):
    """
    绑定微信账号到校园账户
    """
    
    # 获取微信用户信息
    wechat_info = await wechat_service.process_login_code(bind_data.code)
    if not wechat_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="获取微信信息失败"
        )
    
    openid = wechat_info.get('openid')
    if not openid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="微信OpenID获取失败"
        )
    
    # 验证校园账号
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            person_id, person_type, password_hash, password_salt, 
            login_attempts, account_locked, wechat_openid
        FROM persons 
        WHERE (student_id = ? OR employee_id = ?) 
        AND (student_id IS NOT NULL OR employee_id IS NOT NULL)
    """, (bind_data.login_id, bind_data.login_id))
    
    user_row = cursor.fetchone()
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="校园账号不存在"
        )
    
    # 检查账户状态
    security.validate_login_attempts(user_row["login_attempts"], user_row["account_locked"])
    
    # 验证密码
    if not security.verify_password(
        bind_data.password,
        user_row["password_hash"],
        user_row["password_salt"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="校园账号密码错误"
        )
    
    # 检查是否已绑定其他微信号
    if user_row["wechat_openid"] and user_row["wechat_openid"] != openid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该校园账号已绑定其他微信号"
        )
    
    # 检查该微信号是否已绑定其他账号
    cursor.execute("""
        SELECT person_id FROM persons WHERE wechat_openid = ? AND person_id != ?
    """, (openid, user_row["person_id"]))
    
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该微信号已绑定其他校园账号"
        )
    
    # 执行绑定
    cursor.execute("""
        UPDATE persons 
        SET wechat_openid = ?, login_attempts = 0, last_login = ?
        WHERE person_id = ?
    """, (openid, datetime.utcnow().isoformat(), user_row["person_id"]))
    
    db.commit()
    
    return Msg(msg="微信绑定成功")

@router.post("/wechat/login", response_model=WechatLoginResponse, summary="微信登录")
async def wechat_login(
    login_data: WechatLoginRequest,
    db: Database
):
    """
    微信登录接口
    """
    
    # 获取微信用户信息
    wechat_info = await wechat_service.process_login_code(login_data.code)
    if not wechat_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="获取微信信息失败"
        )
    
    openid = wechat_info.get('openid')
    if not openid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="微信OpenID获取失败"
        )
    
    # 查找绑定的用户
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            person_id, person_type, name, student_id, employee_id,
            college_id, major_id, class_id, email, phone, wechat_openid,
            last_login, academic_status, employment_status, account_locked
        FROM persons 
        WHERE wechat_openid = ?
    """, (openid,))
    
    user_row = cursor.fetchone()
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="微信号未绑定校园账号，请先绑定"
        )
    
    # 检查账户状态
    if user_row["account_locked"]:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="账户已被锁定"
        )
    
    # 更新最后登录时间
    cursor.execute("""
        UPDATE persons 
        SET last_login = ?
        WHERE person_id = ?
    """, (datetime.utcnow().isoformat(), user_row["person_id"]))
    
    db.commit()
    
    # 获取用户信息
    user_info = build_user_info(db, user_row)
    
    # 创建访问令牌
    token_data = {
        "sub": user_row["person_id"],
        "person_type": user_row["person_type"],
        "login_id": user_row["student_id"] or user_row["employee_id"]
    }
    
    expires_delta = timedelta(days=7)  # 微信登录默认7天有效
    access_token = security.create_access_token(token_data, expires_delta)
    
    return WechatLoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(expires_delta.total_seconds()),
        user=user_info,
        is_new_bind=False
    )

@router.post("/wechat/unbind", response_model=Msg, summary="解绑微信")
async def unbind_wechat(
    unbind_data: WechatUnbindRequest,
    current_user: CurrentUser,
    db: Database
):
    """
    解绑微信账号
    """
    
    # 验证密码
    cursor = db.cursor()
    cursor.execute("""
        SELECT password_hash, password_salt, wechat_openid
        FROM persons 
        WHERE person_id = ?
    """, (current_user["person_id"],))
    
    user_row = cursor.fetchone()
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if not user_row["wechat_openid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未绑定微信号"
        )
    
    # 验证密码
    if not security.verify_password(
        unbind_data.password,
        user_row["password_hash"],
        user_row["password_salt"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误"
        )
    
    # 解绑微信
    cursor.execute("""
        UPDATE persons 
        SET wechat_openid = NULL
        WHERE person_id = ?
    """, (current_user["person_id"],))
    
    db.commit()
    
    return Msg(msg="微信解绑成功")

def build_user_info(db: sqlite3.Connection, user_row: sqlite3.Row) -> UserInfo:
    """构建用户信息对象"""
    
    cursor = db.cursor()
    college_name = None
    major_name = None
    class_name = None
    
    # 获取学院名称
    if user_row["college_id"]:
        cursor.execute("SELECT college_name FROM colleges WHERE college_id = ?", (user_row["college_id"],))
        college_row = cursor.fetchone()
        if college_row:
            college_name = college_row["college_name"]
    
    # 获取专业名称
    if user_row["major_id"]:
        cursor.execute("SELECT major_name FROM majors WHERE major_id = ?", (user_row["major_id"],))
        major_row = cursor.fetchone()
        if major_row:
            major_name = major_row["major_name"]
    
    # 获取班级名称
    if user_row["class_id"]:
        cursor.execute("SELECT class_name FROM classes WHERE class_id = ?", (user_row["class_id"],))
        class_row = cursor.fetchone()
        if class_row:
            class_name = class_row["class_name"]
    
    # 获取权限
    from app.api.deps import get_user_permissions
    permissions = get_user_permissions(user_row["person_type"])
    
    return UserInfo(
        person_id=user_row["person_id"],
        person_type=user_row["person_type"],
        name=user_row["name"],
        login_id=user_row["student_id"] or user_row["employee_id"],
        student_id=user_row["student_id"],
        employee_id=user_row["employee_id"],
        college_id=user_row["college_id"],
        college_name=college_name,
        major_id=user_row["major_id"],
        major_name=major_name,
        class_id=user_row["class_id"],
        class_name=class_name,
        email=user_row["email"],
        phone=user_row["phone"],
        wechat_bound=bool(user_row["wechat_openid"]),
        permissions=permissions,
        last_login=datetime.fromisoformat(user_row["last_login"]) if user_row["last_login"] else None
    )

def log_login_attempt(
    db: sqlite3.Connection, 
    login_id: str, 
    success: bool, 
    request: Request,
    failure_reason: Optional[str] = None
):
    """记录登录尝试"""
    
    # 获取客户端IP和User-Agent
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # 这里可以记录到日志文件或数据库
    # 为了简化，暂时只记录到应用日志
    import logging
    
    status_text = "成功" if success else "失败"
    log_message = f"登录{status_text}: {login_id} | IP: {client_ip} | Agent: {user_agent}"
    
    if failure_reason:
        log_message += f" | 原因: {failure_reason}"
    
    if success:
        logging.info(log_message)
    else:
        logging.warning(log_message) 