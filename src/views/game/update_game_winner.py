from pydantic import BaseModel
from enum import Enum

class WinnerEnum(str, Enum):
    X = 'X'
    O = 'O'
    Tie = 'Tie'

class UpdateWinnerRequest(BaseModel):
    winner: WinnerEnum
