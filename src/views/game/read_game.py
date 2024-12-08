from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .create_game import GameType
from ..move.read_move import MoveRead
from .update_game_winner import WinnerEnum

class GameRead(BaseModel):
    id: UUID
    createdat: datetime
    winner: Optional[WinnerEnum]
    game_type: GameType
    moves: List['MoveRead'] = []

    @classmethod
    @field_validator("id")
    def convert_uuid_to_str(cls, value: UUID) -> str:
        return str(value)

    class Config:
        from_attributes = True

GameRead.model_rebuild()