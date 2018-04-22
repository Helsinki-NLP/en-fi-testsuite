
include Makefile.submit

TREETAGGERDIR=/homeappl/home/yvessche/appl_taito/treetagger

all: news2007.en.tagged.gz news2008.en.tagged.gz

news2007.en.tagged.gz:
	zcat /proj/OPUS/WMT18/news_data/monolingual/news2007.tok.en.gz | sed -e 's/$$/\n/g' | sed 's/ /\n/g' | $(TREETAGGERDIR)/bin/tree-tagger -token -lemma -sgml $(TREETAGGERDIR)/lib/english-utf8.par | gzip > $@
	# | perl -pe 's/\tV[BDHV]/\tVB/;s/\tIN\/that/\tIN/;'
	#zcat /proj/OPUS/WMT18/news_data/monolingual/news2007.en.gz | head -n200 | $(TREETAGGERDIR)/cmd/tree-tagger-english | gzip > news2007.en.tagged.gz

news2008.en.tagged.gz:
	zcat /proj/OPUS/WMT18/news_data/monolingual/news2008.tok.en.gz | sed -e 's/$$/\n/g' | sed 's/ /\n/g' | $(TREETAGGERDIR)/bin/tree-tagger -token -lemma -sgml $(TREETAGGERDIR)/lib/english-utf8.par | gzip > $@
	#| perl -pe 's/\tV[BDHV]/\tVB/;s/\tIN\/that/\tIN/;'
