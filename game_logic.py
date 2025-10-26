"""Game logic functions for tic-tac-toe."""
from typing import Optional
import random
from sqlalchemy.orm import Session
from database import Game, Move


def empty_board() -> str:
    """Returns empty board representation."""
    return "." * 9


def get_board_position(row: int, col: int) -> int:
    """Convert row,col to board index (0-8)."""
    return row * 3 + col


def make_move_on_board(board: str, row: int, col: int, symbol: str) -> str:
    """Make a move on the board."""
    pos = get_board_position(row, col)
    if board[pos] != '.':
        raise ValueError("Invalid move: position already taken")
    return board[:pos] + symbol + board[pos+1:]


def check_winner(board: str) -> Optional[str]:
    """Check if there's a winner. Returns 'X', 'O', 'TIE', or None."""
    # Check rows
    for i in range(0, 9, 3):
        if board[i] != '.' and board[i] == board[i+1] == board[i+2]:
            return board[i]
    
    # Check columns
    for i in range(3):
        if board[i] != '.' and board[i] == board[i+3] == board[i+6]:
            return board[i]
    
    # Check diagonals
    if board[0] != '.' and board[0] == board[4] == board[8]:
        return board[0]
    if board[2] != '.' and board[2] == board[4] == board[6]:
        return board[2]
    
    # Check for tie
    if '.' not in board:
        return 'TIE'
    
    return None


def get_current_board(db: Session, game_id: int) -> str:
    """Get the current board state for a game."""
    moves = db.query(Move).filter(Move.game_id == game_id).order_by(Move.board_id).all()
    if moves:
        return moves[-1].board_state
    return empty_board()


def _find_winning_move(board: str, symbol: str) -> Optional[int]:
    """Find a winning move for the given symbol."""
    for i in range(9):
        if board[i] == '.':
            # Try this move
            test_board = board[:i] + symbol + board[i+1:]
            if check_winner(test_board) == symbol:
                return i
    return None


def ai_make_move(board: str) -> tuple[int, int]:
    """Strategic AI: tries to win, block, or make smart moves."""
    available = [i for i in range(9) if board[i] == '.']
    if not available:
        return None, None
    
    # 1. Try to win
    winning_move = _find_winning_move(board, 'O')
    if winning_move is not None:
        return winning_move // 3, winning_move % 3
    
    # 2. Block opponent from winning
    blocking_move = _find_winning_move(board, 'X')
    if blocking_move is not None:
        return blocking_move // 3, blocking_move % 3
    
    # 3. Take center if available
    if board[4] == '.':
        return 1, 1
    
    # 4. Take a corner (strategic positions)
    corners = [0, 2, 6, 8]
    available_corners = [c for c in corners if board[c] == '.']
    if available_corners:
        move = random.choice(available_corners)
        return move // 3, move % 3
    
    # 5. Take any remaining edge
    move = random.choice(available)
    return move // 3, move % 3


def get_current_turn(game: Game, last_move: Optional[int]) -> str:
    """Determine whose turn it is."""
    if game.status == 'done':
        return None
    
    if last_move is None:
        return str(game.created_by)  # First move by creator
    
    if int(last_move) == game.created_by:
        return game.opponent
    else:
        return str(game.created_by)

