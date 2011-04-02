#!/usr/bin/env python
from lib import STATES
from multiprocessing import Pool
import os

cmd = "python census2text.py -q --state '%s' --geography tract  -w -o data/%s.tsv %s "

TABLES = ['H11','H12', 'H3', 'H4', 'H5', 'P12', 'P13', 'P14', 'P17', 'P18', 'P19', 'P23', 'P27', 'P28', 'P3', 'P30', 'P33', 'P37', 'P38', 'P7', 'P8', 'P9', 'PCT11', 'PCT15', 'PCT5', 'PCT8']
try:
    os.mkdir('data')
except OSError: pass

def download_state(params):
    state, number, postal = params
    print "downloading %s" % state
    command = cmd % (state, number, ' '.join(TABLES))
    os.system( command )
    print "downloaded %s" % state

p = Pool(5)
p.map(download_state, STATES)
    
