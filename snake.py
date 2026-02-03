#snake game
import curses
from curses.textpad import Textbox, rectangle
from curses import wrapper
import time
import random
from itertools import product
from collections import deque

def function_get_key(stdscr,letter):
    while True:
        key = stdscr.getkey()
        if key == letter:
            break

def color_game_coordinate(screen, lines, cols):
    screen.addstr(lines, cols*2, "██")  

def food_game_coordinate(screen,lines,cols):
     screen.addstr(lines,cols*2,"🍎")

def draw_grid_frame(lines, cols,stdscr):
        
        max_num = max(lines, cols)
        num_width = len(str(max_num))  # largura dos números
        
        # Posições do frame
        grid_top    = num_width      # após números horizontais
        grid_left   = num_width      # após números verticais
        
        # Linha horizontal (topo)
        stdscr.hline(grid_top, grid_left, curses.ACS_HLINE, cols)
        
        
        # Linhas verticais (laterais)
        stdscr.vline(grid_top, grid_left, curses.ACS_VLINE, lines)
        
        stdscr.addch(grid_top, grid_left, curses.ACS_ULCORNER)
        
        stdscr.refresh()

def make_help_grid(help_grid_size, stdscr):
        help_grid_size = (min(help_grid_size[0], curses.LINES), 
                        min(help_grid_size[1], curses.COLS))
        
        lines, cols = help_grid_size
        draw_grid_frame(lines,cols,stdscr)
        
        # Vertical numbers
        for i in range(lines):
            stdscr.addstr(i, 0, f"{i+1}")
        
        # Horizontal numbers 
        for i in range(cols):
            num_str = str(i+1)           
            for digit_idx, digit in enumerate(num_str):
                row = digit_idx    
                col = i               
                stdscr.addstr(row, col, digit)
        
        stdscr.refresh()

def food_coordinate_generator(all_coordinates, snake_coordinates):
     positions_without_snake = list(set(all_coordinates)- set(snake_coordinates))
     food_pos=random.choice(positions_without_snake)
     return food_pos[0], food_pos[1]

def color_snake(screen,snake_coordinates):
     for coordinates in snake_coordinates:
        color_game_coordinate(screen,coordinates[0],coordinates[1])

def move_snake(snake_coordinates,lines,cols):  
            snake_coordinates.append((lines,cols))
            snake_coordinates.popleft()

def draw_fruit_and_grow_snake(i,game_window,food_pos_lines,food_position_cols,all_coordinates,snake_coordinates,last_coordinate_snake):
            if i>0:
                food_game_coordinate(game_window,food_pos_lines,food_position_cols)
                if (food_pos_lines, food_position_cols) in snake_coordinates:
                    food_pos_lines, food_position_cols = food_coordinate_generator(all_coordinates, snake_coordinates)
                    snake_coordinates.appendleft(last_coordinate_snake)
            return food_pos_lines, food_position_cols

def check_collision(lines, cols, screen_size, snake_coordinates, i):
            # Out of bounds
            if (cols < 0 or cols > screen_size - 1 or 
                lines < 0 or lines > screen_size - 1):
                return True
            
            # Hit self (skip head at i=0)
            if i > 0 and (lines, cols) in snake_coordinates:
                return True
            
            return False

def main(stdscr):
    curses.init_pair(1,curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2,curses.COLOR_GREEN, curses.COLOR_GREEN)
    GREEN_ON_BLACK= curses.color_pair(1)

    stdscr.addstr(1,2, "Willkommen!")

    rectangle(stdscr, 2, 1, 7, 71)
    stdscr.addstr(3,3,f"Snake Game 🍎", GREEN_ON_BLACK)
    stdscr.addstr(4,3,f"Developed by André Godinho gmail: am.godinho.2003@gmail.com")
    stdscr.addstr(5,3,f"Terminal window has dimensions:{curses.LINES, curses.COLS}")
    stdscr.addstr(6,3,f"Game needs terminal wide enough")

    stdscr.addstr(9,3,f"To start the game press character {"s"}")


    function_get_key(stdscr, "s")
    stdscr.clear()
    stdscr.refresh()

    # Start the game

    game_running = True
    i, j = 0, 0
    c_left,c_right,c_up,c_down = 0,0,0,0
    dlines, dcols = 0,0

    help_grid_size = (100,300)
    make_help_grid(help_grid_size,stdscr)

    stdscr.addstr(5,7, "Below, input screen_size:")
    stdscr.addstr(7,7, "screen_size should be between 8 and 30 ")
    stdscr.addstr(9,7, "After input type ENTER")
    input_win = curses.newwin(1, 3, 6, 7)   
    stdscr.refresh()

    box = Textbox(input_win)
    box.edit()                                  
    input_text = box.gather().strip()

    input_win.clear()
    stdscr.clear()
    stdscr.refresh()

    try:
        screen_size = int(input_text)          # Convert FIRST
        if not (8 <= screen_size <= 30):      # ← Fixed: NOT here
            stdscr.addstr(5, 7, "screen_size out of range (10-50)")
            stdscr.addstr(6, 7, "type q to quit")
            stdscr.refresh()
            function_get_key(stdscr, "q")
            return
    except ValueError:
        stdscr.addstr(5, 7, "invalid input, should be integer")
        stdscr.addstr(6, 7, "type q to quit")
        stdscr.refresh()
        function_get_key(stdscr, "q")
        return

    cols = int(screen_size/2)
    lines = int(screen_size/2)
    stdscr.clear()
    make_help_grid(help_grid_size, stdscr)
    
    # WINDOWS SECTION
    game_window = curses.newwin(screen_size ,screen_size*2 +1 ,6 ,7) # +1 can be explained, i couldn´t write in the last corner
    stats_window = curses.newwin(50,curses.COLS - screen_size*2 - 10,5, 7 + screen_size*2 + 4)
    rectangle(stdscr, 5, 6, 6 + screen_size, 8 + screen_size*2)  # draw border on stdscr
    stdscr.refresh()

    #possible_positions
    #in terms of rows let´s say that 
    row_pos = list(range(screen_size))
    col_pos = list(range(screen_size))
    all_coordinates = list(product(row_pos,col_pos))

    snake_coordinates= deque()
    snake_coordinates.append((lines,cols))

    game_window.keypad(True)   
    game_window.nodelay(True)
    curses.curs_set(0)

    # initial food coordinates
    food_pos_lines, food_position_cols = food_coordinate_generator(all_coordinates, snake_coordinates)

    # initial sleeptime

    sleep_time= 0.2
    time_played = 0
    last_step = 0 

    while game_running:
        try:
            key = game_window.getkey()
            i += 1
        except:
            key = None
            if i!= 0 : j+=1

        if key == "KEY_LEFT":
            dcols, dlines = -1, 0
            c_left += 1       # Use += not = (from prior)

        elif key == "KEY_RIGHT":
            dcols, dlines = 1, 0
            c_right += 1

        elif key == "KEY_UP":
            dcols, dlines = 0, -1
            c_up += 1

        elif key == "KEY_DOWN":
            dcols, dlines = 0, 1
            c_down += 1

        elif key == "q":
            break

        # update coordinates based on key selected
        cols += dcols
        lines += dlines

        if i == 0:
            instruction_win = curses.newwin(10, 30, screen_size + 8, 7)
            instruction_win.addstr(0, 0, "CONTROLS:")
            instruction_win.addstr(1, 0, "Arrow keys \u2191\u2193\u2190\u2192")
            instruction_win.addstr(2, 0, "q = Quit game")
            instruction_win.refresh()
        
        if check_collision(lines, cols, screen_size, snake_coordinates, i):
            break  
        
        game_window.clear()
        stats_window.clear()
        last_coordinate_snake = snake_coordinates[-1]
        move_snake(snake_coordinates,lines,cols)

        food_pos_lines, food_position_cols = draw_fruit_and_grow_snake(i,
                                                                       game_window,
                                                                       food_pos_lines,food_position_cols,
                                                                       all_coordinates,snake_coordinates,
                                                                       last_coordinate_snake)

        stats_window.addstr(1, 0, f"Num. non key cycle {j}")
        stats_window.addstr(2, 0, f"Num. key cycles {i}")
        stats_window.addstr(3, 0, f"Total Num. Cycles {i+j}")
        stats_window.addstr(4, 0,f"Coordinates of the head of the snake {lines,cols}")
        stats_window.addstr(6, 0,f"Snake coordinates {snake_coordinates}")

        stdscr.refresh()
        color_snake(game_window,snake_coordinates)
        game_window.refresh()
        stats_window.refresh()

        # increase game speed each time snake increases 10 times
        current_step = len(snake_coordinates) // 10
        if current_step > last_step and len(snake_coordinates) % 10 == 0:
            sleep_time -= 0.01
            last_step = current_step
        
        time_played += sleep_time
        time.sleep(sleep_time)
    
    game_window.clear()
    game_window.refresh()
    stdscr.clear()
    make_help_grid(help_grid_size,stdscr)

    if len(snake_coordinates) > screen_size*3:
        stdscr.addstr(5,7,"GREAT JOB BUT GAME OVER", curses.A_BOLD)
    else: 
        stdscr.addstr(5,7,"GAME OVER", curses.A_BOLD)
    
    stdscr.addstr(7,7,"Simple Stats")
    stdscr.addstr(9,7,f"Number of times ← typed: {c_left}")
    stdscr.addstr(10,7,f"Number of times → typed: {c_right}")
    stdscr.addstr(11,7,f"Number of times ↓ typed: {c_down}")
    stdscr.addstr(12,7,f"Number of times ↑ typed: {c_up}")
    stdscr.addstr(14,7,f"Time played: {round(time_played,3)} seconds")
    stdscr.addstr(15,7,f"Snake size: {len(snake_coordinates)}")
    stdscr.addstr(17,7,f"To quit type {"q"}",curses.A_BOLD)
    stdscr.refresh()
    function_get_key(stdscr,"q")    

wrapper(main)