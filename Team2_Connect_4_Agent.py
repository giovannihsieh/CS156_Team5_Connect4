#! /usr/bin/Team5_Connect_4_Agent.py
# python connect_4_main.pyc Team3 Team5
# IMPORTS
import random
import copy
import time

# DEFINITIONS
# board = [[' ' for _ in range(cols)] for _ in range(rows)]

#Constants
EMPTY = ' '
PLAYER_PIECE = 'O'  # opponent
BOT_PIECE = 'X'     # your symbol
WINDOW_LENGTH = 4
TEAM_NAME = "Team2"

# HELPER FUNCTIONS
# Print the Board
def print_board(board):
    """ Prints the connect 4 game board."""
    for row in board:
        print('|' + '|'.join(row) + '|')
    print("-" * (len(board[0]) * 2 + 1))
    print(' ' + ' '.join(str(i+1) for i in range(len(board[0]))))
    return

def get_valid_locations(board):
    """ REPRESENTATION: Get all locations in the game board that are not empty (can be filled).
    Giovanni Hsieh: 100% implemented to work with 2d list implementation of board"""
    return [col for col in range(len(board[0])) if board[0][col] == EMPTY]

def is_valid_location(board, col):
    """Check if there is a valid location in a specific column.
    Giovanni Hsieh: 100% implemented to work with 2d list implementation of board"""
    return board[0][col] == EMPTY

def get_next_open_row(board, col):
    """REPRESENTATION: check which row the game piece will go to when placed in a column.
    Giovanni Hsieh: 100% implemented to work with 2d list implementation of board"""
    for r in reversed(range(len(board))):
        if board[r][col] == EMPTY:
            return r

def drop_piece(board, row, col, piece):
    """REPRESENTATION: drop a game piece into a row/column. used for minimax search algorithm
    Giovanni Hsieh: 100% implemented to work with 2d list implementation of board"""
    board[row][col] = piece

def copy_board(board):
    """REPRESENTATION: copy board state for modification during minimax algorithm
    Giovanni Hsieh: 100% implemented to be used in minimax function without modifying original board state"""
    return copy.deepcopy(board)

def order_valid_locations(valid_locations, col_count):
    """REPRESENTATION: sort moves by how close to center they are since center is usually the best move"""
    center = col_count // 2
    return sorted(valid_locations, key=lambda x: abs(center - x))

def evaluate_window(window, piece):
    """ REASONING: heuristic evaluation. gives a score to 4 windows for current player.
    Giovanni Hsieh: 100% implemented"""
    score = 0
    # Switch scoring based on turn
    opp_piece = PLAYER_PIECE \
    if piece == BOT_PIECE \
        else BOT_PIECE

    # Prioritise a winning move
    if window.count(piece) == 4:
        score += 1000
    # Make connecting 3 second priority
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 50
    # Make connecting 2 third priority
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 10

    # Prioritise blocking an opponent's winning move (but not over bot winning)
    if window.count(opp_piece) == 4:
        score -= 1000
    elif window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 80
    elif window.count(opp_piece) == 2 and window.count(EMPTY) == 2:
        score -= 5

    return score

def score_position(board, piece):
    """ REASONING: give a score of the whole board based on evaluate_window.
    center column is favored, looks at horizontal/vertical/diagonal possibilities
    called at leaf nodes of minimax algorithm to estimate board values
    Giovanni Hsieh: 100% implemented to work with 2d list implementation of board"""
    score = 0
    row_count = len(board)
    col_count = len(board[0])

    # Center column preference
    center_col = col_count // 2
    center_array = [board[r][center_col] for r in range(row_count)]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Horizontal score
    for r in range(row_count):
        row_array = board[r]
        for c in range(col_count - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Vertical score
    for c in range(col_count):
        col_array = [board[r][c] for r in range(row_count)]
        for r in range(row_count - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Positive diagonals
    for r in range(row_count - 3):
        for c in range(col_count - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Negative diagonals
    for r in range(3, row_count):
        for c in range(col_count - 3):
            window = [board[r - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def winning_move(board, piece):
    """REPRESENTATION: check if there is a winning state
    Giovanni Hsieh: 100% implemented to work with 2d list implementation of board"""
    row_count = len(board)
    col_count = len(board[0])

    # Check valid horizontal locations for win
    for r in range(row_count):
        for c in range(col_count - 3):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check valid vertical locations for win
    for c in range(col_count):
        for r in range(row_count - 3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check valid positive diagonal locations for win
    for r in range(row_count - 3):
        for c in range(col_count - 3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check valid negative diagonal locations for win
    for r in range(3, row_count):
        for c in range(col_count - 3):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

    return False


def is_terminal_node(board):
    """REPRESENTATION:  check if current state is win/draw/loss terminal state"""
    return winning_move(board, PLAYER_PIECE) or winning_move(board, BOT_PIECE) or len(get_valid_locations(board)) == 0


def minimax(board, depth, alpha, beta, maximizingPlayer):
    """ SEARCH: Minimax search algorithm with alpha beta pruning for playing connect 4
    Giovanni Hsieh: 100% edited open source code to work"""
    valid_locations = order_valid_locations(get_valid_locations(board), len(board[0]))
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, BOT_PIECE):
                return (None, 9999999)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -9999999)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, BOT_PIECE))

    if maximizingPlayer:
        value = -float('inf')
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = copy_board(board)
            drop_piece(b_copy, row, col, BOT_PIECE)
            _, new_score = minimax(b_copy, depth - 1, alpha, beta, False)
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value

    else:
        value = float('inf')
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = copy_board(board)
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            _, new_score = minimax(b_copy, depth - 1, alpha, beta, True)
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

# FUNCTIONS REQUIRED BY THE connect_4_main.py MODULE
def init_agent(player_symbol, board_num_rows, board_num_cols, board):
   """ Inits the agent. Should only need to be called once at the start of a game.
   NOTE NOTE NOTE: Do not expect the values you might save in variables to retain
   their values each time a function in this module is called. Therefore, you might
   want to save the variables to a file and re-read them when each function was called.
   This is not to say you should do that. Rather, just letting you know about the variables
   you might use in this module.
   NOTE NOTE NOTE NOTE: All functions called by connect_4_main.py  module will pass in all
   of the variables that you likely will need. So you can probably skip the 'NOTE NOTE NOTE'
   above. """
   num_rows = int(board_num_rows)
   num_cols = int(board_num_cols)
   game_board = board
   my_game_symbol = player_symbol
   return True

def what_is_your_move(board, game_rows, game_cols, my_game_symbol):
   """ Decide your move, i.e., which column to drop a disk.
   Giovanni Hsieh: 100% Implemented the agent to determine move based on minimax algorithm.
   : Implemented checking for winning or losing move before running minimax to save time
   """

   global BOT_PIECE, PLAYER_PIECE
   BOT_PIECE = my_game_symbol
   PLAYER_PIECE = 'O' if my_game_symbol == 'X' else 'X'

   valid_locations = get_valid_locations(board)

   # Check for winning move before running minimax to save time
   for col in valid_locations:
       row = get_next_open_row(board, col)
       temp_board = copy_board(board)
       drop_piece(temp_board, row, col, BOT_PIECE)
       if winning_move(temp_board, BOT_PIECE):
           return col + 1

   # Check for opponent's winning move to block before running minimax to save time
   for col in valid_locations:
       row = get_next_open_row(board, col)
       temp_board = copy_board(board)
       drop_piece(temp_board, row, col, PLAYER_PIECE)
       if winning_move(temp_board, PLAYER_PIECE):
           return col + 1

   # If neither above sections happen, run minimax algorithm
   col, _ = minimax(copy_board(board), 5, -float('inf'), float('inf'), True)
   return col + 1 if col is not None else random.randint(1, game_cols)

def connect_4_result(board, winner, looser):
    """The Connect 4 manager calls this function when the game is over.
    If there is a winner, the team name of the winner and looser are the
    values of the respective argument variables. If there is a draw/tie,
    the values of winner = looser = 'Draw'."""

    print(f">>> I am player {TEAM_NAME} <<<")

    if winner == "Draw":
        print(">>> The game resulted in a draw. <<<\n")
    else:
        print("The winner is " + winner)
        if winner == TEAM_NAME:
            print("YEAH!!  :-)")
        else:
            print("BOO HOO HOO  :~(")
        print("The looser is " + looser)
        print()

    # Uncomment to debug final state
    # print("Final board state:")
    # print_board(board)  # You can use the same print_board helper function

    return True

#####
# MAKE SURE MODULE IS IMPORTED
if __name__ == "__main__":
   print("Team2_Connect_4_Agent.py  is intended to be imported and not executed.")
else:
   print("Team2_Connect_4_Agent.py  has been imported.")
