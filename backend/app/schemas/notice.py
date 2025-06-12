from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class NoticeType(str, Enum):
    URGENT = "urgent"
    NORMAL = "normal"
    INFO = "info"

class NoticePriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class NoticeBase(BaseModel):
    title: str
    content: str
    department: str
    notice_type: Optional[NoticeType] = NoticeType.NORMAL
    priority: Optional[NoticePriority] = NoticePriority.MEDIUM
    target_audience: Optional[str] = None
    effective_date: Optional[datetime] = None
    expire_date: Optional[datetime] = None
    is_active: Optional[int] = 1

class NoticeCreate(NoticeBase):
    pass

class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    department: Optional[str] = None
    notice_type: Optional[NoticeType] = None
    priority: Optional[NoticePriority] = None
    target_audience: Optional[str] = None
    effective_date: Optional[datetime] = None
    expire_date: Optional[datetime] = None
    is_active: Optional[int] = None

class Notice(NoticeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 