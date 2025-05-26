from pydantic import BaseModel, ConfigDict


class MatchParticipantBase(BaseModel):
    match_id: int
    user_id: int
    is_winner: bool = False

class MatchParticipantCreate(MatchParticipantBase):
    pass

class MatchParticipantUpdate(BaseModel):
    is_winner: bool

class MatchParticipantRead(BaseModel):
    id: int
    match_id: int
    user_id: int
    is_winner: bool

    model_config = ConfigDict(from_attributes=True)