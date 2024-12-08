from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class MoveRead(BaseModel):
    id: UUID
    game_id: UUID
    player: str
    row: int
    col: int
    timestamp: datetime

    class Config:
        from_attributes = True
