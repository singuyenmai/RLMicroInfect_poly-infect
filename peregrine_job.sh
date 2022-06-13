#!/bin/bash
#SBATCH --job-name=polyInfect
#SBATCH --output=./slurm_log/%j.log

#SBATCH --time=06:00:00
#SBATCH --partition=regular

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB

#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=t.s.n.mai@student.rug.nl

# Check if arguments are given
if [ "$#" -eq "0" ]; then
	echo "ERROR: No arguments supplied. Please provide parameter file name and log file name...";
	exit 1;
fi

if [ -z "$1" ]; then
	echo "ERROR: argument 1 is an empty string. Please provide parameter file name...";
	exit 2;
fi

if [ -z "$2" ]; then
	echo "ERROR: argument 2 is an empty string. Please provide log file name...";
	exit 2;
fi

# Parse arguments
param_file=$1
shift
log_file=$2
shift
options=$@

# Write JobID
echo -e $SLURM_JOB_ID"\t"$param_file"\t"$log_file >> ./jobs.tsv

# Add job to job-queue
RUN_SCRIPT="/home/s4278836/polyInfect/run_experiment.py"
python $RUN_SCRIPT -f $param_file $options > $log_file 2>&1
# echo $PWD $param_file $log_file $options