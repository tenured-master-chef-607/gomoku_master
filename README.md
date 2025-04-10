# Gomoku Reinforcement Learning

This project implements a reinforcement learning agent to play Gomoku (Five in a Row) using Deep Q-Learning (DQN).

## Game Rules

- The game is played on a 19x19 board
- Players take turns placing stones (black and white)
- The first player to connect 5 stones horizontally, vertically, or diagonally wins
- If the board is filled with no winner, the game is a draw

## Project Structure

- `board.py`: Implements the core Gomoku game logic
- `gomoku_env.py`: Creates a Gymnasium environment for the Gomoku game
- `dqn_agent.py`: Implements a Deep Q-Network agent with experience replay
- `train.py`: Handles the training process with TensorBoard logging
- `evaluate.py`: Provides a GUI for playing against the trained agent

## Requirements

```
numpy==1.24.3
pygame==2.5.2
torch==2.2.0
gymnasium==0.29.1
tensorboard==2.15.1
```

## Usage

### Training the Agent

To train the agent, run:

```bash
python train.py
```

This will start training the DQN agent. The training progress can be monitored using TensorBoard:

```bash
tensorboard --logdir=logs
```

### Playing Against the Agent

To play against the trained agent, run:

```bash
python evaluate.py models/gomoku_dqn_<episode>.pth
```

Replace `<episode>` with the episode number of the model you want to use (e.g., `gomoku_dqn_1000.pth`).

In the game, you play as black (first player) and the AI plays as white (second player).

## Implementation Details

- The agent uses a simple feedforward neural network to learn the Q-values for each possible action
- Experience replay is used to stabilize learning
- A target network is updated periodically to prevent overestimation
- Epsilon-greedy exploration strategy is used to balance exploration and exploitation
- The reward function encourages winning and discourages losing

## Customization

You can adjust the following parameters in the code:

- Board size: Change the `size` parameter in `Board` and `GomokuEnv` classes
- Training parameters: Modify the `episodes`, `batch_size`, and `target_update` parameters in `train.py`
- Neural network architecture: Adjust the layers and sizes in the `DQN` class in `dqn_agent.py` 