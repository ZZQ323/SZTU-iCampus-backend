"""
数据库模型包
包含所有的SQLAlchemy数据模型定义
"""

# 导入所有模型，确保它们被SQLAlchemy识别
from .base import *
from .person import *
from .organization import *
from .course import *
from .research import *
from .asset import *
from .library import *
from .finance import *
from .permission import *

__all__ = [
    # 基础模型
    "TimestampMixin", "UUIDMixin",
    
    # 人员相关
    "Person", "Class",
    
    # 组织架构
    "College", "Major", "Department", "Location", "RoomOccupation",
    
    # 课程相关
    "Course", "CourseInstance", "Grade", "GradeStatistics",
    
    # 科研相关
    "ResearchProject", "ResearchApplication", "PaperLibrary",
    
    # 资产管理
    "Asset",
    
    # 图书馆
    "Book", "BorrowRecord",
    
    # 财务系统
    "Transaction", "CampusCard",
    
    # 权限管理
    "NetworkPermission", "SystemAccess", "PlatformConfig",
    "AuditLog", "DeviceRegistration", "WorkflowInstance",
] 