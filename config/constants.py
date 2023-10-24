from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

ENV = Environment.DEVELOPMENT.value

PADDLE_HEIGHT = 50
PADDLE_WIDTH = 10

DEFAULT_SCREEN_HEIGHT = 480
DEFAULT_SCREEN_WIDTH = 640

GAME_CLOCK_SPEED = 60

BUFFER_SIZE = 1024 * 4

MAX_SCORE = 5