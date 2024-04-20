import os
import sqlalchemy
from sqlalchemy import Column, Integer, LargeBinary, DateTime, func, Float, String
from sqlalchemy.orm import DeclarativeBase, Session, mapped_column, Mapped

class Base(DeclarativeBase):
    pass

class Game_db(Base):
    __tablename__ = "Game"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    

game_db_engine = sqlalchemy.create_engine("sqlite:///test_game_1.db")    

def create_game_db():
    Base.metadata.create_all(game_db_engine)
    
def add_game_db(game_db: Game_db):
    with Session(game_db_engine) as session:
        session.add(game_db)
        session.commit()
        
def get_game_db(game_id: int) -> Game_db:
    with Session(game_db_engine) as session:
        return session.query(Game_db).filter(Game_db.id == game_id).first()

create_game_db()
# add_game_db(Game_db(id=1, name="test_game"))
# print(get_game_db(1).name)
        