"""
数据库初始化模块
用于创建数据库表和基础数据
"""

import logging
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401
from app.models.user import User
from app.models.announcement import Announcement
from app.database import engine, Base

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """
    初始化数据库
    创建超级管理员和基础测试数据
    """
    # 创建超级管理员
    user = crud.user.get_by_student_id(db, student_id=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            student_id=settings.FIRST_SUPERUSER,
            email="admin@example.com",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Admin",
            is_superuser=True,
        )
        user = crud.user.create(db, obj_in=user_in)
        logger.info("Initial superuser created")

    # 添加测试公告数据
    announcements_data = [
        {
            "title": "关于2024年春季学期开学安排的通知",
            "content": "各位同学：\n\n根据学校安排，2024年春季学期将于2月26日正式开学。请同学们做好返校准备，具体安排如下：\n\n1. 返校时间：2月24日-25日\n2. 健康检查：返校前需完成健康申报\n3. 宿舍安排：保持原宿舍分配\n\n祝大家新学期学习进步！",
            "department": "教务处"
        },
        {
            "title": "图书馆开放时间调整通知",
            "content": "亲爱的读者：\n\n图书馆开放时间调整如下：\n\n周一至周五：8:00-22:00\n周六至周日：9:00-21:00\n\n请广大师生合理安排学习时间。",
            "department": "图书馆"
        },
        {
            "title": "校园网络维护通知",
            "content": "各位师生：\n\n为提升校园网络服务质量，信息中心将于本周六（3月2日）凌晨2:00-6:00进行网络设备维护升级。\n\n维护期间校园网将暂时中断，请提前做好相关准备。",
            "department": "信息中心"
        }
    ]
    
    # 检查是否已有公告数据，如果没有则添加
    existing_announcements = db.query(Announcement).count()
    if existing_announcements == 0:
        for ann_data in announcements_data:
            announcement = Announcement(**ann_data)
            db.add(announcement)
        db.commit()
        logger.info("Test announcements created")

def create_tables():
    """
    创建所有数据库表
    """
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("数据库表创建完成！") 