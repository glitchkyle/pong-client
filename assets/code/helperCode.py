# You don't need to edit this file at all unless you really want to
from random import randint
import pygame

TupleRect = tuple[int, int, int ,int]

# This draws the score to the screen
def updateScore(lScore:int, rScore:int, screen:pygame.surface.Surface, color, scoreFont:pygame.font.Font) -> pygame.Rect:
    textSurface = scoreFont.render(f"{lScore}   {rScore}", False, color)
    textRect = textSurface.get_rect()
    screenWidth = screen.get_width()
    textRect.center = ((screenWidth/2)+5, 50)
    return screen.blit(textSurface, textRect)

class Paddle:
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect
        self.moving = ""
        self.speed = 5
    
    def __str__(self) -> None:
        return f"({self.rect[0]}, {self.rect[1]})"
    
    def to_tuple_rect(self) -> TupleRect:
        return (self.rect.x, self.rect.y, self.rect.width, self.rect.height)
    
    def update(self, rect: pygame.Rect) -> None:
        self.rect = rect

class Ball:
    def __init__(self, rect:pygame.Rect, startXvel:int, startYvel:int) -> None:
        self.rect = rect
        self.xVel = startXvel
        self.yVel = startYvel
        self.startXpos = rect.x
        self.startYpos = rect.y

    def to_tuple_rect(self) -> TupleRect:
        return (self.rect.x, self.rect.y, self.rect.width, self.rect.height)
    
    def updatePos(self) -> None:
        self.rect.x += self.xVel
        self.rect.y += self.yVel

    def overridePos(self, rect:pygame.Rect, x_vel:int, y_vel:int) -> None:
        self.rect = rect
        self.xVel = x_vel
        self.yVel = y_vel
    
    def hitPaddle(self, paddleCenter:int) -> None:
        self.xVel *= -1
        self.yVel = (self.rect.center[1] - paddleCenter)//2
    
    def hitWall(self) -> None:
        self.yVel *= -1
    
    def reset(self, nowGoing:str) -> None:
        # nowGoing  The direction the ball should be going after the reset
        self.rect.x = self.startXpos
        self.rect.y = self.startYpos
        self.xVel = -5 if nowGoing == "left" else 5
        self.yVel = 0

    def randomize(self) -> None:
        self.xVel = randint(-5, 5)
        self.yVel = randint(-5, 5)
