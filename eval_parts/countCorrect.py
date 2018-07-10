#!/usr/bin/python3
# -*- coding: utf-8 -*-

import collections

# by decreasing BLEU score
systems = ["NICT.5658", "HY-NMT-en-fi.5570", "uedin.5707", "Aalto.5550", "HY-NMTtwostep-en-fi.5639", "CUNI-Kocmi.5620", "talp-upc.5424", "online-B.0", "HY-SMT-en-fi.5436", "online-G.0", "online-A.0", "HY-AH-en-fi.5567"]

features = ["sing_plur", "pron_sing_plur", "pres_past", "comp_adj", "pos_neg", "human_nonhuman_pron", "det_poss", "that_if", "prep_postp", "local_prep", "complex_np", "named_entities", "numbers", "masc_fem_pron", "pres_fut", "the_a"]

correct = collections.defaultdict(int)
total = collections.defaultdict(int)
for s in systems:
	f = open("results/{}.en-fi.eval.csv".format(s), 'r')
	for line in f:
		elements = line.strip().split("\t")
		task = elements[0].split(":")[0]
		number = int(elements[1])
		msg = elements[2].split(":")[0]
		if msg.startswith("Correct"):
			correct[task, number] += 1
		total[task, number] += 1
	f.close()

f = open("all.correct.csv", 'w')
titlerow = ["Task", "Example", "NbCorrect", "AllCorrect", "AlmostAllCorrect", "AllWrong", "AlmostAllWrong"]
noise = 2
f.write("\t".join(titlerow) + "\n")
for feat in features:
	for task, number in sorted(total):
		if task != feat:
			continue
		row = [task, str(number), str(correct[task, number]), str(correct[task, number] == total[task, number]), str(correct[task, number] + noise >= total[task, number]), str(correct[task, number] == 0), str(correct[task, number] <= noise)]
		f.write("\t".join(row) + "\n")
	#f.write("\n") # confuses the Excel filter
f.close()
