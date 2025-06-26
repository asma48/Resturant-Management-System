from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from app.models.database_models import Base


DATABASE_URL = 'postgresql://postgres:asma12@localhost:5432/Resturant'

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
 
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

