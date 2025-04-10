import numpy as np
from gomoku_env import GomokuEnv
from dqn_agent import DQNAgent
import pygame
import sys

class GomokuGUI:
    def __init__(self, size=19, cell_size=30):
        self.size = size
        self.cell_size = cell_size
        self.margin = 50
        self.window_size = size * cell_size + 2 * self.margin
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_size, self.window_size))
        pygame.display.set_caption("Gomoku DQN Evaluation")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BROWN = (139, 69, 19)
        self.RED = (255, 0, 0)
        
    def draw_board(self, board):
        self.screen.fill(self.BROWN)
        
        # Draw grid
        for i in range(self.size):
            # Vertical lines
            pygame.draw.line(self.screen, self.BLACK,
                           (self.margin + i * self.cell_size, self.margin),
                           (self.margin + i * self.cell_size, self.window_size - self.margin))
            # Horizontal lines
            pygame.draw.line(self.screen, self.BLACK,
                           (self.margin, self.margin + i * self.cell_size),
                           (self.window_size - self.margin, self.margin + i * self.cell_size))
        
        # Draw stones
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] != 0:
                    color = self.BLACK if board[i][j] == 1 else self.WHITE
                    center = (self.margin + j * self.cell_size,
                            self.margin + i * self.cell_size)
                    pygame.draw.circle(self.screen, color, center, self.cell_size // 2 - 2)
        
        pygame.display.flip()
    
    def get_cell_from_pos(self, pos):
        x, y = pos
        row = round((y - self.margin) / self.cell_size)
        col = round((x - self.margin) / self.cell_size)
        if 0 <= row < self.size and 0 <= col < self.size:
            return row, col
        return None

def evaluate(model_path):
    env = GomokuEnv()
    state_size = env.size
    action_size = env.size * env.size
    agent = DQNAgent(state_size, action_size)
    agent.load(model_path)
    agent.epsilon = 0  # No exploration during evaluation
    
    gui = GomokuGUI()
    state, _ = env.reset()
    done = False
    
    while not done:
        gui.draw_board(env.board.board)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and env.board.current_player == 1:
                cell = gui.get_cell_from_pos(event.pos)
                if cell and env.board.is_valid_move(*cell):
                    row, col = cell
                    action = row * env.size + col
                    state, reward, done, _, _ = env.step(action)
                    gui.draw_board(env.board.board)
        
        if not done and env.board.current_player == -1:
            valid_moves = [i * env.size + j for i, j in env.board.get_valid_moves()]
            action = agent.act(state, valid_moves)
            state, reward, done, _, _ = env.step(action)
            gui.draw_board(env.board.board)
        
        if done:
            pygame.time.wait(2000)  # Wait 2 seconds before closing
            break

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python evaluate.py <model_path>")
        sys.exit(1)
    evaluate(sys.argv[1]) 