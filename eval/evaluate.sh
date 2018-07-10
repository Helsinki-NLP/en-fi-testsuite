#!/bin/bash -l

#SBATCH -J wmt18-testsuite
#SBATCH -o evaluating.%j.out
#SBATCH -e evaluating.%j.err
#SBATCH --mem=1g
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -t 0:05:00
#SBATCH -p serial

module load python-env/3.4.5

INPUTDIR=../eval_test
TRANSLATION=test

echo "Starting at `date`"

python3 evaluate.py -trans $INPUTDIR/$TRANSLATION.detok -morph $TRANSLATION.morph -source ../select_shuf/morpheval-enfi-2018.en -eval $TRANSLATION.result.csv -nelex ne-lex.txt > $TRANSLATION.numbers.csv

echo "Finishing at `date`"
