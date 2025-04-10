import gymnasium as gym
import numpy as np
from board import Board

class GomokuEnv(gym.Env):
    def __init__(self, size=19):
        super().__init__()
        self.size = size
        self.board = Board(size)
        
        # Define action and observation spaces
        self.action_space = gym.spaces.Discrete(size * size)
        self.observation_space = gym.spaces.Box(
            low=-1, high=1, shape=(size, size), dtype=np.float32
        )
        
        self.reset()

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.board = Board(self.size)
        return self._get_observation(), {}

    def step(self, action):
        # Convert action to row, col
        row = action // self.size
        col = action % self.size
        
        # Make move
        valid_move = self.board.make_move(row, col)
        
        # Get observation
        observation = self._get_observation()
        
        # Check if game is done
        done = self.board.check_win() or len(self.board.get_valid_moves()) == 0
        
        # Calculate reward
        if not valid_move:
            reward = -10  # Penalty for invalid move
        elif done:
            if self.board.check_win():
                reward = 100 if self.board.current_player == -1 else -100  # Win/Lose
            else:
                reward = 0  # Draw
        else:
            reward = -0.1  # Small penalty for each move to encourage faster wins
        
        return observation, reward, done, False, {}

    def _get_observation(self):
        return self.board.board.astype(np.float32)

    def render(self):
        print(self.board) 