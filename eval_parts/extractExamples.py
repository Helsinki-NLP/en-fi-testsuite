#!/usr/bin/python3
# -*- coding: utf-8 -*-

import collections

# by decreasing BLEU score
systems = ["NICT.5658", "HY-NMT-en-fi.5570", "uedin.5707", "Aalto.5550", "HY-NMTtwostep-en-fi.5639", "CUNI-Kocmi.5620", "talp-upc.5424", "online-B.0", "HY-SMT-en-fi.5436", "online-G.0", "online-A.0", "HY-AH-en-fi.5567"]

features = ["sing_plur", "pron_sing_plur", "pres_past", "comp_adj", "pos_neg", "human_nonhuman_pron", "det_poss", "that_if", "prep_postp", "local_prep", "complex_np", "named_entities", "numbers"]
stabfeatures = ["masc_fem_pron", "pres_fut", "the_a"]


def getExampleList(trueColumn=-1, falseColumn=-1):
	examples = set()
	f = open("all.correct.csv", 'r')
	first = True
	for line in f:
		if first:
			first = False
			continue
		elements = line.strip().split("\t")
		keepExample = ((trueColumn < 0) or (elements[trueColumn] == "True")) and ((falseColumn < 0) or (elements[falseColumn] == "False"))
		if keepExample:
			examples.add((elements[0], elements[1]))
	f.close()
	print(trueColumn, falseColumn, len(examples), "examples selected")
	return examples


def extractAllCorrect():
	# extract ids of allCorrect examples
	exampleIds = getExampleList(trueColumn=3)
	
	# extract source and worst system examples
	system = "HY-SMT-en-fi.5436"
	sf = open("../select_shuf/morpheval-enfi-2018.en", 'r', encoding='utf-8')
	tf = open("results/{}.en-fi.eval.csv".format(system), 'r', encoding='utf-8')
	examples = collections.defaultdict(dict)
	nbExamples = 0
	for tline in tf:
		sline1 = sf.readline()
		sline2 = sf.readline()
		telem = tline.strip().split("\t")
		selem = sline1.strip().split("\t") + sline2.strip().split("\t")
		extype = telem[0].split(":")[0]
		if extype+":" in selem[0] and extype+":" in selem[2] and ":"+telem[1]+".1" in selem[0] and ":"+telem[1]+".2" in selem[2]:
			if (extype, telem[1]) in exampleIds:
				examples[extype][telem[1]] = (selem[1], selem[3], telem[2], telem[3], telem[5])
				nbExamples += 1
		else:
			print("Sentence mismatch:", telem[0], selem[0], selem[2])
			continue
	sf.close()
	tf.close()
	print(nbExamples, "examples found")
	
	of = open("examples/allCorrect.csv", 'w', encoding='utf-8')
	examplesPerFeature = 10
	for feature in features:
		if feature not in examples:
			continue
		print(len(examples[feature]), "examples found for feature", feature)
		for example in sorted(examples[feature])[:examplesPerFeature]:
			of.write("\t".join([feature, example, examples[feature][example][0], examples[feature][example][1]]) + "\n")
			of.write("\t".join([system, examples[feature][example][2], examples[feature][example][3], examples[feature][example][4]]) + "\n")
			of.write("\n")
	of.close()


def extractAllWrong():
	# extract ids of allWrong examples
	exampleIds = getExampleList(trueColumn=5)
	
	# extract source and best system examples
	system = "NICT.5658"
	sf = open("../select_shuf/morpheval-enfi-2018.en", 'r', encoding='utf-8')
	tf = open("results/{}.en-fi.eval.csv".format(system), 'r', encoding='utf-8')
	examples = collections.defaultdict(dict)
	nbExamples = 0
	for tline in tf:
		sline1 = sf.readline()
		sline2 = sf.readline()
		telem = tline.strip().split("\t")
		selem = sline1.strip().split("\t") + sline2.strip().split("\t")
		extype = telem[0].split(":")[0]
		if extype+":" in selem[0] and extype+":" in selem[2] and ":"+telem[1]+".1" in selem[0] and ":"+telem[1]+".2" in selem[2]:
			if (extype, telem[1]) in exampleIds:
				examples[extype][telem[1]] = (selem[1], selem[3], telem[2], telem[3], telem[5])
				nbExamples += 1
		else:
			print("Sentence mismatch:", telem[0], selem[0], selem[2])
			continue
	sf.close()
	tf.close()
	print(nbExamples, "examples found")
	
	of = open("examples/allWrong.csv", 'w', encoding='utf-8')
	examplesPerFeature = 10
	for feature in features:
		if feature not in examples:
			continue
		print(len(examples[feature]), "examples found for feature", feature)
		for example in sorted(examples[feature])[:examplesPerFeature]:
			of.write("\t".join([feature, example, examples[feature][example][0], examples[feature][example][1]]) + "\n")
			of.write("\t".join([system, examples[feature][example][2], examples[feature][example][3], examples[feature][example][4]]) + "\n")
			of.write("\n")
	of.close()


def extractAlmostAllCorrect():
	# extract ids of almostAllCorrect examples
	exampleIds = getExampleList(trueColumn=4, falseColumn=3)
	
	sf = open("../select_shuf/morpheval-enfi-2018.en", 'r', encoding='utf-8')
	tfs = [open("results/{}.en-fi.eval.csv".format(x), 'r', encoding='utf-8') for x in systems]
	examples = collections.defaultdict(dict)
	nbExamples = 0
	for tlines in zip(*tfs):
		sline1 = sf.readline()
		sline2 = sf.readline()
		selem = sline1.strip().split("\t") + sline2.strip().split("\t")
		if selem[0].split(".")[0] != selem[2].split(".")[0]:
			print("Sentence mismatch:", selem[0], selem[2])
			continue
			# no sanity check with tlines
		extype = selem[0].split(":")[0]
		exno = selem[0].split(":")[-1].split(".")[0]
		if (extype, exno) in exampleIds:
			examples[extype][exno] = [selem[1], selem[3]] + list(tlines)
			nbExamples += 1
	sf.close()
	[x.close() for x in tfs]
	print(nbExamples, "examples found")
	
	of = open("examples/almostAllCorrect.csv", 'w', encoding='utf-8')
	examplesPerFeature = 10
	for feature in features:
		if feature not in examples:
			continue
		print(len(examples[feature]), "examples found for feature", feature)
		for example in sorted(examples[feature])[:examplesPerFeature]:
			of.write("\t".join([feature, example, examples[feature][example][0], examples[feature][example][1]]) + "\n")
			for systemid, systemline in zip(systems, examples[feature][example][2:]):
				elements = systemline.strip().split("\t")
				of.write("\t".join([systemid, elements[2], elements[3], elements[5]]) + "\n")
			of.write("\n")
	of.close()


def extractAlmostAllWrong():
	# extract ids of almostAllWrong examples
	exampleIds = getExampleList(trueColumn=6, falseColumn=5)
	
	# extract source and worst system examples
	sf = open("../select_shuf/morpheval-enfi-2018.en", 'r', encoding='utf-8')
	tfs = [open("results/{}.en-fi.eval.csv".format(x), 'r', encoding='utf-8') for x in systems]
	examples = collections.defaultdict(dict)
	nbExamples = 0
	for tlines in zip(*tfs):
		sline1 = sf.readline()
		sline2 = sf.readline()
		selem = sline1.strip().split("\t") + sline2.strip().split("\t")
		if selem[0].split(".")[0] != selem[2].split(".")[0]:
			print("Sentence mismatch:", selem[0], selem[2])
			continue
			# no sanity check with tlines
		extype = selem[0].split(":")[0]
		exno = selem[0].split(":")[-1].split(".")[0]
		if (extype, exno) in exampleIds:
			if ("Correct" in tlines[-1]) and not any(["Correct" in x for x in tlines[2:-1]]):
				print(extype, exno, "skip, only AH correct")
			else:
				examples[extype][exno] = [selem[1], selem[3]] + list(tlines)
				nbExamples += 1
	sf.close()
	[x.close() for x in tfs]
	print(nbExamples, "examples found")
	
	of = open("examples/almostAllWrong.csv", 'w', encoding='utf-8')
	examplesPerFeature = 40	# this is exhaustive
	for feature in features:
		if feature not in examples:
			continue
		print(len(examples[feature]), "examples found for feature", feature)
		for example in sorted(examples[feature])[:examplesPerFeature]:
			of.write("\t".join([feature, example, examples[feature][example][0], examples[feature][example][1]]) + "\n")
			for systemid, systemline in zip(systems, examples[feature][example][2:]):
				elements = systemline.strip().split("\t")
				of.write("\t".join([systemid, elements[2], elements[3], elements[5]]) + "\n")
			of.write("\n")
	of.close()


def extractRBCorrect():
	sf = open("../select_shuf/morpheval-enfi-2018.en", 'r', encoding='utf-8')
	rtf = open("results/HY-AH-en-fi.5567.en-fi.eval.csv", 'r', encoding='utf-8')
	ntf = open("results/NICT.5658.en-fi.eval.csv", 'r', encoding='utf-8')
	examples = collections.defaultdict(dict)
	nbExamples = 0
	for rtline, ntline in zip(rtf, ntf):
		rtelem = rtline.strip().split("\t")
		ntelem = ntline.strip().split("\t")
		sline1 = sf.readline()
		sline2 = sf.readline()
		selem = sline1.strip().split("\t") + sline2.strip().split("\t")
		extype = rtelem[0].split(":")[0]
		if rtelem[0] == ntelem[0] and rtelem[1] == ntelem[1] and extype+":" in selem[0] and extype+":" in selem[2] and ":"+rtelem[1]+".1" in selem[0] and ":"+rtelem[1]+".2" in selem[2]:
			if rtelem[2].startswith("Correct") and not ntelem[2].startswith("Correct"):
				examples[extype][rtelem[1]] = (selem[1], selem[3], rtelem[2], rtelem[3], rtelem[5], ntelem[2], ntelem[3], ntelem[5])
				nbExamples += 1
		else:
			print("Sentence mismatch:", rtelem[0], ntelem[0], selem[0], selem[2])
			continue
	sf.close()
	rtf.close()
	ntf.close()
	
	print(nbExamples, "examples found")
	of = open("examples/rbCorrect.csv", 'w', encoding='utf-8')
	examplesPerFeature = 10
	for feature in features + stabfeatures:
		if feature not in examples:
			continue
		print(len(examples[feature]), "examples found for feature", feature)
		for example in sorted(examples[feature])[:examplesPerFeature]:
			of.write("\t".join([feature, example, examples[feature][example][0], examples[feature][example][1]]) + "\n")
			of.write("\t".join(["HY-AH", examples[feature][example][2], examples[feature][example][3], examples[feature][example][4]]) + "\n")
			of.write("\t".join(["NICT", examples[feature][example][5], examples[feature][example][6], examples[feature][example][7]]) + "\n")
			of.write("\n")
	of.close()

def count():
	allCorrect = getExampleList(trueColumn=3)
	allCorrectDict = collections.defaultdict(int)
	for f, e in allCorrect:
		allCorrectDict[f] += 1
	
	allWrong = getExampleList(trueColumn=5)
	allWrongDict = collections.defaultdict(int)
	for f, e in allWrong:
		allWrongDict[f] += 1
	
	almostAllCorrect = getExampleList(trueColumn=4, falseColumn=3)
	almostAllCorrectDict = collections.defaultdict(int)
	for f, e in almostAllCorrect:
		almostAllCorrectDict[f] += 1
	
	almostAllWrong = getExampleList(trueColumn=6, falseColumn=5)
	almostAllWrongDict = collections.defaultdict(int)
	for f, e in almostAllWrong:
		almostAllWrongDict[f] += 1
	
	of = open('perfeature.correct.csv', 'w')
	of.write("\t".join(["Feature", "AllCorrect", "AlmostAllCorrect", "Varied", "AlmostAllWrong", "AllWrong"]) + "\n")
	for f in features + stabfeatures:
		varied = 500 - allCorrectDict[f] - almostAllCorrectDict[f] - almostAllWrongDict[f] - allWrongDict[f]
		of.write("\t".join([f, str(allCorrectDict[f]), str(almostAllCorrectDict[f]), str(varied), str(almostAllWrongDict[f]), str(allWrongDict[f])]) + "\n")
	of.close()
	

if __name__ == "__main__":
	# extractAllCorrect()
	# extractAllWrong()
	extractRBCorrect()
	# extractAlmostAllCorrect()
	# extractAlmostAllWrong()
	# count()
	