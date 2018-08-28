# en-fi-testsuite

## For WMT18 participants

The test suite (English source sentences used in WMT18) can be found in `select_shuf/morpheval-enfi-2018.en`

The results of the evaluation can be found in the `eval_parts` folder:
* Summary of all feature accuracy values: `eval_parts/all.numbers.tsv`
* Per-system feature accuracies: `eval_parts/results/[submission-name].numbers.tsv`
* Detailed output listing each contrast pair with morphological analysis and evaluation decision: `eval_parts/results/[submission-name].eval.tsv`


## Data preprocessing

* The `tag` folder contains scripts to tag the English news files. It also contains a script to extract Adj+Noun chunks from the data.
* The `ner` folder contains scripts to annotate the English news files with the Stanford NER system. It also contains scripts to extract frequent and rare named entities.
* The `lm` folder contains a 5-gram language model trained on the news data and scripts for training it.

## Contrast pair extraction, generation and filtering

* The `extract` folder contains the scripts for extracting example sentences from the tagged news files, and the resulting files.
* The `score` folder contains the scripts for scoring the example sentences with the language model and filtering out the lowest third of sentences.
* The `select_shuf` folder contains scripts to select a random sample of n (=500 in our case) example sentence pairs per feature, and to reformat them for the test suite.

## Translation output evaluation

* The `eval_test` folder contains a script to translate the testsuite using an existing HNMT system, including tokenization/detokenization using the Moses tools.
* The `eval` folder contains the evaluation service scripts, i.e. the script to perform the morphological analysis on the translations and the script to evaluate the contrasts.
* The `eval_parts` folder contains the evaluation results for the systems submitted at WMT18 (see above). It also contains scripts to aggregate values of different systems and to extract examples for manual evaluation.
