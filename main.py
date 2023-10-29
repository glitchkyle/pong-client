# =================================================================================================
# Contributing Authors:	    <Anyone who touched the code>
# Email Addresses:          <Your uky.edu email addresses>
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import pygame
import sys
from pickle import loads, dumps
from socket import socket, AF_INET, SOCK_STREAM
from tkinter import Tk, Entry, PhotoImage, Label, Button, END
from random import randint

from assets.code.helperCode import Paddle, Ball, updateScore
from config.constants import *
from config.colors import Color
from pong.game import GameState

# This is the main game loop.  For the most part, you will not need to modify this.  The sections
# where you should add to the code are marked.  Feel free to change any part of this project
# to suit your needs.
def playGame(client: socket, game_state: GameState) -> None:
    screen_width, screen_height = game_state.screen_size

    # Pygame inits
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    # Constants
    clock = pygame.time.Clock()
    score_font = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
    win_font = pygame.font.Font("./assets/fonts/visitor.ttf", 48)
    point_sound = pygame.mixer.Sound("./assets/sounds/point.wav")
    bounce_sound = pygame.mixer.Sound("./assets/sounds/bounce.wav")

    # Display objects
    screen = pygame.display.set_mode(game_state.screen_size)
    win_message = pygame.Rect(0,0,0,0)
    top_wall = pygame.Rect(-10,0,screen_width+20, 10)
    bottom_wall = pygame.Rect(-10, screen_height-10, screen_width+20, 10)
    center_line = [pygame.Rect((screen_width/2)-5,i,5,5) for i in range(0, screen_height, 10)]

    # Paddle properties and init
    paddle_start_pos_y = (screen_height/2)-(PADDLE_HEIGHT/2)
    left_paddle = Paddle(pygame.Rect(10,paddle_start_pos_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    right_paddle = Paddle(pygame.Rect(screen_width-20, paddle_start_pos_y, PADDLE_WIDTH, PADDLE_HEIGHT))

    x_vel, y_vel = game_state.ball_velocity
    x, y, w, h = game_state.ball
    ball = Ball(pygame.Rect(x, y, w, h), x_vel, y_vel)

    if game_state.player_id == 0:
        # I am the player who initiated the game
        opponent_paddle = right_paddle
        player_paddle = left_paddle
    else:
        # I am the player who joined the game
        opponent_paddle = left_paddle
        player_paddle = right_paddle

    left_score = right_score = sync = 0

    current_game_state = game_state
    while True:
        # Wiping the screen
        screen.fill(Color.BLACK.value)

        # Getting keypress events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    player_paddle.moving = "down"
                elif event.key == pygame.K_UP:
                    player_paddle.moving = "up"
                elif ENV == Environment.DEVELOPMENT.value and event.key == pygame.K_x:
                    # [DEBUG] Simulate out of synchronization
                    sync -= randint(1, 3)
                    ball.randomize()
            elif event.type == pygame.KEYUP:
                player_paddle.moving = ""

        # Update the player paddle and opponent paddle's location on the screen
        for paddle in [player_paddle, opponent_paddle]:
            if paddle.moving == "down":
                if paddle.rect.bottomleft[1] < screen_height-10:
                    paddle.rect.y += paddle.speed
            elif paddle.moving == "up":
                if paddle.rect.topleft[1] > 10:
                    paddle.rect.y -= paddle.speed

        # If the game is over, display the win message
        if left_score > MAX_SCORE - 1 or right_score > MAX_SCORE - 1:
            winText = "Player 1 Wins! " if left_score > 4 else "Player 2 Wins! "
            text_surface = win_font.render(winText, False, Color.WHITE.value, Color.BLACK.value)
            textRect = text_surface.get_rect()
            textRect.center = ((screen_width/2), screen_height/2)
            win_message = screen.blit(text_surface, textRect)
        else:

            # ==== Ball Logic =====================================================================
            if current_game_state.start:
                ball.updatePos()
            else:
                winText = "Waiting for opponent"
                text_surface = win_font.render(winText, False, Color.WHITE.value, Color.BLACK.value)
                textRect = text_surface.get_rect()
                textRect.center = ((screen_width/2), screen_height/2)
                win_message = screen.blit(text_surface, textRect)

            # If the ball makes it past the edge of the screen, update score, etc.
            if ball.rect.x > screen_width:
                left_score += 1
                point_sound.play()
                ball.reset(nowGoing="left")
            elif ball.rect.x < 0:
                right_score += 1
                point_sound.play()
                ball.reset(nowGoing="right")
            
            # If the ball hits a paddle
            if ball.rect.colliderect(player_paddle.rect):
                bounce_sound.play()
                ball.hitPaddle(player_paddle.rect.center[1])
            elif ball.rect.colliderect(opponent_paddle.rect):
                bounce_sound.play()
                ball.hitPaddle(opponent_paddle.rect.center[1])
                
            # If the ball hits a wall
            if ball.rect.colliderect(top_wall) or ball.rect.colliderect(bottom_wall):
                bounce_sound.play()
                ball.hitWall()
            
            pygame.draw.rect(screen, Color.WHITE.value, ball)
            # ==== End Ball Logic =================================================================

        # Drawing the dotted line in the center
        if current_game_state.start:
            for i in center_line:
                pygame.draw.rect(screen, Color.WHITE.value, i)
        
        # Drawing the player's new location
        for paddle in [player_paddle, opponent_paddle]:
            pygame.draw.rect(screen, Color.WHITE.value, paddle)

        pygame.draw.rect(screen, Color.WHITE.value, top_wall)
        pygame.draw.rect(screen, Color.WHITE.value, bottom_wall)
        scoreRect = updateScore(left_score, right_score, screen, Color.WHITE.value, score_font)
        pygame.display.update([top_wall, bottom_wall, ball, left_paddle, right_paddle, scoreRect, win_message])
        clock.tick(GAME_CLOCK_SPEED)
        
        # This number should be synchronized between you and your opponent.  If your number is larger
        # then you are ahead of them in time, if theirs is larger, they are ahead of you, and you need to
        # catch up (use their info)
        sync += 1

        # Send latest information to server

        # Send Paddles
        current_game_state.paddle_rect = [None, None]
        if current_game_state.player_id == 0:
            # I am the player who initiated the game
            current_game_state.paddle_rect[0] = left_paddle.to_tuple_rect()
        else:
            # I am the player who joined the game
            current_game_state.paddle_rect[1] = right_paddle.to_tuple_rect()

        # Send Ball
        current_game_state.ball = ball.to_tuple_rect()
        current_game_state.ball_velocity = (ball.xVel, ball.yVel)

        # Send Score
        current_game_state.scores = (left_score, right_score)

        # Send Sync
        current_game_state.sync = sync

        serialized_game_state = dumps(current_game_state)
        client.sendall(serialized_game_state)

        # Receive latest information from server

        # Fetch information
        received_data = client.recv(BUFFER_SIZE)
        received_game_state: GameState = loads(received_data)

        # Update from information from server
        current_game_state = received_game_state

        if current_game_state.sync > sync:
            sync = current_game_state.sync

            # Update Score
            left_score, right_score = current_game_state.scores

            # Update Ball
            x_vel, y_vel = current_game_state.ball_velocity
            x, y, w, h = current_game_state.ball
            ball.overridePos(pygame.Rect(x, y, w, h), x_vel, y_vel)

        # Update Paddles
        if current_game_state.player_id == 0:
            # If I am the left player
            if current_game_state.paddle_rect[0] is not None:
                # Update my paddle
                x, y, w, h = current_game_state.paddle_rect[0]
                player_paddle.update(pygame.Rect(x, y, w, h))
            if current_game_state.paddle_rect[1] is not None:
                # Update opponent paddle
                x, y, w, h = current_game_state.paddle_rect[1]
                opponent_paddle.update(pygame.Rect(x, y, w, h))
        else:
            # If I am the right player
            if current_game_state.paddle_rect[0] is not None:
                # Update opponent paddle
                x, y, w, h = current_game_state.paddle_rect[0]
                opponent_paddle.update(pygame.Rect(x, y, w, h))
            if current_game_state.paddle_rect[1] is not None:
                # Update my paddle
                x, y, w, h = current_game_state.paddle_rect[1]
                player_paddle.update(pygame.Rect(x, y, w, h))
        

# This is where you will connect to the server to get the info required to call the game loop.  Mainly
# the screen width, height and player paddle (either "left" or "right")
# If you want to hard code the screen's dimensions into the code, that's fine, but you will need to know
# which client is which
def joinServer(ip: str, port: str, app: Tk) -> None:
    # Purpose:      This method is fired when the join button is clicked
    # Arguments:
    # ip            A string holding the IP address of the server
    # port          A string holding the port the server is using
    # app           The tk window object, needed to kill the window
    
    # Create a socket and connect to the server
    # You don't have to use SOCK_STREAM, use what you think is best
    client = socket(AF_INET, SOCK_STREAM)

    # Get the required information from your server (screen width, height & player paddle, "left or "right)
    client.connect((ip, int(port)))

    received_data = client.recv(BUFFER_SIZE)
    initial_received_game_state: GameState = loads(received_data)

    # Close this window and start the game with the info passed to you from the server
    app.withdraw()                                      # Hides the window (we'll kill it later)
    playGame(client, initial_received_game_state)       # User will be either left or right paddle
    app.quit()                                          # Kills the window


# This displays the opening screen, you don't need to edit this (but may if you like)
def startScreen():
    app = Tk()
    app.title("Server Info")

    image = PhotoImage(file="./assets/images/logo.png")

    titleLabel = Label(image=image)
    titleLabel.grid(column=0, row=0, columnspan=2)

    ipLabel = Label(text="Server IP:")
    ipLabel.grid(column=0, row=1, sticky="W", padx=8)

    ipEntry = Entry(app)
    ipEntry.grid(column=1, row=1)
    ipEntry.insert(END, DEFAULT_SOCKET_IP)

    portLabel = Label(text="Server Port:")
    portLabel.grid(column=0, row=2, sticky="W", padx=8)

    portEntry = Entry(app)
    portEntry.grid(column=1, row=2)
    portEntry.insert(END, DEFAULT_SOCKET_PORT)

    joinButton = Button(text="Join", command=lambda: joinServer(ipEntry.get(), portEntry.get(), app))
    joinButton.grid(column=0, row=3, columnspan=2)

    app.mainloop()

def main():
    startScreen()

if __name__ == "__main__":
    main()