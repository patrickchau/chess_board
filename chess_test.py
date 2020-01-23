from stockfish import Stockfish
import sys
import random
import re
import string
import os

# sf = Stockfish('/Users/Patrick Chau/Desktop/chess/stockfish-10-win/stockfish-10-win/stockfish_x86-64-modern.exe') # pull the engine from compiled file
# chess engine used

# class hierarchy: Game -> board -> pieces
# 
# TODO: add timer to game, data structure to represent pieces, command to undo moves

rule = "[a-h][1-9][a-h][1-9]" # regex rule for moves

# white will be lowercase, black will be uppercase
piece_dict = dict([
    (0, "P"),
    (1, "K"),
    (2, "Q"),
    (3, "L"),
    (4, "B"),
    (5, "R"),
    (-1, "empty")
])

side_dict = dict([
    (-1, "empty"),
    (0, "white"),
    (1, "black")
])

class Piece: # pieces
    def __init__(self, pos = -1, t = 0, col = -1):
        self.m_type = t
        self.m_position = pos
        self.m_color = col
    def updatePos(self, new_ind):
        self.m_position = new_ind
        return 1
    def get_pos(self, ):
        return self.m_position
    def get_type(self, ):
        return self.m_type



class Board: # data structure to contain Pieces & update positions
    # 8x8 board so 64 points
    """
          a b c d e f g h
          _ _ _ _ _ _ _ _
       1 |               |
       2 |               |
       3 |               |
       4 |               |
       5 |               |
       6 |               |
       7 |               |
       8 |_ _ _ _ _ _ _ _|
          so if we have a 64 slot 1-dimensional array, taking a1 as 1, h1 as 8, a2 as 9 and so on...
          math.floor($pos / 8) = row (number)
          $pos%8 = column (letter)
    """
    def __init__(self,):
        self.m_board = []
        self.initialize()

    def initialize(self,): #default board setup
        # each side starts with 16 pieces each
        # king starts on opposite color as itself (white king on e1, black king on e8)
        # [pawn pawn pawn pawn pawn pawn pawn pawn]
        # [rook knight bishop queen king bishop knight rook]
        # empty points will be denoted by '*'
        count = 1
        while count <= 64:
            add = None
            if count == 1 or count == 8 or count == 57 or count == 64: # rooks, 5
                if count == 1 or count == 8: # white
                    add = Piece(count, 5, 0) 
                else:                       # black
                    add = Piece(count, 5, 1)
            elif count == 2 or count == 7 or count == 58 or count == 63: # knights
                if count == 2 or count == 7: # white knights
                    add = Piece(count, 3, 0)
                else:                       # black knights
                    add = Piece(count, 3, 1)
            elif count == 3 or count == 6 or count == 59 or count == 62: # bishops
                if count == 3 or count == 6:
                    add = Piece(count, 4, 0)
                else:
                    add = Piece(count, 4, 1)
            elif count == 4 or count == 60: # queens
                if count == 4:
                    add = Piece(count, 2, 0)
                else:
                    add = Piece(count, 2, 1)
            elif count == 5 or count == 61: # kings
                if count == 5:
                    add = Piece(count, 1, 0)
                else:
                    add = Piece(count, 1, 1)
            elif (count >= 9 and count <= 16) or (count >= 49 and count <= 56) : # pawns
                if (count >= 9 and count <= 16):
                    add = Piece(count, 0, 0)
                else:
                    add = Piece(count, 0, 1)
            else: # empty
                add = Piece(count, -1, -1)
            self.m_board.append(add)
            count += 1
        return 1

    def print_board_state(self,):
        """
          a b c d e f g h
          _ _ _ _ _ _ _ _
       1 |               |
       2 |               |
       3 |               |
       4 |               |
       5 |               |
       6 |               |
       7 |               |
       8 |_ _ _ _ _ _ _ _|
          so if we have a 64 slot 1-dimensional array, taking a1 as 1, h1 as 8, a2 as 9 and so on...
          math.floor($pos / 8) = row (number)
          $pos%8 = column (letter)
    """
        print("     a b c d e f g h \n")
        print("     _ _ _ _ _ _ _ _ \n")
        # construct a string to represent pieces
        row = 0
        while row < 8:
            string = str(row+1) + "   |"
            col = 0
            while col <= 7:
                ind = (row) * 8 + col
                addition = " "
                p = self.m_board[ind].get_type()
                if p != -1: # implies a non-empty square
                    addition = piece_dict[p]
                string += addition + " "
                col += 1
            string += "| \n"
            row += 1
            print(string)
        print("     _ _ _ _ _ _ _ _ \n")

    def change_pos(self, s_ind, e_ind): # relies on the fact that the move has already been checked by stockfish to be valid
        # start_pos 
        placeholder = self.m_board[s_ind]
        self.m_board[s_ind] = Piece(s_ind, -1, -1)
        self.m_board[e_ind] = placeholder
        self.m_board[e_ind].updatePos(e_ind)
        return 1

    def undo_move(self):
        return 0

    def restart(self):
        return 0

    def get_position(self):
        return 1

class Game: # handles game logic + interacts with stockfish
    def __init__(self):
        abs_path = os.path.dirname(__file__)
        rel_path = 'stockfish-10-win/stockfish-10-win/stockfish_x86-64-modern.exe'
        self.sf = Stockfish(os.path.join(abs_path, rel_path)) #pull the engine from compiled file
        self.m_skill_level = 0
        self.m_cur_turn = 0                                   # 0 for player turn, 1 for computer turn
        self.m_in_game = False
        self.m_move_his = []
        self.num_moves = 0
        self.set_skill_level(request_skill_level())           # request a skill level for engine
        self.choose_side(request_side())                      # request a starting side
        self.m_board = Board()

    def set_skill_level(self, d_level):   # function to set a skill level
        self.sf.set_skill_level(d_level)
        self.m_skill_level = d_level

    def choose_side(self, d_side):        # function to set a starting side
        self.m_cur_turn = d_side

    def check_for_mate(self, val):        # function periodically checks if there is a checkmate and ends game if true
        return 1

    def updateBoard(self, move): 
        # first two characters of move are start, last two are end
        start_pos = move[:2]
        ind_pos_s = (ord(start_pos[0]) - 97) + ((int(start_pos[1])-1) * 8)
        end_pos = move[2:4]
        ind_pos_e = (ord(end_pos[0]) - 97) + ((int(end_pos[1])-1) * 8)
        self.m_board.change_pos(ind_pos_s, ind_pos_e)
        self.m_board.print_board_state()
        return 1

    def endGame(self, ):                  
        return 1
    
    def run(self,):
        print('Game is now starting.')
        in_game = True
        # start game
        while in_game:
            # check if currently in checkmate (to end game)
            #if len(self.m_move_his) > 0:
            #    print(self.m_move_his)
            move = None
            turn = "your" if self.m_cur_turn == 0 else "the computer's"
            print("It is now " + turn + " turn." + "\n")
            if self.m_cur_turn == 0:
                move_done = 0
                while not move_done:
                    move = input('Enter your move: ' + '\n').strip()
                    # first check if valid move format (letter + number + letter + number)
                    valid = re.search(rule, move)
                    if valid and self.sf.is_move_correct(move):
                        # valid move syntax and able to be made
                        self.m_move_his.append(move)
                        self.sf.set_position(self.m_move_his)
                        print("You entered the move: " + move + '\n')
                        move_done = 1
                    else:
                        print("Invalid move, please enter a different move." + '\n')
                self.m_cur_turn = 1
            else: # computer's turn
                move = self.sf.get_best_move()
                print("The computer moves: " + move + '\n')
                self.m_move_his.append(move)
                self.sf.set_position(self.m_move_his)
                self.m_cur_turn = 0
            self.num_moves = self.num_moves + 1
            self.updateBoard(move)


def request_skill_level(): # prompts user for inputting a skill level for engine
    level_set = False
    count = 0
    while not level_set and count < 5:
        count = count + 1
        skill = input('What skill level? (integers between 1 and 21 inclusive): ')
        if skill.isdigit() and int(skill) > 0 and int(skill) < 22:
            level_set = True
        elif count == 5:
            print("Learn to read. Setting to default of 5.")
            skill = 5
        else:
            print("Invalid input" + "\n")
    return skill

def request_side(): # prompts user for choosing a starting side
    side_set = False
    side = "white"
    count = 0
    c_side = 0
    while not side_set and count < 5:
        count = count + 1
        side = input('Which side? (type in white, black or random): ')
        if side == 'white' or side == 'black' or side == 'random':
            if side == 'black':
                # if black, computer goes first
                c_side = 1
            elif side == 'white':
                # if white, player goes first
                c_side = 0
            else: 
                if (random.randint(0, 999)/100) > 5:
                    c_side = 1
                else:
                    c_side = 0
            side_set = True
        elif count == 5:
            print("Setting to default side of white.")
            c_side = 0
            side_set = True
        else:
            print("Invalid input" + "\n")
    return c_side



def runGame():
    # first instantiate chess board object
    game = Game()
    game.run()

if __name__ == '__main__':
    runGame()




  
    

