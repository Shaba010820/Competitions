from sqlalchemy.orm import relationship

from .base import Base
from sqlalchemy import String, Integer, Column, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    email:Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password:Mapped[str] = mapped_column(String, nullable=True)

    participations = relationship("MatchParticipant", back_populates="user", cascade="all, delete")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete")

