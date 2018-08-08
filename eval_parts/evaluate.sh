#!/bin/bash -l

#SBATCH -J wmt18-testsuite
#SBATCH -o evaluating.%j.out
#SBATCH -e evaluating.%j.err
#SBATCH --mem=1g
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -t 1:00:00
#SBATCH -p serial

module load python-env/3.4.5

echo "Starting at `date`"

mkdir -p results

for file in 37-morpheval-en-fi/*.gz;
do
	base=$(basename $file .gz)
	echo $base
	python3 ../eval/evaluate.py -trans $file -morph analyzed/$base.morph -source ../select_shuf/morpheval-enfi-2018.en -nelex ../eval/ne-lex.txt -eval results/$base.eval.tsv > results/$base.numbers.tsv
done

echo "Finishing at `date`"
