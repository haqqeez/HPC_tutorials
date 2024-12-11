#!/bin/bash
#SBATCH --account=rrg-markpb68
#SBATCH --time=TIMLIM
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=CPUS
#SBATCH --mem=RAM
#SBATCH --job-name=TASKNAME
#SBATCH --output=/home/haqqeez/SLURMS/ANIMAL/TASKNAME_%j.out
#SBATCH --error=/home/haqqeez/SLURMS/ANIMAL/errors/TASKNAME_%j.err
#SBATCH --mail-type="ALL"
#SBATCH --mail-user=MYEMAIL

module load python/3.10
module load scipy-stack

#source /lustre02/home/haqqeez/GLM_env/bin/activate

virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install --no-index sklearn


python -u SCRIPTPATH NUM_CPUS

