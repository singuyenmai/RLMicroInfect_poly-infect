import numpy as np
import pandas as pd

import os
import tempfile
import atexit
import shutil

mpldir = tempfile.mkdtemp()
atexit.register(shutil.rmtree, mpldir)  # rm directory on succ exit

os.environ['MPLCONFIGDIR'] = mpldir

import matplotlib.pyplot as plt
import seaborn as sns
import polin.colors as colchart

def set_plot_style():
    sns.set_style("whitegrid")
    font = {'family': 'sans-serif', 'serif': 'Helvetica',
            'size': 25}
    plt.rc('font', **font)
    legnd = {'fontsize': 20, 'handlelength': 1.5}
    plt.rc('legend', **legnd)

def visualize_train(train_perf_file: str, episode_time_max: float) -> plt.figure:
        set_plot_style()
        mathtext = {'mathtext.default': 'it' } 
        plt.rcParams.update(mathtext)
        plt.rcParams["legend.markerscale"] = 4

        df = pd.read_csv(train_perf_file, sep='\t')
        
        fig, ax = plt.subplots(1, 5, figsize=(7.5*4, 5.5),
                               gridspec_kw={'width_ratios': [0.12, 0.0, 0.12, 0.12, 0.12], 
                                            'wspace': 0.4})
        ax[1].axis('off')

        line_w = 0.0
        palE = colchart.get_colorBook("Egypt")
        palT = colchart.get_colorBook("myTheme")

        # Plot return (cumulative rewards)
        ax[0].scatter(df['episode'], df['e_return'], 
                      s=8, marker='o',
                      c=palE['bla'], label='Return')
        
        ax[0].set_ylim(-1.0, 20.0)
        ax[0].set(xlabel='Episode', ylabel='Return')
        
        # Plot explore rate
        ax01 = ax[0].twinx()
        ax01.plot(df['episode'], df['explore_rate'], 
                  lw=2, color=palT['exp'], label='Explore rate')
        ax01.set(ylabel='Explore rate')

        # Add legends
        ax[0].legend(bbox_to_anchor=(1.1, 1.0), loc='lower right')
        ax01.legend(bbox_to_anchor=(-0.05, 1.0), loc='lower left')
        
        # Plot first time to a tiny density
        tscale = 60.0 # convert min from hour
        tTiny_first = df['tTiny_first'].fillna(value = episode_time_max*1.1) / tscale

        ax[2].scatter(df['episode'], tTiny_first, 
                      s=8, marker='o', c = palT['pink'])
        ax[2].axhline(y = episode_time_max/tscale, color=palT['ora'], lw=2, ls='--', label="Simulation time")

        ax[2].legend(bbox_to_anchor=(1.0, 1.0), loc='lower right')

        ax[2].set_ylim(-2.5, 1.15*episode_time_max/tscale)
        ax[2].set(xlabel='Episode', ylabel="   \n$T_{tiny}$ (hours)")

        # Plot first time to a 5% of initial E
        tscale = 60.0 # convert min from hour
        t5p_first = df['t5p_first'].fillna(value = episode_time_max*1.1) / tscale

        ax[3].scatter(df['episode'], t5p_first, 
                      s=8, marker='o', c = palT['lightblue'])
        ax[3].axhline(y = episode_time_max/tscale, color=palT['ora'], lw=2, ls='--', label="Simulation time")

        ax[3].legend(bbox_to_anchor=(1.0, 1.0), loc='lower right')

        ax[3].set_ylim(-2.5, 1.15*episode_time_max/tscale)
        ax[3].set(xlabel='Episode', ylabel="   \n$T_{5\%}$ (hours)")

        # Plot total drug in
        dscale = 10**3 # converting from ug to mg
        ax[4].scatter(df['episode'], df['total_drug_in']/dscale, 
                      s=8, marker='o', c=palT['tur'])
        
        ax[4].set_ylim(-0.1, 2.2)
        ax[4].set(xlabel='Episode', ylabel='Total supplied drug (mg)')

        return fig

def visualize_simulation(env, st='full', 
                         tscale=60.0, title='auto') -> plt.figure:
        set_plot_style()
        mathtext = {'mathtext.default': 'it' } 
        plt.rcParams.update(mathtext)

        fig, ax = plt.subplots(3,1, figsize=(7, 12), 
                                sharex=True,
                                gridspec_kw={'height_ratios': [0.15, 0.15, 0.7]})

        # time points
        t = env.tSol / tscale if st == 'full' else env.tSol[env.tSol <= st] / tscale
        tmin = t[0]
        tmax = t[-1]

        A = env.actions # actions
        D = env.sSol[:len(t), -1] # drug conc.
        E = env.sSol[:len(t), 0] # E
        Z = env.sSol[:len(t), 1] # Z
        M = E + Z # Total
        
        line_w = 3.0
        palT = colchart.get_colorBook("myTheme")
        action_ms = 80.0

        # Plot actions
        ax[0].scatter(A[:, 0] / tscale, A[:, 1], s=action_ms, marker='^', color=palT['ora'])

        ax[0].set(ylabel='Chosen $D_{in}$\n($\mu$g/mL)')
        ax[0].set_ylim(-10, 140.0)
        ax[0].set_yticks([0, 100, 140])

        # Plot drug conc.
        ax[1].plot(t, D, lw=line_w, color=palT['tur'])

        # Plot MIC
        lEmic = ax[1].axhline(y = env.micE, lw=line_w/2, 
                              color=palT['pur'], ls='--', label="$MIC_E$")
        
        if not env.mono:
            lZmic = ax[1].axhline(y = env.micZ, lw=line_w/2, 
                                  color=palT['gre'], ls='--', label="$MIC_Z$")

        ax[1].set(ylabel='Drug\n($\mu$g/mL)')
        ax[1].set_ylim(0.0, 200.0)
        ax[1].set_yticks([0, 100, 200])

        # Plot bacteria densities
        lE, = ax[2].plot(t, E, lw=line_w, color=palT['pur'], label='E')

        if not env.mono:
            lM, = ax[2].plot(t, M, lw=line_w, color=palT['grey'], label='Total')
            lZ, = ax[2].plot(t, Z, lw=line_w, color=palT['gre'], label='Z')
            
            hdles = [lE, lZ, lM, lEmic, lZmic] if len(A) > 1 else [lE, lZ, lM]
        else:
            hdles = [lE, lEmic] if len(A) > 1 else [lE]

        ax[2].legend(handles=hdles, ncol=2, 
                     loc='upper right', bbox_to_anchor=(1.02, 1.02))
        

        ax[2].set(xlabel = 'Time (hours)', ylabel='OD')
        ax[2].set_ylim(0.0, 1.0)
        ax[2].set_xlim(tmin, tmax)

        # set title
        if title == 'auto':
            title = "Simulation"
        elif title == 'none':
            title = ""
        
        ax[0].set_title(title, y=1.05)
        
        return fig