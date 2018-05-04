#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse, collections, re


# def analyzeSentence(sentence):
	# global analyzer
	# result = []
	# analyzer_out = analyzer.match(sentence)		# this only yields one analysis per word, which might be wrong
	# print(">", analyzer_out)
	# for wordresult in re.split(r'(?<=]) ', analyzer_out):
		# tagdict = {}
		# # this removes anything not in square brackets, e.g. punctuation
		# for match in re.finditer(r'\[([^=\]]+)=([^=\]]+)\]', wordresult):
			# tagdict[match.group(1)] = match.group(2)
		# result.append(tagdict)
	# return result


def readAnalysis(analysisfile):
	line = analysisfile.readline()
	analysis = {}
	# word position is not important, as any occurrence of a word will have the same analysis
	currentword, currentwordfeatures, currentwordpos = "", set(), 1
	while not line.startswith('****\t'):
		if line.isspace():
			if len(currentwordfeatures) > 0:
				currentwordfeatures.add("@{}".format(currentwordpos))
				analysis[currentword] = currentwordfeatures
				currentword = ""
				currentwordfeatures = set()
				currentwordpos += 1
		else:
			elements = line.strip().split("\t")
			currentword = elements[0]
			currentwordfeatures.update(elements[1].split(" "))
		line = analysisfile.readline()
	return analysis


def sanityCheck(translationString, analysis):
	for key in analysis:
		if key not in translationString:
			print("Analyzed word {} not found in original string: {}".format(key, translationString.strip()))


def readSentencePair(translationfile, analysisfile, infofile):
	currenttask, currentexno = "", ""
	currentsentences = []
	currentanalyses = []
	for transline, infoline in zip(translationfile, infofile):
		exno, task = infoline.strip().split(" ", 1)
		analysis = readAnalysis(analysisfile)
		sanityCheck(transline, analysis)
		if task == currenttask and exno == currentexno:
			currentsentences.append(transline.strip())
			currentanalyses.append(analysis)
		else:
			if len(currentsentences) > 0:
				yield currentsentences, currentanalyses, currenttask, currentexno
			currenttask = task
			currentexno = exno
			currentsentences = [transline.strip()]
			currentanalyses = [analysis]
	if len(currentsentences) > 0:
		yield currentsentences, currentanalyses, currenttask, currentexno


def worddiff(analysis1, analysis2):
	words_only1 = {w: analysis1[w] for w in analysis1 if w not in analysis2}
	words_only2 = {w: analysis2[w] for w in analysis2 if w not in analysis1}
	return words_only1, words_only2


# simple feature difference tasks

def sing_plur(s1, s2, wo1, wo2):
	foundSg = any(['Sg' in wo1[x] for x in wo1])	# first sentence should contain singular
	foundPl = any(['Pl' in wo2[x] for x in wo2])	# second sentence should contain plural
	return foundSg, foundPl

def pron_sing_plur(s1, s2, wo1, wo2):
	foundSg = any(['Sg' in wo1[x] for x in wo1])	# first sentence should contain singular
	foundPl = any(['Pl' in wo2[x] for x in wo2])	# second sentence should contain plural
	return foundSg, foundPl

def pres_past(s1, s2, wo1, wo2):
	foundPrs = any(['Prs' in wo1[x] for x in wo1])
	foundPst = any(['Pst' in wo2[x] for x in wo2])
	return foundPrs, foundPst

def comp_adj(s1, s2, wo1, wo2):
	foundPos = any(['Pos' in wo1[x] for x in wo1])
	foundComp = any(['Comp' in wo2[x] for x in wo2])
	return foundPos, foundComp

# doesn't work well if there is more than one negation per sentence
# check again with newly extracted sentences
def pos_neg(s1, s2, wo1, wo2):
	foundPos = not any(['Neg' in wo1[x] for x in wo1])
	foundNeg = any(['Neg' in wo2[x] for x in wo2]) and (any(['ConNeg' in wo2[x] for x in wo2]) or any(['olla' in wo1[x] for x in wo1]))
	# last condition: he ovat tehneet => he eivät tehneet => tehneet does not show up in the second sentence
	return foundPos, foundNeg

# doesn't work well when pronouns are attached as clitics to prepositions
# check again with newly extracted sentences
def human_nonhuman_pron(s1, s2, wo1, wo2):
	foundHuman = any(['hän' in wo1[x] for x in wo1]) or any(['minä' in wo1[x] for x in wo1]) or any(['me' in wo1[x] for x in wo1])
	foundNonhuman = any(['se' in wo2[x] for x in wo2]) or any(['ne' in wo2[x] for x in wo2])
	return foundHuman, foundNonhuman

# check manually - may need to add proper possessive determiners
def det_poss(s1, s2, wo1, wo2):
	foundDet = True		# put a condition here?
	foundPoss = any(['PxSg1' in wo2[x] for x in wo2]) or any(['PxSg2' in wo2[x] for x in wo2]) or any(['Px3' in wo2[x] for x in wo2]) or any(['PxPl1' in wo2[x] for x in wo2]) or any(['PxPl2' in wo2[x] for x in wo2])
	return foundDet, foundPoss

# do we need to check more? position of the verb? what about 'jos'? how do the -va forms work?
def that_if(s1, s2, wo1, wo2):
	foundThat = any(['että' in wo1[x] for x in wo1]) or any(['ettei' in wo1[x] for x in wo1]) or any(['PrsPrc' in wo1[x] for x in wo1])
	foundIf = any(['Foc_kO' in wo2[x] for x in wo2])
	return foundThat, foundIf

# replacement tasks

def numbers(s1, s2, wo1, wo2, repl1, repl2):
	found1 = any([repl1 in x for x in wo1.keys()])
	found2 = any([repl2 in x for x in wo2.keys()])
	return found1, found2

# no way to deal with unanalyzed words - we may want to skip those
def complex_np(s1, s2, wo1, wo2, repl1, repl2):
	foundPron = any(['Pron' in wo1[x] for x in wo1]) or any(['Px3' in wo1[x] for x in wo1])
	nouns = [wo2[x] for x in wo2 if 'N' in wo2[x]]
	adjs = [wo2[x] for x in wo2 if 'A' in wo2[x] or 'Qnt' in wo2[x] or 'Ord' in wo2[x] or any(['vuotias' in f for f in wo2[x]])]
	nounFeatures = set()
	adjFeatures = set()
	for n in nouns:
		nounFeatures.update(n)
	for a in adjs:
		adjFeatures.update(a)

	shared = set(nounFeatures) & set(adjFeatures)
	sharedNum = set(['Sg', 'Pl']) & shared
	sharedCase = set(['Nom', 'Par', 'Gen', 'Ine', 'Ela', 'Ill', 'Ade', 'Abl', 'All', 'Ess', 'Ins', 'Abe', 'Tra', 'Com', 'Lat', 'Acc']) & shared
	sameFeatures = len(sharedNum) > 0 and len(sharedCase) > 0
	if sameFeatures:
		return foundPron, len(sharedNum) > 0 and len(sharedCase) > 0
	
	compoundNoun = any(["#" in f for f in nounFeatures])	# adj+noun is translated into a compound noun
	if compoundNoun:
		return foundPron, compoundNoun

	if len(nouns) > 1:
		snouns = sorted(nouns, key=lambda x: [int(n[1:]) for n in x if n.startswith("@")][0])
		foundGen = any(['Gen' in n for n in snouns[:-1]])
		return foundPron, foundGen

	return foundPron, False


# need to add more rewriting entries
# do we need to check more, e.g. case consistency?
def named_entities(s1, s2, wo1, wo2, repl1, repl2):
	rewrite = {"India": "Intia", "China": "Kiina"}
	found1 = rewrite.get(repl1, repl1).lower() in s1.lower()
	found2 = rewrite.get(repl2, repl2).lower() in s2.lower()
	return found1, found2


def prep1_prep2(wo1, wo2, config1, config2):
	prep1OK = False
	prep1 = [wo1[x] for x in wo1 if config1[0] in wo1[x]]
	if len(prep1) > 0:
		prep1 = prep1[0]	# there should only be one
		prep1Pos = [int(n[1:]) for n in prep1 if n.startswith("@")][0]
		prep1Nouns = [wo1[x] for x in wo1 if 'N' in wo1[x]]
		if config1[2] == 'Prep':
			prep1Nouns = [x for x in prep1Nouns if any([int(n[1:]) > prep1Pos for n in x if n.startswith("@")])]
		else:
			prep1Nouns = [x for x in prep1Nouns if any([int(n[1:]) < prep1Pos for n in x if n.startswith("@")])]

		if len(prep1Nouns) > 0:
			prep1Case = any([config1[3] in x for x in prep1Nouns])
			if not prep1Case:
				print("{}: no {} case found".format(config1[1], config1[3]))
			prep1OK = prep1Case
		else:
			print("{}: no nouns found".format(config1[1]))
	else:
		print("{}: no adposition found".format(config1[1]))

	prep2OK = False
	prep2 = [wo2[x] for x in wo2 if config2[0] in wo2[x]]
	if len(prep2) > 0:
		prep2 = prep2[0]	# there should only be one
		prep2Pos = [int(n[1:]) for n in prep2 if n.startswith("@")][0]
		prep2Nouns = [wo2[x] for x in wo2 if 'N' in wo2[x]]
		if config2[2] == 'Prep':
			prep2Nouns = [x for x in prep2Nouns if any([int(n[1:]) > prep2Pos for n in x if n.startswith("@")])]
		else:
			prep2Nouns = [x for x in prep2Nouns if any([int(n[1:]) < prep2Pos for n in x if n.startswith("@")])]

		if len(prep2Nouns) > 0:
			prep2Case = any([config2[3] in x for x in prep2Nouns])
			if not prep2Case:
				print("{}: no {} case found".format(config2[1], config2[3]))
			prep2OK = prep2Case
		else:
			print("{}: no nouns found".format(config2[1]))
	else:
		print("{}: no adposition found".format(config2[1]))
	return prep1OK, prep2OK


def during_before(s1, s2, wo1, wo2):
	return prep1_prep2(wo1, wo2, ('aikana', 'during', 'Postp', 'Gen'), ('ennen', 'before', 'Prep', 'Par'))

def before_after(s1, s2, wo1, wo2):
	return prep1_prep2(wo1, wo2, ('ennen', 'before', 'Prep', 'Par'), ('jälkeen', 'after', 'Postp', 'Gen'))

def without_with(s1, s2, wo1, wo2):
	return prep1_prep2(wo1, wo2, ('ilman', 'without', 'Prep', 'Par'), ('kanssa', 'with', 'Postp', 'Gen'))


# identity tasks

def masc_fem_pron(s1, s2, wo1, wo2):
	return len(wo1) == 0, len(wo2) == 0

def pres_fut(s1, s2, wo1, wo2):
	if len(wo2) > 0 and any(['tulla' in wo2[x] for x in wo2]):
		return True, True
	return len(wo1) == 0, len(wo2) == 0

def the_a(s1, s2, wo1, wo2):
	return len(wo1) == 0, len(wo2) == 0

def local_prep(s1, s2, wo1, wo2, repl1, repl2):
	# to implement
	return False

####

def evaluate(translationfile, analysesfile, infofile):
	total = collections.defaultdict(int)
	correct = collections.defaultdict(int)
	for sentences, analyses, task, exno in readSentencePair(translationfile, analysesfile, infofile):
		words_only1, words_only2 = worddiff(analyses[0], analyses[1])
		if ":" in task:
			taskname, repl1, repl2 = task.split(":")
		else:
			taskname = task
			repl1, repl2 = "", ""
		
		if taskname != 'without_with':
			continue
		
		if taskname in globals():
			taskproc = globals()[taskname]
			print(task, exno)
			
			if repl1 == "":
				result = taskproc(sentences[0], sentences[1], words_only1, words_only2)
			else:
				result = taskproc(sentences[0], sentences[1], words_only1, words_only2, repl1, repl2)
			
			if len(result) != 2:
				print(result)
				print(sentences[0])
				print(sentences[1])
				print("Skipping")
				continue
			
			x, y = result
			if x and y:		# both features found => correct
				correct[taskname] += 1
				total[taskname] += 1
			
			elif x or y:	# only one feature found => wrong
				print("Only one feature found")
				print(sentences[0])
				print(sentences[1])
				print(words_only1, repl1)
				print(words_only2, repl2)
				total[taskname] += 1
			
			else:			# none of the features found => wrong? skip? (often it's because the sentences are identical => wrong)
				print("Target feature not found")
				total[taskname] += 1
				print(sentences[0])
				print(sentences[1])
				print(words_only1, repl1)
				print(words_only2, repl2)
	
	print(total)
	print(correct)



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-trans', dest='trans', nargs="?", type=argparse.FileType('r'), help="translated input sentences")
	parser.add_argument('-omorfi', dest='omorfi', nargs="?", type=argparse.FileType('r'), help="omorfi-analyzed input sentences")
	parser.add_argument('-info', dest='info', nargs="?", type=argparse.FileType('r'), help="input info file")
	args = parser.parse_args()
	
	evaluate(args.trans, args.omorfi, args.info)

