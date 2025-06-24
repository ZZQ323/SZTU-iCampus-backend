"""
API依赖注入：认证、数据库连接等
"""

from typing import Optional, Dict, Any
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import security
from app.core.config import settings

# 🔄 使用HTTP客户端进行真正的HTTP请求，不导入Python模块
from app.core.http_client import http_client

# HTTP Bearer认证
security_scheme = HTTPBearer()
# 创建可选的HTTP Bearer认证（不自动抛出错误）
optional_security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> Dict[str, Any]:
    """获取当前认证用户 - 通过HTTP请求data-service"""
    
    # 验证token
    payload = security.verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token中缺少用户信息"
        )
    
    # 🔄 通过HTTP请求获取用户信息
    try:
        user_data = await http_client.get_person_by_id(user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )
        
        # 检查账户状态
        if user_data.get("account_locked"):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="账户已被锁定"
            )
        
        # 构建用户信息
        user = {
            "person_id": user_data.get("person_id"),
            "person_type": user_data.get("person_type"),
            "name": user_data.get("name"),
            "student_id": user_data.get("student_id"),
            "employee_id": user_data.get("employee_id"),
            "login_id": user_data.get("student_id") or user_data.get("employee_id"),
            "college_id": user_data.get("college_id"),
            "major_id": user_data.get("major_id"),
            "class_id": user_data.get("class_id"),
            "email": user_data.get("email"),
            "phone": user_data.get("phone"),
            "academic_status": user_data.get("academic_status"),
            "employment_status": user_data.get("employment_status"),
            "wechat_bound": bool(user_data.get("wechat_openid")),
            "permissions": get_user_permissions(user_data.get("person_type"))
        }
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 获取用户信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        )

def get_user_permissions(person_type: str) -> Dict[str, list]:
    """根据用户类型获取权限"""
    permission_matrix = {
        "student": {
            "read": ["own_data", "own_schedule", "own_grades", "own_borrow_records", 
                    "public_announcements", "course_info", "library_info"],
            "write": ["own_profile", "course_evaluation", "library_reservation"],
            "share": ["schedule", "contact_info"]
        },
        "teacher": {
            "read": ["own_data", "own_courses", "student_grades", "course_schedules", 
                    "teaching_announcements", "department_info"],
            "write": ["student_grades", "course_content", "announcements", "own_profile"],
            "share": ["course_materials", "grades", "schedule"]
        },
        "assistant_teacher": {
            "read": ["own_data", "assigned_courses", "student_info", "course_schedules"],
            "write": ["course_assistance", "student_support", "own_profile"],
            "share": ["course_materials", "schedule"]
        },
        "admin": {
            "read": ["*"],  # 所有读权限
            "write": ["*"], # 所有写权限
            "share": ["*"]  # 所有分享权限
        }
    }
    
    return permission_matrix.get(person_type, {
        "read": ["own_data"],
        "write": ["own_profile"],
        "share": []
    })

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security_scheme)
) -> Optional[Dict[str, Any]]:
    """获取可选的当前用户（真正可选，不会抛出认证错误）"""
    if not credentials:
        return None
    
    try:
        # 验证token
        payload = security.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            return None
        
        # 通过HTTP请求获取用户信息
        user_data = await http_client.get_person_by_id(user_id)
        if not user_data:
            return None
        
        # 构建用户信息
        user = {
            "person_id": user_data.get("person_id"),
            "person_type": user_data.get("person_type"),
            "name": user_data.get("name"),
            "student_id": user_data.get("student_id"),
            "employee_id": user_data.get("employee_id"),
            "login_id": user_data.get("student_id") or user_data.get("employee_id"),
            "college_id": user_data.get("college_id"),
            "major_id": user_data.get("major_id"),
            "class_id": user_data.get("class_id"),
            "email": user_data.get("email"),
            "phone": user_data.get("phone"),
            "academic_status": user_data.get("academic_status"),
            "employment_status": user_data.get("employment_status"),
            "wechat_bound": bool(user_data.get("wechat_openid")),
            "permissions": get_user_permissions(user_data.get("person_type"))
        }
        
        return user
        
    except Exception as e:
        # 任何错误都返回None，不抛出异常
        print(f"[WARNING] 可选用户认证失败: {e}")
        return None

def require_permission(permission: str, resource_type: str = "general"):
    """权限检查装饰器工厂"""
    async def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if not security.check_permission(current_user, permission, resource_type):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要{permission}权限"
            )
        return current_user
    return permission_checker

async def require_student(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """要求学生身份"""
    if current_user["person_type"] != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此功能仅限学生使用"
        )
    return current_user

async def require_teacher(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """要求教师身份"""
    if current_user["person_type"] not in ["teacher", "assistant_teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此功能仅限教师使用"
        )
    return current_user

async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """要求管理员身份"""
    if current_user["person_type"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此功能仅限管理员使用"
        )
    return current_user

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """获取当前活跃用户（兼容性函数）"""
    # 检查用户状态
    if current_user.get("academic_status") == "suspended" or current_user.get("employment_status") == "suspended":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被暂停"
        )
    return current_user

async def get_current_active_superuser(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """获取当前活跃超级用户（兼容性函数）"""
    if current_user["person_type"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：需要管理员权限"
        )
    return current_user

async def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """获取当前管理员用户（兼容性函数）"""
    if current_user["person_type"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：需要管理员权限"
        )
    return current_user

# 类型别名，方便使用
CurrentUser = Annotated[Dict[str, Any], Depends(get_current_user)]
OptionalUser = Annotated[Optional[Dict[str, Any]], Depends(get_optional_user)]
StudentUser = Annotated[Dict[str, Any], Depends(require_student)]
TeacherUser = Annotated[Dict[str, Any], Depends(require_teacher)]
AdminUser = Annotated[Dict[str, Any], Depends(require_admin)] 