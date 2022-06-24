from typing import List, Dict, Tuple
import numpy as np
import math

import os
import tempfile
import atexit
import shutil

mpldir = tempfile.mkdtemp()
atexit.register(shutil.rmtree, mpldir)  # rm directory on succ exit

os.environ['MPLCONFIGDIR'] = mpldir

import matplotlib.pyplot as plt
import seaborn as sns
import polin.colors as colchart

class QLearningAgent():
    '''
    Q-learning agent controlling drug in concentration, with drug in time & frequency are fixed.
    Initialized with:
        n_states (int): the number of environment states observable to the agent
        n_actions (int): the number of actions that the agent can choose from
        Din_options (tuple): tuple of available "flow in" drug concentrations that the agent can choose from.
                                The number of options should be equal to the number of actions.
        drug_time (float): time for "flow in" of drug
        gamma (float): discount rate
        alpha (float): learning rate
    '''
    def __init__(self, n_states: int, n_actions: int, 
                 Din_options: Tuple, drug_time = 60.0*3, 
                 gamma=0.9, alpha=0.01):
        
        self.type_name = 'Qlearning'

        self.n_states = n_states
        self.n_actions = n_actions
        self.values = np.zeros((n_states, n_actions))

        if len(Din_options) != n_actions:
            raise ValueError("The number of Din options should be equal to the number of actions")
        else:
            self.Din_options = Din_options

        self.gamma = gamma
        self.alpha = alpha

        self.drug_time = drug_time

    def update_values(self, transition: Tuple) -> None:
        '''
        Updates the agents value function based on the experience in transition
        Parameters:
            transition (tuple): tuple of (state, action_index, reward, next_state, done)
        '''
        state, action, reward, next_state, done = transition

        self.values[state, action] += self.alpha * (reward + self.gamma * np.max(self.values[next_state] * (1-done)) - self.values[state, action])

    def get_action(self, state: int, explore_rate: float) -> [int, Tuple]:
        '''
        Chooses an action based on the agents value function and the current explore rate
        Parameters:
            state (int): the current state given by the environment, should be an index in the values matrix
            explore_rate (float): the chance of taking a random action
        Returns: 
            action_index (int): index of the action in the values matrix to be chosen by the agent
            action (tuple): the action to be applied to the environment, 
                            in the form of (Din (float): "flow in" drug concentration, 
                                            drug_time (float): time for "flow in" of drug)
        '''
        if np.random.random() < explore_rate:
            action_index = np.random.choice(range(self.n_actions))
        
        else:
            action_index = np.argmax(self.values[state])
        
        action = (self.Din_options[action_index], self.drug_time)

        return action_index, action

    def get_rate(self, episode: int, decay: float, min_r = 0.0, max_r = 1.0) -> float:
        '''
        Calculates the logarithmically decreasing exploring or learning rate
        Parameters:
            episode (int): the current episode
            min_r (float): minimum rate
            max_r (float): maximum rate
            decay (float): controls the rate of decay
        Returns:
            rate (float): exploring or learning rate
        '''

        # input validation
        if not 0 <= min_r <= 1:
            raise ValueError("MIN_LEARNING_RATE needs to be bewteen 0 and 1")

        if not 0 <= max_r <= 1:
            raise ValueError("MAX_LEARNING_RATE needs to be bewteen 0 and 1")

        if not 0 < decay:
            raise ValueError("decay needs to be above 0")
        
        rate = max(min_r, min(max_r, 1.0 - math.log10((episode + 1) / decay)))

        return rate
    
    def set_values(self, qtable: np.ndarray) -> None:
        '''
        Sets the values matrix (Q-table) to a (learned) Q-table
        Parameters:
            qtable (numpy array): the (learned) Q-table to set to
        '''
        self.values = qtable
        self.n_states, self.n_actions = np.shape(qtable)
    
    def visualize_policy(self, OD2state=1.0) -> plt.figure:
        '''
        Visualizes the policy of the agent
        Parameters:
        Returns:
            fig: matplotlib figure object
        '''
        sns.set_style("ticks")
        font = {'family': 'sans-serif', 'serif': 'Helvetica',
                'size': 25}
        plt.rc('font', **font)
        legnd = {'fontsize': 18, 'handlelength': 1.5}
        plt.rc('legend', **legnd)

        pal = colchart.get_colorBook("Egypt")

        fig, ax = plt.subplots(1, 3, figsize=(7.5*2 + 0.2, 3), 
                               gridspec_kw={'wspace': 0.1,
                               'width_ratios': [0.49, 0.49, 0.02]})
        
        # xlims = (0, self.n_states)
        # xts = np.arange(self.n_states+1)
        # ods = np.arange(self.n_states+1) * OD2state
        # ylims = (-0.5, self.n_actions-0.5)
        # yts1 = [i for i in range(self.n_actions)]
        # yts2 = [i+0.5 for i in range(self.n_actions)]
        # X_Pmax = Pmax / OD2state
        # X_Et = (Pmax + 0.025) / OD2state

        # X = [] # state
        # Y1 = [] # action
        # # Y2 = [] # value of best action
        # for state in range(self.n_states):
            
        #     action = np.argmax(self.values[state])
        #     value = np.max(self.values[state])
            
        #     X = X + [state, state+1]
        #     Y1 = Y1 + [action, action]
        #     # Y2 = Y2 + [value, value]
        
        # ax[0].plot(X, Y1, color=pal['M'], lw=3.0)
        # ax[0].set_xlim(xlims[0], xlims[1])
        # ax[0].set_xticks(xts)
        # ax[0].set_xticklabels(np.round(ods, 2), fontsize=14)

        # ax[0].set_ylim(ylims[0], ylims[1])
        # ax[0].set_yticks(yts1)
        # ax[0].set_yticklabels(["Close", "Open"], fontsize=16)
        
        # ax[0].set(xlabel="OD (rounded)", ylabel = "Action")

        # v = ax[1].pcolormesh(self.values.T, cmap="plasma")
        # ax[1].set_xticks(xts)
        # ax[1].set_xticklabels(np.round(ods, 2), fontsize=14)
        # ax[1].set_yticks(yts2)
        # ax[1].set_yticklabels(["", ""])
        # ax[1].set(xlabel="OD (rounded)")
        
        # c = plt.colorbar(v, cax=ax[2], label="Value")
        # ax[2].locator_params(tight=True, nbins=4)
        # ax[2].tick_params(labelsize=14)

        # # Plot Pmax
        # ax[0].axvline(x=X_Pmax, color='black', lw=1.5, ls=(0, (3, 7, 1, 7)))
        # ax[1].axvline(x=X_Pmax, color='black', lw=1.5, ls=(0, (3, 7, 1, 7)))

        # # Plot escape threshold
        # ax[0].axvline(x=X_Et, color='black', lw=1.5, ls='dashed')
        # ax[1].axvline(x=X_Et, color='black', lw=1.5, ls='dashed')

        return fig

class RationalAgent():
    '''
    Rational drug policy: Drug in at a constant concentration & frequency, whenever the targeted density (state) > 0.0
    Initialized with:
        Din (float): "flow in" drug concentration
        drug_time (float): time for "flow in" of drug
    '''
    def __init__(self, Din = 100.0, drug_time = 60.0*3):

        self.type_name = "Rational"
        self.Din = Din
        self.drug_time = drug_time
    
    def get_action(self, state: float) -> Tuple:
        '''
        Returns action based on observed state
        Parameters:
            state (float): the most recent (continuous) density of the targeted species 
        Returns:
            action (tuple): action chosen by the controller, 
                            in the form of (Din (float): "flow in" drug concentration, drug_time (float): time for "flow in" of drug)
        '''
        if state > 0.0:
            action = (self.Din, self.drug_time)
        else:
            action = (0.0, self.drug_time)

        return action