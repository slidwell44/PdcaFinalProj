from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db import get_db
from src.db.dbinit import Game, Move
from src.views.move import MoveCreate, MoveRead

router = APIRouter(tags=['Moves'])

@router.post(
    "/games/{game_id}/moves",
    response_model=MoveRead,
    status_code=status.HTTP_201_CREATED,
)
def create_move(game_id: UUID, move: MoveCreate, db: Session = Depends(get_db)):
    db_game = db.query(Game).filter(Game.id == str(game_id)).first()

    if not db_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    db_move = Move(
        game_id=str(game_id),
        player=move.player,
        row=move.position.row,
        col=move.position.col,
    )

    db.add(db_move)
    db.commit()
    db.refresh(db_move)

    return db_move

@router.get(
    "/games/{game_id}/moves",
    response_model=list[MoveRead],
    status_code=status.HTTP_200_OK,
)
def read_moves_for_game(game_id: UUID, db: Session = Depends(get_db)):
    db_moves = db.query(Move).filter(Move.game_id == str(game_id)).all()
    if not db_moves:
        db_game = db.query(Game).filter(Game.id == str(game_id)).first()
        if not db_game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )

    return db_moves

