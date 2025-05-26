from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models.competition import Competition
from app.schemas.competition import CompetitionCreate, CompetitionUpdate, CompetitionRead

router = APIRouter(prefix="/competitions", tags=["Competitions"])

@router.post("/", response_model=CompetitionRead)
def create_competition(data: CompetitionCreate, db: Session = Depends(get_db)):
    competition = Competition(**data.model_dump())
    db.add(competition)
    db.commit()
    db.refresh(competition)
    return competition


@router.get("/", response_model=List[CompetitionRead])
def list_competitions(db: Session = Depends(get_db)):
    return db.query(Competition).all()


@router.get("/{competition_id}", response_model=CompetitionRead)
def get_competition(competition_id: int, db: Session = Depends(get_db)):
    comp = db.query(Competition).filter_by(id=competition_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    return comp

@router.put("/{competition_id}", response_model=CompetitionRead)
def update_competition(competition_id: int, data: CompetitionUpdate, db: Session = Depends(get_db)):
    comp = db.query(Competition).filter_by(id=competition_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(comp, field, value)

    db.commit()
    db.refresh(comp)
    return comp

@router.delete("/{competition_id}")
def delete_competition(competition_id: int, db: Session = Depends(get_db)):
    comp = db.query(Competition).filter_by(id=competition_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    db.delete(comp)
    db.commit()
    return {"detail": "Competition deleted"}