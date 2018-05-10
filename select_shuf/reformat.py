#! /usr/bin/env python3

import os, sys

prefix = sys.argv[1]
suffix = sys.argv[2]

outfile = open("morpheval-enfi-2018.en", 'w', encoding='utf-8')

for filename in os.listdir("."):
	if filename.startswith(prefix) and filename.endswith(suffix + ".txt"):
		print("Processing", filename)
		infile = open(filename)
		for line in infile:
			elements = line.split("\t")
			outfile.write("{}:{}.1\t{}\n".format(elements[2].strip(), elements[3].strip(), elements[0].strip()))
			outfile.write("{}:{}.2\t{}\n".format(elements[2].strip(), elements[3].strip(), elements[1].strip()))
		infile.close()
	else:
		print("Skipping file", filename)

outfile.close()
