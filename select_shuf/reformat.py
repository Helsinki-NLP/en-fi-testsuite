#! /usr/bin/env python3

import os, sys, subprocess

prefix = sys.argv[1]
suffix = sys.argv[2]

outfile = open("morpheval-enfi-2018.en", 'w', encoding='utf-8')

tokenizer = subprocess.Popen(["/proj/nlpl/software/moses/4.0-65c75ff/moses/scripts/tokenizer/detokenizer.perl", "-l en"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

for filename in os.listdir("."):
	if filename.startswith(prefix) and filename.endswith(suffix + ".txt"):
		print("Processing", filename)
		infile = open(filename)
		infile1 = open(filename.replace(".txt", ".1.txt"))
		infile2 = open(filename.replace(".txt", ".2.txt"))
		for line, line1, line2 in zip(infile, infile1, infile2):
			elements = line.split("\t")
			outfile.write("{}:{}.1\t{}\n".format(elements[2].strip(), elements[3].strip(), line1.strip()))
			outfile.write("{}:{}.2\t{}\n".format(elements[2].strip(), elements[3].strip(), line2.strip()))
		infile.close()
	else:
		print("Skipping file", filename)

outfile.close()
