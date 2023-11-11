from config.constants import DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT

TupleRect = tuple[int, int, int ,int]

class GameState(object):
    def __init__(self):
        # Read Only
        self.game_id: str
        self.player_id: int
        self.player_name: str
        self.screen_size: tuple[int, int] = (DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT)

        # Read and Write
        self.sync = 0
        self.start: bool = False
        self.scores: tuple[int, int] = (0, 0)
        self.paddle_rect: list[TupleRect | None] = [None, None]
        self.ball: TupleRect = None
        self.ball_velocity: tuple[int, int] = (0, 0)
        self.again: list[bool] = [False,False]