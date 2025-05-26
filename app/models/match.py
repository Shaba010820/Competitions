from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"))
    result = Column(String)
    date_played = Column(DateTime, default=datetime.utcnow)

    competition = relationship("Competition", back_populates="matches")
    participants = relationship("MatchParticipant", back_populates="match", cascade="all, delete")