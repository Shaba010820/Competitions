from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileCreate, UserProfileRead, UserProfileUpdate

router = APIRouter(prefix="/profiles", tags=["User Profiles"])

@router.post("/{user_id}", response_model=UserProfileRead)
def create_profile(user_id: int, data: UserProfileCreate, db: Session = Depends(get_db)):
    if db.query(UserProfile).filter_by(user_id=user_id).first():
        raise HTTPException(status_code=400, detail="Profile already exists")
    profile = UserProfile(user_id=user_id, **data.dict())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/{user_id}", response_model=UserProfileRead)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter_by(user_id=user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/{user_id}", response_model=UserProfileRead)
def update_profile(user_id: int, data: UserProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter_by(user_id=user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for key, value in data.model_dump().items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile