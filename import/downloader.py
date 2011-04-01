#!/usr/bin/env python
from lib import STATES
import os

cmd = "python census2text.py -q --state '%s' --geography tract  -w -o data/%s.tsv %s "

TABLES = ['P12']
try:
    os.mkdir('data')
except OSError: pass

for state, number, postal in STATES:
    command = cmd % (state, number, ' '.join(TABLES))
    os.system( command )
    print "downloaded %s" % state
