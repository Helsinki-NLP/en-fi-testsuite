#!/bin/bash -l

#SBATCH -J trainlm
#SBATCH -o trainlm.%j.out
#SBATCH -e trainlm.%j.err
#SBATCH --mem=32g
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -t 06:00:00
#SBATCH -p serial

DATADIR="/proj/OPUS/WMT18/news_data/monolingual"
SUFFIX=".tok.en.gz"
LMDATA="$DATADIR/europarl$SUFFIX $DATADIR/news2007$SUFFIX $DATADIR/news2008$SUFFIX $DATADIR/news2009$SUFFIX $DATADIR/news2010$SUFFIX $DATADIR/news2011$SUFFIX $DATADIR/news2012$SUFFIX $DATADIR/news2013$SUFFIX $DATADIR/news2014$SUFFIX $DATADIR/news2015$SUFFIX $DATADIR/newscommv13$SUFFIX"

module use -a /proj/nlpl/software/modulefiles
module load moses

echo $LMDATA
zcat $LMDATA | lmplz -o 5 -S 31G > lm5.arpa

# query:
# echo '{}' | /usr/local/moses/bin/query {}.{}.arpa 2> /dev/null
