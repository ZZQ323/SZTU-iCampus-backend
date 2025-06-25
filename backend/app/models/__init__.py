"""
数据模型层
定义所有的业务数据模型，提供类型安全和数据验证
"""

from .base import BaseModel
from .person import Person, Student, Teacher, Admin
from .academic import Grade, Course, CourseInstance, Exam, Schedule
from .campus import Announcement, Event, CampusCard, Transaction
from .organization import College, Major, Class, Department

__all__ = [
    "BaseModel",
    "Person", "Student", "Teacher", "Admin",
    "Grade", "Course", "CourseInstance", "Exam", "Schedule", 
    "Announcement", "Event", "CampusCard", "Transaction",
    "College", "Major", "Class", "Department"
] 