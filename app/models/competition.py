from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"))
    start_date = Column(DateTime, default=datetime.now)

    discipline = relationship("Discipline")
    matches = relationship("Match", back_populates="competition", cascade="all, delete")