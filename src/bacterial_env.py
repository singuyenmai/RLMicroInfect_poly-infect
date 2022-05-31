from typing import List, Dict, Tuple
import json

import numpy as np
from scipy.integrate import solve_ivp
import random
import warnings

class BacterialEnv():

    '''
    Microbial growth environment that are under drug treatment control policy
    '''

    def __init__(self, param_file: str, sampling_time: float) -> None:
        
        with open(param_file) as f:
            param_dict = json.load(f)
        
        self.set_params(param_dict)
        self.initial_S = np.array([self.init_E, self.init_Z, self.init_D])
        
        self.sSol = np.array(self.initial_S).reshape(1, len(self.initial_S))
        self.tSol = np.array([0.0])

        if self.init_Z == 0.0:
            self.mono = True # if it's a mono-culture env, this is just for visualization
        else:
            self.mono = False # if it's a co-culture env
        
        # self.total_prescription = 0
        
        self.sampling_time = sampling_time
        
        # self.get_reward = reward_func # function for the reward
        # self.reward_kwargs = reward_kwargs # kwargs for reward func

        # self.state_method = state_method # method to derive observable state for the controller
        # self.n_states = n_states
        # self.OD2state = None
        # self.state = self.get_state(self.state_method) # observable state to the controller

    def set_params(self, param_dict: Dict) -> None:
        '''
        Sets environment parameters to those stored in a python dictionary
            Parameters:
                param_dict : pyhon dictionary containing all params
        '''
        # ODE model param
        self.rE = param_dict['ode_params']['rE']; self.rZ = param_dict['ode_params']['rZ'] 
        self.cE = param_dict['ode_params']['cE']; self.cZ = param_dict['ode_params']['cZ']
        self.alpha_EZ = param_dict['ode_params']['alpha_EZ']
        self.alpha_ZE = param_dict['ode_params']['alpha_ZE']

        self.kd = param_dict['ode_params']['kd']
        self.ki = param_dict['ode_params']['ki']

        self.micE = param_dict['ode_params']['micE']
        self.micZ = param_dict['ode_params']['micZ']
        self.dmaxE = param_dict['ode_params']['dmaxE']
        self.dmaxZ = param_dict['ode_params']['dmaxZ']
        self.gamma = param_dict['ode_params']['gamma']
        
        # initial conditions
        self.init_E = param_dict['initial_conditions']['E']
        self.init_Z = param_dict['initial_conditions']['Z']
        self.init_D = param_dict['initial_conditions']['D']
    
    def set_state_method(self, state_method: str) -> None:
        self.state_method = state_method
    
    def set_n_states(self, n_states: int) -> None:
        self.n_states = n_states
    
    def ODEsys(self, t, S, Din: float) -> List:
        '''
        Returns derivatives for the numerical solver odeint
        Parameters:
            S: current environment state
            t: current time
            Din: drug concentration that goes in at some constant rate `ki`
        Returns:
            rhs: array of the right-hand sides of the differential equations for all environment state variables
        '''

        # extract variables
        E, Z, D = S

        # drug response - killing rate functions
        deltaE = self.dmaxE * (D**self.gamma) / (self.micE**self.gamma + D**self.gamma) # of focal species E
        deltaZ = self.dmaxZ * (D**self.gamma) / (self.micZ**self.gamma + D**self.gamma) # of neighbor species Z

        # derivatives
        dE_dt = E * (self.rE - self.rE/self.cE * E + self.alpha_EZ * Z - deltaE) # focal species E
        dZ_dt = Z * (self.rZ - self.rZ/self.cZ * Z + self.alpha_ZE * E - deltaZ) # neighbor species Z
        
        dD_dt = self.ki * Din - self.kd * D # drug concentration
        
        rhs = [dE_dt, dZ_dt, dD_dt]

        return rhs

    def step(self, action: Tuple) -> None:
        '''
        Solve the ODEs system for a time period defined by `sampling_time` param, under the action provided by a controller
        Parameters:
            action (tuple): action chosen by the controller, in the form of (drug in or not - 1 or 0, time `Din` > 0.0)
        Returns:
            state (int): (discretized) OD to be observed by the controller
            reward (float): reward calculated accordingly to the `reward_func`
            done (boolean): whether a terminal state has been observed
            info (dict): other interesting information of the system
        '''
        Din, drug_time = self.action_2_drug(action)

        t_start = self.tSol[-1]
        t_end = t_start + drug_time
        init = self.sSol[-1, :]

        sol = solve_ivp(self.ODEsys, [t_start, t_end], init, args=(Din,), method="LSODA")

        self.sSol = np.append(self.sSol, sol.y.T[1:, :], axis=0)
        self.tSol = np.append(self.tSol, sol.t[1:])

        if (self.sampling_time - drug_time) > 0.0:
            t_start = self.tSol[-1]
            t_end = t_start + (self.sampling_time - drug_time)
            init = self.sSol[-1, :]

            sol = solve_ivp(self.ODEsys, [t_start, t_end], init, args=(0.0,), method="LSODA")

            solEZ = sol.y[:2, :]
            roundedZero_solEZ = np.where(np.round(solEZ, 5) == 0, 0.0, solEZ)
            soly = np.append(roundedZero_solEZ, sol.y[[-1], :], axis=0)

            self.sSol = np.append(self.sSol, soly.T[1:, :], axis=0)
            self.tSol = np.append(self.tSol, sol.t[1:])
                
        # self.state = self.get_state(self.state_method)

        # reward, done, t_failure = self.get_reward(action, self.sSol, self.tSol, 
        #                                           self.N_steps, self.Pmax, self.Pmax_err, 
        #                                           **self.reward_kwargs)
        # info = {
        #     "integrate successful": r.successful(), 
        #     "escape time": t_failure,
        #     "total drug prescribed": self.total_prescription
        # }

        # return self.state, reward, done, info
    
    def action_2_drug(self, action: Tuple) -> Tuple:
        '''
        Convert action into `Din` concentration & drug time
        Parameters:
            action (tuple): action chosen by the controller, in the form of (drug in or not - 1 or 0, time `Din` > 0.0)
        Returns: (wrapped in a tuple)
            Din (float): "flow in" drug concentration
            drug_time (float): the time period for when `Din` in the ODEs system equals the converted Din value here
        '''
        a1, a2 = action
        
        if a2 > self.sampling_time:
            raise ValueError("Time duration for drug in cannot be longer than sampling time")
        
        Din = 100.0 if a1 == 1 else 0.0
        drug_time = a2

        return (Din, drug_time)