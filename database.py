from sqlalchemy import Column, Integer, LargeBinary, DateTime, func, Float, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class database:
    def __init__(self):
        engine = sqlalchemy.create_engine(
            os.getenv("sqlite:///./test.db"), pool_pre_ping=True
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()

   