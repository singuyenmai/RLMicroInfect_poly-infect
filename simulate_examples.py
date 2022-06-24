from polin.bacterial_env import BacterialEnv
from polin.controller import RationalAgent
import polin.viz as viz

import numpy as np
import json

import matplotlib.pyplot as plt

example_dir = "./examples/"

sim_time = 60.0*35.0

# Demonstrating qualitative analysis results:
# simulating with different inter-species interaction strengths &/ initial conditions
exp_names = ["0_0", "neg_neg", "pos_pos", "bi_Edom", "bi_Zdom"]

for e in exp_names:
    pfile = example_dir + "env_params." + e + ".json"

    with open(pfile) as f:
        env_param_dict = json.load(f)
    
    env = BacterialEnv(param_dict=env_param_dict, step_time=sim_time)
    env.step(action = (0.0, sim_time))

    fig = viz.visualize_simulation(env)
    fig.savefig(example_dir + e + ".png", bbox_inches='tight')

# Demonstrating the rational drug policy & its effect on the focal species E
# An example under co-existence regime, with -/- interactions
# Bacterial densities start (initial conditions) at equilibrium levels
timestep = 60.0*6

controller = RationalAgent(Din=100.0, drug_time=60.0*3)

exp_names = ["nodrug", "drug_mono", "drug_sameMIC", "drug_diffMIC"]

for e in exp_names:
    pfile = example_dir + "env_params." + e + ".json"

    with open(pfile) as f:
        env_param_dict = json.load(f)
    
    env = BacterialEnv(param_dict=env_param_dict, step_time=timestep, state_method="cont_E")
    
    if e != "drug_mono":
        env.reset_2_coexist_equilibrium()

    while env.tSol[-1] < sim_time:
        if (e != "nodrug"):
            act = controller.get_action(env.state)
            env.step(action = act)
        else:
            env.step(action = (0.0, timestep))

    print(f'{e}:     {env.t5p}')
    
    fig = viz.visualize_simulation(env)
    fig.savefig(example_dir + e + ".png", bbox_inches='tight')