#!/usr/bin/env python3
import requests
import sys
import time

BASE_URL = "http://localhost:8000"

def print_board(board_state):
    """Print the board in a readable format"""
    print("\nCurrent Board:")
    print("  0 1 2")
    for i in range(3):
        row = board_state[i*3:(i+1)*3]
        print(f"{i} {' '.join(row)}")
    print()

def get_player_by_name(name):
    """Check if a player with this name exists"""
    response = requests.get(f"{BASE_URL}/players/by-name/{name}")
    if response.status_code == 200 and response.json():
        return response.json()
    return None

def register_player(name):
    """Register a new player"""
    response = requests.post(f"{BASE_URL}/players", json={"name": name})
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Registered as {data['name']} (Player ID: {data['player_id']})")
        return data['player_id']
    else:
        print(f"✗ Error registering player: {response.text}")
        return None

def get_active_games(player_id):
    """Get all active games for a player"""
    response = requests.get(f"{BASE_URL}/players/{player_id}/games")
    if response.status_code == 200:
        data = response.json()
        return data.get('games', [])
    return []

def get_player_history(player_id):
    """Get all games for a player (completed and in-progress)"""
    response = requests.get(f"{BASE_URL}/players/{player_id}/history")
    if response.status_code == 200:
        data = response.json()
        return data.get('games', [])
    return []

def get_game_moves(game_id):
    """Get all moves in a game"""
    response = requests.get(f"{BASE_URL}/games/{game_id}/moves")
    if response.status_code == 200:
        return response.json()
    return None

def create_game(player_id, opponent):
    """Create a new game vs AI or another player"""
    response = requests.post(f"{BASE_URL}/games", json={"created_by": player_id, "opponent": opponent})
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Game created! Game ID: {data['game_id']}")
        return data['game_id'], opponent
    else:
        print(f"✗ Error creating game: {response.text}")
        return None, None

def find_existing_game(player_id, opponent_id):
    """Find an existing in-progress game between two players"""
    response = requests.get(f"{BASE_URL}/games/find", params={"player1": player_id, "player2": opponent_id})
    if response.status_code == 200 and response.json():
        data = response.json()
        print(f"✓ Found existing game! Game ID: {data['game_id']}")
        return data['game_id']
    return None

def get_game_status(game_id):
    """Get current game status"""
    response = requests.get(f"{BASE_URL}/games/{game_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"✗ Error getting game status: {response.text}")
        return None

def make_move(game_id, player_id, row, col):
    """Make a move"""
    response = requests.post(f"{BASE_URL}/moves", json={"game_id": game_id, "player_id": player_id, "row": row, "col": col})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"✗ Error making move: {response.text}")
        return None

def play_game(player_id, game_id, opponent):
    """Play a single game with polling support"""
    is_ai = (opponent == "AI")
    last_board = None
    
    print("\nEnter moves as: row col (e.g., '0 1' for top-middle)")
    print("Type 'quit' to exit\n")
    
    # Game loop
    while True:
        # Get current game status
        status = get_game_status(game_id)
        if not status:
            break
        
        # Check if board changed (opponent made a move)
        if last_board and last_board != status['board_state']:
            print("\n" + "="*50)
            if is_ai:
                print("AI made a move!")
            else:
                print("Opponent made a move!")
        
        last_board = status['board_state']
        
        # Show board
        print_board(status['board_state'])
        
        # Check if game is over
        if status['status'] == 'done':
            if status['winner'] == 'TIE':
                print("🤝 Game Over! It's a tie!")
            elif status['winner']:
                # Check if we won
                my_symbol = 'X' if status['created_by'] == player_id else 'O'
                if status['winner'] == my_symbol:
                    print("🎉 Game Over! You win!")
                else:
                    print("💔 Game Over! You lose!")
            else:
                print("Game Over!")
            return True  # Game finished
        
        # Check whose turn it is
        current_turn = status.get('current_turn')
        
        if current_turn == str(player_id):
            # Player's turn
            my_symbol = 'X' if status['created_by'] == player_id else 'O'
            print(f"Your turn ({my_symbol})")
            
            # Get player's move
            move_input = input("Enter move (row col): ").strip()
            
            if move_input.lower() == 'quit':
                return False  # User quit
            
            # Parse move
            try:
                parts = move_input.split()
                if len(parts) != 2:
                    print("Invalid input! Use format: row col (e.g., '0 1')")
                    continue
                
                row, col = int(parts[0]), int(parts[1])
                
                if row < 0 or row > 2 or col < 0 or col > 2:
                    print("Invalid coordinates! Use 0, 1, or 2 for row and column")
                    continue
                
            except ValueError:
                print("Invalid input! Use numbers for row and column")
                continue
            
            # Make the move
            result = make_move(game_id, player_id, row, col)
            if not result:
                continue
            
            print("\n" + "="*50)
            
        else:
            # Opponent's turn - wait and poll
            if is_ai:
                print("AI is thinking...")
                time.sleep(1)  # Short delay for AI
            else:
                opponent_symbol = 'O' if status['created_by'] == player_id else 'X'
                print(f"Waiting for opponent ({opponent_symbol})... (polling every 3s)")
                time.sleep(3)  # Poll every 3 seconds

def view_game_moves(game_id, player_id):
    """View all moves in a completed game"""
    moves_data = get_game_moves(game_id)
    if not moves_data:
        print("✗ Could not retrieve game moves")
        return
    
    moves = moves_data.get('moves', [])
    if not moves:
        print("No moves found for this game")
        return
    
    print(f"\n{'=' * 50}")
    print(f"Move History for Game {game_id}")
    print(f"{'=' * 50}\n")
    
    for move in moves:
        move_num = move['move_number']
        player = move['player']
        board_state = move['board_state']
        
        if player == 'initial':
            print(f"Move {move_num}: Initial board")
        else:
            player_label = "AI" if player == "AI" else f"Player {player}"
            print(f"Move {move_num}: {player_label}")
        
        print_board(board_state)
        print()
    
    input("Press Enter to continue...")

def view_game_history(player_id):
    """View all completed games for a player"""
    all_games = get_player_history(player_id)
    
    # Filter for completed games only
    completed_games = [g for g in all_games if g['status'] == 'done']
    
    if not completed_games:
        print("\n✗ No completed games found")
        return
    
    print(f"\n{'=' * 50}")
    print(f"Game History (Completed Games)")
    print(f"{'=' * 50}\n")
    
    for i, game in enumerate(completed_games, 1):
        opponent_label = "AI" if game['opponent'] == "AI" else f"Player {game['opponent']}"
        winner_label = "TIE" if game['winner'] == 'TIE' else game['winner'] if game['winner'] else "Unknown"
        
        # Determine if the player won
        if game['winner'] == 'TIE':
            result = "TIE"
        elif game['winner']:
            player_symbol = 'X' if game['created_by'] == player_id else 'O'
            result = "WIN" if game['winner'] == player_symbol else "LOSS"
        else:
            result = "Unknown"
        
        print(f"{i}. Game {game['game_id']} vs {opponent_label} - Result: {result} (Winner: {winner_label})")
    
    # Ask if they want to view moves of a game
    choice = input("\nView moves of a game? Enter number or 'n' to go back: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(completed_games):
        selected_game = completed_games[int(choice) - 1]
        view_game_moves(selected_game['game_id'], player_id)

def main():
    print("=" * 50)
    print("Welcome to Tic Tac Toe!")
    print("=" * 50)
    
    # Login or Register
    name = input("\nEnter your name: ").strip()
    if not name:
        print("Name cannot be empty!")
        return
    
    # Check if player exists
    existing_player = get_player_by_name(name)
    player_id = None
    
    if existing_player:
        print(f"✓ Found existing player: {existing_player['name']} (Player ID: {existing_player['player_id']})")
        login = input("Login as this player? (y/n): ").strip().lower()
        if login == 'y':
            player_id = existing_player['player_id']
            print(f"✓ Logged in as {existing_player['name']}")
        else:
            print("Please choose a different name.")
            return
    else:
        print(f"No player found with name '{name}'. Creating new player...")
        player_id = register_player(name)
        if not player_id:
            return
    
    # Check for active games
    active_games = get_active_games(player_id)
    if active_games:
        print(f"\n✓ Found {len(active_games)} active game(s)!")
        for i, game in enumerate(active_games, 1):
            opponent_label = "AI" if game['opponent'] == "AI" else f"Player {game['opponent']}"
            print(f"  {i}. Game {game['game_id']} vs {opponent_label}")
        
        choice = input("\nContinue an existing game? Enter number or 'n' to skip to menu: ").strip().lower()
        if choice != 'n' and choice.isdigit() and 1 <= int(choice) <= len(active_games):
            selected_game = active_games[int(choice) - 1]
            game_id = selected_game['game_id']
            opponent = selected_game['opponent']
            
            print(f"\n✓ Loading Game {game_id}...")
            
            # Get game info to show symbols
            status = get_game_status(game_id)
            if status:
                my_symbol = 'X' if status['created_by'] == player_id else 'O'
                opp_symbol = 'O' if my_symbol == 'X' else 'X'
                opponent_label = "AI" if opponent == "AI" else f"Player {opponent}"
                print(f"You are {my_symbol}, opponent ({opponent_label}) is {opp_symbol}")
            
            # Play the loaded game
            finished = play_game(player_id, game_id, opponent)
            
            if not finished:
                # User quit the game
                print("Returning to menu...")
        else:
            print("Skipping to menu...")
    
    while True:
        # Ask for game type
        print("\n" + "=" * 50)
        print("Menu:")
        print("1. Play vs AI")
        print("2. Play vs Another Player")
        print("3. View Game History (Completed Games)")
        print("4. Quit")
        choice = input("Select (1-4): ").strip()
        
        if choice == '4':
            print("Thanks for playing!")
            break
        
        if choice == '3':
            view_game_history(player_id)
            continue
        
        if choice not in ['1', '2']:
            print("Invalid selection!")
            continue
        
        game_type = choice
        
        opponent = "AI"
        game_id = None
        
        if game_type == '2':
            # Multiplayer
            opponent_id = input("Enter opponent's Player ID: ").strip()
            if not opponent_id.isdigit():
                print("Invalid player ID!")
                continue
            
            opponent = opponent_id
            
            # Check for existing game
            print("\nChecking for existing game...")
            game_id = find_existing_game(player_id, int(opponent_id))
            
            if not game_id:
                print("No existing game found. Creating new game...")
                game_id, opponent = create_game(player_id, opponent)
            
        else:
            # AI game
            print("\nCreating a game against AI...")
            game_id, opponent = create_game(player_id, "AI")
        
        if not game_id:
            continue
        
        # Get game info to show symbols
        status = get_game_status(game_id)
        if status:
            my_symbol = 'X' if status['created_by'] == player_id else 'O'
            opp_symbol = 'O' if my_symbol == 'X' else 'X'
            print(f"\nYou are {my_symbol}, opponent is {opp_symbol}")
        
        # Play the game
        finished = play_game(player_id, game_id, opponent)
        
        if not finished:
            # User quit
            print("Thanks for playing!")
            break
        
        # Ask to play again
        play_again = input("\nPlay again? (y/n): ").strip().lower()
        if play_again != 'y':
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nThanks for playing!")
        sys.exit(0)
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to the server. Make sure it's running at http://localhost:8000")
        sys.exit(1)

