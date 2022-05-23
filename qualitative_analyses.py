from src.qualitative import Quali

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("ticks")
font = {'family': 'sans-serif', 'serif': 'Helvetica',
        'size': 25}
plt.rc('font', **font)
legnd = {'fontsize': 20, 'handlelength': 1.5}
plt.rc('legend', **legnd)
mathtext = {'mathtext.default': 'regular' } 
plt.rcParams.update(mathtext)

# Run qualitative analyses
param_file = "./qualitative_params.json"

Q = Quali(param_file)
Q_result = Q.analyze_across_alphas(out_filename="qualitative_results")

# Function to return regime based on stabilities of equilibria
def which_regime(trip):
    if trip['eqE'] == "stable":
        if trip['eqZ'] == "stable":
            return "bistable competitive exclusion"
        else:
            return "E dominates"
    elif trip['eqZ'] == "stable":
        return "Z dominates"
    elif trip['eqEZ'] == "stable":
        return "co-existence"
    else:
        return "unbounded growth"

# Read result data table and get regimes
df = pd.read_csv("qualitative_results.tsv", sep="\t")

df['regime'] = df.apply(which_regime, axis=1)
df['eqEZ_unbounded'] = df.apply(lambda x: True if x['eqEZ']=="unbounded" else False, axis=1)

# Max, min values of interaction coeffs
maxEZ = df['alpha_EZ'].max()
minEZ = df['alpha_EZ'].min()

maxZE = df['alpha_ZE'].max()
minZE = df['alpha_ZE'].min()

# Visualizing qualitative results
fig, ax = plt.subplots(1, 1, figsize=(7, 6))

sns.scatterplot(data=df, x="alpha_EZ", y="alpha_ZE", hue="regime", palette="Pastel1")

ax.set_xlim((minEZ, maxEZ))
ax.set_ylim((minZE, maxZE))

ax.set_xlabel(r"$\alpha_{EZ}$")
ax.set_ylabel(r"$\alpha_{ZE}$")

ax.legend(bbox_to_anchor=(1, 0.5), loc='upper left', markerscale=2.5)

ax.axvline(0.0, color="black")
ax.axhline(0.0, color="black")

ax.text(x=0.005, y=0.005, s="+/+", fontsize='large')
ax.text(x=-0.03, y=0.005, s="-/+", fontsize='large')
ax.text(x=-0.03, y=-0.03, s="-/-", fontsize='large')
ax.text(x=0.005, y=-0.03, s="+/-", fontsize='large')

ax.text(x=0.0, y=0.028, s="0/+", fontsize='large')
ax.text(x=0.022, y=0.0, s="+/0", fontsize='large')

fig.savefig("./qualitative_results.png", bbox_inches="tight")