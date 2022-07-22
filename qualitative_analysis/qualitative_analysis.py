from polin.qualitative import Quali

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

import matplotlib.tri as tri
x = df['alpha_EZ']
y = df['alpha_ZE']
z = pd.factorize(df['regime'])[0]

triang = tri.Triangulation(x, y)

pastel = sns.color_palette("Pastel1", 5, as_cmap=True)

sns.scatterplot(data=df, x="alpha_EZ", y="alpha_ZE", hue="regime", 
                palette="Pastel1")
tcf = ax.tricontourf(triang, z, levels=6, cmap=pastel, vmin=0, vmax=8)
# fig.colorbar(tcf)
# ax.tricontour(triang, z, levels=6, colors=sns.color_palette("Pastel1", 5), linewidths=2.0)
ax.tricontour(triang, z, levels=6, colors='grey', linewidths=1.5)

ax.set_xlim((minEZ, maxEZ))
ax.set_ylim((minZE, maxZE))

ax.set_xlabel(r"$\alpha_{EZ}$")
ax.set_ylabel(r"$\alpha_{ZE}$")

from matplotlib.patches import Rectangle
ax.add_patch(Rectangle((-0.03, -0.05), 0.05, 0.06, 
             edgecolor = '#dd5129', lw=2, fill=False, label="region of interest"))

ax.scatter(x=-0.06, y=-0.06, marker='^', c='#17A398', s=60,
           label="example in sub-figure C & D")
ax.scatter(x=-0.01, y=-0.03, marker='^', c='#FE7F2D', s=60,
           label="example in sub-figure E")

ax.legend(bbox_to_anchor=(1, -0.04), loc='lower left', markerscale=2.5)

ax.axvline(0.0, color="black", ls='dashed')
ax.axhline(0.0, color="black", ls='dashed')

ax.text(x=0.002, y=0.002, s="+/+", fontsize=25)
ax.text(x=-0.01, y=0.002, s="-/+", fontsize=25)
ax.text(x=-0.01, y=-0.01, s="-/-", fontsize=25)
ax.text(x=0.002, y=-0.01, s="+/-", fontsize=25)

ax.text(x=0.001, y=0.028, s="0/+", fontsize=25)
ax.text(x=0.022, y=0.001, s="+/0", fontsize=25)

ax.text(x=0.001, y=-0.075, s="0/-", fontsize=25)
ax.text(x=-0.06, y=0.001, s="-/0", fontsize=25)

fig.savefig("qualitative_results.png", bbox_inches='tight')
