from pydantic import BaseModel, ConfigDict


class DisciplineCreate(BaseModel):
    name: str

class DisciplineUpdate(BaseModel):
    name: str

class DisciplineRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

