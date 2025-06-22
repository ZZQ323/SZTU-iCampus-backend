"""
认证相关的数据模型
"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

class LoginRequest(BaseModel):
    """登录请求"""
    login_id: str = Field(..., description="登录ID（学号或工号）", min_length=4, max_length=20)
    password: str = Field(..., description="密码", min_length=6, max_length=50)
    remember_me: bool = Field(False, description="记住我")
    
    @validator('login_id')
    def validate_login_id(cls, v):
        if not v.strip():
            raise ValueError('登录ID不能为空')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if not v.strip():
            raise ValueError('密码不能为空')
        return v.strip()

class UserInfo(BaseModel):
    """用户信息"""
    person_id: str = Field(..., description="人员ID")
    person_type: str = Field(..., description="人员类型")
    name: str = Field(..., description="姓名")
    login_id: str = Field(..., description="登录ID")
    student_id: Optional[str] = Field(None, description="学号")
    employee_id: Optional[str] = Field(None, description="工号")
    college_id: Optional[str] = Field(None, description="学院ID")
    college_name: Optional[str] = Field(None, description="学院名称")
    major_id: Optional[str] = Field(None, description="专业ID")
    major_name: Optional[str] = Field(None, description="专业名称")
    class_id: Optional[str] = Field(None, description="班级ID")
    class_name: Optional[str] = Field(None, description="班级名称")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="电话")
    wechat_bound: bool = Field(False, description="是否绑定微信")
    permissions: Dict[str, List[str]] = Field(default_factory=dict, description="权限列表")
    last_login: Optional[datetime] = Field(None, description="最近登录时间")

class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="令牌有效期（秒）")
    user: UserInfo = Field(..., description="用户信息")

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="原密码", min_length=6, max_length=50)
    new_password: str = Field(..., description="新密码", min_length=6, max_length=50)
    confirm_password: str = Field(..., description="确认密码", min_length=6, max_length=50)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不匹配')
        return v

class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    login_id: str = Field(..., description="登录ID", min_length=4, max_length=20)
    id_card_last4: str = Field(..., description="身份证后4位", min_length=4, max_length=4)
    new_password: str = Field(..., description="新密码", min_length=6, max_length=50)
    confirm_password: str = Field(..., description="确认密码", min_length=6, max_length=50)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不匹配')
        return v

class TokenValidateResponse(BaseModel):
    """Token验证响应"""
    valid: bool = Field(..., description="是否有效")
    user: Optional[UserInfo] = Field(None, description="用户信息")
    expires_at: Optional[datetime] = Field(None, description="过期时间")

class UpdateProfileRequest(BaseModel):
    """更新资料请求"""
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="电话")
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('电话号码只能包含数字')
        return v

# 微信相关Schema
class WechatLoginRequest(BaseModel):
    """微信登录请求"""
    code: str = Field(..., description="微信授权码")
    user_info: Optional[Dict[str, Any]] = Field(None, description="微信用户信息")

class WechatBindCheckRequest(BaseModel):
    """微信绑定状态检查请求"""
    code: str = Field(..., description="微信授权码")

class WechatBindCheckResponse(BaseModel):
    """微信绑定状态检查响应"""
    is_bound: bool = Field(..., description="是否已绑定")
    user_info: Optional[UserInfo] = Field(None, description="用户信息（如果已绑定）")
    openid: Optional[str] = Field(None, description="微信OpenID")

class WechatBindRequest(BaseModel):
    """微信绑定请求"""
    code: str = Field(..., description="微信授权码")
    login_id: str = Field(..., description="校园账号ID")
    password: str = Field(..., description="校园账号密码")
    user_info: Optional[Dict[str, Any]] = Field(None, description="微信用户信息")

class WechatUnbindRequest(BaseModel):
    """微信解绑请求"""
    password: str = Field(..., description="确认密码")

class WechatLoginResponse(BaseModel):
    """微信登录响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="令牌过期时间（秒）")
    user: UserInfo = Field(..., description="用户信息")
    is_new_bind: bool = Field(default=False, description="是否为新绑定")

class WechatUserInfo(BaseModel):
    """微信用户信息"""
    openid: str = Field(..., description="微信OpenID")
    nickname: Optional[str] = Field(None, description="微信昵称")
    avatar_url: Optional[str] = Field(None, description="微信头像URL")
    gender: Optional[int] = Field(None, description="性别：1-男，2-女，0-未知")
    city: Optional[str] = Field(None, description="城市")
    province: Optional[str] = Field(None, description="省份")
    country: Optional[str] = Field(None, description="国家") 