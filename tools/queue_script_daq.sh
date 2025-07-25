#!/bin/bash
# Example of simple slurm job submission script
# Prepared for Finlay node, Dec 2020 CNB

# Job parameters
#SBATCH -p debug     # Partition to submit to (Finlay --> debug)
#SBATCH --job-name=DQ-{$1-$2} # Job Name

# Output information redirection
# As the job will be launched in background, terminal output must be redirected
#SBATCH -o ./logs/S-%j_%x.out # This file will record output from STDOUT
#SBATCH -e ./logs/S-%j_%x.err # This file will record output from the STDERR

# Needed resources
#SBATCH --cpus-per-task=1   #	Number of GPUs to request
#SBATCH --mem-per-cpu=8G    #	Request 8 GB of memory per CPU core, 32GB total
#SBATCH --gres=gpu:1        #	Request 1 GPU
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK


# Initial timestamp
echo "Job with ID $SLURM_JOBID DQ-$1-$2 started at $(date)"

#Job steps
cmmd="srun --job-name=DQ-$1-$2 /usr/bin/python3 /home/bioinfo/services/emv/tools/script_execute_daq.py -i $1 -p $2"
echo $cmmd
$cmmd


# Final timestamp
echo "Job with ID $SLURM_JOBID DQ-$1-$2 ended at $(date)"
