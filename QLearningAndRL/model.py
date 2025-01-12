import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    #Initialize the network structure
    def __init__(self, input_size, hidden_size, output_size, dropout_rate=0.2):
        #Constructs the parent class
        super().__init__()
        #Defines the first layer which is a fully connected layer mapping
        self.linear1 = nn.Linear(input_size, hidden_size)
        #Defines the second layer


        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        #Passes the input x through the first layer and applies the ReLU activation function
        x = F.relu(self.linear1(x))
        #Passes the result through the second layer to produce the output


        x = self.linear2(x)
        #Outputs the final Q-values for each position action
        return x

    def save(self, file_name='model.pth'):
        #Defines the directory where the model file will be stored
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        #Saves models parameters to the specified file.
        torch.save(self.state_dict(), file_name)

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr = self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(np.array(state), dtype=torch.float)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float)
        action = torch.tensor(np.array(action), dtype=torch.long)
        reward = torch.tensor(np.array(reward), dtype=torch.float)
        #Checks that the input is a single experience and not a batch
        if len(state.shape) == 1:
            #Adds batch dimension to ensure compatibility witht he model
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )
        #Predicts the Q-values for the current state
        pred = self.model(state)
        #Creates a copy of pred to be modified as the training target
        target = pred.clone()
        #Iterates through all experiences in the batch
        for idx in range(len(done)):

            Q_new = reward[idx]
            #Updates Q-value using the Bellman equation if the episode is not over
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
            #Updates the Q-value for the specific action taken
            target[idx][torch.argmax(action).item()] = Q_new
        #Clears previous gradients to prevent accumulation
        self.optimizer.zero_grad()
        #Computes the loss between predicted and target Q-values
        loss = self.criterion(target, pred)
        #Calculates gradiets for each model parameter
        loss.backward()

        self.optimizer.step()

