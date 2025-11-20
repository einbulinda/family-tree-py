from sqlalchemy import Column, Integer, String, Boolean, Text,Date, TIMESTAMP
from sqlalchemy.sql import func
from app.models.base import Base

class Individual(Base):
    __tablename__ = "individuals"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    gender = Column(String(20), nullable=False)
    birth_date = Column(Date, nullable=True)
    death_date = Column(Date, nullable=True)
    is_alive = Column(Boolean, default=True)
    bio = Column(Text, nullable=True)
    photo_url = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
