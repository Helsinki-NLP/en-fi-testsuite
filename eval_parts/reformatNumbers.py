#!/usr/bin/python3
# -*- coding: utf-8 -*-

# by decreasing BLEU score
systems = ["NICT.5658", "HY-NMT-en-fi.5570", "uedin.5707", "Aalto.5550", "HY-NMTtwostep-en-fi.5639", "CUNI-Kocmi.5620", "talp-upc.5424", "online-B.0", "HY-SMT-en-fi.5436", "online-G.0", "online-A.0", "HY-AH-en-fi.5567"]

features = ["sing_plur", "pron_sing_plur", "pres_past", "comp_adj", "pos_neg", "human_nonhuman_pron", "det_poss", "that_if", "prep_postp", "local_prep", "complex_np", "named_entities", "numbers", "masc_fem_pron", "pres_fut", "the_a"]

data = {}
for s in systems:
	f = open("results/{}.en-fi.numbers.tsv".format(s), 'r')
	data[s] = {}
	first = True
	for line in f:
		if first:
			first = False
			continue
		elements = line.strip().split("\t")
		if len(elements) != 4:
			continue
		data[s][elements[0]] = int(elements[1]) / int(elements[2])
	f.close()

f = open("all.numbers.tsv", 'w')
f.write("\t" + "\t".join(features) + "\n")
for s in systems:
	l = [s.split(".")[0]] + ["{:.1f}".format(100*data[s][x]) for x in features]
	f.write("\t".join(l) + "\n")
f.write("\n")
f.close()
