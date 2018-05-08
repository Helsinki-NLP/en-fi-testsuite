#!/bin/bash -l

#SBATCH -J wmt18-testsuite
#SBATCH -o testing.%j.out
#SBATCH -e testing.%j.err
#SBATCH -t 04:00:00
#SBATCH -N 1
#SBATCH -p gpu
#SBATCH --mem=4g
#SBATCH --gres=gpu:p100:1

module purge
module use -a /proj/nlpl/software/modulefiles
module load moses

echo "Starting at `date`"

TOKENIZER=/proj/nlpl/software/moses/4.0-65c75ff/moses/scripts/tokenizer
RECASER=/proj/nlpl/software/moses/4.0-65c75ff/moses/scripts/recaser
TRUECASEMODEL=/proj/OPUS/WMT18/news_data/truecaser-en.model

TESTFILE=/wrk/yvessche/wmt18/testsuite/select_shuf/morpheval-enfi-2018.en.sents
HNMTMODELDIR=/wrk/yvessche/wmt18/en-fi-hyb2bpe

if [ ! -f test.true ]
then
	cat $TESTFILE |\
		$TOKENIZER/replace-unicode-punctuation.perl |\
		$TOKENIZER/remove-non-printing-char.perl |\
		$TOKENIZER/normalize-punctuation.perl -l en |\
		$TOKENIZER/pre-tokenizer.perl -l en |\
		sed -e "s/it's/it is/g" \
			-e "s/It's/It is/g" \
			-e "s/That's/That is/g" \
			-e "s/What's/What is/g" \
			-e "s/She's/She is/g" \
			-e "s/He's/He is/g" \
			-e "s/We've/We have/g" \
			-e "s/We're/We are/g" \
			-e "s/They're/They are/g" \
			-e "s/There's/There is/g" \
			-e "s/What's/What is/g" \
			-e "s/didn't/did not/g" \
			-e "s/don't/do not/g" \
			-e "s/can't/cannot/g" \
			-e "s/they're/they are/g" \
			-e "s/that's/that is/g" \
			-e "s/he's/he is/g" \
			-e "s/wasn't/was not/g" \
			-e "s/she's/she is/g" \
			-e "s/couldn't/could not/g" \
			-e "s/we're/we are/g" \
			-e "s/you're/you are/g" \
			-e "s/we've/we have/g" \
			-e "s/doesn't/does not/g" \
			-e "s/weren't/were not/g" \
			-e "s/isn't/is not/g" \
			-e "s/haven't/have not/g" \
			-e "s/hadn't/had not/g" \
			-e "s/would've/would have/g" \
			-e "s/wouldn't/would not/g" \
			-e "s/won't/will not/g" \
			-e "s/we'll/we will/g" \
			-e "s/we'd/we would/g" \
			-e "s/she'd/she would/g" \
			-e "s/he'll/he will/g" \
			-e "s/he'd/he would/g" \
			-e "s/I'm/I am/g" \
			-e "s/here's/here is/g" \
			-e "s/I've/I have/g" \
			-e "s/I'v/I have/g" \
			-e "s/I'd/I would/g" \
			-e "s/He'd/He would/g" \
			-e "s/hasn't/has not/g" |\
		$TOKENIZER/tokenizer.perl -no-escape -l en |\
		sed 's/  */ /g;s/^ *//g;s/ *$$//g' |\
		$RECASER/truecase.perl --model $TRUECASEMODEL > test.true
fi

module load nlpl-hnmt

export THEANO_FLAGS="$THEANO_FLAGS",gpuarray.preallocate=0.3

MODELS="$HNMTMODELDIR"/model.a.160000:"$HNMTMODELDIR"/model.a.165000:"$HNMTMODELDIR"/model.a.170000:"$HNMTMODELDIR"/model.a.final
MODELS="$MODELS","$HNMTMODELDIR"/model.b.160000:"$HNMTMODELDIR"/model.b.165000:"$HNMTMODELDIR"/model.b.170000:"$HNMTMODELDIR"/model.b.final
MODELS="$MODELS","$HNMTMODELDIR"/model.c.155000:"$HNMTMODELDIR"/model.c.160000:"$HNMTMODELDIR"/model.c.165000:"$HNMTMODELDIR"/model.c.final
MODELS="$MODELS","$HNMTMODELDIR"/model.d.160000:"$HNMTMODELDIR"/model.d.165000:"$HNMTMODELDIR"/model.d.170000:"$HNMTMODELDIR"/model.d.final

echo "$MODELS"
srun hnmt.py --load-model "$MODELS" --translate test.true --output test.trans --beam-size 10
cat test.trans | $TOKENIZER/replace-unicode-punctuation.perl | $TOKENIZER/remove-non-printing-char.perl | $TOKENIZER/normalize-punctuation.perl -l fi | $TOKENIZER/detokenizer.perl -l fi -u > test.detok
    
echo "Finishing at `date`"
