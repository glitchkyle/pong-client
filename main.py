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

from assets.code.helperCode import Paddle, Ball, update_score
from config.constants import *
from config.colors import Color
from pong.game import GameState
import requests
from tkinter import messagebox

# This is the main game loop.  For the most part, you will not need to modify this.  The sections
# where you should add to the code are marked.  Feel free to change any part of this project
# to suit your needs.
def play_game(client: socket, game_state: GameState) -> None:
    screen_width, screen_height = game_state.screen_size

    # Pygame inits
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    # Constants
    clock = pygame.time.Clock()
    score_font = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
    win_font = pygame.font.Font("./assets/fonts/visitor.ttf", 32)
    point_sound = pygame.mixer.Sound("./assets/sounds/point.wav")
    bounce_sound = pygame.mixer.Sound("./assets/sounds/bounce.wav")

    # Display objects
    screen = pygame.display.set_mode(game_state.screen_size)
    win_message = pygame.Rect(0,0,0,0)
    top_wall = pygame.Rect(-10,0,screen_width+20, 10)
    bottom_wall = pygame.Rect(-10, screen_height-10, screen_width+20, 10)
    center_line = [pygame.Rect((screen_width/2)-5,i,5,5) for i in range(0, screen_height, 10)]
    play_again_message = pygame.Rect(0,0,50,50)

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
    # Enable us to return to the initial state
    start_state = game_state
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

            if (left_score > MAX_SCORE - 1 or right_score > MAX_SCORE - 1) and event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_message.collidepoint(mouse[0],mouse[1]):
                    playAgain()
        
        def playAgain() -> None:
            current_game_state.again[current_game_state.player_id] = True

        def draw_centered_message(rect:pygame.Rect,font:pygame.font.Font,message:str,antialias:bool,center:tuple[float, float]) -> pygame.Rect:
            text_surface = font.render(message,antialias,Color.WHITE.value, (0,0,0))
            text_rect = text_surface.get_rect()
            text_rect.center = center
            rect = screen.blit(text_surface,text_rect)
            return rect
        # =========================================================================================
        # Your code here to send an update to the server on your paddle's information,
        # where the ball is and the current score.
        # Feel free to change when the score is updated to suit your needs/requirements
        
        
        # =========================================================================================

        # Update the player paddle and opponent paddle's location on the screen
        for paddle in [player_paddle, opponent_paddle]:
            if paddle.moving == "down":
                if paddle.rect.bottomleft[1] < screen_height-10:
                    paddle.rect.y += paddle.speed
            elif paddle.moving == "up":
                if paddle.rect.topleft[1] > 10:
                    paddle.rect.y -= paddle.speed

        mouse:tuple[int, int] = pygame.mouse.get_pos()

        # If the game is over, display the win message
        if left_score > MAX_SCORE - 1 or right_score > MAX_SCORE - 1:
            win_text = "Player 1 Wins! " if left_score > MAX_SCORE - 1 else "Player 2 Wins! "
            draw_centered_message(win_message,win_font,win_text,False,((screen_width/2), screen_height/2))
            if current_game_state.again[current_game_state.player_id] == 0:
                play_again_message = draw_centered_message(play_again_message,win_font,"Play Again",True,((screen_width/2), screen_height/2+90))
            
            if current_game_state.again[int(not current_game_state.player_id)] == 1:
                play_again_message = draw_centered_message(play_again_message, win_font,f"Your opponent wants a rematch",True,((screen_width/2), screen_height/2+90))
        else:

            # ==== Ball Logic =====================================================================
            if current_game_state.start:
                ball.update_pos()
            else:
                win_text = "Waiting for opponent"
                draw_centered_message(win_message,win_font,win_text,False,((screen_width/2), screen_height/2))

            # If the ball makes it past the edge of the screen, update score, etc.
            if ball.rect.x > screen_width:
                left_score += 1
                point_sound.play()
                ball.reset(now_going="left")
            elif ball.rect.x < 0:
                right_score += 1
                point_sound.play()
                ball.reset(now_going="right")
            
            # If the ball hits a paddle
            if ball.rect.colliderect(player_paddle.rect):
                bounce_sound.play()
                ball.hit_paddle(player_paddle.rect.center[1])
            elif ball.rect.colliderect(opponent_paddle.rect):
                bounce_sound.play()
                ball.hit_paddle(opponent_paddle.rect.center[1])
                
            # If the ball hits a wall
            if ball.rect.colliderect(top_wall) or ball.rect.colliderect(bottom_wall):
                bounce_sound.play()
                ball.hit_wall()
            
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
        scoreRect = update_score(left_score, right_score, screen, Color.WHITE.value, score_font)
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
        current_game_state.ball_velocity = (ball.x_vel, ball.y_vel)

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
            ball.override_pos(pygame.Rect(x, y, w, h), x_vel, y_vel)

        if current_game_state.again == [True,True]:
            left_score = 0
            right_score = 0
            current_game_state = start_state

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
def join_server(ip: str, port: str, app: Tk,username:str,password:str) -> None:
    # Purpose:      This method is fired when the join button is clicked
    # Arguments:
    # ip            A string holding the IP address of the server
    # port          A string holding the port the server is using
    # app           The tk window object, needed to kill the window
    
    # Create a socket and connect to the server
    # You don't have to use SOCK_STREAM, use what you think is best

    api_url = f"http://{ip}:8000/app/api/authenticate/"

    data_to_send = {
        "username": username,
        "password": password
    }

    response = requests.post(api_url, json=data_to_send)

    if response.status_code == 200:
        response_data = response.json()
        if response_data == {'message': 'Authentication successful'}:
            print("Authentication successful")
        else:
            messagebox.showerror("Authentication Failed", "Incorrect username or password. Please try again.")
   
        client = socket(AF_INET, SOCK_STREAM)

        # Get the required information from your server (screen width, height & player paddle, "left or "right)
        client.connect((ip, int(port)))
        client.send(username.encode())
        received_data = client.recv(BUFFER_SIZE)
        initial_received_game_state: GameState = loads(received_data)
        initial_received_game_state.player_name = username
        # Close this window and start the game with the info passed to you from the server
        app.withdraw()                                      # Hides the window (we'll kill it later)
        play_game(client, initial_received_game_state)       # User will be either left or right paddle
        app.quit()                                          # Kills the window
    else:
        messagebox.showerror("Authentication Error", "Incorrect username or password. Type the correct username and password, and try again")

# This displays the opening screen, you don't need to edit this (but may if you like)
def start_screen():
    app = Tk()
    app.title("Server Info")

    image = PhotoImage(file="./assets/images/logo.png")

    title_label = Label(image=image)
    title_label.grid(column=0, row=0, columnspan=2)
    # IP
    ip_label = Label(text="Server IP:")
    ip_label.grid(column=0, row=1, sticky="W", padx=8)

    ip_entry = Entry(app)
    ip_entry.grid(column=1, row=1)
    ip_entry.insert(END, DEFAULT_SOCKET_IP)
    # PORT
    port_label = Label(text="Server Port:")
    port_label.grid(column=0, row=2, sticky="W", padx=8)

    port_entry = Entry(app)
    port_entry.grid(column=1, row=2)
    port_entry.insert(END, DEFAULT_SOCKET_PORT)
    # Username
    username_label = Label(text="Username:")
    username_label.grid(column=0, row=3, sticky="W", padx=8)

    username_entry = Entry(app)
    username_entry.grid(column=1, row=3)
    username_entry.insert(END, "")
    # Password
    password_label = Label(text="Password:")
    password_label.grid(column=0, row=4, sticky="W", padx=8)

    password_entry = Entry(app)
    password_entry.grid(column=1, row=4)
    password_entry.insert(END, "")

    join_button = Button(text="Join", command=lambda: join_server(ip_entry.get(), port_entry.get(), app,username_entry.get(),password_entry.get()))
    join_button.grid(column=0, row=5, columnspan=2)

    app.mainloop()

def main():
    start_screen()

if __name__ == "__main__":
    main()