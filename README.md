# Tic Tac Toe API

A FastAPI-based tic-tac-toe game with AI opponent support, multiplayer capability, and an interactive CLI client.

## Table of Contents
- [How to Run](#how-to-run)
- [Writeup](#writeup)
  - [Tech Stack](#tech-stack)
  - [Notable Features](#notable-features)
  - [Assumptions and Tradeoffs](#assumptions-and-tradeoffs)
  - [Where I used AI](#where-i-used-ai)
  - [Time Spent](#time-spent)
  - [Feedback](#feedback)
- [Technical Documentation](#technical-documentation)
  - [CLI Client Features](#cli-client-features)
  - [API Endpoints](#api-endpoints)
  - [Testing with curl](#testing-with-curl)
  - [Code Structure](#code-structure)
  - [Database](#database)

## How to Run

### 1. Install Dependencies
```bash
uv sync
```

### 2. Start the Server
```bash
uv run python main.py
```

The API will be available at `http://localhost:8000`  
API documentation at `http://localhost:8000/docs`

### 3. Play the Game
Use the interactive CLI client:
```bash
uv run python client.py
```

### 4. Run Tests (Optional)
```bash
uv run pytest
```

## Writeup

Thank you for the fun take home, y'all. With the open ended nature of it this really felt like a playful weekend project more than an assignment.

I would say the main theme here is that I took this in the direction of a player vs player game, with the basic project description serving more as a foundation than the main course of the project as the default requirements were fairly straightforward. The PvP nature of it allowed me to also work on another core addition to the project which is the CLI client. I think this direction is also indicative of what I enjoy most about software development - thinking how it would be as an end to end user experience for real people as opposed to just an API. With that being the intro, here are some of the points I think are worth talking about:


### Tech Stack

- **uv**: maybe not yet the standard but probably will be very soon. no need for pip and venv!!
- **FastAPI**: My tool of choice for setting up the API mostly due to how lightweight and intuitive it is.
- **SQLite**: simplest database. Storing this in memory would be an option as well but I feel like adding a persistent storage makes it more robust.

### Notable Features

**Player Vs Player Multiplayer**
- Play against other humans, not just AI
- Automatic game discovery between players
- Real-time polling to detect opponent moves
- Multiple concurrent games per player

**Interactive Live CLI Client**
- Full-featured command-line interface
- Login/register with username
- Game history with move replay
- Active game loading on login
- Visual board representation
- Automatic opponent move detection


### Assumptions and Tradeoffs
- **Simple authentication**: Players are identified by username only (no passwords or sessions). No JWT or sessions.
- **Player that starts the game goes first** AI is always on the defensive
- **Single game per player pair**: Only one active game can exist between two players at a time
- **3x3 board only**: Tempting to make it customizable but I had to cut the scope somewhere
- **REST over Sockets**: Would have been cool to make the board syncing live but i think polling is an efficient UI enough to test the APII rapidly and iterate on the features
- **CLI only**: Adding a React frontend would have been a solid choice but I felt like I would be too tempted to polish that way too much and take up a lot of time
- **Store the entire board state for every move**: since under 15 bytes, the duplication cost is very low. Conceptually simpler to manage than storing just the move and then replaying all of them

### Where I used AI
- Writing the scaffolding for this doc, especially the how to use part :D
- Writing tests. Entirely AI generated
- Writing a smarter game AI.
- Scaffolding the initial API endpoints and the DB setup.
- I relied a fair bit on the autocomplete features to enforce typing. Also this gives the best control over what exactly the LLMs are suggesting.

### Time Spent

Approximately **~4 hours** building the complete project, including:

- Standing up the core API  (~1 hour)
- Multiplayer support and CLI iteration (~1.5 hour)
- Miscellaneous stuff like adding history API and fixing bugs that came from adding one feature over another(~30 hour)
- Code refactoring and documentation. Way longer than I thought it would (~1 hour)

### Feedback

As I said above, fun and creative. I am looking forward to seeing having a deeper discussion about this. 


---

## Technical Documentation

### CLI Client Features

The interactive CLI client supports:
- **Login/Register**: Enter your name to log in as existing player or create new one
- **Active Game Loading**: Automatically shows your in-progress games on login
- **Player vs AI**: Play against a strategic AI opponent that tries to win and block your moves
- **Player vs Player**: Play against another human player using their Player ID
- **Automatic game resumption**: If an in-progress game exists between two players, it loads automatically
- **Real-time polling**: When waiting for opponent, polls server every 3 seconds
- **Game History**: View all your completed games with results (WIN/LOSS/TIE)
- **Move Replay**: View all moves in a completed game, board by board
- Multiple games in a session

## API Endpoints

### 1. Register a Player
- **POST** `/players`
- Body: `{"name": "Player Name"}`
- Returns: `{"player_id": 1, "name": "Player Name"}`

### 2. Get Player by Name (Login)
- **GET** `/players/by-name/{name}`
- Returns: Player info if exists, or null

### 3. Get Player's Active Games
- **GET** `/players/{player_id}/games`
- Returns: List of all in-progress games for the player

### 4. Create a Game
- **POST** `/games`
- Body: `{"created_by": 1, "opponent": "AI"}` or `{"created_by": 1, "opponent": "2"}`
- Returns: Game details with `game_id`

### 5. Find Existing Game
- **GET** `/games/find?player1={id}&player2={id}`
- Returns: Existing in-progress game between two players, or null if none exists

### 6. Get Game Status
- **GET** `/games/{game_id}`
- Returns: Current board state, whose turn it is, game status, and winner (if any)

### 7. Make a Move
- **POST** `/moves`
- Body: `{"game_id": 1, "player_id": 1, "row": 0, "col": 0}`
- Returns: Updated board state, AI move (if applicable), and game status
- Note: Validates that it's the player's turn before making the move

### 8. Get Game Move History
- **GET** `/games/{game_id}/moves`
- Returns: All moves in a game, chronologically ordered, with board states

### 9. Get Player Game History
- **GET** `/players/{player_id}/history`
- Returns: All games for a player (completed and in-progress), chronologically ordered

## Testing with curl

### Quick Test Script
```bash
chmod +x test_game.sh
./test_game.sh
```

### Manual Testing

**1. Register a player:**
```bash
curl -X POST "http://localhost:8000/players" \
  -H "Content-Type: application/json" \
  -d '{"name": "Max"}'
```
Save the returned `player_id` for next steps.

**2. Create a game vs AI:**
```bash
curl -X POST "http://localhost:8000/games" \
  -H "Content-Type: application/json" \
  -d '{"created_by": 1, "opponent": "AI"}'
```
Replace `1` with your actual `player_id`. Save the returned `game_id`.

**3. Check game status:**
```bash
curl -X GET "http://localhost:8000/games/1"
```
Replace `1` with your actual `game_id`. Returns current board state and whose turn it is.

**4. Make moves:**
```bash
curl -X POST "http://localhost:8000/moves" \
  -H "Content-Type: application/json" \
  -d '{"game_id": 1, "player_id": 1, "row": 0, "col": 0}'
```

**Example game sequence:**
```bash
# Move 1 - top-left (row:0, col:0)
curl -X POST "http://localhost:8000/moves" \
  -H "Content-Type: application/json" \
  -d '{"game_id": 1, "player_id": 1, "row": 0, "col": 0}'

# Move 2 - top-middle (row:0, col:1)
curl -X POST "http://localhost:8000/moves" \
  -H "Content-Type: application/json" \
  -d '{"game_id": 1, "player_id": 1, "row": 0, "col": 1}'

# Move 3 - center (row:1, col:1)
curl -X POST "http://localhost:8000/moves" \
  -H "Content-Type: application/json" \
  -d '{"game_id": 1, "player_id": 1, "row": 1, "col": 1}'
```

**Board Layout:**
- Positions: `(row, col)` where both are 0, 1, or 2
- Example: `(0,0)` = top-left, `(1,1)` = center, `(2,2)` = bottom-right

Each move response includes the `board_state` (9-char string showing `X`, `O`, and `.` for empty cells).

### Login and Game Resume Example

When you run the client with an existing player name:
```bash
uv run python client.py

Welcome to Tic Tac Toe!
Enter your name: Alice
✓ Found existing player: Alice (Player ID: 1)
Login as this player? (y/n): y
✓ Logged in as Alice

✓ Found 2 active game(s)!
  1. Game 3 vs AI
  2. Game 5 vs Player 2

Continue an existing game? Enter number or 'n' to skip to menu: 1
✓ Loading Game 3...
You are X, opponent (AI) is O

# After completing or quitting the game, returns to main menu
```

### Multiplayer Example

**Terminal 1 (Player 1):**
```bash
uv run python client.py
# Register as "Alice", get Player ID: 1
# Select "2. Play vs Another Player"
# Enter opponent's Player ID: 2
# Creates game and waits for opponent
```

**Terminal 2 (Player 2):**
```bash
uv run python client.py
# Register as "Bob", get Player ID: 2
# Select "2. Play vs Another Player"
# Enter opponent's Player ID: 1
# Loads existing game automatically!
```

The client polls every 3 seconds when waiting for the opponent's move.

### Game History Example

View your completed games and replay moves:
```bash
uv run python client.py

# After logging in, select option 3
Menu:
1. Play vs AI
2. Play vs Another Player
3. View Game History (Completed Games)
4. Quit
Select (1-4): 3

Game History (Completed Games)
==================================================

1. Game 3 vs AI - Result: WIN (Winner: X)
2. Game 5 vs Player 2 - Result: LOSS (Winner: O)
3. Game 7 vs AI - Result: TIE (Winner: TIE)

View moves of a game? Enter number or 'n' to go back: 1

Move History for Game 3
==================================================

Move 0: Initial board
  0 1 2
0 . . .
1 . . .
2 . . .

Move 1: Player 1
  0 1 2
0 X . .
1 . . .
2 . . .

Move 2: AI
  0 1 2
0 X . O
1 . . .
2 . . .
...
```

## Code Structure

The application is organized into separate modules:

### `main.py`
FastAPI application with all API endpoints organized by functionality:
- Player endpoints (register, login, get active games, get history)
- Game endpoints (create, find, get status, get moves)
- Move endpoints (make move)

### `database.py`
Database models and session management:
- `Player` model - Player information
- `Game` model - Game information (status, players, last_move)
- `Move` model - Move history with board states
- Database session factory and helper functions

### `schemas.py`
Pydantic models for API requests and responses:
- Request models (PlayerCreate, GameCreate, MoveCreate)
- Response models (PlayerResponse, GameResponse, MoveResponse, etc.)
- History models (GameHistoryItem, MoveHistoryItem)

### `game_logic.py`
Pure game logic functions:
- Board operations (empty_board, make_move_on_board, get_board_position)
- Game state checking (check_winner, get_current_turn)
- Strategic AI logic (ai_make_move) - tries to win, blocks opponent, prefers center/corners
- Board retrieval (get_current_board)

### `client.py`
Interactive CLI client for playing the game

### `test_game_logic.py`
Comprehensive unit tests for game logic:
- 25 tests organized into 4 test classes
- 100% coverage of game_logic.py functions
- Tests for board operations, winner detection, AI strategy, and game scenarios

## Database

The application uses SQLite with three tables:
- `players`: Stores player information
- `games`: Stores game information (status, players, etc.)
- `moves`: Stores all moves with board states

Board state is represented as a 9-character string where:
- `.` = empty cell
- `X` = player 1
- `O` = player 2/AI