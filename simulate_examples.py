from polin.bacterial_env import BacterialEnv
from polin.controller import RationalAgent
import polin.viz as viz

import numpy as np
import json

import matplotlib.pyplot as plt

example_dir = "./examples/"

reward_kwargs = { "w_E": 1.0,
                  "Din_max": 120.0,
                  "w_D": 0.2
                  }

# Demonstrating qualitative analysis results:
# simulating with different inter-species interaction strengths &/ initial conditions
exp_names = ["0_0", "neg_neg", "pos_pos", "bi_Edom", "bi_Zdom"]
sim_time = 60.0*40.0

for e in exp_names:
    pfile = example_dir + "env_params." + e + ".json"

    with open(pfile) as f:
        env_param_dict = json.load(f)
    
    env = BacterialEnv(param_dict=env_param_dict, step_time=sim_time, 
                       reward_func="minED", reward_kwargs=reward_kwargs,
                       state_method="cont_E", n_states=None)
    env.step(action = (0.0, sim_time))

    fig = viz.visualize_simulation(env = env, st='full', tscale=60.0, title='auto')
    fig.savefig(example_dir + e + ".png", bbox_inches='tight')

# Demonstrating the rational drug policy & its effect on the focal species E
# An example under co-existence regime, with -/- interactions
# Bacterial densities start (initial conditions) at equilibrium levels
timestep = 60.0*6
sim_time = 5760.0

controller = RationalAgent(Din=100.0, drug_time=60.0*3)

exp_names = ["nodrug", "drug_mono", "drug_sameMIC", "drug_diffMIC"]

for e in exp_names:
    pfile = example_dir + "env_params." + e + ".json"

    with open(pfile) as f:
        env_param_dict = json.load(f)
    
    env = BacterialEnv(param_dict=env_param_dict, step_time=timestep, 
                       reward_func="minED", reward_kwargs=reward_kwargs,
                       state_method="cont_E", n_states=None)
    
    if e != "drug_mono":
        env.reset_2_equilibria(eq_type="coexist")
    
    state = env.state

    while env.tSol[-1] < sim_time:
        if (e != "nodrug"):
            action = controller.get_action(state)
            next_state, reward, done = env.step(action)
        else:
            next_state, reward, done = env.step(action = (0.0, timestep))
        state = next_state

    print(f'{e}:     {env.t5p}')
    
    fig = viz.visualize_simulation(env = env, st='full', tscale=60.0, title='auto')
    fig.savefig(example_dir + e + ".png", bbox_inches='tight')