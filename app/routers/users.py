from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .elastic_search import index_user_in_elastic
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix='/users', tags=['Users'])


@router.post('/', response_model=UserRead)
def create_user(user_data: UserCreate, db:Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail='Username or email already exists')

    user = User(**user_data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    try:
        index_user_in_elastic(user)
    except Exception as e:
        print(f"Ошибка отправки в Elasticsearch: {e}")

    return user

@router.get('/', response_model=list[UserRead])
def get_users(db:Session = Depends(get_db)):
    return db.query(User).all()


@router.put('/user_id', response_model=UserRead)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id==user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    if user_data.username is not None:
        user.username = user_data.username

    if user_data.email is not None:
        user.email = user_data.email

    db.commit()
    db.refresh(user)

    return user

@router.delete('/{user_id}', response_model=UserRead)
def delete_user(user_id:int, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    db.delete(user)
    db.commit()

    return user
