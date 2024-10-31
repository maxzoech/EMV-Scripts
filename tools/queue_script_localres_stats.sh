#!/bin/bash
# Example of simple slurm job submission script
# Prepared for Finlay node, Dec 2020 CNB

# Job parameters
#SBATCH -p debug     # Partition to submit to (Finlay --> debug)

# Output information redirection
# As the job will be launched in background, terminal output must be redirected
#SBATCH -o ./logs/S-%j_%x.out # This file will record output from STDOUT
#SBATCH -e ./logs/S-%j_%x.err # This file will record output from the STDERR

# Needed resources
#SBATCH --cpus-per-task=1   #   Number of GPUs to request
#SBATCH --mem-per-cpu=4G    #   Request 4 GB of memory per CPU core, 16GB total
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Initial timestamp
echo "Job with ID $SLURM_JOBID MR-$1 started at $(date)"

#Job steps
eval "$(conda shell.bash hook)"
CMD="srun --job-name=LR-$1 python /home/bioinfo/services/tools/script_execute_localres_stats.py -i $1"
echo $CMD
eval "$CMD"

# Final timestamp
echo "Job with ID $SLURM_JOBID MR-$1 ended at $(date)"

