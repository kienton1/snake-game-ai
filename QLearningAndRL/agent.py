
import torch
import random
import numpy as np
from SnakeGame import SnakeGameAI, Direction, Point
from collections import deque
from model import Linear_QNet, QTrainer
from helper import plot

from sympy.physics.quantum.operatorset import state_mapping
#MAX_MEMORY is in charge of limiting the size of the experience replay buffer to x amount of experiences
MAX_MEMORY = 100_000
#Batch_SIZE is the # of experiences sampled for training at each step
BATCH_SIZE = 10000
#This is the learning rate for the neural network optimizer
LR = 0.0005
#This is used to determine the running epsilon number
InitialEpsilonNum = 100

class Agent:

    def __init__(self):
        #Tracks the number of games played by the Agnet
        self.numberofgames = 0
        #This is a factor controlling exploration. It promotes the snake to explore more in the beginning and then
        #decreases as the agent gets in more games to promote the agent to getting higher and higher scores.
        self.epsilon = 0
        #Gamma places a balance on future rewards and immediate rewards. ie it balances short term and long term rewards
        self.gamma = 0.95
        #memory is a replay buffer that stores states, actions, rewards, next states, and game completion
        self.memory = deque(maxlen=MAX_MEMORY)
        #MODEL is the neural network that has (11 input features, 256 hidden units in single layer, 3 outputs)
        self.model = Linear_QNet(11, 256, 3)
        #TRAINER is an instance of QTrainer for training the model using the replay buffer.
        self.trainer = QTrainer(self.model, lr=LR, gamma = self.gamma)

    def get_state(self, game):

        head = game.snake[0]
        #This creates points for each direction to detect potential collisions. It creates a kind of field around the
        #snakes head
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)
        #This gets the current direction of the snakes movement
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            #Danger straight
            (dir_r and game.is_collision(point_r)) or
            (dir_l and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),

            #Danger to the right
            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)) or
            (dir_l and game.is_collision(point_u)) or
            (dir_r and game.is_collision(point_d)),

            # Danger to the left
            (dir_d and game.is_collision(point_r)) or
            (dir_u and game.is_collision(point_l)) or
            (dir_r and game.is_collision(point_u)) or
            (dir_l and game.is_collision(point_d)),

            #Most direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            #Food Location
            game.food.x < game.head.x,
            game.food.x > game.head.x,
            game.food.y < game.head.y,
            game.food.y > game.head.y
        ]
        #This converts the state list into a numpy array which is useful when it comes to being more memory-efficient
        #as well as conforming to tensor format.
        return np.array(state, dtype = int)

    def remember(self, state, action, reward, next_state, done):
        #This stores a single experience in the memory buffer
        #This is important because it prevents overfitting to recent experiences and helps stabilize the training.
        self.memory.append((state, action, reward, next_state, done)) # popleft if  MAX_MEMORY is reached

    def train_long_memory(self):
        #This samples a batch of experiences for training
        if len(self.memory) > BATCH_SIZE:
        #If the memory BUFFER conains more than the batch_size then we will randomly sample Batch_size experiences from
        #selfmemory using random.sample
            mini_sample = random.sample(self.memory, BATCH_SIZE) #returns a list of tuples
        else:
            #We use all experiences in memory because batchsize has not been reached yet.
            mini_sample = self.memory
        #This unpacks all the samples that are either smaller than or equal to the batchsize amd then it brakes them
        #into seperate lists.
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        #Calling the train_step method of the QTrainer allows for the agent to update the neural network based on the
        #sampled experiences.
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    #this trains the model immediately with the last experience
    #Takes in the current state of the environment, the action taken in the current state, the reward recieved by the
    #action, the resulting state after the action is executed, and then the bool if the game is over or not.
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)


    def get_action(self, state):
        #Sets an epsilon number which was initiated with the value of 0. Higher epsilon equates to higher levels of
        #exploration lower espilon leads to model predictions over exploration.
        self.epsilon = InitialEpsilonNum - self.numberofgames
        #We then initialize final_move
        final_move = [0, 0, 0]
        #This finds a random integer from 0 to 200 to compare to epsilon and if it is smaller than the agent will
        #explore by picking a random move.
        if random.randint(0, 200) < self.epsilon:\
            #Random int from 0 o 2 is chosen and then from there the final move index is set to 1 which indicated the
            #the selected move.
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            #If agent isn't exploring then the state is converted into PyTorch tensor of type float.
            state0 = torch.tensor(state, dtype=torch.float)
            #The neural network model (self.model) preducts the Q-values for each possible move given to the current state
            prediction = self.model(state0)
            #This finds the index of the move with the highest Q-value, and .item() converts it into a Python integer
            move = torch.argmax(prediction).item()
            #Corresponding move is set in final_move.
            final_move[move] = 1
        return final_move

def train():
    #This initializes a list for plot_scores and means
    plot_scores = []
    plot_mean_scores = []
    #accumulates the total score across all games for calculating the mean score.
    total_score = 0
    #Tracks the highest score
    record = 0
    #This calls the Agent object thich handles decision making and training
    agent = Agent()
    #This creates an instance of SnakeGameAI
    game = SnakeGameAI()
    while True:
        #Calls the get_state method of the agent to retrieve the current game state as a feature vector. This is used as
        #input for the agent's decision-making.
        state_old = agent.get_state(game)

        #this variable is the next move by the agent based on state_old.
        final_move = agent.get_action(state_old)

        #This executes the move in the game and then returns the reward, if the game is done, and the score
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        #This performs one-step training using the current experience for immediate learning.
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        #This stores the expeience in the agent's memory buffer for future training.
        agent.remember(state_old, final_move, reward, state_new, done)
        #This handles if the state is done meaning that the snake has collided and the game is over.
        if done:
            #Train the long memory aka experience replay
            game.reset()
            agent.numberofgames += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()
            print('Game', agent.numberofgames, 'Score', score, 'Record', record)
            #Adds the current game's score to the score list
            plot_scores.append(score)
            #Updates the cumulative score for mean calc
            total_score += score
            #Calcs the average score over all games played so far
            mean_score = total_score / agent.numberofgames
            #Stores the mean score for plotting
            plot_mean_scores.append(mean_score)
            #Visualizes the scores and mean scores to track the agent's performance over time.
            plot(plot_scores, plot_mean_scores)
if __name__ == '__main__':
    train()