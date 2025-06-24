from typing import Optional, Dict, Any
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None 

class UserInfo(BaseModel):
    person_id: str
    name: str
    person_type: str
    student_id: Optional[str] = None
    employee_id: Optional[str] = None
    college_name: Optional[str] = None
    major_name: Optional[str] = None
    class_name: Optional[str] = None
    department_name: Optional[str] = None

class LoginResponseData(BaseModel):
    access_token: str
    token_type: str
    user_info: UserInfo

class LoginResponse(BaseModel):
    code: int
    message: str
    data: LoginResponseData
    timestamp: str  # 修复：使用ISO 8601格式字符串，符合API文档标准
    version: str 