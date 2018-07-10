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

echo "Starting at `date`"

for file in 37-morpheval-en-fi/*.gz;
do
	echo $file
	zcat $file | awk '{print $0, "****"}' | finnish-analyze-words > analyzed/$(basename $file .gz).morph
done

echo "Finishing at `date`"
