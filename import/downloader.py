from census2text import states
import os

cmd = "python census2text.py -q --state '%s' --geography tract  -w -o data/%s.tsv %s "

TABLES = ['P12']
try:
    os.mkdir('data')
except OSError: pass

for state in states:
    command = cmd % (state, state.replace(' ','_'), ' '.join(TABLES))
    os.system( command )
    print "downloaded %s" % state
