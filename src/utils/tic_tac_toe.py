import copy
from datetime import datetime, UTC
import json
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
        self.board: List[List[Optional[MoveRead]]] = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ]

        
class IllegalMove(Exception): ...


class TicTacToe(MyGame):
    def __init__(self):
        super().__init__(game_type=GameType.TIC_TAC_TOE.value)

        self.ai_player = 'O'
        self.human_player = 'X'

    def print_board(self):
        game_board = self.get_board()

        row_count = len(game_board.board)
        for i, v in enumerate(game_board.board):
            formatted_row = [val.player if isinstance(val, MoveRead) else str(idx) for idx, val in enumerate(v)]
            print(f"{i}  " + " | ".join(formatted_row) + " ")
            if i < row_count - 1:
                print("   --------- ")


    def get_board(self) -> GameBoard:
        game_board: GameBoard = GameBoard()
        completed_moves: list[MoveRead] = self.get_moves()

        for cm in completed_moves:
            if game_board.board[cm.row][cm.col] is None:
                game_board.board[cm.row][cm.col] = cm
                
        return game_board

    def make_move(self, player: str, row: int, col: int) -> str:
        if self.game_over:
            return "The game is already over"
        
        if player != self.player_turn:
            return f"It's not player {player}'s turn"
        
        try:
            attempted_move = MoveCreate(
                player=player,
                position=Position(row=row, col=col),
            )

            if self._is_legal_move(attempted_move):
                response = httpx.post(
                    self._moves_url,
                    json=attempted_move.model_dump()
                )
                response.raise_for_status()
                game_board = self.get_board()
                result = self._check_win_conditions(game_board)
                self.print_board()
                
                if not result:
                    if self.player_turn == self.human_player:
                        self.player_turn = self.ai_player
                        return self.ai_move()
                    if self.player_turn == self.ai_player:
                        self.player_turn = self.human_player
                        return "Player X make your move"

                if result == 'X':
                    self.update_game_winner(WinnerEnum.X)
                    self.game_over = True
                    self._cleanup()
                    return f"Player X wins!"
                elif result == 'O':
                    self.update_game_winner(WinnerEnum.O)
                    self.game_over = True
                    self._cleanup()
                    return f"Player O wins!"
                elif result == 'Tie':
                    self.update_game_winner(WinnerEnum.Tie)
                    self.game_over = True
                    self._cleanup()
                    return "The game is a tie!"
                else:
                    return "Something bad happened..."
            else:
                raise IllegalMove(f"Performing illegal move: {attempted_move.model_dump()}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error occurred: {e.response.text}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to decode JSON response: {e}") from e
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}") from e

    def _is_legal_move(self, attempted_move: MoveCreate) -> bool:
        if attempted_move.player != self.player_turn:
            self.print_player_turn(attempted_move.player)
            return False
        
        game_board = self.get_board()

        row = attempted_move.position.row
        col = attempted_move.position.col
        
        if game_board.board[row][col] is None:
            return True
        else:
            return False
    
    @staticmethod
    def print_player_turn(player: str):
        if player == 'X':
            print(f"It's player: O's turn")
        elif player == 'O':
            print(f"It's player: X's turn")

    @staticmethod
    def return_player_turn_string(player: str) -> str:
        if player == 'X':
            return f"It's player: O's turn"
        elif player == 'O':
            return f"It's player: X's turn"

    @staticmethod
    def _check_win_conditions(game_board: GameBoard) -> Optional[str]:
        lines = []
    
        for row in game_board.board:
            lines.append(row)
    
        for col in range(3):
            column = [game_board.board[row][col] for row in range(3)]
            lines.append(column)
    
        primary_diag = [game_board.board[i][i] for i in range(3)]
        secondary_diag = [game_board.board[i][2 - i] for i in range(3)]
        lines.append(primary_diag)
        lines.append(secondary_diag)
    
        for line in lines:
            if all(cell is not None and cell.player == 'X' for cell in line):
                return 'X'
            if all(cell is not None and cell.player == 'O' for cell in line):
                return 'O'
    
        if all(cell is not None for row in game_board.board for cell in row):
            return 'Tie'
    
        return None

    def ai_move(self):
        game_board = self.get_board()
        best_score = float('-inf')
        best_move: Optional[Tuple[int, int]] = None
    
        for row in range(3):
            for col in range(3):
                if game_board.board[row][col] is None:
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
                        best_move = (row, col)
    
        if best_move:
            row, col = best_move
            print(f"AI chooses to place at ({row}, {col})")
            return self.make_move(player=self.ai_player, row=row, col=col)
        else:
            return "No possible moves for AI."

    def minimax(self, board: List[List[Optional[MoveRead]]], depth: int, is_maximizing: bool) -> int:
        print(f"Depth: {depth}, is_maximizing: {is_maximizing}")

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
            for row in range(3):
                for col in range(3):
                    if board[row][col] is None:
                        # Simulate AI move
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
            for row in range(3):
                for col in range(3):
                    if board[row][col] is None:
                        # Simulate Human move
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

