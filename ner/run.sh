#!/bin/bash -l

#SBATCH -J ner
#SBATCH -o ner.%j.out
#SBATCH -e ner.%j.err
#SBATCH --mem=5g
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -t 24:00:00
#SBATCH -p serial

NERDIR=/wrk/yvessche/wmt18/testsuite/ner/stanford-ner-2018-02-27

module load java/oracle
module load python-env/3.4.5

DATASET=news2007
#DATASET=news2008
CHUNKSIZE=50000


mkdir -p $DATASET.src
cd $DATASET.src; zcat /proj/OPUS/WMT18/news_data/monolingual/$DATASET.tok.en.gz | split -l $CHUNKSIZE -a 3; cd ..

for f in $DATASET.src/x*
do
	echo "Starting processing $f"
	mkdir -p $DATASET.ner
	java -Xmx5000m -cp "$NERDIR/stanford-ner.jar:$NERDIR/lib/*" edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier $NERDIR/classifiers/english.all.3class.distsim.crf.ser.gz -tokenizerFactory edu.stanford.nlp.process.WhitespaceTokenizer -tokenizerOptions "tokenizeNLs=true" -outputFormat tabbedEntities -textFile $f > ${f//.src/.ner}
	echo "Finished processing $f"
done

python3 makeVocab.py $DATAID.ner $DATAID.nevocab.txt
