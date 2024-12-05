import httpx

from src.views.game import GameRead
from src.views.game.create_game import GameType


class MyGame:
    def __init__(self, game_type: GameType):
        self._url = "http://localhost:8000"
        self._games_url = f"{self._url}/games/"

        self.current_game: GameRead = self.get_or_create_game(game_type)

    def get_or_create_game(self, game_type: GameType) -> GameRead:
        """
        Create a new game or retrieve an existing active game.
        """
        try:
            response = httpx.post(self._games_url, json={"game_type": game_type})
            response.raise_for_status()
            return GameRead(**response.json())
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Failed to create game: {e.response.text}")

    def get_game(self) -> GameRead:
        """
        Fetch game details by ID.
        """
        try:
            response = httpx.get(f"{self._games_url}{self.current_game.id}")
            response.raise_for_status()
            return GameRead(**response.json())
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Failed to fetch game: {e.response.text}")

    def update_game_winner(self, winner: str) -> GameRead:
        """
        Update the winner for the current game.
        """
        try:
            response = httpx.put(
                f"{self._games_url}{self.current_game.id}",
                json={"winner": winner}
            )
            response.raise_for_status()
            return GameRead(**response.json())
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Failed to update game winner: {e.response.text}")

    def delete_game(self, game_id: str) -> None:
        """
        Delete a game by ID.
        """
        try:
            response = httpx.delete(f"{self._games_url}{game_id}")
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Failed to delete game: {e.response.text}")

    def is_game_over(self) -> bool:
        """
        Check if the current game is over (winner is not None).
        """
        return self.current_game.winner is not None

    def refresh_game(self) -> None:
        """
        Refresh the current game details from the server.
        """
        self.current_game = self.get_game()
