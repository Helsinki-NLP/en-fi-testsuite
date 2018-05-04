#!/bin/bash -l

#SBATCH -J score
#SBATCH -o scoring.%j.out
#SBATCH -e scoring.%j.err
#SBATCH --mem=85g
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -t 24:00:00
#SBATCH -p serial

module use -a /proj/nlpl/software/modulefiles
module load moses
module load python-env/3.4.5

echo "Starting at `date`"
which query

DATASET=news2007

for FEATURE in sing_plur pron_sing_plur pres_past comp_adj pos_neg human_nonhuman_pron det_poss numbers named_entities complex_np before_after during_before without_with masc_fem_pron pres_fut the_a local_prep that_if
do
	echo $FEATURE
	if [ ! -e "$DATASET.$FEATURE.1.scored" ]; then
		cut -f 1 ../extract/$DATASET.$FEATURE.txt | query ../lm/lm5.bin | grep -Po '(?<=Total: )[0-9-.]+' > $DATASET.$FEATURE.1.scored
	fi
	if [ ! -e "$DATASET.$FEATURE.2.scored" ]; then
		cut -f 2 ../extract/$DATASET.$FEATURE.txt | query ../lm/lm5.bin | grep -Po '(?<=Total: )[0-9-.]+' > $DATASET.$FEATURE.2.scored
	fi
	if [ ! -e "$DATASET.$FEATURE.filtered.txt" ]; then
		python3 score.py $DATASET.$FEATURE
	fi
done

echo "Finishing at `date`"
