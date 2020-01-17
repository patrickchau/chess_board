from stockfish import Stockfish
import sys
import random
import re
import string

sf = Stockfish('/Users/Patrick Chau/Desktop/chess/stockfish-10-win/stockfish-10-win/stockfish_x86-64-modern.exe') # pull the engine from compiled file
# chess engine used

class piece:
    m_type = 0
    m_position = 0
    m_color = 0

class board:
    board = []
    def make_move():
        return 0
    def undo_move():
        return 0
    def restart():
        return 0

def endgame():
    print("End")  

skill = 5                   # skill level of engine
num_moves = 0               # number of moves made
restart = False             # remake board
in_game = False             # currently in game
level_set = False           # skill level set flag
side_set = False            # side chosen flag
cur_turn = 0                # turn indicator, 0 = player, 1 = computer
rule = "[a-g][1-9][a-g][1-9]" # regex rule for moves
move_history = []           # move_history list

# first prompt user for level
while not level_set:
    skill = input('What skill level? (integers between 1 and 21 inclusive): ')
    if skill.isdigit() and int(skill) > 0 and int(skill) < 22:
        sf.set_skill_level(skill)
        level_set = True
    else:
        print("Invalid input" + "\n")
    
# ask user which side to play on
while not side_set:
    side = input('Which side? (type in white, black or random): ')
    if side == 'white' or side == 'black' or side == 'random':
        if side == 'black':
            # if black, computer goes first
            cur_turn = 1
        elif side == 'white':
            # if white, player goes first
            cur_turn = 0
        else: 
            if random.random() > 0.5:
                cur_turn = 1
            else:
                cur_turn = 0
        side_set = True
    else:
        print("Invalid input" + "\n")

print('Game is now starting.')
in_game = True

# start game
while in_game:
    # check if currently in checkmate (to end game)
    if len(move_history) > 0:
        print(move_history)
    mate = 0
    if mate:
        in_game = false
        endgame()
        break
    turn = "your" if cur_turn == 0 else "the computer's"
    print("It is now " + turn + " turn." + "\n")
    if turn == "your":
        move_done = 0
        while not move_done:
            move = input('Enter your move: ' + '\n')
            # first check if valid move format (letter + number + letter + number)
            valid = re.search(rule, move)
            if valid and sf.is_move_correct(move):
                # valid move syntax and able to be made
                move_history.append(move)
                sf.set_position(move_history)
                print("You entered the move: " + move + '\n')
                move_done = 1
            else:
                print("Invalid move, please enter a different move." + '\n')
        cur_turn = 1
    else: # computer's turn
        com_move = sf.get_best_move()
        print("The computer moves: " + com_move + '\n')
        move_history.append(com_move)
        sf.set_position(move_history)
        cur_turn = 0
    num_moves = num_moves + 1




  
    

