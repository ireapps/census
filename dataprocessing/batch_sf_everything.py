#!/usr/bin/env python

import subprocess
import sys

from get_state_abbr import STATE_ABBRS

if len(sys.argv) > 1 and sys.argv[1] == 'FAKE':
    FAKE = 'FAKE'
else:
    FAKE = ''

for state in sorted(STATE_ABBRS.keys()):
    subprocess.call(['./batch_sf.sh', state, FAKE]) 

