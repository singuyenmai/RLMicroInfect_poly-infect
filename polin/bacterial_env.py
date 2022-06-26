import polin.reward_func as rf

from typing import List, Dict, Tuple

import numpy as np
from scipy.integrate import solve_ivp
import math

class BacterialEnv():
    '''
    Microbial growth environment that are under drug treatment control policy
    Initialized with:
        param_dict (dictionary): parameters for the ODE model & initial conditions
        step_time (float): time for integration whenever the `step` method is called
        reward_func (str): name of the reward function
        reward_kwargs (dict): parameters for reward caculations
        state_method (str): name of the method to return state
        n_states (int or None): number of discrete states, should be 
                                int when `state_method` is "disc_EZ",
                                None when `state_method` is "cont_E"
    '''
    def __init__(self, param_dict: Dict, step_time: 60.0*6.0, 
                 reward_func: "minED", reward_kwargs: {}, 
                 state_method="cont_E", n_states=None):
        
        self.set_params(param_dict) # set params from the param_dict
        
        self.initial_S = np.array([self.init_E, self.init_Z, self.init_D]) # init conditions of S = [E, Z, D]
        self.sSol = np.array(self.initial_S).reshape(1, len(self.initial_S)) # solution of S
        self.tSol = np.array([0.0]) # solution of time t

        self.actions = np.empty((0, 2), float) # matrix of actions with corresponding timepoints
        self.total_drug_in = 0.0 # cumulative drug concentration "flowed" in

        if self.init_Z == 0.0:
            self.mono = True # if it's a mono-culture env, this is just for visualization
        else:
            self.mono = False # if it's a co-culture env
        
        self.five_percent = 0.05 * self.init_E # 5% of init density E
        self.t5p = np.array([]) # timepoints t at which density E = 5% of its initial condition
        self.tTiny = np.array([]) # timepoints t at which density E = tiny number
        
        self.step_time = step_time # total integration time for each time `step` method is called
        
        self.set_reward_func(reward_func) # set the function that returns reward
        self.reward_kwargs = reward_kwargs # kwargs for the reward function

        # method to derive observable state for the controller
        self.defined_state_methods = ["cont_E", "disc_EZ", "disc_E"]
        
        if state_method not in self.defined_state_methods:
            raise ValueError(f"Method to derive observable state is not in the list of defined methods: {self.defined_state_methods}")
        else:
            self.state_method = state_method 
        
        # the 3 below are only applicable to Q-learning controllers
        self.n_states = n_states # total number of states
        self.growth_bounds = [0.0, 0.5] # bounds of bacterial growth density
        self.OD2state = None # distance (in density unit) between 2 consecutive states, 
                             # also the "exchange rate" to convert from density to discrete state

        self.state = self.get_state() # observable state to the controller

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
    
    def set_reward_func(self, func_name: str) -> None:
        '''
        Sets the reward function given the function name
        Parameters;
            func_name (str): name of the reward function to be used
        '''
        if func_name == 'minED':
            self.get_reward = rf.minED
        else:
            raise ValueError('Supplied reward function name is not (yet) defined')

    def reset_state_method(self, state_method: str, n_states: int) -> None:
        '''
        Resets the method to return state given the method name
        Parameters:
            state_method (str): name of the state method to be used
            n_states (int or None): number of states to set to, int when `state_method` is "disc_EZ", None when "cont_E"
        '''
        if state_method not in self.defined_state_methods:
            raise ValueError("Method to derive observable state is not yet defined")
        else:
            self.state_method = state_method
        
        self.n_states = n_states
        # update the env state accordingly to the new method
        self.state = self.get_state()
    
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
        Solves the ODEs system for a time period defined by `step_time` param, under the action taken by a controller
        Parameters:
            action (tuple): action chosen by the controller, 
                            in the form of (Din (float): "flow in" drug concentration, drug_time (float): time for "flow in" of drug)
        Returns:
            state (int or float): the system/env state to be observed by the controller,
                                  int when `state_method` is "disc_EZ", float when "cont_E"
            reward (float): reward calculated accordingly to the `reward_func`
            done (boolean): whether a terminal state has been observed
        '''
        Din, drug_time = action
        if drug_time > self.step_time:
            raise ValueError("Time duration for drug in cannot be longer than step time")
        
        self.actions = np.append(self.actions, np.array([[self.tSol[-1], Din]]), axis=0)
        self.total_drug_in += Din * drug_time * self.ki

        t_start = self.tSol[-1]
        t_end = t_start + drug_time
        init = self.sSol[-1, :]

        sol = solve_ivp(self.ODEsys, [t_start, t_end], init, args=(Din,), 
                        events = [self.event5p, self.eventTiny], max_step=0.01,
                        method = "LSODA")

        solEZ = sol.y[:2, :]
        roundedZero_solEZ = np.where(np.round(solEZ, 5) == 0, 0.0, solEZ)
        soly = np.append(roundedZero_solEZ, sol.y[[-1], :], axis=0)

        self.sSol = np.append(self.sSol, soly.T[1:, :], axis=0)
        self.tSol = np.append(self.tSol, sol.t[1:])
        self.t5p = np.append(self.t5p, sol.t_events[0])
        self.tTiny = np.append(self.tTiny, sol.t_events[1])

        if (self.step_time - drug_time) > 0.0:
            t_start = self.tSol[-1]
            t_end = t_start + (self.step_time - drug_time)
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
                
        self.state = self.get_state()

        reward, done = self.get_reward(action, self.sSol, self.tSol, **self.reward_kwargs)

        return self.state, reward, done
    
    def get_state(self):
        '''
        Returns the "current" state of the system/env for the controller to make decisions:
            state: float if `state_method` is "cont_E", int if "disc_EZ"
        '''
        if self.state_method == "cont_E": # returns the most recent density of species E (continuous value)
            state = self.sSol[-1, 0]
        
        if self.state_method == "disc_EZ" or self.state_method == "disc_E":
            if self.n_states is None:
                raise RuntimeError(f'n_states should be defined for \"{method}\" method')
            elif not isinstance(self.n_states, int):
                raise ValueError("n_states should be an integer")
        
        if self.state_method == "disc_EZ":
            # "current" bacterial densities
            E = self.sSol[-1, 0]
            Z = self.sSol[-1, 1]

            # discretizing bacterial densities
            N_disc = int(math.sqrt(self.n_states) - 2)
            self.OD2state = (self.growth_bounds[1] - self.growth_bounds[0]) / N_disc

            E_disc = int(E // self.OD2state + 1) if E > 0.0 else 0
            Z_disc = int(Z // self.OD2state + 1) if Z > 0.0 else 0
            
            # discrete state is a value in the matrix 
            # S = np.arange(self.n_states).reshape(math.sqrt(self.n_states), math.sqrt(self.n_states))
            # with E_disc as row index and Z_disc as column index
            # state = S[E_disc, Z_disc]
            state = int(E_disc * math.sqrt(self.n_states) + Z_disc)
        
        if self.state_method == "disc_E":
            # "current" bacterial density
            E = self.sSol[-1, 0]

            # discretizing bacterial density
            N_disc = int(self.n_states - 2)
            self.OD2state = (self.growth_bounds[1] - self.growth_bounds[0]) / N_disc

            E_disc = int(E // self.OD2state + 1) if E > 0.0 else 0
            state = E_disc
        
        return state
    
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
        self.total_drug_in = 0.0 

        self.mono = False # system starts at coexistence equilibrium / carrying capacities, so it's co-culture env
        
        self.five_percent = 0.05 * eqE

        self.t5p = np.array([])
        self.tTiny = np.array([]) 
        
        # update observable state to the controller
        self.state = self.get_state()
