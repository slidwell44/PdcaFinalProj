from pydantic import BaseModel

class UpdateWinnerRequest(BaseModel):
    winner: str 
