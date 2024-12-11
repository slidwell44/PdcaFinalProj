import copy
from datetime import datetime, UTC
from typing import List, Optional, Tuple
from uuid import uuid4

import httpx

from .base import MyGame
from src.views.game.create_game import GameType
from src.views.move import MoveCreate, MoveRead
from ..views.game.update_game_winner import WinnerEnum
from ..views.move.position import Position



class GameBoard:
    def __init__(self):
        self.rows = 6
        self.cols = 7
        self.board: List[List[Optional[MoveRead]]] = [
            [None for _ in range(self.cols)] for _ in range(self.rows)
        ]

class IllegalMove(Exception): ...

class ConnectFour(MyGame):
    def __init__(self):
        super().__init__(game_type=GameType.CONNECT4.value)

        self.ai_player = 'O'
        self.human_player = 'X'

    def get_board(self) -> GameBoard:
        game_board: GameBoard = GameBoard()
        completed_moves: list[MoveRead] = self.get_moves()

        for cm in completed_moves:
            if game_board.board[cm.row][cm.col] is None:
                game_board.board[cm.row][cm.col] = cm

        return game_board

    def print_board(self):
        game_board = self.get_board()
        for i, row in enumerate(game_board.board):
            formatted_row = [val.player if val else '.' for val in row]
            print(f"{i}  " + " | ".join(formatted_row) + " ")

        print("   " + "   ".join(str(c) for c in range(game_board.cols)))

    def make_move(self, player: str, col: int) -> str:
        if self.game_over:
            return "The game is already over"

        if player != self.player_turn:
            return f"It's not player {player}'s turn"

        game_board = self.get_board()
        row = self._find_lowest_empty_row(game_board, col)
        if row is None:
            return "Column is full, pick another column."

        attempted_move = MoveCreate(
            player=player,
            position=Position(row=row, col=col),
        )

        if self._is_legal_move(attempted_move):
            response = httpx.post(self._moves_url, json=attempted_move.model_dump())
            response.raise_for_status()

            game_board = self.get_board()
            result = self._check_win_conditions(game_board)
            self.print_board()

            if not result:
                # Toggle player
                if self.player_turn == self.human_player:
                    self.player_turn = self.ai_player
                    return self.ai_move()
                else:
                    self.player_turn = self.human_player
                    return "Human player, make your move"

            if result == 'X':
                self.update_game_winner(WinnerEnum.X)
                self.game_over = True
                self._cleanup()
                return "Player X wins!"
            elif result == 'O':
                self.update_game_winner(WinnerEnum.O)
                self.game_over = True
                self._cleanup()
                return "Player O wins!"
            elif result == 'Tie':
                self.update_game_winner(WinnerEnum.Tie)
                self.game_over = True
                self._cleanup()
                return "The game is a tie!"
            else:
                return "Something bad happened..."
        else:
            raise IllegalMove("That move is not legal.")

    @staticmethod
    def _find_lowest_empty_row(game_board: GameBoard, col: int) -> Optional[int]:
        for row in reversed(range(game_board.rows)):
            if game_board.board[row][col] is None:
                return row
        return None

    def _is_legal_move(self, attempted_move: MoveCreate) -> bool:
        if attempted_move.player != self.player_turn:
            return False

        game_board = self.get_board()
        row = attempted_move.position.row
        col = attempted_move.position.col

        if (0 <= row < game_board.rows and 0 <= col < game_board.cols and
                game_board.board[row][col] is None):
            return True
        return False

    def _check_win_conditions(self, game_board: GameBoard) -> Optional[str]:
        # Horizontal check
        for r in range(game_board.rows):
            for c in range(game_board.cols - 3):
                if self._check_line(game_board, r, c, 0, 1):
                    return game_board.board[r][c].player

        # Vertical check
        for r in range(game_board.rows - 3):
            for c in range(game_board.cols):
                if self._check_line(game_board, r, c, 1, 0):
                    return game_board.board[r][c].player

        # Diagonal checks
        for r in range(game_board.rows - 3):
            for c in range(game_board.cols - 3):
                if self._check_line(game_board, r, c, 1, 1):
                    return game_board.board[r][c].player
        for r in range(3, game_board.rows):
            for c in range(game_board.cols - 3):
                if self._check_line(game_board, r, c, -1, 1):
                    return game_board.board[r][c].player

        # Check for tie
        if all(cell is not None for row in game_board.board for cell in row):
            return 'Tie'

        return None

    @staticmethod
    def _check_line(game_board: GameBoard, start_row: int, start_col: int, delta_row: int, delta_col: int) -> bool:
        first_cell = game_board.board[start_row][start_col]
        if first_cell is None:
            return False
        player = first_cell.player
        for i in range(1, 4):
            r = start_row + delta_row * i
            c = start_col + delta_col * i
            if game_board.board[r][c] is None or game_board.board[r][c].player != player:
                return False
        return True

    def ai_move(self):
        game_board = self.get_board()
        best_score = float('-inf')
        best_col: Optional[int] = None

        for col in range(game_board.cols):
            row = self._find_lowest_empty_row(game_board, col)
            if row is not None:
                # Simulate AI move
                # noinspection PyTypeChecker
                game_board.board[row][col] = MoveRead(
                    id=str(uuid4()),
                    game_id=str(uuid4()),
                    player=self.ai_player,
                    row=row,
                    col=col,
                    timestamp=datetime.now(UTC)
                )
                score = self.minimax(game_board.board, 0, False)
                # Undo move
                game_board.board[row][col] = None
                if score > best_score:
                    best_score = score
                    best_col = col

        if best_col is not None:
            print(f"AI chooses column {best_col}")
            return self.make_move(player=self.ai_player, col=best_col)
        else:
            return "No possible moves for AI."

    def minimax(self, board: List[List[Optional[MoveRead]]], depth: int, is_maximizing: bool) -> int:
        temp_game_board = GameBoard()
        temp_game_board.board = copy.deepcopy(board)
        result = self._check_win_conditions(temp_game_board)

        if result == self.human_player:
            return -1
        elif result == self.ai_player:
            return 1
        elif result == 'Tie':
            return 0

        if is_maximizing:
            best_score = float('-inf')
            for col in range(temp_game_board.cols):
                row = self._find_lowest_empty_row(temp_game_board, col)
                if row is not None:
                    # noinspection PyTypeChecker
                    board[row][col] = MoveRead(
                        id=str(uuid4()),
                        game_id=str(uuid4()),
                        player=self.ai_player,
                        row=row,
                        col=col,
                        timestamp=datetime.now(UTC)
                    )
                    score = self.minimax(board, depth + 1, False)
                    board[row][col] = None
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for col in range(temp_game_board.cols):
                row = self._find_lowest_empty_row(temp_game_board, col)
                if row is not None:
                    # noinspection PyTypeChecker
                    board[row][col] = MoveRead(
                        id=str(uuid4()),
                        game_id=str(uuid4()),
                        player=self.human_player,
                        row=row,
                        col=col,
                        timestamp=datetime.now(UTC)
                    )
                    score = self.minimax(board, depth + 1, True)
                    board[row][col] = None
                    best_score = min(score, best_score)
            return best_score
