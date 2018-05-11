#!/bin/bash -l

module use -a /proj/nlpl/software/modulefiles
module load moses
TOKENIZER=/proj/nlpl/software/moses/4.0-65c75ff/moses/scripts/tokenizer

DATASET=news2007
NBLINES=500

for FEATURE in sing_plur pron_sing_plur pres_past comp_adj pos_neg human_nonhuman_pron det_poss numbers named_entities complex_np prep_postp masc_fem_pron pres_fut the_a local_prep that_if
do
	echo $FEATURE
	if [ ! -e "$DATASET.$FEATURE.$NBLINES.txt" ]; then
		shuf -n $NBLINES ../score/$DATASET.$FEATURE.filtered.txt > $DATASET.$FEATURE.$NBLINES.txt
	fi
	if [ ! -e "$DATASET.$FEATURE.$NBLINES.2.txt" ]; then
		cut -f 1 $DATASET.$FEATURE.$NBLINES.txt | $TOKENIZER/detokenizer.perl -l en > $DATASET.$FEATURE.$NBLINES.1.txt
		cut -f 2 $DATASET.$FEATURE.$NBLINES.txt | $TOKENIZER/detokenizer.perl -l en > $DATASET.$FEATURE.$NBLINES.2.txt
	fi
done

module load python-env/3.4.5
python3 reformat.py news2007 500
