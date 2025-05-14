# ! /usr/bin/Team3_Connect_4_Agent.py
# python connect_4_main.pyc Team2 Team5

import random
import math
import copy
import hashlib
import time

# -------------------
# TRANSPOSITION TABLE
# -------------------

class TranspositionTable:
    def __init__(self):
        self.table = {}

    def _hash_board(self, board, my_symbol, opponent_symbol):
        board_string = ''.join(''.join(row) for row in board)
        return hashlib.md5((board_string + my_symbol + opponent_symbol).encode()).hexdigest()

    def get(self, board, my_symbol, opponent_symbol):
        key = self._hash_board(board, my_symbol, opponent_symbol)
        return self.table.get(key)

    def put(self, board, my_symbol, opponent_symbol, value):
        key = self._hash_board(board, my_symbol, opponent_symbol)
        self.table[key] = value

transposition_table = TranspositionTable()

# -------------------
# HELPER FUNCTIONS
# -------------------

def print_board(board):
    for row in board:
        print('|' + '|'.join(row) + '|')
    print("-" * (len(board[0]) * 2 + 1))
    print(' ' + ' '.join(str(i + 1) for i in range(len(board[0]))))

def get_valid_moves(board):
    return [c for c in range(len(board[0])) if board[0][c] == ' ']

def make_move(board, col, symbol):
    new_board = copy.deepcopy(board)
    for row in reversed(range(len(new_board))):
        if new_board[row][col] == ' ':
            new_board[row][col] = symbol
            return new_board
    return None

def check_winner(board, symbol):
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols - 3):
            if all(board[r][c + i] == symbol for i in range(4)):
                return True
    for r in range(rows - 3):
        for c in range(cols):
            if all(board[r + i][c] == symbol for i in range(4)):
                return True
    for r in range(3, rows):
        for c in range(cols - 3):
            if all(board[r - i][c + i] == symbol for i in range(4)):
                return True
    for r in range(rows - 3):
        for c in range(cols - 3):
            if all(board[r + i][c + i] == symbol for i in range(4)):
                return True
    return False

def is_full(board):
    return all(cell != ' ' for row in board for cell in row)


def evaluate_board(board, my_symbol, opponent_symbol):
    """Evaluate the board and return a score."""
    score = 0

    # Check for winning moves
    if check_winner(board, my_symbol):
        return 100000  # Win score for the agent
    elif check_winner(board, opponent_symbol):
        return -100000  # Loss score for the agent

    # Positional scoring: Center columns are more valuable
    for r in range(len(board)):
        for c in range(len(board[0])):
            if board[r][c] == my_symbol:
                score += 2  # Add value for own pieces
                score += (len(board[0]) // 2 - abs(c - len(board[0]) // 2)) * 2  # Center is better
            elif board[r][c] == opponent_symbol:
                score -= 2  # Subtract value for opponent's pieces
                score -= (len(board[0]) // 2 - abs(c - len(board[0]) // 2)) * 2  # Center is worse

    # Evaluate the number of 2-in-a-row and 3-in-a-row for both the agent and the opponent
    for r in range(len(board)):
        for c in range(len(board[0]) - 3):
            window = [board[r][c + i] for i in range(4)]
            score += evaluate_window(window, my_symbol, opponent_symbol)

    for r in range(len(board) - 3):
        for c in range(len(board[0])):
            window = [board[r + i][c] for i in range(4)]
            score += evaluate_window(window, my_symbol, opponent_symbol)

    for r in range(len(board) - 3):
        for c in range(len(board[0]) - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, my_symbol, opponent_symbol)

    for r in range(3, len(board)):
        for c in range(len(board[0]) - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += evaluate_window(window, my_symbol, opponent_symbol)

    return score


def evaluate_window(window, my_symbol, opponent_symbol):
    """Evaluates a 4-cell window and returns a score based on the contents."""
    score = 0
    my_count = window.count(my_symbol)
    opponent_count = window.count(opponent_symbol)

    if my_count == 4:
        score += 100  # Winning line
    elif my_count == 3 and window.count(' ') == 1:
        score += 10  # Potential to make a 4-in-a-row
    elif my_count == 2 and window.count(' ') == 2:
        score += 5  # Potential for future moves

    if opponent_count == 3 and window.count(' ') == 1:
        score -= 10  # Block opponent from winning
    elif opponent_count == 2 and window.count(' ') == 2:
        score -= 5  # Prevent opponent from setting up a winning move

    return score

def negamax(board, depth, alpha, beta, maximizing, my_symbol, opponent_symbol):
    cached = transposition_table.get(board, my_symbol, opponent_symbol)
    if cached is not None:
        return cached, None

    valid_moves = get_valid_moves(board)
    is_terminal = check_winner(board, my_symbol) or check_winner(board, opponent_symbol) or len(valid_moves) == 0

    if depth == 0 or is_terminal:
        score = evaluate_board(board, my_symbol, opponent_symbol)
        transposition_table.put(board, my_symbol, opponent_symbol, score)
        return score, None

    best_score = -math.inf
    best_move = random.choice(valid_moves)

    for col in valid_moves:
        new_board = make_move(board, col, my_symbol if maximizing else opponent_symbol)
        score, _ = negamax(new_board, depth - 1, -beta, -alpha, not maximizing, my_symbol, opponent_symbol)
        score = -score

        if score > best_score:
            best_score = score
            best_move = col
        alpha = max(alpha, score)
        if alpha >= beta:
            break

    transposition_table.put(board, my_symbol, opponent_symbol, best_score)
    return best_score, best_move

# -------------------
# AGENT ENTRY POINTS
# -------------------

def init_agent(player_symbol, board_num_rows, board_num_cols, board):
    return True

def what_is_your_move(board, game_rows, game_cols, my_game_symbol):
    opponent_symbol = 'O' if my_game_symbol == 'X' else 'X'
    start_time = time.time()
    time_limit = 10.0  # seconds
    best_move = random.choice(get_valid_moves(board))
    depth = 1
    while True:
        try:
            transposition_table.table.clear()
            score, move = negamax(board, depth, alpha=-math.inf, beta=math.inf,
                                   maximizing=True, my_symbol=my_game_symbol, opponent_symbol=opponent_symbol)
            if move is not None:
                best_move = move
            if time.time() - start_time > time_limit:
                break
            depth += 1
        except Exception as e:
            break

    return best_move + 1

def connect_4_result(board, winner, looser):
    print(">>> I am player TEAM3 <<<")
    if winner == "Draw":
        print(">>> The game resulted in a draw. <<<\n")
    else:
        print("The winner is " + winner)
        if winner == "Team3":
            print("YEAH!!  :-)")
        else:
            print("BOO HOO HOO  :~(")
        print("The looser is " + looser)
    return True

# -------------------
# DO NOT RUN AS SCRIPT
# -------------------

if __name__ == "__main__":
    print("Team3_Connect_4_Agent.py is intended to be imported and not executed.")
else:
    print("Team3_Connect_4_Agent.py has been imported.")
