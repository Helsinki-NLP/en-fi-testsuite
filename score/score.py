#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys


def loadScores(fileid):
	avgscores = []
	scorefile1 = open("%s.1.scored" % fileid, 'r')
	scorefile2 = open("%s.2.scored" % fileid, 'r')
	for line1, line2 in zip(scorefile1, scorefile2):
		sc1 = float(line1.strip())
		sc2 = float(line2.strip())
		avgsc = (sc1 + sc2) / 2.0
		avgscores.append(avgsc)
	scorefile1.close()
	scorefile2.close()
	sortedscores = sorted(avgscores)
	cutoff = int(len(sortedscores) / 3.0)
	cutoffvalue = sortedscores[cutoff]
	print(fileid)
	print("Cutoff index:", cutoff, "/", len(sortedscores))
	print("Min value:", sortedscores[0])
	print("Max value:", sortedscores[-1])
	print("Cutoff value:", cutoffvalue)
	print()
	return avgscores, cutoffvalue


def filter(fileid):
	scores, cutoffvalue = loadScores(fileid)
	datafile = open("../extract/%s.txt" % fileid, 'r', encoding='utf-8')
	outfile = open("%s.filtered.txt" % fileid, 'w', encoding='utf-8')
	for line, score in zip(datafile, scores):
		if score < cutoffvalue:
			continue
		outfile.write(line)
	datafile.close()
	outfile.close()


if __name__ == "__main__":
	filter(sys.argv[1])
