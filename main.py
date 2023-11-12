"""
Contributing Authors:	  Nishan Budathoki, James Chen, Kyle Lastimos
Email Addresses:          nishan.budhathoki@uky.edu, James.Chen@uky.edu, klastimosa001@uky.edu
Date:                     Nov 11,2023
Purpose:                  This file contains the implementation of a Pong game using the Pygame library and Tkinter for user input. 
                          It establishes connections with a server, handles user authentication, and manages the game loop.
                          The game involves two players controlling paddles to bounce a ball back and forth, aiming to score points.
"""

import pygame
from pygame import Rect, init
from pygame.draw import rect
from pygame import display
from pygame.font import Font
from pygame.mixer import pre_init, Sound
from pygame.time import Clock

import sys
from pickle import loads, dumps
from socket import socket, AF_INET, SOCK_STREAM
from tkinter import Tk, Entry, PhotoImage, Label, Button, END,messagebox

from assets.code.helperCode import Paddle, Ball, update_score

from config.constants import *
from config.colors import Color

from pong.game import GameState
import ssl

def play_game(client: socket, game_state: GameState) -> None:
    """
    Author:              James Chen, Kyle Lastimosa
    Purpose:             Play the Pong game with the provided client and game state.
    Pre:                 Assumes a valid client connection and initialized game state.
    Post:                Manages the game loop, updates positions, handles collisions, and sends/receives game state data.
    """
    screen_width, screen_height = game_state.screen_size

    # Pygame inits
    pre_init(44100, -16, 2, 2048)
    init()

    # Constants
    clock = Clock()
    score_font = Font("./assets/fonts/pong-score.ttf", 32)
    win_font = Font("./assets/fonts/visitor.ttf", 32)
    point_sound = Sound("./assets/sounds/point.wav")
    bounce_sound = Sound("./assets/sounds/bounce.wav")

    # Display objects
    screen = display.set_mode(game_state.screen_size)
    win_message = Rect(0,0,0,0)
    top_wall = Rect(-10,0,screen_width+20, 10)
    bottom_wall = Rect(-10, screen_height-10, screen_width+20, 10)
    center_line = [Rect((screen_width/2)-5,i,5,5) for i in range(0, screen_height, 10)]
    play_again_message = Rect(0,0,50,50)

    # Paddle properties and init
    paddle_start_pos_y = (screen_height/2)-(PADDLE_HEIGHT/2)
    left_paddle = Paddle(Rect(10,paddle_start_pos_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    right_paddle = Paddle(Rect(screen_width-20, paddle_start_pos_y, PADDLE_WIDTH, PADDLE_HEIGHT))

    x_vel, y_vel = game_state.ball_velocity
    x, y, w, h = game_state.ball
    ball_rect = Rect(x, y, w, h)
    ball = Ball(ball_rect, x_vel, y_vel)

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
            elif event.type == pygame.KEYUP:
                player_paddle.moving = ""

            if (left_score > MAX_SCORE - 1 or right_score > MAX_SCORE - 1) and event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_message.collidepoint(mouse[0],mouse[1]):
                    current_game_state.again[current_game_state.player_id] ^= True
        
        def draw_centered_message(rect:Rect,font:Font,message:str,antialias:bool,center:tuple[float, float]) -> Rect:
            """
            Author:              James Chen
            Purpose:             Draw a centered message on the screen using the provided rectangle, font, message, antialiasing, and center coordinates.
            Pre:                 Assumes a valid Rect, Font, and center tuple are provided.
            Post:                Renders the message on the screen at the specified center coordinates and returns the updated rectangle.   
            """
            text_surface = font.render(message,antialias,Color.WHITE.value, (0,0,0))
            text_rect = text_surface.get_rect()
            text_rect.center = center
            rect = screen.blit(text_surface,text_rect)
            return rect

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
        if left_score >= MAX_SCORE or right_score >= MAX_SCORE :
            win_text = "Player 1 Wins! " if left_score > MAX_SCORE - 1 else "Player 2 Wins! "
            draw_centered_message(win_message, win_font,win_text, False, ((screen_width/2), screen_height/2))

            if current_game_state.again[current_game_state.player_id] == 0:
                play_again_message = draw_centered_message(play_again_message,win_font,"Play Again",True,((screen_width/2), screen_height/2+90))
            else:
                play_again_message = draw_centered_message(play_again_message,win_font,"Cancel Rematch",True,((screen_width/2), screen_height/2+90))
        else:
            if current_game_state.start:
                # Only draw and update the ball when the game started
                ball.update_pos()
            else:
                # Wait for opponent when the game has not started and no one won
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
            
            rect(screen, Color.WHITE.value, ball)

        # Drawing the dotted line in the center
        if current_game_state.start:
            for i in center_line:
                rect(screen, Color.WHITE.value, i)
        
        # Drawing the player's new location
        for paddle in [player_paddle, opponent_paddle]:
            rect(screen, Color.WHITE.value, paddle)

        rect(screen, Color.WHITE.value, top_wall)
        rect(screen, Color.WHITE.value, bottom_wall)
        scoreRect = update_score(left_score, right_score, screen, Color.WHITE.value, score_font)
        display.update([top_wall, bottom_wall, ball, left_paddle, right_paddle, scoreRect, win_message])
        clock.tick(GAME_CLOCK_SPEED)
        
        # This number should be synchronized between you and your opponent.  If your number is larger
        # then you are ahead of them in time, if theirs is larger, they are ahead of you, and you need to
        # catch up (use their info)
        sync += 1

        #   Send latest information to server

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

        current_game_state.scores = (left_score, right_score)
        current_game_state.sync = sync

        serialized_game_state = dumps(current_game_state)
        client.sendall(serialized_game_state)

        #   Receive latest information from server

        received_data = client.recv(BUFFER_SIZE)
        received_game_state: GameState = loads(received_data)

        #   Update based on information from server
        current_game_state = received_game_state

        sync = current_game_state.sync
        left_score, right_score = current_game_state.scores

        # Update Ball
        x_vel, y_vel = current_game_state.ball_velocity
        x, y, w, h = current_game_state.ball
        ball.override_pos(Rect(x, y, w, h), x_vel, y_vel)

        # Update Paddles
        if current_game_state.player_id == 0:
            # If I am the left player
            if current_game_state.paddle_rect[0] is not None:
                # Update my paddle
                x, y, w, h = current_game_state.paddle_rect[0]
                player_paddle.update(Rect(x, y, w, h))
            if current_game_state.paddle_rect[1] is not None:
                # Update opponent paddle
                x, y, w, h = current_game_state.paddle_rect[1]
                opponent_paddle.update(Rect(x, y, w, h))
        else:
            # If I am the right player
            if current_game_state.paddle_rect[0] is not None:
                # Update opponent paddle
                x, y, w, h = current_game_state.paddle_rect[0]
                opponent_paddle.update(Rect(x, y, w, h))
            if current_game_state.paddle_rect[1] is not None:
                # Update my paddle
                x, y, w, h = current_game_state.paddle_rect[1]
                player_paddle.update(Rect(x, y, w, h))


def join_server(ip: str, port: str, app: Tk,username:str,password:str, confirm_password:str = None) -> None:
    """
    Author:              James Chen, Kyle Lastimosa
    Purpose:             Join the Pong game server with the provided IP, port, username, and password.
    Pre:                 Assumes Tkinter app window is provided, and valid username and password credentials.
    Post:                Connects to the server, sends authentication details, receives game state, and starts the game.
    """
    player_credentials = {
        "username": username,
        "password": password
    }

    # Check if player is trying to register
    if confirm_password is not None:
        player_credentials["confirm_password"] = confirm_password

    context = ssl.create_default_context()

    # Options to allow self-signed certificates
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    context.load_verify_locations(cafile="./rootCA.pem")

    with context.wrap_socket(socket(AF_INET, SOCK_STREAM)) as ssock:
        ssock.connect((ip, int(port)))

        ssock.sendall(dumps(player_credentials))
        auth_response = ssock.recv(BUFFER_SIZE)

        if auth_response == b"Authentication failed":
            messagebox.showerror("Authentication Failed", (
                "Incorrect username or password. Please try again.\n\n"
                "If you are trying to sign up, make sure to have the same password and confirm password. "
                "Also, click the register button to complete the registration."
            ))
        else:
            received_data = ssock.recv(BUFFER_SIZE)
            initial_received_game_state: GameState = loads(received_data)
            initial_received_game_state.player_name = username

            # Close this window and start the game with the info passed to you from the server
            app.withdraw()
            play_game(ssock, initial_received_game_state)
            app.quit()

# This displays the opening screen, you don't need to edit this (but may if you like)
def start_screen() -> None:
    """
    Author:       Kyle Lastimosa
    Purpose:      Display the opening screen for the Pong game.
    Pre:          None
    Post:         Initializes Tkinter app window with server information input fields.   
    """ 
    app = Tk()
    app.title("Server Info")

    image = PhotoImage(file="./assets/images/logo.png")

    title_label = Label(image=image)
    title_label.grid(column=0, row=0, columnspan=10)

    # Ip
    ip_label = Label(text="Server IP:")
    ip_label.grid(column=0, row=1, sticky="W", padx=8)
    ip_entry = Entry(app)
    ip_entry.grid(column=1, row=1)
    ip_entry.insert(END, DEFAULT_SOCKET_IP)

    # Port
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
    password_entry = Entry(app,show="*")
    password_entry.grid(column=1, row=4)
    password_entry.insert(END, "")

    # Confirm Password
    confirm_password_label = Label(text="Confirm Password:")
    confirm_password_label.grid(column=4, row=1, sticky="W", padx=8)
    confirm_password_entry = Entry(app,show="*")
    confirm_password_entry.grid(column=5, row=1)
    confirm_password_entry.insert(END, "")

    join_button = Button(text="Join", command=lambda: join_server(ip_entry.get(), port_entry.get(), app,username_entry.get(),password_entry.get()))
    join_button.grid(column=1, row=6, columnspan=1)

    register_button = Button(text="Register & Join", command=lambda: join_server(ip_entry.get(), port_entry.get(), app,username_entry.get(),password_entry.get(),confirm_password_entry.get()))
    register_button.grid(column=4, row=2, columnspan=3)

    app.mainloop()

def main() -> None:
    """
    Author:       Kyle Lastimosa
    Purpose:      Initiate the Pong game.
    Pre:          None
    Post:         Calls the start_screen function to display the opening screen.  
    """
    start_screen()

if __name__ == "__main__":
    main()