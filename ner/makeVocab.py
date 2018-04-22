#! /usr/bin/env python3

import sys, os

def makeVocab(infiledir, outfilename):
	vocab = {}
	for infilename in os.listdir(infiledir):
		print(infilename)
		infile = open(infiledir + "/" + infilename, 'r', encoding='utf-8')
		for line in infile:
			elements = line.split("\t")
			if (len(elements) == 3) and (elements[0] != "") and (elements[1] != ""):
				string = elements[0]
				label = elements[1]
				if string not in vocab:
					vocab[string] = {label: 1}
				elif label not in vocab[string]:
					vocab[string][label] = 1
				else:
					vocab[string][label] += 1
		infile.close()
	
	print("writing results")
	outfile = open(outfilename, 'w', encoding='utf-8')
	for string in sorted(vocab):
		for label in sorted(vocab[string], key=vocab[string].get, reverse=True):
			if vocab[string][label] >= 5:
				outfile.write("{}\t{}\t{}\n".format(string, label, vocab[string][label]))
	outfile.close()

	
if __name__ == "__main__":
	makeVocab(sys.argv[1], sys.argv[2])
	