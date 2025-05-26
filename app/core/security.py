from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.refresh import RefreshToken


SECRET_KEY = 'some_secret'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_TIME = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hashed(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta |  None = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username:str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username==username).first()

    if user is None:
        raise credentials_exception
    return user



def revoke_refresh_token(db: Session, refresh_token: str):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not db_token or db_token.revoked:
        raise HTTPException(status_code=404, detail="Token not found or already revoked")

    db_token.revoked = True
    db_token.revoked_at = datetime.utcnow()
    db.commit()
    return db_token


def issue_refresh_token(db: Session, username: str):
    token_data = {"sub": username, "type": "refresh"}
    refresh_token = create_refresh_token(token_data)

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        revoked=False
    )
    db.add(db_token)
    db.commit()

    return refresh_token