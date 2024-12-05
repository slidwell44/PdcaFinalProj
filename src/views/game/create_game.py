from enum import Enum

from pydantic import BaseModel

class GameType(str, Enum):
    TIC_TAC_TOE = "TicTacToe"
    CONNECT_4 = "Connect4"

class GameCreate(BaseModel):
    game_type: GameType = GameType.TIC_TAC_TOE