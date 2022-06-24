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
    mathtext = {'mathtext.default': 'regular' } 
    plt.rcParams.update(mathtext)

def visualize_train(train_perf_file):
        set_plot_style()

        df = pd.read_csv(train_perf_file, sep='\t')
        
        fig, ax = plt.subplots(1, 2, figsize=(9*2, 6),
                               gridspec_kw={'wspace': 0.5})
        line_w = 0.0
        palE = colchart.get_colorBook("Egypt")
        palT = colchart.get_colorBook("myTheme")

        # Plot return (cumulative rewards)
        ax[0].plot(df['episode'], df['e_return'], 
                   lw=line_w, marker='o', markersize=3,
                   color=palE['bla'], label='Return')
        # Plot explore rate
        ax01 = ax[0].twinx()
        ax01.plot(df['episode'], df['explore_rate'], 
                  lw=2, color=palT['exp'], label='Explore rate')
        
        # Plot total drug in
        ax[1].plot(df['episode'], df['total_drug_in'], 
                   lw=line_w, marker='o', markersize=3,
                   color=palT['tur'])

        # Set axis labels
        ax[0].set(xlabel='Episode', ylabel='Return')
        ax01.set(ylabel='Explore rate')
        ax[1].set(xlabel='Episode', ylabel='Cumulative drug in ($\mu$g/mL)')

        # Add legends
        ax[0].legend(bbox_to_anchor=(1.0, 1.0), loc='lower right')
        ax01.legend(bbox_to_anchor=(0.0, 1.0), loc='lower left')

        return fig

def visualize_simulation(env, st='full', 
                         tscale=60.0, title='auto'):
        set_plot_style()

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

        ax[0].set(ylabel='Action\n($\mu$g/mL)')
        ax[0].set_ylim(-10, 140.0)
        ax[0].set_yticks([0, 100, 140])

        # Plot drug conc.
        ax[1].plot(t, D, lw=line_w, color=palT['tur'])

        # Plot MIC
        if not env.mono:
            ax[1].axhline(y = env.micZ, lw=line_w/2, color=palT['gre'], ls='--')
        ax[1].axhline(y = env.micE, lw=line_w/2, color=palT['pur'], ls='--')

        ax[1].set(ylabel='Drug\n($\mu$g/mL)')
        ax[1].set_ylim(0.0, 200.0)
        ax[1].set_yticks([0, 100, 200])

        # Plot bacteria densities
        lE, = ax[2].plot(t, E, lw=line_w, color=palT['pur'], label='E')

        if not env.mono:
            lM, = ax[2].plot(t, M, lw=line_w, color=palT['grey'], label='Total')
            lZ, = ax[2].plot(t, Z, lw=line_w, color=palT['gre'], label='Z')
            
            ax[2].legend(handles=[lE, lZ, lM], ncol=1, 
                         loc='upper right', bbox_to_anchor=(1.02, 1.02))
        else:
            ax[2].legend(handles=[lE], loc='upper right', bbox_to_anchor=(1.02, 1.02))
        

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