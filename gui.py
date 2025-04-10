import pygame
import sys
import os
from board import Board
from ai import GomokuAI

class GomokuGUI:
    def __init__(self, board_size=15, cell_size=40, margin=50):
        self.board_size = board_size
        self.cell_size = cell_size
        self.margin = margin
        self.window_size = (board_size * cell_size + 2 * margin, 
                          board_size * cell_size + 2 * margin)
        
        # Initialize Pygame
        pygame.init()
        
        # Set up the display
        os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center the window
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Gomoku - Click to Play")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BROWN = (139, 69, 19)
        self.GRAY = (200, 200, 200)
        self.HOVER_COLOR = (255, 255, 255, 128)  # Semi-transparent white
        
        # Game state
        self.board = Board()
        self.ai = GomokuAI(depth=3)
        self.game_over = False
        self.winner = None
        self.hover_pos = None
        
        # Load images
        self.black_stone = pygame.Surface((self.cell_size - 10, self.cell_size - 10))
        self.black_stone.fill(self.BLACK)
        self.white_stone = pygame.Surface((self.cell_size - 10, self.cell_size - 10))
        self.white_stone.fill(self.WHITE)
        
        # Create a simple icon
        icon_size = 32
        icon = pygame.Surface((icon_size, icon_size))
        icon.fill(self.BROWN)
        pygame.draw.circle(icon, self.BLACK, (icon_size//2, icon_size//2), icon_size//3)
        pygame.display.set_icon(icon)
        
    def draw_board(self):
        # Draw background
        self.screen.fill(self.BROWN)
        
        # Draw grid
        for i in range(self.board_size):
            # Horizontal lines
            pygame.draw.line(self.screen, self.BLACK,
                           (self.margin, self.margin + i * self.cell_size),
                           (self.window_size[0] - self.margin, self.margin + i * self.cell_size),
                           2)  # Thicker lines
            # Vertical lines
            pygame.draw.line(self.screen, self.BLACK,
                           (self.margin + i * self.cell_size, self.margin),
                           (self.margin + i * self.cell_size, self.window_size[1] - self.margin),
                           2)  # Thicker lines
        
        # Draw hover effect
        if self.hover_pos and not self.game_over:
            row, col = self.hover_pos
            if self.board.board[row][col] == 0:  # Only show hover on empty cells
                hover_surface = pygame.Surface((self.cell_size - 10, self.cell_size - 10))
                hover_surface.fill(self.WHITE)
                hover_surface.set_alpha(128)  # Semi-transparent
                self.screen.blit(hover_surface,
                               (self.margin + col * self.cell_size - (self.cell_size - 10) // 2,
                                self.margin + row * self.cell_size - (self.cell_size - 10) // 2))
        
        # Draw stones
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board.board[i][j] == 1:  # Black stone
                    self.screen.blit(self.black_stone,
                                   (self.margin + j * self.cell_size - (self.cell_size - 10) // 2,
                                    self.margin + i * self.cell_size - (self.cell_size - 10) // 2))
                elif self.board.board[i][j] == -1:  # White stone
                    self.screen.blit(self.white_stone,
                                   (self.margin + j * self.cell_size - (self.cell_size - 10) // 2,
                                    self.margin + i * self.cell_size - (self.cell_size - 10) // 2))
        
        # Draw game over message
        if self.game_over:
            font = pygame.font.Font(None, 36)
            if self.winner == 1:
                text = font.render("You won! Click to play again.", True, self.BLACK)
            elif self.winner == -1:
                text = font.render("AI won! Click to play again.", True, self.BLACK)
            else:
                text = font.render("Draw! Click to play again.", True, self.BLACK)
            text_rect = text.get_rect(center=(self.window_size[0] // 2, self.margin // 2))
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def get_board_position(self, pos):
        x, y = pos
        row = round((y - self.margin) / self.cell_size)
        col = round((x - self.margin) / self.cell_size)
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return row, col
        return None
    
    def reset_game(self):
        self.board = Board()
        self.game_over = False
        self.winner = None
        self.hover_pos = None
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEMOTION:
                    self.hover_pos = self.get_board_position(event.pos)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        self.reset_game()
                    else:
                        pos = self.get_board_position(event.pos)
                        if pos and self.board.make_move(*pos):
                            if self.board.check_win():
                                self.game_over = True
                                self.winner = 1
                            else:
                                # AI's turn
                                ai_move = self.ai.get_best_move(self.board)
                                if ai_move:
                                    self.board.make_move(*ai_move)
                                    if self.board.check_win():
                                        self.game_over = True
                                        self.winner = -1
            
            self.draw_board()
            pygame.time.delay(100)  # Cap the frame rate

if __name__ == "__main__":
    game = GomokuGUI()
    game.run() 