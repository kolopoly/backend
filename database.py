import os
import sqlalchemy
from sqlalchemy import Column, Integer, LargeBinary, DateTime, func, Float, String, ForeignKey, Boolean, JSON
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Session, mapped_column, Mapped, relationship


class Base(DeclarativeBase):
    pass


from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

# Association table for the many-to-many relationship between Game and Player
association_game_player = Table('Game_Player', Base.metadata,
    Column('game_id', Integer, ForeignKey('Game.id')),
    Column('player_id', Integer, ForeignKey('Player.id'))
)

class Game_db(Base):
    __tablename__ = "Game"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    state = Column(String, default="pending")
    public = Column(Boolean, default=False)
    rules_id = Column(Integer, ForeignKey('Rules.id'), default=None)

    player_ids = Column(JSON)
    # Relationship with Player (many-to-many)
    players = relationship("Player_db", secondary=association_game_player, back_populates="games")


class Rules_db(Base):
    __tablename__ = "Rules"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    rules_json = Column(String)

    # Foreign key to connect with Player table
    owner_id = Column(Integer, ForeignKey('Player.id'))
    owner = relationship("Player_db")

    public = Column(Boolean)


class Player_db(Base):
    __tablename__ = "Player"

    id = Column(Integer, primary_key=True)
    nickname = Column(String)

    total_games = Column(Integer)
    total_wins = Column(Integer)

    # Relationship with Game (many-to-many)
    games = relationship("Game_db", secondary=association_game_player, back_populates="players")


game_db_engine = sqlalchemy.create_engine("sqlite:///test_game_1.db")    

def create_game_db():
    Base.metadata.create_all(game_db_engine)

def drop_game_db():
    Base.metadata.drop_all(bind=game_db_engine)
    
def add_game_db(game_db: Game_db):
    with Session(game_db_engine) as session:
        try:
            session.add(game_db)
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"Game with ID {game_db.id} already exists.")
        
def get_game_db(game_id: int) -> Game_db:
    with Session(game_db_engine) as session:
        return session.query(Game_db).filter(Game_db.id == game_id).first()


# drop_game_db()
create_game_db()
add_game_db(Game_db(id=1, name="test_game"))
print(get_game_db(1).name)
        