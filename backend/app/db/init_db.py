import logging
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401

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