#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
takes tokens as input, returns the initial sentence
and the modified sentence (past tense).
"""

import argparse

import pickle

import pymorphy
from pymorphy import get_morph


def print_out(sent_init, sent):
    global sent_id
    if sent_init != sent:
        args.s.write(' '.join(sent_init) + '\n')
        args.s.write(' '.join(sent) + '\n')
        args.c.write(str(sent_id) + ' past\n')
        args.c.write(str(sent_id) + ' past\n')
        sent_id += 1


parser = argparse.ArgumentParser()
							
parser.add_argument('-i', dest='i', nargs="?", type=argparse.FileType('r'),
                    help="input words")
parser.add_argument('-t', dest='t', nargs="?", type=argparse.FileType('r'),
                    help="input tags")
parser.add_argument('-s', dest='s', nargs="?", type=argparse.FileType('w'),
                    default='past.sents', help="output sentences")
parser.add_argument('-c', dest='c', nargs="?", type=argparse.FileType('w'),
                    default='past.info', help="output information")
args = parser.parse_args()


sent_id = 0

morph = get_morph('/people/burlot/prog/wmt17/analysis/pydict/kmike-pymorphy-3d1a3f962d0e/dicts/converted/en')
en_dict = pickle.load( open("/vol/work1/burlot/wmt17/analysis/news/words_en.pkl", 'r') )

for sent, tags in zip(args.i, args.t):
    sent = sent.split()
    tags = tags.split()
    sent_init = list(sent)
    # no interrogative
    if sent[-1] == '?':
        continue
    in_prog = False
    for i in range(len(sent)):

        # skip complicated cases
        if sent[i] in ['do', 'does', 'don', 'doesn', 'did', 'didn', 'has', 'have', 'haven', 'hasn'] or sent[i].startswith('would'):
            break

        # he is doing -> he has done
        if in_prog:
            # allow only adverb between two verbs
            if tags[i] not in ['VVG', 'RB'] or sent[i] != "'t":
                break
            if tags[i] == 'VVG':
                analysis = morph.decline(sent[i].upper())
                for cand in analysis:
                    if cand['info'] == 'pp':
                        v_out = cand['word'].lower().encode('utf-8')
                        if verb[0].isupper():
                            v_out = v_out[0] + v_out[1:]
                        sent[i] = v_out
                        print_out(sent_init, sent)
                        break
                break
            continue

        if sent[i] in ['am', 'are', 'is', 'aren', 'isn', 'were', 'was', 'weren', 'wasn']:
            in_prog = True
            if sent[i] in ['is', 'was']:
                sent[i] = 'has'
            elif sent[i] in ['isn', 'wasn']:
                sent[i] = 'hasn'
            elif sent[i] in ['am', 'are', 'were']:
                sent[i] = 'have'
            elif sent[i] in ['aren', 'weren']:
                sent[i] = 'haven'
            continue

        # he remembers -> he remembered
        if tags[i] in ['VVZ', 'VVP'] and not in_prog:
            verb = sent[i]
            analysis = morph.decline(verb.upper())
            for cand in analysis:
                if cand['info'] == 'pasa':
                    v_out = cand['word'].lower().encode('utf-8')
                    if verb[0].isupper():
                        v_out = v_out[0] + v_out[1:]
                    sent[i] = v_out
                    print_out(sent_init, sent)
                    break
            break
