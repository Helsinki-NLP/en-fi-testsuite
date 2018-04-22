#! /usr/bin/env python3

import sys, os, gzip


# extract all adj-nn combinations from corpus
# clean them by hand
# extract all adj-nn combinations from corpus with one of allowed nouns
nouns = ['activist', 'admirer', 'adopter', 'adventurer', 'adviser', 'anthropologist', 'arbiter', 'archaeologist', 'artist', 'attacker', 'auctioneer', 'automaker', 'banker', 'believer', 'bidder', 'biographer', 'biologist', 'blogger', 'bomber', 'bowler', 'boxer', 'brewer', 'broadcaster', 'broker', 'brother', 'Buddhist', 'butler', 'buyer', 'bystander', 'caller', 'campaigner', 'carmaker', 'cartoonist', 'catcher', 'challenger', 'chatter', 'choreographer', 'cleaner', 'columnist', 'commander', 'commissioner', 'communist', 'commuter', 'composer', 'constructionist', 'consumer', 'contender', 'coroner', 'co-worker', 'cricketer', 'customer', 'cyclist', 'dancer', 'daughter', 'defender', 'designer', 'developer', 'digger', 'drinker', 'driver', 'economist', 'employer', 'engineer', 'examiner', 'explorer', 'exporter', 'extremist', 'farmer', 'father', 'fielder', 'fighter', 'filmmaker', 'finalist', 'finisher', 'firefighter', 'follower', 'footballer', 'founder', 'frontrunner', 'front-runner', 'Fundamentalist', 'gambler', 'game-winner', 'goalkeeper', 'grandfather', 'grandmother', 'guitarist', 'headmaster', 'hiker', 'hitter', 'hunter', 'hygienist', 'importer', 'industrialist', 'insider', 'interpreter', 'Islamist', 'journalist', 'keeper', 'killer', 'lawmaker', 'lawyer', 'leader', 'lecturer', 'left-hander', 'lender', 'listener', 'lobbyist', 'loser', 'lover', 'loyalist', 'manager', 'manufacturer', 'mapmaker', 'master', 'medalist', 'member', 'midfielder', 'minister', 'mobster', 'mother', 'mover', 'nationalist', 'newcomer', 'note-taker', 'observer', 'offender', 'officer', 'outsider', 'owner', 'painter', 'partner', 'passenger', 'pathologist', 'performer', 'photographer', 'planner', 'player', 'pollster', 'practitioner', 'preacher', 'prisoner', 'producer', 'provider', 'psychiatrist', 'psychologist', 'publisher', 'rapist', 'rapper', 'reader', 'reporter', 'researcher', 'rider', 'right-hander', 'ringer', 'ringleader', 'robber', 'rocker', 'runner', 'satirist', 'saxophonist', 'schoolteacher', 'scientist', 'seller', 'separatist', 'shareholder', 'shooter', 'shopper', 'singer', 'singer-songwriter', 'sister', 'skipper', 'soldier', 'spacewalker', 'specialist', 'sprinter', 'strategist', 'striker', 'stripper', 'subscriber', 'supplier', 'supporter', 'supremacist', 'taxpayer', 'teacher', 'technologist', 'teenager', 'terrorist', 'therapist', 'toddler', 'tourist', 'trainer', 'user', 'violinist', 'vocalist', 'volunteer', 'voter', 'winner', 'worker', 'wrestler', 'writer']


def makeVocab(infilename, outfilename):
	infile = gzip.open(infilename, 'r')
	vocab = {}
	
	adj = ""
	for line in infile:
		elements = line.decode('utf-8').split("\t")
		if elements[1] == 'JJ' and elements[0].lower() != 'own':
			adj = elements[0]
		#elif elements[1] == 'NN' and (adj != "") and (elements[0].endswith('ist') or elements[0].endswith('er')):
		elif elements[1] == 'NN' and (adj != "") and elements[0] in nouns:
			string = adj + " " + elements[0]
			#print(string)
			if string not in vocab:
				vocab[string] = 1
			else:
				vocab[string] += 1
			
			adj = ""
		else:
			adj = ""
	infile.close()
	
	outfile = open(outfilename, 'w', encoding='utf-8')
	for np in sorted(vocab, key=vocab.get, reverse=True):
		if vocab[np] < 10:
			break
		outfile.write(np + "\n")
	outfile.close()

	
if __name__ == "__main__":
	makeVocab("news2007.en.tagged.gz", "news2007.Adj+AgentNoun.txt")
	