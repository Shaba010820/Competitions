from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models.discipline import Discipline
from app.schemas.discipline import DisciplineCreate, DisciplineRead, DisciplineUpdate

router = APIRouter(prefix="/disciplines", tags=["Disciplines"])

@router.post("/", response_model=DisciplineRead)
def create_discipline(data: DisciplineCreate, db: Session = Depends(get_db)):
    existing = db.query(Discipline).filter_by(name=data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Discipline already exists")
    discipline = Discipline(**data.dict())
    db.add(discipline)
    db.commit()
    db.refresh(discipline)
    return discipline

@router.get("/", response_model=List[DisciplineRead])
def list_disciplines(db: Session = Depends(get_db)):
    return db.query(Discipline).all()

@router.get("/{discipline_id}", response_model=DisciplineRead)
def get_discipline(discipline_id: int, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter_by(id=discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return discipline

@router.put("/{discipline_id}", response_model=DisciplineRead)
def update_discipline(discipline_id: int, data: DisciplineUpdate, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter_by(id=discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    discipline.name = data.name
    db.commit()
    db.refresh(discipline)
    return discipline

@router.delete("/{discipline_id}")
def delete_discipline(discipline_id: int, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter_by(id=discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    db.delete(discipline)
    db.commit()
    return {"detail": "Discipline deleted"}