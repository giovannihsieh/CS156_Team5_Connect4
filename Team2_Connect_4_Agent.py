#! /usr/bin/Team5_Connect_4_Agent.py
# python connect_4_main.pyc Team2 Team5
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
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = BOT_PIECE

    # Prioritize a winning move
    if window.count(piece) == 4:
        score += 100
    # Make connecting 3 second priority
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    # Make connecting 2 third priority
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    # Prioritize blocking an opponent's winning move (but not over bot winning)
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    """ REASONING: give a score of the whole board based on evaluate_window.
    center column is favored, looks at horizontal/vertical/diagonal possibilities
    called at leaf nodes of minimax algorithm to estimate board values
    Giovanni Hsieh: 100% implemented to work with 2d list implementation of board"""
    score = 0
    ROW_COUNT = len(board)
    COLUMN_COUNT = len(board[0])
    WINDOW_LENGTH = 4

    # Score center column
    center_col = COLUMN_COUNT // 2
    center_array = [board[r][center_col] for r in range(ROW_COUNT)]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score horizontal positions
    for r in range(ROW_COUNT):
        row_array = [board[r][c] for c in range(COLUMN_COUNT)]
        for c in range(COLUMN_COUNT - WINDOW_LENGTH + 1):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score vertical positions
    for c in range(COLUMN_COUNT):
        col_array = [board[r][c] for r in range(ROW_COUNT)]
        for r in range(ROW_COUNT - WINDOW_LENGTH + 1):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score positive diagonals (bottom-left to top-right)
    for r in range(ROW_COUNT - WINDOW_LENGTH + 1):
        for c in range(COLUMN_COUNT - WINDOW_LENGTH + 1):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Score negative diagonals (top-left to bottom-right)
    for r in range(WINDOW_LENGTH - 1, ROW_COUNT):
        for c in range(COLUMN_COUNT - WINDOW_LENGTH + 1):
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


def minimax(board, depth, alpha, beta, maximizingPlayer, start_time, time_limit):
    """ SEARCH: Minimax search algorithm with alpha beta pruning for playing connect 4
    Giovanni Hsieh: 100% edited open source code to work"""
    if time.time() - start_time > time_limit:
        raise TimeoutError()

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
        score = -float('inf')
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = copy_board(board)
            drop_piece(b_copy, row, col, BOT_PIECE)
            _, new_score = minimax(b_copy, depth - 1, alpha, beta, False, start_time, time_limit)
            if new_score > score:
                score = new_score
                best_col = col
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return best_col, score
    else:
        score = float('inf')
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = copy_board(board)
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            _, new_score = minimax(b_copy, depth - 1, alpha, beta, True, start_time, time_limit)
            if new_score < score:
                score = new_score
                best_col = col
            beta = min(beta, score)
            if alpha >= beta:
                break
        return best_col, score

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

   time_limit = 15  # seconds; leave buffer for return
   start_time = time.time()  # Start the timer
   best_col = random.choice(get_valid_locations(board))  # fallback
   depth = 1
   best_score = -float('inf')

   print(f"[DEBUG] Starting iterative deepening for player '{BOT_PIECE}'")

   while True:
       current_time = time.time()
       if current_time - start_time > time_limit:
           print(f"[DEBUG] Time limit reached. Ending search at depth {depth - 1}")
           break

       try:
           col, score = minimax(board, depth, -float('inf'), float('inf'), True, start_time, time_limit)
           if col is not None:
               best_col = col
               print(f"[DEBUG] Depth {depth}: Best column so far is {col + 1} (score = {score})")

               # If a winning move is found, pick it immediately
               if score == 9999999:
                   print(f"[DEBUG] Found a guaranteed win at column {col + 1} (depth {depth})")
                   best_col = col
                   break

               # Stop if we detect that this depth leads to a guaranteed loss
               if score == -9999999:
                   print(
                       f"[DEBUG] Depth {depth}: All paths lead to guaranteed loss. Using previous best column {best_col + 1}.")
                   break

               if score > best_score:
                   best_score = score
                   best_col = col
                   print(f"[DEBUG] Updated best column to {col + 1} (score = {score})")

       except TimeoutError:
           print(f"[DEBUG] TimeoutError caught at depth {depth}")
           break

       depth += 1

   end_time = time.time()  # End the timer
   elapsed_time = end_time - start_time  # Calculate the time taken

   print(f"[DEBUG] Final move selected: column {best_col + 1}")
   print(f"[DEBUG] Time taken to make the move: {elapsed_time:.4f} seconds")

   return best_col + 1  # convert to 1-based indexing


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
