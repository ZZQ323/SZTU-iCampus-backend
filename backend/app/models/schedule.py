from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(100), nullable=False, comment="课程名称")
    teacher = Column(String(50), nullable=False, comment="授课教师")
    classroom = Column(String(50), nullable=False, comment="教室")
    week_day = Column(Integer, nullable=False, comment="星期几(1-7)")
    start_time = Column(String(5), nullable=False, comment="开始时间(HH:MM)")
    end_time = Column(String(5), nullable=False, comment="结束时间(HH:MM)")
    weeks = Column(String(100), nullable=False, comment="上课周次")
    course_type = Column(String(20), default="必修", comment="课程类型")
    credits = Column(String(10), comment="学分")
    student_id = Column(String(20), nullable=False, comment="学生学号")
    semester = Column(String(20), default="2024春", comment="学期")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 