from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from pydantic.config import ConfigDict

class MatchParticipantCreate(BaseModel):
    user_id: int
    is_winner: bool = False

class MatchCreate(BaseModel):
    competition_id: int
    date_played: Optional[datetime] = None
    participants: List[MatchParticipantCreate]
    result: Optional[str] = None

class MatchParticipantRead(BaseModel):
    user_id: int
    is_winner: bool

    model_config = ConfigDict(from_attributes=True)

class MatchRead(BaseModel):
    id: int
    competition_id: int
    date_played: datetime
    result: Optional[str]
    participants: List[MatchParticipantRead]

    model_config = ConfigDict(from_attributes=True)

class MatchUpdate(BaseModel):
    competition_id: Optional[int]
    date_played: Optional[datetime]
    result: Optional[str]
    participants: Optional[List[MatchParticipantCreate]]