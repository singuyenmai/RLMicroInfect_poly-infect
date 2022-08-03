from typing import List, Dict, Tuple
import numpy as np

import json
import os
import argparse
import subprocess

from copy import deepcopy

class ExperimentsCollection():
    def __init__(self, collection_param_file: str) -> None:

        print("Parsing & Setting collection parameters ... ")

        with open(collection_param_file) as f:
            self.param_dict = json.load(f)
        
        # get arrays of interaction coefficients
        lEZ, uEZ, nEZ = self.param_dict['env']['ode_params']['alpha_EZ']
        self.alpha_EZ_arr = self.alpha_array(lEZ, uEZ, nEZ)

        lZE, uZE, nZE = self.param_dict['env']['ode_params']['alpha_ZE']
        self.alpha_ZE_arr = self.alpha_array(lZE, uZE, nZE)

        # set collection directory - also this is where the jobs are submitted from
        self.pwd = os.getcwd() + '/'
        self.collection_dir = self.pwd + self.param_dict['collection_ID'] + '/'

        # set directory for SLURM log & running log files
        self.slurm_log_dir = self.collection_dir + 'slurm_log/'
        self.log_dir = self.collection_dir + 'log/'

        print("Sucessful\n")
    
    def alpha_array(self, lower: float, upper: float, N: int) -> np.ndarray:
        '''
        Generates array of interaction coefficients (alpha_EZ or alpha_ZE)
        with number of elements N that are equally distributed between 2 regions
        [lower, 0.0] and [0.0, upper]
        Parameters:
            lower: lower bound
            upper: upper bound
            N: total number of elements, including bounds and 0.0
        Returns:
            arr: array of interaction coefficients
        '''
        if (N % 2 == 0):
            raise ValueError("The number of alpha values must be an odd number")
        
        n = int((N + 1)/2)
        
        arr = np.append(np.linspace(lower, 0.0, n), 
                        np.linspace(0.0, upper, n)[1:])
        
        return arr

    def set_directory(self) -> None:
        '''
        Sets up the directories, metadata file, and param files for every experiment
        '''    
        print("Setting up the directories for collection of experiments ... ")
        
        params = deepcopy(self.param_dict)

        collection_ID = params.pop("collection_ID")
        collection_name = params.pop("collection_name")

        if not os.path.exists(self.collection_dir):
            os.mkdir(self.collection_dir)
        
        metadat = self.collection_dir + "metadata.tsv"
        with open(metadat, 'w') as m:
            m.write(f'exp_ID\talpha_EZ\talpha_ZE')

        count = 0

        for a1 in self.alpha_EZ_arr:
            for a2 in self.alpha_ZE_arr:
                exp_ID = collection_ID + "." + str(count)
                exp_name = collection_name + " " + str(count)

                params['exp_ID'] = exp_ID
                params['exp_name'] = exp_name
                params['env']['ode_params']['alpha_EZ'] = a1
                params['env']['ode_params']['alpha_ZE'] = a2

                exp_dir = self.collection_dir + exp_ID + "/"
                if not os.path.exists(exp_dir):
                    os.mkdir(exp_dir)

                param_file = exp_dir + "params." + exp_ID + ".json"
                with open(param_file, 'w') as f:
                    json.dump(params, f, indent=4)
                
                with open(metadat, 'a') as m:
                    m.write(f'\n{exp_ID}\t{a1}\t{a2}')

                count += 1
        
        if not os.path.exists(self.slurm_log_dir):
            os.mkdir(self.slurm_log_dir)
        
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)
        
        print(f"Sucessful. There are in total {count} experiments\n")
    
    def run(self, local=False,
            re_test=False, test_done_break=False,
            test_qtable_episode='last', test_explore_rate=0.0, 
            test_savefig_format = 'png') -> None:
        '''
        Loops over the experiments and submit jobs to run them
        '''
        options = ["--test_qtable_episode", str(test_qtable_episode), 
                   "--test_explore_rate", str(test_explore_rate), 
                   "--test_savefig_format", test_savefig_format]
        if re_test:
            options = options + ["--test_only"]
        
        if test_done_break:
            options = options + ["--test_done_break"]
        
        N_exp = len(self.alpha_EZ_arr) * len(self.alpha_ZE_arr)

        if not local:
            
            JOB_SCRIPT = "/home/s4278836/polyInfect/peregrine_job.sh"
        
        else:
            
            confirmation = input("Argument --local has been provided, which means multiple experiments would be run on local machine. \
                                  Are you sure to continue? [y/n] ")
            while confirmation not in ["y", "n"]:
                confirmation = input("Please only answer either \"y\" (for Yes) or \"n\" (for No) and type your answer again: ")
            
            if confirmation == "y":
                script_dir = os.path.abspath(os.path.dirname(__file__))
                JOB_SCRIPT = script_dir + "/run_experiment.py"
            else:
                return
        
        for i in range(N_exp):
            
            exp_ID = self.param_dict['collection_ID'] + "." + str(i)
            param_file = self.collection_dir + exp_ID + "/" + "params." + exp_ID + ".json"
            log_file = self.log_dir + exp_ID + ".log"

            # args = ["echo", JOB_SCRIPT, param_file, log_file] + options # this is just for testing the script
            if not local:
                args = ["sbatch", JOB_SCRIPT, param_file, log_file] + options
            else:
                args = ["python", JOB_SCRIPT, "-f", param_file] + options

            print(f"Submitting job (if local==False) / Running (if local==True) for experiment {i} ... ")
            proc = subprocess.Popen(args, cwd=self.collection_dir)
            proc.wait()
            print("Done\n")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Running a collection of experiments supplied with a json parameter file")
    
    parser.add_argument("-f", "--collection_param_file", type=str, required=True)
    
    parser.add_argument("--local", action='store_true') # default is False
    
    parser.add_argument("-re", "--re_test", action='store_true') # default is False
    parser.add_argument("-tdb", "--test_done_break", action='store_true') # default is False
    
    parser.add_argument("-tqe", "--test_qtable_episode", 
                        default='last', required=False)
    parser.add_argument("-ter", "--test_explore_rate", type=float, 
                        default=0.0, required=False)
    
    parser.add_argument("-tsf", "--test_savefig_format", type=str, 
                        default='png', required=False)

    args = parser.parse_args()

    collection = ExperimentsCollection(args.collection_param_file)

    if not args.re_test:
        collection.set_directory()
    
    collection.run(local = args.local,
                   re_test = args.re_test, 
                   test_done_break = args.test_done_break,
                   test_qtable_episode = args.test_qtable_episode,
                   test_explore_rate = args.test_explore_rate,
                   test_savefig_format = args.test_savefig_format)