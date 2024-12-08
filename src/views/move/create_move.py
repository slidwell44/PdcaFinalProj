from pydantic import BaseModel, field_validator, ConfigDict

from .position import Position

class MoveCreate(BaseModel):
    player: str
    position: Position

    model_config = ConfigDict(json_encoders={})

    @classmethod
    @field_validator("player", mode="before")
    def validate_player(cls, value):
        if value not in {'X', 'O'}:
            raise ValueError("Player must be either 'X' or 'O'")
        return value

    @classmethod
    @field_validator("position", mode="before")
    def validate_position(cls, value):
        if not isinstance(value, Position):
            raise TypeError("Position must have row: int and col: int")
        return value  
