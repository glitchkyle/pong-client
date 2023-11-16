"""
Contributing Authors:	  Nishan Budathoki, James Chen, Kyle Lastimos
Email Addresses:          nishan.budhathoki@uky.edu, James.Chen@uky.edu, klastimosa001@uky.edu
Date:                     Nov 11,2023
Purpose:                  Define the GameState Class
ChatGPT generated some of these comments for the function
"""
from config.constants import DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT

TupleRect = tuple[int, int, int ,int]

class GameState(object):
    """
    Author:       Kyle Lastimosa
    Purpose:      Defines the JSON object exchanged between client and server, enabling efficient game updates by managing and tracking the dynamic state.
    Pre:          The game is initialized.
    Post:         Enables the game to accurately track and manage its state at any given moment.
    """
    def __init__(self):
        """
        Author:       Kyle Lastimosa
        Purpose:      Initializes the GameState instance.
        Pre:          (Optional) Any specific preconditions for object instantiation.
        Post:         The GameState instance is properly initialized.
        """
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