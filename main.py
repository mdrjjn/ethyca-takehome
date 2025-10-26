from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from database import init_db, get_db, Player, Game, Move
from schemas import (
    PlayerCreate, PlayerResponse, GameCreate, GameResponse,
    MoveCreate, MoveResponse, GameStatusResponse, ActiveGamesResponse,
    MoveHistoryItem, MovesHistoryResponse, GameHistoryItem, AllGamesResponse
)
from game_logic import (
    empty_board, make_move_on_board, check_winner,
    get_current_board, ai_make_move, get_current_turn
)

init_db()

app = FastAPI()

@app.post("/players", response_model=PlayerResponse)
def register_player(player: PlayerCreate, db: Session = Depends(get_db)):
    """Register a new player."""
    db_player = Player(name=player.name)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return PlayerResponse(player_id=db_player.player_id, name=db_player.name)


@app.get("/players/by-name/{name}", response_model=Optional[PlayerResponse])
def get_player_by_name(name: str, db: Session = Depends(get_db)):
    """Get a player by name (for login)."""
    player = db.query(Player).filter(Player.name == name).first()
    if player:
        return PlayerResponse(player_id=player.player_id, name=player.name)
    return None


@app.get("/players/{player_id}/games", response_model=ActiveGamesResponse)
def get_player_games(player_id: int, db: Session = Depends(get_db)):
    """Get all active games for a player."""
    games = db.query(Game).filter(
        Game.status == "progress",
        ((Game.created_by == player_id) | (Game.opponent == str(player_id)))
    ).all()
    
    game_responses = [
        GameResponse(
            game_id=game.game_id,
            created_by=game.created_by,
            opponent=game.opponent,
            status=game.status,
            last_move=game.last_move
        )
        for game in games
    ]
    
    return ActiveGamesResponse(games=game_responses)


@app.get("/players/{player_id}/history", response_model=AllGamesResponse)
def get_player_history(player_id: int, db: Session = Depends(get_db)):
    """Get all games for a player, chronologically ordered."""
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    games = db.query(Game).filter(
        ((Game.created_by == player_id) | (Game.opponent == str(player_id)))
    ).all()
    
    game_items = []
    for game in games:
        first_move = db.query(Move).filter(Move.game_id == game.game_id).order_by(Move.board_id).first()
        
        winner = None
        if game.status == 'done':
            last_move = db.query(Move).filter(Move.game_id == game.game_id).order_by(Move.board_id.desc()).first()
            if last_move:
                winner = check_winner(last_move.board_state)
        
        game_items.append(
            GameHistoryItem(
                game_id=game.game_id,
                created_by=game.created_by,
                opponent=game.opponent,
                status=game.status,
                winner=winner,
                created_at=first_move.move_id if first_move else 0
            )
        )
    
    game_items.sort(key=lambda x: x.created_at)
    
    return AllGamesResponse(games=game_items)



@app.post("/games", response_model=GameResponse)
def create_game(game: GameCreate, db: Session = Depends(get_db)):
    """Create a new game."""
    player = db.query(Player).filter(Player.player_id == game.created_by).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if game.opponent != "AI":
        opponent = db.query(Player).filter(Player.player_id == int(game.opponent)).first()
        if not opponent:
            raise HTTPException(status_code=404, detail="Opponent not found")
    
    new_game = Game(
        created_by=game.created_by,
        opponent=game.opponent,
        status="progress",
        last_move=None
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    
    initial_move = Move(
        game_id=new_game.game_id,
        to_move="initial",
        board_id=0,
        board_state=empty_board()
    )
    db.add(initial_move)
    db.commit()
    
    return GameResponse(
        game_id=new_game.game_id,
        created_by=new_game.created_by,
        opponent=new_game.opponent,
        status=new_game.status,
        last_move=new_game.last_move
    )


@app.get("/games/find", response_model=Optional[GameResponse])
def find_game(player1: int, player2: int, db: Session = Depends(get_db)):
    """Find an existing in-progress game between two players."""
    game = db.query(Game).filter(
        Game.status == "progress",
        ((Game.created_by == player1) & (Game.opponent == str(player2))) |
        ((Game.created_by == player2) & (Game.opponent == str(player1)))
    ).first()
    
    if game:
        return GameResponse(
            game_id=game.game_id,
            created_by=game.created_by,
            opponent=game.opponent,
            status=game.status,
            last_move=game.last_move
        )
    return None


@app.get("/games/{game_id}", response_model=GameStatusResponse)
def get_game_status(game_id: int, db: Session = Depends(get_db)):
    """Get current game status including board state and whose turn it is."""
    game = db.query(Game).filter(Game.game_id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    board = get_current_board(db, game_id)
    
    current_turn = None
    winner = None
    
    if game.status == "progress":
        current_turn = get_current_turn(game, game.last_move)
    else:
        winner = check_winner(board)
    
    return GameStatusResponse(
        game_id=game.game_id,
        created_by=game.created_by,
        opponent=game.opponent,
        status=game.status,
        board_state=board,
        current_turn=current_turn,
        winner=winner
    )


@app.get("/games/{game_id}/moves", response_model=MovesHistoryResponse)
def get_game_moves(game_id: int, db: Session = Depends(get_db)):
    """Get all moves in a game, chronologically ordered."""
    game = db.query(Game).filter(Game.game_id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    moves = db.query(Move).filter(Move.game_id == game_id).order_by(Move.board_id).all()
    
    move_items = [
        MoveHistoryItem(
            move_id=move.move_id,
            move_number=move.board_id,
            player=move.to_move,
            board_state=move.board_state
        )
        for move in moves
    ]
    
    return MovesHistoryResponse(game_id=game_id, moves=move_items)


@app.post("/moves", response_model=MoveResponse)
def make_move(move: MoveCreate, db: Session = Depends(get_db)):
    """Make a move in a game."""
    if move.row < 0 or move.row > 2 or move.col < 0 or move.col > 2:
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    game = db.query(Game).filter(Game.game_id == move.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game.status == 'done':
        raise HTTPException(status_code=400, detail="Game is already complete")
    
    board = get_current_board(db, move.game_id)
    
    current_turn = get_current_turn(game, game.last_move)
    
    if current_turn == "AI":
        raise HTTPException(status_code=400, detail="It's the AI's turn")
    
    if int(current_turn) != move.player_id:
        raise HTTPException(status_code=400, detail="It's not your turn")
    
    if int(current_turn) == game.created_by:
        symbol = 'X'  # Creator is always X
    else:
        symbol = 'O'  # Opponent is always O
    
    try:
        new_board = make_move_on_board(board, move.row, move.col, symbol)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    winner = check_winner(new_board)
    is_done = winner is not None
    
    move_count = db.query(Move).filter(Move.game_id == move.game_id).count()
    new_move = Move(
        game_id=move.game_id,
        to_move=current_turn,
        board_id=move_count,
        board_state=new_board
    )
    db.add(new_move)
    
    game.last_move = int(current_turn)
    if is_done:
        game.status = 'done'
    
    db.commit()
    
    if is_done:
        return MoveResponse(
            move_id=new_move.move_id,
            game_id=move.game_id,
            board_state=new_board,
            to_move=current_turn,
            game_status="done",
            winner=winner if winner != 'TIE' else None
        )
    
    if game.opponent == "AI":
        ai_row, ai_col = ai_make_move(new_board)
        ai_symbol = 'O'
        try:
            ai_board = make_move_on_board(new_board, ai_row, ai_col, ai_symbol)
        except ValueError as e:
            raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")
        
        # Check winner after AI move
        winner = check_winner(ai_board)
        is_done = winner is not None
        
        # Save AI move
        move_count = db.query(Move).filter(Move.game_id == move.game_id).count()
        ai_move = Move(
            game_id=move.game_id,
            to_move="AI",
            board_id=move_count,
            board_state=ai_board
        )
        db.add(ai_move)
        
        # Update game status
        game.last_move = None  # AI doesn't have a player_id
        if is_done:
            game.status = 'done'
        
        db.commit()
        
        return MoveResponse(
            move_id=ai_move.move_id,
            game_id=move.game_id,
            board_state=ai_board,
            to_move="AI",
            game_status="done" if is_done else "progress",
            winner=winner if is_done and winner != 'TIE' else None
        )
    else:
        return MoveResponse(
            move_id=new_move.move_id,
            game_id=move.game_id,
            board_state=new_board,
            to_move=current_turn,
            game_status="progress",
            winner=None
        )


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Tic Tac Toe API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
