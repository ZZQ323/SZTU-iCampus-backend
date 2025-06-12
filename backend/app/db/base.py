# Import all the models, so that Base has them before being
# imported by Alembic
from app.database import Base  # noqa
from app.models.user import User  # noqa
from app.models.announcement import Announcement  # noqa
from app.models.schedule import Schedule  # noqa 