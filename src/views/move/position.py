from pydantic import BaseModel

class Position(BaseModel):
    row: int
    col: int
