"""Tests for game logic functions."""
import pytest
from game_logic import (
    empty_board,
    get_board_position,
    make_move_on_board,
    check_winner,
    ai_make_move,
)


class TestBoardOperations:
    """Test basic board operations."""
    
    def test_empty_board(self):
        """Test empty board creation."""
        board = empty_board()
        assert board == "." * 9
        assert len(board) == 9
    
    def test_get_board_position(self):
        """Test board position calculation."""
        assert get_board_position(0, 0) == 0
        assert get_board_position(0, 1) == 1
        assert get_board_position(0, 2) == 2
        assert get_board_position(1, 0) == 3
        assert get_board_position(1, 1) == 4
        assert get_board_position(2, 2) == 8
    
    def test_make_move_on_board(self):
        """Test making a valid move."""
        board = empty_board()
        result = make_move_on_board(board, 0, 0, "X")
        assert result == "X........"
        
        result = make_move_on_board(result, 1, 1, "O")
        assert result == "X...O...."
    
    def test_make_move_invalid_position(self):
        """Test move on already taken position."""
        board = "X........"
        with pytest.raises(ValueError, match="position already taken"):
            make_move_on_board(board, 0, 0, "O")


class TestWinnerDetection:
    """Test winner detection logic."""
    
    def test_check_winner_row_top(self):
        """Test horizontal win on top row."""
        assert check_winner("XXX......") == "X"
        assert check_winner("OOO......") == "O"
    
    def test_check_winner_row_middle(self):
        """Test horizontal win on middle row."""
        assert check_winner("...XXX...") == "X"
        assert check_winner("...OOO...") == "O"
    
    def test_check_winner_row_bottom(self):
        """Test horizontal win on bottom row."""
        assert check_winner("......XXX") == "X"
        assert check_winner("......OOO") == "O"
    
    def test_check_winner_column_left(self):
        """Test vertical win on left column."""
        assert check_winner("X..X..X..") == "X"
        assert check_winner("O..O..O..") == "O"
    
    def test_check_winner_column_middle(self):
        """Test vertical win on middle column."""
        assert check_winner(".X..X..X.") == "X"
        assert check_winner(".O..O..O.") == "O"
    
    def test_check_winner_column_right(self):
        """Test vertical win on right column."""
        assert check_winner("..X..X..X") == "X"
        assert check_winner("..O..O..O") == "O"
    
    def test_check_winner_diagonal_main(self):
        """Test diagonal win (top-left to bottom-right)."""
        assert check_winner("X...X...X") == "X"
        assert check_winner("O...O...O") == "O"
    
    def test_check_winner_diagonal_anti(self):
        """Test diagonal win (top-right to bottom-left)."""
        assert check_winner("..X.X.X..") == "X"
        assert check_winner("..O.O.O..") == "O"
    
    def test_check_winner_tie(self):
        """Test tie game detection."""
        assert check_winner("XOXOXOOXO") == "TIE"
        assert check_winner("XXOOOXXXO") == "TIE"
    
    def test_check_winner_in_progress(self):
        """Test game in progress (no winner yet)."""
        assert check_winner("X.O......") is None
        assert check_winner("XO.XO....") is None
        assert check_winner(".........") is None


class TestAI:
    """Test AI move selection."""
    
    def test_ai_takes_winning_move_row(self):
        """Test AI takes winning move in a row."""
        board = "OO......."  # AI (O) can win at position 2
        row, col = ai_make_move(board)
        assert (row, col) == (0, 2)
    
    def test_ai_takes_winning_move_column(self):
        """Test AI takes winning move in a column."""
        board = "O..O....."  # AI (O) can win at position 6
        row, col = ai_make_move(board)
        assert (row, col) == (2, 0)
    
    def test_ai_takes_winning_move_diagonal(self):
        """Test AI takes winning move in a diagonal."""
        board = "O...O...."  # AI (O) can win at position 8
        row, col = ai_make_move(board)
        assert (row, col) == (2, 2)
    
    def test_ai_blocks_opponent_winning_move(self):
        """Test AI blocks opponent's winning move."""
        board = "XX......."  # Player (X) about to win, AI must block
        row, col = ai_make_move(board)
        assert (row, col) == (0, 2)
    
    def test_ai_blocks_opponent_column(self):
        """Test AI blocks opponent's column win."""
        board = "X..X....."  # Player about to win column
        row, col = ai_make_move(board)
        assert (row, col) == (2, 0)
    
    def test_ai_takes_center_when_empty(self):
        """Test AI takes center on empty board."""
        board = "........."
        row, col = ai_make_move(board)
        assert (row, col) == (1, 1)
    
    def test_ai_takes_corner_when_center_taken(self):
        """Test AI prefers corners when center is taken."""
        board = "....X...."  # Center taken
        row, col = ai_make_move(board)
        # Should be one of the corners
        assert (row, col) in [(0, 0), (0, 2), (2, 0), (2, 2)]
    
    def test_ai_returns_none_for_full_board(self):
        """Test AI handles full board."""
        board = "XOXOXOXOX"
        row, col = ai_make_move(board)
        assert row is None
        assert col is None
    
    def test_ai_makes_valid_move(self):
        """Test AI only makes moves on empty positions."""
        board = "X.O......"
        row, col = ai_make_move(board)
        pos = get_board_position(row, col)
        assert board[pos] == "."  # Position was empty


class TestGameScenarios:
    """Test complete game scenarios."""
    
    def test_complete_game_x_wins(self):
        """Test a complete game where X wins."""
        board = empty_board()
        board = make_move_on_board(board, 0, 0, "X")  # X
        board = make_move_on_board(board, 1, 0, "O")  # O
        board = make_move_on_board(board, 0, 1, "X")  # X
        board = make_move_on_board(board, 1, 1, "O")  # O
        board = make_move_on_board(board, 0, 2, "X")  # X wins
        assert check_winner(board) == "X"
    
    def test_complete_game_tie(self):
        """Test a complete game that ends in a tie."""
        board = empty_board()
        board = make_move_on_board(board, 0, 0, "X")
        board = make_move_on_board(board, 0, 1, "O")
        board = make_move_on_board(board, 0, 2, "X")
        board = make_move_on_board(board, 1, 0, "O")
        board = make_move_on_board(board, 1, 1, "X")
        board = make_move_on_board(board, 2, 0, "O")
        board = make_move_on_board(board, 1, 2, "X")
        board = make_move_on_board(board, 2, 2, "O")
        board = make_move_on_board(board, 2, 1, "X")
        assert check_winner(board) == "TIE"

