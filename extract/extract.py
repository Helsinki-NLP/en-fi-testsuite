#! /usr/bin/env python
# -*- coding: utf-8 -*-

import gzip, pymorphy, sys, re, random

def TreeTaggerSentenceReader(filehandle, cutoff):
	sentence = []
	for line in filehandle:
		line = line.decode('utf-8')
		elements = [x.strip() for x in line.split("\t")]
		sentence.append((elements[0], elements[1]))
		if elements[1] == "SENT":
			if len(sentence) < cutoff:
				yield sentence
			sentence = []
	if sentence != []:
		if len(sentence) < cutoff:
			yield sentence


def validSentence(sentence):
	#string = " ".join([x[0] for x in sentence])
	tags = [x[1] for x in sentence]
	
	# check that there is at least one inflected verb
	if len(set(tags) & set(['VB', 'VBD', 'VBP', 'VBZ', 'VH', 'VHD', 'VHP', 'VHZ', 'VV', 'VVD', 'VVP', 'VVZ', 'MD'])) == 0:
		#print "Skip sentence (no verb)"
		#print string
		return False
	# check that there is the same number of opening and closing quotation marks
	if tags.count('``') != tags.count("''"):
		#print "Skip sentence (quotation mark mismatch)"
		#print string
		return False
	# check that there is at most one pair of brackets
	if tags.count('(') != tags.count(')') or tags.count('(') > 1:
		#print "Skip sentence (bracket mismatch)"
		#print string
		return False
	# check that there is at most one 'special' punctuation sign
	if tags.count(':') > 1 or tags.count('SYM') > 1:
		#print "Skip sentence (too much punctuation)"
		#print string
		return False

	if sentence[-1][0] == "." and sentence[-2][0] == "Sept":
		return False
	
	return True


morph = pymorphy.get_morph('/wrk/yvessche/wmt18/testsuite/pymorphy_en')

# Extended PTB set: https://corpling.uis.georgetown.edu/ptb_tags.html
# Pymorphy tagset documentation: https://github.com/kmike/pymorphy/blob/master/dicts/src/Dicts/Morph/egramtab.tab


def complex_np(sentence):
	global nplist
	if nplist == []:
		return None
	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if (tag == 'PP') and word.lower() in ['him', 'her']:
			if [x[0] for x in sentence].count('him') + [x[0] for x in sentence].count('her') > 1:
				return None
			if word[0].isupper():
				out_sentence[i] = 'The'
			else:
				out_sentence[i] = 'the'
			np = random.choice(nplist).split(" ")
			out_sentence.insert(i+1, np[1])	# noun after det
			out_sentence.insert(i+1, np[0]) # adj after det
			return [x[0] for x in sentence], out_sentence, word.lower(), " ".join(np)		# him, nP
	return None


def numbers(sentence):
	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if tag == 'CD':
			match = re.search(r'([1-9]\d\d+)', word)	# no leading zeros
			if match:
				try:
					n = int(match.group(1))
					if n > 1900 and n < 2018:	# years
						n = n - 17
					else:
						n = n - 173
					if n > 99:
						out_sentence[i] = re.sub(r'([1-9]\d\d+)', str(n), word, count=1)
						return [x[0] for x in sentence], out_sentence, match.group(1), str(n)
				except ValueError:
					continue
	return None


def that_if(sentence):
	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if word.lower() in ['said', 'says', 'say'] and sentence[i+1][1] == 'IN/that':
			# this should not happen if i+1 is tagged IN/that, but there are tagging errors...
			if sentence[i+2][1].startswith("V") or sentence[i+2][1] in ['IN', 'TO', ',']:
				continue
			if sentence[i-1][0].lower() == 'having':	# having said that...
				continue
			if tag == 'VV' and sentence[i-1][1] != 'MD':
				continue
			# disabled - number of examples drops too much
			# for j in range(i+1, len(sentence)):
			# 	if sentence[j][0].lower() in ['no', 'nobody', 'none', 'no-one', 'never', 'not', 'nothing', 'nowhere', 'nor']:
			# 		return None
			
			if word.lower() == 'said':
				out_sentence[i] = 'asked'
			elif word.lower() == 'says':
				out_sentence[i] = 'asks'
			else:
				out_sentence[i] = 'ask'
			out_sentence[i+1] = 'if'

			if word[0].isupper():
				out_sentence[i] = out_sentence[i][0].upper() + out_sentence[i][1:]
			return [x[0] for x in sentence], out_sentence	# say, ask

		elif word.lower() in ['asked', 'asks', 'ask'] and sentence[i+1][0].lower() in ['if', 'whether']:
			if sentence[i+2][1].startswith("V") or sentence[i+2][1] in ['IN', 'TO', ',']:
				continue
			if tag == 'VV' and sentence[i-1][1] != 'MD':
				continue
			if i == 0 or sentence[i-1][0].lower() in ['when', 'but']:	# Asked if, When asked if...
				continue
			if sentence[i-1][1].startswith('VB'):		# was asked
				continue
			for j in range(i+1, len(sentence)):
				if sentence[j][0].lower() in ['any', 'anybody', 'anyone', 'ever', 'anything', 'anywhere']:
					return None
			
			if word.lower() == 'asked':
				out_sentence[i] = 'said'
			elif word.lower() == 'asks':
				out_sentence[i] = 'says'
			else:
				out_sentence[i] = 'say'
			out_sentence[i+1] = 'that'

			if word[0].isupper():
				out_sentence[i] = out_sentence[i][0].upper() + out_sentence[i][1:]
			return out_sentence, [x[0] for x in sentence]	# say, ask

	return None


def the_a(sentence):
	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if tag == 'DT' and word.lower() in ['a', 'an']:
			for j in range(i-1, -1, -1):	# try to find nouns in subject positions
				if sentence[j][1].startswith('V') or sentence[j][1] == 'MD':
					return None
			
			for j in range(i+1, len(sentence)):
				if sentence[j][0].lower() in ['ago', 'away']:
					return None
			
			if sentence[i+1][1] in ['CD', ',', '.', 'SENT', ':']:
				continue
				
			if sentence[i-1][0].lower() in ['as', 'not']:
				continue
			
			if word[0].isupper():
				out_sentence[i] = 'The'
			else:
				out_sentence[i] = 'the'
			return out_sentence, [x[0] for x in sentence]		# the, a
	return None


# ok, but selects sentences where future tends to be facultative in English anyway
def pres_fut(sentence):
	# no interrogative
	if sentence[-1][0] == '?':
		return None

	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if tag == 'MD' and word.lower() == 'will':
			if (sentence[i-1][1] == 'PP') and (sentence[i-1][0].lower() in ['i', 'you', 'we', 'they']) and (sentence[i+1][1].startswith('VV')):
				del out_sentence[i]
				return out_sentence, [x[0] for x in sentence]		# pres, fut
	return None


# ok
def masc_fem_pron(sentence):
	# no interrogative
	if sentence[-1][0] == '?':
		return None

	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if (tag == 'PP') and word.lower() in ['he', 'she', 'him', 'her']:
			for j in range(i-1, -1, -1):
				if sentence[j][0].lower() in ['i', 'me', 'my', 'we', 'us', 'our', 'he', 'him', 'his', 'she', 'her', 'it', 'himself', 'herself']:
					return None
				if sentence[j][0].lower() in ['mr.', 'ms.', 'mrs.', 'miss']:
					return None
			for j in range(i+1, len(sentence)):
				if sentence[j][0].lower() in ['i', 'me', 'my', 'we', 'us', 'our', 'he', 'him', 'his', 'she', 'her', 'it', 'himself', 'herself']:
					return None
			
			swap = False
			if word.lower() == 'he':
				out_sentence[i] = 'she'
			elif word.lower() == 'she':
				out_sentence[i] = 'he'
				swap = True
			elif word.lower() == 'him':
				out_sentence[i] = 'her'
			elif word.lower() == 'her':
				out_sentence[i] = 'him'
				swap = True
			
			if word[0].isupper():
				out_sentence[i] = out_sentence[i][0].upper() + out_sentence[i][1:]
			if swap:
				return out_sentence, [x[0] for x in sentence] 	# he, she
			else:
				return [x[0] for x in sentence], out_sentence	# he, she
	return None

# 'from behind' => very few sentences, difficult to change

# 'where ... from' => sentences are difficult to change


def local_prep(sentence):
	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		
		if sentence[i-1][1] in ['DT', 'PP$', 'PDT', 'JJ', 'JJR', 'JJS']:
			continue

		# in front of => behind
		if word.lower() == 'front' and sentence[i-1][0].lower() == 'in' and sentence[i+1][0].lower() == 'of':
			if sentence[i-1][0].isupper():
				out_sentence[i] = 'Behind'
			else:
				out_sentence[i] = 'behind'
			del out_sentence[i+1]
			del out_sentence[i-1]
			return out_sentence, [x[0] for x in sentence], 'behind', 'in_front_of'
		
		# the other direction (behind -> in front of) doesn't work as well as there are many non-literal examples that would have to be translated by 'ahead of' or similar
		
		# ahead doesn't work well because it includes many temporal readings that should be contrasted with 'after'
		# elif word.lower() == 'ahead' and sentence[i+1][0].lower() == 'of':
			# if word[0].isupper():
				# out_sentence[i] = 'Behind'
			# else:
				# out_sentence[i] = 'behind'
			# del out_sentence[i+1]
			# return out_sentence, [x[0] for x in sentence], 'behind', 'ahead_of'

		# over <=> under doesn't work well, gives way too many idiomatic readings

		# underneath => next to
		elif word.lower() == 'underneath':
			# particle use
			if sentence[i+1][1].startswith("V") or sentence[i+1][1] in ['MD', ',', '.', 'SENT', ':', 'CC']:
				continue
			if [x[0].lower() for x in sentence].count('next') + [x[0].lower() for x in sentence].count('underneath') > 1:
				continue
			if sentence[i-1][1] == 'IN':
				continue
		
			if word[0].isupper():
				out_sentence[i] = 'Next to'
			else:
				out_sentence[i] = 'next to'
			return [x[0] for x in sentence], out_sentence, 'underneath', 'next_to'
		
		# outside/inside
		elif word.lower() in ['outside', 'inside']:
			if sentence[i+1][1].startswith("V") or sentence[i+1][1] in ['MD', ',', '.', 'SENT', ':', 'CC']:
				continue
			if sentence[i+1][1] in ['NN', 'NNS']:	# get rid of adjectival readings ('outside expert') - keep NP and NPS as they are less prone to this phenomenon
				continue
			
			if sentence[i+1][1] == 'IN' and sentence[i+1][0].lower() != 'of':	# skip any preposition other than of
				continue
			
			if word.lower() == 'outside':
				if word[0].isupper():
					out_sentence[i] = 'Inside'
				else:
					out_sentence[i] = 'inside'
				return [x[0] for x in sentence], out_sentence, 'outside', 'inside'
			
			elif word.lower() == 'inside':
				if word[0].isupper():
					out_sentence[i] = 'Outside'
				else:
					out_sentence[i] = 'outside'
				return out_sentence, [x[0] for x in sentence], 'outside', 'inside'

		# above => below, below => above
		elif word.lower() in ['above', 'below']:
			ingFound = False
			for j in range(i+1, len(sentence)):
				if sentence[j][1] in ['VVG', 'VHG', 'VBG']:
					ingFound = True
					break
			if ingFound:
				continue
			
			# particle use
			if sentence[i+1][1].startswith("V") or sentence[i+1][1] in ['MD', ',', '.', 'SENT', ':', 'CC']:
				continue
			if [x[0].lower() for x in sentence].count('above') + [x[0].lower() for x in sentence].count('below') > 1:
				continue
			if sentence[i-1][0].lower() == 'far':
				continue

			if word.lower() == 'above':
				if sentence[i+1][0].lower() in ['all', 'reproach']:	# above all, above reproach
					continue
				if sentence[i-1][0].lower() in ['rise', 'rises', 'rose', 'risen', 'rising']:	# rises above =*> rises below
					continue
				
				if word[0].isupper():
					out_sentence[i] = 'Below'
				else:
					out_sentence[i] = 'below'
				return [x[0] for x in sentence], out_sentence, 'above', 'below'
			
			elif word.lower() == 'below':
				if sentence[i-1][0].lower() in ['fall', 'falls', 'fell', 'fallen', 'falling']:	# falls below =*> falls above
					continue
				
				if word[0].isupper():
					out_sentence[i] = 'Above'
				else:
					out_sentence[i] = 'above'
				return out_sentence, [x[0] for x in sentence], 'above', 'below'
	return None


# despite => without could work somehow
# without => with works somewhat, but there are very few examples and a lot of idiomatic readings to be filtered out...
def without_with(sentence):
	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if (tag == 'IN') and (word.lower() == 'without'):
			ingFound = False
			for j in range(i+1, len(sentence)):
				if sentence[j][1] in ['VVG', 'VHG', 'VBG']:
					ingFound = True
					break
			if ingFound:
				continue

			for j in range(i+1, len(sentence)):
				if sentence[j][0].lower() in ['much', 'even', 'ever', 'yet', 'either', 'neither', 'anymore', 'any', 'anybody', 'anyone', 'anything', 'until', 'doubt']:
					return None
			for j in range(i-1, i-3, -1):	# only look at the immediate surroundings
				if sentence[j][0].lower() in ['still', 'not']:
					return None
			
			if [x[0].lower() for x in sentence].count('with') + [x[0].lower() for x in sentence].count('without') > 1:
				continue

			# remove bare nouns (N at pos+1)
			if sentence[i+1][1].startswith("N") or sentence[i+1][1] in [',', '.', 'SENT', ':', 'CC']:
				continue
			
			if sentence[i-1][0].lower() in ['go', 'goes', 'went', 'come', 'comes', 'came', 'is', 'are', 'be', 'was', 'were', 'has', 'have', 'had']:
				continue
			
			if word[0].isupper():
				out_sentence[i] = 'With'
			else:
				out_sentence[i] = 'with'
			return [x[0] for x in sentence], out_sentence		# without, with
	return None


# during => before, before => after, after => before (transform during to before works better than the other direction)
def prep_postp(sentence):
	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if (tag == 'IN') and (word.lower() in ['during', 'after', 'before']):
			verbFound = False
			for j in range(i+1, len(sentence)):
				if sentence[j][1] in ['VB', 'VBD', 'VBN', 'VBP', 'VBZ', 'VH', 'VHD', 'VHN', 'VHP', 'VHZ', 'VV', 'VVD', 'VVN', 'VVP', 'VVZ', 'MD', 'VVG', 'VHG', 'VBG']:
					verbFound = True
					break
				if sentence[j][0] in [',', '.', 'SENT', ':', 'CC']:
					break
			if verbFound:
				continue
			
			if sentence[i+1][1] == "CD":		# during/after four years
				continue
			
			if [x[0].lower() for x in sentence].count('during') + [x[0].lower() for x in sentence].count('before') + [x[0].lower() for x in sentence].count('after') > 1:
				continue
			
			if word.lower() == 'during':
				if word[0].isupper():
					out_sentence[i] = 'Before'
				else:
					out_sentence[i] = 'before'
				return out_sentence, [x[0] for x in sentence], 'before', 'during'
			
			else:
				if sentence[i-1][0].lower() == sentence[i+1][0].lower():	# year after year
					continue
				if sentence[i+1][0].lower() == 'all':	# after all, before all
					continue
				if sentence[i+1][1] in ['PP', ',', '.', 'SENT', ':', 'CC']:		# after me
					continue
				if sentence[i-1][0].lower() in ['go', 'goes', 'went', 'is', 'are', 'be', 'was', 'were', 'has', 'have', 'had']:
					continue
					
				if word.lower() == 'after':
					if sentence[i-1][0].lower() in ['name', 'named', 'names', 'naming', 'look', 'looked', 'looks', 'looking']:	# named after, look after
						continue
				
					if word[0].isupper():
						out_sentence[i] = 'Before'
					else:
						out_sentence[i] = 'before'
					return out_sentence, [x[0] for x in sentence], 'before', 'after'
				
				elif word.lower() == 'before':
					if sentence[i+1][0].lower() == 'long':	# before long
						continue
						
					if word[0].isupper():
						out_sentence[i] = 'After'
					else:
						out_sentence[i] = 'after'
					return [x[0] for x in sentence], out_sentence, 'before', 'after'
	return None


# my X => the X
def det_poss(sentence):
	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if (tag == 'PP$') and word.lower() not in ['its', 'their']:
			if sentence[i+1][0].lower() in ['mother', 'father', 'mum', 'mom', 'dad', 'sister', 'brother', 'wife', 'husband', 'parents']:
				continue
			if not sentence[i+1][1].startswith("N"):	# * his is better than mine
				continue
			if out_sentence.count(word) > 1:	# make sure there is only one occurrence of the pronoun
				return None
			if word[0].isupper():
				out_sentence[i] = 'The'
			else:
				out_sentence[i] = 'the'
			return out_sentence, [x[0] for x in sentence]	# the modified sentence is the base, the original is the variant
	return None


# ... me => ... it
# seems ok, although some sentences are not very natural
def human_nonhuman_pron(sentence):
	# no interrogative
	if sentence[-1][0] == '?':
		return None

	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if (tag == 'PP') and word.lower() in ['me', 'us', 'him', 'her']:
			for j in range(i-1, -1, -1):
				if sentence[j][0].lower() in ['i', 'me', 'my', 'we', 'us', 'our', 'he', 'him', 'his', 'she', 'her', 'it', 'himself', 'herself', 'myself', 'yourself', 'itself', 'themselves']:
					return None
			for j in range(i+1, len(sentence)):
				if sentence[j][0].lower() in ['i', 'me', 'my', 'we', 'us', 'our', 'he', 'him', 'his', 'she', 'her', 'it', 'himself', 'herself', 'myself', 'yourself', 'itself', 'themselves']:
					return None
			if sentence[i-1][0].lower() == 'let':	# let us ...
				return None
			if word.lower() in ['him', 'her'] and sentence[i-1][1] in 'IN':		# with him => kanssansa, with it => kanssansa
				return None

			if word[0].isupper():
				out_sentence[i] = 'It'
			else:
				out_sentence[i] = 'it'
			return [x[0] for x in sentence], out_sentence
	return None


# test the opposite generation (it -> me), but it is not fundamentally better...
def human_nonhuman_pron2(sentence):
	# no interrogative
	if sentence[-1][0] == '?':
		return None

	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if (tag == 'PP') and word.lower() == 'it':
			verbFound = False
			verbAfterFound = False
			pronFound = False
			for j in range(i-1, -1, -1):
				if sentence[j][1].startswith("V"):
					verbFound = True
				if sentence[j][0].lower() in ['me', 'i', 'my']:
					pronFound = True
			for j in range(i+1, len(sentence)):
				if sentence[j][1].startswith("V") or sentence[j][1] == 'MD':
					verbAfterFound = True
					break
			if not verbFound:
				continue
			if pronFound:
				continue
			if verbAfterFound:
				continue

			if word[0].isupper():
				out_sentence[i] = 'Me'
			else:
				out_sentence[i] = 'me'
			return [x[0] for x in sentence], out_sentence
	return None


# does not X => Xes
# looks ok, but does not fulfill the one-word-only policy
def pos_neg(sentence):
	# no interrogative
	if sentence[-1][0] == '?':
		return None

	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if word.lower() == 'not':
			for j in range(i+1, len(sentence)):
				if sentence[j][0].lower() in ['much', 'even', 'ever', 'yet', 'either', 'neither', 'anymore', 'any', 'anybody', 'anyone', 'anything', 'until']:
					return None
				if sentence[j-1][0].lower() == 'at' and sentence[j][0].lower() == 'all':
					return None
			for j in range(i-1, -1, -1):
				if sentence[j][0].lower() == 'still':
					return None
			if [x[0].lower() for x in sentence].count('not') > 1:
				continue
			
			# have not Xed, is not Xing, is not Xed => have Xed, is Xing, is Xed
			if sentence[i-1][1].startswith('VB') or sentence[i-1][1].startswith('VH'):
				del out_sentence[i]
				return out_sentence, [x[0] for x in sentence]	# pos, neg
			
			# does not X, did not X => Xes, Xed
			elif sentence[i-1][1].startswith('V') and sentence[i+1][1].startswith('V'):
				preverb = sentence[i-1][0]
				preverbinfo = morph.get_graminfo(preverb.upper())
				tense = ""
				for cand in preverbinfo:
					if cand['class'] == 'VERB':
						tense = cand['info']
						break

				postverb = sentence[i+1][0]
				baseform = ""
				postverbinfo = morph.get_graminfo(postverb.upper())
				for cand in postverbinfo:
					if cand['class'] == 'VERB':
						baseform = cand['norm']
						break
				
				if tense != "" and baseform != "":
					newverbinfo = morph.decline(baseform.upper())
					for cand in newverbinfo:
						if cand['info'] == tense:
							del out_sentence[i+1]
							if preverb[0].isupper():
								out_sentence[i] = cand['word'][0] + cand['word'][1:].lower()
							else:
								out_sentence[i] = cand['word'].lower()
							del out_sentence[i-1]
							return out_sentence, [x[0] for x in sentence]	# pos, neg
	return None


# Xer => X
# ok
def comp_adj(sentence):
	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if (tag == 'JJR'):
			if word.lower() in ['more', 'further', 'less', 'fewer', 'later', 'earlier']:
				continue
			
			if sentence[i-1][0].lower() in ['much', 'little', 'even', 'no', 'hardly', 'still', 'any', 'slightly']:	# much higher, a little higher, even higher, no longer
				continue
			if sentence[i+1][0].lower() in ['still']:
				continue
			
			# remove coordinate structures: 'a more comfortable and cleaner X' =/> 'a more comfortable and clean X'
			taglist = [x[1] for x in sentence]
			if taglist.count('JJR') > 1:
				return None
			
			# remove light verb constructions
			lightVerbFound = False
			if not sentence[i+1][1].startswith("N"):
				for j in range(i-1, i-4, -1):
					if sentence[j][0].lower() in ['get', 'gets', 'got', 'getting', 'make', 'makes', 'made', 'making', 'become', 'becomes', 'became', 'becoming', 'bring', 'brings', 'brought', 'bringing']:
						lightVerbFound = True
			if lightVerbFound:
				continue
			
			# remove comparative structures of type 'higher than X'
			compFound = False
			for j in range(i+1, len(sentence)):
				if sentence[j][0].lower() == "than":
					compFound = True
					break
				if sentence[j][1] not in ["DT", "PDT", "PP", "PP$", "RB", "JJ", "JJR", "JJS", "NN", "NNS", "NP", "NPS", "POS", "IN", "CD"]:
					break
			if compFound:
				continue
			
			# remove structures of type '10 percent higher'
			numeralFound = False
			for j in range(i-1, -1, -1):
				if sentence[j][1] == "CD":
					numeralFound = True
					break
				if sentence[j][1] not in ["DT", "PDT", "PP", "PP$", "RB", "JJ", "JJR", "JJS", "NN", "NNS", "NP", "NPS", "POS"]:
					break
			if numeralFound:
				continue

			if word.lower() == 'better' and not sentence[i+1][1].startswith("N"):
				continue
			
			# remove structures like 'the older ... , the better ...'
			sentstring = " ".join([x[0].lower() for x in sentence])
			match1 = re.findall(r'the \w+er', sentstring)
			match2 = re.findall(r', the \w+er', sentstring)
			if len(match1) >= 2 and len(match2) >= 1:
				continue
			
			info = morph.get_graminfo(word.upper())
			for cand in info:
				if cand['class'] == 'ADJECTIVE':
					baseform = cand['norm']
					if baseform.lower() in [x[0].lower() for x in sentence]:	# skip sentences like 'it is bad and it is getting worse'
						return None
					analysis = morph.decline(baseform.upper())
					#print analysis
					for cand2 in analysis:
						if cand2['info'] == '':
							if word[0].isupper():
								out_sentence[i] = cand2['word'][0] + cand2['word'][1:].lower()
							else:
								out_sentence[i] = cand2['word'].lower()
							return out_sentence, [x[0] for x in sentence]		# positive, comparative
	return None


# ... her => ... them
# looks ok, generate all files
def pron_sing_plur(sentence):
	# no interrogative
	if sentence[-1][0] == '?':
		return None

	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if (tag == 'PP'):
			for j in range(i-1, -1, -1):
				if sentence[j][0].lower() in ['i', 'me', 'my', 'we', 'us', 'our', 'he', 'him', 'his', 'she', 'her', 'it']:
					return None
			for j in range(i+1, len(sentence)):
				if sentence[j][0].lower() in ['i', 'me', 'my', 'we', 'us', 'our', 'he', 'him', 'his', 'she', 'her', 'it']:
					return None
		
			if word.lower() in ['her', 'him']:
				if word[0].isupper():
					out_sentence[i] = 'Them'
				else:
					out_sentence[i] = 'them'
				return [x[0] for x in sentence], out_sentence		# sing, plur
			
			elif word.lower() == 'us':
				if sentence[i-1][0].lower() == "of":	# *all of me, *most of me
					continue
				if sentence[i-1][0].lower() == "let":
					continue
				if sentence[i+1][0].lower() == 'all':
					continue
				
				if word[0].isupper():
					out_sentence[i] = 'Me'
				else:
					out_sentence[i] = 'me'
				return out_sentence, [x[0] for x in sentence]		# sing, plur
	return None


# the Xes => the X
# should be ok, although maybe a bit too harsh
def sing_plur(sentence):
	# no interrogative
	if sentence[-1][0] == '?':
		return None

	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if tag in ['NNS']:
			if word.lower() in ['people', 'police', 'one', 'troops']:
				continue
			# plural possessive
			if word.endswith("s") and sentence[i+1][0] == "'":
				continue

			numeral = False		# checks whether the NP contains a numeral => skip
			defdet = False		# checks whether the NP contains a definite determiner
			possdet = False		# checks whether the NP contains a possessive determiner
			for j in range(i-1, -1, -1):
				if sentence[j][1] == "CD":
					numeral = True
					break
				if sentence[j][1] == "DT" and sentence[j][0].lower() == "the":
					defdet = True
					break
				if sentence[j][1] == "PP$":
					possdet = True
					break
			#	if sentence[j][1] not in ["DT", "PP$", "NN", "NNS", "NP", "NPS", "JJ", "JJR", "JJS", "CD", "POS"]:
				if sentence[j][1] not in ["DT", "PP$", "JJ", "JJR", "JJS", "CD"]:
					break

			if numeral:
				continue
			if possdet:			# this is just for Finnish, as possessive suffixes neutralize sing/pl distinction
				continue

			# determiners: accepted: the X // rejected: X (-> a X), these X (-> this X), her X
			# rejecting any determiner-less NP is a bit harsh though...
			if not defdet:
				continue

			prefix = " ".join([x[0].lower() for x in sentence[:i]])
			if "one of" in prefix or "all the" in prefix:
				continue

			if sentence[i-1][0].lower() in ["major", "few", "many", "most", "more"]:
				continue
			
			if sentence[i+1][1] in ['NN', 'NNS', 'NP', 'NPS']:	# don't change the first element of a compound noun
				continue
			
			verbChange = False
			for j in range(i+1, len(sentence)):
				if sentence[j][1].startswith("V") or sentence[j][1] == "MD":
					if sentence[j][1] in ["VVP", "VBP", "VBD", "VHP"]:
						verbChange = True
						break
					else:
						break
			if verbChange:
				continue
			
			analysis = morph.decline(word.upper())
			for cand in analysis:
				if cand['info'] == 'narr,sg':
					if word[0].isupper():
						out_sentence[i] = cand['word'][0] + cand['word'][1:].lower()
					else:
						out_sentence[i] = cand['word'].lower()
					return out_sentence, [x[0] for x in sentence]		# sing, plur
	return None


def pres_past(sentence):
	if sentence[-1][0] == '?':
		return None
	
	out_sentence = [x[0] for x in sentence]
	for i, (word, tag) in enumerate(sentence):
		if tag in ['VBZ', 'VVZ', 'VBP', 'VVP']:	# skip VHP and VHZ to avoid contrasting perfect and pluperfect
			verbFound = False
			for j in range(i-1, -1, -1):
				if sentence[j][1] in ['VB', 'VBD', 'VBP', 'VBZ', 'VH', 'VHD', 'VHP', 'VHZ', 'VV', 'VVD', 'VVP', 'VVZ', 'MD']:
					verbFound = True
					break
			for j in range(i+1, len(sentence)):
				if sentence[j][1] in ['VB', 'VBD', 'VBP', 'VBZ', 'VH', 'VHD', 'VHP', 'VHZ', 'VV', 'VVD', 'VVP', 'VVZ', 'MD']:
					verbFound = True
					break
			if verbFound:
				continue
			
			if tag.startswith('VB'):
				analysis = morph.decline('BE')
				for cand2 in analysis:
					if tag == 'VBZ' and cand2['info'] == 'pasa,sg':
						out_sentence[i] = cand2['word'].lower()
						break
					if tag == 'VBP' and word.lower() != 'am' and cand2['info'] == 'pasa,pl':
						out_sentence[i] = cand2['word'].lower()
						break
					if tag == 'VBP' and word.lower() == 'am' and cand2['info'] == 'pasa,sg':
						out_sentence[i] = cand2['word'].lower()
						break
				#print word, out_sentence[i]
			else:
				info = morph.get_graminfo(word.upper())
				for cand in info:
					if cand['class'] == 'VERB':
						if cand['norm'] == 'HA':	# there are two analyses for forms of 'have'
							continue
						baseform = cand['norm']
						analysis = morph.decline(baseform.upper())
						if tag.startswith('VB'):
							print word, tag, analysis
						for cand2 in analysis:
							if cand2['info'] == 'pasa':
								out_sentence[i] = cand2['word'].lower()
								break
				#print word, out_sentence[i]
					
			if out_sentence[i] != word:
				if word[0].isupper():
					out_sentence[i] = out_sentence[i][0].upper() + out_sentence[i][1:]
				return [x[0] for x in sentence], out_sentence 	# pres, past
	return None
	

def extract(fileid, taskid, nbsentences=-1):
	taggedfile = gzip.open("../tag/%s.en.tagged.gz" % fileid)
	outfile = open("%s.%s.txt" % (fileid, taskid), 'w')
	
	debugMode = nbsentences > 0
	sentenceid = 0
	maxSentenceLength = 15
	alreadywritten = set()
	taskproc = globals()[taskid]
	
	if taskid == "complex_np":
		global nplist
		nplist = []
		npfile = open("../tag/%s.Adj+AgentNoun.txt" % fileid, 'r')
		for line in npfile:
			if line.startswith("only "):
				continue
			nplist.append(line.strip())
		npfile.close()

	for sentence in TreeTaggerSentenceReader(taggedfile, maxSentenceLength):
		if not validSentence(sentence):
			continue
		result = taskproc(sentence)
		
		if debugMode and (result is not None):
			print " ".join(result[0])
			print " ".join(result[1])
			print
		
		if (result is not None) and (result[0] != result[1]) and (u' '.join(result[0]) not in alreadywritten):
			s1 = u' '.join(result[0])
			s2 = u' '.join(result[1])
			if len(result) == 4:
				s = u"%s\t%s\t%s:%s:%s\t%i\n" % (s1.strip(), s2.strip(), taskid, result[2], result[3], sentenceid)
			else:
				s = u"%s\t%s\t%s\t%i\n" % (s1.strip(), s2.strip(), taskid, sentenceid)
			outfile.write(s.encode('utf-8'))
			sentenceid += 1
			alreadywritten.add(u' '.join(result[0]))
		
		if debugMode and (sentenceid >= nbsentences):
			break
	print fileid, taskid, sentenceid, "sentences written"


if __name__ == "__main__":
	# Usage example: python extract.py news2007 past
	# Usage example: python extract.py news2007 past 100	[first 100 sentences with debugging output on stdout]
	if len(sys.argv) >= 4:
		extract(sys.argv[1], sys.argv[2], int(sys.argv[3]))
	else:
		extract(sys.argv[1], sys.argv[2])
	