from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    ACADEMIC = "academic"
    SOCIAL = "social"
    SPORTS = "sports"
    CULTURAL = "cultural"
    COMPETITION = "competition"

class EventStatus(str, Enum):
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EventBase(BaseModel):
    title: str
    description: str
    organizer: str
    event_type: EventType
    status: Optional[EventStatus] = EventStatus.UPCOMING
    location: str
    start_time: datetime
    end_time: datetime
    registration_deadline: Optional[datetime] = None
    max_participants: Optional[int] = None
    current_participants: Optional[int] = 0
    contact_info: Optional[str] = None
    requirements: Optional[str] = None
    is_active: Optional[int] = 1

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    organizer: Optional[str] = None
    event_type: Optional[EventType] = None
    status: Optional[EventStatus] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    max_participants: Optional[int] = None
    current_participants: Optional[int] = None
    contact_info: Optional[str] = None
    requirements: Optional[str] = None
    is_active: Optional[int] = None

class Event(EventBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 