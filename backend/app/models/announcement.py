# 所有模型都继承自 Base，这样 Base.metadata 就能收集所有表的信息
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base

class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    department = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 

