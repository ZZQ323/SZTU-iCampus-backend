from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    
    # 课程基本信息
    course_name = Column(String(100), nullable=False, comment="课程名称")
    course_code = Column(String(20), comment="课程代码")
    teacher = Column(String(50), nullable=False, comment="授课教师")
    classroom = Column(String(50), nullable=False, comment="教室")
    
    # 时间信息
    week_day = Column(Integer, nullable=False, comment="星期几(1-7, 1=周一)")
    time_slot = Column(Integer, nullable=False, comment="第几节课(1=第1-2节, 2=第3-4节, 3=第5-6节, 4=第7-8节, 5=第9-10节)")
    start_time = Column(String(5), nullable=False, comment="开始时间(HH:MM)")
    end_time = Column(String(5), nullable=False, comment="结束时间(HH:MM)")
    
    # 周次信息
    week_expression = Column(String(100), nullable=False, comment="周次表达式(如:1-16,1,3,5,1-8+10-16)")
    start_week = Column(Integer, nullable=False, comment="开始周次")
    end_week = Column(Integer, nullable=False, comment="结束周次")
    odd_even = Column(String(10), default="all", comment="单双周(all/odd/even)")
    
    # 课程属性
    course_type = Column(String(20), default="必修", comment="课程类型(必修/选修/实验/实践)")
    credits = Column(String(10), comment="学分")
    course_hours = Column(Integer, comment="课时")
    course_nature = Column(String(20), comment="课程性质")
    
    # 学期和学生信息
    semester = Column(String(20), nullable=False, comment="学期(如:2024-2025-1)")
    academic_year = Column(String(20), nullable=False, comment="学年(如:2024-2025)")
    term = Column(Integer, nullable=False, comment="学期(1=上学期,2=下学期)")
    student_id = Column(String(20), nullable=False, comment="学生学号")
    class_name = Column(String(50), comment="班级")
    major = Column(String(100), comment="专业")
    college = Column(String(100), comment="学院")
    
    # 课程描述
    course_description = Column(Text, comment="课程描述")
    textbook = Column(Text, comment="教材信息")
    requirements = Column(Text, comment="课程要求")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Schedule(course_name={self.course_name}, teacher={self.teacher}, week_day={self.week_day}, time_slot={self.time_slot})>"
    
    def is_in_week(self, week_number: int) -> bool:
        """判断指定周次是否有课"""
        if week_number < self.start_week or week_number > self.end_week:
            return False
        
        # 检查单双周
        if self.odd_even == "odd" and week_number % 2 == 0:
            return False
        if self.odd_even == "even" and week_number % 2 == 1:
            return False
        
        # 解析周次表达式
        return self._parse_week_expression(week_number)
    
    def _parse_week_expression(self, week_number: int) -> bool:
        """解析周次表达式，判断指定周是否在表达式范围内"""
        if not self.week_expression:
            return self.start_week <= week_number <= self.end_week
        
        # 处理复杂的周次表达式
        # 支持格式：1-16, 1,3,5, 1-8+10-16 等
        parts = self.week_expression.replace('+', ',').split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part and not part.startswith('-'):
                # 范围表达式，如 1-16
                try:
                    start, end = map(int, part.split('-'))
                    if start <= week_number <= end:
                        return True
                except ValueError:
                    continue
            else:
                # 单个周次，如 5
                try:
                    if int(part) == week_number:
                        return True
                except ValueError:
                    continue
        
        return False 