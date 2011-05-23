#!/usr/bin/env python

import subprocess
import sys

from get_state_abbr import STATE_ABBRS

if len(sys.argv) > 1 and sys.argv[1] == 'FAKE':
    FAKE = 'FAKE'
else:
    FAKE = ''

for state in sorted(STATE_ABBRS.keys()):
    subprocess.call(['./batch_sf_2000.sh', state, FAKE]) 
    subprocess.call(['./batch_sf_2010.sh', state, FAKE]) 

