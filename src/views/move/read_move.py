from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class MoveRead(BaseModel):
    id: UUID
    game_id: UUID
    player: str
    position: int
    timestamp: datetime

    class Config:
        from_attributes = True