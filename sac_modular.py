import argparse
import datetime
import gym
import numpy as np
import itertools
import torch
import time
from sac import SAC
from tensorboardX import SummaryWriter
from replay_memory import ReplayMemory
from env import RAEnv
import pygame

pygame.init()
parser = argparse.ArgumentParser(description='PyTorch Soft Actor-Critic Args')
parser.add_argument('--env-name', default="RAEnv-v0",
                    help='Environment (default: RAEnv-v0)')
parser.add_argument('--policy', default="Gaussian",
                    help='Policy Type: Gaussian | Deterministic (default: Gaussian)')
parser.add_argument('--eval', type=bool, default=True,
                    help='Evaluates a policy a policy every 50 episode (default: True)')
parser.add_argument('--modular', action="store_true",
                    help='Uses two agents, one for each task (default: True)')
parser.add_argument('--gamma', type=float, default=0.99, metavar='G',
                    help='discount factor for reward (default: 0.99)')
parser.add_argument('--tau', type=float, default=0.005, metavar='G',
                    help='target smoothing coefficient(τ) (default: 0.005)')
parser.add_argument('--lr', type=float, default=0.003, metavar='G',
                    help='learning rate (default: 0.003)')
parser.add_argument('--alpha', type=float, default=0.2, metavar='G',
                    help='Temperature parameter α determines the relative importance of the entropy\
                            term against the reward (default: 0.2)')
parser.add_argument('--automatic_entropy_tuning', type=bool, default=False, metavar='G',
                    help='Automaically adjust α (default: False)')
parser.add_argument('--seed', type=int, default=123456, metavar='N',
                    help='random seed (default: 123456)')
parser.add_argument('--batch_size', type=int, default=256, metavar='N',
                    help='batch size (default: 256)')
parser.add_argument('--num_steps', type=int, default=1000001, metavar='N',
                    help='maximum number of steps (default: 1000000)')
parser.add_argument('--hidden_size', type=int, default=256, metavar='N',
                    help='hidden size (default: 256)')
parser.add_argument('--updates_per_step', type=int, default=1, metavar='N',
                    help='model updates per simulator step (default: 1)')
parser.add_argument('--start_steps', type=int, default=10000, metavar='N',
                    help='Steps sampling random actions (default: 10000)')
parser.add_argument('--target_update_interval', type=int, default=1, metavar='N',
                    help='Value target update per no. of updates per step (default: 1)')
parser.add_argument('--replay_size', type=int, default=1000000, metavar='N',
                    help='size of replay buffer (default: 10000000)')
parser.add_argument('--cuda', action="store_true",
                    help='run on CUDA (default: False)')
args = parser.parse_args()

# Environment
# env = NormalizedActions(gym.make(args.env_name))

# env = gym.make(args.env_name)
env = RAEnv()
torch.manual_seed(args.seed)
np.random.seed(args.seed)
env.seed(args.seed)

# env.reset()
# env.init_pygame()
# env.render()
# pygame.event.wait(0)
# exit(0)

# Agent

print("modular:", args.modular)
print('cuda', args.cuda)
print(torch.cuda.get_device_name(0))

agent_1 = SAC(env.observation_space.shape[0], env.action_space, args)
if args.modular:
    agent_2 = SAC(env.observation_space.shape[0], env.action_space, args)

#TesnorboardX
writer_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

writer_1 = SummaryWriter(logdir='runs/{}_SAC_1_{}_{}_{}'.format(writer_datetime, args.env_name,
                                                             args.policy, "autotune" if args.automatic_entropy_tuning else ""))


# Memory
memory_1 = ReplayMemory(args.replay_size, args.seed)

# Training Loop
total_numsteps = 0
updates_1 = 0

for i_episode in range(1500):#itertools.count(1):
    episode_reward = 0
    episode_steps = 0
    done = False
    state = env.reset()

    while not done:
        agent = agent_1
        memory = memory_1
        writer = writer_1
        updates = updates_1

        if args.start_steps > total_numsteps:
            action = env.action_space.sample()  # Sample random action
        else:
            action = agent.select_action(state)  # Sample action from policy

        if len(memory) > args.batch_size:
            # Number of updates per step in environment
            for i in range(args.updates_per_step):
                # Update parameters of all the networks
                critic_1_loss, critic_2_loss, policy_loss, ent_loss, alpha = agent.update_parameters(memory, args.batch_size, updates)

                writer.add_scalar('loss/critic_1', critic_1_loss, updates)
                writer.add_scalar('loss/critic_2', critic_2_loss, updates)
                writer.add_scalar('loss/policy', policy_loss, updates)
                writer.add_scalar('loss/entropy_loss', ent_loss, updates)
                writer.add_scalar('entropy_temprature/alpha', alpha, updates)
                updates += 1

        next_state, reward, done, _ = env.step(action) # Step
        episode_steps += 1
        total_numsteps += 1
        episode_reward += reward

        # Ignore the "done" signal if it comes from hitting the time horizon.
        # (https://github.com/openai/spinningup/blob/master/spinup/algos/sac/sac.py)
        mask = 1 if episode_steps == env._max_episode_steps else float(not done)

        memory.push(state, action, reward, next_state, mask) # Append transition to memory

        state = next_state

    if total_numsteps > args.num_steps:
        break

    writer_1.add_scalar('reward/train', episode_reward, i_episode)

    print("Episode: {}, total numsteps: {}, episode steps: {}, reward: {}".format(i_episode, total_numsteps, episode_steps, round(episode_reward, 2)))

    # args.eval = False
    if i_episode % 50 == 0 and args.eval is True:
        avg_reward = 0.
        episodes = 1
        for _  in range(episodes):
            state = env.reset()
            episode_reward = 0
            done = False
            env.init_pygame()
            while not done:
                agent = agent_1
                memory = memory_1
                writer = writer_1

                action = agent.select_action(state, evaluate=True)

                next_state, reward, done, _ = env.step(action)
                episode_reward += reward
                time.sleep(0.01)
                env.render()

                state = next_state
            avg_reward += episode_reward
        avg_reward /= episodes

        writer_1.add_scalar('avg_reward/test', avg_reward, i_episode)

        print("----------------------------------------")
        print("Test Episodes: {}, Avg. Reward: {}".format(episodes, round(avg_reward, 2)))
        print("----------------------------------------")

env.close()

