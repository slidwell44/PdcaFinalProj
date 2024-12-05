from pydantic import BaseModel

class MoveCreate(BaseModel):
    player: str
    position: str