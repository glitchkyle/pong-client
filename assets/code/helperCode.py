"""
Contributing Authors:	  Nishan Budathoki, James Chen, Kyle Lastimos
Email Addresses:          nishan.budhathoki@uky.edu, James.Chen@uky.edu, klastimosa001@uky.edu
Date:                     Nov 11,2023
Purpose:                  Utility Functions for Pong Game Mechanics
ChatGPT generated some of these comments for the function
"""

from random import randint
from pygame import Rect
from pygame.surface import Surface
from pygame.font import Font

TupleRect = tuple[int, int, int ,int]

# This draws the score to the screen
def update_score(left_score:int, right_score:int, screen:Surface, color, score_font:Font) -> Rect:
    """
    Author:       Kyle Lastimosa
    Purpose:      Updates and displays the game score on the screen.
    Pre:          Assumes the game state, screen, color, and font are properly configured.
    Post:         Returns the Rect object representing the updated score display position.
    """
    text_surface = score_font.render(f"{left_score}   {right_score}", False, color)
    text_rect = text_surface.get_rect()
    screen_width = screen.get_width()
    text_rect.center = ((screen_width/2)+5, 50)
    return screen.blit(text_surface, text_rect)

class Paddle:
    """
    Author:       Kyle Lastimosa
    Purpose:      Represents a paddle in the game, handling movement and position updates.
    Pre:          Assumes the object's initial state is set appropriately for game initiation.
    Post:         The Paddle instance is properly initialized.
    """
    def __init__(self, rect: Rect) -> None:
        """
        Author:       Kyle Lastimosa
        Purpose:      Initializes the Paddle instance.
        Pre:          Assumes the object's initial state is set appropriately for game initiation.
        Post:         The Paddle instance is properly initialized.
        
        Parameters:
        - rect: The Rect object defining the initial position and size of the paddle.
        """
        self.rect = rect
        self.moving = ""
        self.speed = 5
    
    def __str__(self) -> None:
        """
        Author:       Kyle Lastimosa
        Purpose:      Returns a string representation of the Paddle's current position.
        Pre:          Assumes the object's initial state is set.
        Post:         Allows for observing the Paddle's position as a string.
        """
        return f"({self.rect[0]}, {self.rect[1]})"
    
    def to_tuple_rect(self) -> TupleRect:
        """
        Author:       Kyle Lastimosa
        Purpose:      Converts the object's Rect into a tuple format.
        Pre:          Assumes the object's initial state is set.
        Post:         Returns a tuple representing the Rect object's (x, y, width, height).
        """
        return (self.rect.x, self.rect.y, self.rect.width, self.rect.height)
    
    def update(self, rect: Rect) -> None:
        """
        Author:       Kyle Lastimosa
        Purpose:      Updates the Paddle's position.
        Pre:          Assumes the object's initial state is set.
        Post:         Updates the Paddle's position based on the provided Rect parameter.
        
        Parameters:
        - rect:  The Rect object defining the new position and size of the paddle.
        """
        self.rect = rect

class Ball:
    """
    Author:       Kyle Lastimosa
    Purpose:      Represents a ball in the game, handling movement, collisions, and resets.
    Pre:          Assumes the object's initial state is set appropriately for game initiation.
    Post:         Methods provide functionality for updating, resetting, and randomizing the ball's state.
    """
    def __init__(self, rect:Rect, start_x_vel:int, start_y_vel:int) -> None:
        """
        Author:       Kyle Lastimosa
        Purpose:      Initializes the Ball instance.
        Pre:          (Optional) Any specific preconditions for object instantiation.
        Post:         The Ball instance is properly initialized.

        Parameters:
        - rect:         The Rect object defining the initial position.
        - start_x_vel:  The initial horizontal velocity.
        - start_y_vel:  The initial vertical velocity.
        """
        self.rect = rect
        self.x_vel = start_x_vel
        self.y_vel = start_y_vel
        self.start_x_pos = rect.x
        self.start_y_pos = rect.y

    def to_tuple_rect(self) -> TupleRect:
        """
        Author:       Kyle Lastimosa
        Purpose:      Converts the object's Rect into a tuple format.
        Pre:          Assumes the object's initial state is set.
        Post:         Returns a tuple representing the Rect object's (x, y, width, height).
        """
        return (self.rect.x, self.rect.y, self.rect.width, self.rect.height)
    
    def update_pos(self) -> None:
        """
        Author:       Kyle Lastimosa
        Purpose:      Update the current postion of the object with specified horizontal and vertical velocity
        Pre:          Assume the object's initial state is set
        Post:         Update the object's position and velocity based on specified horizontal and vertical velocity
        """
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

    def override_pos(self, rect:Rect, x_vel:int, y_vel:int) -> None:
        """
        Author:       Kyle Lastimosa
        Purpose:      Overrides the current position and velocity of the object with specified values.
        Pre:          Assumes the object's initial state is set.
        Post:         Updates the object's position and velocity based on the provided parameters.
        
        Parameters:
        - rect:     The Rect object defining the new position.
        - x_vel:    The new horizontal velocity.
        - y_vel:    The new vertical velocity.
        """
        self.rect = rect
        self.x_vel = x_vel
        self.y_vel = y_vel
    
    def hit_paddle(self, paddle_center:int) -> None:
        """
        Author:       Kyle Lastimosa
        Purpose:      Handles the collision with a paddle, reversing horizontal velocity and adjusting vertical velocity.
        Pre:          Assumes the object's initial state is set.
        Post:         Reverses the x_vel and adjusts y_vel based on the distance from the paddle's center.
        
        Parameters:
        - paddle_center:  The y-coordinate of the center of the paddle that the object collided with.
        """
        self.x_vel *= -1
        self.y_vel = (self.rect.center[1] - paddle_center)//2
    
    def hit_wall(self) -> None:
        """
        Author:       Kyle Lastimosa
        Purpose:      Reverses the vertical velocity when the object hits a wall to simulate hitting a wall
        Pre:          Assumes the object's initial state is set.
        Post:         Negates the y_vel, causing a change in vertical direction.
        """
        self.y_vel *= -1
    
    def reset(self, now_going:str) -> None:
        """
        Author:       Kyle Lastimosa
        Purpose:      Resets the object's position and velocity based on the specified direction.
        Pre:          Assumes the object's initial state is set.
        Post:         Updates the object's position to its starting coordinates, sets the velocity
                        based on the specified direction ('left' for -5, 'right' for 5), and resets
                        the y_vel to 0.
        Parameters:
        - now_going:  The direction the object should be going after the reset ('left' or 'right').
        """

        # now_going  The direction the ball should be going after the reset
        self.rect.x = self.start_x_pos
        self.rect.y = self.start_y_pos
        self.x_vel = -5 if now_going == "left" else 5
        self.y_vel = 0

    def randomize(self) -> None:
        """
        Author:       Kyle Lastimosa
        Purpose:      Randomizes the velocity of the object.
        Pre:          Assumes the object's initial game state is set.
        Post:         Updates the object's x_vel and y_vel with random values in the range [-5, 5].
        """
        self.x_vel = randint(-5, 5)
        self.y_vel = randint(-5, 5)
