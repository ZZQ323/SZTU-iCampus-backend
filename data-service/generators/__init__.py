"""
Mock数据生成器包
用于生成符合业务逻辑的中文Mock数据
"""

from .base_generator import MockDataGenerator
from .person_generator import PersonGenerator
from .course_generator import CourseGenerator

__all__ = [
    "MockDataGenerator",
    "PersonGenerator", 
    "CourseGenerator"
] 