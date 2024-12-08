import json
from typing import Dict, List, Optional

import httpx

from .base import MyGame
from src.views.game.create_game import GameType
from src.views.move import MoveCreate, MoveRead
from ..views.game.update_game_winner import WinnerEnum
from ..views.move.position import Position

class GameBoard:
    def __init__(self):
        self.board: Dict[int, List[Optional[MoveRead]]] = {
            0: [None, None, None],
            1: [None, None, None],
            2: [None, None, None],
        }

        
class IllegalMove(Exception): ...


class TicTacToe(MyGame):
    def __init__(self):
        super().__init__(game_type=GameType.TIC_TAC_TOE.value)

    def print_board(self):
        game_board = self.get_board()

        row_count = len(game_board.board)
        for i, (k, v) in enumerate(game_board.board.items()):
            formatted_row = [val.player if isinstance(val, MoveRead) else str(idx) for idx, val in enumerate(v)]
            print(f"{k}  " + " | ".join(formatted_row) + " ")
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
                    return self.return_player_turn_string(player)

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
        if attempted_move.player == self.player_turn:
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
    
        # Rows
        for row in game_board.board.values():
            lines.append(row)
    
        # Columns
        for col in range(3):
            column = [game_board.board[row][col] for row in range(3)]
            lines.append(column)
    
        # Diagonals
        primary_diag = [game_board.board[i][i] for i in range(3)]
        secondary_diag = [game_board.board[i][2 - i] for i in range(3)]
        lines.append(primary_diag)
        lines.append(secondary_diag)
    
        # Check for win
        for line in lines:
            if all(cell is not None and cell.player == 'X' for cell in line):
                return 'X'
            if all(cell is not None and cell.player == 'O' for cell in line):
                return 'O'
    
        # Check for tie
        if all(cell is not None for row in game_board.board.values() for cell in row):
            return 'Tie'
    
        # Game is still ongoing
        return None

