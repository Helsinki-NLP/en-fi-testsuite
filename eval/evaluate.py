#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse, collections, re, gzip


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
	
nelex = {}


def readAnalysis(analysisfile):
	line = analysisfile.readline()
	analysis = {}
	# word position is not important, as any occurrence of a word will have the same analysis
	currentword, currentwordfeatures, currentwordpos = "", set(), 1
	while not line.startswith('****\t'):
		if line.isspace():
			if len(currentwordfeatures) > 0:
				currentwordfeatures.add("@{}".format(currentwordpos))
				if currentword in analysis:
					analysis[currentword].update(currentwordfeatures)
				else:
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


def readSentencePair(translationfile, analysisfile, sourcefile):
	currenttask, currentexno = "", ""
	currentsentences = []
	currentsrcsentences = []
	currentanalyses = []
	for transline, sourceline in zip(translationfile, sourcefile):
		sentenceid, sourcesentence = sourceline.strip().split("\t", 1)
		task, exno = sentenceid.strip().rsplit(":", 1)
		exno = exno.split(".")[0]
		analysis = readAnalysis(analysisfile)
		sanityCheck(transline, analysis)
		if task == currenttask and exno == currentexno:
			currentsentences.append(transline.strip())
			currentsrcsentences.append(sourcesentence.strip())
			currentanalyses.append(analysis)
		else:
			if len(currentsentences) > 0:
				yield currentsentences, currentanalyses, currenttask, currentexno, currentsrcsentences
			currenttask = task
			currentexno = exno
			currentsentences = [transline.strip()]
			currentsrcsentences = [sourcesentence.strip()]
			currentanalyses = [analysis]
	if len(currentsentences) > 0:
		yield currentsentences, currentanalyses, currenttask, currentexno, currentsrcsentences


def numberOccurrences(s):
	return len([x for x in s if re.match(r'@\d+', x)])

def worddiff(analysis1, analysis2):
	words_only1 = {w: analysis1[w] for w in analysis1 if (w not in analysis2) or (numberOccurrences(analysis1[w]) > numberOccurrences(analysis2[w]))}
	words_only2 = {w: analysis2[w] for w in analysis2 if (w not in analysis1) or (numberOccurrences(analysis2[w]) > numberOccurrences(analysis1[w]))}
	return words_only1, words_only2


def worddict2str(worddict):
	posdict = {}
	for w in worddict:
		pos = [int(f[1:]) for f in worddict[w] if f.startswith("@")][0]
		posdict[pos] = w
	s = " ".join([posdict[x] for x in sorted(posdict)])
	return s

def isUnknown(worddict):
	return len(worddict) == 2		# the word itself and its position


# simple feature difference tasks

def sing_plur(wo1, wo2):
	foundSg = any([('N' in wo1[x]) and ('Sg' in wo1[x]) for x in wo1])	# first sentence should contain singular
	foundPl = any([('N' in wo2[x]) and ('Pl' in wo2[x]) for x in wo2])	# second sentence should contain plural
	return foundSg, foundPl, ""

def pron_sing_plur(wo1, wo2):
	foundSg = any([('Sg' in wo1[x]) and ('Pron' in wo1[x]) for x in wo1]) or any(['PxSg1' in wo1[x] for x in wo1]) or any(['PxSg2' in wo1[x] for x in wo1]) or any(['Px3' in wo1[x] for x in wo1])	# first sentence should contain singular
	foundPl = any([('Pl' in wo2[x]) and ('Pron' in wo2[x]) for x in wo2]) or any(['PxPl1' in wo2[x] for x in wo2]) or any(['PxPl2' in wo2[x] for x in wo2]) or any(['Px3' in wo2[x] for x in wo2]) # second sentence should contain plural
	return foundSg, foundPl, ""

def pres_past(wo1, wo2):
	foundPrs = any(['Prs' in wo1[x] for x in wo1])
	foundPst = any(['Pst' in wo2[x] for x in wo2])
	return foundPrs, foundPst, ""

def comp_adj(wo1, wo2):
	verbs = {"vanha": "ikääntyä", "kova": "koventua", "vähän": "alentaa", "vähäinen": "alentaa", "halpa": "halventua", "syvä": "syventää", "helppo": "helpottaa", "hyvä": "parantaa", "huono": "paheta", "paha": "paheta", "tiivis": "tiivistyä", "rikas": "rikastua", "heikko": "heikentyä"}
	# don't know which adjectives should trigger the following verbs:
	# kiinnittää, käyttäytyä, lukkiutua, lisätä, vannoutua, piiloutua
	foundAdv = any([('Adv' in wo1[x]) and any([y.endswith('sti') for y in wo1[x]]) for x in wo1])
	foundLocalAdv = any(['lähellä' in wo1[x] for x in wo1]) or any(['lähelle' in wo1[x] for x in wo1]) or any(['läheltä' in wo1[x] for x in wo1])
	foundPos = any([('A' in wo1[x]) and ('Pos' in wo1[x]) for x in wo1]) or foundAdv or foundLocalAdv
	foundComp = any([('A' in wo2[x]) and ('Comp' in wo2[x]) for x in wo2])
	msg = ""
	for a, v in verbs.items():
		if any([a in wo1[x] for x in wo1]) and any([v in wo2[x] for x in wo2]):
			foundPos = True
			foundComp = True
			msg = "adj/verb pair: {}/{}".format(a, v)
			break
	return foundPos, foundComp, msg

def pos_neg(wo1, wo2):
	foundPos = not any(['Neg' in wo1[x] for x in wo1])
	foundNeg = any(['Neg' in wo2[x] for x in wo2]) or (any(['ConNeg' in wo2[x] for x in wo2]) and any(['olla' in wo1[x] for x in wo1]))
	# last condition: he ovat tehneet => he eivät tehneet => tehneet does not show up in the second sentence
	return foundPos, foundNeg, ""

def human_nonhuman_pron(wo1, wo2):
	foundHuman = any(['hän' in wo1[x] for x in wo1]) or any(['minä' in wo1[x] for x in wo1]) or any(['me' in wo1[x] for x in wo1]) or any(['PxSg1' in wo1[x] for x in wo1]) or any(['PxPl1' in wo1[x] for x in wo1]) or any(['Px3' in wo1[x] for x in wo1])
	foundNonhuman = any(['se' in wo2[x] for x in wo2]) or any(['Px3' in wo2[x] for x in wo2]) or any(['sinne' in wo2[x] for x in wo2])
	# or any(['ne' in wo2[x] for x in wo2]) -- is there a reason why this should be kept?
	return foundHuman, foundNonhuman, ""

def det_poss(wo1, wo2, repl1, repl2):
	foundDet = True		# put a condition here?
	msg = ""
	if repl2 == 'my':
		foundPron = any(['Pron' in wo2[x] and 'Gen' in wo2[x] and 'minä' in wo2[x] for x in wo2])
		foundPoss = any(['PxSg1' in wo2[x] for x in wo2])
	elif repl2 == 'your':
		foundPron = any(['Pron' in wo2[x] and 'Gen' in wo2[x] and ('sinä' in wo2[x] or 'te' in wo2[x]) for x in wo2])
		foundPoss = any(['PxSg2' in wo2[x] for x in wo2]) or any(['PxPl2' in wo2[x] for x in wo2])
	elif repl2 == 'his' or repl2 == 'her':
		foundPron = any(['Pron' in wo2[x] and 'Gen' in wo2[x] and 'hän' in wo2[x] for x in wo2])
		foundPoss = any(['Px3' in wo2[x] for x in wo2])
	elif repl2 == 'our':
		foundPron = any(['Pron' in wo2[x] and 'Gen' in wo2[x] and 'me' in wo2[x] for x in wo2])
		foundPoss = any(['PxPl1' in wo2[x] for x in wo2])
	else:
		msg = "possessive not defined:" + repl2
	
	#foundPron = any(['Pron' in wo2[x] and 'Gen' in wo2[x] for x in wo2])
	#foundPoss = any(['PxSg1' in wo2[x] for x in wo2]) or any(['PxSg2' in wo2[x] for x in wo2]) or any(['Px3' in wo2[x] for x in wo2]) or any(['PxPl1' in wo2[x] for x in wo2]) or any(['PxPl2' in wo2[x] for x in wo2])
	return foundDet, foundPoss or foundPron, msg

# do we need to check more? position of the verb? morph features of the verb?
def that_if(wo1, wo2):
	foundMukaan = any(['mukaan' in wo1[x] for x in wo1])
	foundKertoa = any(['kertoa' in wo1[x] for x in wo1]) and any(['PrfPrc' in wo1[x] for x in wo1])
	foundThat = any(['että' in wo1[x] for x in wo1]) or any(['ettei' in wo1[x] for x in wo1]) or any(['PrsPrc' in wo1[x] for x in wo1])
	foundIf = any(['Foc_kO' in wo2[x] for x in wo2])
	return foundThat or foundMukaan or foundKertoa, foundIf, ""

# replacement tasks

def numbers(wo1, wo2, repl1, repl2):
	found1 = any([repl1 in x for x in wo1.keys()])
	found2 = any([repl2 in x for x in wo2.keys()])
	return found1, found2, ""

def complex_np(wo1, wo2, repl1, repl2):
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
		if foundPron:
			return foundPron, len(sharedNum) > 0 and len(sharedCase) > 0, "adj + noun"
		else:
			return foundPron, len(sharedNum) > 0 and len(sharedCase) > 0, "no pronoun"
	
	compoundNoun = any(["#" in f for f in nounFeatures]) or any(["-" in f for f in nounFeatures])	# adj+noun is translated into a compound noun
	if compoundNoun:
		return foundPron, compoundNoun, "compound noun"

	if len(nouns) > 1:
		snouns = sorted(nouns, key=lambda x: [int(n[1:]) for n in x if n.startswith("@")][0])
		foundGen = any(['Gen' in n for n in snouns[:-1]])
		return foundPron, foundGen, "genitive apposition"
	
	# it's difficult to judge what would be the best label for unanalyzeable words: wrong => 86.6% accuracy, correct => 87.4% accuracy
	# in light of the small difference, assume them to be wrong
	# for x in wo2:
		# if isUnknown(wo2[x]) and (x.startswith(repl2.split(" ")[0]) or x.startswith(repl2.split(" ")[1])):
			# return foundPron, True, 'unanalyzeable target word, assume correct'
	
	return foundPron, False, ""


def find_named_entity(repl, wo):
	# find repl as a lemma in wo
	repl_mod = repl.lower().replace("#", "").replace(".", "")
	for x in wo:
		for y in wo[x]:
			if repl_mod == y.lower().replace("#", "").replace(".", ""):
				return True
	
	# find nelex-translation of repl as a lemma in wo
	if repl_mod in nelex:
		repl_mod = nelex[repl_mod]	
		for x in wo:
			for y in wo[x]:
				if repl_mod == y.lower().replace("#", "").replace(".", ""):
					return True
				if repl_mod in y.lower().split("#") or repl_mod+"n" in y.lower().split("#"):		# match lontoo with länsi-#lontoo etc.
					return True
	
	# find repl as a string
	s = worddict2str(wo)
	if repl.lower() in s.lower():
		return True
	return False

# do we need to check more, e.g. case consistency?
def named_entities(wo1, wo2, repl1, repl2):
	found1 = find_named_entity(repl1, wo1)
	found2 = find_named_entity(repl2, wo2)
	return found1, found2, ""


# what about unknown nouns for which no case information is available?
def prep_postp(wo1, wo2, repl1, repl2):
	msg = ""
	prepOK = False
	if repl1 == 'before':
		repl1_fi = ['ennen']
	elif repl1 == 'without':
		repl1_fi = ['ilman']
	else:
		return None
	
	prep = [wo1[x] for x in wo1 if any([y in wo1[x] for y in repl1_fi])]
	if len(prep) > 0:
		prep = prep[0]	# there should only be one
		prepPos = [int(n[1:]) for n in prep if n.startswith("@")][0]
		prepNouns = [wo1[x] for x in wo1 if 'N' in wo1[x] or 'Pron' in wo1[x] or 'Num' in wo1[x]]
		prepNouns = [x for x in prepNouns if any([int(n[1:]) > prepPos for n in x if n.startswith("@")])]
		prepOK = False

		if len(prepNouns) > 0:
			prepCase = any(['Par' in x for x in prepNouns])
			if not prepCase:
				msg += "no {} case found after {} ".format('Par', "/".join(repl1_fi))
			prepOK = prepCase
		
		if not prepOK:	# sitä ennen, tätä ennen
			postpPos = [int(n[1:]) for n in prep if n.startswith("@")][0]
			postpProns = [wo1[x] for x in wo1 if 'Pron' in wo1[x]]
			postpProns = [x for x in postpProns if any([int(n[1:]) < postpPos for n in x if n.startswith("@")])]
			if len(postpProns) > 0:
				postpCase = any(['Par' in x for x in postpProns])
				if not postpCase:
					msg += "no {} case found before {} ".format('Par', "/".join(repl1_fi))
				prepOK = postpCase
		
		if not prepOK:
			msg += "no nouns found with {} ".format("/".join(repl1_fi))
	else:
		msg += "no {} preposition found".format("/".join(repl1_fi))

	postpOK = False
	if repl2 == 'after':
		repl2_fi = ['jälkeen', 'kuluttua']
	elif repl2 == 'during':
		repl2_fi = ['aikana']
	elif repl2 == 'with':
		repl2_fi = ['kanssa', 'myötä']
	else:
		return None
		
	postp = [wo2[x] for x in wo2 if any([y in wo2[x] for y in repl2_fi])]
	if len(postp) > 0:
		postp = postp[0]	# there should only be one
		postpPos = [int(n[1:]) for n in postp if n.startswith("@")][0]
		postpNouns = [wo2[x] for x in wo2 if 'N' in wo2[x] or 'Pron' in wo2[x] or 'Num' in wo2[x]]
		postpNouns = [x for x in postpNouns if any([int(n[1:]) < postpPos for n in x if n.startswith("@")])]

		if len(postpNouns) > 0:
			postpCase = any(['Gen' in x for x in postpNouns])
			postpCase2 = ('aikana' in repl2_fi) and any([('Pron' in x) and ('Ess' in x) for x in postpNouns])	# tuona aikana
			if postpCase:
				postpOK = True
			elif postpCase2:
				postpOK = True
			else:
				msg += "no {} case found with {} ".format('Gen', "/".join(repl2_fi))
				postpOK = False
		else:
			msg += "no nouns found with {} ".format("/".join(repl2_fi))
	else:
		msg += "no {} postposition found ".format("/".join(repl2_fi))

	if postp == [] and repl2 == 'during':
		#ess = any(['Ess' in wo2[x] for x in wo2])
		#ess |= any(['Ade' in wo2[x] and ('luku' in " ".join(wo2[x]) or 'viikko' in " ".join(wo2[x])) for x in wo2])
		ess = any([('Ess' in wo2[x]) or ('Ade' in wo2[x]) or ('Ine' in wo2[x]) for x in wo2])	# allow Ess/Ade/Ine anywhere - may be too lenient
		if ess:
			postpOK = True
			msg += "Ess found"
	
	if postp == [] and repl2 == 'after':
		# He puhuivat tavattuaan presidentti
		tempinf = any(['PrfPrc' in wo2[x] and 'Pass' in wo2[x] and 'Par' in wo2[x] and 'Px3' in wo2[x] for x in wo2])
		if tempinf:
			postpOK = True
			msg += "Temp Inf found"

	return prepOK, postpOK, msg


# identity tasks

def masc_fem_pron(wo1, wo2):
	return len(wo1) == 0, len(wo2) == 0, ""

def pres_fut(wo1, wo2):
	if len(wo2) > 0 and any(['tulla' in wo2[x] for x in wo2]):
		return True, True, "tulla"
	return len(wo1) == 0, len(wo2) == 0, ""

def the_a(wo1, wo2):
	return len(wo1) == 0, len(wo2) == 0, ""

def local_prep(wo1, wo2, repl1, repl2):
	localcases = set(['Ess', 'Ine', 'Ela', 'Ill', 'Ade', 'Abl', 'All', 'Par'])
	msg = []
	
	cases1 = set()
	for x in wo1:
		if repl1 == 'behind':
			if 'taka' in wo1[x]:
				cases1.update(wo1[x] & localcases)
			if 'taakse' in wo1[x]:
				cases1.add('Ill')
		
		elif repl1 == 'above':
			if 'ylä#puoli' in wo1[x]:
				cases1.update(wo1[x] & localcases)
			if 'yli' in wo1[x]:
				cases1.add('All'); cases1.add('Ade')
			if 'ylle' in wo1[x]:
				cases1.add('All')
			if 'yllä' in wo1[x]:
				cases1.add('Ade')
			if 'yltä' in wo1[x]:
				cases1.add('Abe')
			if 'edelle' in wo1[x]:
				cases1.add('All')
			if 'edellä' in wo1[x]:
				cases1.add('Ade')
			if 'edeltä' in wo1[x]:
				cases1.add('Abe')
			if ('korkea' in wo1[x]) and ('Comp' in wo1[x]):
				cases1.update(wo1[x] & localcases)
		
		elif repl1 == 'underneath':
			if 'alle' in wo1[x]:
				cases1.add('All')
			if 'alla' in wo1[x]:
				cases1.add('Ade')
			if 'alta' in wo1[x]:
				cases1.add('Abl')
		
		elif repl1 == 'outside':
			if 'ulko#puoli' in wo1[x]:
				cases1.update(wo1[x] & localcases)
			if 'ulkona' in wo1[x]:
				cases1.add('Ess')
			if 'ulkoa' in wo1[x]:
				cases1.add('Par')
			if 'ulos' in wo1[x]:
				cases1.add('All')
			# what should we do with 'ulkopuolinen'? outside isn't supposed to be used as an adjective in the chosen sample...
	
	cases2 = set()
	for x in wo2:
		if repl2 == 'in_front_of':
			if 'edessä' in wo2[x]:
				cases2.add('Ine')
			if 'eteen' in wo2[x]:
				cases2.add('Ill')
			if 'edestä' in wo2[x]:
				cases2.add('Ela')
			if 'ääri' in wo2[x]:
				cases2.update(wo2[x] & localcases)
		
		elif repl2 == 'below':
			if 'ala#puoli' in wo2[x]:
				cases2.update(wo2[x] & localcases)
			if 'alle' in wo2[x]:
				cases2.add('All')
			if 'alla' in wo2[x]:
				cases2.add('Ade')
			if 'alta' in wo2[x]:
				cases2.add('Abl')
		
		elif repl2 == 'ahead_of':
			if 'edessä' in wo2[x]:
				cases2.add('Ine')
			if 'eteen' in wo2[x]:
				cases2.add('Ill')
			if 'edestä' in wo2[x]:
				cases2.add('Ela')
			if 'ennen' in wo2[x]:
				cases2.add('All'); cases2.add('Ade')	# dummy cases
		
		elif repl2 == 'next_to':
			if 'vieri' in wo2[x]:
				cases2.update(wo2[x] & localcases)
		
		elif repl2 == 'inside':
			if 'sisä#puoli' in wo2[x]:
				cases2.update(wo2[x] & localcases)
			if 'sisällä' in wo2[x]:
				cases2.add('Ade')
			if 'sisälle' in wo2[x]:
				cases2.add('All')
			if 'sisältä' in wo2[x]:
				cases2.add('Abl')
			if 'N' in wo2[x]:		# add cases if no postposition is used
				cases2.update(wo2[x] & set(['Ine', 'Ela', 'Ill']))
	
	if len(cases1) == 0 and len(cases2) == 0:
		return False, False, "no translation of {} and {} found".format(repl1, repl2)
	elif len(cases1) == 0:
		return False, True, "no translation of {} found".format(repl1)
	elif len(cases2) == 0:
		return True, False, "no translation of {} found".format(repl2)
		
	caseMatch = False
	for case1 in cases1:
		if case1 in cases2:
			caseMatch = True
			break
		elif case1 in ['Ill', 'All'] and (('All' in cases2) or ('Ill' in cases2)):
			caseMatch = True
			break
		elif case1 in ['Ade', 'Ine', 'Ess'] and (('Ade' in cases2) or ('Ine' in cases2) or ('Ess' in cases2)):
			caseMatch = True
			break
		elif case1 in ['Ela', 'All', 'Par'] and (('All' in cases2) or ('Ela' in cases2) or ('Par' in cases2)):
			caseMatch = True
			break
	
	if not caseMatch:
		return False, False, "no case match"
	else:
		return True, True, ""

####


def format_worddict(worddict):
	posdict = {}
	for w in worddict:
		pos = [int(f[1:]) for f in worddict[w] if f.startswith("@")][0]
		posdict[pos] = worddict[w]
	s = []
	for x in sorted(posdict):
		s.append(" ".join(sorted(posdict[x])))
	return " || ".join(s)


def evaluate(translationfile, analysesfile, sourcefile, nelexfile=None, verboseevalfile=None, features=None):
	if nelexfile:
		global nelex
		nelex = {l.split("\t")[0].strip().lower(): l.split("\t")[1].strip().lower() for l in nelexfile}

	total = collections.defaultdict(int)
	correct = collections.defaultdict(int)
	for sentences, analyses, task, exno, srcsentences in readSentencePair(translationfile, analysesfile, sourcefile):
		words_only1, words_only2 = worddiff(analyses[0], analyses[1])
		if ":" in task:
			taskname, repl1, repl2 = task.split(":")
		else:
			taskname = task
			repl1, repl2 = "", ""

		if features is not None and taskname not in features.split(" "):
			continue
		
		if taskname in globals():
			taskproc = globals()[taskname]
			
			if repl1 == "":
				result = taskproc(words_only1, words_only2)
			else:
				result = taskproc(words_only1, words_only2, repl1, repl2)
			
			if result is None:
				if verboseevalfile:
					verboseevalfile.write("\t".join([task, exno, "Unknown word", sentences[0], format_worddict(words_only1), sentences[1], format_worddict(words_only2)]) + "\n")
				continue
			
			x, y, msg = result
			if x and y:		# both features found => correct
				correct[taskname] += 1
				total[taskname] += 1
				if verboseevalfile:
					s = "Correct: " + msg if msg else "Correct"
					verboseevalfile.write("\t".join([task, exno, s, sentences[0], "", sentences[1], ""]) + "\n")

			elif len(words_only1) == 0 and len(words_only2) == 0:
				# identical
				total[taskname] += 1
				if verboseevalfile:
					s = "Identical: " + msg if msg else "Identical"
					verboseevalfile.write("\t".join([task, exno, s, sentences[0], "", sentences[1], ""]) + "\n")
			
			elif x or y:	# only one feature found => wrong
				total[taskname] += 1
				if verboseevalfile and not x:
					s = "Left feature not found: " + msg if msg else "Left feature not found"
					verboseevalfile.write("\t".join([task, exno, s, sentences[0], format_worddict(words_only1), sentences[1], ""]) + "\n")
				if verboseevalfile and not y:
					s = "Right feature not found: " + msg if msg else "Right feature not found"
					verboseevalfile.write("\t".join([task, exno, s, sentences[0], "", sentences[1], format_worddict(words_only2)]) + "\n")
			
			else:
				total[taskname] += 1
				if verboseevalfile:
					s = "Both features not found: " + msg if msg else "Both features not found"
					verboseevalfile.write("\t".join([task, exno, s, sentences[0], format_worddict(words_only1), sentences[1], format_worddict(words_only2)]) + "\n")
	
	print("\t".join(["Task", "Correct", "Total", "Accuracy"]))
	for task in sorted(total):
		print("\t".join([task, "{}".format(correct.get(task, 0)), "{}".format(total[task]), "{:.1f}%".format(100 * correct.get(task, 0) / total[task])]))
	print()


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-trans', dest='trans', nargs="?", type=str, help="translated input sentences")
	parser.add_argument('-morph', dest='morph', nargs="?", type=argparse.FileType('r'), help="hfst-analyzed input sentences")
	parser.add_argument('-source', dest='source', nargs="?", type=argparse.FileType('r'), help="input source file (sentence IDs + English sentences)")
	parser.add_argument('-eval', dest='eval', nargs="?", type=argparse.FileType('w'), help="output file for verbose evaluation (optional)")
	parser.add_argument('-nelex', dest='nelex', nargs="?", type=argparse.FileType('r'), help="dictionary with named entity correspondences")
	parser.add_argument('-feats', dest='feats', nargs="?", help="list of features to analyze")
	args = parser.parse_args()
	
	if args.trans.endswith(".gz"):
		evaluate(gzip.open(args.trans, 'rt'), args.morph, args.source, args.nelex, args.eval, args.feats)
	else:
		evaluate(open(args.trans, 'r'), args.morph, args.source, args.nelex, args.eval, args.feats)
