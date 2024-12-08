from datetime import datetime, UTC
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

from config import Config

class Base(DeclarativeBase):
    """Base class for declarative models"""
    pass

class Game(Base):
    __tablename__ = 'games'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()), unique=True, nullable=False)
    createdat = Column(DateTime, default=datetime.now(UTC), nullable=False)
    winner = Column(Enum('X', 'O', 'Tie', name='game_winner'), nullable=True)
    game_type = Column(Enum('TicTacToe', 'Connect4', name='game_type'), nullable=False)

    moves = relationship('Move', back_populates='game', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Game(id='{self.id}', createdat='{self.createdat}', game_type='{self.game_type}')>"


class Move(Base):
    __tablename__ = 'moves'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()), unique=True, nullable=False)
    game_id = Column(String(36), ForeignKey('games.id'), nullable=False)
    player = Column(Enum('X', 'O', name='player_move'), nullable=False)
    row = Column(Integer, nullable=False)
    col = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(UTC), nullable=False)

    game = relationship('Game', back_populates='moves')
    
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)