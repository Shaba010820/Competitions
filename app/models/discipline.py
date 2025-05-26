from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base

class Discipline(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    competitions = relationship("Competition", back_populates="discipline", cascade="all, delete")
