import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
font = {'family': 'sans-serif', 'serif': 'Helvetica',
        'size': 25}
plt.rc('font', **font)
legnd = {'fontsize': 20, 'handlelength': 2.0}
plt.rc('legend', **legnd)
mathtext = {'mathtext.default': 'it' } 
plt.rcParams.update(mathtext)

palT_ora = "#FE7F2D"
palE_gre = "#43b284"
palT_grey = "#919191"

fig, ax = plt.subplots(1, 4, figsize=(6*4, 5*1), sharex=True, gridspec_kw={'wspace': 0.4})
    
sim_time = 5760.0 #min
tscale = 60.0 #convert min to h
dscale = 10**3 #convert ug/mL to mg/mL

ax[0].set_ylim(9.8, 16.0)
ax[0].set_ylabel("Return")
ax[1].set_ylim(-5.0, 1.15*sim_time/tscale)
ax[1].set_ylabel("$T_{\\theta}$ (hours)")
ax[2].set_ylim(-5.0, 1.15*sim_time/tscale)
ax[2].set_ylabel("$T_{5\%}$ (hours)")
ax[3].set_ylim(-0.1, 1.8)
ax[3].set_ylabel("Total supplied drug (mg/mL)")

for a in ax:
    a.set_xlim(-0.035, 0.025)
    a.set_xticks([-0.03, 0.0, 0.02])
    a.set_xlabel(r"$\alpha_{EZ}$")

for a in ax[1:3]:
    sl = a.axhline(y = sim_time / tscale, ls="--", color=palT_grey, label="Simulation time")
ax[3].legend(handles=[sl], frameon=False, markerscale=1.5, 
                bbox_to_anchor=(1.0, 0.0), loc="lower left")

fig.savefig("blank.png", bbox_inches='tight')