"""
Gomoku Board Module
Author: TJ Qiu
Copyright © 2023 TJ Qiu. All rights reserved.
"""

import numpy as np

class Board:
    def __init__(self, size=19):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.last_move = None
        self.current_player = 1  # 1 for black, -1 for white
        self.move_history = []  # Store move history for undo functionality

    def make_move(self, row, col):
        if self.is_valid_move(row, col):
            self.board[row][col] = self.current_player
            self.last_move = (row, col)
            # Store the move in history
            self.move_history.append((row, col, self.current_player))
            self.current_player *= -1
            return True
        return False

    def is_valid_move(self, row, col):
        return (0 <= row < self.size and 
                0 <= col < self.size and 
                self.board[row][col] == 0)

    def check_win(self):
        if self.last_move is None:
            return False
        
        row, col = self.last_move
        player = self.board[row][col]
        
        # Directions to check: horizontal, vertical, diagonal down-right, diagonal down-left
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1  # Count the current stone
            
            # Check in positive direction
            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
                
                # If we already have 5 in a row, we can stop checking
                if count >= 5:
                    return True
            
            # Check in negative direction
            r, c = row - dr, col - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
                
                # If we already have 5 in a row, we can stop checking
                if count >= 5:
                    return True
        
        return False

    def get_valid_moves(self):
        moves = []
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    moves.append((i, j))
        return moves

    def copy(self):
        new_board = Board(self.size)
        new_board.board = self.board.copy()
        new_board.last_move = self.last_move
        new_board.current_player = self.current_player
        new_board.move_history = self.move_history.copy()
        return new_board

    def __str__(self):
        symbols = {0: '.', 1: 'X', -1: 'O'}
        board_str = ""
        for row in self.board:
            board_str += " ".join(symbols[cell] for cell in row) + "\n"
        return board_str 

    def undo_move(self):
        """Undo the last move and return to the previous state."""
        if not self.move_history:
            return False  # No moves to undo
            
        # Get the last move from history
        row, col, player = self.move_history.pop()
        
        # Clear the position
        self.board[row][col] = 0
        
        # Update the current player
        self.current_player = player
        
        # Update the last move
        if self.move_history:
            self.last_move = (self.move_history[-1][0], self.move_history[-1][1])
        else:
            self.last_move = None
            
        return True 