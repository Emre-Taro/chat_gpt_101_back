from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"

engine = create_engine(DATABASE_URL, echo=True)  # 同期版なら `create_engine`
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally: 
        db.close()
