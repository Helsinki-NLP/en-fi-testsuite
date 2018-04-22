#!/bin/bash -l

#SBATCH -J binarize
#SBATCH -o binarize.%j.out
#SBATCH -e binarize.%j.err
#SBATCH --mem=128g
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -t 06:00:00
#SBATCH -p serial

module use -a /proj/nlpl/software/modulefiles
module load moses

build_binary lm5.arpa lm5.bin

# query:
# echo '{}' | /usr/local/moses/bin/query {}.{}.arpa 2> /dev/null
