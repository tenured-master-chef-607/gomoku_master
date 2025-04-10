"""
Gomoku AI Module
Author: TJ Qiu
Copyright © 2023 TJ Qiu. All rights reserved.
"""

import numpy as np
from board import Board
import random
import time

class GomokuAI:
    def __init__(self, depth=3, difficulty="medium"):
        self.depth = depth
        self.evaluation_cache = {}
        self.opening_moves = [(7, 7), (7, 8), (8, 7), (8, 8), (6, 6), (6, 7), (7, 6)]
        
        # Different time limits and depths based on difficulty
        self.difficulty = difficulty.lower()
        if self.difficulty == "easy":
            self.time_limit = 1.0
            self.depth = 2
            self.use_opening_book = False
        elif self.difficulty == "medium":
            self.time_limit = 3.0
            self.depth = 4
            self.use_opening_book = True
        else:  # hard
            self.time_limit = 5.0
            self.depth = 6
            self.use_opening_book = True

    def evaluate_position(self, board):
        # Check for cached evaluation
        board_hash = hash(str(board.board))
        if board_hash in self.evaluation_cache:
            return self.evaluation_cache[board_hash]
            
        # Check for immediate win
        if board.check_win():
            score = 100000 * -board.current_player  # Opponent won
            self.evaluation_cache[board_hash] = score
            return score
            
        score = 0
        size = board.size
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        # Count pieces for each player using numpy
        black_count = np.sum(board.board == 1)
        white_count = np.sum(board.board == -1)
        
        # Material advantage (small factor)
        score += (black_count - white_count) * 10

        # Evaluate patterns for each player
        for player in [1, -1]:  # 1 for black, -1 for white
            player_factor = 1 if player == 1 else -1
            
            # Create pattern scores based on threat level
            # Five in a row (win)
            five_score = 100000 * player_factor
            # Open four (one move to win)
            open_four_score = 15000 * player_factor
            # Blocked four (can be blocked)
            blocked_four_score = 4000 * player_factor
            # Open three (can create an open four)
            open_three_score = 3000 * player_factor
            # Blocked three
            blocked_three_score = 1000 * player_factor
            # Open two
            open_two_score = 500 * player_factor
            
            # Scan the entire board for patterns
            for i in range(size):
                for j in range(size):
                    if board.board[i][j] == player:
                        # Check each direction from this position
                        for dr, dc in directions:
                            # Count consecutive stones and empty spaces
                            consecutive = 1
                            empty_before = False
                            empty_after = False
                            
                            # Check backwards for empty space
                            r, c = i - dr, j - dc
                            if 0 <= r < size and 0 <= c < size and board.board[r][c] == 0:
                                empty_before = True
                            
                            # Check forwards for consecutive stones and empty space
                            r, c = i + dr, j + dc
                            while 0 <= r < size and 0 <= c < size and board.board[r][c] == player:
                                consecutive += 1
                                r += dr
                                c += dc
                            
                            # Check for empty space after consecutive stones
                            if 0 <= r < size and 0 <= c < size and board.board[r][c] == 0:
                                empty_after = True
                            
                            # Evaluate the pattern
                            if consecutive >= 5:
                                score += five_score
                            elif consecutive == 4:
                                if empty_before and empty_after:
                                    score += open_four_score
                                elif empty_before or empty_after:
                                    score += blocked_four_score
                            elif consecutive == 3:
                                if empty_before and empty_after:
                                    score += open_three_score
                                elif empty_before or empty_after:
                                    score += blocked_three_score
                            elif consecutive == 2:
                                if empty_before and empty_after:
                                    score += open_two_score

        # Center control bonus (weighted by distance from center)
        center = size // 2
        for i in range(size):
            for j in range(size):
                if board.board[i][j] != 0:
                    # Distance from center (smaller is better)
                    distance = abs(i - center) + abs(j - center)
                    # Maximum distance could be 2*center
                    distance_factor = 1 - (distance / (2 * center))
                    # Apply center control bonus
                    score += board.board[i][j] * 50 * distance_factor

        # Proximity to opponent's stones
        # Encourage play near opponent's pieces
        for i in range(size):
            for j in range(size):
                if board.board[i][j] == 0:  # Empty spot
                    # Check surrounding squares for opponent pieces
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            ni, nj = i + di, j + dj
                            if 0 <= ni < size and 0 <= nj < size and board.board[ni][nj] == -board.current_player:
                                # Empty spots next to opponent pieces are valuable
                                score += board.current_player * 5

        # Cache the evaluation for future use
        self.evaluation_cache[board_hash] = score
        return score

    def _is_relevant_move(self, board, move):
        """Check if a move is near existing stones and worth evaluating."""
        i, j = move
        size = board.size
        
        # Consider all moves in small boards
        if size <= 10:
            return True
            
        # Always consider center area
        center = size // 2
        if abs(i - center) <= 2 and abs(j - center) <= 2:
            return True
            
        # Check proximity to existing stones
        for di in range(-2, 3):
            for dj in range(-2, 3):
                ni, nj = i + di, j + dj
                if 0 <= ni < size and 0 <= nj < size and board.board[ni][nj] != 0:
                    return True
                    
        return False

    def minimax(self, board, depth, alpha, beta, maximizing_player, start_time):
        # Check if time limit exceeded
        if time.time() - start_time > self.time_limit:
            return self.evaluate_position(board)
            
        # Terminal conditions
        if depth == 0 or board.check_win():
            return self.evaluate_position(board)

        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return 0

        # Filter to relevant moves to improve efficiency
        relevant_moves = [move for move in valid_moves if self._is_relevant_move(board, move)]
        if not relevant_moves:
            relevant_moves = valid_moves
            
        # Limit the number of moves to evaluate at each level
        if len(relevant_moves) > 12:
            # Sort moves by distance to the center
            center = board.size // 2
            relevant_moves.sort(key=lambda m: abs(m[0] - center) + abs(m[1] - center))
            relevant_moves = relevant_moves[:12]  # Take only the 12 closest to center

        if maximizing_player:
            max_eval = float('-inf')
            for move in relevant_moves:
                new_board = board.copy()
                new_board.make_move(*move)
                eval = self.minimax(new_board, depth - 1, alpha, beta, False, start_time)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in relevant_moves:
                new_board = board.copy()
                new_board.make_move(*move)
                eval = self.minimax(new_board, depth - 1, alpha, beta, True, start_time)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def _check_for_threats(self, board, player_color):
        """Check for significant threats on the board and return the best move to make or block.
        
        Handles threats in order of priority:
        1. Immediate win (5 in a row)
        2. Block opponent's immediate win
        3. Create an open four (one move away from winning)
        4. Block opponent's open four
        3. Create/extend an open three that can lead to an open four
        4. Block opponent's open three
        """
        size = board.size
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        opponent_color = -player_color
        
        # Dictionary to track moves by threat level
        threat_moves = {
            "win": [],             # Our immediate winning moves
            "block_win": [],       # Moves to block opponent's win
            "create_open4": [],    # Create our open four
            "block_open4": [],     # Block opponent's open four
            "create_open3": [],    # Create our open three
            "block_open3": [],     # Block opponent's open three
            "extend_seq": []       # Extend an existing sequence
        }
        
        # Check each empty cell for potential threats
        for i in range(size):
            for j in range(size):
                if board.board[i][j] != 0:  # Skip non-empty cells
                    continue
                    
                # Try this move for us
                temp_board = board.copy()
                temp_board.board[i][j] = player_color
                
                # Check if this gives us a win
                if self._has_five_in_a_row(temp_board, i, j, player_color):
                    threat_moves["win"].append((i, j))
                    continue
                
                # Try this move for opponent
                temp_board = board.copy()
                temp_board.board[i][j] = opponent_color
                
                # Check if opponent would win here
                if self._has_five_in_a_row(temp_board, i, j, opponent_color):
                    threat_moves["block_win"].append((i, j))
                    continue
                
                # Check for creating open fours for us
                temp_board = board.copy()
                temp_board.board[i][j] = player_color
                if self._has_open_four(temp_board, i, j, player_color):
                    threat_moves["create_open4"].append((i, j))
                    continue
                
                # Check for blocking opponent's open fours
                temp_board = board.copy()
                temp_board.board[i][j] = opponent_color
                if self._has_open_four(temp_board, i, j, opponent_color):
                    threat_moves["block_open4"].append((i, j))
                    continue
                
                # Check for creating open threes for us
                temp_board = board.copy()
                temp_board.board[i][j] = player_color
                if self._has_open_three(temp_board, i, j, player_color):
                    threat_moves["create_open3"].append((i, j))
                    continue
                
                # Check for blocking opponent's open threes
                temp_board = board.copy()
                temp_board.board[i][j] = opponent_color
                if self._has_open_three(temp_board, i, j, opponent_color):
                    threat_moves["block_open3"].append((i, j))
                    continue
                
                # Check if this move extends an existing sequence
                temp_board = board.copy()
                temp_board.board[i][j] = player_color
                if self._extends_sequence(temp_board, i, j, player_color):
                    threat_moves["extend_seq"].append((i, j))
        
        # Return the best move based on priority
        for threat_type in ["win", "block_win", "create_open4", "block_open4", "create_open3", "block_open3", "extend_seq"]:
            if threat_moves[threat_type]:
                # If we have multiple moves of the same threat level, pick the one closest to the center
                if len(threat_moves[threat_type]) > 1:
                    center = size // 2
                    threat_moves[threat_type].sort(key=lambda m: abs(m[0] - center) + abs(m[1] - center))
                return threat_moves[threat_type][0]
        
        return None

    def _has_five_in_a_row(self, board, row, col, color):
        """Check if placing a stone at (row, col) creates 5 in a row."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        size = board.size
        
        for dr, dc in directions:
            count = 1  # The stone we just placed
            
            # Check in positive direction
            r, c = row + dr, col + dc
            while 0 <= r < size and 0 <= c < size and board.board[r][c] == color:
                count += 1
                r += dr
                c += dc
            
            # Check in negative direction
            r, c = row - dr, col - dc
            while 0 <= r < size and 0 <= c < size and board.board[r][c] == color:
                count += 1
                r -= dr
                c -= dc
            
            if count >= 5:
                return True
        
        return False

    def _has_open_four(self, board, row, col, color):
        """Check if placing a stone at (row, col) creates an open four (one move away from winning)."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        size = board.size
        
        for dr, dc in directions:
            # Count consecutive stones
            count = 1  # The stone we just placed
            empty_ends = 0
            
            # Check if the sequence has open ends (spaces to extend)
            
            # Check in positive direction
            r, c = row + dr, col + dc
            while 0 <= r < size and 0 <= c < size and board.board[r][c] == color:
                count += 1
                r += dr
                c += dc
            
            # Is there an empty space after the sequence?
            if 0 <= r < size and 0 <= c < size and board.board[r][c] == 0:
                empty_ends += 1
            
            # Check in negative direction
            r, c = row - dr, col - dc
            while 0 <= r < size and 0 <= c < size and board.board[r][c] == color:
                count += 1
                r -= dr
                c -= dc
            
            # Is there an empty space before the sequence?
            if 0 <= r < size and 0 <= c < size and board.board[r][c] == 0:
                empty_ends += 1
            
            # An open four has exactly 4 stones and at least one open end
            if count == 4 and empty_ends >= 1:
                return True
        
        return False

    def _has_open_three(self, board, row, col, color):
        """Check if placing a stone at (row, col) creates an open three (can lead to an open four)."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        size = board.size
        
        for dr, dc in directions:
            # Count consecutive stones
            count = 1  # The stone we just placed
            empty_ends = 0
            
            # Check in positive direction
            r, c = row + dr, col + dc
            while 0 <= r < size and 0 <= c < size and board.board[r][c] == color:
                count += 1
                r += dr
                c += dc
            
            # Is there enough empty space after the sequence to make it valuable?
            empty_after = 0
            while 0 <= r < size and 0 <= c < size and board.board[r][c] == 0:
                empty_after += 1
                r += dr
                c += dc
                if empty_after >= 2:  # We need at least 2 empty spaces for an open three to be valuable
                    break
            
            if empty_after >= 1:
                empty_ends += 1
            
            # Check in negative direction
            r, c = row - dr, col - dc
            while 0 <= r < size and 0 <= c < size and board.board[r][c] == color:
                count += 1
                r -= dr
                c -= dc
            
            # Is there enough empty space before the sequence?
            empty_before = 0
            while 0 <= r < size and 0 <= c < size and board.board[r][c] == 0:
                empty_before += 1
                r -= dr
                c -= dc
                if empty_before >= 2:
                    break
            
            if empty_before >= 1:
                empty_ends += 1
            
            # An open three has exactly 3 stones and 2 open ends
            if count == 3 and empty_ends == 2 and (empty_before >= 1 and empty_after >= 1):
                return True
        
        return False

    def _extends_sequence(self, board, row, col, color):
        """Check if placing a stone at (row, col) extends an existing sequence."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        size = board.size
        
        for dr, dc in directions:
            # Count consecutive stones
            count = 1  # The stone we just placed
            
            # Check in positive direction
            r, c = row + dr, col + dc
            while 0 <= r < size and 0 <= c < size and board.board[r][c] == color:
                count += 1
                r += dr
                c += dc
            
            # Check in negative direction
            r, c = row - dr, col - dc
            while 0 <= r < size and 0 <= c < size and board.board[r][c] == color:
                count += 1
                r -= dr
                c -= dc
            
            # If we found a sequence of 2 or more, this move extends it
            if count >= 2:
                return True
        
        return False

    def get_best_move(self, board):
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None

        # Opening book moves (only on larger boards and if enabled)
        empty_count = np.sum(board.board == 0)
        if self.use_opening_book and board.size >= 15 and empty_count > board.size * board.size - 4:
            opening_moves = [move for move in self.opening_moves if move in valid_moves]
            if opening_moves:
                return random.choice(opening_moves)

        # For easy difficulty, sometimes make a random move
        if self.difficulty == "easy" and random.random() < 0.3:
            return random.choice(valid_moves)
            
        # Check for threats and respond to them
        threat_move = self._check_for_threats(board, board.current_player)
        if threat_move:
            return threat_move

        # Filter to relevant moves to improve efficiency
        relevant_moves = [move for move in valid_moves if self._is_relevant_move(board, move)]
        if not relevant_moves:
            relevant_moves = valid_moves

        # For very few moves left, just quickly evaluate each one
        if len(relevant_moves) <= 3:
            best_move = None
            best_score = float('-inf')
            for move in relevant_moves:
                new_board = board.copy()
                new_board.make_move(*move)
                score = self.evaluate_position(new_board)
                if score > best_score:
                    best_score = score
                    best_move = move
            return best_move

        # Initialize search
        best_move = None
        best_eval = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        start_time = time.time()

        # Sort moves by distance to the center
        center = board.size // 2
        relevant_moves.sort(key=lambda m: abs(m[0] - center) + abs(m[1] - center))
        
        # Limit the number of moves to evaluate based on difficulty
        max_moves = 8 if self.difficulty == "easy" else (12 if self.difficulty == "medium" else 16)
        if len(relevant_moves) > max_moves:
            relevant_moves = relevant_moves[:max_moves]
    
        # Regular minimax search with iterative deepening
        current_depth = 1
        while current_depth <= self.depth and time.time() - start_time < self.time_limit * 0.8:
            for move in relevant_moves:
                new_board = board.copy()
                new_board.make_move(*move)
                eval = self.minimax(new_board, current_depth - 1, alpha, beta, False, start_time)
                
                if eval > best_eval:
                    best_eval = eval
                    best_move = move
                
                alpha = max(alpha, eval)
                
                # Check if time limit is approaching
                if time.time() - start_time > self.time_limit * 0.8:
                    break
            
            current_depth += 1

        # If no move was selected (due to time limit), pick a good move
        if best_move is None and relevant_moves:
            # Try to find a move near existing stones
            for move in relevant_moves:
                if self._is_relevant_move(board, move):
                    return move
            
            # Fallback to center-biased random move
            center_dist = [(move, abs(move[0]-center) + abs(move[1]-center)) for move in relevant_moves]
            center_dist.sort(key=lambda x: x[1])
            return center_dist[0][0]

        return best_move 