from abc import ABC, abstractmethod
import json
from typing import Optional

import httpx

from src.views.game import GameRead, UpdateWinnerRequest
from src.views.game.update_game_winner import WinnerEnum
from src.views.move import MoveRead


class MyGame(ABC):
    def __init__(self, game_type: str):
        self._url = "http://localhost:8000"
        self._games_url = f"{self._url}/games"
        self.game_type = game_type
        self.game_over = False
        self.player_turn: str = 'X'

        self.current_game: GameRead = self.get_or_create_game()
        self._moves_url = f"{self._games_url}/{self.current_game.id}/moves"

    def get_or_create_game(self) -> GameRead:
        try:
            response = httpx.get(f"{self._games_url}/{self.current_game.id}")
            response.raise_for_status()
            return GameRead(**response.json())
        except AttributeError:
            response = httpx.post(f"{self._games_url}/{self.game_type}")
            response.raise_for_status()
            return GameRead(**response.json())
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Failed to get or create game: {e.response.text}")

    def update_game_winner(self, winner: WinnerEnum) -> GameRead:
        try:
            winner_request = UpdateWinnerRequest(winner=winner)
            response = httpx.put(
                f"{self._games_url}/{self.current_game.id}/winner",
                json=winner_request.model_dump(),
            )
            response.raise_for_status()
            return GameRead(**response.json())
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Failed to update game winner: {e.response.text}") from e

    def delete_game(self, game_id: str) -> None:
        """
        Delete a game by ID.
        """
        try:
            response = httpx.delete(f"{self._games_url}/{game_id}")
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Failed to delete game: {e.response.text}")

    @abstractmethod
    def print_board(self):
        ...

    def get_moves(self) -> list[MoveRead]:
        try:
            response = httpx.get(self._moves_url)
            response.raise_for_status()
            return [MoveRead(**item) for item in response.json()]
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Failed to get moves: {e}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to decode JSON response: {e}") from e

    def _cleanup(self):
        print("Cleaning up game resources.")
        self.current_game = None
        self._moves_url = None
