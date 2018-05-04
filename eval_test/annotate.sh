#!/bin/bash -l

#SBATCH -J wmt18-testsuite
#SBATCH -o annotating.%j.out
#SBATCH -e annotating.%j.err
#SBATCH --mem=1g
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -t 2:00:00
#SBATCH -p serial

module load hfst/3.14.0

TRANSLATION=test

echo "Starting at `date`"

awk '{print $0, "****"}' < $TRANSLATION.detok | finnish-analyze-words > $TRANSLATION.omorfi

echo "Finishing at `date`"
