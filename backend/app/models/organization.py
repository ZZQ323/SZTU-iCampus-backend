"""
组织架构相关数据模型
包含学院、专业、班级、部门等组织结构数据
"""
from datetime import date
from typing import Optional
from decimal import Decimal
from pydantic import Field
from .base import BaseModel


class College(BaseModel):
    """学院模型"""
    
    college_id: str = Field(..., description="学院ID")
    college_name: str = Field(..., description="学院名称")
    college_code: str = Field(..., description="学院代码")
    
    # 联系信息
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    website: Optional[str] = Field(None, description="网站")
    office_location: Optional[str] = Field(None, description="办公地点")
    main_building: Optional[str] = Field(None, description="主要建筑")
    
    # 负责人信息
    dean_id: Optional[str] = Field(None, description="院长ID")
    vice_dean_id: Optional[str] = Field(None, description="副院长ID")
    secretary_id: Optional[str] = Field(None, description="秘书ID")
    
    # 统计信息
    total_teachers: Optional[int] = Field(None, description="教师总数")
    total_students: Optional[int] = Field(None, description="学生总数")
    total_majors: Optional[int] = Field(None, description="专业总数")
    
    # 描述信息
    description: Optional[str] = Field(None, description="学院简介")
    mission: Optional[str] = Field(None, description="办学使命")
    
    @property
    def primary_key(self) -> str:
        return self.college_id


class Major(BaseModel):
    """专业模型"""
    
    major_id: str = Field(..., description="专业ID")
    major_name: str = Field(..., description="专业名称")
    major_code: str = Field(..., description="专业代码")
    college_id: str = Field(..., description="所属学院ID")
    
    # 基本信息
    duration_years: Optional[int] = Field(None, description="学制年限")
    degree_type: Optional[str] = Field(None, description="学位类型")
    director_id: Optional[str] = Field(None, description="专业负责人ID")
    
    # 统计信息
    total_teachers: Optional[int] = Field(None, description="教师总数")
    total_students: Optional[int] = Field(None, description="学生总数")
    total_classes: Optional[int] = Field(None, description="班级总数")
    total_courses: Optional[int] = Field(None, description="课程总数")
    
    # 招生信息
    enrollment_quota: Optional[int] = Field(None, description="招生计划")
    tuition_fee: Optional[Decimal] = Field(None, description="学费")
    
    # 专业描述
    description: Optional[str] = Field(None, description="专业介绍")
    career_prospects: Optional[str] = Field(None, description="就业前景")
    core_courses: Optional[str] = Field(None, description="核心课程JSON")
    
    # 质量评估
    accreditation: Optional[str] = Field(None, description="专业认证")
    ranking: Optional[str] = Field(None, description="专业排名")
    
    @property
    def primary_key(self) -> str:
        return self.major_id


class Class(BaseModel):
    """班级模型"""
    
    class_id: str = Field(..., description="班级ID")
    class_name: str = Field(..., description="班级名称")
    class_code: str = Field(..., description="班级代码")
    
    # 基本信息
    grade: int = Field(..., description="年级")
    semester_enrolled: str = Field(..., description="入学学期")
    major_id: str = Field(..., description="专业ID")
    college_id: str = Field(..., description="学院ID")
    
    # 负责人信息
    class_advisor_id: Optional[str] = Field(None, description="班主任ID")
    counselor_id: Optional[str] = Field(None, description="辅导员ID")
    
    # 统计信息
    total_students: Optional[int] = Field(None, description="学生总数")
    male_count: Optional[int] = Field(None, description="男生人数")
    female_count: Optional[int] = Field(None, description="女生人数")
    
    # 其他信息
    graduation_date: Optional[date] = Field(None, description="预计毕业日期")
    classroom_location: Optional[str] = Field(None, description="固定教室")
    class_motto: Optional[str] = Field(None, description="班级口号")
    class_description: Optional[str] = Field(None, description="班级简介")
    
    @property
    def primary_key(self) -> str:
        return self.class_id
    
    @property
    def current_grade(self) -> int:
        """计算当前年级"""
        from datetime import datetime
        current_year = datetime.now().year
        return current_year - self.grade + 1


class Department(BaseModel):
    """部门模型"""
    
    department_id: str = Field(..., description="部门ID")
    department_name: str = Field(..., description="部门名称")
    department_type: str = Field(..., description="部门类型")
    
    # 组织关系
    college_id: Optional[str] = Field(None, description="所属学院ID")
    parent_department_id: Optional[str] = Field(None, description="上级部门ID")
    level: Optional[int] = Field(None, description="部门层级")
    
    # 联系信息
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    office_location: Optional[str] = Field(None, description="办公地点")
    
    # 负责人信息
    head_id: Optional[str] = Field(None, description="部门主管ID")
    deputy_head_id: Optional[str] = Field(None, description="副主管ID")
    
    # 统计信息
    total_staff: Optional[int] = Field(None, description="员工总数")
    
    # 职能描述
    description: Optional[str] = Field(None, description="部门简介")
    responsibilities: Optional[str] = Field(None, description="职责JSON")
    
    @property
    def primary_key(self) -> str:
        return self.department_id 