"""Pydantic schemas for API request/response models."""
from pydantic import BaseModel
from typing import Optional, List


class PlayerCreate(BaseModel):
    """Player creation request."""
    name: str


class PlayerResponse(BaseModel):
    """Player response."""
    player_id: int
    name: str


class GameCreate(BaseModel):
    """Game creation request."""
    created_by: int
    opponent: str  # "AI" or player_id


class GameResponse(BaseModel):
    """Game response."""
    game_id: int
    created_by: int
    opponent: str
    status: str
    last_move: Optional[int] = None


class MoveCreate(BaseModel):
    """Move creation request."""
    game_id: int
    player_id: int
    row: int
    col: int


class MoveResponse(BaseModel):
    """Move response."""
    move_id: int
    game_id: int
    board_state: str
    to_move: str
    game_status: str
    winner: Optional[str] = None


class GameStatusResponse(BaseModel):
    """Game status response."""
    game_id: int
    created_by: int
    opponent: str
    status: str
    board_state: str
    current_turn: Optional[str] = None
    winner: Optional[str] = None


class ActiveGamesResponse(BaseModel):
    """Active games response."""
    games: List[GameResponse]


class MoveHistoryItem(BaseModel):
    """Single move in history."""
    move_id: int
    move_number: int
    player: str  # player_id or "AI" or "initial"
    board_state: str


class MovesHistoryResponse(BaseModel):
    """Moves history response."""
    game_id: int
    moves: List[MoveHistoryItem]


class GameHistoryItem(BaseModel):
    """Single game in history."""
    game_id: int
    created_by: int
    opponent: str
    status: str
    winner: Optional[str] = None
    created_at: int  # Move ID of first move (for ordering)


class AllGamesResponse(BaseModel):
    """All games response."""
    games: List[GameHistoryItem]

