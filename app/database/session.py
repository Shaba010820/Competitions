from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL="postgresql+psycopg2://admin:secret@postgres:5432/app_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False,  bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


