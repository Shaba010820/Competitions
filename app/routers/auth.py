from fastapi import status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, Token, TokenRefresh
from app.core.security import get_password_hashed, verify_password, create_access_token, decode_token
from datetime import timedelta, datetime
from app.models.refresh import RefreshToken
from app.core.security import issue_refresh_token, revoke_refresh_token, get_current_user


router = APIRouter(prefix='/auth', tags=['Auth'])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


@router.post("/revoke")
def revoke_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    revoke_refresh_token(db, token_data.refresh_token)
    return {"detail": "Refresh token revoked successfully"}




@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    revoke_refresh_token(db, refresh_token)
    return {"message": "Logged out and token revoked"}


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=user_data.username,
        email=user_data.email,
        password=get_password_hashed(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token_data = {"sub": user.username}
    refresh_token = issue_refresh_token(db, user.username)

    return {
        "access_token": create_access_token(token_data),
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token_data = {"sub": user.username}
    refresh_token = issue_refresh_token(db, user.username)

    return {
        "access_token": create_access_token(token_data),
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    payload = decode_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    db_token = db.query(RefreshToken).filter(RefreshToken.token == token_data.refresh_token).first()
    if not db_token or db_token.revoked:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")

    access_token = create_access_token({"sub": username})
    new_refresh_token = issue_refresh_token(db, username)

    db_token.revoked = True
    db_token.revoked_at = datetime.now()
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }
