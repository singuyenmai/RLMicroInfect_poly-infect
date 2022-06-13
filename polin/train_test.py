from polin.bacterial_env import BacterialEnv
from polin.controller import RationalAgent

from typing import List, Dict, Tuple
import numpy as np
import json

import os
import warnings

class TrainTest():
    def __init__(self, env_param_dict: Dict, env_step_time=60.0*6.0, sim_time=60.0*35.0):
        
        # Simulation (integration) parameters
        self.env_step_time = env_step_time # in min (default 6.0h) # time between making drug control decision
        self.simulation_time = sim_time # in min (default 35.0h)

        # Bacterial environments
        self.env = BacterialEnv(env_param_dict, self.env_step_time)

        # Controller agent
        self.agent = None
        
        # Controlling performance
        # self.e_return = 0.0
    
    def test_rational(self, Din = 100.0, drug_time = 60.0*3):
        
        self.agent = RationalAgent(Din = Din, drug_time = drug_time)
        self.env.set_state_method("cont_E")

        self.simulate()
    
    def simulate(self, explore_rate=0.0, training=False) -> None:

        # reset the env to the coexistence equilibrium
        self.env.reset_2_coexist_equilibrium()
        state = self.env.state

        while self.env.tSol[-1] < self.simulation_time:
            
            # if self.agent.type_name == "Qlearning":
            #     action = self.agent.get_action(state, explore_rate)
            if self.agent.type_name == "Rational":
                action = self.agent.get_action(state)
            
            next_state, reward, done = self.env.step(action)

            # if training:
            #     transition = (state, action, reward, next_state, done)
            #     self.agent.update_values(transition)

            state = next_state
            # self.e_return += reward
    
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