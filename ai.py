import numpy as np
from board import Board
import random

class GomokuAI:
    def __init__(self, depth=5):
        self.depth = depth
        self.evaluation_cache = {}
        self.opening_moves = [(7, 7), (7, 8), (8, 7), (8, 8)]

    def evaluate_position(self, board):
        # Convert board to string for caching
        board_str = str(board.board)
        if board_str in self.evaluation_cache:
            return self.evaluation_cache[board_str]

        score = 0
        size = board.size
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        # Count pieces for each player
        black_count = sum(row.count(1) for row in board.board)
        white_count = sum(row.count(-1) for row in board.board)
        
        # Material advantage
        score += (black_count - white_count) * 100

        for i in range(size):
            for j in range(size):
                if board.board[i][j] != 0:
                    player = board.board[i][j]
                    for dr, dc in directions:
                        # Check if this is the start of a sequence
                        if (i - dr < 0 or j - dc < 0 or i - dr >= size or j - dc >= size or 
                            board.board[i-dr][j-dc] != player):
                            count = 1
                            blocked = False
                            space_before = False
                            space_after = False
                            
                            # Check space before
                            if (0 <= i-dr < size and 0 <= j-dc < size and 
                                board.board[i-dr][j-dc] == 0):
                                space_before = True
                            
                            # Count consecutive pieces
                            r, c = i + dr, j + dc
                            while (0 <= r < size and 0 <= c < size and 
                                   board.board[r][c] == player):
                                count += 1
                                r += dr
                                c += dc
                            
                            # Check space after
                            if (0 <= r < size and 0 <= c < size and 
                                board.board[r][c] == 0):
                                space_after = True
                            
                            # Check if sequence is blocked
                            if not space_before and not space_after:
                                blocked = True
                            
                            # Score based on sequence length, blocking, and spaces
                            if count >= 5:
                                score += player * 100000
                            elif count == 4:
                                if not blocked:
                                    score += player * 10000
                                elif space_before or space_after:
                                    score += player * 5000
                            elif count == 3:
                                if not blocked:
                                    score += player * 1000
                                elif space_before and space_after:
                                    score += player * 500
                            elif count == 2:
                                if not blocked:
                                    score += player * 100
                                elif space_before and space_after:
                                    score += player * 50
                            elif count == 1:
                                if space_before and space_after:
                                    score += player * 10

        # Center control bonus
        center_size = 3
        center_start = (size - center_size) // 2
        for i in range(center_start, center_start + center_size):
            for j in range(center_start, center_start + center_size):
                if board.board[i][j] != 0:
                    score += board.board[i][j] * 50

        # Mobility bonus (number of valid moves)
        valid_moves = board.get_valid_moves()
        score += len(valid_moves) * 10

        self.evaluation_cache[board_str] = score
        return score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.check_win():
            return self.evaluate_position(board)

        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return 0

        # Sort moves by evaluation (best moves first)
        move_scores = []
        for move in valid_moves:
            new_board = board.copy()
            new_board.make_move(*move)
            score = self.evaluate_position(new_board)
            move_scores.append((move, score))
        
        # Sort moves by score (highest for maximizing, lowest for minimizing)
        move_scores.sort(key=lambda x: x[1], reverse=maximizing_player)
        sorted_moves = [move for move, _ in move_scores]

        if maximizing_player:
            max_eval = float('-inf')
            for move in sorted_moves:
                new_board = board.copy()
                new_board.make_move(*move)
                eval = self.minimax(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in sorted_moves:
                new_board = board.copy()
                new_board.make_move(*move)
                eval = self.minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, board):
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None

        # Opening book
        if sum(row.count(0) for row in board.board) > 200:  # First few moves
            opening_moves = [move for move in self.opening_moves if move in valid_moves]
            if opening_moves:
                return random.choice(opening_moves)

        best_move = None
        best_eval = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        # Sort moves by evaluation
        move_scores = []
        for move in valid_moves:
            new_board = board.copy()
            new_board.make_move(*move)
            score = self.evaluate_position(new_board)
            move_scores.append((move, score))
        
        move_scores.sort(key=lambda x: x[1], reverse=True)
        sorted_moves = [move for move, _ in move_scores]

        for move in sorted_moves:
            new_board = board.copy()
            new_board.make_move(*move)
            eval = self.minimax(new_board, self.depth - 1, alpha, beta, False)
            if eval > best_eval:
                best_eval = eval
                best_move = move
            alpha = max(alpha, eval)

        return best_move 