# Adapting drug policy for microbial community context in infections

I aimed to answer the two following questions: 

1. Would microbial community contexts in infections change the outcome of a rational drug policy?
2. Can reinforcement learning be applied to adapt drug policy to different community contexts?

## Installation

Create virtual environment

```bash
conda create -n rl4Infect python=3.6
conda activate rl4Infect
```

Install dependencies

```bash
pip install -r requirements.txt
```

Install the source code

```
pip install -e .
```

Pipeline scripts are:

- `run_experiment.py` for single experiment with 1 pair of interaction strengths
- `parallel_experiments.py` for multiple experiments with multiple pairs of interaction strengths 
  - If on Peregrine HPC, multiple jobs will be submitted (job script `peregrine_job.sh`) 
  - If on local machine, experiments will be run sequentially in a `for` loop

## The microbial infectious environment

### Parameters from (de Vos *et al.*, 2017)

Directory `params_deVos2017`

```bash
cd params_deVos2017

# Read the `README.md` to understand the data files 

# create pretty metadata table
python make_selected_list.py

# Open and run the Jupyter Notebook `data_exploration.ipynb`
```

### Qualitative analysis - Inter-species interaction strengths for stable co-existence

 On 2-species model without drug ---> different regimes of species abundance for varying inter-species interaction strengths

Directory `qualitative_analysis`

Mathematica notebook `mathematical_analyses.nb`

Running for many pairs of interaction strengths & visualizing results

```bash
cd qualitative_analysis

python qualitative_analysis.py 
# or run Jupyter Notebook `qualitative_analysis.ipynb`

# Example simulations
# stored in `examples` directory
# input - parameter files: `env_params.bi_Edom.json` (Fig. 4.2C); `env_params.bi_Zdom.json` (Fig. 4.2D); `env_params.neg_neg.json` (Fig. 4.2E)
# output - figures: `bi_Edom.png` (Fig. 4.2C); `bi_Zdom.png` (Fig. 4.2D); `neg_neg.png` (Fig. 4.2E)
python simulate_examples.py
```

## Rational drug policy on different ecological contexts

Directory `Rational`

### Example in mono-culture, stored in `examples` directory

```bash
cd Rational

# input - parameter file: `env_params.drug_mono.json`
# output - figure: `drug_mono.png`
python simulate_examples.py
```

### Run the experiments & collect performance measurements

**First, if you run the experiments on an HPC with SLURM**, then

- Create your own job script by following the script `peregrine_job.sh`, particularly from lines 16. At line 42, change the path to the script `run_experiment.py` accordingly to your machine.
- Open the script `parallel_experiments.py`, then change the path to your job script at line 129.

**To run separately for each case of MIC level of the neighbor microbe $Z$**, run the `parallel_experiments.py`  script with input as a parameter json file.  For example, to do experiments in the case where $MIC_E = MIC_Z = 70$, follow these command lines

```bash
cd Rational

# Set a variable named PARALLEL_SCRIPT to the script `parallel_experiments.py` in your machine

# If run on an HPC with SLURM
python $PARALLEL_SCRIPT -f collection_params.rational.micEZ70.json

# If run on local or remote machine (no SLURM job submissions), 
# make sure that the script `run_experiment.py` is in the same directory with the `parallel_experiments.py`
# use the argument `--local`
python $PARALLEL_SCRIPT -f collection_params.rational.micEZ70.json --local
```

- To collect the performance measurements, run the lines 15-45 of the script `Rational/main.sh` in your terminal

**To run all the experiments and collect the measurements from them**:

- Open the script `main.sh` 
- At line 2, change the path to the script file `parallel_experiments.py` 
- If run on local or remote machine (no SLURM job submissions), add the argument `--local` to lines 4-10
- Then run the script by following the below command lines

```bash
cd Rational
bash main.sh
```

### Visualize results across experiments

Run Jupyter Notebook `viz_features.ipynb`


## Q-learning on different ecological contexts

Directory `QLearning_stateE`

The process for running the experiments here is very similar to when you run the rational policy. Therefore, please follow the instructions in the above section. You would just need to modify the following things:

- The parameter file. For example, to do experiments in the case where $MIC_E = MIC_Z = 70$, the parameter file would be `collection_params.qlearning.micEZ70.json`.

- Whether you want to do both the training and testing

  - If yes, then no additional argument is required

  - If no, and you could do only testing (given that all the training files have been already there) by using the argument `--re_test`. For example, the following command will test the learned Q-Learning policies in the case where $MIC_E = MIC_Z = 70$ on a local machine:

    ```bash
    python $PARALLEL_SCRIPT -f collection_params.qlearning.micEZ70.json --local --re_test
    ```

- **To run all the experiments and collect the measurements from them**, 

  - Open the script `main.sh`, then change the lines 3-11 to fit your running environment (SLURM or local) and your purpose (training-testing or testing-only)
  - Run the script with `bash main.sh`

- To collect the performance measurements, run the lines 16-47 of the script `QLearning_stateE/main.sh` in your terminal. To collect from both Q-Learning & rational policies, run the lines 52-66.

- To visualize the results across experiments, also run the Jupyter Notebook named `viz_features.ipynb`

## References

**de Vos MGJ**, **Zagorski M**, **McNally A**, **Bollenbach T**. Interaction networks, ecological stability, and collective antibiotic tolerance in polymicrobial infections. *Proc Natl Acad Sci*. 2017;114: 10666–10671. doi:10.1073/PNAS.1713372114

http://www.antimicrobe.org/h04c.files/history/PK-PD%20Quint.asp

https://www.medicines.org.uk/emc/product/5752/smpc#gref

https://go.drugbank.com/drugs/DB00440
