# Adapting drug policy for microbial community context in infections

-by- Si-Nguyen Mai 
-contact- t.s.n.mai@student.rug.nl
-contact- singuyenthumai@gmail.com

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

```bash
cd Rational

# Example in mono-culture
# stored in `examples` directory
# input - parameter file: `env_params.drug_mono.json`
# output - figure: `drug_mono.png`
python simulate_examples.py

# run the experiments & collect performance measurements
bash main.sh

# visualize results across experiments
# run Jupyter Notebook `viz_features.ipynb`
```

## Q-learning on different ecological contexts

Directory `QLearning_stateE`

```bash
cd QLearning_stateE

# run the experiments & collect performance measurements
# read the file `main.sh` before running it, manual modifications may be needed at lines 3-11
bash main.sh

# visualize results across experiments
# run Jupyter Notebook `viz_features.ipynb`
```

## References

**de Vos MGJ**, **Zagorski M**, **McNally A**, **Bollenbach T**. Interaction networks, ecological stability, and collective antibiotic tolerance in polymicrobial infections. *Proc Natl Acad Sci*. 2017;114: 10666–10671. doi:10.1073/PNAS.1713372114

http://www.antimicrobe.org/h04c.files/history/PK-PD%20Quint.asp

https://www.medicines.org.uk/emc/product/5752/smpc#gref

https://go.drugbank.com/drugs/DB00440