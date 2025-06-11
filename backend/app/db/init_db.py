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

def init_db():
    # 创建所有表
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("数据库初始化完成！") 