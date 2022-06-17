from typing import List, Dict, Tuple

import numpy as np
from scipy.integrate import solve_ivp
import warnings

class BacterialEnv():

    '''
    Microbial growth environment that are under drug treatment control policy
    '''

    def __init__(self, param_dict: Dict, sampling_time: float, state_method="cont_E") -> None:
        
        self.set_params(param_dict)
        self.initial_S = np.array([self.init_E, self.init_Z, self.init_D]) # init conditions of S = [E, Z, D]
        
        self.sSol = np.array(self.initial_S).reshape(1, len(self.initial_S)) # solution of S
        self.tSol = np.array([0.0]) # solution of time t

        self.actions = np.empty((0, 2), float) # matrix of actions with corresponding timepoints

        if self.init_Z == 0.0:
            self.mono = True # if it's a mono-culture env, this is just for visualization
        else:
            self.mono = False # if it's a co-culture env
        
        self.five_percent = 0.05 * self.init_E # 5% of init density E
        self.t5p = np.array([]) # timepoints t at which density E = 5% of its initial condition
        self.tTiny = np.array([]) # timepoints t at which density E = tiny number
        
        self.sampling_time = sampling_time
        
        # self.get_reward = reward_func # function for the reward
        # self.reward_kwargs = reward_kwargs # kwargs for reward func

        self.state_method = state_method # method to derive observable state for the controller
        # self.n_states = n_states
        # self.OD2state = None
        self.state = self.get_state(self.state_method) # observable state to the controller

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
    
    # def set_n_states(self, n_states: int) -> None:
        # self.n_states = n_states
    
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
    
    def event5p(self, t, S, Din: float) -> float:
        '''
        Event for ODE solver: time at which E density == 5% of its initial condition
        '''
        return S[0] - self.five_percent
    
    def eventTiny(self, t, S, Din: float) -> float:
        '''
        Event for ODE solver: time at which E density == tiny 10**(-4)
        '''
        return S[0] - 10**(-4)

    def step(self, action: Tuple) -> None:
        '''
        Solves the ODEs system for a time period defined by `sampling_time` param, under the action provided by a controller
        Parameters:
            action (tuple): action chosen by the controller, 
                            in the form of (Din (float): "flow in" drug concentration, drug_time (float): time for "flow in" of drug)
        Returns:
            state (int): the system/env state to be observed by the controller
            reward (float): reward calculated accordingly to the `reward_func`
            done (boolean): whether a terminal state has been observed
            info (dict): other interesting information of the system
        '''
        Din, drug_time = action
        if drug_time > self.sampling_time:
            raise ValueError("Time duration for drug in cannot be longer than sampling time")
        
        self.actions = np.append(self.actions, np.array([[self.tSol[-1], Din]]), axis=0)

        t_start = self.tSol[-1]
        t_end = t_start + drug_time
        init = self.sSol[-1, :]

        sol = solve_ivp(self.ODEsys, [t_start, t_end], init, args=(Din,), 
                        events = [self.event5p, self.eventTiny], max_step=0.01,
                        method = "LSODA")

        self.sSol = np.append(self.sSol, sol.y.T[1:, :], axis=0)
        self.tSol = np.append(self.tSol, sol.t[1:])
        self.t5p = np.append(self.t5p, sol.t_events[0])
        self.tTiny = np.append(self.tTiny, sol.t_events[1])

        if (self.sampling_time - drug_time) > 0.0:
            t_start = self.tSol[-1]
            t_end = t_start + (self.sampling_time - drug_time)
            init = self.sSol[-1, :]

            sol = solve_ivp(self.ODEsys, [t_start, t_end], init, args=(0.0,), 
                            events = [self.event5p, self.eventTiny], max_step=0.01,
                            method = "LSODA")

            solEZ = sol.y[:2, :]
            roundedZero_solEZ = np.where(np.round(solEZ, 5) == 0, 0.0, solEZ)
            soly = np.append(roundedZero_solEZ, sol.y[[-1], :], axis=0)

            self.sSol = np.append(self.sSol, soly.T[1:, :], axis=0)
            self.tSol = np.append(self.tSol, sol.t[1:])
            self.t5p = np.append(self.t5p, sol.t_events[0])
            self.tTiny = np.append(self.tTiny, sol.t_events[1])
                
        self.state = self.get_state(self.state_method)

        reward, done = None, None

        return self.state, reward, done
    
    def get_state(self, method: str):
        '''
        Returns the "current" state of the system/env for the controller to make decisions.
        Parameters:
            method (str): name of the method to compute the state of the system
        Returns: the type of the return depends on the method of deriving the state 
        '''
        if method == "cont_E": # returns the most recent density of species E (continuous value)
            return self.sSol[-1, 0]
        else:
            raise ValueError("Method to derive observable state is not yet defined")
    
    def coexist_equilibrium(self) -> Tuple:
        '''
        Computes the equilibrium of coexistence
        Returns: (wrapped in a tuple)
            E: density of species E at the equilibrium (should be > 0.0)
            Z: density of species Z at the equilibrium (should be > 0.0)
        '''
        E = (self.cE * self.rE * self.rZ + self.cE * self.cZ * self.rZ * self.alpha_EZ) / (self.rE * self.rZ - self.cE * self.cZ * self.alpha_EZ * self.alpha_ZE)
        Z = (self.cZ * self.rE * self.rZ + self.cE * self.cZ * self.rE * self.alpha_ZE) / (self.rE * self.rZ - self.cE * self.cZ * self.alpha_EZ * self.alpha_ZE)

        if (E <= 0.0) or (Z <= 0.0):
            raise RuntimeError("Coexist equilibrium does not exist.")
        
        return (E, Z)
    
    def reset_2_equilibria(self, eq_type="coexist") -> None:
        '''
        Resets the system. The initial densities of E & Z are set to either:
        - the equilibrium of co-existence in co-culture, if parameter `eq_type` is "coexist"; or
        - the equilibria in their mono-culture, equivalent to co-culture with no interaction, if parameter `eq_type` is "mono"
        (both of these are in environment without drug)
        '''
        if eq_type == "coexist":
            eqE, eqZ = self.coexist_equilibrium() # equilibrium of co-existence in co-culture
        elif eq_type == "mono":
            eqE, eqZ = self.cE, self.cZ # equilibria in mono-culture = carrying capacity
        else:
            raise ValueError("Parameter `eq_type` can only be either \"coexist\" or \"mono\".")

        self.initial_S = np.array([eqE, eqZ, self.init_D])
        
        self.sSol = np.array(self.initial_S).reshape(1, len(self.initial_S))
        self.tSol = np.array([0.0])

        self.actions = np.empty((0, 2), float)

        self.mono = False # system starts at coexistence equilibrium / carrying capacities, so it's co-culture env
        
        self.five_percent = 0.05 * eqE

        self.t5p = np.array([])
        self.tTiny = np.array([]) 
