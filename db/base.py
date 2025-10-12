from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Импортируй модели, чтобы Alembic их «видел»
from models.models import *  # noqa
