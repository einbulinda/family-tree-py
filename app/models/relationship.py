from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True)
    individual_id = Column(Integer, ForeignKey("individuals.id", ondelete="CASCADE"))
    related_individual_id = Column(Integer, ForeignKey("individuals.id", ondelete="CASCADE"))
    relationship_type = Column(String(50), nullable=False)  # parent, child, spouse

    created_at = Column(DateTime, server_default=func.now())

    # ORM relations (optional)
    individual = relationship("Individual", foreign_keys=[individual_id])
    related_individual = relationship("Individual", foreign_keys=[related_individual_id])