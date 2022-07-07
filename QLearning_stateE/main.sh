#!/bin/bash
PARALLEL_SCRIPT="/home/s4278836/polyInfect/parallel_experiments.py"

python $PARALLEL_SCRIPT -f collection_params.qlearning.micEZ70.json

python $PARALLEL_SCRIPT -f collection_params.qlearning.micZ140.json
