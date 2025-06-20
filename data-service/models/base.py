"""
基础数据模型
包含通用的Mixin类和基础字段定义
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from database import Base


class TimestampMixin:
    """时间戳混入类，提供创建时间和更新时间字段"""
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )


class UUIDMixin:
    """UUID混入类，提供UUID主键字段"""
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        comment="UUID主键"
    )


class SoftDeleteMixin:
    """软删除混入类，提供逻辑删除功能"""
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已删除"
    )
    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="删除时间"
    )


class StatusMixin:
    """状态混入类，提供通用状态字段"""
    
    status = Column(
        String(20),
        default="active",
        nullable=False,
        comment="状态"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )


class NotesMixin:
    """备注混入类，提供备注字段"""
    
    notes = Column(
        Text,
        nullable=True,
        comment="备注信息"
    )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin, StatusMixin, NotesMixin):
    """
    基础模型类
    包含所有通用字段的抽象基类
    """
    __abstract__ = True
    
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )
    
    def to_dict(self) -> dict:
        """
        将模型转换为字典
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: dict) -> None:
        """
        从字典更新模型属性
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def get_table_name(cls) -> str:
        """
        获取表名
        """
        return cls.__tablename__
    
    @classmethod
    def get_columns(cls) -> list:
        """
        获取所有列名
        """
        return [column.name for column in cls.__table__.columns]
    
    def __repr__(self) -> str:
        """
        字符串表示
        """
        return f"<{self.__class__.__name__}(id={self.id})>"


# 枚举值定义

# 人员类型枚举
PERSON_TYPES = [
    "student",              # 学生
    "teacher",              # 教师
    "assistant_teacher",    # 助教
    "counselor",           # 辅导员
    "class_advisor",       # 班主任
    "department_head",     # 部门主管
    "dean",                # 院长
    "major_director",      # 专业主任
    "admin",               # 系统管理员
    "security",            # 保卫人员
    "librarian",           # 图书管理员
]

# 性别枚举
GENDERS = ["male", "female", "other"]

# 学籍状态枚举
ACADEMIC_STATUSES = [
    "active",              # 在读
    "suspended",           # 休学
    "graduated",           # 已毕业
    "dropout",             # 退学
    "transfer_in",         # 转入
    "transfer_out",        # 转出
]

# 就职状态枚举
EMPLOYMENT_STATUSES = [
    "active",              # 在职
    "probation",           # 试用期
    "leave",               # 请假
    "retired",             # 退休
    "resigned",            # 离职
    "transfer",            # 调动
]

# 课程类型枚举
COURSE_TYPES = [
    "required",            # 必修课
    "elective",            # 选修课
    "practice",            # 实践课
    "experiment",          # 实验课
    "thesis",              # 毕业设计
    "internship",          # 实习
]

# 考试形式枚举
EXAM_FORMS = [
    "closed_book",         # 闭卷考试
    "open_book",           # 开卷考试
    "online",              # 在线考试
    "oral",                # 口试
    "presentation",        # 答辩
    "project",             # 项目作业
]

# 成绩等第枚举
GRADE_LEVELS = ["A", "B", "C", "D", "E", "F", "P", "NP"]

# 资产状态枚举
ASSET_STATUSES = [
    "in_use",              # 使用中
    "maintenance",         # 维修中
    "idle",                # 闲置
    "scrapped",            # 已报废
    "lost",                # 丢失
]

# 教室类型枚举
ROOM_TYPES = [
    "classroom",           # 普通教室
    "lab",                 # 实验室
    "computer_lab",        # 机房
    "language_lab",        # 语音室
    "multimedia",          # 多媒体教室
    "lecture_hall",        # 阶梯教室
    "office",              # 办公室
    "conference",          # 会议室
    "library",             # 图书馆
    "canteen",             # 食堂
    "dormitory",           # 宿舍
    "gym",                 # 体育馆
]

# 网络类型枚举
NETWORK_TYPES = [
    "campus_wifi",         # 校园WiFi
    "dormitory_network",   # 宿舍网络
    "lab_network",         # 实验室网络
]

# 设备类型枚举
DEVICE_TYPES = [
    "mobile",              # 手机
    "laptop",              # 笔记本
    "desktop",             # 台式机
    "tablet",              # 平板
]

# 交易类型枚举
TRANSACTION_TYPES = [
    "consumption",         # 消费
    "recharge",            # 充值
    "refund",              # 退款
    "transfer",            # 转账
    "subsidy",             # 补助
]

# 支付方式枚举
PAYMENT_METHODS = [
    "campus_card",         # 校园卡
    "wechat",              # 微信支付
    "alipay",              # 支付宝
    "cash",                # 现金
    "bank_card",           # 银行卡
]

# 系统代码枚举
SYSTEM_CODES = [
    "EMS",                 # 教务管理系统
    "RMS",                 # 科研管理平台
    "AMS",                 # 资产管理平台
    "LMS",                 # 图书馆管理系统
    "CMS",                 # 校园卡管理系统
]

# 项目类型枚举
PROJECT_TYPES = [
    "vertical",            # 纵向项目
    "horizontal",          # 横向项目
    "internal",            # 校内项目
    "international",       # 国际合作项目
]

# 项目级别枚举
PROJECT_LEVELS = [
    "national",            # 国家级
    "provincial",          # 省级
    "municipal",           # 市级
    "university",          # 校级
    "department",          # 院级
]

# 论文类型枚举
THESIS_TYPES = [
    "journal",             # 期刊论文
    "conference",          # 会议论文
    "patent",              # 专利
    "thesis",              # 学位论文
    "report",              # 研究报告
]

# 期刊级别枚举
JOURNAL_LEVELS = [
    "SCI",                 # SCI期刊
    "EI",                  # EI期刊
    "CSCD",                # CSCD期刊
    "核心",                # 核心期刊
    "普通",                # 普通期刊
]

# 常用状态值
COMMON_STATUSES = [
    "active",              # 活跃/正常
    "inactive",            # 非活跃
    "pending",             # 等待中
    "approved",            # 已批准
    "rejected",            # 已拒绝
    "suspended",           # 暂停
    "completed",           # 已完成
    "cancelled",           # 已取消
    "expired",             # 已过期
    "locked",              # 已锁定
] 