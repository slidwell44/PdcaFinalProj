from .base import MyGame
from src.views.game.create_game import GameType


class TicTacToe(MyGame):
    def __init__(self):
        super().__init__(game_type=GameType.TIC_TAC_TOE)