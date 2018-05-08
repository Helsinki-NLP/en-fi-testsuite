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

INPUTDIR=../eval_test
TRANSLATION=test

echo "Starting at `date`"

awk '{print $0, "****"}' < $INPUTDIR/$TRANSLATION.detok | finnish-analyze-words > $TRANSLATION.morph
#awk '{print $0, "****"}' < $INPUTDIR/$TRANSLATION.detok | hfst-tokenize --unique --xerox /homeappl/home/yvessche/appl_taito/hfst_omorfi/tokenize.pmatch > $TRANSLATION.morph2
# this doesn't work with upper case words

echo "Finishing at `date`"
