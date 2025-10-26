∏"""Database models and session management."""
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///./tic_tac_toe.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Player(Base):
    """Player model."""
    __tablename__ = "players"
    
    player_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class Game(Base):
    """Game model."""
    __tablename__ = "games"
    
    game_id = Column(Integer, primary_key=True, index=True)
    created_by = Column(Integer)
    opponent = Column(String)  # "AI" or player_id
    status = Column(String)  # "done" or "progress"
    last_move = Column(Integer)  # player_id who made the last move


class Move(Base):
    """Move model."""
    __tablename__ = "moves"
    
    move_id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, index=True)
    to_move = Column(String)  # player_id or "AI"
    board_id = Column(Integer)  # for ordering moves
    board_state = Column(String)  # "XOXO.OXX." format (9 chars)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

