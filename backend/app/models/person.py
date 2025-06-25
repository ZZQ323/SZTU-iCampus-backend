"""
人员相关数据模型
包含人员基础信息和不同类型人员的特定信息
"""
from datetime import date, datetime
from typing import Optional, Dict, Any
from pydantic import Field, validator
from .base import BaseModel


class Person(BaseModel):
    """人员基础模型"""
    
    # 主键标识
    person_id: str = Field(..., description="人员ID")
    person_type: str = Field(..., description="人员类型：student/teacher/admin")
    
    # 基本信息
    name: str = Field(..., description="姓名")
    name_en: Optional[str] = Field(None, description="英文姓名")
    gender: str = Field(..., description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    id_card: Optional[str] = Field(None, description="身份证号")
    nationality: Optional[str] = Field(None, description="国籍")
    ethnicity: Optional[str] = Field(None, description="民族")
    
    # 联系信息
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    wechat_openid: Optional[str] = Field(None, description="微信OpenID")
    qq_number: Optional[str] = Field(None, description="QQ号")
    
    # 地址信息
    home_address: Optional[str] = Field(None, description="家庭地址")
    current_address: Optional[str] = Field(None, description="现住址")
    postal_code: Optional[str] = Field(None, description="邮编")
    
    # 组织关系
    college_id: Optional[str] = Field(None, description="学院ID")
    major_id: Optional[str] = Field(None, description="专业ID")
    department_id: Optional[str] = Field(None, description="部门ID")
    class_id: Optional[str] = Field(None, description="班级ID")
    
    # 权限信息
    permissions: Optional[str] = Field(None, description="权限配置JSON")
    
    # 认证信息
    password_hash: Optional[str] = Field(None, description="密码哈希")
    password_salt: Optional[str] = Field(None, description="密码盐")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    login_attempts: int = Field(0, description="登录尝试次数")
    account_locked: bool = Field(False, description="账户是否锁定")
    
    @property
    def primary_key(self) -> str:
        """主键是person_id"""
        return self.person_id
    
    @property
    def display_name(self) -> str:
        """显示名称"""
        return self.name
    
    @property
    def is_student(self) -> bool:
        """是否为学生"""
        return self.person_type == "student"
    
    @property
    def is_teacher(self) -> bool:
        """是否为教师"""
        return self.person_type == "teacher"
    
    @property
    def is_admin(self) -> bool:
        """是否为管理员"""
        return self.person_type == "admin"
    
    def get_permissions(self) -> Dict[str, Any]:
        """获取权限配置"""
        if not self.permissions:
            return {}
        
        try:
            import json
            return json.loads(self.permissions)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @validator('person_type')
    def validate_person_type(cls, v):
        """验证人员类型"""
        allowed_types = ['student', 'teacher', 'admin', 'staff']
        if v not in allowed_types:
            raise ValueError(f'person_type must be one of {allowed_types}')
        return v


class Student(Person):
    """学生模型"""
    
    student_id: Optional[str] = Field(None, description="学生ID")
    admission_date: Optional[date] = Field(None, description="入学日期")
    graduation_date: Optional[date] = Field(None, description="毕业日期")
    academic_status: Optional[str] = Field(None, description="学籍状态")
    
    # 学生特有字段
    enrollment_year: Optional[int] = Field(None, description="入学年份")
    grade_level: Optional[int] = Field(None, description="年级")
    
    @property
    def primary_key(self) -> str:
        """学生主键优先使用student_id"""
        return self.student_id or self.person_id
    
    @property
    def current_grade(self) -> Optional[int]:
        """计算当前年级"""
        if not self.admission_date:
            return None
        
        current_year = datetime.now().year
        admission_year = self.admission_date.year
        return current_year - admission_year + 1


class Teacher(Person):
    """教师模型"""
    
    employee_id: Optional[str] = Field(None, description="员工ID")
    employment_date: Optional[date] = Field(None, description="入职日期")
    employment_status: Optional[str] = Field(None, description="任职状态")
    academic_title: Optional[str] = Field(None, description="学术职称")
    research_field: Optional[str] = Field(None, description="研究领域")
    education_background: Optional[str] = Field(None, description="教育背景")
    graduate_school: Optional[str] = Field(None, description="毕业院校")
    
    @property
    def primary_key(self) -> str:
        """教师主键优先使用employee_id"""
        return self.employee_id or self.person_id
    
    @property
    def title_display(self) -> str:
        """职称显示"""
        if self.academic_title:
            return f"{self.name} {self.academic_title}"
        return self.name


class Admin(Person):
    """管理员模型"""
    
    employee_id: Optional[str] = Field(None, description="员工ID") 
    employment_date: Optional[date] = Field(None, description="入职日期")
    admin_level: Optional[str] = Field(None, description="管理员级别")
    admin_scope: Optional[str] = Field(None, description="管理范围")
    
    @property
    def primary_key(self) -> str:
        """管理员主键优先使用employee_id"""
        return self.employee_id or self.person_id
    
    @property
    def is_super_admin(self) -> bool:
        """是否为超级管理员"""
        return self.admin_level == "super" 