from sqlalchemy import Column, Integer, String, DateTime, Float, Enum
from datetime import datetime
from app.database import Base
import enum

class GradeType(enum.Enum):
    REGULAR = "regular"        # 平时成绩
    MIDTERM = "midterm"        # 期中成绩
    FINAL = "final"           # 期末成绩
    TOTAL = "total"           # 总成绩

class GradeStatus(enum.Enum):
    PASS = "pass"             # 通过
    FAIL = "fail"             # 不通过
    RESIT = "resit"           # 重修
    MAKEUP = "makeup"         # 补考

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), nullable=False, index=True, comment="学生学号")
    student_name = Column(String(50), nullable=False, comment="学生姓名")
    course_code = Column(String(20), nullable=False, comment="课程代码")
    course_name = Column(String(100), nullable=False, comment="课程名称")
    course_type = Column(String(20), default="必修", comment="课程类型")
    credits = Column(Float, nullable=False, comment="学分")
    semester = Column(String(20), nullable=False, comment="学期")
    academic_year = Column(String(10), nullable=False, comment="学年")
    teacher_name = Column(String(50), nullable=False, comment="任课教师")
    
    # 各项成绩
    regular_score = Column(Float, comment="平时成绩")
    midterm_score = Column(Float, comment="期中成绩")
    final_score = Column(Float, comment="期末成绩")
    total_score = Column(Float, nullable=False, comment="总成绩")
    
    # 等级和绩点
    grade_level = Column(String(5), comment="等级(A+,A,B+,B,C+,C,D+,D,F)")
    gpa_points = Column(Float, comment="绩点")
    status = Column(Enum(GradeStatus), default=GradeStatus.PASS, comment="成绩状态")
    
    # 排名信息
    class_rank = Column(Integer, comment="班级排名")
    class_total = Column(Integer, comment="班级总人数")
    
    # 时间信息
    exam_date = Column(DateTime, comment="考试时间")
    publish_date = Column(DateTime, default=datetime.utcnow, comment="成绩发布时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间") 