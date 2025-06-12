from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from datetime import datetime
from app.database import Base
import enum

class EventType(enum.Enum):
    ACADEMIC = "academic"        # 学术活动
    SOCIAL = "social"           # 社团活动
    SPORTS = "sports"           # 体育活动
    CULTURAL = "cultural"       # 文化活动
    COMPETITION = "competition" # 比赛活动

class EventStatus(enum.Enum):
    UPCOMING = "upcoming"       # 即将开始
    ONGOING = "ongoing"         # 进行中
    COMPLETED = "completed"     # 已结束
    CANCELLED = "cancelled"     # 已取消

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="活动标题")
    description = Column(Text, nullable=False, comment="活动描述")
    organizer = Column(String(100), nullable=False, comment="主办方")
    event_type = Column(Enum(EventType), nullable=False, comment="活动类型")
    status = Column(Enum(EventStatus), default=EventStatus.UPCOMING, comment="活动状态")
    location = Column(String(200), nullable=False, comment="活动地点")
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")
    registration_deadline = Column(DateTime, comment="报名截止时间")
    max_participants = Column(Integer, comment="最大参与人数")
    current_participants = Column(Integer, default=0, comment="当前参与人数")
    contact_info = Column(String(200), comment="联系方式")
    requirements = Column(Text, comment="参与要求")
    is_active = Column(Integer, default=1, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间") 