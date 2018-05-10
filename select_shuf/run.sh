#!/bin/bash -l

DATASET=news2007
NBLINES=500

for FEATURE in sing_plur pron_sing_plur pres_past comp_adj pos_neg human_nonhuman_pron det_poss numbers named_entities complex_np prep_postp masc_fem_pron pres_fut the_a local_prep that_if
do
	echo $FEATURE
	if [ ! -e "$DATASET.$FEATURE.$NBLINES.txt" ]; then
		shuf -n $NBLINES ../score/$DATASET.$FEATURE.filtered.txt > $DATASET.$FEATURE.$NBLINES.txt
	fi
done

module load python-env/3.4.5
python3 reformat.py news2007 500
