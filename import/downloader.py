#!/usr/bin/env python
from lib import STATES
from multiprocessing import Pool
import os

cmd = "python census2text.py -q --state '%s' --geography tract  -w -o data/%s.tsv %s "

TABLES = ['P12']
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
    
