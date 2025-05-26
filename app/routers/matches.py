from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.match import MatchCreate, MatchRead, MatchUpdate
from app.models import match as match_model
from app.models import match_participants as mp_model
from app.database.session import get_db

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get('/', response_model=list[MatchRead])
def list_matches(db: Session = Depends(get_db)):
    return db.query(match_model.Match).all()

@router.get('/{match_id}', response_model=MatchRead)
def get_match(match_id:int, db: Session = Depends(get_db)):
    match = db.query(match_model.Match).filter(match_id==match_model.Match.id).first()
    if not match:
        raise HTTPException(status_code=404, detail='match not found')
    return match


@router.put("/{match_id}", response_model=MatchRead)
def update_match(match_id: int, match_data: MatchUpdate, db: Session = Depends(get_db)):
    match = db.query(match_model.Match).filter_by(id=match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match_data.competition_id is not None:
        match.competition_id = match_data.competition_id
    if match_data.date_played is not None:
        match.date_played = match_data.date_played
    if match_data.result is not None:
        match.result = match_data.result

    if match_data.participants is not None:
        db.query(mp_model.MatchParticipant).filter_by(match_id=match_id).delete()
        participants = [
            mp_model.MatchParticipant(
                match_id=match.id,
                user_id=p.user_id,
                is_winner=p.is_winner
            ) for p in match_data.participants
        ]
        db.add_all(participants)

    db.commit()
    db.refresh(match)
    return match


@router.post("/", response_model=MatchRead)
def create_match(match_data: MatchCreate, db: Session = Depends(get_db)):
    match = match_model.Match(
        competition_id=match_data.competition_id,
        date_played=match_data.date_played,
        result=match_data.result,
    )
    db.add(match)
    db.flush()

    participants = [
        mp_model.MatchParticipant(
            match_id=match.id,
            user_id=p.user_id,
            is_winner=p.is_winner
        ) for p in match_data.participants
    ]

    db.add_all(participants)
    db.commit()
    db.refresh(match)
    return match


@router.delete("/{match_id}")
def delete_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(match_model.Match).filter_by(id=match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    db.delete(match)
    db.commit()
    return {"detail": "Match deleted"}
