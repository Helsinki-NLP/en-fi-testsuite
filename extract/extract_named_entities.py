#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re, os, extract, gzip, random

def levenshtein(seq1, seq2):
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
    return thisrow[len(seq2) - 1]


def matchAlternatives(nefilename):
	nefile = open(nefilename, 'r')
	highfreqvocab = {"ORGANIZATION": set(), "LOCATION": set(), "PERSON": set()}
	lowfreqvocab = {"ORGANIZATION": set(), "LOCATION": set(), "PERSON": set()}
	for line in nefile:
		elements = line.decode('utf-8').strip().split("\t")
		if " " in elements[0] or " " in elements[1]:		# only use one-word named entities
			continue
		if elements[0] in ['UK', 'Treasury', 'House']:
			continue
		freq = int(elements[2])
		if freq > 1000:
			highfreqvocab[elements[1]].add(elements[0])
		elif freq < 100 and freq > 20:
			lowfreqvocab[elements[1]].add(elements[0])
	nefile.close()
	
	matches = {"ORGANIZATION": {}, "LOCATION": {}, "PERSON": {}}
	used = set()
	for k in matches:
		for s in highfreqvocab[k]:
			distmin, argmin = sys.maxsize, []
			
			for x in lowfreqvocab[k]:
				if x not in used:		# make sure every low-freq word is used only for one high-freq word
					d = levenshtein(s, x)
					if (d > 2):
						if d == distmin:
							argmin.append(x)
						elif d < distmin:
							distmin = d
							argmin = [x]
			if len(argmin) > 0:
				matches[k][s] = argmin
				used.update(argmin)
	return matches


def extractSentences(fileid, taskid, nbsentences=-1):
	print "Load named entity pairs"
	matches = matchAlternatives("../ner/%s.nevocab.txt" % fileid)
	print "Done"
	
	print "Load and validate tagged sentences"
	taggedfile = gzip.open("../tag/%s.en.tagged.gz" % fileid)
	maxSentenceLength = 15
	validsentences = set()
	for sentence in extract.TreeTaggerSentenceReader(taggedfile, maxSentenceLength):
		if extract.validSentence(sentence):
			validsentences.add(u" ".join([x[0] for x in sentence]))
	taggedfile.close()
	print "Done"
	
	outfile = open("%s.%s.txt" % (fileid, taskid), 'w')
	sentenceid = 0
	alreadywritten = set()
	
	for filename in os.listdir("../ner/%s.ner" % fileid):
		print "Process file", filename
		nerfile = open("../ner/%s.ner/%s" % (fileid, filename), 'r')
		origsentence = []
		modsentence = []
		modification = []
		for line in nerfile:
			line = line.decode('utf-8')
			if line.strip() == "":
				if len(modification) > 0:
					modstr = u' '.join(modsentence)
					origstr = u' '.join(origsentence)
					if (modstr != "") and (origstr != modstr) and (origstr in validsentences) and (modstr not in validsentences) and (modstr not in alreadywritten) and (modstr.count(' ') <= maxSentenceLength) and (origstr.split(" ").count(modification[0]) == 1):
						s = u"%s\t%s\t%s:%s:%s\t%i\n" % (origstr.strip(), modstr.strip(), taskid, modification[0], modification[1], sentenceid)
						outfile.write(s.encode('utf-8'))
						if nbsentences > 0:
							print origstr
							print modstr
							print
						sentenceid += 1
						alreadywritten.add(modstr)
				origsentence = []
				modsentence = []
				modification = []
			else:
				elements = [x.strip() for x in line.split("\t")]
				if elements[0] != "":
					if elements[0] in matches[elements[1]] and (len(modification) == 0):		# only change one NE per line
						origsentence.append(elements[0])
						mod = random.choice(matches[elements[1]][elements[0]])
						modsentence.append(mod)
						modification = (elements[0], mod)
						#matches[elements[1]][elements[0]].remove(mod)	# remove the element from the candidate list - leads to very low numbers
					else:
						origsentence.append(elements[0])
						modsentence.append(elements[0])
				if len(elements) > 2 and elements[2] != "":
					origsentence.append(elements[2])
					modsentence.append(elements[2])
			if (nbsentences > 0) and (sentenceid > nbsentences):
				break
	
	print fileid, taskid, sentenceid, "sentences written"


if __name__ == "__main__":
	# Usage example: python extract_ner.py news2007
	# Usage example: python extract.py news2007 100	[first 100 sentences with debugging output on stdout]
	if len(sys.argv) >= 3:
		extractSentences(sys.argv[1], 'named_entities', int(sys.argv[2]))
	else:
		extractSentences(sys.argv[1], 'named_entities')
	