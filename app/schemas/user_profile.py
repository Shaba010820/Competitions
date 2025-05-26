from pydantic import BaseModel, ConfigDict


class UserProfileBase(BaseModel):
    bio: str = ""
    country: str = ""
    avatar_url: str | None = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileRead(UserProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)