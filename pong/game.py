from pygame import Rect

from config.constants import DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT

class GameState(object):
    # Read Only
    game_id: str
    player_id: str
    screen_size: tuple[int, int] = (DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT)

    # Read and Write
    ball: Rect = None
    ball_velocity: tuple[int, int] = (0, 0)
    paddle_rect: list[Rect] = [None,None]
    scores: tuple[int, int] = (0, 0)