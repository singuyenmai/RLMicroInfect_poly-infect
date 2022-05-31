from src.bacterial_env import BacterialEnv
import src.viz as viz
import numpy as np

import matplotlib.pyplot as plt

example_dir = "./examples/"

sim_time = 60.0*35.0

# Demonstrating qualitative analysis results:
# simulating with different inter-species interaction strengths &/ initial conditions
exp_names = ["0_0", "neg_neg", "pos_pos", "bi_Edom", "bi_Zdom"]

for e in exp_names:
    pfile = example_dir + "env_params." + e + ".json"
    
    env = BacterialEnv(param_file=pfile, sampling_time=sim_time)
    env.step(action = (0, sim_time))

    fig = viz.visualize_simulation(env)
    fig.savefig(example_dir + e + ".png", bbox_inches='tight')

# Demonstrating the rational drug policy & its effect on the focal species E
# An example under co-existence regime, with -/- interactions
# Bacterial densities start (initial conditions) at equilibrium levels
timestep = 60.0*6
drug_time = 60.0*3

exp_names = ["nodrug", "drug_mono", "drug_sameMIC", "drug_diffMIC"]

for e in exp_names:
    pfile = example_dir + "env_params." + e + ".json"

    env = BacterialEnv(param_file=pfile, sampling_time=timestep)

    while env.tSol[-1] < sim_time:
        if (env.sSol[-1, 0] > 0.0) & (e != "nodrug"):
            env.step(action = (1, drug_time))
        else:
            env.step(action = (0, timestep))
    
    fig = viz.visualize_simulation(env)
    fig.savefig(example_dir + e + ".png", bbox_inches='tight')