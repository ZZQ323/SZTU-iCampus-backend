"""
学术相关数据模型
包含成绩、课程、课表、考试等学术数据
"""
from datetime import date, datetime, time
from typing import Optional, Dict, Any, List
from decimal import Decimal
from pydantic import Field, validator
from .base import BaseModel


class Grade(BaseModel):
    """成绩模型"""
    
    grade_id: str = Field(..., description="成绩ID")
    student_id: str = Field(..., description="学生ID")
    course_instance_id: str = Field(..., description="课程实例ID")
    
    # 各项成绩
    usual_score: Optional[Decimal] = Field(None, description="平时成绩")
    midterm_score: Optional[Decimal] = Field(None, description="期中成绩")
    final_score: Optional[Decimal] = Field(None, description="期末成绩")
    lab_score: Optional[Decimal] = Field(None, description="实验成绩")
    homework_score: Optional[Decimal] = Field(None, description="作业成绩")
    total_score: Optional[Decimal] = Field(None, description="总成绩")
    
    # 成绩评价
    grade_point: Optional[Decimal] = Field(None, description="绩点")
    grade_level: Optional[str] = Field(None, description="等级：A/B/C/D/F")
    
    # 权重配置
    score_weights: Optional[str] = Field(None, description="成绩权重配置JSON")
    
    # 考试信息
    exam_type: Optional[str] = Field(None, description="考试类型")
    exam_date: Optional[datetime] = Field(None, description="考试日期")
    submit_date: Optional[datetime] = Field(None, description="提交日期")
    
    # 状态信息
    grade_status: str = Field("draft", description="成绩状态：draft/confirmed/final")
    is_passed: Optional[bool] = Field(None, description="是否通过")
    is_retake_required: bool = Field(False, description="是否需要重修")
    
    # 教师评价
    teacher_comment: Optional[str] = Field(None, description="教师评语")
    grade_notes: Optional[str] = Field(None, description="成绩备注")
    reviewed_by: Optional[str] = Field(None, description="审核人")
    reviewed_at: Optional[datetime] = Field(None, description="审核时间")
    
    # 关联信息（冗余字段，便于查询）
    course_name: Optional[str] = Field(None, description="课程名称")
    course_code: Optional[str] = Field(None, description="课程代码") 
    credit_hours: Optional[Decimal] = Field(None, description="学分")
    semester: Optional[str] = Field(None, description="学期")
    teacher_name: Optional[str] = Field(None, description="教师姓名")
    
    @property
    def primary_key(self) -> str:
        return self.grade_id
    
    def calculate_gpa(self) -> Optional[Decimal]:
        """计算GPA（基于总成绩）"""
        if not self.total_score:
            return None
        
        score = float(self.total_score)
        if score >= 90:
            return Decimal("4.0")
        elif score >= 80:
            return Decimal("3.0")
        elif score >= 70:
            return Decimal("2.0")
        elif score >= 60:
            return Decimal("1.0")
        else:
            return Decimal("0.0")
    
    def calculate_grade_level(self) -> Optional[str]:
        """计算等级"""
        if not self.total_score:
            return None
            
        score = float(self.total_score)
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


class Course(BaseModel):
    """课程模型"""
    
    course_id: str = Field(..., description="课程ID")
    course_name: str = Field(..., description="课程名称")
    course_name_en: Optional[str] = Field(None, description="英文课程名称")
    course_code: str = Field(..., description="课程代码")
    course_type: str = Field(..., description="课程类型：required/elective/public")
    
    # 学分学时
    credit_hours: Decimal = Field(..., description="学分")
    total_hours: int = Field(..., description="总学时")
    theory_hours: Optional[int] = Field(None, description="理论学时")
    practice_hours: Optional[int] = Field(None, description="实践学时")
    experiment_hours: Optional[int] = Field(None, description="实验学时")
    
    # 归属信息
    major_id: str = Field(..., description="专业ID")
    college_id: str = Field(..., description="学院ID")
    
    # 课程内容
    prerequisite_courses: Optional[str] = Field(None, description="先修课程JSON")
    assessment_method: Optional[str] = Field(None, description="考核方式")
    exam_form: Optional[str] = Field(None, description="考试形式")
    description: Optional[str] = Field(None, description="课程描述")
    objectives: Optional[str] = Field(None, description="课程目标")
    syllabus: Optional[str] = Field(None, description="教学大纲")
    textbook: Optional[str] = Field(None, description="教材")
    references: Optional[str] = Field(None, description="参考资料JSON")
    
    # 难度评估
    difficulty_level: Optional[int] = Field(None, description="难度等级1-5")
    workload_level: Optional[int] = Field(None, description="工作量等级1-5")
    
    # 审批状态
    approval_status: Optional[str] = Field(None, description="审批状态")
    
    @property
    def primary_key(self) -> str:
        return self.course_id


class CourseInstance(BaseModel):
    """开课实例模型"""
    
    instance_id: str = Field(..., description="开课实例ID")
    course_id: str = Field(..., description="课程ID")
    teacher_id: str = Field(..., description="主讲教师ID")
    assistant_teacher_id: Optional[str] = Field(None, description="助教ID")
    
    # 学期信息
    semester: str = Field(..., description="学期")
    academic_year: str = Field(..., description="学年")
    
    # 排课信息
    schedule_info: Optional[str] = Field(None, description="排课信息JSON")
    class_locations: Optional[str] = Field(None, description="上课地点JSON")
    
    # 选课信息
    max_students: Optional[int] = Field(None, description="最大选课人数")
    current_students: Optional[int] = Field(None, description="当前选课人数")
    min_students: Optional[int] = Field(None, description="最小开课人数")
    target_grades: Optional[str] = Field(None, description="目标年级JSON")
    target_majors: Optional[str] = Field(None, description="目标专业JSON")
    
    # 实例状态
    instance_status: Optional[str] = Field(None, description="实例状态")
    registration_start: Optional[datetime] = Field(None, description="选课开始时间")
    registration_end: Optional[datetime] = Field(None, description="选课结束时间")
    
    # 上课时间
    class_start_date: Optional[date] = Field(None, description="开课日期")
    class_end_date: Optional[date] = Field(None, description="结课日期")
    total_weeks: Optional[int] = Field(None, description="总周数")
    weekly_hours: Optional[int] = Field(None, description="周学时")
    
    # 考试安排
    exam_date: Optional[datetime] = Field(None, description="考试时间")
    exam_location: Optional[str] = Field(None, description="考试地点")
    makeup_exam_date: Optional[datetime] = Field(None, description="补考时间")
    
    # 统计信息
    avg_score: Optional[Decimal] = Field(None, description="平均分")
    pass_rate: Optional[Decimal] = Field(None, description="通过率")
    excellent_rate: Optional[Decimal] = Field(None, description="优秀率")
    teacher_rating: Optional[Decimal] = Field(None, description="教师评分")
    course_rating: Optional[Decimal] = Field(None, description="课程评分")
    
    @property
    def primary_key(self) -> str:
        return self.instance_id


class Schedule(BaseModel):
    """课表模型"""
    
    schedule_id: str = Field(..., description="课表ID")
    course_instance_id: str = Field(..., description="课程实例ID")
    
    # 时间安排
    day_of_week: int = Field(..., description="星期几(1-7)")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")
    
    # 地点信息
    classroom: Optional[str] = Field(None, description="教室")
    building: Optional[str] = Field(None, description="建筑物")
    
    # 周次信息
    week_range: Optional[str] = Field(None, description="周次范围")
    
    # 授课信息
    teacher_id: Optional[str] = Field(None, description="授课教师ID")
    class_type: str = Field("lecture", description="课程类型：lecture/lab/tutorial")
    
    # 冗余字段（便于查询）
    course_name: Optional[str] = Field(None, description="课程名称")
    teacher_name: Optional[str] = Field(None, description="教师姓名")
    
    @property
    def primary_key(self) -> str:
        return self.schedule_id
    
    @property
    def time_display(self) -> str:
        """时间显示"""
        return f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"


class Exam(BaseModel):
    """考试模型"""
    
    exam_id: str = Field(..., description="考试ID")
    course_instance_id: str = Field(..., description="课程实例ID")
    
    # 考试基本信息
    exam_name: str = Field(..., description="考试名称")
    exam_type: str = Field(..., description="考试类型：midterm/final/quiz/makeup")
    
    # 时间地点
    exam_date: datetime = Field(..., description="考试时间")
    duration_minutes: int = Field(..., description="考试时长(分钟)")
    exam_location: str = Field(..., description="考试地点")
    
    # 考试安排
    seat_arrangement: Optional[str] = Field(None, description="座位安排")
    invigilators: Optional[str] = Field(None, description="监考老师JSON")
    
    # 考试要求
    exam_requirements: Optional[str] = Field(None, description="考试要求")
    allowed_materials: Optional[str] = Field(None, description="允许携带材料")
    
    # 状态信息
    exam_status: str = Field("scheduled", description="考试状态")
    
    # 冗余字段
    course_name: Optional[str] = Field(None, description="课程名称")
    teacher_name: Optional[str] = Field(None, description="教师姓名")
    
    @property
    def primary_key(self) -> str:
        return self.exam_id
    
    @property
    def is_upcoming(self) -> bool:
        """是否即将到来"""
        return self.exam_date > datetime.now()
    
    @property
    def countdown_days(self) -> int:
        """倒计时天数"""
        if not self.is_upcoming:
            return 0
        delta = self.exam_date - datetime.now()
        return delta.days 