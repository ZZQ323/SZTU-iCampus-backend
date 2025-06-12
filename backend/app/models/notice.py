from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from datetime import datetime
from app.database import Base
import enum

class NoticeType(enum.Enum):
    URGENT = "urgent"      # 紧急通知
    NORMAL = "normal"      # 普通通知
    INFO = "info"         # 信息通知

class NoticePriority(enum.Enum):
    HIGH = "high"         # 高优先级
    MEDIUM = "medium"     # 中优先级
    LOW = "low"          # 低优先级

class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=False, comment="通知内容")
    department = Column(String(100), nullable=False, comment="发布部门")
    notice_type = Column(Enum(NoticeType), default=NoticeType.NORMAL, comment="通知类型")
    priority = Column(Enum(NoticePriority), default=NoticePriority.MEDIUM, comment="优先级")
    target_audience = Column(String(200), comment="目标受众")
    effective_date = Column(DateTime, comment="生效日期")
    expire_date = Column(DateTime, comment="过期日期")
    is_active = Column(Integer, default=1, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 