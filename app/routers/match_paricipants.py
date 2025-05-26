from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models.match_participants import MatchParticipant
from app.schemas.match_participant import (
    MatchParticipantCreate,
    MatchParticipantRead,
    MatchParticipantUpdate
)

router = APIRouter(prefix="/match-participants", tags=["Match Participants"])

@router.post("/", response_model=MatchParticipantRead)
def create_match_participant(data: MatchParticipantCreate, db: Session = Depends(get_db)):
    participant = MatchParticipant(**data.model_dump())
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant

@router.get("/", response_model=List[MatchParticipantRead])
def list_match_participants(db: Session = Depends(get_db)):
    return db.query(MatchParticipant).all()

@router.get("/{participant_id}", response_model=MatchParticipantRead)
def get_match_participant(participant_id: int, db: Session = Depends(get_db)):
    participant = db.query(MatchParticipant).filter_by(id=participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Match participant not found")
    return participant

@router.put("/{participant_id}", response_model=MatchParticipantRead)
def update_match_participant(participant_id: int, data: MatchParticipantUpdate, db: Session = Depends(get_db)):
    participant = db.query(MatchParticipant).filter_by(id=participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Match participant not found")
    participant.is_winner = data.is_winner
    db.commit()
    db.refresh(participant)
    return participant

@router.delete("/{participant_id}")
def delete_match_participant(participant_id: int, db: Session = Depends(get_db)):
    participant = db.query(MatchParticipant).filter_by(id=participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Match participant not found")
    db.delete(participant)
    db.commit()
    return {"detail": "Match participant deleted"}