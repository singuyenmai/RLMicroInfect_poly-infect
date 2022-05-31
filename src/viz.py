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
import src.colors as colchart

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
        
        # Plot total number of times drug valve opened
        # ax[1].plot(df['episode'], df['total_drug_prescribed'], 
        #            lw=line_w, marker='o', markersize=3,
        #            color=palE['yel'])

        # Set axis labels
        ax[0].set(xlabel='Episode', ylabel='Return')
        ax01.set(ylabel='Explore rate')
        # ax[1].set(xlabel='Episode', ylabel='Total times\ndrug valve opened')

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

        A = np.zeros((len(t), 1)) # actions
        D = env.sSol[:len(t), -1] # drug conc.
        E = env.sSol[:len(t), 0] # E
        Z = env.sSol[:len(t), 1] # Z
        M = E + Z # Total
        
        line_w = 3.0
        palT = colchart.get_colorBook("myTheme")
        action_ms = 3.0 if tmax <= (120.0 / tscale)  else 1.0

        # Plot actions
        # ax[0].plot(t, A, lw=0, marker='o', markersize=action_ms, color=palT['ora'])

        ax[0].set(ylabel='Action')
        # ax[0].set_ylim(0.0, 1.1)
        # ax[0].set_yticks([0.0, 1.0])
        # ax[0].set_yticklabels(["Close", "Open"], fontsize=22)

        # Plot drug conc.
        ax[1].plot(t, D, lw=line_w, color=palT['tur'])

        # Plot MIC
        ax[1].axhline(y = env.micE, lw=line_w/2, color=palT['tur'], ls='--')

        ax[1].set(ylabel='Drug\n($\mu$g/mL)')
        # if np.max(D) <= 250.0:
        #     ax[1].set_ylim(0.0, 250.0)
        #     ax[1].set_yticks([0, 125, 250])
        # else:
        #     ax[1].set_ylim(0.0, 400.0)
        #     ax[1].set_yticks([0, 250, 400])

        # Plot bacteria densities
        lE, = ax[2].plot(t, E, lw=line_w, color=palT['pur'], label='E')

        if not env.mono:
            lM, = ax[2].plot(t, M, lw=line_w, color=palT['grey'], label='Total')
            lZ, = ax[2].plot(t, Z, lw=line_w, color=palT['gre'], label='Z')
            
            ax[2].legend(handles=[lE, lZ, lM], ncol=3, 
                         loc='upper left', bbox_to_anchor=(-0.02, 1.02))
        else:
            ax[2].legend(handles=[lE], loc='upper left', bbox_to_anchor=(-0.02, 1.02))
        

        ax[2].set(xlabel = 'Time (hours)', ylabel='OD')
        ax[2].set_ylim(0.0, 1.2)
        ax[2].set_xlim(tmin, tmax)

        # set title
        if title == 'auto':
            title = "Simulation"
        
        ax[0].set_title(title, y=1.05)
        
        return fig