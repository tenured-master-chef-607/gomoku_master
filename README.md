# Gomoku Master

A sophisticated AI system for playing Gomoku (Five in a Row) with both traditional minimax AI and reinforcement learning capabilities.

## Game Rules

- The game is played on a board (default 15×15)
- Players take turns placing stones (black and white)
- The first player to connect 5 stones horizontally, vertically, or diagonally wins
- If the board is filled with no winner, the game is a draw

## Features

- Beautiful GUI with wooden board texture and stone animations
- Multiple AI difficulty levels (Easy, Medium, Hard)
- Play as either Black or White
- Classic AI using Minimax algorithm with alpha-beta pruning
- Optional reinforcement learning agent using Deep Q-Learning (DQN)

## Project Structure

- `main.py`: Entry point for running the game
- `gui.py`: Implements the graphical user interface with Pygame
- `board.py`: Implements the core Gomoku game logic
- `ai.py`: Contains the minimax AI implementation with various difficulty levels
- `gomoku_env.py`: Creates a Gymnasium environment for reinforcement learning
- `dqn_agent.py`: Implements a Deep Q-Network agent with experience replay
- `train.py`: Handles the training of the DQN agent with TensorBoard logging
- `evaluate.py`: Provides functionality for evaluating trained agents

## Requirements

```
numpy
pygame
torch
gymnasium
tensorboard
```

## Usage

### Playing the Game

To play against the classic minimax AI:

```bash
python main.py
```

This will open the GUI where you can:
- Choose to play as Black or White
- Select AI difficulty (Easy, Medium, Hard)
- Place stones by clicking on the board

### Training the Reinforcement Learning Agent

To train the DQN agent, run:

```bash
python train.py
```

This will start training the DQN agent. The training progress can be monitored using TensorBoard:

```bash
tensorboard --logdir=logs
```

### Playing Against the Trained DQN Agent

To play against the trained agent, run:

```bash
python evaluate.py models/gomoku_dqn_<episode>.pth
```

Replace `<episode>` with the episode number of the model you want to use.

## AI Implementation Details

### Classic AI (Minimax)
- Uses minimax algorithm with alpha-beta pruning
- Evaluates board positions using pattern recognition
- Adjustable depth and time limits based on difficulty
- Tactical threat detection for improved play

### Reinforcement Learning Agent
- Uses a Deep Q-Network (DQN) to learn optimal moves
- Experience replay stabilizes learning
- Target network updated periodically to prevent overestimation
- Epsilon-greedy exploration strategy balances exploration and exploitation

## Customization

To customize the game or AI behavior:

- Board size: Modify the `board_size` parameter in `GomokuGUI` constructor
- AI difficulty: Change the `difficulty` parameter when creating a `GomokuAI` instance
- Neural network architecture: Adjust the layers in the `DQN` class
- Training parameters: Modify parameters in `train.py` 