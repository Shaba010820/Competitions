from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from pydantic.config import ConfigDict

class CompetitionCreate(BaseModel):
    name: str
    discipline_id: int
    start_date: Optional[datetime] = None


class CompetitionUpdate(BaseModel):
    name: Optional[str] = None
    discipline_id: Optional[int] = None
    start_date: Optional[datetime] = None

class CompetitionRead(BaseModel):
    id: int
    name: str
    discipline_id: int
    start_date: datetime

    model_config = ConfigDict(from_attributes=True)