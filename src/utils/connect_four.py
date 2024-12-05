from .base import MyGame
from src.views.game.create_game import GameType


class ConnectFour(MyGame):
    def __init__(self):
        super().__init__(game_type=GameType.CONNECT_4)