# =================================================================================================
# Contributing Authors:	    <Anyone who touched the code>
# Email Addresses:          <Your uky.edu email addresses>
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import pygame
import sys
import pickle
from socket import socket, AF_INET, SOCK_STREAM
from tkinter import Tk, Entry, PhotoImage, Label, Button

from assets.code.helperCode import Paddle, Ball, updateScore
from config.constants import *
from config.colors import COLORS
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
    scoreFont = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
    winFont = pygame.font.Font("./assets/fonts/visitor.ttf", 48)
    pointSound = pygame.mixer.Sound("./assets/sounds/point.wav")
    bounceSound = pygame.mixer.Sound("./assets/sounds/bounce.wav")

    # Display objects
    screen = pygame.display.set_mode(game_state.screen_size)
    winMessage = pygame.Rect(0,0,0,0)
    topWall = pygame.Rect(-10,0,screen_width+20, 10)
    bottomWall = pygame.Rect(-10, screen_height-10, screen_width+20, 10)
    centerLine = [pygame.Rect((screen_width/2)-5,i,5,5) for i in range(0, screen_height, 10)]

    # Paddle properties and init
    paddleStartPosY = (screen_height/2)-(PADDLE_HEIGHT/2)
    leftPaddle = Paddle(pygame.Rect(10,paddleStartPosY, PADDLE_WIDTH, PADDLE_HEIGHT))
    rightPaddle = Paddle(pygame.Rect(screen_width-20, paddleStartPosY, PADDLE_WIDTH, PADDLE_HEIGHT))

    x_vel, y_vel = game_state.ball_velocity
    ball = Ball(game_state.ball, x_vel, y_vel)

    if game_state.player_id == 0:
        # I am the player who initiated the game
        opponentPaddleObj = rightPaddle
        playerPaddleObj = leftPaddle
    else:
        # I am the player who joined the game
        opponentPaddleObj = leftPaddle
        playerPaddleObj = rightPaddle

    lScore = rScore = sync = 0

    current_game_state = game_state
    while True:
        start = current_game_state.player_two_paddle_rect is not None
        print(start)

        # Wiping the screen
        screen.fill((0,0,0))

        # Getting keypress events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    playerPaddleObj.moving = "down"

                elif event.key == pygame.K_UP:
                    playerPaddleObj.moving = "up"

            elif event.type == pygame.KEYUP:
                playerPaddleObj.moving = ""

        # =========================================================================================
        # Your code here to send an update to the server on your paddle's information,
        # where the ball is and the current score.
        # Feel free to change when the score is updated to suit your needs/requirements
        
        
        # =========================================================================================

        # Update the player paddle and opponent paddle's location on the screen
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            if paddle.moving == "down":
                if paddle.rect.bottomleft[1] < screen_height-10:
                    paddle.rect.y += paddle.speed
            elif paddle.moving == "up":
                if paddle.rect.topleft[1] > 10:
                    paddle.rect.y -= paddle.speed

        # If the game is over, display the win message
        if lScore > 4 or rScore > 4:
            winText = "Player 1 Wins! " if lScore > 4 else "Player 2 Wins! "
            textSurface = winFont.render(winText, False, COLORS["WHITE"], (0,0,0))
            textRect = textSurface.get_rect()
            textRect.center = ((screen_width/2), screen_height/2)
            winMessage = screen.blit(textSurface, textRect)
        else:

            # ==== Ball Logic =====================================================================
            if start is True:
                ball.updatePos()
            else:
                winText = "Waiting for opponent"
                textSurface = winFont.render(winText, False, COLORS["WHITE"], (0,0,0))
                textRect = textSurface.get_rect()
                textRect.center = ((screen_width/2), screen_height/2)
                winMessage = screen.blit(textSurface, textRect)

            # If the ball makes it past the edge of the screen, update score, etc.
            if ball.rect.x > screen_width:
                lScore += 1
                pointSound.play()
                ball.reset(nowGoing="left")
            elif ball.rect.x < 0:
                rScore += 1
                pointSound.play()
                ball.reset(nowGoing="right")
            
            # If the ball hits a paddle
            if ball.rect.colliderect(playerPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(playerPaddleObj.rect.center[1])
            elif ball.rect.colliderect(opponentPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(opponentPaddleObj.rect.center[1])
                
            # If the ball hits a wall
            if ball.rect.colliderect(topWall) or ball.rect.colliderect(bottomWall):
                bounceSound.play()
                ball.hitWall()
            
            pygame.draw.rect(screen, COLORS["WHITE"], ball)
            # ==== End Ball Logic =================================================================

        # Drawing the dotted line in the center
        if start is True:
            for i in centerLine:
                pygame.draw.rect(screen, COLORS["WHITE"], i)
        
        # Drawing the player's new location
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            pygame.draw.rect(screen, COLORS["WHITE"], paddle)

        pygame.draw.rect(screen, COLORS["WHITE"], topWall)
        pygame.draw.rect(screen, COLORS["WHITE"], bottomWall)
        scoreRect = updateScore(lScore, rScore, screen, COLORS["WHITE"], scoreFont)
        pygame.display.update([topWall, bottomWall, ball, leftPaddle, rightPaddle, scoreRect, winMessage])
        clock.tick(GAME_CLOCK_SPEED)
        
        # This number should be synchronized between you and your opponent.  If your number is larger
        # then you are ahead of them in time, if theirs is larger, they are ahead of you, and you need to
        # catch up (use their info)
        sync += 1
        # =========================================================================================
        # Send your server update here at the end of the game loop to sync your game with your
        # opponent's game

        # =========================================================================================

        game_state.ball = ball.rect
        game_state.ball_velocity = (ball.xVel, ball.yVel)

        if game_state.player_id == 0:
            # I am the player who initiated the game
            game_state.player_one_paddle_rect = leftPaddle.rect
        else:
            # I am the player who joined the game
            game_state.player_two_paddle_rect = rightPaddle.rect

        game_state.scores = (lScore, rScore)

        client.sendall(pickle.dumps(current_game_state))
        received_data = client.recv(BUFFER_SIZE)
        current_game_state = pickle.loads(received_data)

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

    initial_received_game_state: GameState = pickle.loads(client.recv(BUFFER_SIZE))

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

    portLabel = Label(text="Server Port:")
    portLabel.grid(column=0, row=2, sticky="W", padx=8)

    portEntry = Entry(app)
    portEntry.grid(column=1, row=2)

    joinButton = Button(text="Join", command=lambda: joinServer(ipEntry.get(), portEntry.get(), app))
    joinButton.grid(column=0, row=3, columnspan=2)

    app.mainloop()

def main():
    startScreen()

if __name__ == "__main__":
    main()