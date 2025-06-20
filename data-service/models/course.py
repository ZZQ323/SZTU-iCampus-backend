"""
课程相关数据模型
包含Course（课程基础信息）、CourseInstance（开课实例）、Grade（成绩）、GradeStatistics（成绩统计）
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, Time,
    Text, ForeignKey, JSON, Enum as SQLEnum, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

from .base import BaseModel, COURSE_TYPES, EXAM_FORMS, GRADE_LEVELS


class Course(BaseModel):
    """
    课程表 - 管理课程基础信息
    """
    __tablename__ = "courses"
    
    # 基础信息
    course_id = Column(String(20), unique=True, nullable=False, comment="课程编码")
    course_name = Column(String(100), nullable=False, comment="课程名称")
    course_name_en = Column(String(200), nullable=True, comment="英文名称")
    course_code = Column(String(20), nullable=False, comment="课程代码")
    
    # 课程属性
    course_type = Column(SQLEnum(*COURSE_TYPES, name="course_type_enum"), nullable=False, comment="课程类型")
    credit_hours = Column(Numeric(3, 1), nullable=False, comment="学分")
    total_hours = Column(Integer, nullable=False, comment="总学时")
    theory_hours = Column(Integer, default=0, comment="理论学时")
    practice_hours = Column(Integer, default=0, comment="实践学时")
    experiment_hours = Column(Integer, default=0, comment="实验学时")
    
    # 所属信息
    major_id = Column(String(10), ForeignKey("majors.major_id"), nullable=False, comment="所属专业")
    college_id = Column(String(10), ForeignKey("colleges.college_id"), nullable=False, comment="所属学院")
    
    # 先修课程
    prerequisite_courses = Column(JSON, default=list, comment="先修课程列表")
    
    # 考核方式
    assessment_method = Column(String(50), nullable=True, comment="考核方式")
    exam_form = Column(SQLEnum(*EXAM_FORMS, name="exam_form_enum"), default="closed_book", comment="考试形式")
    
    # 课程描述
    description = Column(Text, nullable=True, comment="课程简介")
    objectives = Column(Text, nullable=True, comment="教学目标")
    syllabus = Column(Text, nullable=True, comment="教学大纲")
    textbook = Column(String(200), nullable=True, comment="指定教材")
    references = Column(JSON, default=list, comment="参考书目")
    
    # 难度等级
    difficulty_level = Column(Integer, default=3, comment="难度等级（1-5）")
    workload_level = Column(Integer, default=3, comment="作业量（1-5）")
    
    # 课程状态
    is_active = Column(Boolean, default=True, comment="是否开设")
    approval_status = Column(String(20), default="approved", comment="审批状态")
    
    # 关联关系
    major = relationship("Major", back_populates="courses")
    course_instances = relationship("CourseInstance", back_populates="course")
    
    # 索引
    __table_args__ = (
        Index("idx_course_major", "major_id"),
        Index("idx_course_type", "course_type"),
        Index("idx_course_code", "course_code"),
        Index("idx_course_active", "is_active"),
    )
    
    def __repr__(self):
        return f"<Course(id={self.course_id}, name={self.course_name})>"


class CourseInstance(BaseModel):
    """
    开课实例表 - 管理具体某学期的开课情况
    """
    __tablename__ = "course_instances"
    
    # 基础信息
    instance_id = Column(String(20), unique=True, nullable=False, comment="开课实例ID")
    
    # 关联信息
    course_id = Column(String(20), ForeignKey("courses.course_id"), nullable=False, comment="课程")
    teacher_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=False, comment="主讲教师")
    assistant_teacher_id = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="助教")
    
    # 时间信息
    semester = Column(String(20), nullable=False, comment="学期，如2024-2025-1")
    academic_year = Column(String(10), nullable=False, comment="学年，如2024-2025")
    
    # 上课安排
    schedule_info = Column(JSON, default=list, comment="上课时间安排")
    class_locations = Column(JSON, default=list, comment="上课地点")
    
    # 选课信息
    max_students = Column(Integer, default=50, comment="最大选课人数")
    current_students = Column(Integer, default=0, comment="当前选课人数")
    min_students = Column(Integer, default=10, comment="最少开课人数")
    
    # 班级信息
    target_grades = Column(JSON, default=list, comment="目标年级")
    target_majors = Column(JSON, default=list, comment="目标专业")
    
    # 课程状态
    instance_status = Column(String(20), default="planning", comment="实例状态：planning/open/closed/cancelled")
    registration_start = Column(DateTime, nullable=True, comment="选课开始时间")
    registration_end = Column(DateTime, nullable=True, comment="选课结束时间")
    class_start_date = Column(Date, nullable=True, comment="开课日期")
    class_end_date = Column(Date, nullable=True, comment="结课日期")
    
    # 教学安排
    total_weeks = Column(Integer, default=16, comment="总周数")
    weekly_hours = Column(Integer, default=2, comment="周学时")
    
    # 考核安排
    exam_date = Column(DateTime, nullable=True, comment="考试时间")
    exam_location = Column(String(50), nullable=True, comment="考试地点")
    makeup_exam_date = Column(DateTime, nullable=True, comment="补考时间")
    
    # 成绩统计
    avg_score = Column(Numeric(5, 2), nullable=True, comment="平均分")
    pass_rate = Column(Numeric(5, 2), nullable=True, comment="及格率")
    excellent_rate = Column(Numeric(5, 2), nullable=True, comment="优秀率")
    
    # 评价信息
    teacher_rating = Column(Numeric(3, 2), nullable=True, comment="教师评分")
    course_rating = Column(Numeric(3, 2), nullable=True, comment="课程评分")
    
    # 关联关系
    course = relationship("Course", back_populates="course_instances")
    teacher = relationship("Person", foreign_keys=[teacher_id])
    assistant_teacher = relationship("Person", foreign_keys=[assistant_teacher_id])
    grades = relationship("Grade", back_populates="course_instance")
    room_occupations = relationship("RoomOccupation", back_populates="course_instance")
    
    # 索引
    __table_args__ = (
        Index("idx_instance_course", "course_id"),
        Index("idx_instance_teacher", "teacher_id"),
        Index("idx_instance_semester", "semester"),
        Index("idx_instance_status", "instance_status"),
    )
    
    def __repr__(self):
        return f"<CourseInstance(id={self.instance_id}, semester={self.semester})>"
    
    @property
    def is_full(self):
        """是否已满"""
        return self.current_students >= self.max_students
    
    @property
    def can_open(self):
        """是否满足开课条件"""
        return self.current_students >= self.min_students


class Grade(BaseModel):
    """
    成绩表 - 管理学生课程成绩
    """
    __tablename__ = "grades"
    
    # 基础信息
    grade_id = Column(String(20), unique=True, nullable=False, comment="成绩记录ID")
    
    # 关联信息
    student_id = Column(String(12), ForeignKey("persons.student_id"), nullable=False, comment="学生学号")
    course_instance_id = Column(String(20), ForeignKey("course_instances.instance_id"), nullable=False, comment="开课实例")
    
    # 成绩信息
    usual_score = Column(Numeric(5, 2), nullable=True, comment="平时成绩")
    midterm_score = Column(Numeric(5, 2), nullable=True, comment="期中成绩")
    final_score = Column(Numeric(5, 2), nullable=True, comment="期末成绩")
    lab_score = Column(Numeric(5, 2), nullable=True, comment="实验成绩")
    homework_score = Column(Numeric(5, 2), nullable=True, comment="作业成绩")
    
    # 总成绩
    total_score = Column(Numeric(5, 2), nullable=True, comment="总成绩")
    grade_point = Column(Numeric(3, 2), nullable=True, comment="绩点")
    grade_level = Column(SQLEnum(*GRADE_LEVELS, name="grade_level_enum"), nullable=True, comment="等第")
    
    # 成绩权重（JSON格式）
    score_weights = Column(JSON, default=lambda: {
        "usual": 20, "midterm": 30, "final": 50, "lab": 0, "homework": 0
    }, comment="成绩权重配置")
    
    # 考试信息
    exam_type = Column(String(20), default="normal", comment="考试类型：normal/makeup/retake")
    exam_date = Column(DateTime, nullable=True, comment="考试时间")
    submit_date = Column(DateTime, nullable=True, comment="成绩提交时间")
    
    # 状态信息
    grade_status = Column(String(20), default="draft", comment="成绩状态：draft/submitted/confirmed")
    is_passed = Column(Boolean, nullable=True, comment="是否及格")
    is_retake_required = Column(Boolean, default=False, comment="是否需要重修")
    
    # 备注信息
    teacher_comment = Column(Text, nullable=True, comment="教师评语")
    grade_notes = Column(Text, nullable=True, comment="成绩备注")
    
    # 审核信息
    reviewed_by = Column(String(10), ForeignKey("persons.employee_id"), nullable=True, comment="审核人")
    reviewed_at = Column(DateTime, nullable=True, comment="审核时间")
    
    # 关联关系
    student = relationship("Person", foreign_keys=[student_id])
    course_instance = relationship("CourseInstance", back_populates="grades")
    reviewer = relationship("Person", foreign_keys=[reviewed_by])
    
    # 索引
    __table_args__ = (
        Index("idx_grade_student", "student_id"),
        Index("idx_grade_course_instance", "course_instance_id"),
        Index("idx_grade_status", "grade_status"),
        Index("idx_grade_student_course", "student_id", "course_instance_id"),
    )
    
    def __repr__(self):
        return f"<Grade(id={self.grade_id}, student={self.student_id}, score={self.total_score})>"
    
    def calculate_total_score(self):
        """计算总成绩"""
        weights = self.score_weights or {}
        scores = {
            "usual": self.usual_score or 0,
            "midterm": self.midterm_score or 0,
            "final": self.final_score or 0,
            "lab": self.lab_score or 0,
            "homework": self.homework_score or 0,
        }
        
        total = 0
        total_weight = 0
        
        for score_type, weight in weights.items():
            if weight > 0 and scores.get(score_type) is not None:
                total += scores[score_type] * weight / 100
                total_weight += weight
        
        if total_weight > 0:
            self.total_score = round(total, 2)
            self.is_passed = self.total_score >= 60
            self.grade_point = self._calculate_gpa(self.total_score)
            self.grade_level = self._calculate_grade_level(self.total_score)
    
    def _calculate_gpa(self, score):
        """计算绩点"""
        if score >= 90:
            return 4.0
        elif score >= 80:
            return 3.0 + (score - 80) * 0.1
        elif score >= 70:
            return 2.0 + (score - 70) * 0.1
        elif score >= 60:
            return 1.0 + (score - 60) * 0.1
        else:
            return 0.0
    
    def _calculate_grade_level(self, score):
        """计算等第"""
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


class GradeStatistics(BaseModel):
    """
    成绩统计表 - 管理课程成绩统计信息
    """
    __tablename__ = "grade_statistics"
    
    # 基础信息
    stat_id = Column(String(20), unique=True, nullable=False, comment="统计记录ID")
    
    # 关联信息
    course_instance_id = Column(String(20), ForeignKey("course_instances.instance_id"), nullable=False, comment="开课实例")
    
    # 统计时间
    stat_date = Column(Date, nullable=False, comment="统计日期")
    
    # 基础统计
    total_students = Column(Integer, default=0, comment="总人数")
    submitted_count = Column(Integer, default=0, comment="已提交成绩人数")
    
    # 分数统计
    max_score = Column(Numeric(5, 2), nullable=True, comment="最高分")
    min_score = Column(Numeric(5, 2), nullable=True, comment="最低分")
    avg_score = Column(Numeric(5, 2), nullable=True, comment="平均分")
    median_score = Column(Numeric(5, 2), nullable=True, comment="中位数")
    std_deviation = Column(Numeric(5, 2), nullable=True, comment="标准差")
    
    # 等第统计
    grade_a_count = Column(Integer, default=0, comment="A等人数")
    grade_b_count = Column(Integer, default=0, comment="B等人数")
    grade_c_count = Column(Integer, default=0, comment="C等人数")
    grade_d_count = Column(Integer, default=0, comment="D等人数")
    grade_f_count = Column(Integer, default=0, comment="F等人数")
    
    # 率统计
    pass_rate = Column(Numeric(5, 2), nullable=True, comment="及格率")
    excellent_rate = Column(Numeric(5, 2), nullable=True, comment="优秀率（>=90分）")
    good_rate = Column(Numeric(5, 2), nullable=True, comment="良好率（>=80分）")
    
    # 分数段统计
    score_distribution = Column(JSON, default=dict, comment="分数段分布")
    
    # 关联关系
    course_instance = relationship("CourseInstance")
    
    # 索引
    __table_args__ = (
        Index("idx_stat_course_instance", "course_instance_id"),
        Index("idx_stat_date", "stat_date"),
    )
    
    def __repr__(self):
        return f"<GradeStatistics(id={self.stat_id}, avg_score={self.avg_score})>" 