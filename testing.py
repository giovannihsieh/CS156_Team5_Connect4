from Team5_Connect_4_Agent import init_agent, what_is_your_move

# Example test board state (6 rows x 7 columns)
test_board = [
    [' ', ' ', ' ', ' ', ' ', ' ', ' '],  # Top row (row 0)
    [' ', ' ', ' ', ' ', ' ', ' ', ' '],  # row 1
    [' ', ' ', ' ', 'O', ' ', ' ', ' '],  # row 2
    [' ', ' ', ' ', 'X', ' ', ' ', ' '],  # row 3
    [' ', ' ', ' ', 'O', ' ', ' ', ' '],  # row 4
    [' ', ' ', ' ', 'X', ' ', ' ', ' ']   # Bottom row (row 5)
]

# Initialize the agent as 'O' on a 6x7 board
init_agent('O', 6, 7, test_board)

# Ask the agent to make a move
move = what_is_your_move(test_board, 6, 7, 'X')
print("Agent chose column:", move)