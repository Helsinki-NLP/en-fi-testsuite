#!/bin/bash -l

#SBATCH -J agent
#SBATCH -o agent.%j.out
#SBATCH -e agent.%j.err
#SBATCH --mem=5g
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -t 24:00:00
#SBATCH -p serial

module load python-env/3.4.5
python3 makeAgentVocab.py
