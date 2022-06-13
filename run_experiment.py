from polin.train_test import TrainTest
import polin.viz as viz

from typing import List, Dict, Tuple
import numpy as np

import json
import os
import argparse

defined_controllers = ["Rational", "Qlearning"]

class Experiment():
    def __init__(self, exp_param_file: str) -> None:
        
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

        sim_dict = param_dict['simulation']

        self.simulation_time = sim_dict['simulation_time']
        self.env_step_time = sim_dict['env_step_time']
        
        # self.reward_func = sim_dict['reward_func']
        # self.reward_params_dict = sim_dict['reward_params_dict']

        controller_dict = param_dict['controller']
        self.type_name = controller_dict['type_name']

        global defined_controllers
        if self.type_name not in defined_controllers:
            raise ValueError('Controller type name should only be either \"Rational\" or \"Qlearning\"')

        if self.type_name == 'Qlearning':

            self.growth_bound = controller_dict['growth_bound']
            
            self.n_states = controller_dict['agent']['n_states']
            self.n_actions = controller_dict['agent']['n_actions']
            self.gamma = controller_dict['agent']['gamma']
            self.alpha = controller_dict['agent']['alpha']

            self.n_episodes = controller_dict['training']['n_episodes']
            self.decay = controller_dict['training']['decay']
        
        elif self.type_name == 'Rational':
            self.Din = controller_dict['Din']
            self.drug_time = controller_dict['drug_time']
        
        self.pwd = os.getcwd() + '/'
        self.exp_dir = self.pwd + self.exp_ID + '/'
        if not os.path.exists(self.exp_dir):
            os.mkdir(self.exp_dir)
    
    def run(self, test_only=False, 
            test_qtable_episode='last', test_explore_rate=0.0, 
            test_savefig_format = 'png') -> None:
        if test_qtable_episode != 'last' and test_qtable_episode > (self.n_episodes - 1):
                raise ValueError("test_qtable_episode should not >= number of episodes")
        
        tt = TrainTest(self.env_param_dict, 
                    #    self.reward_func, self.reward_params_dict,
                       env_step_time=self.env_step_time, sim_time=self.simulation_time)
        
        if self.type_name == 'Rational':
            
            tt.test_rational(Din=self.Din, drug_time=self.drug_time)
        
        # else:

        #     tt.set_Qlearning_agent(self.n_states, self.n_actions, self.gamma, self.alpha)

        #     train_fig = tt.train_Qlearing(self.n_episodes, self.decay, self.exp_dir, viz_only=test_only)
        #     train_fig.savefig(self.exp_dir + "training_performance.png", bbox_inches='tight')
            
        #     ep = self.n_episodes - 1 if test_qtable_episode == 'last' else test_qtable_episode

        #     learned_qtable_file = self.exp_dir + 'learned_qtables/QLearningAgent_values.ep' + str(ep) + '.npy'
        #     tt.test_Qlearning(learned_qtable_file=learned_qtable_file, 
        #                       explore_rate=test_explore_rate, 
        #                       done_break=test_done_break)
            
        #     # Plot policy of the Q-learning agent
        #     fig_Qpolicy = tt.visualize_Qpolicy()
        #     fig_Qpolicy_name = self.exp_dir + "Qpolicy." + self.exp_ID + "." + test_savefig_format
        #     fig_Qpolicy.savefig(fig_Qpolicy_name, bbox_inches='tight')
        
        # Plot testing results
        fig_test = viz.visualize_simulation(env = tt.env, st='full', tscale=60.0, title='none')      
        
        fig_test_name = self.exp_dir + "testing." + self.exp_ID + "." + test_savefig_format
        fig_test.savefig(fig_test_name, bbox_inches='tight')

        # Write testing performance to file
        test_pfname = self.exp_dir + "testing_perf." + self.exp_ID + ".tsv"
        with open(test_pfname, 'w') as pf:
            # pf.write(f'exp_ID\te_return\tescape_time\ttotal_drug_prescribed\tdone_count')
            # pf.write(f'\n{self.exp_ID}\t{tt.e_return}\t{tt.escape_time}\t{tt.total_prescription}\t{tt.done_count}')
            pf.write(f'exp_ID\tt5p')
            pf.write(f'\n{self.exp_ID}\t{tt.env.t5p}')
        
        # Write simulation data to file
        tt.export_env_data(output_filename = self.exp_dir + "testing." + self.exp_ID)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Running experiment supplied with a json parameter file")
    
    parser.add_argument("-f", "--exp_param_file", type=str, required=True)
    parser.add_argument("-to", "--test_only", type=bool, 
                        default=False, required=False)
    parser.add_argument("-tqe", "--test_qtable_episode", 
                        default='last', required=False)
    parser.add_argument("-ter", "--test_explore_rate", type=float, 
                        default=0.0, required=False)
    # parser.add_argument("-tdb", "--test_done_break", type=bool, 
    #                     default=False, required=False)
    parser.add_argument("-tsf", "--test_savefig_format", type=str, 
                        default='png', required=False)

    args = parser.parse_args()

    print("Parsing experiment parameters ...\n")
    exp = Experiment(exp_param_file = args.exp_param_file)
    
    print("Parsing successful. Running experiment ...")
    exp.run(test_only = args.test_only, 
            test_qtable_episode = args.test_qtable_episode,
            test_explore_rate = args.test_explore_rate,
            # test_done_break = args.test_done_break,
            test_savefig_format = args.test_savefig_format)