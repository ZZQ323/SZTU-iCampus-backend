from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class GradeType(str, Enum):
    REGULAR = "regular"
    MIDTERM = "midterm"
    FINAL = "final"
    TOTAL = "total"

class GradeStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    RESIT = "resit"
    MAKEUP = "makeup"

class GradeBase(BaseModel):
    student_id: str
    student_name: str
    course_code: str
    course_name: str
    course_type: Optional[str] = "必修"
    credits: float
    semester: str
    academic_year: str
    teacher_name: str
    regular_score: Optional[float] = None
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None
    total_score: float
    grade_level: Optional[str] = None
    gpa_points: Optional[float] = None
    status: Optional[GradeStatus] = GradeStatus.PASS
    class_rank: Optional[int] = None
    class_total: Optional[int] = None
    exam_date: Optional[datetime] = None
    publish_date: Optional[datetime] = None

class GradeCreate(GradeBase):
    pass

class GradeUpdate(BaseModel):
    student_name: Optional[str] = None
    course_name: Optional[str] = None
    course_type: Optional[str] = None
    credits: Optional[float] = None
    semester: Optional[str] = None
    academic_year: Optional[str] = None
    teacher_name: Optional[str] = None
    regular_score: Optional[float] = None
    midterm_score: Optional[float] = None
    final_score: Optional[float] = None
    total_score: Optional[float] = None
    grade_level: Optional[str] = None
    gpa_points: Optional[float] = None
    status: Optional[GradeStatus] = None
    class_rank: Optional[int] = None
    class_total: Optional[int] = None
    exam_date: Optional[datetime] = None
    publish_date: Optional[datetime] = None

class Grade(GradeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GradeSummary(BaseModel):
    """成绩汇总统计"""
    total_courses: int
    total_credits: float
    avg_score: float
    avg_gpa: float
    pass_rate: float
    course_distribution: dict  # 课程类型分布
    grade_distribution: dict   # 等级分布 