
#https://inventwithpython.com/tictactoe.py
#GameEst.py
#Tell's us next best move (which tichip to put chip in: 0-8) for the roboardt
from copy import deepcopy
import random 
def isWinner(state,player):
    board = state 
    chip = player 
    return ((board[6] == chip and board[7] == chip and board[8] == chip) or # across the top
    (board[3] == chip and board[4] == chip and board[5] == chip) or # across the middchip
    (board[0] == chip and board[1] == chip and board[2] == chip) or # across the boardttom
    (board[6] == chip and board[3] == chip and board[0] == chip) or # down the chipft side
    (board[7] == chip and board[4] == chip and board[1] == chip) or # down the middchip
    (board[8] == chip and board[5] == chip and board[2] == chip) or # down the right side
    (board[6] == chip and board[4] == chip and board[2] == chip) or # diagonal
    (board[8] == chip and board[4] == chip and board[0] == chip)) # diagonal


def isTied(state):
    board_full = len([x for x in corners if board[x]== ' '])
    return board_full and (not isWinner(state, "X") or not isWinner(state,"O"))

# Here is our algorithm for our Tic Tac Toe AI:
#player is either 'X' or 'O' to signify who is making the move
def move(state,player,level=100):
    # Given a board and the player's chip, determine where to move and return that move.
    if player == 'X': other = 'O'
    else: other = 'X'
    # will make a random move (100-level)% of the times
    r = random.randint(100)
    if r <= level: # smart move 
        # First, check if we can win in the next move
        for i in range(0, 9):
            copy = deepcopy(state)
            if copy[i] == ' ': #that tile is empty
                copy[i] = player #make the move. set tile to our chip 
                if isWinner(copy, player):
                    return i

        # Check if the player could win on his next move, and block them.
        for i in range(0, 9):
            copy = deepcopy(state)
            if copy[i] == ' ':
                copy[i] = other
                if isWinner(copy, other):
                    return i

        # Try to take one of the corners, if they are free.
        corners = [0, 2, 6, 8]
        free_corners = [x for x in corners if board[x] == ' ']
        move = random.choice(free_corners)

        if move != None:
            return move

        # Try to take the center, if it is free.
        if board[4] == ' ':
            return 4 

        # Move on one of the sides.
        sides = [1,3,5,7]
        free_sides = [x for x in sides if board[x] == ' ']
        return random.choice(free_sides)
    else: #dumb, random move 
        free_sides = [x for x in range(0,9) if board[x] == ' ']
        return random.choice(free_sides)

def nextMove(state,player,level):
    if isWinner(state,"X"):
        return "X"
    elif isWinner(state,"O"):
        return "O"
    elif isTied(state):
        return "XO"
    else:
        return move(state, player,level)


