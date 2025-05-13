#! /usr/bin/Team3_Connect_4_Agent.py
# python connect_4_main.pyc Team1 Team5
# IMPORTS
import random
import copy

# DEFINITIONS
# board = [[' ' for _ in range(cols)] for _ in range(rows)]

#Constants
EMPTY = ' '
PLAYER_PIECE = 'O'  # opponent
BOT_PIECE = 'X'     # your symbol
WINDOW_LENGTH = 4
TEAM_NAME = "Team3"

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
    return [col for col in range(len(board[0])) if board[0][col] == EMPTY]

def is_valid_location(board, col):
    return board[0][col] == EMPTY

def get_next_open_row(board, col):
    for r in reversed(range(len(board))):
        if board[r][col] == EMPTY:
            return r

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def copy_board(board):
    return copy.deepcopy(board)

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == BOT_PIECE else BOT_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
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
    row_count = len(board)
    col_count = len(board[0])

    for r in range(row_count):
        for c in range(col_count - 3):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    for c in range(col_count):
        for r in range(row_count - 3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    for r in range(row_count - 3):
        for c in range(col_count - 3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    for r in range(3, row_count):
        for c in range(col_count - 3):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

    return False


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, BOT_PIECE) or len(get_valid_locations(board)) == 0


def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
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
   """ Decide your move, i.e., which column to drop a disk. """

   global BOT_PIECE, PLAYER_PIECE
   BOT_PIECE = my_game_symbol
   PLAYER_PIECE = 'O' if my_game_symbol == 'X' else 'X'

   col, _ = minimax(copy_board(board), 4, -float('inf'), float('inf'), True)
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
   print("Team3_Connect_4_Agent.py  is intended to be imported and not executed.")
else:
   print("Team3_Connect_4_Agent.py  has been imported.")
