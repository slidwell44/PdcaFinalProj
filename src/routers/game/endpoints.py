from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db import get_db
from src.db.dbinit import Game
from src.views.game.read_game import GameRead
from src.views.game.update_game_winner import UpdateWinnerRequest

router = APIRouter(tags=['Games'])

@router.post(
    "/games/{game_type}",
    response_model=GameRead,
    status_code=status.HTTP_201_CREATED,
)
def create_game(game_type: str, db: Session = Depends(get_db)):
    db_game = Game(game_type=game_type)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game



@router.get(
    '/games/{game_id}',
    response_model=GameRead,
    status_code=status.HTTP_200_OK,
)
def read_game(game_id: UUID, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == str(game_id)).first()
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Game not found')
    return game

@router.put(
    "/games/{game_id}/winner", 
    response_model=GameRead, 
    status_code=status.HTTP_200_OK
)
def update_game_winner(game_id: UUID, winner_request: UpdateWinnerRequest, db: Session = Depends(get_db)):
    db_game = db.query(Game).filter(Game.id == str(game_id)).first()
    if not db_game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    db_game.winner = winner_request.winner
    db.commit()
    db.refresh(db_game)
    return db_game

@router.delete(
    '/games/{game_id}', 
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_game(game_id: UUID, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == str(game_id)).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    db.delete(game)
    db.commit()