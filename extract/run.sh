#!/bin/bash -l

#SBATCH -J extraction
#SBATCH -o extraction.%j.out
#SBATCH -e extraction.%j.err
#SBATCH --mem=1g
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -t 3:00:00
#SBATCH -p serial

module load python-env/2.7.13

DATASET=news2007

echo "Starting at `date`"


# Fairly good features: sing_plur[A1] pron_sing_plur[A2] pres_past[A5] comp_adj[A6] pos_neg[A7] det_poss[*] numbers[*] complex_np[B1] named_entities[*] before_after[B4,*] during_before[B4,2]
# python extract.py $DATASET sing_plur
# python extract.py $DATASET pron_sing_plur
# python extract.py $DATASET pres_past
# python extract.py $DATASET comp_adj
# python extract.py $DATASET pos_neg
python extract.py $DATASET det_poss
# python extract.py $DATASET that_if
# python extract.py $DATASET numbers
# python extract.py $DATASET complex_np
# python extract_named_entities.py $DATASET
# python extract.py $DATASET before_after
# python extract.py $DATASET during_before

# Features that need to be checked:  human_nonhuman_pron[*] without_with[B4,5]
# python extract.py $DATASET human_nonhuman_pron
# python extract.py $DATASET without_with

# Identity features: masc_fem_pron[A3] pres_fut[A4] the_a[*] local_prep[*]
# python extract.py $DATASET local_prep
# python extract.py $DATASET masc_fem_pron
# python extract.py $DATASET pres_fut
# python extract.py $DATASET the_a

wc -l news2007.* > stats.txt

echo "Finishing at `date`"
