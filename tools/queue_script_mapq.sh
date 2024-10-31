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
#SBATCH --cpus-per-task=8   #	Number of GPUs to request
#SBATCH --mem-per-cpu=4G    #	Request 4 GB of memory per CPU core, 32GB total
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Initial timestamp
echo "Job with ID $SLURM_JOBID MQ-$1-$2 started at $(date)"

#Job steps
eval "$(conda shell.bash hook)"
conda activate scipion3
cmmd="srun --job-name=MQ-$1-$2 python3 /home/bioinfo/services/emv/tools/script_execute_mapq.py -i $1 -p $2"
echo $cmmd
echo "---> SLURM_CPUS_PER_TASK = $SLURM_CPUS_PER_TASK"
echo "---> OMP_NUM_THREAD = $OMP_NUM_THREAD"
$cmmd


# Final timestamp
echo "Job with ID $SLURM_JOBID MQ-$1-$2 ended at $(date)"
