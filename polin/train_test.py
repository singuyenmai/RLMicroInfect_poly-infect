from polin.bacterial_env import BacterialEnv
from polin.controller import RationalAgent, QLearningAgent

from typing import List, Dict, Tuple
import numpy as np
import json

import os

class TrainTest():
    def __init__(self, env_param_dict: Dict, sim_param_dict: Dict, test_done_break: False):

        # Set simulation parameters from `sim_param_dict``
        self.set_params(sim_param_dict)
        self.test_done_break = test_done_break

        # Bacterial environment
        self.env = BacterialEnv(env_param_dict, step_time = self.env_step_time,
                                reward_func = self.reward_func, reward_kwargs = self.reward_kwargs)

        # Controller agent
        self.agent = None
        
        # Cummulative return the controller receive
        self.e_return = 0.0
    
    def set_params(self, param_dict: Dict) -> None:
        '''
        Sets simulation parameters to those stored in a python dictionary
        Parameters:
            param_dict : pyhon dictionary containing all params
        '''
        self.simulation_time = param_dict['simulation_time'] # in min (default 6.0h) # time between making drug control decision
        self.env_step_time = param_dict['env_step_time'] # in min
        self.reset_type = param_dict['reset_type'] # which equilibria to reset the system to
        
        self.reward_func = param_dict['reward_func'] # name of the reward function
        self.reward_kwargs = param_dict['reward_kwargs'] # kwargs for the reward function

    def test_rational(self, Din = 100.0, drug_time = 60.0*3) -> None:
        
        self.agent = RationalAgent(Din = Din, drug_time = drug_time)
        self.env.reset_state_method(state_method = 'cont_E', n_states = None)

        self.simulate(sim_time=self.simulation_time, done_break = self.test_done_break)
    
    def set_QLearning_agent(self, param_dict: Dict) -> None:
        n_states = param_dict['n_states']
        n_actions = param_dict['n_actions']
        
        Din_options = tuple(param_dict['Din_options'])
        drug_time = param_dict['drug_time']
        
        gamma = param_dict['gamma']
        alpha = param_dict['alpha']
        
        self.agent = QLearningAgent(n_states, n_actions, 
                                    Din_options, drug_time, 
                                    gamma, alpha)
    
    def is_agent_QLearning(self) -> None:
        
        if self.agent is None:
            raise RuntimeError('Agent is not set. Please run method: set_QLearning_agent.')
        elif self.agent.type_name != 'QLearning':
            raise RuntimeError('Agent is not QLearning. Please run method: set_QLearning_agent.')
        
        return True
    
    def train_Qlearing(self, n_episodes: int, decay: float, 
                       episode_time_max: float, exp_dir: str) -> None:

        self.is_agent_QLearning()

        perf_filename = exp_dir + 'training_performance.tsv'

        if not os.path.exists(exp_dir):
            os.mkdir(exp_dir)
        
        qtable_dir = exp_dir + 'learned_qtables/'
        if not os.path.exists(qtable_dir):
            os.mkdir(qtable_dir)

        qtable_filename = qtable_dir + 'QLearningAgent_values.ep'

        with open(perf_filename, 'w') as pf:
            pf.write(f'episode\texplore_rate\te_return\tt5p_first\ttTiny_first\ttotal_drug_in')

        self.env.reset_state_method(state_method = 'disc_EZ', n_states = self.agent.n_states)

        print(f"Training for {n_episodes} episodes ...\n")

        for episode in range(n_episodes):

            explore_rate = self.agent.get_rate(episode, decay)

            self.simulate(sim_time = episode_time_max, done_break = True, 
                          explore_rate = explore_rate, training = True)
            
            with open(qtable_filename + str(episode) + '.npy', 'wb') as f:
                np.save(f, self.agent.values)
            
            t5p_first = self.env.t5p[0] if len(self.env.t5p) > 0 else "N/A"
            tTiny_first = self.env.tTiny[0] if len(self.env.tTiny) > 0 else "N/A"
            with open(perf_filename, 'a') as pf:
                pf.write(f'\n{episode}\t{explore_rate}\t{self.e_return}\t{t5p_first}\t{tTiny_first}\t{self.env.total_drug_in}')
            
            if episode % 10 == 0:
                print(f'episode: {episode} \t| explore_rate: {round(explore_rate, 3)} \t| return: {round(self.e_return, 3)}')
    
    def test_QLearning(self, learned_qtable_file=None, explore_rate=0.0) -> None:
        
        self.is_agent_QLearning()
        
        if learned_qtable_file is not None:
            
            learned_qtable = np.load(learned_qtable_file)
            self.agent.set_values(learned_qtable)

        print(f'\nTesting on agent with Q-table:\n{self.agent.values}\n')
        
        self.env.reset_state_method(state_method = 'disc_EZ', n_states = self.agent.n_states)

        self.simulate(sim_time = self.simulation_time, done_break = self.test_done_break, 
                      explore_rate = explore_rate, training = False)
        
        print("Learned Q-learning policy tested\n")
        
        print(f'e_return\tt5p_first\ttTiny_first\ttotal_drug_in')

        t5p_first = self.env.t5p[0] if len(self.env.t5p) > 0 else "N/A"
        tTiny_first = self.env.tTiny[0] if len(self.env.tTiny) > 0 else "N/A"

        print(f'\n{self.e_return}\t{t5p_first}\t{tTiny_first}\t{self.env.total_drug_in}')

    def simulate(self, sim_time: float, done_break: bool, 
                 explore_rate=0.0, training=False) -> None:

        # reset the env
        self.env.reset_2_equilibria(eq_type=self.reset_type)
        state = self.env.state
        
        # reset the cumulative return
        self.e_return = 0.0

        while self.env.tSol[-1] < sim_time:
            
            if self.agent.type_name == "QLearning":
                action_index, action = self.agent.get_action(state, explore_rate)
            
            if self.agent.type_name == "Rational":
                action = self.agent.get_action(state)
            
            next_state, reward, done = self.env.step(action)

            if training:
                transition = (state, action_index, reward, next_state, done)
                self.agent.update_values(transition)

            state = next_state
            self.e_return += reward

            if done & done_break:
                break
    
    def export_env_data(self, output_filename):
        output_file = output_filename + ".tsv"
        header = "t\tE\tZ\tM\tD"

        n = len(self.env.tSol)
        output = np.reshape(self.env.tSol, [n, 1])

        EnZ = self.env.sSol[:, :2]
        output = np.append(output, EnZ, axis=1)

        M = np.reshape(self.env.sSol[:, 0] + self.env.sSol[:, 1], [n, 1])
        output = np.append(output, M, axis=1)

        D = np.reshape(self.env.sSol[:, -1], [n, 1])
        output = np.append(output, D, axis=1)

        np.savetxt(output_file, output, 
                   delimiter="\t", fmt='%.5f',
                   header=header, comments='')