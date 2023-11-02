# You don't need to edit this file at all unless you really want to
from random import randint
import pygame

TupleRect = tuple[int, int, int ,int]

# This draws the score to the screen
def update_score(left_score:int, right_score:int, screen:pygame.surface.Surface, color, score_font:pygame.font.Font) -> pygame.Rect:
    text_surface = score_font.render(f"{left_score}   {right_score}", False, color)
    text_rect = text_surface.get_rect()
    screen_width = screen.get_width()
    text_rect.center = ((screen_width/2)+5, 50)
    return screen.blit(text_surface, text_rect)

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
    def __init__(self, rect:pygame.Rect, start_x_vel:int, start_y_vel:int) -> None:
        self.rect = rect
        self.x_vel = start_x_vel
        self.y_vel = start_y_vel
        self.start_x_pos = rect.x
        self.start_y_pos = rect.y

    def to_tuple_rect(self) -> TupleRect:
        return (self.rect.x, self.rect.y, self.rect.width, self.rect.height)
    
    def update_pos(self) -> None:
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

    def override_pos(self, rect:pygame.Rect, x_vel:int, y_vel:int) -> None:
        self.rect = rect
        self.x_vel = x_vel
        self.y_vel = y_vel
    
    def hit_paddle(self, paddle_center:int) -> None:
        self.x_vel *= -1
        self.y_vel = (self.rect.center[1] - paddle_center)//2
    
    def hit_wall(self) -> None:
        self.y_vel *= -1
    
    def reset(self, now_going:str) -> None:
        # now_going  The direction the ball should be going after the reset
        self.rect.x = self.start_x_pos
        self.rect.y = self.start_y_pos
        self.x_vel = -5 if now_going == "left" else 5
        self.y_vel = 0

    def randomize(self) -> None:
        self.x_vel = randint(-5, 5)
        self.y_vel = randint(-5, 5)
