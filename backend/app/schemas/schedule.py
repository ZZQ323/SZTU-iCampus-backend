from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScheduleBase(BaseModel):
    course_name: str
    teacher: str
    classroom: str
    week_day: int
    start_time: str
    end_time: str
    weeks: str
    course_type: Optional[str] = "必修"
    credits: Optional[str] = None
    student_id: str
    semester: Optional[str] = "2024春"

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    course_name: Optional[str] = None
    teacher: Optional[str] = None
    classroom: Optional[str] = None
    week_day: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    weeks: Optional[str] = None
    course_type: Optional[str] = None
    credits: Optional[str] = None

class Schedule(ScheduleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 