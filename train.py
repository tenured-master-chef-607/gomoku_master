import numpy as np
from gomoku_env import GomokuEnv
from dqn_agent import DQNAgent
from torch.utils.tensorboard import SummaryWriter
import os

def train(episodes=20000, batch_size=64, target_update=20):
    env = GomokuEnv()
    state_size = env.size
    action_size = env.size * env.size
    agent = DQNAgent(state_size, action_size)
    
    # Create logs directory for tensorboard
    if not os.path.exists('logs'):
        os.makedirs('logs')
    writer = SummaryWriter('logs/gomoku_dqn')
    
    for episode in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            valid_moves = [i * env.size + j for i, j in env.board.get_valid_moves()]
            action = agent.act(state, valid_moves)
            next_state, reward, done, _, _ = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            
            if len(agent.memory) > batch_size:
                agent.replay(batch_size)
        
        # Update target network periodically
        if episode % target_update == 0:
            agent.update_target_model()
        
        # Log metrics
        writer.add_scalar('Reward/Episode', total_reward, episode)
        writer.add_scalar('Epsilon/Episode', agent.epsilon, episode)
        
        # Save model periodically
        if episode % 100 == 0:
            agent.save(f'models/gomoku_dqn_{episode}.pth')
        
        # Print progress
        if episode % 10 == 0:
            print(f"Episode: {episode}/{episodes}, Score: {total_reward}, Epsilon: {agent.epsilon:.2f}")

if __name__ == "__main__":
    # Create models directory if it doesn't exist
    if not os.path.exists('models'):
        os.makedirs('models')
    train() 