# 导入所有模型，确保Alembic可以识别
from app.database import Base
from app.models.user import User
from app.models.announcement import Announcement
from app.models.schedule import Schedule