from polin.train_test import TrainTest
import polin.viz as viz

from typing import List, Dict, Tuple
import numpy as np

import json
import os
import argparse

class Experiment():
    def __init__(self, exp_param_file: str) -> None:
        
        self.defined_controllers = ["Rational", "QLearning"]

        with open(exp_param_file) as f:
            param_dict = json.load(f)
        
        self.set_params(param_dict)

    def set_params(self, param_dict: Dict) -> None:
        '''
        Set all the parameters involved in an experiment, which are stored in a python dictionary
        '''
        self.exp_ID = param_dict['exp_ID']
        self.exp_name = param_dict['exp_name']

        self.env_param_dict = param_dict['env']

        self.sim_param_dict = param_dict['simulation']

        controller_dict = param_dict['controller']
        self.controller_type = controller_dict['type_name']

        if self.controller_type not in self.defined_controllers:
            raise ValueError(f'Controller type name should be in this list: {self.defined_controllers}')

        if self.controller_type == 'QLearning':
            
            self.QLearningAgent_param_dict = controller_dict['agent']

            self.n_episodes = controller_dict['training']['n_episodes']
            self.decay = controller_dict['training']['decay']
            self.episode_time_max = controller_dict['training']['episode_time_max']
        
        elif self.controller_type == 'Rational':
            self.Din = controller_dict['Din']
            self.drug_time = controller_dict['drug_time']
        
        self.pwd = os.getcwd() + '/'
        self.exp_dir = self.pwd + self.exp_ID + '/'
        if not os.path.exists(self.exp_dir):
            os.mkdir(self.exp_dir)
    
    def run(self, test_only=False, test_done_break=False, 
            test_qtable_episode='last', test_explore_rate=0.0, 
            test_savefig_format = 'png') -> None:
        '''
        Runs the experiment
        '''
        if test_qtable_episode != 'last' and test_qtable_episode > (self.n_episodes - 1):
                raise ValueError("test_qtable_episode should not >= number of episodes")
        
        tt = TrainTest(self.env_param_dict, self.sim_param_dict, test_done_break = test_done_break)
        
        if self.controller_type == 'Rational':
            
            tt.test_rational(Din=self.Din, drug_time=self.drug_time)
        
        else:

            tt.set_QLearning_agent(self.QLearningAgent_param_dict)

            perf_filename = self.exp_dir + 'training_performance.tsv'

            if not test_only:
                tt.train_Qlearing(self.n_episodes, self.decay, self.episode_time_max, self.exp_dir)
            
            elif not os.path.exists(perf_filename):
                raise RuntimeError('Training performance file does not exist. Please run training.')
            
            train_fig = viz.visualize_train(train_perf_file = perf_filename)            
            train_fig.savefig(self.exp_dir + "training_performance.png", bbox_inches='tight')
            
            ep = self.n_episodes - 1 if test_qtable_episode == 'last' else test_qtable_episode

            learned_qtable_file = self.exp_dir + 'learned_qtables/QLearningAgent_values.ep' + str(ep) + '.npy'
            tt.test_QLearning(learned_qtable_file = learned_qtable_file, 
                              explore_rate = test_explore_rate)
            
            # Plot policy of the Q-learning agent
            fig_Qpolicy = tt.agent.visualize_policy(OD2state = tt.env.OD2state)
            
            fig_Qpolicy_name = self.exp_dir + "Qpolicy." + self.exp_ID + "." + test_savefig_format
            fig_Qpolicy.savefig(fig_Qpolicy_name, bbox_inches='tight')
        
        # Plot testing results
        fig_test = viz.visualize_simulation(env = tt.env, st='full', tscale=60.0, title='none')      
        
        fig_test_name = self.exp_dir + "testing." + self.exp_ID + "." + test_savefig_format
        fig_test.savefig(fig_test_name, bbox_inches='tight')

        # Write testing performance to file
        test_pfname = self.exp_dir + "testing_perf." + self.exp_ID + ".tsv"
        with open(test_pfname, 'w') as pf:
            pf.write(f'exp_ID\te_return\tt5p\ttTiny\ttotal_drug_in')
            pf.write(f'\n{self.exp_ID}\t{tt.e_return}\t{tt.env.t5p}\t{tt.env.tTiny}\t{tt.env.total_drug_in}')
        
        # Write simulation data to file
        tt.export_env_data(output_filename = self.exp_dir + "testing." + self.exp_ID)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Running experiment supplied with a json parameter file")
    
    parser.add_argument("-f", "--exp_param_file", type=str, required=True)
    parser.add_argument("-to", "--test_only", type=bool, 
                        default=False, required=False)
    parser.add_argument("-tdb", "--test_done_break", type=bool, 
                        default=False, required=False)
    parser.add_argument("-tqe", "--test_qtable_episode", 
                        default='last', required=False)
    parser.add_argument("-ter", "--test_explore_rate", type=float, 
                        default=0.0, required=False)
    parser.add_argument("-tsf", "--test_savefig_format", type=str, 
                        default='png', required=False)

    args = parser.parse_args()

    print("Parsing experiment parameters ...\n")
    exp = Experiment(exp_param_file = args.exp_param_file)
    
    print("Parsing successful. Running experiment ...\n")
    exp.run(test_only = args.test_only, 
            test_done_break = args.test_done_break,
            test_qtable_episode = args.test_qtable_episode,
            test_explore_rate = args.test_explore_rate,
            test_savefig_format = args.test_savefig_format)
    
    print("Done")